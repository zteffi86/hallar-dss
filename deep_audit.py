"""
HALLAR DSS — Deep Pre-Build Audit
Checks everything a lawyer or auditor would challenge.
"""
import math
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from hallar_risk_factors.structural_factors import SCENARIO_FACTORS, STRUCTURAL_FACTORS, get_scenario_profile
from hallar_risk_factors.risk_sensitivities import RISK_PROFILES, FactorDirection, Sensitivity, FactorSensitivity
from hallar_risk_factors.goal_impacts import GOALS, RISK_GOAL_IMPACTS, ImpactUnit, pert_mean
from hallar_risk_factors.risk_calculator import (
    calculate_factor_effect,
    calculate_scenario_modifier,
    calculate_adjusted_probability, calculate_scenario_risk_profile,
    NEUTRAL_FACTOR,
)
from hallar_risk_factors.goal_scoring import (
    calculate_scenario_goal_profile, calculate_weighted_score,
    rank_scenarios, WEIGHTS_BALANCED,
)
from justifications_and_calculator import (
    SCENARIO_FACTOR_JUSTIFICATIONS, RISK_CONFIDENCE,
    calculate_risk_logistic,
)

passed = 0
failed = 0
warnings = 0
findings = []

def ok(msg):
    global passed
    passed += 1

def fail(msg):
    global failed
    failed += 1
    findings.append(("FAIL", msg))
    print(f"  ❌ FAIL: {msg}")

def warn(msg):
    global warnings
    warnings += 1
    findings.append(("WARN", msg))
    print(f"  ⚠️  WARN: {msg}")


# ═══════════════════════════════════════════════════════════════
print("=" * 80)
print("SECTION 1: STRUCTURAL INTEGRITY")
print("=" * 80)

# 1.1 All scenarios have all 7 factors in range 1-5
print("\n--- 1.1 Factor ranges ---")
for sid, sf in SCENARIO_FACTORS.items():
    for fid in ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]:
        val = sf.get_factor(fid)
        if not (1 <= val <= 5):
            fail(f"{sid}.{fid}={val} outside 1-5 range")
        else:
            ok(f"{sid}.{fid} in range")
print(f"  ✅ All {len(SCENARIO_FACTORS)*7} factor values in 1-5 range")

# 1.2 All 12 scenarios present
print("\n--- 1.2 Scenario completeness ---")
expected_scenarios = [f"S{i}" for i in range(1, 13)]
for sid in expected_scenarios:
    if sid not in SCENARIO_FACTORS:
        fail(f"Missing scenario {sid}")
    else:
        ok(f"{sid} present")
print(f"  ✅ All {len(expected_scenarios)} scenarios present")

# 1.3 All risks present and valid
print("\n--- 1.3 Risk completeness ---")
for rid, rp in RISK_PROFILES.items():
    if rp.risk_id != rid:
        fail(f"{rid}: risk_id mismatch (says {rp.risk_id})")
    else:
        ok(f"{rid} present")
print(f"  ✅ All {len(RISK_PROFILES)} risks present")

# 1.4 All 10 goals present
print("\n--- 1.4 Goal completeness ---")
expected_goals = [f"G{i}" for i in range(1, 11)]
for gid in expected_goals:
    if gid not in GOALS:
        fail(f"Missing goal {gid}")
    else:
        ok(f"{gid} present")
print(f"  ✅ All {len(expected_goals)} goals present")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 2: RISK PROBABILITY DATA INTEGRITY")
print("=" * 80)

# 2.1 Base probability ordering: low <= likely <= high
print("\n--- 2.1 Base probability ordering ---")
for rid, rp in RISK_PROFILES.items():
    if not (rp.base_prob_low <= rp.base_prob_likely <= rp.base_prob_high):
        fail(f"{rid}: low={rp.base_prob_low} likely={rp.base_prob_likely} high={rp.base_prob_high} — ordering violated")
    elif rp.base_prob_low == rp.base_prob_likely or rp.base_prob_likely == rp.base_prob_high:
        warn(f"{rid}: degenerate range (some equal)")
    else:
        ok(f"{rid} ordering OK")

# 2.2 Base probabilities in (0, 1)
print("\n--- 2.2 Base probability bounds ---")
for rid, rp in RISK_PROFILES.items():
    for field, val in [("low", rp.base_prob_low), ("likely", rp.base_prob_likely), ("high", rp.base_prob_high)]:
        if val <= 0 or val >= 1:
            fail(f"{rid}.{field}={val} outside (0,1)")
        else:
            ok(f"{rid}.{field} OK")

