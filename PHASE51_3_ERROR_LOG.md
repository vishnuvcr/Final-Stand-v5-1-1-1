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

## F51-3-002 — TT-02 summary metadata exception — PATCHED, RETRY PENDING

- **Date:** 2026-10-09
- **Runs:** [37878089042](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37878089042), [37879416000](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879416000)
- **Observation:** TT-02 completed the replay loop but failed while constructing the summary with `NameError: name 'TT02_ENGINE_REV' is not defined`. The exact traceback became visible after the wrapper was patched to print and persist exception details.
- **Secondary implementation warning:** The Newton update used `np.where(good, sigma - diff/vega, sigma)`; NumPy evaluates `diff/vega` before choosing the branch, producing divide-by-zero/overflow warnings on invalid-vega elements. These warnings were not proven to cause the NameError.
- **Impact:** The failing runs produced no accepted/published artifact. TT-04's 22/22 trades, 100% coverage, zero row-level data errors, and TT-05's 17/20 trades / 85% coverage are diagnostic console outputs only. No P&L is accepted from the failed run.
- **Cause:** Missing TT-02 engine-revision constant; separate eager-divide warning in the vectorized implementation.
- **Correction:** Added `TT02_ENGINE_REV = "50B-TT02-COVERAGE-V3"`. Replaced the eager division with `np.divide(..., where=good)`, leaving valid-v ega Newton updates unchanged. The wrapper now tags every candidate with a coverage/data-error gate, prints all tracebacks, and preserves artifacts on failure.
- **Status:** PATCHED; clean rerun still required.

## F51-3-003 — Duplicate orchestration on one correction cycle — CLOSED

- **Date:** 2026-10-09
- **Runs:** Phase-branch workflow 37879416000 and main orchestrator 37879632246 were started by separate updates within the same correction cycle.
- **Impact:** Redundant compute was used; there was no accepted result from the failed phase-branch run.
- **Cause:** The branch wrapper update triggered the branch workflow, while the main trigger-marker update triggered the orchestrator.
- **Correction:** Future diagnostic retries are initiated through the main marker after the code correction; the main orchestrator uses a finite completion marker to avoid recurring execution after success.
- **Status:** CLOSED for this one-time overlap; future published evidence remains gated on a single accepted artifact set.
