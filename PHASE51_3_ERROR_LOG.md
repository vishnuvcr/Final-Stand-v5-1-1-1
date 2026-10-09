# Phase 51-3 Error Log

Rules:
- Every workflow/code failure must be recorded here with run ID, cause, correction, and whether the failed result is evidence.
- Never promote or interpret an artifact from a failed gate.

## F51-3-001 — Actions dispatch unavailable — RESOLVED

- **Date:** 2026-10-09
- **Observation:** API-authored commits initially produced no workflow run for the phase branch or main orchestrator.
- **Impact:** Numerical sweep was delayed; no P&L evidence existed at that point.
- **Cause:** Available GitHub connector does not expose workflow dispatch.
- **Correction:** Added a main-branch orchestrator with push/PR/manual triggers and an autonomous schedule. Run 37878089042 confirmed the orchestrator starts successfully.
- **Status:** RESOLVED as an orchestration blocker.

## F51-3-002 — TT-02 summary metadata exception — PATCHED, POST-FIX RUN REQUIRED

- **Date:** 2026-10-09
- **Runs:** [37878089042](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37878089042), [37879416000](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879416000), [37879632246](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879632246)
- **Observation:** TT-02 failed while constructing the summary with `NameError: name 'TT02_ENGINE_REV' is not defined`. Run 37879632246 also uploaded the full diagnostic summary, but its job had checked out the phase branch before the metadata fix was committed.
- **Secondary implementation warning:** The Newton update used `np.where(good, sigma - diff/vega, sigma)`; NumPy evaluates `diff/vega` before choosing a branch, producing divide-by-zero/overflow warnings on invalid-vega elements. These warnings were not the cause of the NameError.
- **Impact:** The failed runs did not provide an accepted result artifact set. TT-04's 22/22 candidates, 100% coverage and zero row-level data errors, and TT-05's 17/20 candidates / 85% coverage, are diagnostic outputs only. No P&L is accepted from these failed runs.
- **Cause:** Missing TT-02 engine-revision constant; separate eager-division warning in the vectorized implementation.
- **Correction:** Added `TT02_ENGINE_REV = "50B-TT02-COVERAGE-V3"` in commit `a25c7eedb4b6f1d66374d09a1d0567ba30ec758b`. Replaced eager division with `np.divide(..., where=good)` in commit `e33a022b7601de71ea652e4f62bb9dd34f530168`, preserving valid positive-vega Newton updates. Wrapper now tags each candidate with coverage/data-error gates, prints all tracebacks, and preserves diagnostic artifacts on failure.
- **Status:** Code patch committed; a clean post-fix rerun is still required.

## F51-3-003 — Duplicate orchestration on one correction cycle — CLOSED

- **Date:** 2026-10-09
- **Runs:** Phase-branch workflow 37879416000 and main orchestrator 37879632246 were started by separate updates within the same correction cycle.
- **Impact:** Redundant compute was used; neither failed run is accepted evidence.
- **Cause:** The branch wrapper update triggered the branch workflow, while the main trigger-marker update triggered the orchestrator.
- **Correction:** Future diagnostic retries are initiated through the main marker after the code correction; the main orchestrator uses a finite completion marker to avoid recurring execution after success.
- **Status:** CLOSED for this one-time overlap; future evidence remains gated on a single accepted post-fix artifact set.
