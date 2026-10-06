# Phase 33 — NIFTY D−6 Prediction Models

## Abstract
This phase tests whether information observable at exactly 10:00 IST on six calendar days before NIFTY expiry predicts the subsequent expiry-day NIFTY close. The registered model set includes LSTM, GARCH/EGARCH/GJR-GARCH volatility forecasting, a sentiment-augmented SOFNN-inspired fuzzy classifier, Random Forest, and a fixed equal-weight ensemble. The design uses point-in-time feature censoring, chronological validation and an untouched 2026 holdout.

Across 245 eligible expiry events, the strongest full directional model differs by period: Random Forest is strongest on validation log loss, while the equal-weight ensemble has the strongest holdout accuracy among the full models. Neither result is robust enough to justify a trading overlay because the apparent 2026 directional edge does not beat the simple always-down baseline on accuracy and the signed-return confidence intervals include zero.

## Research question
Can D−6/10:00 IST information predict expiry-day NIFTY direction or magnitude out of sample, and does any requested model family produce a stable enough edge to justify a future strategy overlay?

## Aims and objectives
1. Quantify point-in-time directional predictability.
2. Compare LSTM, GARCH-family volatility models, SOFNN-inspired fuzzy learning, Random Forest and an equal-weight ensemble.
3. Measure incremental information from sentiment, cross-market, options and FII/DII variables.
4. Evaluate volatility forecasting separately from directional classification.
5. Apply a pre-registered promotion gate.

## Methods
Reference timestamp: expiry minus six calendar days at exactly 10:00 IST.
Target: latest complete NIFTY spot observation at or before 15:29 IST on expiry day.
Events without an exact 10:00 observation are excluded rather than shifted.

Development/training contains 128 events, validation contains 95 events, and the untouched 2026 holdout contains 22 events. The LSTM uses the 30 most recent completed trading sessions strictly before the reference date. Random Forest and SOFNN-inspired parameters are fixed. GARCH, EGARCH and GJR-GARCH are fit only to returns available before the reference timestamp. Multi-step EGARCH uses simulation forecasting because analytic multi-step forecasts are unsupported for that model family in the selected econometrics implementation.

## Data and leakage control
The point-in-time feature set contains 67 numeric features from NIFTY price/volatility history, prior-session global markets, exact-reference option-chain diagnostics where available, sentiment and cached FII/DII data. Forward-return and target columns from the sentiment dataset are excluded. Global values are shifted to prior sessions, institutional flow joins use the previous available publication, and all time keys are normalized to IST with a common nanosecond resolution.

## Out-of-sample results

### Directional metrics
| Split | Model | Accuracy | Balanced accuracy | ROC-AUC | Log loss | Brier | ECE |
|---|---|---:|---:|---:|---:|---:|---:|
| holdout | rf | 0.5455 | 0.4554 | 0.5804 | 0.6562 | 0.2326 | 0.1094 |
| holdout | ensemble | 0.5909 | 0.6518 | 0.6607 | 0.6857 | 0.2463 | 0.1508 |
| holdout | lstm | 0.3636 | 0.5000 | 0.5000 | 0.6931 | 0.2500 | 0.1364 |
| holdout | sofnn | 0.3636 | 0.5000 | 0.6696 | 0.7343 | 0.2700 | 0.2151 |
| holdout | sofnn_sent | 0.3636 | 0.5000 | 0.7500 | 0.7515 | 0.2785 | 0.2461 |
| validation | rf | 0.5474 | 0.5439 | 0.5812 | 0.6851 | 0.2461 | 0.0755 |
| validation | ensemble | 0.4947 | 0.4843 | 0.5776 | 0.6879 | 0.2474 | 0.0395 |
| validation | lstm | 0.5158 | 0.5000 | 0.5000 | 0.6931 | 0.2500 | 0.0158 |
| validation | sofnn | 0.5158 | 0.5000 | 0.5169 | 0.6988 | 0.2528 | 0.0508 |
| validation | sofnn_sent | 0.5158 | 0.5000 | 0.5169 | 0.6988 | 0.2528 | 0.0508 |

### Costless directional-return diagnostic
This is a prediction diagnostic, not an executed option P&L. It signs the expiry-horizon log return according to the model's predicted direction.

