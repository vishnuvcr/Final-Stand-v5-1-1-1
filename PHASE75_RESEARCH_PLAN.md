# Phase 75 — Exact expiry and strategy-leg identity audit
Date opened: 2026-10-10
Status: PLAN FROZEN; audit implementation pending.

## Research question
Can each frozen strategy leg on 2026-07-28 and 2026-08-04 be mapped unambiguously to a historical NIFTY option expiry date, absolute strike, and option side using authorized evidence, and can the DhanHQ rolling-option expiry code be independently tied to that contract?

## Frozen scope
- Target dates: 2026-07-28 and 2026-08-04 only.
- Existing strategy configurations/trigger rows only; no new strategy variants.
- Contract identity fields: trade date, signal timestamp, expiry date, absolute strike, CE/PE side, quantity/lot size, and source provenance.
- Sources prioritized: existing frozen research artifacts; official NSE contract/expiry archives and circulars; DhanHQ official API documentation and returned metadata. Do not use unofficial guesses as ground truth.
- No paid data purchases and no raw market data in public repo without confirmed retention rights.

## Method
1. Read the canonical frozen strategy/trigger artifacts and enumerate every required leg; do not infer missing legs.
2. Derive the legally valid expiry candidates from official exchange records for each target date.
3. Determine whether the rolling endpoint exposes enough metadata to bind code/flag to an exact expiry date. If not, mark the mapping as unidentifiable rather than guessing.
4. Cross-check strike increments, option side, and expiry against official contract records where available.
5. Join the Phase 74 aggregate strike-coverage result only after exact identity is established. Coverage counts alone cannot establish identity.
6. Produce a leg-by-leg audit with PASS/BLOCKED and source links; retain no API token or unlicensed raw prices.

## Decision gates
- PASS only when every required frozen leg has a source-backed exact expiry date, absolute strike, and side, with no ambiguous mapping.
- If any required field is absent or code-to-expiry mapping cannot be independently verified, classify the affected replay as BLOCKED; do not impute expiry.
- No P&L until data rights and execution model are also approved. OHLC-only data require explicit conservative fill assumptions and Paytm Money fees, brokerage, taxes, slippage and spread stress.

## Deliverables
- `PHASE75_STATUS.md`, `PHASE75_ERROR_LOG.md`
- `results/phase75_contract_identity/summary.json` and `report.md`
- A manual GitHub Actions workflow; aggregate-only outputs.
- README checkpoint updated after the audit outcome.
