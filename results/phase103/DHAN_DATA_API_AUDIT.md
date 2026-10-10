# Phase 103.1 — Dhan Data API smoke test

**Status:** DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS
**Window:** 2026-08-03 inclusive to 2026-08-04 exclusive (1 days)
**Probe limit:** 1
**Run:** 38089152325

This is a data-feasibility probe, not a strategy test. The token and raw rows are not published.

| Symbol | Side | HTTP | Status | Error code | Safe message | Rows | Arrays consistent | First UTC | Last UTC | IST-date row counts | Rows outside requested dates |
|---|---|---:|---|---|---|---:|---|---|---|---|---:|
| HDFCBANK | CALL | 200 | DATA_RETURNED |  |  | 770 | True | 2026-08-03T03:45:00+00:00 | 2026-08-04T10:09:00+00:00 | | {"2026-08-03": 385, "2026-08-04": 385} | 385 |

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
- Returned timestamps are audited in Asia/Kolkata against the documented half-open request window; out-of-window rows block accepting the sample.
