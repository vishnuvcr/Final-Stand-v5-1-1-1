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

## F51-3-004 — Rejected alternative source / stale expiry universe — CORRECTED

- **Run:** 37879953815; artifact 11594226978.
- **Observation:** The inherited engines used `thetrademarkk/india-index-options-1m` through the Phase-43 loader and the old Phase-43 expiry matrix. Trade rows stopped around 2026-05-21 although the declared interval ended 2026-07-21.
- **Impact:** All P&L from that run is **REJECTED / NON-EVIDENCE**.
- **Correction:** Added `phase51_3_primary_source_adapter.py`, source hash/size checks, direct primary-source expiry derivation, validated spot-source acquisition/cache, and source-manifest audit checks.
- **Status:** CORRECTED; authoritative replay passed on run 37882057283.

## F51-3-005 — Primary-source adapter hardening — VERIFIED

- **Date:** 2026-10-09
- **Observation:** Reusing frozen engines by changing only START/END was insufficient because their data loader and expiry dependencies remained bound to Phase-43.
- **Correction:** Adapter injects the hash/size-locked RISSIN options source, validated NIFTY spot source, and expiry discovery from primary options rows. Strategy rules, cost functions, slippage and execution semantics remain unchanged.
- **Verification:** Run 37882057283 passed the source-manifest checks; 23,625 spot observations cover 2026-04-21 09:15 through 2026-07-21 15:29 IST; 14 weekly expiry dates are observed from the primary options source.
- **Status:** VERIFIED.

## F51-3-006 — Redundant branch workflow lacks spot-source acquisition — CLOSED

- **Date:** 2026-10-09
- **Run:** 37881823544.
- **Observation:** The legacy phase-branch workflow fired on the adapter commit and failed because it does not contain the main orchestrator's validated-spot acquisition/cache step.
- **Impact:** No evidence was generated; the redundant workflow is not the authoritative Phase-51-3 execution path.
- **Correction:** Removed its push trigger; manual dispatch remains available. Main orchestrator is authoritative.
- **Status:** CLOSED.

## F51-3-007 — Spot-source path assumption — PATCHED AND VERIFIED

- **Date:** 2026-10-09
- **Run:** 37881916446 (failed before replay acceptance).
- **Observation:** Acquisition expected a literal `nifty/1min/2026` path, but repository layout differed.
- **Impact:** Run 37881916446 is non-evidence.
- **Correction:** Recursive discovery searches for 2026 1-minute CSV files.
- **Verification:** Run 37882057283 acquired/cached the source and passed the source-manifest audit.
- **Status:** PATCHED AND VERIFIED.

## F51-3-008 — Source-faithful replay result / finite diagnostic closure — PASS_AVAILABLE_OOS

- **Date:** 2026-10-09
- **Authoritative run:** [37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283); artifact 11594572803.
- **Checks:** Source repo/file/hash/size matched preregistration; spot observations span the declared interval; expiry list is derived from primary option rows; expected eligible candidates exactly TT02, TT04, TT05; no candidate errors; all three have 100% recorded execution coverage and zero row-level data errors.
- **Results:** TT-02 net -₹1,341.12 at ₹10/order; TT-04 +₹13,271.51; TT-05 +₹17,098.15. All remain partial-window descriptive results only. Cost and +50% friction scenarios are published in the sweep summary.
- **Interpretation restriction:** No strategy is promoted. This finite diagnostic is not the final full Phase-51 OOS because 2026-07-28 and 2026-08-04 option blocks remain missing.
- **Status:** CLOSED FOR PHASE 51-3; full Phase-51 data gate remains open.
