# Strategy Specification

## Entry selector

At 10:00 IST on the selected 4-DTE trading date, identify the nearest ATM strike A.

For each n in 6..15, calculate:

- Put X(n) = PE(n+2) + PE(n+1) - PE(n)
- Call X(n) = CE(n+2) + CE(n+1) - CE(n)

Here OTMk means the kth strike outside ATM on that side.

Select the single maximum X across all 20 candidates. Ties are resolved deterministically in favor of Put, then smaller n.

## Position

If the winner is Put:
- Buy 1 OTMn Put
- Sell 1 OTM(n+1) Put
- Sell 1 OTM(n+2) Put

If the winner is Call:
- Buy 1 OTMn Call
- Sell 1 OTM(n+1) Call
- Sell 1 OTM(n+2) Call

## Credit and target

Initial credit per unit = winning X.

Initial credit for one lot = winning X × lot quantity.

Profit target = 0.90 × initial credit for one lot.

The primary backtest does not add a stop-loss.

## Exit

Exit all three legs when the position P&L reaches the 90% initial-credit target. Otherwise exit at 0 DTE/expiry using the historical execution convention defined in RESEARCH_PLAN.md.

## Accounting

Report gross P&L and net P&L separately. Net P&L includes slippage, brokerage, statutory charges, and applicable taxes/fees.
