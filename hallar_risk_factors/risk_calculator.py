"""
Risk Calculation Engine (v2 — Logistic Model)

Computes scenario-adjusted risk magnitudes by combining:
1. Base risk parameters (from risk_sensitivities.py)
2. Scenario factor scores (from structural_factors.py)
3. Risk sensitivity to factors (from risk_sensitivities.py)

v2 CHANGES (from audit):
- Replaced capped multiplicative model with logistic (sigmoid) transformation
- Removed MAX_MODIFIER / MIN_MODIFIER caps that destroyed information in 20% of cases
- Added output clamping to guarantee strict (0, 1) bounds at float64 precision
- Resolves all 48 large disagreements from model comparison in favor of logistic

WHY LOGISTIC:
The old model capped the combined modifier at ×2.5 / ×0.2. This meant:
- S9 × R11 (Contractor Bankruptcy): raw modifier 4.5× → capped 2.5× → P=37.5%
  Logistic gives 82.9% — far more defensible for weakest scenario.
- S7 × R16 (Material Prices): moderate modifier × high base → clipped at 99%
  Logistic gives 64.8% — no false certainty.

The logistic transform maps probability through log-odds space where factor
effects are additive, then maps back through the sigmoid. This is standard
in epidemiology, actuarial science, and risk modeling.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .structural_factors import SCENARIO_FACTORS, STRUCTURAL_FACTORS, get_scenario_profile
from .risk_sensitivities import RISK_PROFILES, RiskProfile, FactorDirection, Sensitivity


NEUTRAL_FACTOR = 3.0

# Strict output bounds — float64 sigmoid can round to exactly 0 or 1
# at |log-odds| > ~36, even below the exp() overflow threshold
PROB_FLOOR = 1e-15
PROB_CEIL = 1.0 - 1e-15


def calculate_factor_effect(
    factor_score: int,
    direction: FactorDirection,
    sensitivity: Sensitivity,
) -> float:
    """
    Calculate the effect of a single structural factor on risk probability.
    Returns a multiplier (1.0 = no effect, <1 = reduces risk, >1 = increases risk).

    Formula:
    - PROTECTIVE: base = neutral / (neutral + deviation)
      Score 5 → deviation +2 → base = 3/5 = 0.6 → risk reduced
      Score 1 → deviation -2 → base = 3/1 = 3.0 → risk increased (weak protection)
    - EXPOSURE: base = (neutral + deviation) / neutral
      Score 5 → deviation +2 → base = 5/3 = 1.67 → risk increased
      Score 1 → deviation -2 → base = 1/3 = 0.33 → risk reduced

    Sensitivity exponent scales the effect:
      LOW=0.5, MEDIUM=1.0, HIGH=1.5, CRITICAL=2.0

    Properties verified by audit:
    - At score=3 (neutral): effect = 1.0 for all directions and sensitivities
    - Monotonic: better scores always reduce risk, worse always increase
    - Continuous: no jumps or discontinuities
    """
    deviation = factor_score - NEUTRAL_FACTOR

    if direction == FactorDirection.PROTECTIVE:
        base_effect = NEUTRAL_FACTOR / (NEUTRAL_FACTOR + deviation)
    else:
        base_effect = (NEUTRAL_FACTOR + deviation) / NEUTRAL_FACTOR

    # Floor at 0.2 to prevent extreme artifacts at boundary scores
    base_effect = max(0.2, base_effect)

    adjusted_effect = base_effect ** sensitivity.value

    return adjusted_effect


def _logistic_transform(
    base_prob: float,
    factor_effects: List[float],
) -> Tuple[float, Dict]:
    """
    Logistic probability transformation.

    Process:
    1. Convert base probability to log-odds: ln(p / (1-p))
    2. Each factor effect shifts log-odds by ln(effect)
    3. Convert back via sigmoid: 1 / (1 + exp(-log_odds))
    4. Clamp to strict (0, 1) bounds for float64 safety

    This is equivalent to treating factor effects as odds-ratio multipliers,
    which is the standard approach in logistic regression / risk modeling.
    """
    base_prob = max(0.001, min(0.999, base_prob))

    base_log_odds = math.log(base_prob / (1.0 - base_prob))

    adjustments = []
    total_adjustment = 0.0
    for effect in factor_effects:
        effect = max(0.001, effect)
        adj = math.log(effect)
        adjustments.append(adj)
        total_adjustment += adj

    adjusted_log_odds = base_log_odds + total_adjustment

    # Sigmoid with overflow protection
    if adjusted_log_odds > 700:
        adjusted_prob = PROB_CEIL
    elif adjusted_log_odds < -700:
        adjusted_prob = PROB_FLOOR
    else:
        adjusted_prob = 1.0 / (1.0 + math.exp(-adjusted_log_odds))

    # Final clamp: sigmoid rounds to exactly 0.0/1.0 at |log-odds| > ~36
    adjusted_prob = max(PROB_FLOOR, min(PROB_CEIL, adjusted_prob))

    details = {
        "base_prob": base_prob,
        "base_log_odds": round(base_log_odds, 4),
        "adjustments": [round(a, 4) for a in adjustments],
        "total_adjustment": round(total_adjustment, 4),
        "adjusted_log_odds": round(adjusted_log_odds, 4),
        "final_prob": adjusted_prob,
    }

    return adjusted_prob, details


def calculate_scenario_modifier(
    scenario_id: str,
    risk_profile: RiskProfile,
) -> Tuple[float, List[Tuple[str, float, str]]]:
    """
    Calculate factor effects for a risk in a specific scenario.
    Returns (display_modifier, breakdown).

    The display_modifier is the raw product of effects — used for
    explanations and UI only. Actual probability uses logistic transform.
    """
    scenario = SCENARIO_FACTORS.get(scenario_id)
    if not scenario:
        return 1.0, []

    if risk_profile.requires_factors:
        for factor_id, (min_val, max_val) in risk_profile.requires_factors.items():
            factor_score = scenario.get_factor(factor_id)
            if not (min_val <= factor_score <= max_val):
                return 0.0, [(factor_id, 0.0, "Risk does not apply to this scenario")]

    combined_modifier = 1.0
    breakdown = []

    for sens in risk_profile.sensitivities:
        factor_score = scenario.get_factor(sens.factor_id)
        factor_info = STRUCTURAL_FACTORS.get(sens.factor_id)

        effect = calculate_factor_effect(factor_score, sens.direction, sens.sensitivity)
        combined_modifier *= effect

        if effect < 0.9:
            impact = f"reduces risk ({effect:.2f}×)"
        elif effect > 1.1:
            impact = f"increases risk ({effect:.2f}×)"
        else:
            impact = f"neutral ({effect:.2f}×)"

        breakdown.append((
            sens.factor_id,
            effect,
            f"{factor_info.name_is if factor_info else sens.factor_id} = {factor_score}: {impact}"
        ))

    return combined_modifier, breakdown


def calculate_adjusted_probability(
    scenario_id: str,
    risk_id: str,
) -> Tuple[List[float], float, List[Tuple[str, float, str]]]:
    """
    Calculate scenario-adjusted probability for a risk using logistic model.
    Returns (adjusted_prob [low, likely, high], display_modifier, breakdown)
    """
    risk_profile = RISK_PROFILES.get(risk_id)
    if not risk_profile:
        return [0.0, 0.0, 0.0], 1.0, []

    scenario = SCENARIO_FACTORS.get(scenario_id)
    if not scenario:
        return [0.0, 0.0, 0.0], 1.0, []

    # Check applicability
    if risk_profile.requires_factors:
        for factor_id, (min_val, max_val) in risk_profile.requires_factors.items():
            factor_score = scenario.get_factor(factor_id)
            if not (min_val <= factor_score <= max_val):
                return [0.0, 0.0, 0.0], 0.0, [
                    (factor_id, 0.0, "Risk does not apply to this scenario")
                ]

    # Collect factor effects
    effects = []
    breakdown = []
    for sens in risk_profile.sensitivities:
        factor_score = scenario.get_factor(sens.factor_id)
        factor_info = STRUCTURAL_FACTORS.get(sens.factor_id)
        effect = calculate_factor_effect(factor_score, sens.direction, sens.sensitivity)
        effects.append(effect)

        if effect < 0.9:
            impact = f"reduces risk ({effect:.2f}×)"
        elif effect > 1.1:
            impact = f"increases risk ({effect:.2f}×)"
        else:
            impact = f"neutral ({effect:.2f}×)"

        breakdown.append((
            sens.factor_id,
            effect,
            f"{factor_info.name_is if factor_info else sens.factor_id} = {factor_score}: {impact}"
        ))

    # Apply logistic transform to each PERT estimate
    prob_low, _ = _logistic_transform(risk_profile.base_prob_low, effects)
    prob_likely, _ = _logistic_transform(risk_profile.base_prob_likely, effects)
    prob_high, _ = _logistic_transform(risk_profile.base_prob_high, effects)

    adjusted_prob = [prob_low, prob_likely, prob_high]

    # Display modifier (raw product — for UI explanation, not for calculation)
    display_modifier = 1.0
    for e in effects:
        display_modifier *= e

    return adjusted_prob, display_modifier, breakdown


@dataclass
class ScenarioRiskResult:
    """Result of risk calculation for a single risk in a scenario."""
    risk_id: str
    name_is: str
    name_en: str
    category: str
    prob_low: float
    prob_likely: float
    prob_high: float
    modifier: float
    affected_goals: List[str]
    breakdown: List[Tuple[str, float, str]]

    @property
    def prob_pert_mean(self) -> float:
        """PERT mean of probability."""
        return (self.prob_low + 4 * self.prob_likely + self.prob_high) / 6


@dataclass
class ScenarioRiskProfile:
    """Complete risk profile for a scenario."""
    scenario_id: str
    scenario_name_is: str
    scenario_name_en: str
    factor_scores: Dict[str, int]
    risks: List[ScenarioRiskResult]

    def risks_by_category(self) -> Dict[str, List[ScenarioRiskResult]]:
        """Group risks by category."""
        result: Dict[str, List[ScenarioRiskResult]] = {}
        for risk in self.risks:
            if risk.category not in result:
                result[risk.category] = []
            result[risk.category].append(risk)
        return result

    def risks_affecting_goal(self, goal_id: str) -> List[ScenarioRiskResult]:
        """Get risks that affect a specific goal."""
        return [r for r in self.risks if goal_id in r.affected_goals]

    def top_risks(self, n: int = 5) -> List[ScenarioRiskResult]:
        """Get top N risks by likely probability."""
        return sorted(self.risks, key=lambda r: r.prob_likely, reverse=True)[:n]


def calculate_scenario_risk_profile(scenario_id: str) -> Optional[ScenarioRiskProfile]:
    """Calculate complete risk profile for a scenario."""
    scenario = SCENARIO_FACTORS.get(scenario_id)
    if not scenario:
        return None

    results = []

    for risk_id, risk_profile in RISK_PROFILES.items():
        adjusted_prob, modifier, breakdown = calculate_adjusted_probability(scenario_id, risk_id)

        if modifier == 0:
            continue

        results.append(ScenarioRiskResult(
            risk_id=risk_id,
            name_is=risk_profile.name_is,
            name_en=risk_profile.name_en,
            category=risk_profile.category,
            prob_low=adjusted_prob[0],
            prob_likely=adjusted_prob[1],
            prob_high=adjusted_prob[2],
            modifier=modifier,
            affected_goals=risk_profile.affected_goals,
            breakdown=breakdown,
        ))

    return ScenarioRiskProfile(
        scenario_id=scenario_id,
        scenario_name_is=scenario.name_is,
        scenario_name_en=scenario.name_en,
        factor_scores=get_scenario_profile(scenario_id),
        risks=results,
    )


def compare_scenarios_by_goal(
    scenario_ids: List[str],
    goal_id: str,
) -> Dict[str, List[ScenarioRiskResult]]:
    """Compare multiple scenarios by risks affecting a specific goal."""
    result = {}
    for sid in scenario_ids:
        profile = calculate_scenario_risk_profile(sid)
        if profile:
            result[sid] = profile.risks_affecting_goal(goal_id)
    return result


def get_scenario_risk_summary(scenario_id: str) -> Dict:
    """Get a summary of risk profile for a scenario."""
    profile = calculate_scenario_risk_profile(scenario_id)
    if not profile:
        return {}

    high_risks = [r for r in profile.risks if r.prob_likely > 0.40]
    medium_risks = [r for r in profile.risks if 0.20 <= r.prob_likely <= 0.40]
    low_risks = [r for r in profile.risks if r.prob_likely < 0.20]

    return {
        "scenario_id": scenario_id,
        "factor_scores": profile.factor_scores,
        "risk_count": len(profile.risks),
        "high_risk_count": len(high_risks),
        "medium_risk_count": len(medium_risks),
        "low_risk_count": len(low_risks),
        "high_risks": [(r.risk_id, r.name_is, r.prob_likely) for r in high_risks],
        "medium_risks": [(r.risk_id, r.name_is, r.prob_likely) for r in medium_risks],
    }


def print_scenario_comparison(scenario_ids: List[str] = None):
    """Print a comparison table of scenarios."""
    if scenario_ids is None:
        scenario_ids = list(SCENARIO_FACTORS.keys())

    print(f"{'Scenario':<8} {'High':<6} {'Med':<6} {'Low':<6}")
    print("-" * 30)

    for sid in sorted(scenario_ids, key=lambda x: int(x[1:])):
        summary = get_scenario_risk_summary(sid)
        if not summary:
            continue
        print(f"{sid:<8} {summary['high_risk_count']:<6} {summary['medium_risk_count']:<6} "
              f"{summary['low_risk_count']:<6}")
