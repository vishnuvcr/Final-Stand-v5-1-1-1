# Phase 54 research plan — OHLC-reference eligibility sensitivity

## Purpose
Determine whether the committed Phase 52 pilot output retains enough per-leg evidence to support a valid OHLC-reference threshold sensitivity. The first implementation showed that it does not: 373 rows have empty leg payloads and six range-excluded rows have only partial leg payloads. Threshold estimates are therefore blocked rather than imputed.

## Research question
Does the Phase 52 output preserve all selected legs for each configuration-event row, so alternate OHLC thresholds can be recalculated without inventing data? If not, what audit-schema repair is required?

## Aims and objectives
1. Reconcile baseline status counts from the exact Phase 52 event replay CSV.
2. Compute a predeclared threshold sensitivity at 2%, 3%, 4%, 5%, 6%, 8%, 10%, 12%, 15%, 20% and 1000% (the last is a diagnostic near-removal of the range gate, not a proposed setting).
3. Keep the prior-minute OI threshold at 100 and require each leg's existing entry-data status to be PASS.
4. Report eligible row counts by threshold, share of planned rows, excluded counts by reason and strategy family.
5. Hash the exact input and pin the parent data revision; keep raw source files out of the repo.
6. Stop after the sensitivity report and decide whether additional licensed quote/OI data is necessary before any executable replay.

## Preregistered hypotheses
- H1: sensitivity is computable only if each row includes all expected legs and the exact leg-level OHLC/OI evidence used for its status.
- H2: missing/partial leg payloads cannot be treated as OI failures or range passes.
- H3: eligibility counts alone cannot establish executable liquidity, valid exits, positive P&L or strategy superiority.

## Frozen inputs and rules
- Parent evidence: Phase 52 v0.2.1 audit-provenance output.
- Exact input: results/phase52/historical_pilot/event_replay.csv.
- Grid: phase52-grid-v1.3; 40 configurations × 24 selected events = 480 rows.
- Parent data revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- Strict prior-minute OI: OI >= 100 at the exact prior minute; do not use same-minute or future OI.
- Existing per-leg entry status must be PASS; no missing leg bars may be imputed.
- Threshold set: 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 1000 percent.
- No changes to grid, event universe, contracts, timestamp logic, exit logic, cost assumptions, source revision, splits or canonical Phase 52 result.
- No holdout use; no raw data download; no P&L or strategy ranking.

## Methodology
1. Load the committed Phase 52 CSV and parse its JSON leg payload.
2. Reconcile the 480 parent status rows: 100 blocked on OI eligibility, 379 excluded by range proxy, 1 replay pass.
3. Compare payload leg counts with expected leg counts by strategy family. Treat empty/partial payloads as unassessable, not as losses, OI failures or threshold passes.
4. Do not emit alternate-threshold eligibility numbers until complete per-leg OHLC/OI evidence is available for every row.
5. Emit JSON, CSV and Markdown with the input SHA-256, source revision, payload completeness counts and explicit blocker.
6. Run tests/self-test in Actions, upload artifact, and persist status/research/error/chat logs and README checkpoint.
7. Hand off to Phase 55: repair the parent audit output to retain all leg evidence, rerun the frozen pilot, then return to this sensitivity only if the output is complete.

## Statistical analysis
This is descriptive coverage analysis, not a performance experiment. Report counts and percentages only. No p-values, confidence intervals, P&L estimates or inferential claims are appropriate because threshold variants are not independent samples and the required exit/fill evidence is not recomputed.

## Acceptance criteria
- 480 rows reconcile to parent statuses.
- Every row is classified for complete, partial or empty leg payload.
- No alternative threshold counts are emitted while evidence is incomplete.
- Input fingerprint matches the exact committed CSV.
- Tests pass, artifact is uploaded and checkpoint logs persist.
- Explicit warning that OHLC range is not spread and eligibility is not profitability.

## Error handling
Any missing input, schema mismatch, malformed row or test failure is logged in PHASE54_ERROR_LOG.md; no synthetic rows or guessed data are permitted. If persistence races occur, rebase and retry; never force-push or discard concurrent logs.

## Phase status
- Plan: FROZEN.
- Implementation: committed.
- Automated run: pending/under verification.
- Scientific conclusion: threshold sensitivity is currently not computable; parent output is lossy. Phase 55 audit-schema repair required.
- Promotion/live strategy: prohibited by this phase.
