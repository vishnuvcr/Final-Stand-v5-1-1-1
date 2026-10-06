# Phase 40 Literature Review

Forecast combination can help when component errors are not perfectly correlated. Recent work also supports regime-aware routing and the use of implied-volatility information as an additional forecasting channel.

Relevant evidence:
- VIX variables can add out-of-sample information to volatility forecasts and the effect is especially relevant in stressed regimes. citeturn795644search1
- A 2026 Bayesian stacking paper reports that the forecasting objective can shift ensemble weight toward VIX/implied-volatility models and improve economic performance. citeturn795644search2
- Recent regime-aware forecasting work uses causal rolling regime detection with VIX as an input and explicitly avoids look-ahead. citeturn795644search7
- NSE provides a historical-data endpoint specifically for India VIX, and Yahoo Finance exposes ^INDIAVIX historical daily observations. citeturn681497search3turn681497search1

The literature motivates VIX as a routing/context variable, not as a deterministic bullish/bearish oracle. Phase 40 therefore tests VIX both as an expert and as a gate.

This literature review does not establish that the Phase-40 ensemble will improve the trading strategy.
