# Phase 35 Status — Advanced Tree, Probabilistic and Adaptive NIFTY Prediction

## Current state
**COMPLETE — NO LIVE-TRADING PROMOTION**

### Evidence set
- 245 eligible events: 128 development, 95 validation, 22 untouched 2026 holdout.
- Accepted principal numerical run: GitHub Actions 37425240176.
- Accepted Markov-switching addendum: GitHub Actions 37426499636.
- Accepted CEEMDAN addendum: GitHub Actions 37426761476.
- Failed/superseded runs are excluded from evidence and logged in ERROR_LOG.md.
- Phase 20 remains the canonical trading strategy.

### Model families tested
- Core tree/boosting: XGBoost, LightGBM, CatBoost, ExtraTrees, HistGradientBoosting, LightGBM-DART.
- Tree combinations: equal six-tree pool, winsorized pool, RFE-LightGBM, dynamic pool, regime-gated tree, chronological OOF stack.
- Probabilistic/distributional: NGBoost, quantile boosting, BART.
- Decomposition + trees: wavelet, EMD, VMD, CEEMDAN.
- Adaptive: fixed 52-event rolling tree, exponentially weighted recent-history tree.
- Calibration/uncertainty: Platt, isotonic, conformal prediction/abstention.
- Regime: reproducible two-state Markov-switching volatility proxy + LightGBM.

### Key results
| Model | Validation accuracy | 2026 holdout accuracy | Holdout signed-return mean |
|---|---:|---:|---:|
| XGBoost | 57.89% | 63.64% | +0.00463 |
| LightGBM | 54.74% | 63.64% | +0.00844 |
| CatBoost | 57.89% | 68.18% | +0.00656 |
| ExtraTrees | 50.53% | 68.18% | +0.00663 |
| HistGradientBoosting | 54.74% | 63.64% | +0.00832 |
| DART | 47.37% | 68.18% | +0.00856 |
| Equal 6-tree | 54.74% | 59.09% | +0.00863 |
| RFE-LightGBM | 49.47% | 50.00% | +0.00495 |
| NGBoost | 54.74% | 54.55% | +0.00043 |
| Quantile tree | 50.53% | 50.00% | +0.00267 |
| BART | 55.79% | 54.55% | +0.00236 |
| Wavelet + tree | 50.53% | 68.18% | +0.00880 |
| EMD + tree | 49.47% | 45.45% | +0.00127 |
| VMD + tree | 55.79% | 54.55% | +0.00705 |
| Adaptive 52 | 51.58% | 36.36% | +0.00072 |
| Adaptive EW | 52.63% | 59.09% | +0.00448 |
| Dynamic pool | 54.74% | 63.64% | +0.00614 |
| OOF stack | 51.58% | 68.18% | +0.00951 |
| Platt | 47.37% | 50.00% | +0.00257 |
| Isotonic | 50.53% | 54.55% | +0.00443 |
| Conformal | 51.58% | 36.36% | −0.00425 |
| Markov regime + tree | 53.68% | 68.18% | +0.00868 |
| CEEMDAN + tree | 48.42% | 50.00% | +0.00281 |

### Promotion decision
**No Phase-35 model passes the complete promotion gate.** The strongest Phase-34 validation benchmark is 57.89% accuracy; no Phase-35 method exceeds it, and CatBoost only ties it.

### Recommended next phase
Freeze a small candidate set for a separate trading-overlay validation: OOF tree stack, Wavelet + tree, DART, CatBoost, ExtraTrees, and Markov-regime tree.

That phase must include exact option execution prices, Paytm Money brokerage/statutory charges, slippage, spread/liquidity constraints, expiry-gap handling, existing expiry-day stop rules, MAE/MFE, drawdown, regime stability, and no further tuning on the untouched holdout.

### Final artifacts
- results/phase35_advanced_tree_prediction/PHASE35_FINAL_MANUSCRIPT.md
- results/phase35_advanced_tree_prediction/PHASE35_FINAL_STATISTICAL_SUMMARY.csv
- results/phase35_advanced_tree_prediction/PHASE35_FINAL_DECISION_TABLE.csv
- results/phase35_advanced_tree_prediction/model_metrics.csv
- results/phase35_advanced_tree_prediction/directional_economic_diagnostic.csv
- results/phase35_advanced_tree_prediction/calibration_diagnostics.csv
- results/phase35_advanced_tree_prediction/uncertainty_summary.csv
- results/phase35_advanced_tree_prediction/ms_regime_tree_metrics.csv
- results/phase35_advanced_tree_prediction/ms_regime_tree_economic.csv
- results/phase35_advanced_tree_prediction/ceemdan_tree_metrics.csv
- results/phase35_advanced_tree_prediction/ceemdan_tree_economic.csv
- results/phase35_advanced_tree_prediction/phase35_holdout_accuracy.svg
- results/phase35_advanced_tree_prediction/phase35_holdout_signed_return.svg

### Final conclusion
**Phase 35 closes the prediction-model search. No predictor is promoted to live trading. Phase 20 remains canonical.**
