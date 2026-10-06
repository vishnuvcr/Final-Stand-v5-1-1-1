# Phase 41 Manuscript — Regime-Conditional Counterfactual Policy Learning

## Abstract

Phase 41 tested a bounded regime-conditional economic-margin policy family after Phase 39 showed the promise of counterfactual learning and Phase 40 showed that India VIX was more useful as a routing variable than as a direct direction signal. Twenty-four pre-registered variants were evaluated with expanding-window chronology on a 477-opportunity fixed counterfactual panel. The canonical stateful strategy remained the default action. The top three validation policies were frozen before the 2026 holdout was evaluated, then replayed through the exact sequential trading engine with the repository one-tick adverse slippage, brokerage and statutory-cost model.

## Research questions

1. Does explicit India-VIX regime state improve control-relative economic-margin prediction?
2. Does the policy concentrate positive CALL-versus-PUT counterfactual value in its highest-scored states?
3. Does the apparent override value persist under matched-state diagnostics?
4. Does it survive exact sequential replay, the untouched 2026 holdout and cost stress?
5. Is India VIX more useful as a regime/router than as a direct directional predictor?

## Aims and objectives

The primary aim was to identify a small, pre-registered regime-conditional override policy that improves the canonical strategy without materially worsening risk. Secondary objectives were to quantify India-VIX routing value, test ranking concentration, examine treatment-overlap diagnostics and preserve strict chronology.

## Scientific methodology

### Data
Accepted fixed-opportunity panel: 477 opportunities; 271 development / 172 validation / 34 untouched holdout. Both hypothetical CALL and PUT spread outcomes were already available in the accepted Phase-39 ledger. The feature layer contains point-in-time NIFTY, option, global-market, FII/DII, sentiment and volatility variables. India VIX was aligned using the prior available session and development-only thresholds.

### Candidate family
Two learners were registered: a low-capacity spline-Ridge economic-margin model with explicit VIX interactions and a shallow ExtraTrees margin learner. Each was crossed with four override margins (0/250/500/1000 rupees) and three VIX routing gates (ALL/HIGH_VIX/HIGH_VIX_RISING), giving exactly 24 declared variants.

### Chronology and execution
Each prediction used only earlier observations, with a 100-opportunity warm-up. The economic target was DeltaP&L = CALL net P&L minus PUT net P&L. Overrides were scored as the model predicted improvement over the current canonical direction minus one uncertainty unit. Exact sequential replay allowed the selected direction to change the exit timestamp and therefore future entries. One adverse tick of slippage, four order executions per spread, historical lot sizes, brokerage and date-aware statutory charges were retained.

### Selection discipline
The top three candidates were selected using development/validation results only. The 2026 holdout was not used to tune model, margin or routing gate. Propensity matching used only pre-evaluation history for propensity fitting and was treated strictly as a selection-overlap diagnostic. Ranking diagnostics examined the observed counterfactual DeltaP&L concentration in the top 10%, 20% and 30% model-score groups.

## Pre-registered hypotheses

H1: explicit volatility-regime context improves economic-margin prediction and override quality.
H2: the best regime-conditional policy yields positive sequential validation and untouched-holdout incremental P&L with acceptable drawdown and execution-cost robustness.

## Results

### Fixed-opportunity screen
Twenty-four declared variants were completed. The validation ranking and complete grid are stored in results/phase41_regime_policy/fixed_grid_validation.csv. The top-three freeze is stored in results/phase41_regime_policy/selection.json.

![Validation grid](results/phase41_regime_policy/phase41_validation_grid.png)

### Frozen candidates

| Rank | Model | Margin | Gate | Validation uplift | Holdout uplift | Holdout overrides |
|---:|---|---:|---|---:|---:|---:|
| 1 | SPLINE_RIDGE_VIX | 0 | ALL | 0.00 | 0.00 | 0 |
| 2 | SPLINE_RIDGE_VIX | 0 | HIGH_VIX | 0.00 | 0.00 | 0 |
| 3 | SPLINE_RIDGE_VIX | 0 | HIGH_VIX_RISING | 0.00 | 0.00 | 0 |

![Top three sequential results](results/phase41_regime_policy/phase41_top3_sequential.png)

### Paired-expiry inference

Results below use 10,000 paired-expiry bootstrap resamples and paired sign-flip inference. The 95% interval is reported for the mean expiry-level incremental P&L; the holdout is the principal generalization test.

| Rank | Period | Mean uplift/expiry | 95% CI low | 95% CI high | One-sided p | Positive expiry share |
|---:|---|---:|---:|---:|---:|---:|
| 1 | validation | 0.00 | 0.00 | 0.00 | 1.0000 | 0.0% |
| 1 | holdout | 0.00 | 0.00 | 0.00 | 1.0000 | 0.0% |
| 2 | validation | 0.00 | 0.00 | 0.00 | 1.0000 | 0.0% |
| 2 | holdout | 0.00 | 0.00 | 0.00 | 1.0000 | 0.0% |
| 3 | validation | 0.00 | 0.00 | 0.00 | 1.0000 | 0.0% |
| 3 | holdout | 0.00 | 0.00 | 0.00 | 1.0000 | 0.0% |

### Cost stress

