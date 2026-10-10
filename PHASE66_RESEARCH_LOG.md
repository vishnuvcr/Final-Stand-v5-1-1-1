# Phase 66 Research Log

## 2026-10-10 — Phase initiated
- User explicitly authorized proceeding with OHLC bars.
- Created a dedicated branch and froze the scope around the CCI paper's rules plus the already-frozen EMA-filter adaptation.
- Inherited prior Phase 64 result: zero completed trades, so profitability metrics were not estimable.
- Inherited Phase 65 diagnostic: 30 events, with blockers of 15 no strictly ITM contract observed at trigger, 12 next-minute entry missing/outside window, and 3 missing exact next-minute option bars.
- Decision: do not relax causal entry rules or infer fills from absent bars. Reproduce what the data supports and explicitly label the outcome partial/blocked if coverage is insufficient.

## 2026-10-10 — Successful numerical execution
- Workflow run [38028140800](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38028140800) completed successfully. Dependency install, syntax/unit-test gate, frozen DEV/VAL numerical run, report/figure generation, output validation, completion marker, aggregate publication, and artifact upload passed.
- Pinned revision: `3eacf762d401efd9a08e804592fa7882b354c4a2`; 56 monthly-expiry proxy files loaded; 436,424 underlying minute rows; 2026 option files downloaded = 0.
- CCI_BASE: 12 DEV and 13 VAL breakouts, zero completed trades in each split.
- CCI_EMA_FILTER: 4 DEV and 1 VAL breakouts, zero completed trades in each split.
- Entry/exit coverage = 0% for all four rows. No win rate, expectancy, profit factor, drawdown, or inference is estimable.
- Coverage categories for CCI_BASE over all expiry-file rows: 14 no-qualified-signal, 17 signal-without-later-breakout, 14 no strictly ITM strike observed on trigger, 9 next-minute entry/window failures, 2 missing exact next-minute option bars.
- Coverage categories for CCI_EMA_FILTER over all expiry-file rows: 49 no-qualified-signal, 2 signal-without-later-breakout, 1 no strictly ITM strike observed on trigger, 3 next-minute entry/window failures, 1 missing exact next-minute option bar.
- Net P&L fields display ₹0.00 because the aggregate sum over an empty ledger is zero; this is a reporting placeholder and is not evidence of zero return. The report now explicitly states that all performance metrics are not estimable.
- Decision: `RESEARCH_ONLY_NO_PROMOTION`. The result does not reproduce the original paper's historical P&L; source years 2008–2018 are not covered. This is a modern-sample OHLC rule test, partial rule reconstruction only.
- The report's machine-readable decision initially carried a stale phase number (64); corrected to Phase 66 and corrected in the generating runner. The report builder was also updated to make empty-sample interpretation explicit.

## Remediation record
- First workflow attempt [38028015865](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38028015865) failed because the copied runner imported `phase43_vix_strategy_sweep`, which was not present on the isolated branch. Copied the required helper module to `research/phase66_cost_helpers.py` and rewired the import.
- Corrected run passed all required gates. Follow-up metadata/reporting patches correct the phase identifier and state clearly that zero trade ledgers make performance metrics not estimable; they do not alter the numerical strategy rules or underlying result.
