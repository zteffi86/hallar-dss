"""
Goal Scoring Engine

Connects:
1. Scenario → Risk probabilities (from risk_calculator)
2. Risk × Goal → Impact magnitudes (from goal_impacts)
3. Aggregation → Expected impact per goal per scenario
4. Weighting → Overall scenario score
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .risk_calculator import calculate_scenario_risk_profile
from .goal_impacts import GOALS, RISK_GOAL_IMPACTS, GoalDefinition, pert_mean
from .structural_factors import SCENARIO_FACTORS


@dataclass
class GoalRiskContribution:
    """Contribution of one risk to one goal."""
    risk_id: str
    risk_name: str
    probability: float
    impact_if_occurs: float
    expected_impact: float
    unit: str


@dataclass
class GoalScore:
    """Score for a single goal in a scenario."""
    goal_id: str
    goal_name_is: str
    goal_name_en: str
    unit: str
    baseline: float
    expected_impact: float
    expected_value: float
    risk_contributions: List[GoalRiskContribution]

    @property
    def top_contributors(self) -> List[GoalRiskContribution]:
        """Get top 5 risks contributing to this goal's expected impact."""
        return sorted(
            self.risk_contributions,
            key=lambda x: abs(x.expected_impact),
            reverse=True
        )[:5]


@dataclass
class ScenarioGoalProfile:
    """Complete goal profile for a scenario."""
    scenario_id: str
    scenario_name_is: str
    scenario_name_en: str
    goal_scores: Dict[str, GoalScore]

    def get_goal(self, goal_id: str) -> Optional[GoalScore]:
        return self.goal_scores.get(goal_id)

    def rank_goals_by_impact(self) -> List[Tuple[str, float]]:
        """Rank goals by expected impact magnitude."""
        return sorted(
            [(gid, gs.expected_impact) for gid, gs in self.goal_scores.items()],
            key=lambda x: abs(x[1]),
            reverse=True
        )


@dataclass
class WeightedScenarioScore:
    """Overall scenario score with weighted goals."""
    scenario_id: str
    scenario_name_is: str
    total_score: float
    goal_contributions: Dict[str, float]
    rank: int = 0


def calculate_scenario_goal_profile(scenario_id: str) -> Optional[ScenarioGoalProfile]:
    """
    Calculate goal impacts for a scenario.
    """
    risk_profile = calculate_scenario_risk_profile(scenario_id)
    if not risk_profile:
        return None

    # Build risk probability lookup
    risk_probs: Dict[str, float] = {}
    risk_names: Dict[str, str] = {}
    for risk in risk_profile.risks:
        risk_probs[risk.risk_id] = risk.prob_pert_mean
        risk_names[risk.risk_id] = risk.name_is

    # Calculate goal scores
    goal_scores: Dict[str, GoalScore] = {}

    for goal_id, goal_def in GOALS.items():
        contributions: List[GoalRiskContribution] = []
        total_impact = 0.0

        for risk_id, impacts in RISK_GOAL_IMPACTS.items():
            for impact in impacts:
                if impact.goal_id != goal_id:
                    continue

                prob = risk_probs.get(risk_id, 0.0)
                if prob == 0:
                    continue

                impact_mean = pert_mean(
                    impact.impact_low,
                    impact.impact_likely,
                    impact.impact_high
                )
                expected = prob * impact_mean
                total_impact += expected

                contributions.append(GoalRiskContribution(
                    risk_id=risk_id,
                    risk_name=risk_names.get(risk_id, risk_id),
                    probability=prob,
                    impact_if_occurs=impact_mean,
                    expected_impact=expected,
                    unit=goal_def.unit.value,
                ))

        # Impact signs already encode direction:
        # positive impact = worse for lower_better goals (more months, more cost)
        # negative impact = worse for higher_better goals (less completion, less quality)

        # G9 (City Control) uses a variable baseline: scenarios where the city
        # has no structural involvement start at a lower control ceiling.
        # Formula: 40 + 8*(F6-1) + 7*(F7-1)
        #   F6=5, F7=5 → 100 (maximum: city owns and enforces everything)
        #   F6=1, F7=3 →  54 (moderate: city has contractual leverage only)
        #   F6=1, F7=1 →  40 (minimum: city is just a regulator)
        if goal_id == "G9":
            scenario = SCENARIO_FACTORS.get(scenario_id)
            if scenario:
                baseline = 40.0 + 8.0 * (scenario.F6 - 1) + 7.0 * (scenario.F7 - 1)
            else:
                baseline = goal_def.baseline
        else:
            baseline = goal_def.baseline

        expected_value = baseline + total_impact

        goal_scores[goal_id] = GoalScore(
            goal_id=goal_id,
            goal_name_is=goal_def.name_is,
            goal_name_en=goal_def.name_en,
            unit=goal_def.unit.value,
            baseline=baseline,
            expected_impact=total_impact,
            expected_value=expected_value,
            risk_contributions=contributions,
        )

    scenario = SCENARIO_FACTORS.get(scenario_id)
    return ScenarioGoalProfile(
        scenario_id=scenario_id,
        scenario_name_is=scenario.name_is if scenario else scenario_id,
        scenario_name_en=scenario.name_en if scenario else scenario_id,
        goal_scores=goal_scores,
    )


