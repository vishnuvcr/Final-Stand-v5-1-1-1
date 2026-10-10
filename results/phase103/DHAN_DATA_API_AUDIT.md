# Phase 103.1 — Dhan Data API smoke test

**Status:** NO_DATA_RETURNED_OR_SCHEMA_MISMATCH
**Window:** 2026-08-02 inclusive to 2026-09-01 exclusive (30 days)
**Run:** 38088386046

This is a data-feasibility probe, not a strategy test. The token and raw rows are not published.

| Symbol | Side | HTTP | Status | Rows | Arrays consistent | First UTC | Last UTC |
|---|---|---:|---|---:|---|---|---|
| HDFCBANK | CALL | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| HDFCBANK | PUT | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| ICICIBANK | CALL | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| ICICIBANK | PUT | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| RELIANCE | CALL | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| RELIANCE | PUT | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| SBIN | CALL | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| SBIN | PUT | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| INFY | CALL | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |
| INFY | PUT | 400 | HTTP_OR_NETWORK_ERROR | 0 | False |  |  |

## Underlying ID mapping

| Symbol | ID resolved | Status |
|---|---|---|
| HDFCBANK | yes | MATCHED |
| ICICIBANK | yes | MATCHED |
| RELIANCE | yes | MATCHED |
| SBIN | yes | MATCHED |
| INFY | yes | MATCHED |

## Limitations

- Rolling strikes can change actual strike over time.
- This endpoint documents OHLC, IV, volume, OI, strike and spot, not historical bid/ask/depth.
- A single 30-day probe does not establish full-history completeness or independent test sufficiency.
