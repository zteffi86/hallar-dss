# HALLAR DSS — v5 Changes (33-risk model)

## AUDIT: 2,874 PASSED, 0 FAILED, 0 WARNINGS

---

## FILES CHANGED

| File | Changes |
|------|---------|
| `risk_sensitivities.py` | R29 F6 removed; R04/R11 affected_goals updated; R30 expanded; R34–R37 added |
| `goal_impacts.py` | R04→G9 removed; R11→G9 removed; R30 G4 added; R34–R37 impacts added |
| `goal_scoring.py` | G9 variable baseline; normalizer recalibration; G9 scorer fix |
| `deep_audit.py` | Normalizers updated |
| `justifications_and_calculator.py` | Confidence tiers for R34–R37 |
| `structural_factors.py` | **No changes** |
| `risk_calculator.py` | **No changes** |
| `__init__.py` | **No changes** |
| `app.py` | **No changes** |

---

## STRUCTURAL FIXES (3)

### Fix 1: R29 — F6 EXPOSURE removed

F6 EXPOSURE LOW on R29 (latent defect liability) was a who-pays question,
not a do-defects-exist question. City ownership doesn't cause defects.

### Fix 2: G9 (City Control) — variable baseline + risk pruning

**Problem:** S4 (F6=1, city owns nothing) ranked #1 on City Control.
S1 (F6=5, city owns everything) ranked #8.

**Root cause:** All scenarios shared baseline=100. Contractor factors (F2, F4)
leaked into G9 via R04 and R11, inflating scenarios with strong contractors.

**Fix:**
- Variable G9 baseline: `40 + 8×(F6-1) + 7×(F7-1)`
- Removed R04→G9 (driven by F4 integration, not city governance)
- Removed R11→G9 (driven by F2 contractor strength, not city governance)
- Scorer includes baseline penalty in weighted score

### Fix 3: Normalizer recalibration

At equal user weights, G2 had 15× the influence of G6. Recalibrated all
normalizers to `1/actual_spread` so each goal contributes equally at weight=1.

---

## NEW & EXPANDED RISKS (5)

### R30 (Expanded): City Value Capture Failure

**Was:** "Bad Initial Deal by City" — general poor negotiation.
**Now:** Also covers byggingarréttur resale markup. When city grants rights
at price X to intermediary (pension fund) who resells at X+Y to contractor,
city loses the Y margin.

| Change | Detail |
|--------|--------|
| Name | "Borgin missir af virðisaukningu lands" |
| Base prob | 10/25/45% → 15/30/50% |
| G4 added | 200/800/2000 M kr. (lost land value uplift) |
| F6 | MEDIUM → HIGH (F6=5 eliminates intermediary) |

### R34 (New): Tax Complications from City Ownership

When Reykjavík co-owns a commercial entity, it's no longer tax-exempt —
corporate income tax, VAT complications, transfer pricing, EEA state aid rules.

| Property | Value |
|----------|-------|
| Base prob | 40/65/85% |
| Goals | G2 (+2/6/14 mán.), G4 (+200/600/1500 M kr.), G9 (-5/-10/-20) |
| Protective | F5 HIGH, F7 MEDIUM |
| Gate | F6 = 3–4 only (S10, S11) |

### R35 (New): Procurement Rules Constrain and Delay

EEA public procurement: mandatory tenders, minimum timelines, standstill
periods, appeal rights. Structural cost of city involvement.

| Property | Value |
|----------|-------|
| Base prob | 35/55/80% |
| Goals | G1 (+2/6/12 mán.), G2 (+3/8/18 mán.), G5 (-3/-8/-15 pp) |
| Exposure | F6 HIGH |
| Protective | F5 MEDIUM |
| Gate | F6 ≥ 3 (S1, S10, S11) |

### R36 (New): Partnership Exit / Dissolution Difficulty

Unwinding multi-party ownership is expensive and slow. Applies to all
scenarios but severity scales with F1 (number of parties).

| Property | Value |
|----------|-------|
| Base prob | 8/20/40% |
| Goals | G2 (+3/8/18 mán.), G4 (+100/400/1200 M kr.), G5 (-5/-12/-25 pp), G9 (-5/-15/-30) |
| Exposure | F1 HIGH |
| Protective | F7 HIGH, F5 MEDIUM |
| Gate | None (all scenarios) |

### R37 (New): City Dual Role Conflict of Interest

