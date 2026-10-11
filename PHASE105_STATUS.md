# Phase 105 Status — EOD OHLC Strategy Pilot

**Updated:** 2026-10-11  
**Branch:** \`phase-105-eod-ohlc-strategy-pilot\`  
**Latest workflow:** [38131616138 — success](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38131616138)  
**State:** COMPLETE — EXPLORATORY OHLC PROXY PILOT; NO STRATEGY PROMOTED  
**Unit tests:** 8/8 passed  
**Source gate:** PASS  
**Accounting gate:** PASS — 72/72 prespecified scenario rows  
**Promotion:** NONE

## Frozen scope and results

- Universe: HDFCBANK, ICICIBANK, INFY, RELIANCE and SBIN.
- Sample: 2026-08-03 inclusive to 2026-09-02 exclusive; 22 official NSE daily archive sessions.
- Selected / parsed rows: 18,082 / 18,082; identity and OHLC completeness 100%.
- Duplicate daily contract keys and date mismatches: zero; zero invalid positive-volume OHLC rows.
- Three fixed candidates: MOMENTUM_ATM, REVERSAL_ATM and MOMENTUM_OI_CONFIRM.
- Entry proxy is next-session open and exit proxy the same session's close; signals and contract selection use only information available by the signal-session close.
- Brokerage sensitivity ₹10/₹15/₹20 per executed order; date-effective modelled statutory/exchange fees; adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side; fee multipliers 1.0×/1.5×.
- Raw source rows, price rows and trade-by-trade records are not published.

## Primary case and strict stress

Primary: ₹20/order, ₹0.25 per unit per side adverse slippage, 1.0× model fees.

| Strategy | Trades | Net P&L | Return on premium | Max drawdown (₹) | Mean-day 95% cluster bootstrap CI |
|---|---:|---:|---:|---:|---|
| MOMENTUM_ATM | 79 | -₹117,882.02 | -12.1585% | ₹123,599.29 | -₹9,011.00 to -₹2,638.14 |
| REVERSAL_ATM | 79 | +₹15,018.02 | +1.4912% | ₹42,223.32 | -₹2,682.37 to +₹3,957.35 |
| MOMENTUM_OI_CONFIRM | 55 | -₹84,041.39 | -11.9918% | ₹85,292.63 | -₹6,706.59 to -₹1,703.86 |

Strict stress: ₹20/order, ₹0.50 adverse slippage per unit per side, 1.5× model fees. Net P&L: MOMENTUM_ATM -₹144,436.93; REVERSAL_ATM -₹11,709.36; MOMENTUM_OI_CONFIRM -₹102,999.67.

The reversal candidate is not robust: its primary-case bootstrap interval crosses zero and its median trade is negative; net P&L turns negative under strict stress. Positive numbers under milder assumptions are not evidence of an executable edge.

## Bounded phase status

- [x] 105.0 Registration and scope freeze.
- [x] 105.1 Source/schema/identity/OHLC integrity gate.
- [x] 105.2 Unit tests and selector/accounting regression checks.
- [x] 105.3 Frozen replay and registered brokerage/slippage/fee sensitivity (72 rows).
- [x] 105.4 Accounting review, report, machine-readable aggregates, CSV and figure published.

## Decision and limitation

This was one previously inspected month with 20 post-warm-up outcome sessions. Daily OHLC open/close marks and assumed slippage do not establish bid/ask execution, spread, depth, queue, latency, partial fills or impact. Account-specific Paytm Money brokerage is not verified. No strategy is promoted. Further work requires a new registered phase with an independently frozen, longer sample and an execution model validated against authorized quotes/trades or a validated conservative proxy.
