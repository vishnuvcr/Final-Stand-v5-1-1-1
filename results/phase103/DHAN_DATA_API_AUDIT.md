# Phase 103.1 — Dhan Data API smoke test

**Status:** PROBE_ABORTED_AFTER_FIRST_INVALID_RELATIVE_STRIKE
**Target window (IST):** 2026-08-03 inclusive to 2026-08-04 exclusive (1 days)
**Dhan request dates:** fromDate=2026-08-03; toDate=2026-08-03 (empirically inclusive; target end remains exclusive)
**Relative strikes:** ATM, ATM+1, ATM+2, ATM+3, ATM-1, ATM-2, ATM-3
**Probe limit:** 70
**Run:** 38090149633

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
| HDFCBANK | PUT | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 750 | 750 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | PUT | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 760 | 760 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | PUT | ATM+2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 770 | 770 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | PUT | ATM+3 | 200 | DATA_RETURNED |  |  | 384 | True | 2 | 8 | 780 | 780 | 2026-08-03T03:46:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 384} | 0 |
| HDFCBANK | PUT | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 740 | 740 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | PUT | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 730 | 730 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| HDFCBANK | PUT | ATM-3 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 8 | 720 | 720 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1440 | 1460 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1450 | 1470 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1460 | 1480 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | ATM+3 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1470 | 1490 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1430 | 1450 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1420 | 1440 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | CALL | ATM-3 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1410 | 1430 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | PUT | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1440 | 1460 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | PUT | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1450 | 1470 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | PUT | ATM+2 | 200 | DATA_RETURNED |  |  | 379 | True | 3 | 41 | 1460 | 1480 | 2026-08-03T03:51:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 379} | 0 |
| ICICIBANK | PUT | ATM+3 | 200 | DATA_RETURNED |  |  | 378 | True | 3 | 41 | 1470 | 1490 | 2026-08-03T03:52:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 378} | 0 |
| ICICIBANK | PUT | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1430 | 1450 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | PUT | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1420 | 1440 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| ICICIBANK | PUT | ATM-3 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 41 | 1410 | 1430 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1310 | 1320 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1320 | 1330 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1330 | 1340 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | ATM+3 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1340 | 1350 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1300 | 1310 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1290 | 1300 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | CALL | ATM-3 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1280 | 1290 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1310 | 1320 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1320 | 1330 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | ATM+2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1330 | 1340 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | ATM+3 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1340 | 1350 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1300 | 1310 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1290 | 1300 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| RELIANCE | PUT | ATM-3 | 200 | DATA_RETURNED |  |  | 385 | True | 2 | 1 | 1280 | 1290 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1040 | 1040 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1050 | 1050 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1060 | 1060 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | ATM+3 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1070 | 1070 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1030 | 1030 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1020 | 1020 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | CALL | ATM-3 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1010 | 1010 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | PUT | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1040 | 1040 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | PUT | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1050 | 1050 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | PUT | ATM+2 | 200 | DATA_RETURNED |  |  | 383 | True | 3 | 17 | 1050 | 1060 | 2026-08-03T03:47:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 383} | 0 |
| SBIN | PUT | ATM+3 | 200 | DATA_RETURNED |  |  | 382 | True | 3 | 17 | 1060 | 1070 | 2026-08-03T03:48:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 382} | 0 |
| SBIN | PUT | ATM-1 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1030 | 1030 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | PUT | ATM-2 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1020 | 1020 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| SBIN | PUT | ATM-3 | 200 | DATA_RETURNED |  |  | 385 | True | 3 | 18 | 1010 | 1010 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| INFY | CALL | ATM | 200 | DATA_RETURNED |  |  | 385 | True | 4 | 26 | 1160 | 1180 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| INFY | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 385 | True | 4 | 26 | 1175 | 1200 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 385} | 0 |
| INFY | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 216 | True | 4 | 8 | 1180 | 1220 | 2026-08-03T03:45:00+00:00 | 2026-08-03T10:09:00+00:00  | {"2026-08-03": 216} | 0 |
| INFY | CALL | ATM+3 | 200 | UNKNOWN |  |  | 0 | True | 0 | 0 |  |  |  |   | {} | n/a |

## Relative-strike surface / fixed-contract continuity audit

| Symbol | Side | Offsets returned | Common timestamps | Union timestamps | Min distinct strikes/minute | Max distinct strikes/minute | Distinct actual strikes | Strikes seen every minute | Duplicate timestamp-strike keys | Surface gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HDFCBANK | CALL | 7 | 384 | 385 | 6 | 7 | 8 | 6 | 0 | FAIL |
| HDFCBANK | PUT | 7 | 384 | 385 | 6 | 7 | 8 | 5 | 0 | FAIL |
| ICICIBANK | CALL | 7 | 385 | 385 | 7 | 7 | 9 | 5 | 0 | PASS |
| ICICIBANK | PUT | 7 | 378 | 385 | 5 | 7 | 9 | 3 | 0 | FAIL |
| INFY | CALL | 4 | 0 | 385 | 2 | 3 | 6 | 0 | 0 | FAIL |
| RELIANCE | CALL | 7 | 385 | 385 | 7 | 7 | 8 | 6 | 0 | PASS |
| RELIANCE | PUT | 7 | 385 | 385 | 7 | 7 | 8 | 6 | 0 | PASS |
| SBIN | CALL | 7 | 385 | 385 | 7 | 7 | 9 | 5 | 0 | PASS |
| SBIN | PUT | 7 | 382 | 385 | 5 | 7 | 9 | 4 | 0 | FAIL |

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
