# Phase 91 Status

Date: 2026-10-10  
Status: **PREREGISTERED — execution not yet verified; no numerical Phase 91 result is available**  
Branch: `phase-91-iv-temporal-replication-2023`  
Draft PR: [#41](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/41)  
Strategy promotion: **NONE**.

- [Research plan](PHASE91_RESEARCH_PLAN.md)
- [Error log](PHASE91_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE91_CHAT_LOG.md)
- [Analysis engine](research/phase91/iv_incremental_study.py)
- [Phase branch workflow](.github/workflows/phase91-iv-temporal-replication-2023.yml)
- [PR-triggered fallback runner in the parent branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-90-iv-incremental-prediction/.github/workflows/phase91-pr-runner.yml)
- [Results report](results/phase91/PHASE91_RESULTS.md) — expected from a completed run

The research question is whether rolling ATM-relative mean IV adds out-of-sample prediction value for the next-15-minute absolute NIFTY spot move beyond lagged spot features and India VIX. Splits are fixed: DEV Jan–Jun 2023, report-only validation Jul–Sep, confirmatory OOS Oct–Dec. Phase 90's cache/data is not reused. Phase 89's 2025 data and Phase 83's protected 2026 holdout are excluded.

The generated results file and summary JSON were absent at the latest repository check, and available status checks did not surface an Actions run ID. This is a workflow-execution verification issue, **not** a positive or negative research result. Do not claim IV replication passed/failed or promote a strategy until an actual run and its coverage/sample gates are verified.

No strategy P&L, exact-contract execution replay, or live orders are in scope.
