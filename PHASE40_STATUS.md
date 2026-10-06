# Phase 40 Status — Ensemble Direction Selection with VIX

**ACTIVE — exhaustive grid and fixed-opportunity inference complete; exact stateful replay in progress**

Branch: `phase-40-ensemble-direction-models`

## Hypothesis
The five rejected individual selectors may contain complementary information. A dynamic ensemble and VIX-conditioned routing may extract that information without replacing the canonical stateful strategy outright.

## Registered universe
- 6 experts including India VIX.
- 63 non-empty expert subsets.
- 4 aggregators.
- 7 VIX modes.
- 1,764 declared candidates.
- 306 unique validation direction policies after alias deduplication.
- Top 10 unique policies frozen before holdout.

## Completed evidence

### Step 1 — Expert/VIX data audit — COMPLETE
India VIX cached in `data/phase40_vix/india_vix.csv` with 1,589 rows used by the current run. Development-derived thresholds:
- absolute VIX daily-return q67 = 0.03988018
- VIX level q33 = 14.7474
- VIX level q67 = 20.4300

### Step 2 — Full 1,764-candidate grid — COMPLETE
All 1,764 combinations passed CI. The VIX-high routing mode is the dominant validation regime:
- 252 HIGH-mode candidates
- all 252 have positive validation uplift
- best validation uplift = **₹21,262.83**

### Step 3 — Validation selection — COMPLETE
Top 10 are selected from **unique expiry-level signal sequences**, not merely different parameter labels.

Top validation candidate:
- Candidate 3
- CATBOOST
- HIGH-VIX gate with canonical fallback
- validation net = **₹98,104.79**
- common-control uplift = **₹21,262.83**
- validation win rate = **70.13%**
- validation profit factor = **1.549**
- validation max drawdown by trade stream = **₹26,764.09**

### Step 4 — Fixed-opportunity holdout/inference — COMPLETE
10,000 paired expiry resamples were run on the frozen top 10. Candidate 3's fixed-opportunity holdout:
- candidate net = **₹12,797.11**
- frozen-control net = **-₹275.65**
- uplift = **₹13,072.75**
- 20 holdout expiries
- mean uplift ≈ **₹653.64/expiry**
- 95% bootstrap CI for mean uplift ≈ **-₹183.23 to ₹2,144.15**
- one-sided sign-flip p ≈ **0.407**

This is **promising but not statistically established**. The holdout result does not justify promotion by itself.

### Step 5 — Fixed-opportunity cost stress — COMPLETE
For candidate 3, fixed-opportunity validation/holdout cost stress remains positive through +100% costs in the inference artifact. Exact sequential replay is still required before drawing a strategy conclusion.

## Current Step

### Step 6 — Exact stateful top-10 replay — IN PROGRESS
The exact Phase-32 chronological state machine is now being applied to each frozen top-10 policy. The policy supplies the initial direction for each expiry; after entry, the canonical engine controls subsequent direction changes, exits, costs, brokerage and one-tick adverse slippage.

The workflow will compare each candidate against the frozen Phase-38 control at expiry level on validation and untouched 2026 holdout.

## Remaining registered steps
- Step 6: exact stateful replay — IN PROGRESS
- Step 7: VIX routing/series robustness — PENDING
- Step 8: final statistical inference and promotion gate — PENDING
- Step 9: manuscript, figures, appendices, limitations and closeout — PENDING

## Current scientific interpretation
Phase 40 has **not** yet produced a promoted trading strategy. The important new finding is that **high India VIX materially changes the model-selection landscape**: the best validation policies are concentrated in the HIGH-VIX gate family, while OFF/LOW modes are generally negative relative to the control.

The key risk is selection instability: validation improvement is large, but the untouched holdout contains only 20 expiry blocks and its paired confidence interval crosses zero. Exact stateful replay is therefore mandatory before any acceptance decision.
