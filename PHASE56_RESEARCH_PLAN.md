# Phase 56 research plan — prior-minute OI coverage diagnosis

## Research question
For every unique option contract/timestamp responsible for Phase 52's 100 blocked configuration-event rows, does the pinned source contain exactly one prior-minute row, no row, duplicate rows, null OI, or a real numeric OI value below the fixed minimum?

## Aim
Resolve the ambiguity between absent exact prior-minute records and numeric zero/below-gate open interest without changing any Phase 52 eligibility rule or selecting outcomes.

## Frozen inputs and controls
- Parent: Phase 55 complete leg-audit ledger, 480 rows, pinned dataset revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`.
- Investigate only rows whose parent status is `BLOCKED_LEG_ELIGIBILITY`; do not select by P&L.
- Expected target expiry partitions: 2025-03-13, 2025-07-31, 2025-12-30. Validate exact file SHA-256 against the parent source audit.
- Strict prior timestamp remains exactly entry time minus one minute; exact expiry/type/strike matching only.
- Preserve the fixed OI >= 100 rule. No forward fill, interpolation, nearest timestamp/strike, or missing-value imputation.
- No P&L, strategy ranking, parameter tuning, holdout use, or promotion. Do not commit raw market data or print HF_TOKEN.

## Method
1. Parse the 480-row Phase 55 ledger and extract all selected legs from the 100 blocked rows.
2. Deduplicate the requested audit universe by exact expiry, prior timestamp, option type and strike.
3. Download only the three pinned expiry parquet partitions from the exact Hugging Face revision using the GitHub Actions cache and HF_TOKEN secret.
4. Normalize timestamps to Asia/Kolkata and numeric contract/OI columns using the same exact-key semantics as Phase 52.
5. For each key, count exact source rows before/after exact duplicate removal and classify as MISSING, DUPLICATE, NULL_OI, ZERO_OI, BELOW_GATE, or PASS. Compare observed OI to the saved pilot diagnostic without treating the saved status as source truth.
6. Validate expected partition hashes, key coverage and row-count reconciliation; write JSON, CSV and Markdown outputs with hashes and limitations.
7. Run regression tests and persist results/status/research/error/chat logs. Use a manual workflow_dispatch button and push trigger; never require the user to run Actions.

## Statistical analysis
Descriptive coverage counts only. No inferential statistics because this is a source-row diagnosis, not an efficacy sample.

## Acceptance criteria
- All target contracts from all 100 blocked rows are enumerated without outcome-based selection.
- Three pinned partition hashes match the accepted Phase 55 source audit.
- Every unique contract-time key receives an explicit source-row classification; any duplicate conflicts remain fail-closed.
- Source revision and exact timestamps are recorded; raw data remain outside the repository.
- Any source or parsing failure is logged; no silent missing-row substitution.
- Status and README clearly distinguish data coverage from strategy performance.

## Stop rule
Stop after this bounded three-partition diagnosis. If rows are missing or OI is below 100, report the exact reason and do not relax the gate. If all keys pass source validation, return the issue to Phase 52 for a separately preregistered replay design; do not rerun or promote within this phase.

## Status
Plan frozen before diagnostic run. No strategy performance has been tested by Phase 56.
