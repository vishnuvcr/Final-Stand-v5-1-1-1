# Phase 106 Status — Forward EOD Replication

**Updated:** 2026-10-11  
**Branch:** `phase-106-forward-eod-replication`  
**Workflow:** [38132092115 — success](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38132092115)  
**State:** COMPLETE — FORWARD-CALENDAR OHLC PROXY REPLICATION; NO STRATEGY PROMOTED  
**Unit tests:** passed  
**Source gate:** PASS  
**Accounting gate:** PASS — 72/72 scenario rows  
**Promotion:** NONE

## Source coverage
- Window: 2026-09-02 inclusive to 2026-10-02 exclusive.
- Official NSE archives parsed: 21; selected/parsed rows: 17,791 / 17,791.
- Identity and OHLC completeness: 100% / 100%.
- Duplicate daily keys, date mismatches and invalid positive-volume OHLC rows: zero.
- Missing volume/OI/underlying/lot size: 0 / 0 / 0 / 0.
- Positive-volume rows: 11,928; zero-volume rows: 5,863.
- Common sessions with all five underlyings: 21; 19 post-warm-up outcome sessions used for strategy P&L.

## Primary case
₹20 per order, ₹0.25 per-unit adverse slippage per side, 1.0× modeled fees.

| Strategy | Proxy trades | Net P&L | Return on premium | Max drawdown |
|---|---:|---:|---:|---:|
| MOMENTUM_ATM | 95 | -₹57,392.82 | -4.9831% | ₹93,318.30 |
| REVERSAL_ATM | 95 | -₹51,308.17 | -4.2106% | ₹87,274.01 |
| MOMENTUM_OI_CONFIRM | 65 | -₹10,630.92 | -1.2363% | ₹51,594.51 |

All three 95% daily-cluster bootstrap intervals cross zero. Under strict stress (₹20/order, ₹0.50 per-unit slippage per side, 1.5× modeled fees), net P&L was -₹89,420.31, -₹83,420.84 and -₹32,582.46, respectively.

## Bounded phase status
- [x] 106.0 Freeze later non-overlapping calendar window and unchanged Phase 105 rules.
- [x] 106.1 Official NSE source integrity gate.
- [x] 106.2 Regression and chronology tests.
- [x] 106.3 Frozen replay and all 72 cost scenarios.
- [x] 106.4 Aggregate report and decision published.

## Interpretation boundary
This is a later calendar sample, not proof of statistical independence. Daily OHLC bars and assumed slippage do not establish executable fills. No candidate is promoted. See `results/phase106/PHASE106_REPORT.md` for full methods and limitations.