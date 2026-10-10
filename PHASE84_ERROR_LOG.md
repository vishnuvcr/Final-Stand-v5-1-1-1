# Phase 84 Error Log

Date: 2026-10-10

| ID | Severity | Issue | Resolution/status |
|---|---|---|---|
| E84-001 | INFO | Default-branch README checkpoint lagged the Phase 83 closeout and still emphasized Phase 67. | Phase 84 is based directly on the verified Phase 83 branch; the README checkpoint is updated on the Phase 84 branch. It is not merged into the default branch. |
| E84-002 | GUARDRAIL | Different studies use different samples, strategies and cost assumptions, so a single raw-P&L ranking would be misleading. | Keep evidence strata separate and prohibit cross-study profit ranking without normalization. |
| E84-003 | GUARDRAIL | Phase 83 explicitly closed its registered experiment and sealed the 2026 holdout. | Phase 84 is synthesis-only; no holdout access or new strategy test. |
| E84-004 | LOW / RESOLVED | Initial evidence-matrix source reference used a nonexistent Phase 66 branch name; repository fetch returned 404. | Verified the report exists on `phase-66-ohcl-paper-replication`; corrected the matrix reference. No numeric result was changed. |
| E84-005 | LOW / RESOLVED | First validation run 38046328622 failed because the Phase 66 CSV row had one fewer field than the declared header; the validator identified an empty `next_action`. | Added the missing inference-status field and restored all 11 columns. Rerun required. |\n| E84-006 | INFO / PENDING | Corrected validation rerun has not yet been inspected. | Keep Phase 84 status pending until a successful run is confirmed. |

Add every further reproducible error or inconsistency with its impact and resolution. Do not log hidden chain-of-thought or private internal reasoning; retain auditable actions and decisions only.