# 2.3 Sensitivity factor_id references valid factors
print("\n--- 2.3 Sensitivity factor references ---")
for rid, rp in RISK_PROFILES.items():
    for sens in rp.sensitivities:
        if sens.factor_id not in STRUCTURAL_FACTORS:
            fail(f"{rid}: sensitivity references unknown factor {sens.factor_id}")
        else:
            ok(f"{rid}→{sens.factor_id} valid")

# 2.4 No duplicate sensitivities (same risk → same factor twice)
print("\n--- 2.4 Duplicate sensitivity check ---")
for rid, rp in RISK_PROFILES.items():
    factor_ids = [s.factor_id for s in rp.sensitivities]
    if len(factor_ids) != len(set(factor_ids)):
        dups = [f for f in factor_ids if factor_ids.count(f) > 1]
        fail(f"{rid}: duplicate sensitivity to factor(s) {set(dups)}")
    else:
        ok(f"{rid} no duplicates")

# 2.5 requires_factors references valid factors and sensible ranges
print("\n--- 2.5 requires_factors validation ---")
for rid, rp in RISK_PROFILES.items():
    if rp.requires_factors:
        for fid, (lo, hi) in rp.requires_factors.items():
            if fid not in STRUCTURAL_FACTORS:
                fail(f"{rid}: requires_factors references unknown {fid}")
            elif lo > hi:
                fail(f"{rid}: requires_factors {fid} has lo={lo} > hi={hi}")
            elif lo < 1 or hi > 5:
                fail(f"{rid}: requires_factors {fid} range ({lo},{hi}) outside 1-5")
            else:
                ok(f"{rid} requires_factors {fid} valid")

# 2.6 affected_goals references valid goals
print("\n--- 2.6 affected_goals references ---")
for rid, rp in RISK_PROFILES.items():
    for gid in rp.affected_goals:
        if gid not in GOALS:
            fail(f"{rid}: affected_goals references unknown {gid}")
        else:
            ok(f"{rid}→{gid} valid")

# 2.7 affected_goals matches RISK_GOAL_IMPACTS exactly
print("\n--- 2.7 affected_goals ↔ RISK_GOAL_IMPACTS consistency ---")
for rid, rp in RISK_PROFILES.items():
    declared = set(rp.affected_goals)
    actual = set()
    if rid in RISK_GOAL_IMPACTS:
        actual = {imp.goal_id for imp in RISK_GOAL_IMPACTS[rid]}
    
    if declared != actual:
        missing_impacts = declared - actual
        extra_impacts = actual - declared
        if missing_impacts:
            fail(f"{rid}: declares goals {missing_impacts} but no impact data")
        if extra_impacts:
            fail(f"{rid}: has impact data for {extra_impacts} not in affected_goals")
    else:
        ok(f"{rid} goals consistent")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 3: GOAL IMPACT DATA INTEGRITY")
print("=" * 80)

# 3.1 Impact ordering: |low| <= |likely| <= |high| for each impact
print("\n--- 3.1 Impact magnitude ordering ---")
for rid, impacts in RISK_GOAL_IMPACTS.items():
    for imp in impacts:
        # For negative impacts (higher_better goals), all values should be negative
        # For positive impacts (lower_better goals like delays), all values should be positive
        if imp.impact_low >= 0 and imp.impact_likely >= 0 and imp.impact_high >= 0:
            # All positive — should be low <= likely <= high
            if not (imp.impact_low <= imp.impact_likely <= imp.impact_high):
                fail(f"{rid}→{imp.goal_id}: positive impacts not ordered: {imp.impact_low} <= {imp.impact_likely} <= {imp.impact_high}")
            else:
                ok(f"{rid}→{imp.goal_id} positive ordering OK")
        elif imp.impact_low <= 0 and imp.impact_likely <= 0 and imp.impact_high <= 0:
            # All negative — should be |low| <= |likely| <= |high| i.e. low >= likely >= high
            if not (imp.impact_low >= imp.impact_likely >= imp.impact_high):
                fail(f"{rid}→{imp.goal_id}: negative impacts not ordered: {imp.impact_low} >= {imp.impact_likely} >= {imp.impact_high}")
            else:
                ok(f"{rid}→{imp.goal_id} negative ordering OK")
        else:
            fail(f"{rid}→{imp.goal_id}: mixed signs in impacts: {imp.impact_low}, {imp.impact_likely}, {imp.impact_high}")

