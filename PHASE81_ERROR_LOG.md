# Phase 81 Error / Limitation Log
Date: 2026-10-10

## E81-001 — No quote/depth fills
- Status: KNOWN LIMITATION.
- The primary dataset exposes OHLCV(+OI), not historical bid/ask/depth. Candle-open references plus adverse tick are only a conservative proxy, not executable fills.

## E81-002 — Coverage/exact-minute missingness
- Status: OPEN until workflow run completes.
- Every missing timestamp, missing exact contract, duplicated row, nonpositive open, missing/zero volume, or expiry-identity mismatch must be excluded and counted. No imputation permitted.

## E81-003 — Held-out sample isolation
- Status: CONTROL.
- Workflow uses only listed option-expiry files through 2025-12-31. It must not compute 2026 holdout results.

## E81-004 — Historical cost-model limitations
- Status: DOCUMENTED.
- Paytm Money ₹10/order + historical fees and one-/two-tick slippage are modeled. Actual queue position, quote spread, partial fills and market impact are unavailable.

## E81-006 — Initial duplicate-key audit was too coarse
- Status: ROOT CAUSE IDENTIFIED; corrected script is rerunning.
- First successful run 38044126538 classified 6,039 session×variant attempts as duplicates because the snapshot key used timestamp/side/strike but omitted explicit expiry identity. This could conflate separate contract identities and also rejected all duplicate records without distinguishing identical data from conflicting observations.
- Correction: the snapshot key now includes timestamp, side, strike and explicit expiry. Rows whose expiry disagrees with the file-named expiry are counted and excluded from the expected-contract snapshot. Repeated same-contract/minute rows are collapsed only when the fields used for this experiment (open and volume) are identical. Conflicting duplicates remain missing/excluded.
- The first run's performance summaries are exploratory diagnostics only and are superseded by the corrected run. No candidate selection/promotion was based on them.
