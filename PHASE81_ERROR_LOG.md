# Phase 81 Error / Limitation Log
Date: 2026-10-10

## E81-001 — No quote/depth fills
- Status: KNOWN LIMITATION.
- The primary dataset exposes OHLCV(+OI), not historical bid/ask/depth. Candle-open references plus adverse tick are only a conservative proxy, not executable fills.

## E81-002 — Coverage/exact-minute missingness
- Status: RESOLVED FOR CURRENT RUN; 182 incomplete cases explicitly excluded, zero file/schema errors.
- Every missing timestamp, missing exact contract, duplicated row, nonpositive open, missing/zero volume, or expiry-identity mismatch must be excluded and counted. No imputation permitted.

## E81-003 — Held-out sample isolation
- Status: CONTROL.
- Workflow uses only listed option-expiry files through 2025-12-31. It must not compute 2026 holdout results.

## E81-004 — Historical cost-model limitations
- Status: DOCUMENTED.
- Paytm Money ₹10/order + historical fees and one-/two-tick slippage are modeled. Actual queue position, quote spread, partial fills and market impact are unavailable.


## E81-006 — Initial duplicate-key audit was too coarse
- Status: RESOLVED IN CODE; correction validated by successful persisted run 38044579698.
- First successful run 38044126538 classified 6,039 session×variant attempts as duplicates because the snapshot key omitted explicit expiry identity. Those results are superseded and were not used for selection.
- Corrected snapshot key includes timestamp, side, strike and explicit expiry. Only rows identical on open and volume for the same exact key are collapsed; conflicting rows remain excluded.
- Corrected result: 122,310 identical rows collapsed; zero conflicting duplicate keys; zero rows with expiry not matching the file name; zero invalid identity-field rows.

## E81-007 — Corrected run initially failed at result persistence
- Status: RESOLVED by successful retry.
- Run 38044559407 completed the corrected computation and uploaded artifact 11666557659, but its final Git rebase failed with a conflict on PHASE81_STATUS.md after a concurrent repository status update.
- The subsequent run 38044579698 completed all steps and successfully persisted the corrected aggregate and derived research ledger. No strategy selection was based on the non-persisted intermediate run. Future phase workflows must avoid manual writes to status files while a workflow is running and should use retry-safe commits.
