# Phase 91 Status

Date: 2026-10-10  
Status: **NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero**  
Latest workflow run: [38049302830](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38049302830)  
Strategy promotion: **NONE**.

- [Research plan](PHASE91_RESEARCH_PLAN.md)
- [Error log](PHASE91_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE91_CHAT_LOG.md)
- [Engine](research/phase91/iv_incremental_study.py)
- [Phase branch workflow](.github/workflows/phase91-iv-temporal-replication-2023.yml)
- [Default-branch PR runner + manual dispatch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/main/.github/workflows/phase91-pr-runner.yml)
- [Detailed results](results/phase91/PHASE91_RESULTS.md)
- [Cross-year synthesis and stopping decision](results/phase91/CROSS_YEAR_SYNTHESIS.md)
- [Summary JSON](results/phase91/summary.json)
- [Coverage ledger](results/phase91/coverage.csv)
- [Model metrics](results/phase91/model_metrics.csv)
- [VIX-regime metrics](results/phase91/vix_regime_metrics.csv)

## Primary conclusion
**No incremental gain established.** M1 MAE − M2 MAE = +0.0001111 bps (paired session-cluster bootstrap 95% CI −0.0110700 to +0.0102532; positive share 0.5240; 5,000 resamples, seed 90210). The interval crosses zero; this fails the preregistered decision rule.

Complete OOS rows/sessions: 3633/60. Sample gate=PASS; India VIX gate=PASS. The Phase 83 2026 holdout remains sealed.
