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
Pending automated GitHub Actions run.
