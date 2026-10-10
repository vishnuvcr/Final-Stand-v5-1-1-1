# Phase 91 — Temporal replication of IV incremental prediction (calendar 2023)

Registered: 2026-10-10  
Branch: `phase-91-iv-temporal-replication-2023`  
Status: PREREGISTERED; run begins when the workflow is committed.  
Parent evidence: [Phase 90](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-90-iv-incremental-prediction)

## Rationale and question

Phase 90 reported a small incremental OOS improvement when mean ATM CALL/PUT IV was added to lagged spot-movement features and India VIX: M1 MAE − M2 MAE = +0.0330 bps, 95% session-cluster bootstrap CI +0.0001 to +0.0562 bps. Its lower interval limit is close to zero. A distinct period is needed before drawing a stronger predictive conclusion.

**Primary research question:** Does adding mean rolling ATM-relative NIFTY CALL/PUT IV improve out-of-sample prediction of the next-15-minute absolute NIFTY spot return, beyond lagged spot movement and India VIX, on an independently acquired 2023 sample?

## Aims and objectives

1. Independently collect 2023 Dhan rolling ATM-relative CALL/PUT IV and spot series, and five-minute India VIX history.
2. Resolve India VIX’s security ID dynamically from the current Dhan instrument master.
3. Enforce timestamp, CALL/PUT pairing, strike agreement, spot consistency, exact lag/forward horizons, and session-bound VIX as-of matching.
4. Apply the same model family and feature definitions as Phase 90: M0 spot/time features; M1 plus VIX level/change; M2 plus mean ATM IV.
5. Fit only on Jan–Jun 2023; show Jul–Sep as report-only validation; reserve Oct–Dec 2023 as confirmatory OOS.
6. Evaluate the single primary endpoint, M1 MAE minus M2 MAE, using a paired session-cluster bootstrap (5,000 resamples, seed 90210).
7. Report RMSE/R² and DEV-tertile VIX-regime descriptives without extra inferential tests.
8. Publish only aggregated metrics and sanitized coverage/error information; never publish raw price/API payloads.

## Design and frozen protocol

- **Universe:** NIFTY index options (Dhan underlying security ID 13), monthly rolling ATM, CALL and PUT, five-minute bars; India VIX from the official Dhan instrument master and five-minute index history.
- **Study bounds:** options and VIX requests are strictly 2023-01-01 inclusive to 2024-01-01 exclusive. A request ending at midnight on 2024-01-01 is only an exclusive boundary: no 2024 observations may enter the sample. Requests are chunked to remain below documented API limits and use bounded retries/splits.
- **Feature/outcome definitions:** unchanged from Phase 90. Outcome is absolute next-15-minute spot return in basis points, requiring an exact same-session t+15m observation. M0 uses trailing 15/60-minute realized movement, signed 15/60-minute spot returns and time-of-day sine/cosine. M1 adds VIX level and trailing 15-minute VIX percentage change. M2 adds mean CALL/PUT IV at t.
- **Contract/rolling controls:** CALL and PUT strikes must match at each paired timestamp; inconsistent pairs are excluded and counted. ATM-relative option premium returns are not used because rolling strikes are not a stable listed contract.
- **VIX controls:** unique eligible instrument-master match; merge only as of timestamp t, at most five minutes stale and within the same session. No future VIX values or cross-session carry.
- **Splits:** DEV 2023-01-01 through 2023-07-01 exclusive; validation 2023-07-01 through 2023-10-01 exclusive; confirmatory OOS 2023-10-01 through 2024-01-01 exclusive.
- **Training:** standardization and OLS coefficients are fitted on DEV only; no tuning on validation/OOS. Both compared models use the exact same complete OOS rows; predictions clipped to zero for the nonnegative outcome.
- **Primary statistic:** MAE(M1) − MAE(M2) in bps. Positive means M2 improves prediction. Bootstrap whole trading-session clusters, row-weighted within each sampled bootstrap, 5,000 resamples and fixed seed 90210.
- **Gates:** at least 1,000 complete OOS observations over at least 30 sessions; India VIX valid as-of coverage at least 80%; instrument master yields one unique eligible VIX record. A predictive gain is established only if the complete 95% bootstrap interval is above zero. If a data/sample gate fails, report INCONCLUSIVE.
- **Independent run:** cache namespace and output paths are Phase 91-specific; no Phase 90 cache/payload is reused. 2025 Phase 89 data is not requested. Phase 83's protected 2026 holdout must not be requested, loaded or used for selection.

## Statistical analysis and interpretation

The primary inference is the paired day/session-cluster bootstrap interval for the MAE improvement. RMSE and R², validation performance, and VIX regime subgroups are secondary/descriptive only; no extra subgroup p-values or tuning. A negative/overlapping-zero primary interval means this replication does not establish a reliable incremental gain; it does not prove IV contains no information.

This is a temporal predictive replication, not causal identification and not a trading-strategy test. Rolling ATM-relative IV/spot data do not establish exact-contract premium fills, historical bid/ask/depth or executable latency. Therefore no strategy P&L or strategy promotion is allowed in this phase. Any future rule-level replay must reconstruct the exact listed contracts and include Paytm Money brokerage, statutory levies, bid/ask spreads, slippage, latency and stress costs.

## Stop condition

One complete 2023 run and its audit are the full scope of Phase 91. Do not recursively search years or tune the model based on the result. If evidence remains too weak, the decision is to stop this IV-prediction line pending a materially better execution-grade dataset or a separately preregistered hypothesis.

## Data documentation

- Dhan expired-options data: https://dhanhq.co/docs/v2/expired-options-data/
- Dhan historical data: https://dhanhq.co/docs/v2/historical-data/
- Dhan instrument master: https://dhanhq.co/docs/v2/instruments/
