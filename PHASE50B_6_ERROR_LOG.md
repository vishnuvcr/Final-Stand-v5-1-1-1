# Phase 50B-6 Error Log

No execution error has occurred in Phase 50B-6.

Pre-execution controls:
- OTM350 selection was frozen in Phase 50B-4 before validation/HOLD interpretation.
- BASE remains the fixed source-faithful comparator.
- 2026 HOLD is protected.
- No new strategy tuning is permitted.
- Statistical inference will operate at expiry/campaign level.

## 2026-10-09 — Error F50B6-001

Actions run 37851483949 stopped during the pre-inference pairing audit because the first implementation incorrectly required OTM350 and BASE to have identical exit timestamps. Exit timestamps are an outcome of the strategy geometry and are expected to differ; requiring identical exits would invalidate the treatment comparison. The correct paired unit is the common expiry/campaign block. The engine was therefore corrected to pair by exact common expiry membership and retain entry/exit/direction differences as treatment outcomes rather than integrity failures.
