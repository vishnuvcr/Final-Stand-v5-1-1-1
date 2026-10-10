# Phase 71 — DhanHQ bounded historical-options pilot

Decision: **BLOCKED_NO_DHAN_ACCESS_TOKEN**

Checked at UTC: 2026-10-10T08:18:06.753502+00:00

## Aggregate results

| Target session | Expiry flag | Side | Returned rows | Target-session rows | Decision |
|---|---|---:|---:|---:|---|

## Interpretation

The authenticated API probe was not run because repository secret DHAN_ACCESS_TOKEN is absent. No purchase was made. Configure the secret only after confirming an active DhanHQ Data API subscription and permitted research/data-retention terms.

No raw market rows or credentials are stored in this report. A passing target-date probe only confirms that some ATM-relative rows exist; it does not establish full-chain coverage, executable bid/ask fills, complete expiry mapping, or profitability.
