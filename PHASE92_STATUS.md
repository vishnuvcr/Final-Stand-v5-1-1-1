# Phase 92 Status

Date: 2026-10-10  
Status: **NEGATIVE INCREMENTAL VALUE — synthetic-forward/OI feature block worsens OOS magnitude prediction in this sample**  
Latest workflow run: [38051908021](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38051908021)  
Strategy promotion: **NONE**.

- [Research plan](PHASE92_RESEARCH_PLAN.md)
- [Error log](PHASE92_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE92_CHAT_LOG.md)
- [Engine](research/phase92/synthetic_forward_oi_study.py)
- [Phase branch workflow](.github/workflows/phase92-synthetic-forward-oi-2022.yml)
- [Default-branch runner + manual dispatch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/main/.github/workflows/phase92-pr-runner.yml)
- [Detailed results](results/phase92/PHASE92_RESULTS.md)
- [Research manuscript draft](results/phase92/MANUSCRIPT_DRAFT.md)
- [Supplementary materials](results/phase92/SUPPLEMENTARY_MATERIALS.md)
- [Cross-phase synthesis and stopping decision](results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md)
- [IV incremental effects figure](results/phase92/IV_INCREMENTAL_EFFECTS.svg)
- [OOS MAE comparison figure](results/phase92/OOS_MAE_COMPARISON.svg)
- [Summary JSON](results/phase92/summary.json)
- [Coverage ledger](results/phase92/coverage.csv)
- [Model metrics](results/phase92/model_metrics.csv)
- [Descriptive VIX-regime metrics](results/phase92/vix_regime_metrics.csv)

## Primary conclusion
M2 MAE − M4 MAE = -0.1708 bps (paired session-cluster bootstrap 95% CI -0.2299 to -0.1152; bootstrap positive share 0.0000; 5000 resamples; seed 90210).

Complete OOS rows/sessions: 3660/61. Sample gate=PASS; VIX gate=PASS. The Phase 83 2026 holdout remains sealed.

## Final manuscript quality check — 2026-10-10

- Latest acquisition/analysis/publication workflow: [38051908021 — success](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38051908021).
- Manuscript equation typography, abstract p-value punctuation, and references heading corrected in commit [cc764f9](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/cc764f98c17349fd4d8821495a39e5010521c592).
- Post-correction text scan found no known malformed equation fragments. This was documentation-only; the registered results are unchanged.
- Predictor programme remains at its finite Phase 92 stopping boundary. No strategy promoted; no Phase 83/2026 holdout access.
