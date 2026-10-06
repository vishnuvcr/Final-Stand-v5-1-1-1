# Phase 33 Research Plan — NIFTY D−6 Prediction Models

## Research question
At exactly 10:00 IST on 6 calendar days before each NIFTY 50 weekly expiry, can point-in-time prediction models forecast the subsequent expiry-day NIFTY close direction and magnitude well enough to justify a direction-selection overlay for the Continuous Delta 6x6 study?

## Secondary question
Do the requested model families — LSTM, GARCH, sentiment-augmented self-organizing fuzzy neural network (SOFNN), Random Forest/ensemble — add incremental predictive value over simple baselines under strict chronological out-of-sample testing?

## Locked reference point
For each expected weekly expiry E:
- reference timestamp = E minus 6 calendar days at 10:00:00 IST;
- exact 10:00 observation is required;
- if the calendar date is not a valid trading date or the exact 10:00 observation is absent, the event is excluded and logged rather than shifted.

## Locked targets
Primary directional target:
- y = 1 if NIFTY expiry-day closing spot > reference spot; otherwise 0.
Regression target:
- log_return = ln(expiry_close / reference_spot).
Volatility target:
- squared log_return and, where minute coverage permits, realized variance over the reference-to-expiry horizon.

Expiry close convention:
- latest complete NIFTY spot observation at or before 15:29 IST on the expiry date.

## Candidate models
### M1 — LSTM
A small, reproducible LSTM using a fixed lookback of the previous 30 trading sessions of NIFTY-derived features available by each reference timestamp. Primary output: continuous horizon return; direction = sign(return).

### M2 — GARCH family
GARCH(1,1), EGARCH(1,1), and GJR-GARCH(1,1) fitted only on returns available before the reference timestamp. Primary output: multi-day conditional volatility forecast. Directional probability is obtained only through a pre-specified conditional-drift mapping, not by tuning the sign after seeing outcomes.

### M3 — Sentiment-SOFNN
A self-organizing fuzzy-neural classifier inspired by the published SOFNN approach. Inputs include point-in-time financial-news sentiment aggregates available before the reference cutoff plus NIFTY regime variables. The implementation is explicitly labelled SOFNN-inspired unless the exact published architecture can be reproduced from an accessible source.

### M4 — Random Forest
Random Forest classifier using technical, volatility, cross-market and sentiment features available before the cutoff.

### M5 — Fixed-weight ensemble
Equal-weight probability ensemble of M1/M3/M4 direction probabilities. GARCH contributes a confidence/range gate only; it does not get a post-hoc weight.

## Feature families
Primary price/volatility:
- 1/3/5/10/20/30-session returns;
- rolling standard deviations and realized volatility;
- ATR/range, distance to moving averages, RSI and MACD-style trend features;
- current-session return from prior close to the 10:00 reference;
- drawdown from rolling highs.

Global/cross-market:
- prior-session S&P 500, Nasdaq, Dow, Nikkei and USD/INR returns where available;
- prior-session VIX / India VIX proxies where available;
- gold and crude oil returns where available.
Same-day global values are forbidden when their market has not closed by 10:00 IST.

Sentiment:
- daily aggregate positive/negative/neutral sentiment from the cached Indian financial-news dataset;
- the primary sentiment-augmented SOFNN subtrack uses 2024 as development, 2025 as validation and 2026 as holdout because the selected source begins in January 2024.
- 1/3/5/7-day sentiment means and breadth;
- no forward-return or target columns from any sentiment dataset may be used as features.

Institutional flow:
- FII/FPI and DII net equity flow plus selected index futures/options positioning from the cached open-source history; joins are strictly backward-looking and missing periods remain missing.

Options/market microstructure (event-level diagnostic where coverage is available):
- reference-time ATM/near-ATM call/put volume and open interest;
- put-call OI ratio;
- normalized near-ATM call/put premium differences.
Option features are secondary because the public option history is explicitly partial.

## Data sources
Primary NIFTY:
- Hugging Face thetrademarkk/india-index-options-1m.
Sentiment:
- Hugging Face dixitdharmansh07/indic-finance.
Global markets:
- a reproducible market-data source captured into the Phase-33 cache before modeling.
Public web literature and source audits are retained in results/phase33_nifty_prediction/PHASE33_LITERATURE_REVIEW.md.

## Chronological evaluation
Primary split:
- development/training: earliest eligible observations through 2023-12-31;
- validation: 2024-01-01 through 2025-12-31;
- untouched holdout: 2026-01-01 through 2026-09-30.

Within development, model hyperparameters are fixed before validation. No holdout observation is used for model selection.

For LSTM training, all scalers are fit only on the training fold.
For Random Forest/SOFNN/GARCH, fitting uses only information available before each prediction date.

## Statistical analyses
Directional:
- accuracy;
- balanced accuracy;
- ROC-AUC;
- log loss;
- Brier score;
- calibration error where feasible.

Regression:
- MAE;
- RMSE;
- directional hit rate of predicted return.

Volatility:
- RMSE;
- MAE;
- QLIKE;
- correlation between forecast volatility and realized volatility.

Economic:
- model-directed direction hit/miss by expiry;
- comparison with always-CALL, always-PUT, and 50/50 baselines;
- only after predictive scoring, a frozen overlay is tested against the Phase-32 strategy under identical execution-cost assumptions.

Uncertainty:
- bootstrap confidence intervals for mean forecast score and mean strategy uplift;
- paired permutation/sign tests for model-vs-baseline directional accuracy where applicable.

## Promotion gates
A model is considered predictive only if it improves at least one primary out-of-sample metric over the strongest simple baseline without worsening the others materially.
A trading overlay is considered for paper validation only if:
- positive validation and holdout economic uplift;
- no look-ahead;
- complete cost/slippage accounting;
- no dependence on missing data;
- stability across subperiods/regimes.

No threshold, model family, feature or ensemble weight may be added after seeing holdout results. A materially different model is a new phase.

## Phase sequence
1. Freeze plan, pre-registration, data dictionary and literature review.
2. Build and cache the compact point-in-time event dataset.
3. Audit reference timestamps, expiry mapping and leakage controls.
4. Implement M1–M4 and fixed ensemble.
5. Run chronological validation and untouched holdout.
6. Statistical and regime analysis.
7. Optional frozen direction-overlay test against Phase 32.
8. Produce manuscript, figures, tables, appendix, limitations and final decision.
9. Update main README/status and close the phase.

## Stopping rule
The phase stops after the preregistered model families and economic overlay test are exhausted. It must not become an unbounded feature/threshold search.
