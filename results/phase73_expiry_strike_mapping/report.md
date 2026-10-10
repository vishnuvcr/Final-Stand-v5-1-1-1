# Phase 73 — DhanHQ expiry-code and strike mapping audit

Decision: **PARTIAL_OR_FAILED_COMPARISON**

Checked UTC: 2026-10-10T09:37:59.921861+00:00

| Date | Flag | Code | Side | Total rows | Target rows | Regular | Off-session | Strike unique | Strike range | Aligned |
|---|---|---:|---|---:|---:|---:|---:|---:|---|---|
| 2026-07-28 | WEEK | 0 | CALL | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-07-28 | WEEK | 0 | PUT | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-07-28 | WEEK | 1 | CALL | 750 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-07-28 | WEEK | 1 | PUT | 750 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-07-28 | WEEK | 2 | CALL | 750 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-07-28 | WEEK | 2 | PUT | 750 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-07-28 | MONTH | 0 | CALL | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-07-28 | MONTH | 0 | PUT | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-07-28 | MONTH | 1 | CALL | 750 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-07-28 | MONTH | 1 | PUT | 750 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-07-28 | MONTH | 2 | CALL | 750 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-07-28 | MONTH | 2 | PUT | 749 | 375 | 375 | 0 | 7 | 23950.0–24300.0 | True |
| 2026-08-04 | WEEK | 0 | CALL | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-08-04 | WEEK | 0 | PUT | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-08-04 | WEEK | 1 | CALL | 770 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |
| 2026-08-04 | WEEK | 1 | PUT | 770 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |
| 2026-08-04 | WEEK | 2 | CALL | 770 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |
| 2026-08-04 | WEEK | 2 | PUT | 770 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |
| 2026-08-04 | MONTH | 0 | CALL | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-08-04 | MONTH | 0 | PUT | 0 | 0 | 0 | 0 | 0 | n/a | False |
| 2026-08-04 | MONTH | 1 | CALL | 770 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |
| 2026-08-04 | MONTH | 1 | PUT | 770 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |
| 2026-08-04 | MONTH | 2 | CALL | 768 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |
| 2026-08-04 | MONTH | 2 | PUT | 770 | 385 | 375 | 10 | 5 | 24450.0–24650.0 | True |

## Interpretation

Recorded 16/24 probes. This compares rolling ATM strike-series metadata and counts; the endpoint does not establish the exact expiry date from these aggregates. Map target contracts independently before replay. Rolling ATM strikes are not absolute-strike history; no executable quote/depth data or profitability inference is available.

Only aggregate metadata is stored; raw market rows and credentials are not committed.
