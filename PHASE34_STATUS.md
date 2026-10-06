# Phase 34 Status — Alternative NIFTY D−6 Prediction Models

## Current state
**COMPLETE — NO PROMOTION.**

### Scope
Tested eight model families not used as primary Phase-33 predictors plus two fixed ensembles:
- XGBoost
- ExtraTrees
- HistGradientBoosting
- RBF-SVM
- Elastic-Net Logistic Regression
- point-in-time HMM regime probability
- compact Transformer
- compact temporal-convolution model
- NEW_EQUAL_8
- TREE_EQUAL_3

Phase-33 Random Forest is retained as the control.

### Evidence
- Accepted numerical run #2: **37422865721**.
- Run #1: 37422843285 computed successfully but failed only at persistence because of a branch race; it is non-final.
- Postprocess run #7: **37423631294** completed successfully and persisted the summary tables and SVG figures.
- Phase-34 sample: **245 events = 128 development + 95 validation + 22 untouched 2026 holdout**.

### Key results
| Model | Validation accuracy | 2026 holdout accuracy | 2026 holdout log loss |
|---|---:|---:|---:|
| XGBoost | **57.89%** | 63.64% | 0.6843 |
| ExtraTrees | 50.53% | **68.18%** | 0.6435 |
| HistGradientBoosting | 54.74% | 63.64% | 0.6649 |
| RBF-SVM | 51.58% | 36.36% | 0.7205 |
| Elastic-Net Logistic | 51.58% | 63.64% | 0.6751 |
| HMM regime | 51.58% | 36.36% | 0.7402 |
| Transformer | 51.58% | 40.91% | 0.9395 |
| TCN | 51.58% | 36.36% | 0.7194 |
| Equal-weight 8 | 53.68% | **68.18%** | 0.6672 |
| Tree equal-3 | 54.74% | 63.64% | **0.6350** |
| Phase-33 RF control | 54.74% | 54.55% | 0.6562 |
| Always-down | 48.42% | 63.64% | 5.0238 |

### Economic diagnostic
- HistGradientBoosting: mean signed holdout log return **0.00832**, bootstrap 95% CI **0.00138 to 0.01534**, sign-flip p=**0.0363**. Its holdout accuracy only tied the always-down baseline, so the full promotion gate still fails.
- Equal-weight-8: 68.18% holdout accuracy and mean signed log return **0.00746**, but its bootstrap interval includes zero by a very small margin.
- TCN: mean signed holdout log return **−0.01005**, 95% CI **−0.01670 to −0.00374**.
- No candidate passed every preregistered validation, holdout and uncertainty gate.

### Decision
**No Phase-34 prediction model is promoted to trading. Phase 20 remains canonical.**

Any use of HistGradientBoosting, ExtraTrees or the equal-weight ensemble requires a fresh registered direction-overlay phase with the canonical strategy and full Paytm Money brokerage, statutory charges, slippage, execution/fill and expiry-gap modeling.

### Reporting artifacts
- `results/phase34_alternative_prediction/PHASE34_STATISTICAL_SUMMARY.csv`
- `results/phase34_alternative_prediction/PHASE34_DECISION_TABLE.csv`
- `results/phase34_alternative_prediction/PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md`
- `results/phase34_alternative_prediction/phase34_accuracy_comparison.svg`
- `results/phase34_alternative_prediction/phase34_holdout_signed_return_ci.svg`
- `results/phase34_alternative_prediction/model_predictions.csv`

### Research errors/corrections
- Phase-34 numerical run #1 persistence race: logged; run #2 accepted.
- Postprocess initially failed repeatedly due a naming mismatch between `rf_phase33_control` in model metrics and `rf_phase33` in the economic diagnostic. This was corrected and postprocess run #7 succeeded.
- Earlier failed postprocess outputs are explicitly non-evidence.

### Stop rule
Phase 34 is closed. No further model-family expansion is permitted under this registration. A materially different model search or a trading-overlay test must be a new research phase.
