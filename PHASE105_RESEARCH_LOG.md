# Phase 105 Research Log

## 2026-10-11 — Step 105.0: registration

- User instruction: “Continue” from the revised plan to proceed with available EOD data and clearly treat OHLC as a research execution proxy, not a verified fill.
- Re-read the main README and Phase 104's plan, terminal status, cost gate, error log, chat log and source/audit code before creating this phase.
- Phase 104 finding preserved: 18,082 selected rows across 22 official NSE archive dates; identity and OHLC completeness passed; no strategy P&L was run in Phase 104.
- Opened this isolated Phase 105 branch from Phase 104, rather than modifying Phase 104 evidence.
- Frozen five-stock universe, dates, three candidate rules, prior-information-only selector, next-session-open/same-session-close proxy, brokerage/fee/slippage grid, bootstrap, accounting gates and finite stop rules in `PHASE105_RESEARCH_PLAN.md`.

## 2026-10-11 — Steps 105.1–105.4: automated pilot complete

- GitHub Actions run [38131616138](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38131616138) completed successfully; all 8 unit tests passed.
- Official NSE archives: 22 parsed sessions, 18,082/18,082 selected/parsed records; identity/OHLC completeness 100%, zero duplicate daily keys/date mismatches/invalid positive-volume OHLC bars. Volume was positive for 12,160 records, zero for 5,922, missing for zero. Zero missing OI, underlying or lot-size fields.
- Exact-contract/target-session data gate: 79 proxy trades for MOMENTUM_ATM, 79 for REVERSAL_ATM and 55 for MOMENTUM_OI_CONFIRM. No selected contract lacked its exact next-session record; there were 20 signals per momentum/reversal candidate without a prior eligible contract and 24 OI-filter rejections for the OI-confirmed candidate. These are coverage counts, not verified live fills.
- Replayed the three frozen candidates over 72 scenario rows: 3 candidates × 3 brokerage assumptions × 4 per-unit adverse-slippage assumptions × 2 fee multipliers.
- Primary case (₹20/order, ₹0.25/unit/side, fee multiplier 1.0): MOMENTUM_ATM net -₹117,882.02, REVERSAL_ATM +₹15,018.02, MOMENTUM_OI_CONFIRM -₹84,041.39. Reversal's 95% day-cluster bootstrap interval for mean daily P&L crossed zero (-₹2,682.37 to +₹3,957.35), and its median trade was -₹798.60.
- Strict stress (₹20/order, ₹0.50/unit/side, 1.5× fees): MOMENTUM_ATM -₹144,436.93, REVERSAL_ATM -₹11,709.36, MOMENTUM_OI_CONFIRM -₹102,999.67.
- Accounting reconciliation passed; scenario trade counts do not vary with costs; all raw market rows and per-trade price records remained unpublished.
- Final decision: complete only as an exploratory OHLC execution-proxy pilot. No strategy promoted. The sample is one previously inspected month and cannot validate real-world execution or prove profitability.
- Published report, compact structured summary, 72-row scenario CSV, decision JSON, and aggregate cost-sensitivity SVG in `results/phase105/`. The automatic/manual-dispatch workflow is `.github/workflows/phase105-eod-ohlc-strategy-pilot.yml`.

## Future work boundary

No further parameter tuning inside Phase 105. Any independent replication or extension of the universe/date window must be a new preregistered phase, with independently frozen data, an authorized rights path, actual Paytm Money contract-note reconciliation, and quote/trade-validated or otherwise validated conservative execution assumptions.
