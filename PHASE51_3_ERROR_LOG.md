# Phase 51-3 Error Log

Rules:
- Every workflow/code failure must be recorded here with run ID, cause, correction, and whether the failed result is evidence.
- A green Actions conclusion is not a scientific pass unless source lineage, complete candidate universe and row-level gates also pass.
- Never promote or interpret an artifact from a failed gate.

## F51-3-001 — Actions dispatch unavailable — RESOLVED

- **Date:** 2026-10-09
- **Observation:** API-authored commits initially produced no workflow run for the phase branch or main orchestrator.
- **Impact:** Numerical sweep was delayed; no P&L evidence existed at that point.
- **Cause:** Available GitHub connector does not expose workflow dispatch.
- **Correction:** Added a main-branch orchestrator with push/PR/manual triggers and an autonomous schedule. Run 37878089042 confirmed the orchestrator starts successfully.
- **Status:** RESOLVED as an orchestration blocker.

## F51-3-002 — TT-02 summary metadata exception — PATCHED

- **Date:** 2026-10-09
- **Runs:** [37878089042](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37878089042), [37879416000](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879416000), [37879632246](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879632246)
- **Observation:** TT-02 failed while constructing the summary with `NameError: name 'TT02_ENGINE_REV' is not defined`.
- **Correction:** Added `TT02_ENGINE_REV = "50B-TT02-COVERAGE-V3"` and changed the volatility Newton update to masked division for valid-vega rows, preserving valid Newton updates and strategy rules.
- **Status:** PATCHED. The post-fix software workflow ran successfully, but its results were later rejected under F51-3-004 source lineage audit.

## F51-3-003 — Duplicate orchestration on one correction cycle — CLOSED

- **Date:** 2026-10-09
- **Runs:** Phase-branch workflow 37879416000 and main orchestrator 37879632246.
- **Cause:** Branch wrapper commit and main trigger-marker commit each triggered a run during the same correction cycle.
- **Correction:** A finite completion marker was added to stop scheduled retries after a completed workflow. The branch workflow's automatic push filters are now being narrowed so code commits do not start redundant replay runs.
- **Status:** CLOSED for the original overlap.

## F51-3-004 — Phase-51-3 replay used rejected alternative options source / stale expiry universe — CORRECTION IN PROGRESS

- **Date:** 2026-10-09
- **Run:** [37879953815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879953815), artifact ID 11594226978.
- **Observation:** The workflow passed its local software audit, but the inherited Phase-50B engines still imported `load_parquet` from `research/phase43_vix_strategy_sweep.py`, whose `HF_REPO` is `thetrademarkk/india-index-options-1m`. This source was rejected by Phase 51-1 for missing nominal 2026-07-28/2026-08-04 endpoint coverage and failed source-overlap checks. Engines also read expiries from the existing `results/phase43_vix/strategy_trade_matrix_all_splits.csv` rather than deriving the frozen window's opportunity universe from the primary RISSIN raw file.
- **Additional symptom:** Trades produced by the successful run stopped around 2026-05-21 even though the declared diagnostic window ended 2026-07-21. TT-02 had 5 trades and TT-04 had 22, with no rows near the end of the window. Their reported 100% local coverage measured only the visible/entered candidates, so it was not valid proof of opportunity coverage over the whole declared interval. TT-05's 85% local coverage was already below threshold; that result is also non-evidence because of source mismatch.
- **Impact:** All P&L from run 37879953815 is **REJECTED / NON-EVIDENCE**, regardless of the green workflow status. No strategy decision or inference is permitted from it.
- **Cause:** Reuse of a frozen replay engine without swapping its data-loader and expiry-registry dependencies to the Phase-51 frozen primary source; no endpoint/observed-trade-span assertion existed.
- **Correction:** Inject the frozen RISSIN raw options source `rissin/nse-options-intraday / upstox_intraday/NIFTY/NIFTY_2026.parquet` (expected SHA-256 `bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73`, 394,805,617 bytes), the hash-locked validated spot source `technovusin/nifty50-historical-data`, and an expiry schedule derived from observed primary-source expiries plus an explicit unavailable 2026-07-28 boundary. Add source manifest checks, candidate-span checks, TT-02 expected-expiry campaign denominator, trade/equity diagnostics, and rejected-run traceability; then rerun once through the main orchestrator.
- **Status:** OPEN until a new source-faithful run passes source and coverage gates.
