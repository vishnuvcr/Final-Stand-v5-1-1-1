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

Phase 91 has been registered on its own branch `phase-91-iv-temporal-replication-2023` with frozen 2023 DEV/validation/OOS splits. Draft PR [#41](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/41) is open and unmerged. A parent-branch PR runner is present at [.github/workflows/phase91-pr-runner.yml](.github/workflows/phase91-pr-runner.yml). Phase 91 completed successfully in [Actions run 38050932108](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050932108): 54/54 options windows, 5/5 VIX windows, 3,633 OOS rows / 60 sessions. The primary MAE improvement was +0.0001111 bps with 95% CI −0.0110700 to +0.0102532, so incremental gain was not established. See [Phase 91 report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-91-iv-temporal-replication-2023/results/phase91/PHASE91_RESULTS.md) · [cross-year synthesis](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-91-iv-temporal-replication-2023/results/phase91/CROSS_YEAR_SYNTHESIS.md). This does not change the 2024 Phase 90 estimate; no strategy is promoted.

## Subsequent factor-screen checkpoint — Phase 92

Phase 92 completed on a distinct calendar-2022 sample in [run 38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106). After spot+VIX+IV, adding a lagged synthetic-forward proxy gap and CE/PE OI imbalance worsened OOS MAE: M2−M4 = −0.1708363 bps; paired session-cluster 95% CI −0.2298769 to −0.1152015. Coverage and sample gates passed. The rolling-ATM IV/synthetic-proxy/OI predictor screen is closed at its Phase 92 stop boundary; see [cross-phase synthesis](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-92-synthetic-forward-oi-study-2022/results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md). No strategy is promoted.
