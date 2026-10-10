# Phase 56 status — prior-minute OI coverage diagnosis

**Overall:** COMPLETE — bounded source-row diagnosis passed; no strategy evaluation.

- Branch: `phase-56-prior-oi-coverage-diagnosis`
- Parent: Phase 55 complete selected-leg audit, 480 rows.
- Research target: 100 `BLOCKED_LEG_ELIGIBILITY` rows, all in validation split.
- Saved diagnostic reports 220 blocked leg references. Independent source inspection found exactly one row at every unique contract-time key and source-recorded OI=0 for all 60 unique keys; there were no missing or duplicate exact prior rows.
- Target partitions: 2025-03-13, 2025-07-31 and 2025-12-30 at pinned dataset revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`.
- Frozen rule: exact prior-minute timestamp and contract key, OI >= 100. No fallback or filter relaxation.
- Holdout untouched; no P&L or strategy promotion.

## Phase status
- Plan: FROZEN.
- Source diagnosis: PASS — 60/60 unique keys classified as ZERO_OI.
- Regression tests: PASS — six classification boundary cases.
- Results/log persistence: PASS — report, CSV, Markdown and phase checkpoint persisted.

## Run 38018825640

- Run: [38018825640](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38018825640); job status=success; diagnostic=PASS_SOURCE_ROW_DIAGNOSIS.
- Blocked rows=100; blocked leg references=220; unique exact keys=60.
- Classification counts={"ZERO_OI": 60}.
- Fixed OI >= 100 gate unchanged; no P&L, holdout use or strategy promotion.
\n## Final interpretation\n\nAll 60 unique expiry/timestamp/type/strike keys have exactly one matching source row in the pinned parquet files, and every row reports numeric open interest of zero. Those keys are referenced 220 times across the 100 blocked configuration-event rows. This resolves the immediate ambiguity: the source does not lack the exact prior-minute rows for these keys; it explicitly records OI=0. This does not prove the source's zero values perfectly represent exchange reality, but the frozen OI >= 100 gate correctly rejects them under the preregistered rule. No filter relaxation, P&L recalculation or strategy promotion.\n
## Run 38018882316

- Run: [38018882316](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38018882316); job status=success; diagnostic=PASS_SOURCE_ROW_DIAGNOSIS.
- Blocked rows=100; blocked leg references=220; unique exact keys=60.
- Classification counts={"ZERO_OI": 60}.
- Fixed OI >= 100 gate unchanged; no P&L, holdout use or strategy promotion.
