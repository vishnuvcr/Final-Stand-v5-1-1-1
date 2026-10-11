# Phase 107 Research Plan — Regime-Filtered EOD Option Candidates

**Branch:** `phase-107-regime-filtered-eod-strategies`  
**Registration date:** 2026-10-12  
**Status:** Registered exploratory screening; no strategy promotion.

## Research question
Do simple, preregistered one-session return-regime filters change the after-cost outcomes of long-option directional rules in the already-used Phase 106 daily EOD OHLC proxy sample?

## Candidate rules
- `MOMENTUM_ATM`: baseline direction follows the prior underlying session return.
- `REVERSAL_ATM`: baseline direction opposes the prior underlying session return.
- `MOMENTUM_OI_CONFIRM`: baseline momentum plus the existing near-ATM same-side OI-increase filter.
- `LARGE_MOVE_MOMENTUM`: momentum only when absolute prior-session underlying return is at least 0.5%.
- `SMALL_MOVE_REVERSAL`: reversal only when absolute prior-session underlying return is below 0.5%.
- `LARGE_MOVE_REVERSAL`: reversal only when absolute prior-session underlying return is at least 0.5%.

The 0.5% threshold is fixed before this run; it is not tuned. Baselines are included for comparison. This sample was already inspected in Phase 106, so these are discovery/screening results only and cannot be treated as independent confirmation.

## Fixed data and costs
- Same five stocks and official NSE daily UDiFF F&O archive parser as Phase 106.
- Same window: 2026-09-02 inclusive to 2026-10-02 exclusive. No window extension or source substitution.
- Same expiry/strike selector and next-session open to same-session close OHLC proxy.
- Cost grid: brokerage ₹10/₹15/₹20 per order × slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side × modeled fee multipliers 1.0×/1.5×.
- 6 candidates × 24 cost scenarios = 144 rows. Paytm Money brokerage remains a sensitivity, not a verified account-specific fee schedule.

## Steps and gates
1. 107.0 Freeze rules, sample, thresholds, cost grid and no-promotion rule.
2. 107.1 Run regression tests including exact threshold boundary checks.
3. 107.2 Validate source integrity and chronology using the Phase 106 gates.
4. 107.3 Replay all six fixed rules and all 144 cost scenarios.
5. 107.4 Publish aggregate-only CSV/JSON, SVG, report, decision, status, research log, error log, visible chat log and update README.
6. Stop after 107.4. Do not tune thresholds or promote winners. Any candidate worth further study needs a newly frozen, genuinely later holdout and a better validated execution model.

## Statistical analysis
Report net/gross P&L, fees, assumed slippage, return on premium deployed, win rate, mean/median trade, profit factor, drawdown, coverage and exclusions; deterministic session-cluster bootstrap intervals are descriptive. Because this is a reused sample and multiple candidate rules are compared, no p-value or in-sample winner is interpreted as confirmatory evidence.

## Limitations and safety gates
Daily OHLC does not verify bid/ask, depth, latency, partial fills, market impact or actual fills. No strategy can be promoted based on this study. Do not publish raw contract rows or per-trade prices. A source/accounting failure blocks interpretation.
