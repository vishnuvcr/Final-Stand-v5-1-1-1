# Phase 90 Status

Date: 2026-10-10  
Status: **PASS — small incremental OOS IV magnitude-prediction gain beyond spot features and India VIX; not strategy evidence**  
Latest workflow run: [38048556674](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38048556674)  
Strategy promotion: **NONE**.

- [Research plan](PHASE90_RESEARCH_PLAN.md)
- [Error log](PHASE90_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE90_CHAT_LOG.md)
- [Engine](research/phase90/iv_incremental_study.py)
- [Workflow](.github/workflows/phase90-iv-incremental-prediction.yml)
- [Detailed results](results/phase90/PHASE90_RESULTS.md)
- [Summary JSON](results/phase90/summary.json)
- [Coverage ledger](results/phase90/coverage.csv)
- [Model metrics](results/phase90/model_metrics.csv)
- [VIX-regime metrics](results/phase90/vix_regime_metrics.csv)

## Primary conclusion
M1 MAE − M2 MAE = 0.0330 bps (paired session-cluster bootstrap 95% CI 0.0001 to 0.0562; bootstrap positive share 0.9750; 5000 resamples).

Complete OOS rows/sessions: 3604/60. Sample gate=PASS; India VIX gate=PASS. The Phase 83 2026 holdout remains sealed.

## Downstream replication checkpoint

Phase 91 has been registered on its own branch `phase-91-iv-temporal-replication-2023` with frozen 2023 DEV/validation/OOS splits. Draft PR [#41](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/41) is open and unmerged. A parent-branch PR runner is present at [.github/workflows/phase91-pr-runner.yml](.github/workflows/phase91-pr-runner.yml). At the last repository check, Phase 91 execution was not verified and its aggregate results were not published. This is not a change to Phase 90's result and no strategy is promoted.
