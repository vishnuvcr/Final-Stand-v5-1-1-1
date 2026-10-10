# Phase 90 — Incremental predictive value of ATM IV beyond spot and India VIX

Registered: 2026-10-10  
Branch: `phase-90-iv-incremental-prediction`  
Status: PREREGISTERED; execution begins when the workflow file is committed.

## Why this phase exists
Phase 89 found that mean ATM CALL/PUT IV was associated with the absolute next-15-minute NIFTY spot move in the 2025 Dhan rolling-options sample (Holm-adjusted p=0.0071). That finding does not answer whether IV adds useful prediction once lagged realized movement and an observable market-regime measure are already known. Phase 89’s 2025 period has been seen and must not be reused as a new confirmatory test here.

## Primary research question
On a separate Dhan rolling-options sample from calendar 2024, does adding contemporaneous ATM-relative mean IV to a frozen model of lagged NIFTY spot movement and India VIX reduce out-of-sample absolute prediction error for the next 15-minute absolute NIFTY spot return?

## Aims / objectives
1. Acquire paired NIFTY ATM CALL/PUT IV and spot, plus India VIX five-minute history, for 2024 only.
2. Verify the India VIX security ID from Dhan’s instrument master at runtime rather than hardcoding an ID.
3. Enforce exact CALL/PUT timestamp pairing, CALL/PUT strike matching, spot consistency, timestamp ordering, and within-session lag/forward intervals.
4. Compare three frozen OLS prediction models: (M0) lagged spot movement + time-of-day; (M1) M0 + India VIX level and trailing 15-minute VIX change; (M2) M1 + mean ATM CALL/PUT IV.
5. Fit every model on January–June 2024 only. July–September is a fixed validation display; October–December is the confirmatory OOS period, without model selection or tuning.
6. Use the single preregistered primary statistic: M1 MAE minus M2 MAE, in bps; positive means adding IV improves the M1 baseline. Construct a paired trading-session cluster bootstrap 95% confidence interval (5,000 fixed-seed resamples).
7. Report RMSE and OOS R-squared as secondary metrics; report performance by DEV-defined VIX tertiles as descriptive only, without additional significance tests.
8. Publish aggregate results and data-quality ledgers. Do not commit raw prices or API payloads.

## Frozen universe and requests
- Options API: `POST https://api.dhan.co/v2/charts/rollingoption`.
- Underlying: NIFTY index options, securityId 13, `NSE_FNO`, `OPTIDX`, monthly rolling ATM, CALL and PUT.
- Interval: five minutes. Requested fields: IV, strike, spot, timestamp, plus required OHLC/OI/volume arrays for schema/alignment validation.
- Options sample period: 2024-01-01 inclusive to 2024-12-31 exclusive; use 14-calendar-day request chunks (under the 30-day documented maximum). Request boundaries may not enter 2025. Retry failed chunks at most twice; a failed 14-day chunk may be retried as two 7-day halves, still strictly within 2024.
- Instrument master: resolve the unique NSE India VIX index record from Dhan’s official instrument master; record only match count and sanitized metadata required for reproducibility, not the entire master.
- VIX history API: `POST https://api.dhan.co/v2/charts/intraday`, 5-minute `IDX_I` / `INDEX` bars, using the instrument-master ID. Use at most 80 calendar days per request, strictly inside 2024.
- Raw API responses remain in the Phase 90 GitHub Actions cache. No raw data files are published.

## Feature engineering frozen before the run
- Outcome: `abs((spot[t+15m] / spot[t] - 1) * 10,000)` bps. Target rows are retained only when the forward timestamp is exactly 15 minutes later, within the same session, with no intervening gap.
- M0 spot features: trailing realized absolute returns summed over the previous 15 and 60 minutes; signed spot returns over the previous 15 and 60 minutes; cyclical time-of-day sine/cosine.
- M1 regime features: M0 plus India VIX close known at or before t, matched no more than five minutes stale, plus its trailing 15-minute percentage change. No future VIX values or backward extrapolation across sessions.
- M2 added feature: mean of CALL and PUT IV at t. CALL and PUT ATM strikes must match at t.
- No option premium return feature is used because the ATM-relative strike can roll over time.

## Splits and model training
- DEV / fit only: 2024-01-01 through 2024-07-01 exclusive.
- VALIDATION / reporting only: 2024-07-01 through 2024-10-01 exclusive.
- CONFIRMATORY OOS: 2024-10-01 through 2024-12-31 exclusive.
- Model feature scaling parameters and OLS coefficients are fit on DEV only and remain fixed in VALIDATION/OOS. Validation cannot tune features, thresholds or model form.
- Both M1 and M2 are evaluated on exactly the same observations with complete features/outcomes. Predictions for the nonnegative target are clipped at zero for both models before MAE/RMSE calculation.
- Primary paired session bootstrap: seed 90210, 5,000 resamples of OOS session clusters, preserve all rows inside each sampled session, recompute the row-weighted MAE difference. No rows are imputed.

## Acceptance / stopping gates
- All 2024 requests are bounded by the 2024 date window.
- API response arrays must be present and aligned; date, side, status, counts and sanitized error class are recorded.
- India VIX must be uniquely identified and at least 80% of otherwise valid paired option rows in the confirmatory OOS period must receive a valid VIX value within the five-minute as-of tolerance. Otherwise, the primary question is INCONCLUSIVE and no VIX-adjusted conclusion is made.
- OOS needs at least 1,000 complete rows across at least 30 sessions. Otherwise inferential results are descriptive only.
- Candidate signal is considered to add predictive value only if the 95% paired day-cluster bootstrap interval for M1 MAE − M2 MAE lies entirely above zero. Do not rely on raw coefficient p-values.
- Stop after this one fixed 2024 sample and one primary comparison. No parameter optimization, strategy P&L replay or additional sample search.
- Do not request/load the protected 2026 Phase 83 holdout.

## Interpretation and boundaries
A positive result would support incremental prediction of *spot move magnitude*, not directional prediction, options profitability or causality. Historical bid/ask/depth and exact listed-contract reconstruction are not provided by the rolling endpoint. No transaction-cost-adjusted strategy conclusion can be drawn from this phase. Any later executable replay must include Paytm Money brokerage, statutory levies, spread, slippage and latency.

## Official data documentation
- Dhan expired-options endpoint: https://dhanhq.co/docs/v2/expired-options-data/
- Dhan historical intraday candles: https://dhanhq.co/docs/v2/historical-data/
- Dhan instrument master and security IDs: https://dhanhq.co/docs/v2/instruments/
