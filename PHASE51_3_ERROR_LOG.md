# Phase 51-3 Error Log

Rules:
- Every workflow/code failure must be recorded here with run ID, cause, correction, and whether the failed result is evidence.
- A green Actions conclusion is not a scientific pass unless source lineage, complete candidate universe and row-level gates also pass.
- Never promote or interpret an artifact from a failed gate.

## F51-3-001 — Actions dispatch unavailable — RESOLVED

- **Date:** 2026-10-09
- **Observation:** API-authored commits initially produced no workflow run for the phase branch or main orchestrator.
- **Correction:** Added a main-branch orchestrator with push/PR/manual triggers and an autonomous schedule. Run 37878089042 confirmed startup.
- **Status:** RESOLVED.

## F51-3-002 — TT-02 summary metadata exception — PATCHED

- **Runs:** 37878089042, 37879416000, 37879632246.
- **Root cause:** Missing `TT02_ENGINE_REV`.
- **Correction:** Defined the constant and masked invalid Newton divisions without changing valid updates.
- **Status:** PATCHED.

## F51-3-003 — Duplicate orchestration — CLOSED

- **Runs:** 37879416000 and 37879632246.
- **Cause:** Separate branch/main commits triggered overlapping runs.
- **Correction:** Finite completion marker and controlled main trigger.
- **Status:** CLOSED.

## F51-3-004 — Rejected alternative source / stale expiry universe — CORRECTED, REPLAY PENDING

- **Run:** 37879953815; artifact 11594226978.
- **Observation:** The inherited engines used `thetrademarkk/india-index-options-1m` through the Phase-43 loader and the old Phase-43 expiry matrix. Trade rows stopped around 2026-05-21 although the declared interval ended 2026-07-21.
- **Impact:** All P&L from that run is **REJECTED / NON-EVIDENCE**.
- **Correction:** Added `phase51_3_primary_source_adapter.py`, source hash/size checks, direct primary-source expiry derivation, validated spot-source acquisition/cache, and source-manifest audit checks.
- **Status:** CORRECTED; clean replay required.

## F51-3-005 — Primary-source adapter hardening

- **Date:** 2026-10-09
- **Observation:** Reusing frozen engines by changing only START/END was insufficient because their data loader and expiry dependencies remained bound to Phase-43.
- **Correction:** Monkey-patch only those dependencies to the frozen RISSIN options source and validated NIFTY spot source; retain all trading rules, cost functions, slippage and execution semantics. The main workflow now caches the spot source and audits its observed window.
- **Evidence status:** No results accepted yet; next run is the first source-faithful replay.
- **Status:** READY FOR REPLAY.


## F51-3-005 — Primary-source adapter hardening — READY FOR REPLAY

- **Date:** 2026-10-09
- **Observation:** Reusing the frozen engines by changing only START/END was insufficient because their data-loader and expiry dependencies remained bound to Phase-43.
- **Correction:** Added `research/phase51_3_primary_source_adapter.py` to inject the hash/size-locked RISSIN options source, validated NIFTY spot source, and expiry discovery from the primary options rows. Strategy rules, cost functions, slippage and execution semantics remain unchanged.
- **Workflow correction:** Main orchestrator now caches the validated spot repository and checks the primary-source manifest before accepting results.
- **Evidence status:** No Phase-51-3 P&L accepted yet.

## F51-3-006 — Redundant branch workflow lacks spot-source acquisition — CLOSED

- **Date:** 2026-10-09
- **Run:** 37881823544.
- **Observation:** The legacy phase-branch workflow fired on the adapter commit and failed because it does not contain the main orchestrator's validated-spot acquisition/cache step.
- **Impact:** No evidence was generated; this redundant workflow is not the authoritative Phase-51-3 execution path.
- **Correction:** The main orchestrator run 37881916446 contains the complete source-acquisition path and is the only run eligible for Phase-51-3 publication. The branch workflow will be prevented from creating duplicate scientific conclusions.
- **Status:** CLOSED as redundant-workflow noise; no P&L accepted.

## F51-3-007 — Spot-source path assumption — PATCHED

- **Date:** 2026-10-09
- **Run:** 37881916446.
- **Observation:** The source-faithful adapter was correct, but the orchestrator's acquisition step required the spot repository to have exactly `nifty/1min/2026`. The cloned repository's current layout did not satisfy that literal path, so the acquisition step stopped before replay acceptance.
- **Impact:** Run 37881916446 is non-evidence; its artifact is retained only for diagnostics.
- **Correction:** Spot-source discovery now searches recursively for 2026 1-minute CSVs, while the adapter applies the same recursive discovery. No spot values are transformed beyond the previously validated Timestamp/Close mapping.
- **Status:** PATCHED; clean source-faithful retry required.
