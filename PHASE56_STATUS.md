# Phase 56 status — prior-minute OI coverage diagnosis

**Overall:** ACTIVE — bounded source-row audit; no strategy evaluation.

- Branch: `phase-56-prior-oi-coverage-diagnosis`
- Parent: Phase 55 complete selected-leg audit, 480 rows.
- Research target: 100 `BLOCKED_LEG_ELIGIBILITY` rows, all in validation split.
- Saved diagnostic reports 220 leg records with `prior_oi=0` / `prior_oi_status=FAIL`; the audit must independently determine whether exact source rows are absent, duplicated, null, zero or below the fixed threshold.
- Target partitions: 2025-03-13, 2025-07-31 and 2025-12-30 at pinned dataset revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`.
- Frozen rule: exact prior-minute timestamp and contract key, OI >= 100. No fallback or filter relaxation.
- Holdout untouched; no P&L or strategy promotion.

## Phase status
- Plan: FROZEN.
- Source diagnosis: PENDING.
- Regression tests: PENDING.
- Results/log persistence: PENDING.

## Run 38018825640

- Run: [38018825640](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38018825640); job status=success; diagnostic=PASS_SOURCE_ROW_DIAGNOSIS.
- Blocked rows=100; blocked leg references=220; unique exact keys=60.
- Classification counts={"ZERO_OI": 60}.
- Fixed OI >= 100 gate unchanged; no P&L, holdout use or strategy promotion.
