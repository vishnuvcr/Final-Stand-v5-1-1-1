# Phase 103.1 — Dhan Data API smoke test

**Status:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES
**Target window (IST):** 2026-08-03 inclusive to 2026-08-04 exclusive (1 days)
**Dhan request dates:** fromDate=2026-08-03; toDate=2026-08-03 (empirically inclusive; target end remains exclusive)
**Relative strikes:** ATM, ATM+1, ATM+2, ATM+3, ATM-1, ATM-2, ATM-3
**Probe limit:** 7
**Run:** 38089913649

This is a data-feasibility probe, not a strategy test. The token and raw rows are not published.

| Symbol | Side | Offset | HTTP | Status | Error code | Safe message | Rows | Arrays consistent | Distinct actual strikes | Strike changes | First strike | Last strike | First UTC | Last UTC | IST-date row counts | Rows outside dates |
|---|---|---|---:|---|---|---|---:|---|---:|---:|---|---|---|---|---|---:|
| HDFCBANK | CALL | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 750 | 750 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 760 | 760 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 770 | 770 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | CALL | ATM+3 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 780 | 780 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | CALL | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 740 | 740 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | CALL | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 730 | 730 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | CALL | ATM-3 | 200 | DATA_RETURNED |  |  | 384 | True | 2 | 8 | 720 | 720 | 2026-08-03T03:46:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 384} | 0 |

## Relative-strike surface / fixed-contract continuity audit

| Symbol | Side | Offsets returned | Common timestamps | Union timestamps | Min distinct strikes/minute | Max distinct strikes/minute | Distinct actual strikes | Strikes seen every minute | Duplicate timestamp-strike keys | Surface gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HDFCBANK | CALL | 7 | 384 | 385 | 6 | 7 | 8 | 6 | 0 | FAIL |

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
