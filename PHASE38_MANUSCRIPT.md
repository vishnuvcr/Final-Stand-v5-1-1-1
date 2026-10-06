# Phase 38 Manuscript — Corrected Model Robustness vs Stateful Control

## Abstract

Phase 38 tested whether the five Phase-37 polarity-corrected model direction selectors genuinely improve the Continuous Delta 6x6 strategy relative to the canonical Phase-32 stateful direction rule. The five treatments were CATBOOST, MARKOV_REGIME_TREE, WAVELET_TREE, OOF_STACK and DART. The strategy, costs, slippage, delta targeting, entry/exit rules and lot schedule were frozen.

A reproducibility audit found that a fresh Phase-32 reconstruction did not exactly reproduce the previously accepted control artifact: 205 trades and +₹65,945.47 were reconstructed versus the frozen canonical 206 trades and +₹63,672.58. This discrepancy was logged as F38-001. To prevent benchmark drift, the accepted Phase-32 result was frozen by SHA-256 fingerprint and expiry-level P&L cache; the reconstruction is retained as an audit check only.

Using the frozen canonical control, all five corrected selectors remained profitable after costs and remained positive in the 2026 holdout, but none outperformed the control on the paired common-expiry comparison. Across 93 common expiry blocks, mean selector-minus-control differences were negative for every model, with 95% bootstrap intervals crossing zero and probabilities of beating control between 18.1% and 37.6%. Direction asymmetry was also severe: every selector generated positive CALL-side P&L but negative PUT-side P&L. Consequently, no model selector is promoted to the live/paper strategy on the basis of Phase 38.

## Research question

Do the Phase-37 polarity-corrected predictive direction selectors improve post-cost performance relative to the accepted canonical Phase-32 stateful direction rule when evaluated on identical available expiry blocks without any tuning?

## Aims and objectives

1. Establish a frozen, reproducible control comparator.
2. Compare each corrected selector against that control on common expiry blocks.
3. Quantify uncertainty using a deterministic 10,000-resample paired expiry bootstrap.
4. Evaluate 2024, 2025 and 2026 temporal behavior.
5. Test resilience to +25%, +50% and +100% transaction-cost inflation.
6. Examine CALL/PUT asymmetry and drawdown/profit-factor characteristics.
7. Apply the preregistered promotion gate without post hoc tuning.

## Methodology

### Control

The canonical control is the accepted Phase-32 state machine:

- initial direction = CALL;
- winning trade -> retain direction;
- losing trade -> flip direction;
- zero-P&L trade -> retain direction.

The frozen comparator contains 206 trades over 102 expiry blocks, net P&L ₹63,672.58, gross ₹84,054.00 and costs ₹20,381.42. The source artifact SHA-256 is f98fc6e38e84bdfab09aeeffc2df333da1a3060d3756b1ab12b7e8cb5f32435f.

### Treatments

- CATBOOST
- MARKOV_REGIME_TREE
- WAVELET_TREE
- OOF_STACK
- DART

The Phase-37 corrected mapping is retained without retraining, threshold tuning or feature changes. The execution engine remains the same Continuous Delta 6x6 50-point vertical structure with six lots per leg, one-tick adverse slippage, brokerage and statutory/exchange costs, and the frozen delta-based entry/exit logic.

### Statistical analysis

For each selector, net P&L was aggregated by expiry and paired against the frozen control on common expiry blocks. The primary uncertainty analysis used 10,000 deterministic bootstrap resamples with NumPy default_rng(38001). Reported statistics are the mean and median paired difference, percentile bootstrap interval, bootstrap probability that selector exceeds control, expiry-block win rate, and total P&L difference on common blocks.

Secondary analyses included annual net P&L, trade count, win rate, profit factor, maximum drawdown, transaction-cost stress and CALL/PUT direction asymmetry.

## Results

### Primary paired common-expiry comparison

| Selector | Common expiries | Mean Δ vs control | 95% bootstrap CI | P(selector > control) | Expiry blocks won | Total Δ on common expiries |
|---|---:|---:|---:|---:|---:|---:|
| CATBOOST | 93 | -₹200.98 | -₹1,485 to +₹1,050 | 37.63% | 40.86% | -₹18,691.52 |
| MARKOV_REGIME_TREE | 93 | -₹252.75 | -₹1,559 to +₹995 | 34.37% | 37.63% | -₹23,506.01 |
| WAVELET_TREE | 93 | -₹486.79 | -₹1,792 to +₹772 | 23.19% | 39.78% | -₹45,271.43 |
| OOF_STACK | 93 | -₹557.00 | -₹1,876 to +₹731 | 20.18% | 33.33% | -₹51,800.60 |
| DART | 93 | -₹614.99 | -₹1,918 to +₹699 | 18.11% | 35.48% | -₹57,194.20 |

