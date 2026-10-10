# Phase 82 Error / Limitation Log
Date: 2026-10-10

## E82-001 — Expiry-cluster independence assumption
- Status: KNOWN LIMITATION.
- The inference uses expiry as the resampling cluster; macro/regime shocks can span several expiries, so confidence intervals may still be too narrow if dependence persists across expiry boundaries.

## E82-002 — Historical execution evidence
- Status: KNOWN LIMITATION.
- OHLC candle opens plus adverse ticks are not historical bid/ask/depth. Any apparent significance still requires quote/depth validation before executable claims.

## E82-003 — Historical multiple-testing count
- Status: KNOWN LIMITATION.
- The registered 60-test family is controlled, but the complete number of prior experiments across earlier project phases is not fully enumerable. The final manuscript must disclose this residual selection-bias risk.

## E82-004 — Holdout boundary
- Status: CONTROL.
- The inference script may read only DEV/VAL outputs through 2025-12-31. If no eligible defined-risk candidate passes, 2026 data remain unopened.
