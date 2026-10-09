# Phase 51-3 Error Log

Rules:
- Every workflow/code failure must be recorded here with run ID, cause, correction, and whether the failed result is evidence.
- Never promote or interpret an artifact from a failed gate.

## F51-3-001 — Actions dispatch unavailable

- **Date:** 2026-10-09
- **Observation:** API-authored commits initially produced no workflow run for the phase branch or main orchestrator.
- **Impact:** Numerical sweep was delayed; no P&L evidence existed at that point.
- **Cause:** Available GitHub connector does not expose workflow dispatch.
- **Correction:** Added a main-branch orchestrator with push/PR/manual triggers and an autonomous schedule. Run 37878089042 confirmed the orchestrator starts successfully.
- **Status:** RESOLVED as an orchestration blocker; current execution issue is F51-3-002.

## F51-3-002 — TT-02 candidate engine failure; traceback suppressed

- **Date:** 2026-10-09
- **Run:** [GitHub Actions 37878089042](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37878089042)
- **Observation:** The Phase-51-3 wrapper ran candidate slots, but TT-02 raised an exception. The initial wrapper recorded a Python traceback only in the temporary sweep summary but printed a generic failure message; the workflow audit/upload steps were skipped after the non-zero exit, so no artifact was retained. The visible log also contained repeated divide-by-zero/overflow warnings at the frozen TT-02 implied-volatility Newton step.
- **Secondary gate observation:** TT-05 logged 17 completed trades from 20 candidates (85% coverage), below the preregistered >=95% threshold. This is a candidate quality-gate failure, not permission to discard missing opportunities or report it as eligible evidence.
- **Impact:** The workflow failed and generated no accepted/published result artifact. All metrics emitted by that attempt remain **NON-EVIDENCE**; no P&L inference or candidate promotion is allowed.
- **Cause:** Exact TT-02 exception is unresolved because the initial wrapper suppressed the captured traceback. Runtime numerical warnings are observed but are not yet proven to be the terminating exception.
- **Correction:** Updated the wrapper to print and store full tracebacks, classify each candidate's coverage and row-level data-error gate, and configured audit/artifact steps to run despite a prior step failure. The next retry should retain a diagnostic artifact for exact diagnosis.
- **Status:** RETRY_PENDING; not a scientific result and not a strategy rejection.
