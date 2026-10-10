# Phase 65 — CCI option-data timestamp and contract-coverage audit

## Research question
Why did Phase 64's paper-derived CCI rules produce zero completed trades despite breakout triggers, and can the failure be explained by timestamp convention, sparse option-chain observations, or the frozen entry-window rule without changing the strategy?

## Frozen scope
- Inspect only the exact Phase 64 source revision and only option files corresponding to Phase 64 DEV/VAL monthly-expiry proxies (through 2025-12-31).
- No 2026 option files, no 2026 index features, no holdout analysis.
- No strategy P&L replays, no parameter search, no gate relaxation, no interpolation/forward fill, no synthesized prices.
- Do not treat a nearby timestamp as an executable fill. Nearest-timestamp comparisons are diagnostics only.
- Publish only aggregate timestamp-offset histograms, coverage counts, and reasons; no raw market data.

## Steps
1. Read the Phase 64 opportunity audit and pinned source manifest.
2. For each breakout event, compare underlying trigger timestamp, next-minute underlying timestamp, option timestamp coverage at the trigger and next minute, and the time delta to nearest observed option-chain timestamp.
3. Check minute-key conventions, timezone, duplicate/conflicting keys, option-side/strike availability, and whether the calendar-day 3–15 rule rejects a next-minute entry after a day-15 trigger.
4. Report exact coverage denominators and reasons, split DEV/VAL and candidate; never impute fills.
5. Unit-test timestamp alignment and timezone handling using synthetic rows.
6. Publish a diagnostic report and machine-readable JSON/CSV. Update status/logs/error log/README.
7. Stop after this diagnosis. Only a source-supported root cause may justify a separately preregistered correction phase.

## Decision gates
- PASS: source timestamp/coverage conventions are understood and exact observed-bar coverage is quantified.
- BLOCKED: data source cannot support exact trigger/entry pairing or lacks adequate observations.
- No candidate promotion in this phase, irrespective of findings.

## Deliverables
- PHASE65_RESEARCH_PLAN.md, PHASE65_STATUS.md, PHASE65_RESEARCH_LOG.md, PHASE65_ERROR_LOG.md, PHASE65_CHAT_LOG.md
- research/phase65_cci_data_coverage_audit.py and tests/test_phase65_coverage_audit.py
- results/phase65_cci_data_coverage_audit/aggregate_report.md and machine-readable aggregate outputs
- scheduled/manual GitHub Actions workflow; raw files stay in the runner/Hugging Face cache.

## Statistical methods
Descriptive counts and timestamp-offset distributions only. No inferential tests or P&L statistics because this phase diagnoses data coverage rather than strategy efficacy.

## Stopping rule
One complete diagnostic run. If source coverage remains inadequate, stop and retain NO-GO; do not repeat searches or loosen rules.
