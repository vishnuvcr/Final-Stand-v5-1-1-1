# Phase 35 Status — Advanced Tree and Adaptive Prediction Search

## Current state
**COMPLETE — NO LIVE-TRADING PROMOTION**

### Evidence set
- 245 eligible events: 128 development, 95 validation, 22 untouched 2026 holdout.
- Final accepted numerical run: GitHub Actions run **37425240176**.
- Markov-switching regime addendum numerical output persisted; the first masked failure and subsequent corrections are logged in `ERROR_LOG.md`.
- Phase 20 remains canonical for the trading strategy.

### Main battery — validation / 2026 holdout
| Model | Validation accuracy | Holdout accuracy |
|---|---:|---:|
| XGBoost | 57.89% | 63.64% |
| LightGBM | 54.74% | 63.64% |
| CatBoost | 57.89% | **68.18%** |
| ExtraTrees | 50.53% | **68.18%** |
| HistGradientBoosting | 54.74% | 63.64% |
| LightGBM-DART | 47.37% | **68.18%** |
| Equal 6-tree pool | 54.74% | 59.09% |
| RFE-LightGBM | 49.47% | 50.00% |
| NGBoost | 54.74% | 54.55% |
| Quantile tree | 50.53% | 50.00% |
| BART | 55.79% | 54.55% |
| Wavelet + tree | 50.53% | **68.18%** |
| EMD + tree | 49.47% | 45.45% |
| VMD + tree | 55.79% | 54.55% |
| Adaptive 52-event | 51.58% | 36.36% |
| Adaptive EW | 52.63% | 59.09% |
| Dynamic pool | 54.74% | 63.64% |
| OOF stack | 51.58% | **68.18%** |
| Platt | 47.37% | 50.00% |
| Isotonic | 50.53% | 54.55% |
| Conformal abstention | 51.58% | 36.36% |
| Markov-switching regime + tree | 53.68% | **68.18%** |

### Economic diagnostic
The strongest holdout signed-return means were:
- OOF stack: **+0.00951**, bootstrap 95% CI **[+0.00255, +0.01627]**, sign-flip p=0.0139.
- Wavelet + tree: **+0.00880**, CI **[+0.00164, +0.01560]**, p=0.0252.
- LightGBM-DART: **+0.00856**, CI **[+0.00139, +0.01561]**, p=0.0311.
- LightGBM: **+0.00844**, CI **[+0.00132, +0.01550]**, p=0.0350.
- Markov-switching regime + tree: **+0.00868**, CI **[+0.00154, +0.01559]**, p=0.0267.

However, the 2026 holdout contains only **22 events**. Several methods are therefore statistically fragile, and the raw directional diagnostic is not executable option P&L.

### Uncertainty
Conformal intervals achieved approximately:
- Validation coverage: **89.47%** for the nominal 90% interval.
- Holdout coverage: **86.36%**.
- No event met the implementation's strict confident-direction rule, so conformal abstention did not provide a useful trading filter in this sample.

### Decision
**No Phase-35 model is promoted directly to live trading.**

Reason:
1. The holdout is too small for model selection by raw accuracy alone.
2. Several strong-looking models are correlated tree variants rather than independent evidence.
3. Validation performance does not uniformly agree with holdout performance.
4. The signed-return diagnostic is not option-strategy P&L.
5. Transaction costs, Paytm Money brokerage/statutory charges, slippage, fills, spread, liquidity, expiry gaps and the actual Continuous Delta 6x6 payoff have not yet been incorporated into this prediction-model screen.

### Recommended next phase
A dedicated **direction-chooser overlay validation** should freeze a small candidate set (CatBoost, DART, Wavelet-tree, OOF stack, Markov-regime tree) and test them prospectively against the Continuous Delta 6x6 strategy with:
- exact entry/exit rules;
- option-chain execution prices;
- Paytm Money charges;
- slippage and fill assumptions;
- expiry-day gap handling;
- existing expiry-day stop-loss rules;
- MFE/MAE;
- drawdown and risk-adjusted return;
- regime-by-regime performance;
- no further model tuning on the 2026 holdout.

### Research files
- `PHASE35_RESEARCH_PLAN.md`
- `PHASE35_PRE_REGISTRATION.md`
- `PHASE35_DATA_DICTIONARY.md`
- `results/phase35_advanced_tree_prediction/model_metrics.csv`
- `results/phase35_advanced_tree_prediction/directional_economic_diagnostic.csv`
- `results/phase35_advanced_tree_prediction/PHASE35_DECISION_TABLE.csv`
- `results/phase35_advanced_tree_prediction/uncertainty_summary.csv`
- `results/phase35_advanced_tree_prediction/ms_regime_tree_metrics.csv`
- `results/phase35_advanced_tree_prediction/ms_regime_tree_economic.csv`
