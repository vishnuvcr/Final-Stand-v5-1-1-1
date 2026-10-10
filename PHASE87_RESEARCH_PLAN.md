# Phase 87 — Dhan expired-options data qualification

Date: 2026-10-10
Branch: `phase-87-expired-options-data-qualification`
Status: IN PROGRESS — bounded historical expired-options probe committed; Actions result pending.

## Research question
Can the authenticated Dhan account retrieve historical rolling options candles for a specified NSE index-option underlying and one bounded date window, with OHLC and selected derived fields? What remains unavailable for execution-quality strategy replay?

## Aim and objectives
1. Use the Phase 86 verified Dhan token and active Data API plan.
2. Make exactly one bounded request to the documented `POST /v2/charts/rollingoption` endpoint.
3. Probe five-minute NIFTY index-option rolling data for 2026-07-28 only (end date non-inclusive), ATM, monthly expiry code 1, call side.
4. Record HTTP status, whether an option block exists, row count, and presence of expected arrays; never print or persist raw response values.
5. Determine whether rolling OHLC/IV/OI/volume/spot can support a subsequent feature/data-coverage study.
6. Keep historical bid/ask and depth as a separate mandatory gate for execution-quality claims.

## Method
- Read Phase 86 plan/status/error log first.
- Use `secrets.DHAN_ACCESS_TOKEN` in GitHub Actions.
- Request fields: open, high, low, close, IV, volume, strike, OI and spot.
- Use official Dhan API documentation and one date only; no broad download or repeated retries.
- No live order API, no raw data artifact, no strategy replay and no Phase 83 holdout.
- A successful request proves only the endpoint/data shape for this one rolling series and date. It does not prove exact contract reconstruction, completeness across all strikes/expiries, or historical executable quotes.

## Acceptance gates
- A: token remains valid and the request reaches the endpoint.
- B: non-empty timestamp array and matching OHLC arrays returned.
- C: IV/OI/volume/strike/spot arrays evaluated for presence and length alignment.
- D: rights and terms for research caching/publication reviewed before retaining bulk data.
- E: exact contract/expiry coverage and historical bid/ask/depth remain unproven until separately established.
- F: freeze Paytm Money brokerage, statutory charges, slippage and latency before any replay.

## Stop rule
One API call, one workflow run result, then classify PASS / PARTIAL / FAIL. Do not bulk-fetch five years, fan out across strikes, cache raw payloads or tune strategies in this phase.

## Statistical analysis
No profitability tests or strategy ranking are run. If data shape passes, the next phase is a finite coverage/alignment audit against the exact required dates and registered strategies; no holdout access.

## Source
Official Dhan expired-options documentation: https://dhanhq.co/docs/v2/expired-options-data/