| Split | Model | Hit rate | Mean signed log return | 95% bootstrap CI |
|---|---|---:|---:|---|
| validation | rf | 0.5474 | 0.00183 | [-0.00144, 0.00498] |
| validation | sofnn | 0.5158 | 0.00066 | [-0.00256, 0.00371] |
| validation | sofnn_sent | 0.5158 | 0.00066 | [-0.00256, 0.00371] |
| validation | lstm | 0.5158 | 0.00066 | [-0.00256, 0.00371] |
| validation | ensemble | 0.4947 | 0.00050 | [-0.00269, 0.00355] |
| holdout | rf | 0.5455 | 0.00348 | [-0.00423, 0.01122] |
| holdout | sofnn | 0.3636 | -0.00425 | [-0.01169, 0.00363] |
| holdout | sofnn_sent | 0.3636 | -0.00425 | [-0.01169, 0.00363] |
| holdout | lstm | 0.3636 | -0.00425 | [-0.01169, 0.00363] |
| holdout | ensemble | 0.5909 | 0.00414 | [-0.00385, 0.01186] |

### Main findings
- Validation best full-model log loss: rf at 0.6851; accuracy 0.5474.
- Holdout best full-model log loss: rf at 0.6562; accuracy 0.5455.
- Holdout best full-model accuracy: ensemble at 0.5909; the simple always-down baseline reaches 0.6364 accuracy on the same 22-event holdout.
- Holdout ensemble balanced accuracy is 0.6518; this is the clearest sign of some discrimination, but the sample is small and validation ensemble accuracy was only 0.4947.
- Sentiment augmentation does not improve the SOFNN track: its validation result is identical to SOFNN and its holdout accuracy is 0.3636 with Brier score 0.2785.
- LSTM is effectively non-informative in this specification: ROC-AUC 0.50 and 0.5 probability output in both evaluation periods.
- GARCH-family volatility forecasts have MAE 0.01020, RMSE 0.01231, QLIKE 66548.975, and correlation 0.066 with realized absolute return. Directional accuracy is 0.4957.

## Statistical interpretation
Bootstrap intervals for all model mean signed returns include zero in both validation and holdout. Paired accuracy permutation and McNemar-style discordance tests do not show a robust advantage over the simple constant-direction comparator in this sample. The small 2026 holdout substantially limits power.

## Discussion
The literature supports testing these architectures but does not imply that one architecture should dominate for this specific NIFTY expiry horizon. The present experiment illustrates why model family selection from published studies cannot replace market-specific, point-in-time validation. Random Forest shows a modest validation edge, and the ensemble shows a modest 2026 holdout discrimination signal, but neither is stable enough to justify trading.

## Strengths
- Exact D−6/10:00 anchor.
- Chronological development/validation/holdout design.
- Explicit look-ahead controls.
- Multiple model families and strong simple baselines.
- Separate volatility and direction evaluation.
- Cached data and automated GitHub workflows.
- FII/DII, global markets, options and sentiment included where reliable historical coverage exists.

## Limitations
- Holdout size is only 22 expiry events.
- Public option-chain coverage is incomplete.
- FII/DII cache coverage is sparse relative to the full event set.
- The sentiment source starts in 2024, so its dedicated track cannot be trained on the pre-2024 period.
- SOFNN is an SOFNN-inspired reproducible implementation rather than a guaranteed byte-for-byte reproduction of every original paper-specific component.
- Costless signed-return diagnostics do not include brokerage, statutory charges or slippage and must not be interpreted as executable option strategy returns.

## Conclusion
**Phase 33 does not promote a NIFTY direction-prediction model to trading use.** The requested architectures provide some statistically interesting signals, especially Random Forest on validation and the ensemble on the 2026 holdout, but none clears the pre-registered stability and economic promotion gate. Phase 20 remains the canonical strategy. Any model-directed option overlay must be a separately registered phase with the established Paytm Money transaction-cost, slippage and execution model.

## Future research
A separate Phase 34 can freeze the ensemble/RF candidate and test it only as a direction chooser for the Continuous Delta 6x6 strategy, including brokerage, statutory charges, slippage, entry fills, expiry gaps and regime segmentation. Alternative reference timings such as D−4, D−5 and D−7 can be tested only as new preregistered phases.

## Reproducibility artifacts
- PHASE33_STATISTICAL_SUMMARY.csv
- PHASE33_YEARLY_STABILITY.csv
- PHASE33_DECISION_TABLE.csv
- PHASE33_GARCH_SUMMARY.json
- PHASE33_POSTPROCESS_SUMMARY.json
- model_predictions.csv
- garch_predictions.csv
- cached data under data/phase33
- figures under results/phase33_nifty_prediction/figures
