# Phase 46 Status — VIX Strategy Discovery from YouTube

**STATUS: COMPLETE — EXPANDED DISCOVERY ONLY / NO NUMERICAL PROMOTION**

## Completed
- Created isolated branch `phase-46-vix-youtube-strategy-discovery`.
- Audited Phase-45 plan/status/research log/error log before starting.
- Performed a systematic indexed YouTube/web scan using multiple VIX/IV/NIFTY strategy query families.
- Registered 10 directly relevant video/public-source leads and 8 priority candidate families for possible numerical follow-up.
- Explicitly separated Indian/NIFTY sources from global transferable volatility sources.
- Excluded YouTube claims from the evidence hierarchy unless independently backtested.
- Identified the most promising unexplored high/rising-VIX research directions:
  **Put Ratio Backspread, Calendar Trap, Long Straddle/Strangle, Reverse Iron Condor/Long Iron Butterfly, and post-spike VIX-reversal short-volatility structures.**

## Key conclusion

The empty RISING/HIGH/SPIKE buckets should **not** be filled by simply selecting a generic high-VIX short-premium strategy. The source scan points to two distinct hypotheses that need separate testing:

1. **VIX expansion / continuation:** long-gamma or convex structures (backspreads, long straddles/strangles, reverse iron structures, calendar structures).
2. **VIX spike followed by reversal:** defined-risk short-volatility structures entered only after the spike begins to mean-revert.

The distinction is essential because the same HIGH VIX level can represent either an ongoing volatility expansion or a post-panic volatility peak.

## Numerical status

No Phase-46 numerical backtest has been run. No strategy is promoted or added to the canonical strategy.

## Next phase

A separate preregistered numerical phase should test a finite list of the top candidates using the existing NIFTY data/cost framework, preserving the untouched 2026 holdout.


## Scope expansion — Profit Breakout channel

The user-designated `@profitbreakout` channel has been incorporated as a dedicated source stream. Nine directly relevant indexed videos were added to the source ledger. Importantly, the channel's material spans both **LOW/NORMAL and HIGH/RISING** volatility contexts, so subsequent testing will evaluate its candidates across the full eight-state VIX panel rather than restricting them to the currently empty high-VIX states.

### New high-priority channel hypotheses
- India-VIX-conditioned strategy selection among Calendar, Iron Fly, Iron Condor, Straddle and Strangle.
- Batman/double-ratio with VIX filter.
- Iron Fly ↔ Iron Condor transition rule based on premium imbalance and structural change.
- Monthly strategy with VIX-based strike selection.
- Hedged weekly/monthly credit-spread combinations.
- Longer-duration covered-call/protective-put structures.

No strategy is promoted from these videos. The next numerical phase must reconstruct exact deterministic rules before testing.