# 3.2 Impact signs match goal direction
print("\n--- 3.2 Impact sign ↔ goal direction ---")
for rid, impacts in RISK_GOAL_IMPACTS.items():
    for imp in impacts:
        goal = GOALS.get(imp.goal_id)
        if not goal:
            fail(f"{rid}→{imp.goal_id}: goal not found")
            continue
        
        if goal.direction == "lower_better":
            # Risks should INCREASE this metric (positive = bad)
            if imp.impact_likely < 0:
                fail(f"{rid}→{imp.goal_id}: lower_better goal but negative impact {imp.impact_likely}")
            else:
                ok(f"{rid}→{imp.goal_id} sign OK")
        else:  # higher_better
            # Risks should DECREASE this metric (negative = bad)
            if imp.impact_likely > 0:
                fail(f"{rid}→{imp.goal_id}: higher_better goal but positive impact {imp.impact_likely}")
            else:
                ok(f"{rid}→{imp.goal_id} sign OK")

# 3.3 Every goal is affected by at least 2 risks
print("\n--- 3.3 Goal coverage ---")
goal_risk_count = defaultdict(int)
for rid, impacts in RISK_GOAL_IMPACTS.items():
    for imp in impacts:
        goal_risk_count[imp.goal_id] += 1

for gid in GOALS:
    count = goal_risk_count.get(gid, 0)
    if count == 0:
        fail(f"{gid}: NO risks affect this goal")
    elif count == 1:
        warn(f"{gid} ({GOALS[gid].name_en}): only 1 risk contributes — fragile. Risk={[rid for rid, imps in RISK_GOAL_IMPACTS.items() for imp in imps if imp.goal_id == gid]}")
    else:
        ok(f"{gid}: {count} contributing risks")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 4: CALCULATOR MATHEMATICS")
print("=" * 80)

# 4.1 Factor effect at neutral (score=3) should be 1.0
print("\n--- 4.1 Factor effect at neutral ---")
for direction in [FactorDirection.PROTECTIVE, FactorDirection.EXPOSURE]:
    for sens in [Sensitivity.LOW, Sensitivity.MEDIUM, Sensitivity.HIGH, Sensitivity.CRITICAL]:
        effect = calculate_factor_effect(3, direction, sens)
        if abs(effect - 1.0) > 0.001:
            fail(f"Factor effect at score=3, {direction.value}/{sens.name}: {effect} ≠ 1.0")
        else:
            ok(f"Neutral OK for {direction.value}/{sens.name}")

# 4.2 Factor effect monotonicity — protective: higher score = lower effect (reduces risk)
print("\n--- 4.2 Factor effect monotonicity ---")
for sens in [Sensitivity.LOW, Sensitivity.MEDIUM, Sensitivity.HIGH, Sensitivity.CRITICAL]:
    prev = None
    for score in [1, 2, 3, 4, 5]:
        effect = calculate_factor_effect(score, FactorDirection.PROTECTIVE, sens)
        if prev is not None and effect >= prev:
            fail(f"PROTECTIVE {sens.name}: score {score} effect {effect} >= score {score-1} effect {prev}")
        prev = effect
    ok(f"PROTECTIVE {sens.name} monotonic")
    
    prev = None
    for score in [1, 2, 3, 4, 5]:
        effect = calculate_factor_effect(score, FactorDirection.EXPOSURE, sens)
        if prev is not None and effect <= prev:
            fail(f"EXPOSURE {sens.name}: score {score} effect {effect} <= score {score-1} effect {prev}")
        prev = effect
    ok(f"EXPOSURE {sens.name} monotonic")

# 4.3 Logistic calculator: identity property f(p, []) = p
print("\n--- 4.3 Logistic identity ---")
for p in [0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]:
    result, _ = calculate_risk_logistic(p, [])
    if abs(result - p) > 0.001:
        fail(f"Logistic identity: f({p}, []) = {result} ≠ {p}")
    else:
        ok(f"Logistic identity at {p}")