The frozen control earned ₹76,566.32 over the 93 expiry blocks common to the selector universe, while each selector earned less.

### Full-sample performance

| Strategy | Trades | Net P&L | Win rate | Profit factor | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Stateful control | 206 | ₹63,672.58 | 65.53% | 1.203 | ₹61,960.87 |
| CATBOOST | 203 | ₹57,874.80 | 64.04% | 1.186 | ₹49,337.02 |
| MARKOV_REGIME_TREE | 197 | ₹53,060.31 | 63.96% | 1.174 | ₹40,547.67 |
| WAVELET_TREE | 195 | ₹31,294.89 | 63.59% | 1.100 | ₹54,085.53 |
| OOF_STACK | 198 | ₹24,765.71 | 63.64% | 1.081 | ₹62,024.82 |
| DART | 198 | ₹19,372.11 | 62.12% | 1.060 | ₹52,629.57 |

CatBoost is the closest model on full-sample net P&L, while Markov-regime tree has the lowest maximum drawdown among the model treatments. Neither establishes superiority versus the control.

### Temporal behavior

| Selector | 2024 | 2025 | 2026 holdout |
|---|---:|---:|---:|
| Stateful control | ₹31,010.64 | ₹32,937.58 | -₹275.65 |
| CATBOOST | ₹13,081.58 | -₹4,261.12 | ₹49,054.33 |
| MARKOV_REGIME_TREE | ₹22,476.47 | -₹11,385.52 | ₹41,969.35 |
| WAVELET_TREE | ₹17,661.99 | -₹37,143.78 | ₹50,776.68 |
| OOF_STACK | ₹16,768.94 | -₹40,348.81 | ₹48,345.59 |
| DART | ₹13,076.77 | -₹32,758.62 | ₹39,053.96 |

All model selectors were positive in the 2026 holdout, but every model underperformed the control in 2025. The sharp temporal reversal is a major robustness concern.

### Transaction-cost stress

At +50% recorded transaction costs, all five selectors remained positive:

- CATBOOST: ₹48,337.20
- MARKOV_REGIME_TREE: ₹43,519.21
- WAVELET_TREE: ₹21,789.58
- OOF_STACK: ₹15,084.32
- DART: ₹9,424.67

At +100% costs, DART became slightly negative (−₹522.77); the other four remained positive.

### Risk-adjusted comparison

A secondary **net-P&L / maximum-drawdown ratio** was calculated. This is a Calmar-style diagnostic, not a formal annualized Calmar ratio because the numerator is cumulative sample P&L rather than annualized return.

| Strategy | Net P&L | Max drawdown | Net/DD |
|---|---:|---:|---:|
| MARKOV_REGIME_TREE | ₹53,060.31 | ₹40,547.67 | **1.309** |
| CATBOOST | ₹57,874.80 | ₹49,337.02 | **1.173** |
| STATEFUL_CONTROL | ₹63,672.58 | ₹61,960.87 | **1.028** |
| WAVELET_TREE | ₹31,294.89 | ₹54,085.53 | **0.579** |
| OOF_STACK | ₹24,765.71 | ₹62,024.82 | **0.399** |
| DART | ₹19,372.11 | ₹52,629.57 | **0.368** |

Thus Markov-regime tree has the best cumulative-return-to-drawdown efficiency, followed by CatBoost. The stateful control still has the highest absolute net P&L and highest win rate. The risk-adjusted result does not reverse the Phase-38 promotion decision because the model selectors still underperform the frozen control on the preregistered paired expiry comparison.

### Direction asymmetry

| Selector | CALL trades / net | PUT trades / net |
|---|---:|---:|
| CATBOOST | 95 / +₹64,964.67 | 108 / -₹7,089.87 |
| MARKOV_REGIME_TREE | 95 / +₹72,182.19 | 102 / -₹19,121.88 |
| WAVELET_TREE | 86 / +₹52,715.78 | 109 / -₹21,420.89 |
| OOF_STACK | 38 / +₹43,059.97 | 160 / -₹18,294.25 |
| DART | 79 / +₹45,575.41 | 119 / -₹26,203.30 |

The asymmetry is economically important. The corrected model selectors are not producing balanced CALL/PUT value. OOF_STACK is especially problematic because 80.8% of its trades are PUT-side while its PUT-side P&L is negative.

