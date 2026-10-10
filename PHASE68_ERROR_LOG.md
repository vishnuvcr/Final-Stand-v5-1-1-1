# Phase 68 Limitations Log

## E68-001 — Prior target-named files may contain stale data
Status: OPEN pending fresh byte-level validation. Earlier audits reported bytes ending 2026-07-02 despite filenames for 2026-07-28 and 2026-08-04. Validate actual timestamps, not filenames.

## E68-002 — OHLC is not execution-grade data
Status: OPEN. No bid/ask, depth, queue priority, or market-impact evidence. No execution-quality claim is allowed.

## E68-003 — Source license/completeness
Status: OPEN. Dataset card indicates CC-BY-NC-4.0. Do not redistribute raw data or imply exchange authorization.