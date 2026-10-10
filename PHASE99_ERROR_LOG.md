# Phase 99 Error / Limitation Log

## Source and data limitations
- U07's put-butterfly heading says “Short Butterfly”, while its described/example legs buy one lower-strike put, sell two middle-strike puts, and buy one higher-strike put. These legs are a long butterfly payoff; source naming/legs conflict. Preserve source label and report the conflict.
- U07 examples are payoff illustrations, not prediction signals or an executable historical NIFTY strategy.
- U05's rule depends on historical exact-contract option prices/liquidity, first-Wednesday underlying data, strike selection, lot sizes and early exits. The price/quote/fill coverage required for full replication has not been established.
- Historical Paytm Money charges, statutory levies, bid/ask spread, slippage and latency are mandatory for market P&L.

## Runtime errors
- None recorded at phase start. Record every test or workflow defect and its fix here.

- 2026-10-10: Phase 99 workflow [38073059250](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38073059250) passed. The payoff calculator is analytical only; no market-data or cost model was run. U07 put-butterfly source inconsistency is explicitly logged.
