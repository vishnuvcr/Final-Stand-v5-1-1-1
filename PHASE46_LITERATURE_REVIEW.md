# Phase 46 Literature / Source Review

The source scan reinforces several distinct mechanisms that can be tested independently:

- High implied volatility can make short-vega structures attractive **only if volatility subsequently falls**; this is different from trading into an ongoing VIX expansion. (YT-001, YT-002, YT-004)
- Put ratio backspreads are explicitly used for sharp downside movement and therefore provide a structurally different candidate for rising/high VIX regimes. (YT-005)
- Calendar structures provide exposure to differences in volatility/time decay across expiries rather than requiring a simple directional prediction. (YT-002, YT-006)
- Volatility skew may contain information beyond the level of India VIX and can be used to select between asymmetric downside/upside structures. (YT-008)
- VIX term structure is a distinct state variable from the spot VIX level; a robust India analogue should be established before using it. (YT-010)

These are mechanism hypotheses only. The Phase-46 objective is to convert them into finite, point-in-time, reproducible NIFTY tests rather than accept video recommendations as evidence.


## Profit Breakout channel review

The user-designated Profit Breakout channel materially expands the discovery set because several videos explicitly connect strategy choice to India VIX or changing volatility. In particular, the channel presents:

- an India-VIX framework comparing Calendar Spread, Iron Fly, Iron Condor, Straddle and Strangle by volatility environment;
- a Batman/double-ratio strategy with a VIX-based entry filter;
- Iron Fly versus Iron Condor selection across high and low volatility;
- an adaptive Iron Fly-to-Iron Condor transition using premium imbalance and market-structure changes;
- a monthly strategy that explicitly adapts strike selection to India VIX;
- weekly/monthly premium-selling structures with hedges and adjustment rules.

These sources support a broader research hypothesis: **VIX should be treated as a state/context variable, not a single “high = sell / low = buy” switch.** The project therefore retains LOW/NORMAL as active test regimes while adding the missing RISING/HIGH/SPIKE/HIGH_RISING hypotheses.

The source material also motivates testing **within-state transitions** (for example, rising-to-falling VIX) in addition to static VIX levels. No source's claimed profitability is accepted as evidence without the project's independent backtesting protocol.
