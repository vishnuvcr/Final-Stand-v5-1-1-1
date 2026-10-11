# Phase 106 Research Log

## 2026-10-11 — Step 106.0 registration
- User instruction: “Ok proceed” after Phase 105 closeout.
- Checked Phase 105 plan, status, methodology and workflow before creating a separate branch.
- Froze a later non-overlapping calendar window: 2026-09-02 inclusive to 2026-10-02 exclusive, with the same five stocks, selector, three candidate rules and 72-scenario cost grid.

## 2026-10-11 — Steps 106.1–106.4 complete
- Automated workflow [38132092115](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38132092115) completed successfully; regression tests, source gate and accounting checks passed.
- 21 official NSE daily archives parsed; 17,791/17,791 selected rows; identity/OHLC completeness 100%; zero duplicate daily contract keys, date mismatches or invalid positive-volume OHLC rows.
- Completed OHLC proxy trades: MOMENTUM_ATM 95, REVERSAL_ATM 95, MOMENTUM_OI_CONFIRM 65; the OI filter rejected 30 signals.
- Primary case (₹20/order, ₹0.25/unit/side, 1.0× modeled fees): net P&L -₹57,392.82, -₹51,308.17 and -₹10,630.92, respectively.
- Strict stress (₹20/order, ₹0.50/unit/side, 1.5× fees): net P&L -₹89,420.31, -₹83,420.84 and -₹32,582.46.
- All 72 cost scenarios reconciled; no strategy promoted. These are OHLC proxies, not verified fills.
- Phase 105 is unchanged. Full Phase 106 report and scenario table are stored under `results/phase106/`.