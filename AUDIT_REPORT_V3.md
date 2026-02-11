# HALLAR DSS — Pre-Build Audit Results (v3)

## AUDIT RESULT: 2452 PASSED, 0 FAILED, 0 WARNINGS

---

## CHANGES APPLIED

### 1. CRITICAL: risk_calculator.py — Full Rewrite to Logistic Model

**Problem:** The capped multiplicative model destroyed information in 20% of calculations.
Two caps (×2.5 modifier + 0.99 probability) created indefensible results:
- Understated risk for compounding bad factors (S9×R11: 37.5% → should be ~89%)
- Overstated risk for moderate cases (S7×R16: 99% → should be ~65%)

**Fix:** Replaced with logistic (sigmoid) transformation through log-odds space.
Added output clamping at `[1e-15, 1-1e-15]` to handle float64 precision limits
where sigmoid rounds to exactly 0 or 1 at |log-odds| > ~36.

**Impact:** 48 large disagreements (>10pp) resolved. Rankings shift slightly
but directional conclusions unchanged (S4 still best, S9 still worst).

### 2. DATA FIX: G6 Single-Risk Dependency Eliminated

**Problem:** G6 (Infrastructure Budget Adherence) depended on only R08.
Every other goal had 2-8 contributing risks.

**Fix:** Added:
- R09 (Quality Defects) → G6: -5/-10/-20 pp impact  
  _Rationale: rework from quality issues increases cost and reduces budget adherence_
- R10 (Infrastructure Delays) → G6: -5/-15/-30 pp impact  
  _Rationale: delays cause inflation and standby costs that erode budget_
- Updated `affected_goals` in risk_sensitivities.py for both R09 and R10

**Impact:** G6 now has 3 contributing risks. More robust to calibration errors.

### 3. DATA FIX: 4 Missing Risk-Factor Sensitivities Added

All LOW sensitivity — adds nuance without changing rankings:

| Risk | Factor | Direction | Rationale |
|------|--------|-----------|-----------|
| R04 (Change Requests) | F7 | Protective | Strong city contracts limit permissible changes |
| R11 (Contractor Bankruptcy) | F7 | Protective | Performance bonds and step-in rights |
| R17 (Coordination Failure) | F2 | Protective | Strong contractors have internal coordination capacity |
| R21 (Competing Developments) | F3 | Protective | Patient capital absorbs competitive pressure |

### 4. CODE FIX: Dead if/else Removed from goal_scoring.py

**Problem:** Lines had identical branches for `lower_better` and `higher_better`.
Not a bug (impact signs encode direction) but misleading for auditors.

**Fix:** Replaced with single line + explanatory comment.

### 5. DATA FIX: 10 Short Justifications Expanded

The following justifications were under 80 characters — too brief for legal review:

- S3.F6, S3.F7, S5.F6, S5.F7, S6.F6, S7.F6, S8.F6, S9.F6, S12.F6, S12.F7

All expanded with scenario-specific context explaining WHY the score applies
to that particular development structure.

### 6. CALCULATOR FIX: Logistic Output Clamping (justifications_and_calculator.py)

**Problem:** The standalone logistic calculator in the justifications file had
overflow protection at ±700 log-odds, but float64 sigmoid rounds to exactly
0.0/1.0 at |log-odds| > ~36, below the overflow threshold.

**Fix:** Added `max(1e-15, min(1-1e-15, result))` after sigmoid computation.

---

## FILES CHANGED

| File | Changes |
|------|---------|
| `risk_calculator.py` | **Full rewrite** — logistic model, output clamping, removed caps |
| `risk_sensitivities.py` | +4 sensitivities, +2 affected_goals updates |
| `goal_impacts.py` | +2 new risk-goal impacts (R09→G6, R10→G6) |
| `goal_scoring.py` | Dead if/else → single line + comment |
| `justifications_and_calculator.py` | Output clamping fix, 10 justification expansions |
| `structural_factors.py` | **No changes** |
| `__init__.py` | **No changes** |

---

## VERIFICATION CHECKLIST (ALL PASSING)

- [x] 12 scenarios, 28 risks, 10 goals — all present
- [x] All 84 factor values in 1-5 range
- [x] Base probability ordering (low ≤ likely ≤ high) for all 28 risks
- [x] All base probabilities in (0, 1)
- [x] No duplicate sensitivities
- [x] All sensitivity factor references valid
- [x] requires_factors ranges valid (R23 correctly gates on F3)
- [x] affected_goals matches RISK_GOAL_IMPACTS for all 28 risks
- [x] Impact magnitude ordering preserved for all 84 impacts
- [x] Impact signs match goal direction for all 84 impacts
- [x] Every goal has ≥2 contributing risks
- [x] Factor effect = 1.0 at neutral (score=3) for all combinations
- [x] Factor effect monotonic for all direction/sensitivity combinations
- [x] Logistic identity: f(p, []) = p for all test points
- [x] All 1008 logistic calculations in strict (0, 1) bounds
- [x] PERT ordering preserved after logistic for all combinations
- [x] Logistic overflow protection handles extreme values
- [x] Logistic monotonicity: worse factors always increase risk
- [x] Dead code removed
- [x] Normalizers cover all 10 goals with correct signs
- [x] abs() in scoring is safe (no risks improve goals)
- [x] S4 rank 1, S9 rank 12 on balanced weights
- [x] All 84 justifications present and >80 characters
- [x] All 84 justification scores match actual factor values
- [x] All 28 confidence tiers valid
- [x] 0 model disagreements >10pp (logistic is now the model)
- [x] All scenarios have 25+ applicable risks
- [x] PERT mean formula correct
- [x] Rankings stable (no ties)
- [x] Goal baselines in expected ranges

**Total automated checks: 2452 passed, 0 failed, 0 warnings**
