# Phase 64 Status — Paper-derived CCI strategy tests

**State: IN PROGRESS — plan frozen and committed; implementation, automated test and numerical evidence pending. No strategy promotion.**

- Branch: phase-64-paper-derived-strategy-tests
- Source paper: Pinkal Shaha (2019), CCI-based NIFTY monthly in-the-money long-option rule, supplied PDF ssrn-3323746.pdf; public abstract: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3323746
- Additional adaptation: same CCI rule plus daily EMA(50)/EMA(200) trend confirmation, frozen before the backtest.
- Source dataset planned: thetrademarkk/india-index-options-1m at pinned commit 3eacf762d401efd9a08e804592fa7882b354c4a2. Dataset license is CC-BY-NC-4.0; no raw files will be committed or uploaded.
- Available chronological split: DEV 2021-05-27–2023-12-31, VAL 2024-01-01–2025-12-31. The runner is explicitly barred from loading or using 2026 option files and drops 2026 index rows before feature construction.
- This is not a reproduction of the original 2008–2018 dataset; those historical years are not covered by the selected source.
- Dataset provides OHLC, not bid/ask/depth. The execution model is a one-tick-adverse OHLC close proxy, not executable quotes.
- Costs: existing date-aware Phase-43 historical charges, primary one-tick slip, ₹10/order and ₹20/order scenarios, +50% fee/charge stress, and separate 10% price slippage sensitivity.
- Validation promotion gates: >=20 completed trades, >=95% coverage, positive net under all registered cost cases including stressed ₹20/order, adequate 95% statistical interval/permutation/Holm gate; even then this phase is research only and requires a separate decision. No HOLD-based tuning.
- Workflow not yet validated; actual numerical result must be inspected before labeling the test PASS or NO-GO.

## Current decision
No numerical conclusion yet. The research plan is frozen; next gate is code/data QA and bounded DEV/VAL run.


## Runtime and point-in-time audit checkpoint — 2026-10-10

- First automated workflow run: [38026911131](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38026911131). Checkout, cache restoration, dependency installation, syntax check and unit tests passed. Numerical execution was cancelled before producing accepted results.
- A source-code self-audit found that contract selection must be based on contracts observable at the breakout minute, not on later availability.
- Correction committed: strike candidates must have an observed bar at the trigger minute; the actual entry price must still exist at the exact following minute. A regression test covers future-only contract availability.
- The cancelled run is non-evidence. Current numerical test status remains PENDING; inspect the corrected automated run and its outputs before interpreting results.

## Final numerical run — 2026-10-10

- Corrected run https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38027023283 completed successfully: syntax/unit tests, numerical runner, report generation, output validation, aggregate publication and artifact upload all passed.
- Data gate: 56 late-month option files in the pinned source; 32 DEV and 24 VAL monthly-expiry proxies; 2026 option files downloaded = 0.
- Strategy result: 0 completed trades in all four variant/split combinations. CCI_BASE produced 12 DEV / 13 VAL breakout-triggered opportunities, but none passed entry/coverage gates. CCI_EMA_FILTER produced 4 DEV / 1 VAL breakout-triggered opportunity, also with zero completed trades.
- Therefore P&L, win rate, expectancy, profit factor and drawdown are not estimable; printed zero sums are empty-sample placeholders, not evidence of zero economic return. Both candidates fail minimum 20 validation trades and 95% trigger coverage. No statistical inference was attempted.
- Decision: RESEARCH_ONLY_NO_PROMOTION; empirical strategy efficacy remains untested because the chosen dataset/execution protocol could not produce covered trades. This is a data/protocol failure, not evidence that CCI has negative expectancy.
- Frequent failures include no strictly ITM contract with an observed bar at the trigger minute, missing exact next-minute option bar, and entry minute outside the calendar-day window. Do not relax these gates or impute prices to force trades. Next action is a bounded data timestamp/contract-coverage audit, not another parameter search.
