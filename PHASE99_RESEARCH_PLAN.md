# Phase 99 — Options Strategy Taxonomy and Payoff Replay

**Branch:** `phase-99-options-strategy-taxonomy-replay`  
**Parent:** `phase-98-cci-options-paper-replication-gate`  
**Status:** PLAN REGISTERED; payoff calculator pending CI  
**Strategy promotion:** NONE

## Research question
Can the payoff structures explicitly described in U05/U07 be transcribed into transparent, unit-tested expiration payoff functions, and which source examples are internally inconsistent or insufficient for historical profitability backtests?

## Source-faithful scope
- U07 / Chatterjee et al. (2022): long call, long put, short call, short put, bull call spread, bull put spread, bear put spread, bear call spread, call butterfly, put butterfly/“short butterfly”, long/short straddle and long strangle where described.
- U05 / Atheetha et al. (2019): one-month European option design, first-Thursday entry, strike selected from prior three-year monthly return and liquidity, 20% target, 30% stop, and T+3 delay before stop-loss activation. This is recorded as a rule specification; historical trade replay requires point-in-time exact-contract premiums and the paper's source-period option records.
- Any ambiguous leg descriptions are preserved and flagged, not silently corrected.

## Method
1. Transcribe source-defined legs and examples from the uploaded PDFs. Keep payoff-at-expiry distinct from premium cash flow and from realized early-exit P&L.
2. Implement generic European option intrinsic payoff for exact strike/right/side/premium legs and named structures only when their leg definitions are unambiguous.
3. Test piecewise payoff values at/below/at/between/above strikes and compare against source examples.
4. Use illustrative paper premiums solely to verify arithmetic. Do not call these market backtests or infer expected profitability.
5. Publish source-definition ledger, tests, payoff examples and ambiguity/coverage log.
6. No historical options P&L without point-in-time exact-contract entry/exit prices, expiry/lot rules, transaction charges, bid/ask or validated fill model, slippage, latency and cost stress. Paytm Money charges must be verified.
7. Proceed to Phase 100 after bounded audit; no access to Phase 83's sealed 2026 holdout.

## Acceptance / stop
- All payoff functions pass deterministic unit tests.
- Every source method is reproduced, partial, ambiguous or data-blocked.
- No parameter search, synthetic premium series or false backtest claims.
