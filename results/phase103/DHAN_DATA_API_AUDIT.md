# Phase 103.1 — Dhan Data API smoke test

**Status:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES
**Target window (IST):** 2026-08-03 inclusive to 2026-08-04 exclusive (1 days)
**Dhan request dates:** fromDate=2026-08-03; toDate=2026-08-03 (empirically inclusive; target end remains exclusive)
**Probe limit:** 10
**Run:** 38089393338

This is a data-feasibility probe, not a strategy test. The token and raw rows are not published.

| Symbol | Side | HTTP | Status | Error code | Safe message | Rows | Arrays consistent | First UTC | Last UTC | IST-date row counts | Rows outside requested dates |
|---|---|---:|---|---|---|---:|---|---|---|---|---:|
| HDFCBANK | CALL | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | PUT | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | PUT | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | PUT | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| INFY | CALL | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| INFY | PUT | 200 | DATA_RETURNED |  |  | 385 | True | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |

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
- One stock/side probe does not establish full-history completeness or independent test sufficiency.
- Empirical diagnostic showed Dhan included toDate in returned rows despite documentation describing it as non-inclusive; requests therefore pass target_end_exclusive minus one day and still audit every timestamp in the original half-open target window.
