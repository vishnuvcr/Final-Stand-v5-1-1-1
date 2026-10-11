# Phase 103.1 — Dhan Data API smoke test

**Status:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES
**Target window (IST):** 2026-08-03 inclusive to 2026-08-10 exclusive (7 days)
**Dhan request dates:** fromDate=2026-08-03; toDate=2026-08-09 (empirically inclusive; target end remains exclusive)
**Panels:** ICICIBANK:CALL, RELIANCE:CALL, RELIANCE:PUT, SBIN:CALL
**Relative strikes:** ATM, ATM+1, ATM+2, ATM+3, ATM-1, ATM-2, ATM-3
**Probe limit:** 28
**Run:** 38115153795

This is a multi-session data-feasibility audit, not a strategy P&L test. Panels were selected from the prior one-session alignment screen. The token and raw rows are not published.

| Symbol | Side | Offset | HTTP | Status | Error code | Safe message | Rows | Arrays consistent | Distinct actual strikes | Strike changes | First strike | Last strike | First UTC | Last UTC | IST-date row counts | Rows outside dates |
|---|---|---|---:|---|---|---|---:|---|---:|---:|---|---|---|---|---|---:|
| ICICIBANK | CALL | ATM | 200 | DATA_RETURNED |  |  | 1925 | True | 5 | 113 | 1440 | 1420 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| ICICIBANK | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 1925 | True | 5 | 113 | 1450 | 1430 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| ICICIBANK | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 1925 | True | 5 | 113 | 1460 | 1440 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| ICICIBANK | CALL | ATM+3 | 200 | DATA_RETURNED |  |  | 1925 | True | 5 | 113 | 1470 | 1450 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| ICICIBANK | CALL | ATM-1 | 200 | DATA_RETURNED |  |  | 1925 | True | 5 | 113 | 1430 | 1410 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| ICICIBANK | CALL | ATM-2 | 200 | DATA_RETURNED |  |  | 1925 | True | 5 | 113 | 1420 | 1400 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| ICICIBANK | CALL | ATM-3 | 200 | DATA_RETURNED |  |  | 1920 | True | 5 | 111 | 1410 | 1390 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 383, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 382} | 0 |
| RELIANCE | CALL | ATM | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1310 | 1330 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1320 | 1340 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1330 | 1350 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | CALL | ATM+3 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1340 | 1360 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | CALL | ATM-1 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1300 | 1320 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | CALL | ATM-2 | 200 | DATA_RETURNED |  |  | 1923 | True | 8 | 80 | 1290 | 1310 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 383, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | CALL | ATM-3 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1280 | 1300 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | PUT | ATM | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1310 | 1330 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | PUT | ATM+1 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1320 | 1340 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | PUT | ATM+2 | 200 | DATA_RETURNED |  |  | 1923 | True | 8 | 80 | 1330 | 1350 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 384, "2026-08-05": 385, "2026-08-06": 384, "2026-08-07": 385} | 0 |
| RELIANCE | PUT | ATM+3 | 200 | DATA_RETURNED |  |  | 1924 | True | 8 | 80 | 1340 | 1360 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 384, "2026-08-07": 385} | 0 |
| RELIANCE | PUT | ATM-1 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1300 | 1320 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| RELIANCE | PUT | ATM-2 | 200 | DATA_RETURNED |  |  | 1922 | True | 8 | 80 | 1290 | 1310 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 383, "2026-08-05": 385, "2026-08-06": 384, "2026-08-07": 385} | 0 |
| RELIANCE | PUT | ATM-3 | 200 | DATA_RETURNED |  |  | 1925 | True | 8 | 80 | 1280 | 1300 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| SBIN | CALL | ATM | 200 | DATA_RETURNED |  |  | 1925 | True | 10 | 77 | 1040 | 1100 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| SBIN | CALL | ATM+1 | 200 | DATA_RETURNED |  |  | 1925 | True | 10 | 77 | 1050 | 1110 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| SBIN | CALL | ATM+2 | 200 | DATA_RETURNED |  |  | 1925 | True | 10 | 77 | 1060 | 1120 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| SBIN | CALL | ATM+3 | 200 | DATA_RETURNED |  |  | 1925 | True | 10 | 77 | 1070 | 1130 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| SBIN | CALL | ATM-1 | 200 | DATA_RETURNED |  |  | 1924 | True | 10 | 77 | 1030 | 1090 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 385, "2026-08-06": 384, "2026-08-07": 385} | 0 |
| SBIN | CALL | ATM-2 | 200 | DATA_RETURNED |  |  | 1924 | True | 10 | 77 | 1020 | 1080 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 385, "2026-08-05": 384, "2026-08-06": 385, "2026-08-07": 385} | 0 |
| SBIN | CALL | ATM-3 | 200 | DATA_RETURNED |  |  | 1922 | True | 10 | 77 | 1010 | 1070 | 2026-08-03T03:45:00+00:00 | 2026-08-07T10:09:00+00:00  | {"2026-08-03": 385, "2026-08-04": 384, "2026-08-05": 383, "2026-08-06": 385, "2026-08-07": 385} | 0 |

## Relative-strike surface / fixed-contract continuity audit

| Symbol | Side | Offsets returned | Common timestamps | Union timestamps | Min distinct strikes/minute | Max distinct strikes/minute | Distinct actual strikes | Strikes seen every minute | Duplicate timestamp-strike keys | Surface gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ICICIBANK | CALL | 7 | 1920 | 1925 | 6 | 7 | 11 | 3 | 0 | FAIL |
| RELIANCE | CALL | 7 | 1923 | 1925 | 6 | 7 | 14 | 0 | 0 | FAIL |
| RELIANCE | PUT | 7 | 1922 | 1925 | 4 | 7 | 14 | 0 | 0 | FAIL |
| SBIN | CALL | 7 | 1921 | 1925 | 5 | 7 | 16 | 0 | 0 | FAIL |

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
