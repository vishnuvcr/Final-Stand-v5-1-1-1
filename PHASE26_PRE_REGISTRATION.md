# Phase 26 — Direct OTM7/8/9 (789) Structure Test

## Research question
Did the fixed structure **buy OTM7 / sell OTM8 / sell OTM9** materially avoid historical losses relative to the locked dynamic-n strategy, and were any apparent avoided losses offset by profitable trades sacrificed?

## Scope
Only the construction parameter changes: fixed n=7, so the three legs are OTM7/8/9. Stage-1 direction remains the locked OTM6/7/8 chooser. Entry remains 10:00 IST at 4 trading sessions before expiry. Target is 90% of the structure's own entry-time payoff expression. Execution costs remain the canonical model: one adverse ₹0.05 option tick per leg, six orders, Paytm Money brokerage assumption of ₹10/order, date-aware statutory/transaction charges and historical lot sizes.

The first diagnostic uses the corrected minute-level engine's standard target/expiry fallback. It is explicitly a structure test, not a new direction chooser. The Phase-20 expiry-day stop is not silently substituted into this first direct reconstruction; if the loss comparison is materially informative, a separate registered follow-up can test the final exit stack on the same fixed structure.

## Comparators
- Locked dynamic-n corrected trade ledger.
- Fixed n=7 / OTM7-8-9 on the same executable universe and Stage-1 direction.

## Primary endpoints
1. Number of net losing trades.
2. Number of baseline losses avoided by fixed n=7.
3. Number of baseline winners converted to losses.
4. Net P&L difference.
5. Maximum drawdown.
6. Trade-level identities of all changed outcomes.

No post-hoc threshold or trade selection is permitted.