def calculate_weighted_score(
    scenario_id: str,
    weights: Dict[str, float],
    normalize: bool = True,
) -> Optional[WeightedScenarioScore]:
    """
    Calculate overall scenario score with weighted goals.
    Lower score = better scenario.
    """
    profile = calculate_scenario_goal_profile(scenario_id)
    if not profile:
        return None

    # Normalization factors to make different units comparable.
    # Calibrated to actual spread across scenarios so each goal
    # contributes ~1.0 unit of differentiation at weight=1.
    # Sign convention: positive for lower_better, negative for higher_better.
    # Recalibrated in v5 for 33-risk model.
    NORMALIZERS = {
        "G1":  0.023171,   # Infra Speed: spread ~43 months
        "G2":  0.006498,   # Construction Speed: spread ~154 months
        "G3":  0.022491,   # Affordability: spread ~44 pp
        "G4":  0.000225,   # City Financial: spread ~4453 M ISK
        "G5": -0.005898,   # Completion: spread ~170 pp
        "G6": -0.025075,   # Infra Budget: spread ~40 pp
        "G7": -0.023433,   # Infra Quality: spread ~43 pts
        "G8": -0.014442,   # Construction Quality: spread ~69 pts
        "G9": -0.009893,   # City Control: spread ~101 pts (incl. variable baseline)
        "G10": -0.015430,  # Social Mix: spread ~65 pp
    }

    total = 0.0
    contributions: Dict[str, float] = {}

    for goal_id, weight in weights.items():
        goal_score = profile.goal_scores.get(goal_id)
        if not goal_score:
            continue

        impact = goal_score.expected_impact

        # G9 has a variable baseline (depends on F6/F7). The scorer must
        # include the baseline gap so scenarios with less city involvement
        # are penalized structurally, not just by risk damage.
        if goal_id == "G9":
            g9_max_baseline = 100.0  # F6=5, F7=5
            baseline_penalty = goal_score.baseline - g9_max_baseline
            impact = impact + baseline_penalty

        if normalize:
            normalizer = NORMALIZERS.get(goal_id, 1.0)
            normalized_impact = impact * normalizer
        else:
            normalized_impact = impact

        weighted_contribution = abs(normalized_impact) * weight
        total += weighted_contribution
        contributions[goal_id] = weighted_contribution

    scenario = SCENARIO_FACTORS.get(scenario_id)
    return WeightedScenarioScore(
        scenario_id=scenario_id,
        scenario_name_is=scenario.name_is if scenario else scenario_id,
        total_score=total,
        goal_contributions=contributions,
    )


