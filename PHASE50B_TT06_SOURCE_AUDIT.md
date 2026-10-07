# Phase 50B — TT-06 Source Audit

## Strategy
Intraday Asym Premium.

## Entry
- Monday excluded.
- 09:30 through 15:10 while flat and no prior trade that day.
- Sell current-week ATM CE.
- Sell next-week ATM PE.

## Repair
- If the current-week CE LTP falls to <= 50% of the next-week PE LTP, buy back the CE and sell a current-week CE whose LTP matches the next-week PE observed LTP.
- Symmetrically, if the next-week PE LTP falls to <= 50% of the current-week CE LTP, buy back the PE and sell a next-week PE whose LTP matches the current-week CE observed LTP.

## Exit
- Universal exit at/after 15:15 IST or strategy P&L <= -₹4,000.

## Reconciliation warning
TT-06 is likely the same lineage as Option-intraday-v1, whose independent repository study was closed with negative cost-adjusted performance. Therefore the native Tradetron positive result is specifically flagged for implementation/cost reconciliation and cannot be imported as confirmation.

## Evidence
Source-faithful replay must use exact observed LTPs and exact premium matching; missing strikes are not substituted.