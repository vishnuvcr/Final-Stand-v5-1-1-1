# Phase 50 Literature Review — Far-OTM Tail Geometry and Volatility Regimes

## Main evidence themes

### 1. Deep OTM options contain information about tail risk

Wang and Yen study option-implied tail loss/gain measures constructed from deep out-of-the-money options and report information about future underlying returns, with tail-risk effects related to the priced premium for extreme outcomes.

Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2977988

### 2. OTM volatility skew can contain information

Doran, Tarrant and Peterson document strong short-maturity OTM put skew and report that the shape of the skew contains information about crashes and upside spikes, with the strongest results in short-term OTM puts.

Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=874991

### 3. Volatility-surface construction matters especially away from ATM

Ulrich and Walther report that forward-looking variance, skewness and variance-risk-premium measures can be sensitive to volatility-surface construction, with economically meaningful biases in OTM put regions.

Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3184767

### 4. NIFTY-50 evidence directly motivates the high-volatility test

A 2026 paper by Potharla and Sen studies conditional volatility-smile asymmetry in NIFTY-50 index options over 2008–2024 and reports stronger smile convexity in high-volatility regimes, with liquidity and trading activity influencing downside-tail pricing.

Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6857939

### 5. Option returns and tail-risk premia

The broader options literature identifies non-trivial risk premia associated with skewness/tail exposure. These premia are not automatically harvestable after transaction costs and selection bias, which is why Phase 50 requires strict out-of-sample confirmation.

## Implication for Phase 50

The literature supports treating far-OTM strike geometry and smile/skew state as legitimate research variables. It does not establish a profitable NIFTY trading rule.

Phase 50 therefore tests:
- whether high-VIX states alter the optimal tail distance;
- whether far-OTM variants improve net/stressed P&L;
- whether improvements survive active-vs-complement inference and Holm correction;
- whether any apparent advantage survives the protected 2026 holdout.

## Search limitations

This is a targeted literature review rather than a claim of exhaustive retrieval of every paper, working paper or video on OTM option tails. The numerical research remains governed by the repository preregistration and evidence hierarchy.