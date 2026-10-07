# Phase 50B — TT-03 Replay Specification

## Status
Frozen source-faithful numerical replay contract. V3 is the current implementation after a hard-close completeness correction; V2 failed the feasibility gate and is non-evidence.

## Entry
- Historical Current Week Expiry dates are taken from the project expiry calendar.
- Entry date is exactly three calendar days before the expiry date.
- If that date is not a trading day / has no index observations, no trade is opened.
- Entry scan is 10:00:00 through 10:05:59 IST using observed timestamps.
- The earliest timestamp in the window with a complete source-defined ratio set is used.
- Must be flat.
- ATM is the nearest listed strike to point-in-time NIFTY spot.
- Bearish call ratio: buy CE ATM+300, sell CE ATM+350, sell CE ATM+400.
- Bullish put ratio: buy PE ATM-300, sell PE ATM-350, sell PE ATM-400.
- One historical NIFTY lot per leg.
- Source-set precedence is frozen as call-ratio first, with put-ratio fallback only when the call-ratio quote set is not complete at an earlier observation.

## Exit
- Only on the current-week expiry day.
- From 13:30 IST onward, evaluate source strategy P&L at observed timestamps where all live legs have simultaneous quotes.
- First observed negative gross mark-to-market P&L triggers exit.
- If no negative exit occurs, close no later than 15:29 IST using the latest valid observed timestamp at/within the source-defined hard-close window.
- No requirement for an exact 15:15 timestamp.
- No quote forward-fill or imputation.

## Delta / strike selection
The baseline itself does not use delta selection. The ATM and point-distance strikes are selected from contemporaneous listed quotes only.

## Execution model
- Historical NIFTY lot size per expiry.
- Adverse 0.05-point option slippage on every execution.
- Primary brokerage ₹10/order.
- Robustness brokerage ₹20/order.
- Date-aware statutory charges.
- +50% charge/friction stress.
- No look-ahead.

## Coverage
- Every opened candidate must become either a completed trade or an explicit coverage exclusion.
- Minimum complete coverage: 95%.
- Coverage gaps are retained separately and never imputed.
- data_errors.csv must be empty for evidence acceptance.
- Published summary must reconcile trades + coverage exclusions = candidate trades and carry net/net50/net20/net20_50.

## Chronology
- DEV: expiry through 2023-12-31.
- VAL: 2024-01-01 through 2025-12-31.
- HOLD: 2026-01-01 onward, protected from selection.

## VIX
VIX is an external attribution variable only. Baseline entry/exit is not VIX-conditioned. Entry-date VIX state is assigned after trade entry using the project's frozen historical VIX definitions.

## Finite future mutation
Only after baseline completion and only from the preregistered universe may the 300-point outer anchor be shifted outward while keeping the 50-point internal spacing and all other source rules unchanged. No holdout tuning.

## Determinism
- If more than one timestamp is valid, use the earliest valid observation.
- If ATM tie exists, use the smaller strike.
- Any source-required quote not observed simultaneously is treated as a feasibility gap, never synthesized.


## V3 correction — 2026-10-07
At the no-negative-P&L hard close, search backward from 15:29 for the latest observed timestamp at or before 15:29 where every live leg has a contemporaneous quote. A timestamp containing only a subset of the legs is not an exit candidate. No forward fill, interpolation or imputation is permitted.
