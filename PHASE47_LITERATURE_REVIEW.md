# Phase 47 Literature / Video-Derived Strategy Review

## Profit Breakout

Profit Breakout's India-VIX video explicitly frames VIX as a context indicator and discusses Calendar Spread, Iron Fly, Iron Condor, Straddle and Strangle as different volatility-environment tools. Its Batman video explicitly mentions a VIX-based entry filter. Its Iron Fly versus Iron Condor video compares the structures across high/low volatility. Its Covered Call 2.0 describes a long future, ~0.30-delta protective put, current-week ~0.30-delta call sale and next-week ~0.30-delta call sale. Its longer-duration income video combines a long-term NIFTY options position with weekly/monthly call selling.

The Phase-47 reconstruction deliberately avoids copying unsupported performance claims. It tests only structures whose mechanics can be represented from the cached NIFTY option data or are explicitly labelled as proxies.

## Additional source evidence

The indexed Profit Breakout monthly wide-range strategy transcript describes a current-month 30-delta short call/put pair plus next-month ATM call/put hedge, with rule-based adjustments and an explicit warning that very high VIX can make the strategy risky. A secondary indexed backtest source independently reconstructs this as a wide-range, next-month-hedged monthly short-premium structure and highlights its short-premium tail shape.

These sources motivate S2 but do not establish profitability.

## Methodological caution

Video sources are hypothesis-generation evidence, not independent validation. The project continues to require point-in-time reconstruction, realistic costs, validation-only freezing, protected holdout confirmation and multiple-testing correction.