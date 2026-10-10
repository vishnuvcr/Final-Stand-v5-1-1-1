# Phase 90 Chat / Decision Log

Date: 2026-10-10

## User request
User replied “Ok proceed” after Phase 89 recommended testing whether ATM IV adds value beyond baseline predictors and market-regime information.

## Prior repo state reviewed
- Read Phase 89 plan, status, error log, auditable decision log, results, engine, workflow and README.
- Phase 89 final run: [38047775690](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38047775690); status COMPLETE WITH DATA-COVERAGE CAVEAT, 25/26 option windows passed, one CALL window timed out.
- Phase 89's positive IV-magnitude association used 2025. That period will not be re-used as a Phase 90 confirmatory sample.
- Phase 83 2026 holdout remains sealed.

## Registered Phase 90 choices
1. Create a separate phase branch.
2. Use a distinct calendar-2024 Dhan sample.
3. Verify India VIX instrument ID from the official instrument master; model only an in-sample-fitted VIX baseline if its history and join pass the fixed quality gates.
4. Compare the frozen spot baseline, spot+VIX regime baseline, and spot+VIX+ATM-IV model.
5. Use DEV fit only (Jan–Jun), validation display only (Jul–Sep), and final OOS (Oct–Dec 2024); no tuning.
6. Primary endpoint is OOS MAE improvement from adding IV after VIX (M1 MAE − M2 MAE), with fixed-seed paired session-cluster bootstrap CI.
7. Publish only aggregate results and sanitized quality/error logs; no orders or strategy P&L replay.

## Execution
The initial 2024 study run [38048410498](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38048410498) and cached interpretation rerun [38048556674](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38048556674) both completed successfully. The cached rerun reused the same frozen data, model specification and OOS sample; it added explicit effect-size context, without tuning or expanding the study.

<!-- PHASE90_RUNTIME_START -->
## Automated execution record — 38048556674
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38048556674
- Status: PASS — small incremental OOS IV magnitude-prediction gain beyond spot features and India VIX; not strategy evidence
- VIX ID resolved dynamically: True
- Options valid chunks=54/54; VIX valid chunks=5/5
- OOS rows/sessions=3604/60
- Primary result: M1 MAE − M2 MAE = 0.0330 bps (paired session-cluster bootstrap 95% CI 0.0001 to 0.0562; bootstrap positive share 0.9750; 5000 resamples).
- Raw market responses were not printed, committed, or uploaded as artifacts; 2026 was not requested.
<!-- PHASE90_RUNTIME_END -->


## Downstream continuation — Phase 91 (2026-10-10)

Following the user's “Ok proceed” request after the Phase 90 result, Phase 91 was created on branch `phase-91-iv-temporal-replication-2023` to independently replicate the incremental IV prediction analysis on 2023 data. The child phase uses a separate cache and the same single primary endpoint, with a fixed 2023 OOS window. Draft PR [#41](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/41) is unmerged. The parent branch now contains a PR-triggered runner at [.github/workflows/phase91-pr-runner.yml](.github/workflows/phase91-pr-runner.yml). Execution is not yet verified; there is no numerical Phase 91 result to record. Phase 90 metrics remain unchanged.
