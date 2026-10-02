# Dynamic-n Strategy Specification — Final Corrected Entry-to-Exit Rules

## Entry snapshot
- NIFTY weekly options.
- Four trading sessions before expiry.
- Exactly 10:00 IST.
- ATM = strike nearest NIFTY spot at 10:00.
- OTM-n = exact strike distance of n×₹50.
- No ordinal quote substitution and no forward filling.

## Direction
X_call_direction = CE8 + CE7 − CE6  
X_put_direction = PE8 + PE7 − PE6

- Call expression higher → BEARISH call-side trade.
- Put expression higher → BULLISH put-side trade.
- Equality → no trade.

## Dynamic candidate score
For each n=6,…,15:

X_n = P(OTM(n+2)) + P(OTM(n+1)) − P(OTM n)

All exact OTM6…17 prices on the selected side are required.

## Higher-n preference
threshold = 0.95×max(X_6…X_15)

Select the largest n with X_n >= threshold.

## Position
- Buy OTM-n.
- Sell OTM-(n+1).
- Sell OTM-(n+2).

## Target
Target = 0.90×X_selected×lot.

Exit at the first complete minute where slippage-adjusted combined gross P&L reaches target.

## Conditional expiry-day stop
At or after 13:30 IST on expiry day:
- current combined MTM must be negative;
- running combined MFE from entry must be below 0.50×original target.

Then exit all three legs.

## Expiry fallback
If still open, exit at the latest complete three-leg observation at or before 15:29 IST.

## No payoff-boundary stop
Crossing the entry-time expiry payoff green-area/zero-P&L boundary does not by itself trigger an exit before expiry day. Phase 20 rejected boundary-based stops after out-of-sample testing.

## Costs
- one adverse ₹0.05 tick per leg;
- six option orders;
- modeled ₹10/order brokerage;
- date-aware statutory/transaction charges;
- historical lot sizes;
- no imputation or synthetic fills.

## Exit precedence
Target → 13:30 conditional stop → 15:29 expiry fallback.
