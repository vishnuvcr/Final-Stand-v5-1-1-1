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

## 2026-10-07 account-template validation reconciliation

The current saved template is Tradetron strategy 999088026. Its deterministic summary confirms:
- non-expiry entry 10:00–10:05, sell one ATM CE + one ATM PE of current week;
- expiry-day entry 10:00–10:05, sell one ATM CE + one ATM PE of the next weekly expiry;
- each side has one premium-match repair at a 100-point premium differential;
- universal exit is P&L <= -₹7,000 or time >=15:15;
- execution setting is market price and continuous evaluation.

Tradetron's current validator also emits important warnings. They are source warnings, not silently corrected strategy rules:
1. Find Strike with premium matching and results 'any' has no distance cap; it chooses the nearest premium match at any strike distance.
2. A fixed -₹7,000 P&L threshold is multiplier-sensitive.
3. The repair structure sits inside a re-enterable set and the validator warns that repair-driven re-entry can compound duplicate entries.

Phase-50B common replay will preserve the source's observed rule semantics rather than silently replace these warnings. Any safer mutation would be a separate preregistered variant, not the baseline.


## 2026-10-07 V3 source-fidelity lock
- Exact premium match means an exact contemporaneous observed LTP match; nearest-premium substitution is not permitted.
- The universal time exit is evaluated at the earliest observed timestamp at or after 15:15 for which all live legs have simultaneous quotes; a missing first observation is not by itself a coverage failure.
- These corrections are frozen in engine revision 50B-TT04-COVERAGE-V3 before numerical execution.