City is both regulator (zoning, permits) and developer/owner. Competitors
and neighbors challenge decisions because city has financial interest.
Distinct from R02 (general zoning appeal).

| Property | Value |
|----------|-------|
| Base prob | 20/40/65% |
| Goals | G1 (+2/5/12 mán.), G2 (+2/5/12 mán.), G5 (-3/-8/-18 pp), G9 (-5/-15/-30) |
| Exposure | F6 HIGH |
| Protective | F7 MEDIUM, F5 LOW |
| Gate | F6 ≥ 3 (S1, S10, S11) |

---

## SCENARIO TARGETING

| Risk | S1 | S2–S5,S12 | S6–S9 | S10 | S11 |
|------|-----|-----------|-------|-----|-----|
| R30 (value capture) | Protected (F6=5) | Exposed (F6=1) | Exposed (F6=1) | Protected (F6=4) | Partially protected (F6=3) |
| R34 (tax) | — | — | — | ✓ | ✓ |
| R35 (procurement) | ✓ | — | — | ✓ | ✓ |
| R36 (exit) | All scenarios (scales with F1) |||||
| R37 (conflict) | ✓ | — | — | ✓ | ✓ |

---

## IMPACT ON RESULTS

### Rankings by weight profile

| Profile  | #1  | #2  | #3  | #4  | #5  |
|----------|-----|-----|-----|-----|-----|
| Balanced | S11 | S4  | S3  | S5  | S12 |
| Speed    | S4  | S3  | S5  | S12 | S11 |
| Fiscal   | S11 | S3  | S4  | S5  | S12 |
| Social   | S11 | S4  | S3  | S5  | S12 |
| Control  | S11 | S4  | S3  | S5  | S12 |
| City CRO | S11 | S4  | S3  | S5  | S12 |

Key change: S4 now beats S11 on Speed profile. The new city-involvement
penalties make the tradeoff real — city participation costs speed.

### Monte Carlo (10k iterations, Dirichlet sum-to-1)

**Uniform priorities (α=1.0):**

| Scenario | v4 Win% | v5 Win% | Δ |
|----------|---------|---------|---|
| S11      | 36.2%   | 61.4%   | +25 |
| S4       | 63.1%   | 28.9%   | -34 |
| S3       | 0.7%    | 9.0%    | +8 |
| S1       | 0.0%    | 0.7%    | +1 |

**Strong preferences (α=0.3):**

| Scenario | v4 Win% | v5 Win% | Δ |
|----------|---------|---------|---|
| S11      | 39.6%   | 48.1%   | +8 |
| S4       | 55.2%   | 33.9%   | -21 |
| S3       | 4.4%    | 12.0%   | +8 |
| S1       | 0.0%    | 5.5%    | +6 |

### G9 (City Control) — fixed rankings

| Rank | Scenario | Score | F6 | F7 |
|------|----------|-------|-----|-----|
| #1   | S1       | 59    | 5   | 5   |
| #2   | S10      | 38    | 4   | 4   |
| #3   | S11      | 34    | 3   | 4   |
| #4   | S3       | 29    | 1   | 3   |
| #12  | S9       | -28   | 1   | 1   |

### S11 penalty from new risks

| Risk | G2 | G4 | G5 | G9 | G1 |
|------|-----|-----|-----|-----|-----|
| R34 Tax | +3.2 | +328 | — | -5.2 | — |
| R35 Procurement | — | — | -4.1 | — | +3.1 |
| R36 Exit | +1.5 | +83 | -2.2 | -2.7 | — |
| R37 Conflict | +1.8 | — | -2.8 | -5.0 | +1.8 |
| **Total** | **+6.5 mán.** | **+411 M kr.** | **-9.1 pp** | **-12.9 pts** | **+4.9 mán.** |

S11 takes ~411 M kr. penalty on G4 and ~13 points on G9 from city-involvement
risks. This makes its lead conditional on affordability and social goals
outweighing the structural costs of city partnership.

---

## MODEL SUMMARY (v5)

- **33 risks** (was 29)
- **~100 goal impacts** (was 84)
- **12 scenarios**, **7 factors**, **10 goals**
- S11 wins under balanced/social/fiscal/control priorities
- S4 wins under speed priorities
- S3 is competitive under fiscal priorities
- No scenario wins under all weight profiles — genuine tradeoffs exist