# Phase 108 Error and Limitation Log

## Registered limitations
- Reused sample; multiple-comparison and selection bias.
- Range proxy is not India VIX or implied volatility.
- Daily OHLC and assumed slippage do not verify fills, spreads, depth, latency, partial fills or market impact.
- Paytm Money account-specific brokerage is unverified.

## Runtime errors
None at registration. Append any workflow/test/data/accounting/publication failures.


## 2026-10-12 — Workflow audit
- Workflow 38167282757 succeeded, including regression tests, replay, aggregate artifact upload and publication; no runtime error remains for this run.
- Result limitation: all ten candidates were negative under primary and strict stress costs; sample is short and reused, and the volatility estimator is realized absolute underlying return, not India VIX or implied volatility.
- Do not use this 240-row cost sensitivity as a substitute for Phase 109's ≥1,000 unique parameter configurations per family.