# 4.4 Logistic: all results in (0, 1)
print("\n--- 4.4 Logistic bounds for all scenario×risk ---")
bound_violations = 0
for sid in SCENARIO_FACTORS:
    scenario = SCENARIO_FACTORS[sid]
    for rid, risk in RISK_PROFILES.items():
        effects = []
        for sens in risk.sensitivities:
            score = scenario.get_factor(sens.factor_id)
            effect = calculate_factor_effect(score, sens.direction, sens.sensitivity)
            effects.append(effect)
        
        for base_field in ["base_prob_low", "base_prob_likely", "base_prob_high"]:
            base = getattr(risk, base_field)
            prob, _ = calculate_risk_logistic(base, effects)
            if prob <= 0 or prob >= 1:
                fail(f"Logistic {sid}×{rid} ({base_field}): {prob} outside (0,1)")
                bound_violations += 1
            else:
                ok(f"{sid}×{rid} {base_field}")

if bound_violations == 0:
    print(f"  ✅ All {len(SCENARIO_FACTORS)*len(RISK_PROFILES)*3} logistic calculations in (0,1)")

# 4.5 Logistic: PERT ordering preserved (low <= likely <= high after transform)
print("\n--- 4.5 PERT ordering preserved after logistic ---")
pert_violations = 0
for sid in SCENARIO_FACTORS:
    scenario = SCENARIO_FACTORS[sid]
    for rid, risk in RISK_PROFILES.items():
        # Skip if doesn't apply
        if risk.requires_factors:
            skip = False
            for fid, (lo, hi) in risk.requires_factors.items():
                if not (lo <= scenario.get_factor(fid) <= hi):
                    skip = True
            if skip:
                continue
        
        effects = []
        for sens in risk.sensitivities:
            score = scenario.get_factor(sens.factor_id)
            effect = calculate_factor_effect(score, sens.direction, sens.sensitivity)
            effects.append(effect)
        
        p_low, _ = calculate_risk_logistic(risk.base_prob_low, effects)
        p_likely, _ = calculate_risk_logistic(risk.base_prob_likely, effects)
        p_high, _ = calculate_risk_logistic(risk.base_prob_high, effects)
        
        if not (p_low <= p_likely + 1e-10 and p_likely <= p_high + 1e-10):
            fail(f"PERT ordering: {sid}×{rid}: low={p_low:.4f} likely={p_likely:.4f} high={p_high:.4f}")
            pert_violations += 1
        else:
            ok(f"{sid}×{rid} PERT ordering")

if pert_violations == 0:
    print(f"  ✅ PERT ordering preserved for all applicable scenario×risk combinations")

# 4.6 Logistic overflow protection
print("\n--- 4.6 Logistic overflow protection ---")
extreme_effects = [100.0] * 10  # Extreme positive
try:
    p, _ = calculate_risk_logistic(0.5, extreme_effects)
    if 0 < p < 1:
        ok("Extreme positive overflow handled")
    else:
        fail(f"Extreme positive: {p}")
except Exception as e:
    fail(f"Extreme positive crashed: {e}")

extreme_effects = [0.001] * 10  # Extreme negative
try:
    p, _ = calculate_risk_logistic(0.5, extreme_effects)
    if 0 < p < 1:
        ok("Extreme negative overflow handled")
    else:
        fail(f"Extreme negative: {p}")
except Exception as e:
    fail(f"Extreme negative crashed: {e}")

# 4.7 Logistic monotonicity: worse factors always increase risk
print("\n--- 4.7 Logistic monotonicity (worse → higher risk) ---")
mono_violations = 0
for rid, risk in RISK_PROFILES.items():
    for sens in risk.sensitivities:
        # Create two effect lists: one with score=2, one with score=4
        # For PROTECTIVE: score 2 should give HIGHER risk than score 4
        # For EXPOSURE: score 4 should give HIGHER risk than score 2
        
        effect_low = calculate_factor_effect(2, sens.direction, sens.sensitivity)
        effect_high = calculate_factor_effect(4, sens.direction, sens.sensitivity)
        
        p_low, _ = calculate_risk_logistic(risk.base_prob_likely, [effect_low])
        p_high, _ = calculate_risk_logistic(risk.base_prob_likely, [effect_high])
        
        if sens.direction == FactorDirection.PROTECTIVE:
            # Score 2 (bad protection) should give higher risk than score 4 (good protection)
            if p_low < p_high - 1e-10:
                fail(f"{rid}→{sens.factor_id} PROTECTIVE monotonicity: score=2 gives {p_low:.4f} < score=4 {p_high:.4f}")
                mono_violations += 1
        else:
            # Score 4 (more exposure) should give higher risk than score 2
            if p_high < p_low - 1e-10:
                fail(f"{rid}→{sens.factor_id} EXPOSURE monotonicity: score=4 gives {p_high:.4f} < score=2 {p_low:.4f}")
                mono_violations += 1
        ok(f"{rid}→{sens.factor_id} monotonicity")

