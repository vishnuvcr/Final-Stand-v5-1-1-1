# Phase 99 — Options Payoff Taxonomy Replay

**Outcome: analytical payoff checks implemented; historical profitability backtest remains DATA-BLOCKED. No strategy is promoted.**

The payoff table calculates intrinsic payoff plus initial premium cash flow per underlying unit at expiry. The included premiums and most strike combinations are illustrative inputs to test the algebra, not historical NIFTY quotes and not recommendations. The results exclude brokerage, statutory charges, bid/ask, slippage, latency, margin funding and lot-specific execution.

Source extraction:
- U07 describes directional options, vertical spreads, butterflies and volatility structures. The source's put-butterfly section is internally inconsistent: its heading calls it “Short Butterfly”, while its example legs buy one lower-strike put, sell two middle-strike puts and buy one higher-strike put. The legs imply a long butterfly payoff; this is flagged, not silently corrected.
- U05 specifies first-Thursday entry, one-month European options, strike based on first-Wednesday price and prior three-year average monthly return, a 20% target, a 30% stop and delayed stop activation after T+3. The original market replay is blocked without point-in-time exact-contract prices/liquidity and credible early-exit fills.
- These payoff formulas are not evidence that any strategy predicts NIFTY or makes money after costs.

See illustrative_payoffs.csv and source_method_status.csv. Phase 83's 2026 holdout remains sealed.
