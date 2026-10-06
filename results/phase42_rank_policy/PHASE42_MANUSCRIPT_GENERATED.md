# Phase 42 Manuscript — Rank-to-Action Selective Policy

## Abstract

Phase 42 tested whether the ranking signal identified in Phase 41 could be converted into a selective trading policy without introducing another unrestricted predictive model family. Six pre-registered policies reused the leading Phase-41 spline-Ridge economic-margin model and selected only opportunities in the historical top 5%, 10% or 20% of model score, with either no VIX gate or a high-VIX gate. Exact chronology, the untouched 2026 holdout and the established one-tick slippage/cost model were retained.

## Research questions

1. Does raw directional economic-benefit score contain usable selective-ranking information?
2. Can controlled score coverage produce a positive, robust trading uplift?
3. Does high India VIX improve selective routing?
4. Does the result survive exact sequential replay and cost stress?

## Methods

Fixed sample: 477 opportunities (271 development, 172 validation, 34 holdout). One leading model was used. The score was the predicted control-relative economic benefit. For each timestamp, the score threshold was an empirical quantile of earlier scores only. Six candidates crossed three coverage targets (5%, 10%, 20%) with two routing gates (ALL, HIGH_VIX).

## Results

![Validation grid](results/phase42_rank_policy/phase42_validation_grid.png)

| Rank | Cutoff | Gate | Validation uplift | Holdout uplift | Holdout overrides |
|---:|---|---|---:|---:|---:|
| 1 | TOP_5 | ALL | 44447.40 | -0.00 | 0 |
| 2 | TOP_5 | HIGH_VIX | 26744.94 | -0.00 | 0 |
| 3 | TOP_10 | HIGH_VIX | 35728.96 | -0.00 | 0 |

![Sequential top three](results/phase42_rank_policy/phase42_top3_sequential.png)

### Paired-expiry inference

| Rank | Period | Mean uplift/expiry | 95% CI low | 95% CI high | p |
|---:|---|---:|---:|---:|---:|
| 1 | validation | 511.67 | -121.08 | 1327.42 | 0.1281 |
| 1 | holdout | -0.00 | -0.00 | 0.00 | 0.8768 |
| 2 | validation | 295.78 | -0.00 | 881.38 | 0.2360 |
| 2 | holdout | -0.00 | -0.00 | 0.00 | 0.8726 |
| 3 | validation | 405.34 | -0.00 | 1100.65 | 0.1133 |
| 3 | holdout | -0.00 | -0.00 | 0.00 | 0.8730 |

### Cost stress

| Rank | Period | +25% | +50% | +100% |
|---:|---|---:|---:|---:|
| 1 | validation | 44517.38 | 44587.35 | 44727.30 |
| 1 | holdout | -0.00 | -0.00 | -0.00 |
| 2 | validation | 26804.93 | 26864.91 | 26984.88 |
| 2 | holdout | -0.00 | -0.00 | -0.00 |
| 3 | validation | 35704.32 | 35679.68 | 35630.41 |
| 3 | holdout | -0.00 | -0.00 | -0.00 |

### Ranking diagnostics

Validation: {"split": "validation", "rows": 172, "top_5_mean_delta": -11.506440116666504, "top_5_positive_share": 0.5555555555555556, "top_10_mean_delta": -114.96176381416551, "top_10_positive_share": 0.5555555555555556, "top_20_mean_delta": 684.2680276422867, "top_20_positive_share": 0.6285714285714286}.
Holdout: {"split": "holdout", "rows": 34, "top_5_mean_delta": 9693.449275321509, "top_5_positive_share": 1.0, "top_10_mean_delta": 2610.6024235687646, "top_10_positive_share": 0.75, "top_20_mean_delta": 3792.5036252721525, "top_20_positive_share": 0.7142857142857143}.

### Propensity diagnostics

Validation: {"split": "validation", "treated": 3, "matched": 0, "att": null}.
Holdout: {"split": "holdout", "treated": 1, "matched": 1, "att": 243.88226358601423, "ci_lo": 243.88226358601423, "ci_hi": 243.88226358601423, "common_support_fraction": 1.0}.

## Decision

| Rank | Promotion result |
|---:|---|
| 1 | FAIL |
| 2 | FAIL |
| 3 | FAIL |

## Discussion

Phase 42 directly tested the bottleneck exposed by Phase 41: the model had useful ranking signal but its uncertainty-penalized action rule produced no overrides. Selective coverage separates ranking quality from action density. A positive ranking curve without positive sequential policy value is not a tradable edge.

## Strengths

- No new classifier family; the leading Phase-41 model was retained.
- Explicit historical-score coverage controls and strict point-in-time percentile construction.
- Exact sequential replay, one-tick adverse slippage, brokerage and statutory charges.
- Untouched 2026 holdout and paired-expiry inference.

## Limitations

- The holdout contains only 20 expiry blocks.
- Rank thresholds control action coverage but are not causal treatment-effect estimators.
- Historical execution assumptions remain imperfect relative to live bid/ask and fill queue.

## Conclusion

The Phase-42 candidate family is closed under its preregistered scope. The canonical stateful strategy remains unchanged unless a candidate satisfies every promotion gate.

## Future direction

Prospective broker-quality paper validation remains preferable to expanding model search. If selective ranking shows repeated out-of-sample value without promotion, the next phase should isolate economic regime or spread-geometry interactions rather than add model complexity.

## Reproducibility artifacts

- PHASE42_RESEARCH_PLAN.md
- PHASE42_PRE_REGISTRATION.md
- PHASE42_LITERATURE_REVIEW.md
- results/phase42_rank_policy/fixed_grid_validation.csv
- results/phase42_rank_policy/selection.json
- results/phase42_rank_policy/frozen_top3_fixed_results.csv
- results/phase42_rank_policy/sequential_summary.csv
- results/phase42_rank_policy/diagnostics_validation.json
- results/phase42_rank_policy/diagnostics_holdout.json
- ERROR_LOG.md
- RESEARCH_LOG.md
