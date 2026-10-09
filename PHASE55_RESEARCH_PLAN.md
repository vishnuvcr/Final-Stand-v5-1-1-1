# Phase 55 research plan — complete leg-audit payload repair

## Problem statement
Phase 54 discovered that the frozen Phase 52 event replay output is lossy for exclusions: out of 480 rows, the parent status counts reconcile to 100 OI eligibility blocks, 379 OHLC range exclusions and one replay pass, but many excluded rows do not retain all selected legs. A sensitivity analysis cannot safely recompute alternate thresholds from an empty or partial payload.

## Research question
Can the Phase 52 runner preserve the full selected strategy leg list, including per-leg entry, strictly prior-minute OI, OHLC range and exact 15:15 exit status, for every row that reaches leg-level replay, including early exclusions?

## Scope
- Keep the same frozen 40 configurations × 24 events (480 rows), event universe, configuration grid, data revision, prior-minute OI >= 100 rule, canonical 2% OHLC range proxy, exact 15:15 exit, and six transaction-cost/slippage scenarios.
- Repair audit serialization only; do not optimize strategies or change gate thresholds.
- Every selected leg must be represented before any per-leg gate can return. The row should include NOT_TESTED/MISSING/DUPLICATE/PASS/EXCLUDED states where appropriate rather than omitting later legs.
- After replay, assert that every post-resolution row status has the expected number of unique leg IDs by family.
- Keep raw market data out of the repository. Use the pinned HF revision and a GitHub Actions cache for repeated runs, without printing HF_TOKEN.
- No holdout selection or promotion. The run is an engineering/data-audit rerun, not an efficacy study.

## Expected leg count
- BUY_CALL: 1
- BUY_PUT: 1
- BULL_CALL_SPREAD: 2
- BEAR_CALL_SPREAD: 2
- SHORT_IRON_CONDOR: 4
- LONG_STRADDLE: 2
- LONG_STRANGLE: 2

## Methodology
1. Add a helper that creates an audit skeleton for every resolved strategy leg before gate evaluation.
2. Evaluate all selected legs instead of returning at the first leg failure. Capture exact entry, prior-minute OI, OHLC range and exit results for every leg where data is available; retain explicit NOT_TESTED reasons where upstream data prevents evaluation.
3. Select the first deterministic exclusion reason for the row, but preserve all leg outcomes in the payload.
4. Add a fail-closed invariant validating expected leg count and unique leg IDs for all leg-level statuses.
5. Run syntax validation, unit tests and runner self-tests.
6. Rerun the same frozen historical pilot with the same pinned revision; use GitHub Actions cache keyed by the revision for Hugging Face files.
7. Verify 480 rows, status counts, leg payload completeness, six cost rows per replay pass, source hashes and no exceptions. Compare statuses to the parent run and explain any changes; do not rank strategy performance.
8. If the audit invariant fails, stop before accepting outputs and log the failing rows. Do not weaken the invariant to get a green run.

## Acceptance criteria
- Unit tests pass for all expected family leg counts and serialized complete payloads.
- Runner self-test passes.
- Actual rerun uses the pinned revision and all 480 rows.
- Every post-resolution status preserves the expected number of unique leg IDs.
- Baseline status counts and cost rows are reported; any differences are explicitly reconciled.
- No holdout use, no raw data committed, no strategy promotion.
- Artifact, status, research log, error log, chat summary and README checkpoint are persisted.

## Statistical analysis
None. This is audit-pipeline engineering and coverage validation, not a profitability test. No p-values or strategy efficacy claims.

## Status
**COMPLETE** — workflow [37993968572](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37993968572) passed syntax validation, regression tests, self-test, the 480-row rerun, all-leg invariant audit, artifact upload and log persistence. The persisted audit confirms exactly 480 rows, all 480 selected-leg payloads complete by family, and six cost rows for the single replay-pass row. Source revision and frozen study design are unchanged.