| Rank | Period | +25% cost uplift | +50% cost uplift | +100% cost uplift |
|---:|---|---:|---:|---:|
| 1 | validation | 0.00 | 0.00 | 0.00 |
| 1 | holdout | 0.00 | 0.00 | 0.00 |
| 2 | validation | 0.00 | 0.00 | 0.00 |
| 2 | holdout | 0.00 | 0.00 | 0.00 |
| 3 | validation | 0.00 | 0.00 | 0.00 |
| 3 | holdout | 0.00 | 0.00 | 0.00 |

### Selection-overlap diagnostics

Validation propensity diagnostic: {"att": null, "common_support_fraction": 0.0, "matched": 0, "split": "validation", "treated": 0}.
Holdout propensity diagnostic: {"att": null, "common_support_fraction": 0.0, "matched": 0, "split": "holdout", "treated": 0}.

These matched-state calculations do not establish causal efficacy. They diagnose whether override opportunities have usable common-support analogues.

### Ranking diagnostics

Validation ranking: {"rows": 172, "split": "validation", "top_10_ci_hi": 4688.788488404583, "top_10_ci_lo": 425.30792675122854, "top_10_mean_delta": 2502.6131905700017, "top_10_positive_share": 0.7777777777777778, "top_20_ci_hi": 3543.5375761784694, "top_20_ci_lo": -22.579576907977998, "top_20_mean_delta": 1783.829266855287, "top_20_positive_share": 0.7428571428571429, "top_30_ci_hi": 2620.233326380724, "top_30_ci_lo": -428.7274576819757, "top_30_mean_delta": 1092.9268786234618, "top_30_positive_share": 0.6346153846153846}.
Holdout ranking: {"rows": 34, "split": "holdout", "top_10_ci_hi": 9856.560701812514, "top_10_ci_lo": 2593.3477083052526, "top_10_mean_delta": 7338.852990534007, "top_10_positive_share": 1.0, "top_20_ci_hi": 8607.903719693579, "top_20_ci_lo": -6338.588700232271, "top_20_mean_delta": 1823.4468022847245, "top_20_positive_share": 0.7142857142857143, "top_30_ci_hi": 9023.642860778946, "top_30_ci_lo": -3128.9134252124777, "top_30_mean_delta": 3359.9035994124583, "top_30_positive_share": 0.7272727272727273}.

## Statistical inference and decision

Promotion was evaluated against the pre-registered quantitative gates. A policy must simultaneously show positive sequential validation and holdout uplift, acceptable drawdown in both periods, non-negative paired-expiry confidence lower bounds, positive +50% cost-stress uplift, at least five holdout overrides, and no expiry-level concentration above 40% of total positive OOS uplift.

| Rank | Promotion gate result |
|---:|---|
| 1 | FAIL |
| 2 | FAIL |
| 3 | FAIL |

## Discussion

The primary scientific question is not whether a point estimate is positive but whether the result is stable under chronology, control-relative inference and the untouched holdout. The phase therefore treats the fixed-opportunity oracle and raw validation ranking as exploratory and uses sequential replay for the trading claim.

India VIX remains scientifically interesting as a state variable. This phase was intentionally narrow: it did not add another unrestricted classifier family. The result is interpreted together with Phase 40, where high-VIX routing was the strongest validation cluster but remained statistically inconclusive on holdout.

## Strengths

- Explicit counterfactual action target rather than indirect market-direction classification.
- Frozen 24-variant universe and holdout discipline.
- Strict expanding-window chronology and deterministic point-in-time VIX alignment.
- Exact sequential replay with the established one-tick adverse slippage, brokerage, statutory charges and lot-size schedule.
- Matched-state and ranking diagnostics in addition to P&L.

## Limitations

- Only 20 holdout expiry blocks are present in the accepted counterfactual panel.
- The policy is learned from a small number of independent expiry-level states.
- Propensity matching is not causal identification because treatment is policy-generated and both counterfactual arms are available in the historical panel.
- Historical one-minute data do not fully reproduce live bid/ask fill probability, latency or queue position.
- The base historical execution model uses one adverse slippage tick; larger slippage was not re-optimized because the research goal was fixed-policy robustness rather than threshold retuning.

## Conclusion

The Phase-41 registered research phase is closed. The canonical stateful strategy remains unchanged unless an accepted candidate satisfies the complete promotion screen. India VIX is retained as a regime/routing research variable rather than a promoted direct direction predictor.

## Future direction

The next scientifically valuable step is prospective and paper validation using broker-quality bid/ask and fill data, together with a longer untouched sample. Another unrestricted classifier sweep is not justified by the present evidence.

## Reproducibility artifacts

- PHASE41_RESEARCH_PLAN.md
- PHASE41_PRE_REGISTRATION.md
- PHASE41_LITERATURE_REVIEW.md
- results/phase41_regime_policy/fixed_grid_validation.csv
- results/phase41_regime_policy/selection.json
- results/phase41_regime_policy/frozen_top3_fixed_results.csv
- results/phase41_regime_policy/sequential_summary.csv
- results/phase41_regime_policy/sequential_candidate_*.csv
- results/phase41_regime_policy/diagnostics_validation.json
- results/phase41_regime_policy/diagnostics_holdout.json
- results/phase41_regime_policy/phase41_validation_grid.png
- results/phase41_regime_policy/phase41_top3_sequential.png
- ERROR_LOG.md and RESEARCH_LOG.md
