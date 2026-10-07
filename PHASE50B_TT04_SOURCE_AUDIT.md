# Phase 50B — TT-04 Source Audit

## Strategy
Profit Breakout Premium Match Straddle.

## Non-expiry days
- Entry: 10:00–10:05 IST, flat.
- Sell current-week ATM CE + ATM PE, one lot each.
- Not on current-week expiry day.
- Repair once on the CE when PE entry premium minus CE entry premium >= 100 points: buy back the original CE and sell a new current-week CE at a strike whose LTP matches the entry PE premium.
- Symmetric PE repair when CE entry premium minus PE entry premium >= 100 points: buy back the original PE and sell a new current-week PE at a strike whose LTP matches the entry CE premium.

## Expiry-day set
- Entry: 10:00–10:05 IST, flat, current-week expiry day.
- Sell one-lot ATM CE + ATM PE of the next weekly expiry.
- The same premium-matching repair logic uses the next-week expiry.

## Universal exit
- Exit when strategy P&L <= -₹7,000, or at/after 15:15 IST.

## Evidence and implementation caution
The repair target is a premium-matching strike selected from exact observed LTPs, not a delta or fixed strike-distance target. A source-faithful replay must therefore retain exact quote availability and cannot substitute missing strikes with a nearby strike.

Native report performance is provenance only. Common replay will use Final Stand costs, historical lot sizes, adverse option slippage and +50% cost stress.

## Phase-50B role
TT-04 is a control rather than the leading HIGH-VIX candidate. It should be replayed after TT-02/TT-03 source-faithful baselines and then evaluated for VIX conditioning without changing its premium-matching semantics.