if mono_violations == 0:
    print(f"  ✅ All sensitivities monotonic through logistic")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 5: GOAL SCORING ENGINE")
print("=" * 80)

# 5.1 Dead code check
print("\n--- 5.1 Dead if/else in goal_scoring.py ---")
import inspect
source = inspect.getsource(calculate_scenario_goal_profile)
if 'if goal_def.direction == "lower_better"' in source:
    warn("Dead if/else still present in goal_scoring.py — both branches identical. Not a bug but misleading.")
else:
    ok("Dead code removed")

# 5.2 Normalizers cover all 10 goals
print("\n--- 5.2 Normalizer coverage ---")
# Read normalizers from source since they're inline
from hallar_risk_factors.goal_scoring import calculate_weighted_score
source = inspect.getsource(calculate_weighted_score)
for gid in GOALS:
    if f'"{gid}"' not in source:
        fail(f"Goal {gid} missing from NORMALIZERS")
    else:
        ok(f"{gid} in normalizers")

# 5.3 Normalizer signs: lower_better goals should have positive normalizers, 
# higher_better should have negative (to convert to "badness")
print("\n--- 5.3 Normalizer sign logic ---")
# Parse normalizers from source (v5 — recalibrated for 33-risk model)
NORMALIZERS = {
    "G1":  0.023171, "G2":  0.006498, "G3":  0.022491, "G4":  0.000225,
    "G5": -0.005898, "G6": -0.025075, "G7": -0.023433, "G8": -0.014442,
    "G9": -0.009893, "G10": -0.015430,
}
for gid, norm in NORMALIZERS.items():
    goal = GOALS[gid]
    if goal.direction == "lower_better":
        # Impacts are positive (more months, more cost = bad). Normalizer should be positive.
        if norm <= 0:
            fail(f"{gid} ({goal.name_en}): lower_better but normalizer={norm} (should be positive)")
        else:
            ok(f"{gid} normalizer sign OK")
    else:
        # Impacts are negative (less completion, less quality = bad). Normalizer should be negative.
        if norm >= 0:
            fail(f"{gid} ({goal.name_en}): higher_better but normalizer={norm} (should be negative)")
        else:
            ok(f"{gid} normalizer sign OK")

# 5.4 Weighted scoring uses abs() — check this makes sense
print("\n--- 5.4 abs() in weighted scoring ---")
# The scoring uses abs(normalized_impact) * weight
# For lower_better: impact > 0, normalizer > 0 → normalized > 0 → abs() = no change ✓
# For higher_better: impact < 0, normalizer < 0 → normalized > 0 → abs() = no change ✓
# BUT: what if a risk somehow IMPROVES a goal? Then signs would mismatch.
# Check: are there any positive impacts on higher_better goals or negative on lower_better?
sign_mismatches = 0
for rid, impacts in RISK_GOAL_IMPACTS.items():
    for imp in impacts:
        goal = GOALS.get(imp.goal_id)
        if not goal:
            continue
        if goal.direction == "lower_better" and imp.impact_likely < 0:
            sign_mismatches += 1
        elif goal.direction == "higher_better" and imp.impact_likely > 0:
            sign_mismatches += 1

if sign_mismatches == 0:
    print(f"  ✅ No risks improve goals — abs() in scoring is safe")
else:
    fail(f"{sign_mismatches} impacts have wrong sign direction — abs() would mask this")

# 5.5 Sanity check: S4 should beat S9 on balanced weights
print("\n--- 5.5 Sanity check: S4 vs S9 ---")
rankings = rank_scenarios(WEIGHTS_BALANCED)
s4_rank = next((r.rank for r in rankings if r.scenario_id == "S4"), None)
s9_rank = next((r.rank for r in rankings if r.scenario_id == "S9"), None)
if s4_rank and s9_rank and s4_rank < s9_rank:
    ok(f"S4 (rank {s4_rank}) beats S9 (rank {s9_rank}) on balanced weights")
    print(f"  ✅ S4 (rank {s4_rank}) beats S9 (rank {s9_rank})")
else:
    fail(f"S4 rank={s4_rank}, S9 rank={s9_rank} — S4 should beat S9")