def rank_scenarios(
    weights: Dict[str, float],
    scenario_ids: Optional[List[str]] = None,
) -> List[WeightedScenarioScore]:
    """
    Rank all scenarios by weighted goal score.
    Returns sorted list (best first = lowest score).
    """
    if scenario_ids is None:
        scenario_ids = list(SCENARIO_FACTORS.keys())

    scores = []
    for sid in scenario_ids:
        score = calculate_weighted_score(sid, weights)
        if score:
            scores.append(score)

    scores.sort(key=lambda x: x.total_score)

    for i, score in enumerate(scores):
        score.rank = i + 1

    return scores


def compare_scenarios_by_goals(
    scenario_ids: List[str],
) -> Dict[str, Dict[str, float]]:
    """
    Compare scenarios across all goals.
    Returns dict[scenario_id][goal_id] = expected_impact
    """
    result: Dict[str, Dict[str, float]] = {}

    for sid in scenario_ids:
        profile = calculate_scenario_goal_profile(sid)
        if profile:
            result[sid] = {
                gid: gs.expected_impact
                for gid, gs in profile.goal_scores.items()
            }

    return result


def find_best_scenario_per_goal(
    scenario_ids: Optional[List[str]] = None,
) -> Dict[str, Tuple[str, float]]:
    """
    Find which scenario is best for each goal.
    Returns dict[goal_id] = (best_scenario_id, expected_impact)
    """
    if scenario_ids is None:
        scenario_ids = list(SCENARIO_FACTORS.keys())

    comparison = compare_scenarios_by_goals(scenario_ids)

    result: Dict[str, Tuple[str, float]] = {}

    for goal_id in GOALS.keys():
        goal_def = GOALS[goal_id]
        best_scenario = None
        best_impact = float('inf') if goal_def.direction == "lower_better" else float('-inf')

        for sid, impacts in comparison.items():
            impact = impacts.get(goal_id, 0)

            if goal_def.direction == "lower_better":
                if impact < best_impact:
                    best_impact = impact
                    best_scenario = sid
            else:
                if impact > best_impact:
                    best_impact = impact
                    best_scenario = sid

        if best_scenario:
            result[goal_id] = (best_scenario, best_impact)

    return result


# ─────────────────────────────────────────────────────────────────
# Default Goal Weights
# ─────────────────────────────────────────────────────────────────

WEIGHTS_BALANCED: Dict[str, float] = {
    "G1": 1.0, "G2": 1.0, "G3": 1.0, "G4": 1.0, "G5": 1.0,
    "G6": 1.0, "G7": 1.0, "G8": 1.0, "G9": 1.0, "G10": 1.0,
}

WEIGHTS_SPEED_FOCUSED: Dict[str, float] = {
    "G1": 2.0, "G2": 2.0, "G3": 1.0, "G4": 0.5, "G5": 1.5,
    "G6": 0.5, "G7": 0.5, "G8": 0.5, "G9": 0.5, "G10": 0.5,
}

WEIGHTS_FISCAL_FOCUSED: Dict[str, float] = {
    "G1": 0.5, "G2": 0.5, "G3": 1.0, "G4": 2.0, "G5": 1.0,
    "G6": 2.0, "G7": 1.0, "G8": 0.5, "G9": 1.0, "G10": 0.5,
}

WEIGHTS_SOCIAL_FOCUSED: Dict[str, float] = {
    "G1": 1.0, "G2": 1.5, "G3": 2.0, "G4": 0.5, "G5": 1.5,
    "G6": 0.5, "G7": 1.0, "G8": 1.5, "G9": 1.0, "G10": 2.0,
}

WEIGHTS_CONTROL_FOCUSED: Dict[str, float] = {
    "G1": 0.5, "G2": 0.5, "G3": 1.0, "G4": 1.0, "G5": 1.5,
    "G6": 1.0, "G7": 1.5, "G8": 1.5, "G9": 2.0, "G10": 1.5,
}

WEIGHTS_CITY_CRO: Dict[str, float] = {
    "G1": 1.5, "G2": 2.0, "G3": 1.5, "G4": 1.0, "G5": 2.0,
    "G6": 1.0, "G7": 1.0, "G8": 0.5, "G9": 1.5, "G10": 1.5,
}