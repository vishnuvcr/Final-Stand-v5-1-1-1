# Phase 36 Strategy Specification — Independent Direction Overlay

Phase 36 is the Continuous Delta 6x6 Vertical Spread with one deliberate modification:

The direction of each new trade is chosen independently by the registered selector at that entry. Previous trade P&L does not determine the next direction.

## Entry
- NIFTY 50 current weekly expiry.
- Earliest new entry 09:20 IST.
- No new entry on expiry day.
- No new action at or after 15:28 IST.
- No position may be open when a new entry is created.

## Position
CALL: sell 6 lots of the current-week CE nearest +0.25 delta and buy 6 lots of the same expiry CE at short strike +50.
PUT: sell 6 lots of the current-week PE nearest −0.25 delta and buy 6 lots at short strike −50.

## Exit
CALL: first complete observation with short CE delta >= +0.50 or <= +0.04.
PUT: first complete observation with short PE delta <= −0.50 or >= −0.04.
If no delta exit occurs, close at contract termination under the same Phase-32 reproducible historical convention.

## Direction independence
After exit:
- do not inspect net P&L to choose the next side;
- do not retain the previous side because the trade won;
- do not flip because the trade lost.

The next eligible entry performs a new selector decision.

## Selectors
OTM678_FRESH and OTM789_FRESH are recomputed at the entry snapshot.
CATBOOST, DART, WAVELET_TREE, OOF_STACK and MARKOV_REGIME_TREE use their cached Phase-35 forecast for the corresponding expiry.

## Costs
Use the identical Phase-32 cost model: ₹0.05 adverse option slippage per leg, date-aware lot size, ₹10 brokerage per executed F&O order, audited statutory/exchange charges and GST, and no synthetic prices/fills.

## Control
Phase-32's published stateful direction logic remains the comparator and is not part of the treatment.
