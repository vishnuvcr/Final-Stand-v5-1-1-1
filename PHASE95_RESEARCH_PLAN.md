# Phase 95 — Daily NIFTY Forecast-Method Replication

**Registered:** 2026-10-10  
**Branch:** `phase-95-daily-forecast-model-replication`  
**Parent:** `phase-94-paper-method-replication-program`  
**Status at registration:** implementation committed; empirical runtime output pending  
**Scope:** bounded price-level forecast replication and common baseline comparison; not options P&L

## Research question
Do the price-forecasting methods from U01, U03, U04, U06, U08, U09, U11, U12 and U13 improve on persistence under strictly chronological evaluation when placed on the same NIFTY daily price dataset, and how much of each paper's original claim can be reproduced without its exact dataset, external modalities and training settings?

## Preregistered protocol

### Data and split
- Primary dataset: daily NIFTY 50 OHLCV from Yahoo Finance `^NSEI`, fetched with `auto_adjust=False`, date range 2004-01-01 through 2025-12-31 (API end-exclusive 2026-01-01). Source URI, retrieval time, date bounds, row count, first/last date, source symbol and SHA-256 are written to `results/phase95/data_manifest.json`.
- Validated daily data are reused from `.cache/phase95/nifty_daily.csv` via GitHub Actions cache when available; raw market rows are not committed.
- Calendar year 2025 is the fixed common test block. 5-, 10-, and 20-calendar-year training windows end before 2025 starts. All model comparisons use aligned target dates within each target/window.
- The existing 2026 Phase 83 holdout is not accessed.
- This is a common-data/domain-adapted replication, not an exact recreation of other papers' stock universes, source-specific train/test splits, feature availability or published hyperparameter searches.

### Targets and models
- Primary target: next observed trading session's NIFTY close level, using inputs available no later than the preceding session.
- Supplemental targets: next-session open for source methods that forecast open/close; next-session high and low for U12's OHLC method.
- Tabular methods: persistence baseline; linear regression; Lasso; Ridge; Elastic Net; SGD regressor; SVR; KNN; decision tree; Random Forest; gradient boosting; AdaBoost; XGBoost; MLP; SLP-style linear neural baseline; RBF feature-network operationalization.
- Sequence methods for close target: vanilla RNN, LSTM, GRU, causal CNN, TCN, LSTM+GRU, CNN+RNN, CNN+TCN, LSTM+TCN and a train-only feature-pruned LSTM analogue for backward-elimination studies.
- Fixed settings in the runner are transparent operationalizations. Where the PDF omits exact settings or data, outcomes are partial, not exact reproduction. LSTM+BERT/news sentiment, FII/DII, PCR, option Greeks and historical option-price inputs are not silently replaced with price-only features; their availability is separately reported.

### Features and leakage controls
Features are current OHLCV, lagged returns, SMA(5/20/50), EMA(12/26), RSI(14), 20-day realized volatility and high-low range, computed from data available on or before the feature timestamp. Targets are shifted one observed session forward. Feature/target scalers are fitted only on training subsets. Hyperparameters are fixed before OOS scoring. Failed model fits receive explicit failure rows.

### Metrics and inference
For every model/window/target: MAE, RMSE, R-squared, MAPE, train/test counts and target-level persistence MAE. For close, also report next-close directional accuracy relative to current close. The primary effect is MAE improvement over persistence. Report a 5-observation circular moving-block-bootstrap 95% confidence interval (2,000 resamples, seed 90210), HAC/Newey-West paired loss-difference p-values (lag 5), and Holm-adjusted p-values across the compared variants. Price-level R-squared and source-specific “accuracy” percentages are not assumed to imply directional skill or profitable trading.

### Reproduction labels
- **PARTIAL / common-data replication:** method family tested consistently on NIFTY, but original universe, test dates, exact data, external modalities or training protocol differ.
- **REPRODUCED:** reserved for later paper-specific tests where source protocol, data/sample and metric are matched and a preregistered tolerance is met.
- **NOT REPRODUCED / INCONCLUSIVE / DATA-BLOCKED / NOT IDENTIFIABLE:** used according to Phase 94 definitions.
A common-data run cannot by itself upgrade a paper to REPRODUCED.

### Outputs
`results/phase95/REPORT.md`, `model_metrics.csv`, `data_manifest.json`, `modality_status.csv`, `coverage.csv`, `comparison.svg`, and `run_summary.json`. The workflow commits aggregate outcomes, status and error-log updates. Raw daily bars stay in the Actions cache.

## Acceptance gates
- Test target dates are strictly in 2025; no 2026 target rows are scored.
- All models use identical target/window-specific test rows and a persistence baseline.
- No target leakage; indicators and labels are aligned; scalers fit on training only.
- Every registered variant is either measured or explicitly failed/blocked.
- Confidence intervals, dependent-data inference and multiple-comparison correction are published.
- Missing external features, source-specific procedures and data limitations are explicit.
- Workflow runs automatically on phase code/plan changes and has a manual `workflow_dispatch` button.
- Results, status/error/research logs are updated regardless of positive, negative or blocked outcomes.

## Stopping rule
One fixed test-block run plus necessary implementation repairs is the entire Phase 95 scope. No tuning against 2025, repeated window search to find positive results, or 2026 holdout access. Once output and errors are reconciled, proceed to Phase 96.
