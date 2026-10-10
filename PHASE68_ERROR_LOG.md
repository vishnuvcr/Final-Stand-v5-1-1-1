# Phase 68 Limitations Log

## E68-001 — Prior target-named files may contain stale data
Status: OPEN pending fresh byte-level validation. Earlier audits reported bytes ending 2026-07-02 despite filenames for 2026-07-28 and 2026-08-04. Validate actual timestamps, not filenames.

## E68-002 — OHLC is not execution-grade data
Status: OPEN. No bid/ask, depth, queue priority, or market-impact evidence. No execution-quality claim is allowed.

## E68-003 — Source license/completeness
Status: OPEN. Dataset card indicates CC-BY-NC-4.0. Do not redistribute raw data or imply exchange authorization.

## E68-004 — Timestamp timezone interpretation risk
- Status: RESOLVED in code before accepting runtime results.
- Risk: interpreting naive local-session timestamps as UTC would shift observations and misclassify exact-session coverage.
- Correction: naive timestamps are localized to Asia/Kolkata; already timezone-aware timestamps are converted to Asia/Kolkata.
- Verification: implementation commit exists; end-to-end workflow result remains pending, so the correction is not yet runtime-validated.

## E68-005 — Workflow execution not independently verified
- Status: OPEN.
- Impact: no target-date coverage conclusion can be accepted until aggregate output from a successful run is inspected.
- Mitigation: inspect the Phase 68 Actions run and repair any setup, authentication, schema or publication failure before proceeding.
