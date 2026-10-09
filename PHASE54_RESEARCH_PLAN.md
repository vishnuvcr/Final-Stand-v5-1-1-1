# Phase 54 research plan — OHLC-reference eligibility sensitivity

## Purpose and question
Quantify how the 480 frozen Phase 52 configuration-event rows respond to predeclared OHLC high-low/open thresholds while retaining strict prior-minute OI eligibility. Candle range is not bid/ask spread. This phase is a diagnostic coverage study, not a profitability backtest.

## Aims
1. Reconcile the exact Phase 52 event replay status counts.
2. Measure coverage at thresholds 2%, 3%, 4%, 5%, 6%, 8%, 10%, 12%, 15%, 20%, and 1000% (the last is a diagnostic near-removal of the range gate, not a proposed setting).
3. Preserve prior-minute OI >= 100 and the existing per-leg entry status.
4. Report qualified rows, shares, exclusions by reason and strategy family.
5. Fingerprint the exact input and pin the source revision.
6. Stop after this bounded analysis; do not proceed to executable replay without lawful, independent quote/OI evidence.

## Preregistered hypotheses
- H1: higher range thresholds increase rows passing the three diagnostic checks.
- H2: strict prior-minute OI failures remain unchanged across thresholds.
- H3: higher eligibility counts do not prove executable liquidity, valid exits, positive P&L or strategy superiority.

## Frozen rules and inputs
- Input: results/phase52/historical_pilot/event_replay.csv.
- Parent grid: phase52-grid-v1.3; 40 configurations × 24 selected events = 480 rows.
- Parent data revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- Each leg requires prior_oi_status=PASS and OI >= 100 at the exact prior minute, entry_status=PASS, a finite range proxy and max per-row leg range <= threshold.
- No changes to the grid, event universe, contracts, timestamp rules, exit rules, cost assumptions, source revision, or data split.
- No holdout use, raw-data download, P&L recalculation, strategy ranking or promotion.

## Methodology
1. Parse the committed CSV and each JSON leg payload.
2. Fail closed on missing input, empty rows or missing required columns.
3. At each threshold count rows passing all leg-level OI, entry-data and range conditions; report mutually exclusive rejection counts and family coverage.
4. Save JSON, CSV and Markdown with input SHA-256, parent revision and limitations.
5. Run unit tests and self-test in GitHub Actions; upload report artifacts and append checkpoint logs/README.
6. Review counts descriptively and close the phase. No broader replay is authorized.

## Statistical analysis
Descriptive counts and percentages only. No p-values, confidence intervals or performance claims: threshold variants are not independent samples and exits/fills are not recomputed.

## Acceptance criteria
- Reconcile all 480 rows and baseline status counts.
- Emit all 11 thresholds; eligible + OI/legs-rejected + entry-data-rejected + range-rejected must equal 480 for each threshold.
- OI-block count invariant across thresholds.
- Input fingerprint present; unit tests and self-test pass.
- Explicitly state candle range is not spread and eligibility is not profitability.
- Artifact and phase logs persist.

## Error handling
Log failures with run URL, exact step, root cause, correction, regression test and verification run. Never synthesize missing rows or force-push over concurrent logs.

## Status
Plan frozen; implementation committed; workflow execution and results pending verification. Live execution and strategy promotion are prohibited.