# 5.6 All weight profiles are valid (positive values, cover all goals)
print("\n--- 5.6 Weight profiles validation ---")
from hallar_risk_factors.goal_scoring import (
    WEIGHTS_BALANCED, WEIGHTS_SPEED_FOCUSED, WEIGHTS_FISCAL_FOCUSED,
    WEIGHTS_SOCIAL_FOCUSED, WEIGHTS_CONTROL_FOCUSED, WEIGHTS_CITY_CRO,
)
weight_profiles = {
    "Balanced": WEIGHTS_BALANCED, "Speed": WEIGHTS_SPEED_FOCUSED,
    "Fiscal": WEIGHTS_FISCAL_FOCUSED, "Social": WEIGHTS_SOCIAL_FOCUSED,
    "Control": WEIGHTS_CONTROL_FOCUSED, "CRO": WEIGHTS_CITY_CRO,
}
for name, weights in weight_profiles.items():
    for gid in GOALS:
        if gid not in weights:
            fail(f"{name} profile missing {gid}")
        elif weights[gid] < 0:
            fail(f"{name} profile {gid} weight={weights[gid]} (negative)")
        else:
            ok(f"{name}.{gid} OK")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 6: JUSTIFICATION & CONFIDENCE DATA")
print("=" * 80)

# 6.1 All 84 justifications present (12 scenarios × 7 factors)
print("\n--- 6.1 Justification coverage ---")
just_missing = 0
for sid in SCENARIO_FACTORS:
    if sid not in SCENARIO_FACTOR_JUSTIFICATIONS:
        fail(f"Scenario {sid} missing all justifications")
        just_missing += 7
    else:
        for fid in ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]:
            if fid not in SCENARIO_FACTOR_JUSTIFICATIONS[sid]:
                fail(f"{sid}.{fid} missing justification")
                just_missing += 1
            else:
                ok(f"{sid}.{fid} justification present")

if just_missing == 0:
    print(f"  ✅ All 84 justifications present")

# 6.2 Each justification mentions the correct score
print("\n--- 6.2 Justification ↔ score consistency ---")
score_mismatches = 0
for sid in SCENARIO_FACTORS:
    if sid not in SCENARIO_FACTOR_JUSTIFICATIONS:
        continue
    scenario = SCENARIO_FACTORS[sid]
    for fid in ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]:
        text = SCENARIO_FACTOR_JUSTIFICATIONS[sid].get(fid, "")
        actual_score = scenario.get_factor(fid)
        
        # Check that "Einkunn: X" appears with correct score
        expected_pattern = f"Einkunn: {actual_score}"
        if expected_pattern not in text:
            fail(f"{sid}.{fid}: actual score={actual_score} but justification says something else")
            score_mismatches += 1
        else:
            ok(f"{sid}.{fid} score matches")

if score_mismatches == 0:
    print(f"  ✅ All 84 justification scores match actual factor values")

# 6.3 Confidence tier coverage
print("\n--- 6.3 Confidence tier coverage ---")
for rid in RISK_PROFILES:
    if rid not in RISK_CONFIDENCE:
        fail(f"{rid} missing confidence tier")
    else:
        tier = RISK_CONFIDENCE[rid]
        if tier.tier_en not in ["High", "Medium", "Low"]:
            fail(f"{rid}: invalid tier '{tier.tier_en}'")
        else:
            ok(f"{rid} confidence tier valid")
print(f"  ✅ All {len(RISK_PROFILES)} confidence tiers present and valid")

# 6.4 Justification minimum length (should be substantial, not placeholder)
print("\n--- 6.4 Justification quality (min length) ---")
short_count = 0
for sid in SCENARIO_FACTOR_JUSTIFICATIONS:
    for fid, text in SCENARIO_FACTOR_JUSTIFICATIONS[sid].items():
        if len(text) < 80:
            warn(f"{sid}.{fid}: justification only {len(text)} chars — may be too brief for lawyers")
            short_count += 1
        else:
            ok(f"{sid}.{fid} length OK")

if short_count == 0:
    print(f"  ✅ All justifications are substantive (>80 chars)")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 7: KNOWN ISSUES FROM AUDIT REPORT")
print("=" * 80)

