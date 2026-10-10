# Phase 92 Chat / Decision Log

Date: 2026-10-10

## User request
User replied “Ok proceed” after completion of the Phase 91 temporal replication.

## Prior state checked
- Read current main README and Phase 91 plan/status/error/chat/synthesis.
- Read Phase 60 and Phase 61 source-sufficiency decisions before proposing the next phase.
- Phase 91 concluded no reliable replicated incremental ATM-IV predictor gain (latest run 38049680438). The IV-only line is closed at its registered stop.
- Phase 60/61 remain NO-GO for empirical execution-grade options strategy tests until documented data rights and exact contract/timestamp coverage are available. Do not repeat the same metadata-only source search.
- Official Dhan docs state rolling expired options history extends up to five years, allows up to 30 days per call, and `toDate` is non-inclusive. Historical candle timestamps are candle-start timestamps. This motivates 2022 rolling-option data with a one-bar feature lag.

## Phase 92 decision
Run one bounded 2022 study of a lagged ATM synthetic-forward proxy gap and CE/PE OI imbalance as predictors beyond spot/VIX/IV. Use Jan–Jun DEV, Jul–Sep reporting-only validation, Oct–Dec confirmatory OOS. One primary endpoint: M2 MAE minus M4 MAE; paired session-cluster bootstrap, 5,000 draws, seed 90210. This tests predictive contribution, not strategy P&L or actual futures arbitrage.

## Point-in-time control
Because source candle timestamps are candle-start time and close-derived features cannot be known at the candle start, option-derived IV, OI, and synthetic-proxy values are lagged one whole 5-minute row; VIX close is also lagged one row. This conservative design is registered before execution. Direct FUTIDX basis is omitted rather than guessed because exact historical futures contract mapping is not supplied by the rolling-options endpoint.

## Execution log
Phase 92 branch and preregistration files are being added. The next record must report the actual Actions run and result. Raw option prices and market payloads are not to be committed or uploaded.

<!-- PHASE92_RUNTIME_START -->
## Automated execution record — 38050805106
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106
- Status: NEGATIVE INCREMENTAL VALUE — synthetic-forward/OI feature block worsens OOS magnitude prediction in this sample
- VIX ID resolved dynamically: True
- Options valid chunks=54/54; VIX valid chunks=5/5
- OOS rows/sessions=3660/61
- Primary result: M2 MAE − M4 MAE = -0.1708 bps (paired session-cluster bootstrap 95% CI -0.2299 to -0.1152; bootstrap positive share 0.0000; 5000 resamples; seed 90210).
- Option-derived close/IV/OI features were lagged one full five-minute row; no raw market responses were printed, committed, or uploaded as artifacts.
- Phase 83's 2026 holdout was not requested.
<!-- PHASE92_RUNTIME_END -->
