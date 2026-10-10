# Phase 92 — Synthetic-forward proxy and CALL/PUT OI incremental prediction study (calendar 2022)

Registered: 2026-10-10  
Branch: `phase-92-synthetic-forward-oi-study-2022`  
Status: PREREGISTERED — one fixed study; no strategy P&L in scope.  
Parent: [Phase 91 terminal IV replication](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-91-iv-temporal-replication-2023)

## Research question

On an independently acquired 2022 Dhan rolling-ATM options sample, does adding (a) a same-strike CALL/PUT synthetic-forward proxy gap and (b) a CALL/PUT open-interest imbalance improve out-of-sample prediction of the absolute next-15-minute NIFTY spot return beyond lagged spot features, India VIX and mean ATM IV?

This is a predictor-quality question only. It is not a test of actual futures prices, arbitrage, option direction, or options-strategy profitability.

## Rationale

Phase 90/91 studied IV's incremental predictive value and stopped that line because the small 2024 result did not replicate on the fixed 2023 sample. The broader factor programme still has a distinct untested feature block: synthetic-forward proxy and contemporaneous CE/PE OI imbalance. Phase 60/61 separately concluded that exact-contract execution-grade historical OI/quotes remain source-gated; Phase 92 will not repeat those source searches or claim fills.

Dhan's official [expired-options documentation](https://dhanhq.co/docs/v2/expired-options-data/) describes up to five years of rolling ATM-relative options data with OHLC, IV, volume, OI, strike and spot, with requests limited to 30 days and a non-inclusive `toDate`. Its [historical intraday documentation](https://dhanhq.co/docs/v2/historical-data/) describes historical candles but for active instruments. This phase therefore uses the documented rolling-options fields and does not claim an exact historical FUTIDX series. As of registration, calendar 2022 falls inside the stated five-year rolling-options window.

## Aims and objectives

1. Acquire paired NIFTY monthly rolling-ATM CALL/PUT five-minute data and India VIX for calendar 2022 only.
2. Resolve India's VIX security ID at runtime from Dhan's instrument master, never hardcode it.
3. Validate array alignment, timestamp bounds, unique timestamps, CALL/PUT spot consistency and exact strike matching.
4. Engineer the synthetic-forward proxy (F_{syn}=K+C-P) using paired CALL/PUT bar closes and a normalized proxy gap (10{,}000(F_{syn}-S)/S) bps.
5. Engineer same-time OI imbalance ((OI_{CE}-OI_{PE})/(OI_{CE}+OI_{PE})), defined only when the denominator is positive. This is not treated as a literal directional-position or sentiment measure.
6. Use a conservative point-in-time convention: Dhan documents rolling candle timestamps as candle-start timestamps. Lag option-derived IV, option close/synthetic-forward proxy and OI features by one complete five-minute row; lag VIX by one row too. This avoids using a candle's closing information before it is available.
7. Compare five frozen models on exactly the same complete observations: M0 spot/time; M1 M0+VIX; M2 M1+mean ATM IV; M3 M2+synthetic-forward proxy gap; M4 M3+OI imbalance.
8. Fit on Jan–Jun 2022 only; Jul–Sep is report-only validation; Oct–Dec is confirmatory OOS. Standardization and coefficients are fitted on DEV only.
9. The single primary statistic is OOS MAE(M2) − MAE(M4), in bps, with a paired session-cluster bootstrap confidence interval (5,000 resamples; fixed seed 90210). M2-to-M3 and M3-to-M4 are secondary descriptive comparisons, not additional hypothesis tests.
10. Publish only aggregate metrics and sanitized coverage/error ledgers; raw API responses remain in the Phase 92 Actions cache and must not be committed or uploaded as artifacts.

## Feature definitions

- Target: (|(S_{t+15}/S_t-1) 	imes 10{,}000|) bps. Both spot timestamps must be exactly 15 minutes apart within the same session, and no target may cross a missing interval/session boundary.
- M0 features: previous 15/60-minute realized movement, signed spot returns over 15/60 minutes and time-of-day sine/cosine.
- M1 adds India VIX close known by the forecast start and the trailing 15-minute VIX change; both are lagged conservatively to the preceding completed candle.
- M2 adds mean CALL/PUT IV from the prior completed five-minute bar.
- M3 adds the prior completed bar's (F_{syn}=K+C-P) proxy gap relative to spot. Because exact expiry/time-to-maturity and rates are not established by this rolling endpoint, the gap is a predictor feature only—not an arbitrage residual.
- M4 adds prior-bar OI imbalance. The underlying rolling ATM strike can change over time; no OI changes across rolling-strike transitions are used.

## Splits, statistics and acceptance gates

- DEV/fit only: 2022-01-01 inclusive to 2022-07-01 exclusive.
- VALIDATION/reporting only: 2022-07-01 inclusive to 2022-10-01 exclusive.
- CONFIRMATORY OOS: 2022-10-01 inclusive to 2023-01-01 exclusive.
- All five model specifications use the same rows with complete lagged features and target; no imputation is allowed.
- Data gate: one unique VIX instrument-master match; at least 80% valid lagged VIX coverage in OOS.
- Sample gate: at least 1,000 complete OOS rows over at least 30 sessions. Training gate: at least 1,000 complete DEV rows and 100 VALIDATION rows.
- Only claim an incremental predictive gain if all gates pass and the entire paired session-cluster bootstrap 95% interval for M2 MAE − M4 MAE is above zero. An interval that includes zero is inconclusive for a gain; it is not proof of no information.
- VIX-regime results are descriptive only and cannot be used for feature/strategy selection.

## Limitations and boundaries

- ATM-relative data do not identify an unchanged listed contract across time and do not provide historical bid/ask/depth or executable fills.
- (F_{syn}=K+C-P) is a rolling ATM synthetic-forward proxy from candle closes, not an actual traded FUTIDX candle or executable synthetic position. It can reflect carry, moneyness, expiry changes and quote/microstructure noise; do not call it arbitrage.
- The available endpoint does not supply the exact historical NIFTY futures contract mapping across expiries, so direct FUTIDX basis, actual futures/OI, Greeks and execution profitability are not evaluated in this phase. Do not synthesize missing futures records.
- This study does not use or unseal the Phase 83 2026 holdout. No options strategy is promoted. Any later trading replay needs authorized exact-contract data plus Paytm Money brokerage, statutory charges, spread, slippage, latency and cost stress.

## Stopping rule

One fixed 2022 run plus audit is the entire scope of Phase 92. Do not extend to additional years, tune features, or search for a positive result if the preregistered gain criterion fails. Reopen only with a materially new hypothesis or authorized execution-grade data.

## Related records

- [Phase 91 cross-year synthesis](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-91-iv-temporal-replication-2023/results/phase91/CROSS_YEAR_SYNTHESIS.md)
- [Phase 60 evidence-sufficiency gate](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-60-evidence-sufficiency-gate)
- [Phase 61 source restart audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-61-new-source-restart-audit)
