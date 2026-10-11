# Phase 103 Visible Conversation and Decision Log

This log records user-visible conversation events and research decisions. It does not include hidden/private reasoning.

## 2026-10-11 — User requested a separate stock-options study

- User asked to freeze all prior data and create a separate branch to search for successful options strategies in NIFTY 50 stocks, selecting five stocks for the initial scope.
- Decision: isolate the work in `phase-103-nifty50-stock-options`; preserve earlier branches and results; prohibit reuse of index-options strategy P&L as stock-options evidence.
- The first five are HDFCBANK, ICICIBANK, RELIANCE, SBIN and INFY. This is a provisional study basket based on an official constituent-weight snapshot and visible option-contract discovery/activity, not a claimed top-five average-options-volume ranking.
- Accepted boundaries: no backtest until an authorised sample and comparable stock-option liquidity/coverage are verified; all costs including Paytm Money charges, spread, slippage and latency are mandatory; a failed or blocked outcome is recorded rather than bypassed.


## 2026-10-11 — Dhan data acquisition preference

- User specified: “Use the dhan data API access token for data”.
- Decision: DhanHQ API is the primary Phase 103.1 source. The workflow references repository secrets by candidate names and never exposes the token. It first checks the instrument master and a 30-day sample for the five frozen underlyings.
- Evidence policy: an API run must produce logged aggregate results before we claim successful access. No strategy backtest or promotion may proceed merely because connector code was committed.


## 2026-10-11 — User requested “Ok proceed”; publication and data gate completed

- User asked to proceed with the existing research plan. The current workflow was checked before advancing; the previous run's non-fast-forward publication failure was documented rather than treated as a data failure.
- Run [38124954633](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38124954633) completed successfully including safe result publication. The audit returned rows for all 28 selected Dhan probes and zero out-of-window timestamps.
- Added explicit `BLOCKED_EXPIRY_NOT_RETURNED` to the audit because the observed row schema does not return a verified expiry date or immutable contract identifier. Regression/workflow run [38125302970](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38125302970) passed 21 tests, returned data for all 28 probes, and successfully published the run-matched result after reconciling a concurrent push without force-pushing.
- Exact-strike union diagnostics: 1,925 union timestamps per panel; zero duplicate timestamp/actual-strike keys. Best union coverage: ICICIBANK CALL three strikes 100%, RELIANCE CALL/PUT 99.065%, SBIN CALL 94.130%. These are not expiry-verified contract-level histories.
- Public/free source review found no verified dataset meeting the registered intraday stock-options identity, executable-price and retention/cache rights gates. The branch was closed out at the data gate as **NO-GO for numerical intraday stock-options strategy P&L**. No P&L, strategy inference or strategy promotion was reported.
- Published the final data-feasibility manuscript and SVG coverage chart. Phases 103.2–103.6 remain unentered under the registered stop rule; 103.7 contains the bounded closeout. Reopening requires a new authorized sample meeting the registered gates.



## 2026-10-11 — User confirmed subscription and instructed continuation

- User said: “We have the rights! I have subscribed” and then “Ok proceed!”
- Research decision: accept the user's confirmation of their Dhan subscription and authorization for the intended research access; do not continue treating “subscription not established” as a reason to stop acquisition.
- Data handling remains conservative: raw Dhan minute rows and raw NSE EOD contract rows stay ephemeral in the runner. The repository and GitHub Pages outputs contain only aggregate audit counts, safe diagnostics and expiry-date counts, not raw price rows.
- Next bounded gate: independently reconcile full-session exact-strike Dhan OHLC against official NSE daily stock-option OHLC to test the expiryCode=1 selection. No strategy P&L until this identity and price-quality test passes; no profitability inference from the cross-check itself.


## 2026-10-11 — Bounded selector calibration exhausted

- User instructed: “Ok proceed!” after confirming Dhan subscription and rights.
- Code-1 full-panel run [38126663036](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38126663036): 28/28 API probes returned rows; 5/5 official NSE daily files downloaded; 88 full-session profiles; only 3 unique four-field OHLC matches (all expiry 2026-08-25); 0 expected rank-2 matches; 85 unmatched. No raw rows persisted.
- One code-0 near/current selector calibration [38127361683](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38127361683) returned HTTP 400 / DH-905 / “expiryCode is required” on the first ICICIBANK CALL ATM request. The run stopped with 0 data probes returned; no identity comparison could be made.
- Terminal action for this bounded calibration: stop searching expiry selectors. No strategy P&L or strategy promotion; require provider-confirmed contract identity or an authorized alternative historical contract dataset. Raw data remain ephemeral/public aggregates only.
