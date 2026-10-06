# Phase 36 Status — Independent Per-Trade Direction Selector Overlay

## Final state
**COMPLETE — REJECTED — NO LIVE-TRADING PROMOTION**

The previous trade's status/P&L/direction remains part of the Continuous Delta 6x6 direction mechanism. Removing that state and using an independent selector before every new trade worsened net performance and holdout robustness.

### Accepted final evidence
- GitHub Actions run: 37428502722 (#4)
- corrected source revision: c8963bcded49ae15cf5b059394f3471ec1c3f2a4
- all seven selector jobs: success
- publish job: success
- per-selector numerical artifacts persisted in the repository

### Primary sample
2024-01-01 through 2026-06-30; 128 expected expiries, 104 available files, 1 incomplete file, 103 processed expiries.

### Final result
Stateful control: +₹63,672.58 net, PF 1.203, max DD ₹61,960.87.

Best independent selector: OTM789_FRESH at -₹39,122.38 net, PF 0.898, max DD ₹102,707.29.

All seven independent selectors were negative over the primary sample and all seven were negative in the 2026 holdout.

### Control-relative bootstrap
All seven selector-minus-control mean expiry-P&L intervals were entirely below zero.

### Error history
- F36-001: mixed skip-record widths; corrected.
- F36-002: duplicate quote rows in fresh selectors; corrected.
- Final corrective run #4: successful.

### Final recommendation
Retain the Phase-32 stateful direction rule. Do not promote any Phase-36 selector.

Next priority: forward/paper validation of the canonical stateful strategy with full execution realism, not additional selector hunting.


## Final accepted run — 37428502722
All seven selector jobs and the artifact-publication job completed successfully. No numerical implementation error remained in the accepted evidence.

## Error F36-003 — Final artifact-manifest blob mapping
The first final-research commit mapped several prepared content blobs to the wrong filenames. The numerical evidence was unaffected, but the repository manifest was incorrect. The files are being repaired and verified individually.

**Evidence status:** packaging-only, non-evidence.

**Prevention:** verify file headers/content against expected artifact type before closing a research phase.


## Error F36-004 — Invalid workflow content during artifact-manifest repair
**Runs:** 37429445210, 37429450459, 37429454606, 37429458477, 37429477965, 37429482697, 37429486634.

**Cause:** During repair of the final artifact-manifest mapping, the workflow file temporarily contained the error-log content. Documentation/result-file update commits triggered the broad `PHASE36_**` path filter, and GitHub therefore attempted several invalid workflow runs.

**Evidence status:** CI/packaging-only. No numerical evidence was produced or accepted by these runs.

**Correction:** Restored the executable Phase-36 workflow and narrowed push triggers to the research source/cache/workflow and preregistration files only.

**Prevention:** Verify workflow file type/content before making any commit that can trigger Actions; do not use broad documentation globs for numerical research workflows.
