# Phase 71 — DhanHQ bounded historical-options pilot

Decision: **PILOT_TARGET_ROWS_FOUND**

Checked at UTC: 2026-10-10T09:32:16.653172+00:00

## Aggregate results

| Target session | Expiry flag | Side | Returned rows | Target-session rows | Decision |
|---|---|---:|---:|---:|---|
| 2026-07-28 | WEEK | CALL | 750 | 375 | ROWS_FOUND |
| 2026-07-28 | WEEK | PUT | 750 | 375 | ROWS_FOUND |
| 2026-07-28 | MONTH | CALL | 750 | 375 | ROWS_FOUND |
| 2026-07-28 | MONTH | PUT | 750 | 375 | ROWS_FOUND |
| 2026-08-04 | WEEK | CALL | 770 | 385 | ROWS_FOUND |
| 2026-08-04 | WEEK | PUT | 770 | 385 | ROWS_FOUND |
| 2026-08-04 | MONTH | CALL | 770 | 385 | ROWS_FOUND |
| 2026-08-04 | MONTH | PUT | 770 | 385 | ROWS_FOUND |

## Interpretation

At least one configured ATM-relative probe returned target-session rows. Inspect per-probe coverage and expiry-code semantics before expanding the pull.

No raw market rows or credentials are stored in this report. A passing target-date probe only confirms that some ATM-relative rows exist; it does not establish full-chain coverage, executable bid/ask fills, complete expiry mapping, or profitability.
