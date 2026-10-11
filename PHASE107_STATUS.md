# Phase 107 Status — Regime-Filtered EOD Candidates

**Updated:** 2026-10-12  
**Branch:** `phase-107-regime-filtered-eod-strategies`  
**Workflow:** [38167042024 — success](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38167042024)  
**State:** COMPLETE — EXPLORATORY SCREEN; NO STRATEGY PROMOTED  
**Regression tests:** PASS  
**Source gate:** PASS  
**Accounting:** PASS — 144/144 scenarios  
**Promotion:** NONE

## Source coverage
- Window: 2026-09-02 inclusive to 2026-10-02 exclusive.
- Official NSE daily archives parsed: 21; selected/parsed rows: 17,791 / 17,791.
- Identity/OHLC completeness: 100% / 100%.
- Duplicate daily keys, date mismatches and invalid positive-volume OHLC rows: zero.
- Missing volume/OI/underlying/lot size: zero.
- Common sessions across five underlyings: 21; post-warm-up outcome sessions: 19.

## Primary case
₹20 brokerage per order, ₹0.25 adverse slippage per option unit per side, 1.0× modeled fees.

| Candidate | Proxy trades | Net P&L | Return on premium | Max drawdown |
|---|---:|---:|---:|---:|
| MOMENTUM_ATM | 95 | -₹57,392.82 | -4.9831% | ₹93,318.30 |
| REVERSAL_ATM | 95 | -₹51,308.17 | -4.2106% | ₹87,274.01 |
| MOMENTUM_OI_CONFIRM | 65 | -₹10,630.92 | -1.2363% | ₹51,594.51 |
| LARGE_MOVE_MOMENTUM | 67 | -₹45,941.08 | -6.0254% | ₹76,429.24 |
| SMALL_MOVE_REVERSAL | 28 | -₹29,635.78 | -8.4436% | ₹34,237.13 |
| LARGE_MOVE_REVERSAL | 67 | -₹21,672.39 | -2.4981% | ₹57,030.77 |

All six were negative in the primary cost case. The small-move reversal descriptive session-bootstrap interval was also below zero, but this cannot validate an edge: the sample is reused, short, and selected among multiple candidates. All six were negative under strict stress (₹20/order, ₹0.50/unit/side slippage, 1.5× modeled fees); net P&L was -₹89,420.31, -₹83,420.84, -₹32,582.46, -₹68,139.82, -₹39,401.55 and -₹44,019.29 in the table order above.

## Phase checklist
- [x] 107.0 Register rules, sample, costs and no-promotion rule.
- [x] 107.1 Regression and threshold-boundary tests.
- [x] 107.2 Source integrity and chronology gate.
- [x] 107.3 Six-candidate replay and all 144 cost scenarios.
- [x] 107.4 Aggregate outputs and report published.

## Interpretation boundary
This is exploratory screening on the already-inspected Phase 106 window, not independent confirmation. Daily OHLC and assumed slippage do not verify executable fills. No strategy is promoted.