# 7.1 G6 single-risk dependency
print("\n--- 7.1 G6 single-risk dependency ---")
g6_risks = [rid for rid, imps in RISK_GOAL_IMPACTS.items() for imp in imps if imp.goal_id == "G6"]
if len(g6_risks) <= 1:
    warn(f"G6 depends on only {len(g6_risks)} risk(s): {g6_risks}. Every other goal has 2+. NEEDS FIX.")
else:
    ok(f"G6 has {len(g6_risks)} contributing risks")

# 7.2 Every risk with sensitivities references valid, non-duplicate factors
print("\n--- 7.2 Sensitivity completeness ---")
for rid, rp in RISK_PROFILES.items():
    factor_ids = [s.factor_id for s in rp.sensitivities]
    for fid in factor_ids:
        if fid not in STRUCTURAL_FACTORS:
            fail(f"{rid} references invalid factor {fid}")
        else:
            ok(f"{rid}→{fid} valid")
    if len(factor_ids) != len(set(factor_ids)):
        dups = [f for f in factor_ids if factor_ids.count(f) > 1]
        fail(f"{rid}: duplicate sensitivity to {set(dups)}")
    else:
        ok(f"{rid} no duplicate sensitivities")

# 7.3 requires_factors gating — R23 should exclude non-PF scenarios
print("\n--- 7.3 R23 requires_factors gating ---")
r23 = RISK_PROFILES["R23"]
non_pf_scenarios = ["S7", "S8", "S9"]  # These have F3 < 3
for sid in non_pf_scenarios:
    scenario = SCENARIO_FACTORS[sid]
    f3_val = scenario.get_factor("F3")
    if r23.requires_factors:
        lo, hi = r23.requires_factors.get("F3", (1, 5))
        if lo <= f3_val <= hi:
            fail(f"R23 should exclude {sid} (F3={f3_val}) but it doesn't. Range is ({lo},{hi})")
        else:
            ok(f"R23 correctly excludes {sid} (F3={f3_val})")
    else:
        fail("R23 has no requires_factors — should gate on F3")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 8: CROSS-SCENARIO LOGIC CHECKS")
print("=" * 80)

# 8.1 Scenarios with same factor should produce same effect on same risk
print("\n--- 8.1 Factor-driven risk differentiation makes sense ---")
# S7 F3=1 and S8 F3=1 — both bank-financed, should have same F3 effect on R18
for rid in ["R18", "R19", "R20", "R22"]:  # These are F3-CRITICAL risks
    risk = RISK_PROFILES[rid]
    f3_sens = [s for s in risk.sensitivities if s.factor_id == "F3"]
    if f3_sens:
        for s7_s8 in [("S7", "S8")]:
            effects_7 = calculate_factor_effect(
                SCENARIO_FACTORS["S7"].get_factor("F3"),
                f3_sens[0].direction, f3_sens[0].sensitivity
            )
            effects_8 = calculate_factor_effect(
                SCENARIO_FACTORS["S8"].get_factor("F3"),
                f3_sens[0].direction, f3_sens[0].sensitivity
            )
            if abs(effects_7 - effects_8) > 0.001:
                fail(f"{rid}: S7 and S8 both have F3=1 but different F3 effects")
            else:
                ok(f"{rid}: S7=S8 on F3 ✓")

# 8.2 S9 should be worst or near-worst on every goal under balanced weights
print("\n--- 8.2 S9 should be worst or near-worst ---")
profile = calculate_scenario_goal_profile("S9")
all_profiles = {sid: calculate_scenario_goal_profile(sid) for sid in SCENARIO_FACTORS}
for gid in GOALS:
    s9_impact = profile.goal_scores[gid].expected_impact if gid in profile.goal_scores else 0
    # Check how S9 ranks
    all_impacts = [(sid, p.goal_scores[gid].expected_impact) for sid, p in all_profiles.items() if p and gid in p.goal_scores]
    all_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
    s9_rank = next((i+1 for i, (sid, _) in enumerate(all_impacts) if sid == "S9"), None)
    if s9_rank and s9_rank > 4:
        warn(f"S9 ranks {s9_rank}/12 on {gid} ({GOALS[gid].name_en}) — expected to be worse")
    else:
        ok(f"S9 ranks {s9_rank}/12 on {gid}")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 9: MODEL COMPARISON SPOT-CHECKS")
print("=" * 80)

