# Phase 107 Research Log

## 2026-10-12 — Step 107.0 registration
- User instruction: “Ok proceed with next strategies”.
- Checked the Phase 106 plan, status, logs, workflow and completed result publication before opening this branch.
- Registered three new fixed regime-filtered candidates alongside three Phase 106 baselines: large-move momentum, small-move reversal and large-move reversal, using a fixed 0.5% absolute one-session return threshold.
- Reused sample explicitly designated exploratory only; no in-sample winner selection or promotion.

## 2026-10-12 — Steps 107.1–107.4 complete
- Automated workflow [38167042024](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38167042024) succeeded. Regression/boundary tests, source gate, replay and publication passed.
- Parsed 21 official NSE daily archives: 17,791 selected/parsed rows, 100% identity/OHLC completeness, zero duplicate keys, date mismatches or invalid positive-volume OHLC rows.
- Completed proxy trades: MOMENTUM_ATM 95; REVERSAL_ATM 95; MOMENTUM_OI_CONFIRM 65; LARGE_MOVE_MOMENTUM 67; SMALL_MOVE_REVERSAL 28; LARGE_MOVE_REVERSAL 67.
- Primary cost case (₹20/order, ₹0.25/unit/side slippage, 1.0× modeled fees) net P&L: -₹57,392.82; -₹51,308.17; -₹10,630.92; -₹45,941.08; -₹29,635.78; -₹21,672.39, respectively.
- Strict stress (₹20/order, ₹0.50/unit/side slippage, 1.5× fees) net P&L: -₹89,420.31; -₹83,420.84; -₹32,582.46; -₹68,139.82; -₹39,401.55; -₹44,019.29, respectively.
- All 144 scenario accounting checks passed. No candidate promoted. The small-move reversal bootstrap interval did not cross zero in this reused sample, but this is exploratory and does not overcome multiple-comparison/selection bias or execution-proxy limitations.
- Aggregate-only results are in `results/phase107/`; raw market rows and per-trade prices are not published.