## Control reproducibility audit

The Phase-38 workflow independently reconstructed the stateful engine but obtained 205 trades, 103 expiry blocks, net ₹65,945.47, gross ₹86,139.00 and costs ₹20,193.53. These values do not match the accepted frozen control. Therefore they were not used for the primary treatment comparison.

This discrepancy is explicitly recorded as F38-001 in ERROR_LOG.md. The frozen artifact and SHA-256 fingerprint prevent silent benchmark drift in future phases.

## Discussion

The main result is negative for the intended hypothesis. Corrected model direction selectors can produce positive standalone P&L, including strong 2026 results, yet still fail to improve the canonical stateful strategy. This demonstrates why absolute profitability is insufficient: the relevant decision is incremental post-cost performance against a frozen control.

The paired bootstrap reinforces the result. Every point estimate favors the control, every bootstrap probability of selector superiority is below 50%, and the selector-minus-control total is negative for all five treatments. The confidence intervals cross zero, so the evidence does not prove a statistically significant negative difference in a conventional inferential sense; however, it clearly does not support promotion because the observed effect is consistently in the wrong direction.

The temporal pattern is also concerning. The models lost money in 2025 while the control gained about ₹32.9k, then produced large gains in 2026 while the control was approximately flat. This may reflect regime dependence, opportunity-set differences, or model instability. The current sample is too small to decide among these explanations.

The CALL/PUT asymmetry is the strongest practical warning. Every model treatment earned all or most of its model P&L from CALL trades and lost on PUT trades. Because the strategy is a direction-specific option spread whose risk/decay/strike-selection behavior can differ between calls and puts, this asymmetry cannot be dismissed as a neutral classifier property. A future research phase would need to separate signal calibration from execution-leg asymmetry before any promotion.

## Strengths

- Frozen Phase-37 predictions; no retraining or tuning.
- Common-expiry paired comparison reduces exposure to unrelated expiry-level conditions.
- Full transaction-cost model retained.
- Deterministic 10,000-resample bootstrap.
- Explicit 2026 holdout reporting.
- Cost-stress and direction-asymmetry diagnostics.
- Control benchmark drift was detected rather than silently accepted.

## Limitations

1. The paired sample contains 93 common expiry blocks, not all 102 frozen-control expiries, because selector coverage/execution was not identical.
2. The 2026 holdout contains only 34 control trades and 37–42 model trades.
3. The model direction split is strongly asymmetric, particularly for OOF_STACK.
4. The present test remains based on historical close/quote execution assumptions; true bid/ask fill probability, latency and broker-routing effects are not fully modeled.
5. No formal superiority claim can be made from the bootstrap because all confidence intervals cross zero.
6. The control reconstruction mismatch indicates that exact research-era datasets/engine artifacts must remain frozen for future comparisons.

## Conclusion

**Phase 38 rejects all five corrected model selectors as replacements for the canonical stateful direction rule.**

CatBoost is the strongest rejected candidate on full-sample net P&L and Markov-regime tree has the lowest model maximum drawdown, but neither beats the stateful control on paired common-expiry performance. No model is promoted to live trading or paper trading as the primary direction selector.

The canonical stateful Phase-32 direction rule therefore remains the control strategy entering Phase 39.

## Future research direction

Phase 39 should focus on robustness of the canonical stateful strategy, not on automatically replacing its direction rule. The most valuable next experiments are:

- bid/ask and latency/fill-probability realism using broker-compatible execution assumptions;
- formal slippage and transaction-cost sensitivity beyond +50%;
- regime-conditional diagnostics explaining the 2025 model failure and 2026 model success;
- explicit CALL/PUT structural decomposition;
- forward/paper validation before any live deployment decision.

## Reproducibility appendix

Primary result files:

- results/phase38_corrected_model_robustness/paired_bootstrap.csv
- results/phase38_corrected_model_robustness/cost_stress.csv
- results/phase38_corrected_model_robustness/selector_summary.csv
- results/phase38_corrected_model_robustness/yearly_results.csv
- results/phase38_corrected_model_robustness/direction_asymmetry.csv
- results/phase38_corrected_model_robustness/control_validation.json
- results/phase38_corrected_model_robustness/frozen_control_expiry.csv
- results/phase38_corrected_model_robustness/frozen_control_metadata.json

Workflow runs:

- Phase 38 successful run with frozen-control correction: 37433424224
- Earlier mismatched-control run: 37432966945 — rejected as primary evidence.

Branch: phase-38-corrected-model-robustness

Pull request: #12
