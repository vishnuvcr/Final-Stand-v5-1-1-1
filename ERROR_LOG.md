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
