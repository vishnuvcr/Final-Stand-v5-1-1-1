# Phase 91 Status

Date: 2026-10-10  
Status: **NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero**  
Latest workflow run: [38050576808](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050576808)  
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
