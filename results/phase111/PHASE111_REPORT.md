# Phase 111 — ZigZag weekly options report

Generated UTC: 2026-10-23T22:50:21.850067+00:00

Status: **EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION**. Strategy promotion: **NONE**.

## Data coverage
- Dataset revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Observed expiry files: 267, from 2021-05-27 through 2026-08-04.
- Campaigns scheduled: 259; exact-path eligible: 142; excluded: 121.
- Complete daily index candles: 1250; incomplete sessions excluded: 8.
- Eligible campaign counts by split: {"development": 96, "validation": 45, "holdout": 1}.
- Exclusions: {"INCOMPLETE_OPTION_PATH": 50, "INCOMPLETE_SPOT_PATH": 1, "INVALID_SESSION_GRID": 1, "MISSING_INVALID_OR_DUPLICATE_ENTRY_BAR": 17, "NO_CONFIRMED_PIVOT_SIGNAL": 22, "NO_NEXT_OBSERVED_SESSION": 4, "NO_VALID_ABS_0_10_DELTA_CONTRACT": 22, "PREVIOUS_EXPIRY_DAILY_CANDLE_INCOMPLETE": 2, "UNSUPPORTED_HISTORICAL_LOT_SIZE_DATE": 2}.

## Locked strategy
Last confirmed daily HL/LL means sell a put; HH/LH means sell a call. Option target is absolute model delta 0.10 using the exact 09:59 completed bar; sell at the exact 10:00 open on the first observed session after the previous expiry. Scheduled exit is the exact 10:00 open on target weekly expiry. A completed one-minute observation with absolute model delta >= 0.50 exits at the next exact market minute's open.

## Cost model
24 scenarios: brokerage ₹10/₹15/₹20 per order; adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit on entry and exit; modeled fee multipliers 1.0×/1.5×. One-lot historical quantity and date-aware STT, exchange/IPFT, SEBI, stamp duty and GST are included. Account-specific Paytm Money contract-note charges are not verified. OHLC opens are simulation proxies, not proven executions.

## Indicator limitation
The supplied Pine script imports external DevLucem/ZigLib/1; the library code body was not included in the user submission. The engine's causal MT4-style proxy is not verified as byte-identical to the TradingView library. Do not treat this as a definitive test of the exact plotted indicator until confirmed-label parity is demonstrated.

## Result interpretation
Cost rows are in cost_grid.csv; event-level summary outcomes (without raw minute prices) are in campaign_ledger.csv; exclusion counts/reasons are in campaign_exclusions.csv. Null statistics from empty samples indicate unestimable performance, not a zero-return result. The no-stop benchmark uses the same signal, strike and entry, with a scheduled expiry-day 10:00 exit.

No strategy is promoted. If the sample is small, coverage is selective, or the signal implementation does not match TradingView, any apparent edge is provisional.
