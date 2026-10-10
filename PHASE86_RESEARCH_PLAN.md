# Phase 86 — Dhan API connectivity and data-capability audit

Date: 2026-10-10
Branch: `phase-86-dhan-api-connectivity-audit`
Status: IN PROGRESS — read-only connectivity workflow committed; run result pending.

## Research question
Can the configured `DHAN_ACCESS_TOKEN` authenticate successfully in GitHub Actions, and does the account expose a usable historical candle endpoint for a minimal index probe? If yes, what can be concluded—and what remains unproven—for options-strategy execution-quality research?

## Aims and objectives
1. Verify token presence without revealing it.
2. Call Dhan's documented GET `/v2/profile` endpoint and record only HTTP/authentication outcome plus whether the Data API plan is reported active.
3. If the profile confirms an active data plan, make one bounded, read-only five-minute index-candle probe for 2026-10-08 through 2026-10-09.
4. Never persist or print the profile response, client identifiers, token, or raw market-data payload.
5. Distinguish historical OHLC/OI capability from historical bid/ask and depth; do not treat candles as executable prices.
6. Record outcomes and errors in the phase log and README. Do not run a strategy backtest in this phase.

## Method
- Use GitHub Actions secrets; secret name: `DHAN_ACCESS_TOKEN`.
- Use only Dhan's documented profile endpoint and one small historical-candle request.
- The workflow does not submit, modify, or cancel orders.
- The workflow has a manual `workflow_dispatch` trigger and a branch-scoped push trigger.
- Only status codes, boolean capability flags, candle count, and exception class are written to logs/summary. Raw responses are never printed or uploaded.
- If the probe fails, classify the result as authentication, entitlement, instrument/schema, network, or inconclusive; do not silently change identifiers and claim success.

## Acceptance gates
- Gate A: secret exists in the workflow environment.
- Gate B: profile endpoint returns HTTP 200 and token validity is confirmed.
- Gate C: profile reports Data API plan active.
- Gate D: bounded candle probe returns OHLC/timestamp arrays with at least one candle.
- Gate E (separate, not established by this probe): target option contracts/expiries are resolvable and have adequate historical coverage.
- Gate F (separate, not established by this probe): historical bid/ask and quantities/depth are available at entry/exit timestamps and permitted for research/cache/publication.
- Gate G: freeze Paytm Money brokerage, statutory charges, slippage and latency before any executable P&L claims.

## Statistical plan
No hypothesis test or profitability analysis is run in Phase 86. If gates E–G later pass, preregister a finite contract/date coverage audit first; only then design a separate replay phase. Keep the Phase 83 holdout sealed.

## Stop rule
Stop this phase after the single profile request and at most one small candle request. No loops over instruments, bulk downloads, raw-data caching, paid purchases, live orders, strategy tuning, or holdout access.

## Sources
- DhanHQ authentication and User Profile: https://dhanhq.co/docs/v2/authentication/
- DhanHQ historical data: https://dhanhq.co/docs/v2/historical-data/
- DhanHQ API introduction: https://dhanhq.co/docs/v2/

## Deliverables
Workflow, plan, status, error log, auditable chat/decision log, README checkpoint, and a finite GO/NO-GO for the next data qualification phase.
