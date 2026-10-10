# Phase 91 Chat / Decision Log

Date: 2026-10-10

## User request
User replied “Ok proceed” to continue the planned research following Phase 90.

## Prior repository state reviewed
- Read Phase 90 plan, status, error log, chat log, analysis engine, workflow and detailed results on `phase-90-iv-incremental-prediction`.
- Phase 90's latest cached interpretation run was [38048556674](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38048556674): 3,604 OOS rows / 60 sessions; M1 MAE − M2 MAE = +0.0330 bps, bootstrap 95% CI +0.0001 to +0.0562 bps.
- The estimate is small, its lower interval bound is near zero, and it is not strategy evidence.
- Confirmed guardrail: do not promote a strategy; keep Phase 83's 2026 holdout sealed.

## Decisions made for Phase 91
1. Create a new branch from the Phase 90 branch; keep Phase 91's data cache and outputs separate.
2. Conduct one temporal replication on 2023 data with the same three model families and one primary endpoint.
3. Fit Jan–Jun 2023 only, use Jul–Sep as report-only validation and Oct–Dec as confirmatory OOS.
4. Enforce the 2023 sample boundary through 2024-01-01 exclusive so 31 December is included but no 2024 observations enter the sample.
5. Require sample and VIX coverage gates; if failed, report inconclusive.
6. Publish sanitized aggregate results, error/status/chat logs and README checkpoint via the branch workflow.
7. No options strategy replay, transaction P&L inference, orders or strategy promotion in this phase.

## Execution log
- Created branch `phase-91-iv-temporal-replication-2023` from the Phase 90 branch.
- Added the preregistered plan, status, error log, decision log, isolated engine and workflow. Workflow commit: [c4d7ccdd6bdef1a1f8a6d0235bf2d9ae2abc52bf](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/c4d7ccdd6bdef1a1f8a6d0235bf2d9ae2abc52bf).
- Added official Dhan date-range semantics to the plan using the documentation's explicit non-inclusive `toDate` definition: https://dhanhq.co/docs/v2/expired-options-data/.
- Created [draft PR #41](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/41), targeting the Phase 90 branch; it remains unmerged.
- Updated the README with the Phase 91 checkpoint and links.
- Static review found and fixed a stale copied JSON metadata value (`phase: 90` → `phase: 91`) before any confirmed run; logged as E91-010.
- Added a PR-triggered fallback workflow in the Phase 90 parent branch to attempt automatic execution on PR synchronization. Latest repository checks still did not surface an Actions run ID or result files. This remains an execution-verification blocker; no statistical conclusion is available yet.
- The Phase 91 workflow contains `workflow_dispatch`, but availability of the UI's manual Run button is not confirmed because GitHub documents that a workflow must be present on the default branch for that button to be displayed. No workflow was claimed to have run.

Append the confirmed Actions run, actual data coverage and primary result when available. This is an auditable activity log, not a record of private reasoning.

<!-- PHASE91_RUNTIME_START -->
## Automated execution record — 38049302830
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38049302830
- Status: NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero
- VIX ID resolved dynamically: True
- Options valid chunks=54/54; VIX valid chunks=5/5
- OOS rows/sessions=3633/60
- Primary result: M1 MAE − M2 MAE = 0.0001 bps (paired session-cluster bootstrap 95% CI -0.0111 to 0.0103; bootstrap positive share 0.5240; 5000 resamples).
- Raw market responses were not printed, committed, or uploaded as artifacts; 2026 was not requested.
<!-- PHASE91_RUNTIME_END -->
