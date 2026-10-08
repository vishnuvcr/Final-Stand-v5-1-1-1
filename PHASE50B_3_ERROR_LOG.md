# Phase 50B-3 Error Log

## 2026-10-09 — Initialization

No execution error has occurred in Phase 50B-3 yet.

Pre-execution controls:
- only TT-02/03/04/05 are admitted;
- TT-06/07 terminal FAIL_COVERAGE results are excluded;
- all 28 strategy×VIX hypotheses are frozen before the new conditioning run;
- VIX is reconstructed from entry timestamps;
- 2026 HOLD is descriptive only;
- no post-result VIX threshold or regime selection is permitted.

Any subsequent workflow or data-quality defect will be appended here and classified as evidence-impacting or non-evidence before correction.

## 2026-10-09 — Error F50B3-001: workflow cancelled by concurrent documentation commit

Affected run: 37848475527.

The replay was cancelled while dependency installation was in progress because the workflow used cancel-in-progress=true and a routine phase-log commit triggered a replacement run. No scientific evidence was produced or lost.

Correction: cancel-in-progress is now false. Routine documentation commits cannot cancel an active Phase 50B-3 replay.
