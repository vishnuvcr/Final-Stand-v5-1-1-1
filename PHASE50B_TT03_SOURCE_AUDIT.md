# Phase 50B — TT-03 Source Audit

## Strategy
Corrected Dynamic-n NIFTY Weekly Options Strategy.

## Exact Tradetron entry rule
- 3-day difference between today and Current Week Expiry.
- Entry window: 10:00 to 10:05 IST.
- Must be flat.
- Two symmetric sets may compete:
  - Bearish call ratio: buy current-week CE at ATM + 300 points; sell one CE at ATM + 350; sell one CE at ATM + 400.
  - Bullish put ratio: buy current-week PE at ATM - 300 points; sell one PE at ATM - 350; sell one PE at ATM - 400.
- One historical NIFTY lot per leg.

## Exit
- On current-week expiry day, from 13:30 onward, exit if strategy P&L < 0.
- Otherwise exit no later than 15:29.
- Native Tradetron fills settle at 15:30 in the existing report.

## State
The embedded Python only tracks MFE when runtime state equals 2; it does not alter the visible entry/exit rules. The source-faithful replay therefore does not add an MFE-based discretionary exit.

## Native backtest provenance
- job: ttbt-999071838261005
- public report: https://tradetron.tech/bt/view/0bc9dbe746525bfffdafb58ed7e4b405
- headline native net P&L: ₹104,274.20
- native headline trade count: 558
- profit factor: 1.185
- fill ledger: 1,116 fills, 558 buys and 558 sells
- first fill: 2021-10-04 10:00
- last fill: 2026-04-13 15:30

The headline 558 count is not equivalent to 558 complete three-leg trades. Scientific inference will use complete trade units from the fill ledger.

## Expiry-calendar audit
Native ledger examples:
- 2021-10-04 entry → 2021-10-07 expiry.
- 2024-08-19 entry → 2024-08-22 expiry.
- 2025-05-19 entry → 2025-05-22 expiry.
- 2025-10-17 entry → 2025-10-20 expiry.
- 2026-02-27 entry → 2026-03-02 expiry.

This indicates the three-day condition is tied to the actual historical expiry calendar. The common replay will use the exact listed historical expiry dates rather than hard-coding Thursday or Tuesday.

## Costs
Native Tradetron P&L remains provenance only. Common replay will use historical NIFTY lot size, ₹10/order brokerage, statutory/exchange charges, adverse slippage and +50% cost stress.

## Allowed Phase-50B mutation
A finite source-semantic tail-distance study may shift the 300/350/400-point anchor outward while preserving the 50-point spacing, three-day expiry-relative rule, entry timing and exit rule. Selection remains development-only before validation and holdout.

## V2 feasibility result and V3 correction — 2026-10-07
The V2 replay completed 187/202 candidate campaigns (92.57%) and therefore failed the preregistered 95% feasibility threshold; its P&L is not evidence. Self-audit identified a hard-close completeness defect whereby a latest timestamp with some-but-not-all leg quotes could create a false coverage gap. V3 searches backward for the latest complete all-live-leg quote at or before 15:29. V3 is now the active source-faithful implementation.
