# Phase 88 — Dhan options gap coverage audit

Date: 2026-10-10
Branch: `phase-88-dhan-options-gap-coverage-audit`
Status: IN PROGRESS — bounded four-series coverage workflow committed; Actions result pending.

## Research question
Does Dhan's rolling expired-options endpoint return usable, aligned option OHLC/IV/OI/volume/strike/spot/timestamp arrays on the two previously identified missing sessions, 2026-07-28 and 2026-08-04, for both call and put sides?

## Aim and objectives
1. Use the Phase 86/87 verified token and endpoint.
2. Probe exactly two dates and two sides per date (four API requests total).
3. Record HTTP status, candle count, array presence and length alignment.
4. Keep all raw prices and response bodies out of logs, repository artifacts and workflow summaries.
5. Decide whether Dhan rolling options can provide factor-study coverage for those dates.
6. Explicitly separate this rolling-data result from exact-contract execution quality.

## Method
- Read Phase 87 status, plan and error log first.
- Use Dhan `POST /v2/charts/rollingoption`, five-minute bars, NIFTY index-option underlying, ATM, monthly expiry code 1, CALL and PUT.
- Windows: 2026-07-28 only and 2026-08-04 only (end date exclusive).
- Request OHLC, IV, volume, strike, OI and spot; test alignment with timestamp arrays.
- Four calls only, one-second spacing, no retry, no broad downloads.
- Do not place orders, run strategy backtests, cache raw data, or access Phase 83 holdout.

## Acceptance gates
- A: each of four requests returns HTTP 200.
- B: each response has non-empty timestamp and OHLC arrays.
- C: all requested field arrays are present and length-aligned.
- D: record per-date/per-side coverage without raw values.
- E: treat success only as rolling ATM-relative data availability; exact contract and historical bid/ask/depth remain separate gates.
- F: freeze Paytm Money brokerage, statutory charges, slippage and latency before any execution-quality replay.

## Stop rule
Stop after these four requests. If all pass, recommend a separate finite date/coverage analysis; do not bulk-download or promote a strategy. If any fail, log the failed date/side and continue only with available, explicitly qualified evidence.

## Statistical analysis
No profitability or hypothesis tests are run. This phase only tests API coverage and array integrity.

## Sources
- Dhan expired-options data: https://dhanhq.co/docs/v2/expired-options-data/
- Dhan historical data: https://dhanhq.co/docs/v2/historical-data/
