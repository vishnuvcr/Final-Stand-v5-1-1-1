# Phase 108 Status — Volatility-Regime Candidates

**State: COMPLETE AS EXPLORATORY SCREEN; NO STRATEGY PROMOTED**
**Branch:** phase-108-volatility-and-market-regime-rules
**Workflow:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38167282757
**Report:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-108-volatility-and-market-regime-rules/results/phase108/PHASE108_REPORT.md

- [x] 108.0 Register rules and cost assumptions.
- [x] 108.1 Tests.
- [x] 108.2 Source gate.
- [x] 108.3 Replay and accounting.
- [x] 108.4 Publish outputs and report.

The workflow passed all steps. 21 official NSE archives and 17,791 selected/parsed rows; 100% identity/OHLC completeness; zero duplicate keys, date mismatches, or invalid positive-volume OHLC rows. Ten strategy families × 24 cost scenarios = 240 rows; accounting PASS.

Primary case (₹20/order, ₹0.25/unit/side slippage, 1× modeled fees): MOMENTUM_ATM -₹57,392.82; REVERSAL_ATM -₹51,308.17; MOMENTUM_OI_CONFIRM -₹10,630.92; LARGE_MOVE_MOMENTUM -₹45,941.08; SMALL_MOVE_REVERSAL -₹29,635.78; LARGE_MOVE_REVERSAL -₹21,672.39; LOW_VOL_MOMENTUM -₹23,935.51; HIGH_VOL_MOMENTUM -₹22,037.97; LOW_VOL_REVERSAL -₹32,571.87; HIGH_VOL_REVERSAL -₹23,172.15.

All ten are negative under strict stress (₹20/order, ₹0.50/unit/side, 1.5× modeled fees). Sample reused from Phase 106/107; not an independent holdout. OHLC and assumed slippage do not establish executable fills; Paytm Money account-specific fees remain unverified. No promotion.
