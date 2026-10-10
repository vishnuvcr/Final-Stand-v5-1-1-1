# Phase 74 — Fixed-strike stitch feasibility audit

Decision: **STITCH_FEASIBILITY_RECORDED_REVIEW_REQUIRED**

Checked UTC: 2026-10-10T09:39:28.357966+00:00

| Date | Flag | Code | Side | Offset probes passed | Session timestamps | Distinct strikes | Best strike coverage | Full 375-bar strikes |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 2026-07-28 | MONTH | 1 | CALL | 21/21 | 375 | 23 | 375/375 | 19 |
| 2026-07-28 | MONTH | 1 | PUT | 21/21 | 375 | 23 | 375/375 | 19 |
| 2026-07-28 | MONTH | 2 | CALL | 21/21 | 375 | 9 | 375/375 | 5 |
| 2026-07-28 | MONTH | 2 | PUT | 21/21 | 375 | 9 | 375/375 | 5 |
| 2026-07-28 | WEEK | 1 | CALL | 21/21 | 375 | 23 | 375/375 | 19 |
| 2026-07-28 | WEEK | 1 | PUT | 21/21 | 375 | 23 | 375/375 | 19 |
| 2026-07-28 | WEEK | 2 | CALL | 21/21 | 375 | 23 | 375/375 | 19 |
| 2026-07-28 | WEEK | 2 | PUT | 21/21 | 375 | 23 | 375/375 | 18 |
| 2026-08-04 | MONTH | 1 | CALL | 21/21 | 375 | 25 | 375/375 | 15 |
| 2026-08-04 | MONTH | 1 | PUT | 21/21 | 375 | 25 | 375/375 | 15 |
| 2026-08-04 | MONTH | 2 | CALL | 21/21 | 375 | 11 | 375/375 | 2 |
| 2026-08-04 | MONTH | 2 | PUT | 21/21 | 375 | 11 | 375/375 | 2 |
| 2026-08-04 | WEEK | 1 | CALL | 21/21 | 375 | 25 | 375/375 | 17 |
| 2026-08-04 | WEEK | 1 | PUT | 21/21 | 375 | 25 | 375/375 | 17 |
| 2026-08-04 | WEEK | 2 | CALL | 21/21 | 375 | 11 | 375/375 | 3 |
| 2026-08-04 | WEEK | 2 | PUT | 21/21 | 375 | 11 | 375/375 | 3 |

## Interpretation

Completed all 16 date/expiry/side groups: True. At least one absolute strike had all 375 regular-session timestamps in a group: True. Inspect group-level coverage and field mismatches. Even full strike continuity does not identify the exact expiry date for code 1/2; verify historical contract mapping independently before replay. No prices are persisted.

No raw market rows or credentials are stored. Full strike coverage here only demonstrates the mechanics of stitching rolling offsets; it does not establish the exact expiry date or execution-quality fills.