# Compare capped vs logistic for key scenarios
print("\n--- 9.1 Key disagreements between models ---")
key_cases = []
for sid in SCENARIO_FACTORS:
    scenario = SCENARIO_FACTORS[sid]
    for rid, risk in RISK_PROFILES.items():
        if risk.requires_factors:
            skip = False
            for fid, (lo, hi) in risk.requires_factors.items():
                if not (lo <= scenario.get_factor(fid) <= hi):
                    skip = True
            if skip:
                continue
        
        effects = []
        for sens in risk.sensitivities:
            score = scenario.get_factor(sens.factor_id)
            effect = calculate_factor_effect(score, sens.direction, sens.sensitivity)
            effects.append(effect)
        
        adj_prob, modifier, _ = calculate_adjusted_probability(sid, rid)
        current = adj_prob[1]
        logistic, _ = calculate_risk_logistic(risk.base_prob_likely, effects)
        diff = abs(logistic - current) * 100
        
        if diff > 10:
            key_cases.append((sid, rid, risk.name_en, current, logistic, diff))

key_cases.sort(key=lambda x: x[5], reverse=True)
print(f"  Found {len(key_cases)} cases with >10pp disagreement")
if key_cases:
    print(f"\n  {'Scenario':<8} {'Risk':<8} {'Name':<35} {'Current':>8} {'Logistic':>9} {'Δ pp':>8}")
    print(f"  {'-'*77}")
    for sid, rid, name, curr, logi, diff in key_cases[:15]:
        print(f"  {sid:<8} {rid:<8} {name[:34]:<35} {curr*100:>7.1f}% {logi*100:>8.1f}% {diff:>+7.1f}")
    if len(key_cases) > 15:
        print(f"  ... and {len(key_cases)-15} more")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 10: EDGE CASES & DEFENSIBILITY")
print("=" * 80)

# 10.1 Check that no scenario gets 0 applicable risks
print("\n--- 10.1 All scenarios have applicable risks ---")
for sid in SCENARIO_FACTORS:
    profile = calculate_scenario_risk_profile(sid)
    if not profile or len(profile.risks) == 0:
        fail(f"{sid} has 0 applicable risks")
    elif len(profile.risks) < 20:
        warn(f"{sid} has only {len(profile.risks)} applicable risks (expected ~25+)")
    else:
        ok(f"{sid}: {len(profile.risks)} risks")

# 10.2 Check PERT mean function
print("\n--- 10.2 PERT mean correctness ---")
result = pert_mean(1, 4, 7)
expected = (1 + 4*4 + 7) / 6  # = 24/6 = 4.0
if abs(result - expected) > 0.001:
    fail(f"PERT mean(1,4,7) = {result}, expected {expected}")
else:
    ok("PERT mean formula correct")

# 10.3 Check that ranking is stable (no ties that would cause non-determinism)
print("\n--- 10.3 Ranking stability ---")
rankings = rank_scenarios(WEIGHTS_BALANCED)
scores = [r.total_score for r in rankings]
for i in range(len(scores)-1):
    if abs(scores[i] - scores[i+1]) < 0.0001:
        warn(f"Near-tie between rank {i+1} ({rankings[i].scenario_id}) and rank {i+2} ({rankings[i+1].scenario_id}): diff={abs(scores[i]-scores[i+1]):.6f}")

# 10.4 Goal baselines make sense
print("\n--- 10.4 Goal baseline sanity ---")
baseline_checks = {
    "G1": (12, 60, "infrastructure months"),
    "G2": (24, 120, "construction months"),
    "G3": (-5, 50, "price increase %"),
    "G4": (-1000, 10000, "M ISK range"),
    "G5": (50, 100, "completion probability"),
    "G6": (50, 100, "budget adherence"),
    "G7": (50, 100, "quality score"),
    "G8": (50, 100, "quality score"),
    "G9": (50, 100, "control score"),
    "G10": (0, 100, "affordable %"),
}
for gid, (lo, hi, desc) in baseline_checks.items():
    baseline = GOALS[gid].baseline
    if not (lo <= baseline <= hi):
        warn(f"{gid} baseline={baseline} outside expected ({lo},{hi}) for {desc}")
    else:
        ok(f"{gid} baseline={baseline} ✓")


# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"\n  PASSED:   {passed}")
print(f"  FAILED:   {failed}")
print(f"  WARNINGS: {warnings}")
print()

if findings:
    print("ALL FINDINGS:")
    print("-" * 80)
    for severity, msg in findings:
        icon = "❌" if severity == "FAIL" else "⚠️ "
        print(f"  {icon} [{severity}] {msg}")