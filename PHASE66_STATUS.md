# Phase 66 Status — OHLC-Based Paper Replication

**State: COMPLETE — numerical workflow passed; outcome is NO-GO / INSUFFICIENT EVIDENCE. No strategy promotion.**

- Branch: `phase-66-ohcl-paper-replication`
- Successful workflow: [run 38028140800](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38028140800).
- Source paper: Shaha (2019), CCI-based NIFTY monthly long-option rule. This is an independent modern-sample rule test, not a direct replication of the original October 2008–September 2018 period.
- Dataset: `thetrademarkk/india-index-options-1m`, pinned revision `3eacf762d401efd9a08e804592fa7882b354c4a2`, CC-BY-NC-4.0; no raw market data published.
- Data evaluated: 56 monthly-expiry proxy files, 436,424 underlying minute rows; latest underlying timestamp used 2025-12-31 15:59 IST. Zero 2026 option files were downloaded.
- Candidate results:
  - CCI_BASE: DEV 12 breakout triggers / 0 trades; VAL 13 breakout triggers / 0 trades.
  - CCI_EMA_FILTER: DEV 4 breakout triggers / 0 trades; VAL 1 breakout trigger / 0 trades.
  - Entry/exit coverage: 0% for all four candidate/split rows.
- Because there are zero completed trades, win rate, expectancy, profit factor, drawdown, mean/median trade P&L, and statistical evidence are NOT ESTIMABLE. Printed ₹0.00 aggregate P&L values are empty-sample placeholders, not observed zero-return performance.
- Main trigger blockers in CCI_BASE: 14 events had no strictly ITM contract observed on trigger minute; 9 failed next-minute entry/window requirements; 2 lacked the exact next-minute option bar. The remaining monthly rows had no qualified CCI signal or no later breakout. For CCI_EMA_FILTER, 1 trigger had no strictly ITM contract, 3 failed next-minute entry/window requirements, and 1 lacked the exact next-minute option bar; most rows had no qualified signal.
- Costs preserved: adverse ₹0.05 per-fill tick model, date-aware charges, ₹10 and ₹20/order brokerage cases, +50% fee/charge stress, and separate 10% adverse price-slippage sensitivity. The cost cases cannot determine profitability when there are no completed trades.
- No same-bar or interpolated fill, no relaxation of rules, and no 2026 holdout use.
- Decision: `RESEARCH_ONLY_NO_PROMOTION`. The test did not reproduce the original paper's headline figures and does not show CCI is profitable or unprofitable. It shows the available data and frozen causal entry protocol do not produce completed trades.
- Report: [PHASE66_REPORT.md](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-66-ohcl-paper-replication/results/phase66_paper_strategy_tests/PHASE66_REPORT.md).
- Machine-readable decision: [decision.json](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-66-ohcl-paper-replication/results/phase66_paper_strategy_tests/decision.json).
- Opportunity audit: [opportunity_audit.csv](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-66-ohcl-paper-replication/results/phase66_paper_strategy_tests/opportunity_audit.csv).
- Source manifest: [source_manifest.json](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-66-ohcl-paper-replication/results/phase66_paper_strategy_tests/source_manifest.json).

## Reproduction classification
**PARTIAL RULE RECONSTRUCTION; NUMERICAL REPRODUCTION BLOCKED.** The published rule was tested on a modern OHLC sample under explicit costs, but original-period data and completed trades are unavailable. A faithful numerical comparison to the reported 68 trades, ₹145,362 net profit, 63.25% win rate, and 232.16% average annual ROI cannot be made.
