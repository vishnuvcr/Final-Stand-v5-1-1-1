# Strategy Specification

## Legs
At 10:00 IST, identify the nearest ATM strike A.

Put side: buy 1 sixth-OTM put below A; sell 1 seventh-OTM put; sell 1 eighth-OTM put.

Call side: buy 1 sixth-OTM call above A; sell 1 seventh-OTM call; sell 1 eighth-OTM call.

## Entry selector
P_put = PE7 + PE8 - PE6.
P_call = CE7 + CE8 - CE6.
Trade the side with the larger P; ties go to puts.

## Expiry payoff
Put payoff = max(K6-S,0) - max(K7-S,0) - max(K8-S,0) + (P_put).
Call payoff = max(S-K6,0) - max(S-K7,0) - max(S-K8,0) + (P_call).

The actual flatline, bump/peak, and breakevens are calculated from the selected strikes and premium rather than assumed from a textbook ratio spread.
