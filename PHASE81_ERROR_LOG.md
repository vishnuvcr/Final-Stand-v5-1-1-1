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
