# Phase 91 Status

Date: 2026-10-10  
Status: **NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero**  
Latest workflow run: [38050932108](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050932108)  
Strategy promotion: **NONE**.

- [Research plan](PHASE91_RESEARCH_PLAN.md)
- [Error log](PHASE91_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE91_CHAT_LOG.md)
- [Engine](research/phase91/iv_incremental_study.py)
- [Phase branch workflow](.github/workflows/phase91-iv-temporal-replication-2023.yml)
- [Default-branch runner + manual dispatch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/main/.github/workflows/phase91-pr-runner.yml)
- [Detailed results](results/phase91/PHASE91_RESULTS.md)
- [Summary JSON](results/phase91/summary.json)
- [Coverage ledger](results/phase91/coverage.csv)
- [Model metrics](results/phase91/model_metrics.csv)
- [VIX-regime metrics](results/phase91/vix_regime_metrics.csv)

## Primary conclusion
M1 MAE − M2 MAE = 0.0001 bps (paired session-cluster bootstrap 95% CI -0.0111 to 0.0103; bootstrap positive share 0.5240; 5000 resamples).

Complete OOS rows/sessions: 3633/60. Sample gate=PASS; India VIX gate=PASS. The Phase 83 2026 holdout remains sealed.

## Downstream factor-screen checkpoint — Phase 92

Phase 92 completed on the independent 2022 sample in [run 38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106). The synthetic-forward proxy + OI block worsened OOS MAE relative to spot+VIX+IV: M2−M4 MAE = −0.1708363 bps, paired session-cluster 95% CI −0.2298769 to −0.1152015. All data/sample gates passed (54/54 options windows, 5/5 VIX, 3,660 OOS rows/61 sessions). See [Phase 92 detailed results](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-92-synthetic-forward-oi-study-2022/results/phase92/PHASE92_RESULTS.md) and [cross-phase synthesis](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-92-synthetic-forward-oi-study-2022/results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md). No strategy P&L was run and no strategy is promoted.
