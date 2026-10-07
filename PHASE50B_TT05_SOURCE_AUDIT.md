# Phase 50B — TT-05 Source Audit

## Strategy
Simple Intraday Short Straddle.

## Entry
- Non-Thursday standard days: 09:30 through 15:10, maximum one trade per day while flat.
- Thursday expiry-day set: same time window, but sell the next weekly expiry rather than the expiring weekly options.
- One lot ATM CE + one lot ATM PE sold.
- Runtime `trades_today` increments on entry.

## Exit
- Universal exit at/after 15:15 IST or strategy P&L <= -₹3,000.

## VIX role
This strategy has no source VIX input. Any VIX conditioning in Phase 50B is an external overlay evaluated only after source-faithful baseline replay and is not part of the native strategy.

## Evidence
Native Tradetron result is provenance only; common replay applies project-standard brokerage, statutory charges and adverse slippage.