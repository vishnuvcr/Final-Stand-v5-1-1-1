# Phase 54 research plan — OHLC-reference eligibility sensitivity

## Purpose
Quantify how the Phase 52 pilot's eligibility counts respond to different OHLC high-low/open thresholds, without representing candle range as bid/ask spread and without converting the exercise into a strategy backtest. This is a bounded diagnostic phase following Phase 53's no-go for a free independent historical quote/depth source.

## Research question
How sensitive are the 480 frozen configuration-event rows to the OHLC range-proxy threshold, after retaining the strictly prior-minute OI requirement and existing entry-data eligibility, and how much of the low coverage is caused by missing/zero OI?

## Aims and objectives
1. Reconcile baseline status counts from the exact Phase 52 event replay CSV.
2. Compute a predeclared threshold sensitivity at 2%, 3%, 4%, 5%, 6%, 8%, 10%, 12%, 15%, 20% and 1000% (the last is a diagnostic near-removal of the range gate, not a proposed setting).
3. Keep the prior-minute OI threshold at 100 and require each leg's existing entry-data status to be PASS.
4. Report eligible row counts by threshold, share of planned rows, excluded counts by reason and strategy family.
5. Hash the exact input and pin the parent data revision; keep raw source files out of the repo.
6. Stop after the sensitivity report and decide whether additional licensed quote/OI data is necessary before any executable replay.

## Preregistered hypotheses
- H1: relaxing the candle-range threshold will increase rows that pass the three diagnostic checks.
- H2: strict prior-minute OI failures will not change as the range threshold changes.
- H3: increased diagnostic eligibility alone will not establish executable liquidity, valid exits, positive P&L or superiority of any strategy.

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
1. Load the committed Phase 52 CSV with Python's CSV parser and parse the JSON leg payload.
2. Validate required columns, non-empty input and parseable leg arrays.
3. For each threshold, require all legs to have prior_oi_status=PASS, prior OI >= 100, entry_status=PASS, a finite range proxy and maximum per-row leg range <= threshold.
4. Count diagnostic eligible rows and rejected rows by OI/missing legs, entry-data status and range proxy. Group eligible rows by strategy family.
5. Emit machine-readable JSON, CSV and Markdown with the input SHA-256, source revision, frozen-rule flags and caveats.
6. Run unit tests and self-test in GitHub Actions; upload an artifact; persist status, research, error and chat logs plus README checkpoint.
7. Review results only as coverage sensitivity. If the OI block remains material or quote history remains absent, close this phase without a larger replay.

## Statistical analysis
This is descriptive coverage analysis, not a performance experiment. Report counts and percentages only. No p-values, confidence intervals, P&L estimates or inferential claims are appropriate because threshold variants are not independent samples and the required exit/fill evidence is not recomputed.

## Acceptance criteria
- 480 rows reconciled against parent status counts.
- All 11 thresholds emitted with mutually exclusive qualification/rejection categories summing to 480.
- Prior-OI blocked row count invariant across thresholds.
- Input fingerprint present and matches the exact committed CSV.
- Unit tests and self-test pass.
- Explicit warning that OHLC range is not spread and eligibility is not profitability.
- Workflow report artifact and checkpoint logs are persisted.

## Error handling
Any missing input, schema mismatch, malformed row or test failure is logged in PHASE54_ERROR_LOG.md; no synthetic rows or guessed data are permitted. If persistence races occur, rebase and retry; never force-push or discard concurrent logs.

## Phase status
- Plan: FROZEN.
- Implementation: committed.
- Automated run: pending/under verification.
- Scientific conclusion: pending actual workflow artifact.
- Promotion/live strategy: prohibited by this phase.
