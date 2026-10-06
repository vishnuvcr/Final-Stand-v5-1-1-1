# Phase 34 Manuscript — Alternative NIFTY D−6 Prediction Models

## Abstract
Phase 34 tested eight model families not used as primary models in Phase 33: XGBoost, ExtraTrees, histogram gradient boosting, RBF-SVM, elastic-net logistic regression, a point-in-time HMM regime model, a compact Transformer and a compact temporal-convolution model. Two fixed ensembles were also evaluated. The reference remained exactly 10:00 IST on six calendar days before expiry, with chronological development, validation and untouched 2026 holdout periods.

## Sample
245 eligible events: 128 development, 95 validation and 22 holdout.

## Methods
All tabular models use the same Phase-33 point-in-time event feature set. Sequence models use 30 completed NIFTY sessions before each reference. The HMM is fitted only to daily data strictly before each test reference. No hyperparameter tuning was performed on the holdout.

## Results
The best new-family validation model by log loss was **xgb** (accuracy 0.579, log loss 0.6769). The best new-family holdout model by log loss was **tree_equal_3** (accuracy 0.636, log loss 0.6350). Exact model-by-model results are in PHASE34_DECISION_TABLE.csv and model_metrics.csv.

## Statistical inference
Bootstrap confidence intervals and sign-flip tests were computed for model-signed expiry-horizon log returns. These diagnostics are predictive diagnostics, not executable option P&L.

## Decision
No model is promoted directly to trading from this phase. Any candidate that appears attractive must survive a separate frozen direction-overlay backtest against the canonical strategy with Paytm Money brokerage, statutory charges, slippage, fill constraints and expiry-gap handling.

## Limitations
The event sample remains small, the 2026 holdout contains only 22 events, and deep sequence models have limited statistical degrees of freedom. Public option-chain and sentiment coverage is incomplete and therefore cannot be interpreted as universally available live information.

## Conclusion
Phase 34 provides an expanded model-family comparison without changing the canonical strategy. The research stops here unless a new phase is explicitly registered for a trading overlay or a materially different forecasting family.
