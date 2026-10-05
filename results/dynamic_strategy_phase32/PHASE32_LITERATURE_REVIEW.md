# Phase 32 — Literature and External Evidence Supplement

## 1. Indian index-option market efficiency

Aggarwal and Gupta (2009) examined call/put spreads, box spreads and convexity relationships in Indian index options while incorporating bid-ask spread, brokerage and taxes. Their evidence shows that market frictions materially affect whether apparent pricing violations are exploitable.

Priyan and Mohanti (2015) studied box-spread arbitrage in Indian index options and reported that the proportion of exploitable violations fell sharply after transaction costs. This is directly relevant to Phase 32 because the strategy's gross edge is substantially reduced by modeled trading costs.

Mohanti and Priyan (2015) applied Black–Scholes and dynamic hedging to Indian index options and explicitly evaluated whether theoretical pricing deviations remained exploitable after hedging costs. Their work supports treating model-derived delta as a research tool, not as proof of free arbitrage.

## 2. Option-selling and volatility-risk-premium literature

Bhat (2024), in the *Journal of Futures Markets*, documented day/night asymmetry in option returns in an emerging market and discussed the positive-return characteristics associated with delta-hedged option selling. This supports studying systematic option-premium effects, but the result is not evidence for the specific Phase-32 directional state machine.

Pillai (2026), SSRN 6876580, studied several NIFTY volatility-risk-premium strategies using explicit transaction-cost and slippage assumptions. The methodological relevance is the emphasis on implementation frictions and the difficulty of distinguishing theoretical option-selling premium from a tradeable net edge.

John (2026), a recent preprint on NIFTY volatility-risk-premium harvesting, emphasizes out-of-sample design and the possibility of a post-2024/2025 structural regime break. This is contextually consistent with the Phase-32 finding that performance is materially different across calendar periods.

## 3. Data-source and implementation evidence

The primary Phase-32 data source is the public Hugging Face dataset `thetrademarkk/india-index-options-1m`, which provides 1-minute index-option and spot data suitable for reproducible research but has documented sparse/incomplete historical coverage.

A secondary public source, `artist-23/nifty-options-data`, contains tens of millions of NIFTY option rows with IV/OI/spot fields and rolling weekly-strike labels. It was intentionally not merged into the primary estimate because explicit contract/expiry identifiers are not exposed in the published representation, and an unvalidated contract-mapping layer could create look-ahead or wrong-expiry contamination.

## 4. Regulatory and cost references

Historical NIFTY weekly-expiry and lot-size transitions were validated against NSE circulars, including the 2021 lot-size changes and the 2025 Thursday-to-Monday-to-Tuesday expiry-calendar transitions.

The primary cost model uses ₹10 brokerage per executed order in line with the current Paytm Money F&O FAQ, plus historical STT, exchange transaction charges, SEBI turnover fee, IPFT, stamp duty and GST. The exact historical broker-level monthly slab cannot be reconstructed from public information, so the backtest uses a transparent per-order model rather than claiming exact account-level billing.

## 5. Interpretation for Phase 32

The literature does not establish that a 0.25-delta directional spread with a keep/flip state machine should be profitable. Instead, the literature supports three methodological conclusions used in this phase:

1. transaction costs can eliminate apparent option-market edges;
2. delta-based option-selling results can be regime- and timing-dependent;
3. realistic execution and complete contract history are essential before promoting a short-option strategy.

### References

- Aggarwal, N., & Gupta, M. (2009). *Empirical Evidence on the Efficiency of Index Options Market in India*. Asia Pacific Business Review.
- Bhat, A. (2024). *The asymmetry in day and night option returns: Evidence from an emerging market*. Journal of Futures Markets, 44(8), 1320–1337. DOI: 10.1002/fut.22512.
- Mohanti, D., & Priyan, P. K. (2015). *An Empirical Test of Market Efficiency of Indian Index Options Market Using the Black–Scholes Model and Dynamic Hedging Strategy*. DOI: 10.1177/0971890714558709.
- Priyan, P. K., & Mohanti, D. (2015). *An Investigation of Box-Spread Strategy and Arbitrage Efficiency on Indian Index Options Market*. Metamorphosis, 14(1), 39–47.
- Pillai, S. (2026). *Trading the Volatility Risk Premium on Nifty 50: Strategy Backtest with Realistic Frictions*. SSRN 6876580.
- John, A. R. (2026). *Harvesting the Volatility Risk Premium in Nifty Index Options: Out-of-Sample Evidence and the Post-2024 Regulatory Regime Break*. DOI: 10.13140/RG.2.2.20010.99528.
