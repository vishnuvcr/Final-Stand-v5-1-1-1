# Phase 79 — Current-revision fixed-contract source recheck
Date: 2026-10-10
Status: PLAN FROZEN

## Research question
Have updates to the Hugging Face dataset since the pinned Phase 76 revision filled the two previously missing NIFTY expiry sessions (2026-07-28 and 2026-08-04) with explicit expiry/strike/side identity and usable regular-session minute coverage?

## Rationale
Phase 76 audited pinned revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5` and found the two named files stale. Public dataset listings now show newer commits, so the source must be rechecked before finalizing the data no-go.

## Method
1. Use `HF_TOKEN` only as a GitHub Actions secret; never print or persist it.
2. Download only the two target Parquet files from the current dataset revision into the ephemeral runner.
3. Filter using explicit `expiry` field; inspect timestamps on each target expiry date.
4. Count regular-session minutes (09:15–15:29 IST), unique contract-side-strike groups, complete 375-minute groups, and null/invalid identity fields.
5. Emit aggregate metadata only: revision, row counts, date spans, coverage counts, hashes, and decision. Never commit raw Parquet.
6. If expiry-day coverage is valid, still require legal/retention review and quote/execution-quality checks before replay. OHLC bars alone are not proof of executable fills.

## Decision gates
- `CURRENT_SOURCE_COVERS_TARGETS`: both expiry dates present and at least one explicit expiry/strike/option-side contract has 375 unique regular-session bars per date.
- `BLOCKED_CURRENT_SOURCE_INCOMPLETE`: either date fails the gate.
- `BLOCKED_SOURCE_ACCESS_OR_SCHEMA`: access, schema, or integrity fails.

## Boundaries
No strategy tuning, no synthetic prices, no purchase, no raw data committed, and no strategy promotion in this phase. Missing dates remain excluded until the gate passes.
