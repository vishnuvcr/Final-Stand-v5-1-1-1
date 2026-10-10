# Phase 92 Status

Date: 2026-10-10  
Status: **NEGATIVE INCREMENTAL VALUE — synthetic-forward/OI feature block worsens OOS magnitude prediction in this sample**  
Latest workflow run: [38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106)  
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
- [IV incremental effects figure](results/phase92/IV_INCREMENTAL_EFFECTS.svg)
- [OOS MAE comparison figure](results/phase92/OOS_MAE_COMPARISON.svg)
- [Cross-phase factor synthesis and stopping decision](results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md)
- [Summary JSON](results/phase92/summary.json)
- [Coverage ledger](results/phase92/coverage.csv)
- [Model metrics](results/phase92/model_metrics.csv)
- [Descriptive VIX-regime metrics](results/phase92/vix_regime_metrics.csv)

## Primary conclusion
M2 MAE − M4 MAE = -0.1708 bps (paired session-cluster bootstrap 95% CI -0.2299 to -0.1152; bootstrap positive share 0.0000; 5000 resamples; seed 90210).

Complete OOS rows/sessions: 3,660/61. DEV and validation complete rows: 7,357/3,780. Sample gate=PASS; VIX gate=PASS; training gate=PASS. The Phase 83 2026 holdout remains sealed.

## Model comparison and decision

| OOS model | MAE (bps) | RMSE (bps) | R² |
|---|---:|---:|---:|
| M1 spot + VIX | 4.7987 | 6.6109 | 0.0693 |
| M2 spot + VIX + IV | 4.8214 | 6.6003 | 0.0723 |
| M3 plus synthetic-forward proxy | 4.8791 | 6.6208 | 0.0665 |
| M4 plus OI imbalance | 4.9922 | 6.6615 | 0.0550 |

The primary M2 MAE − M4 MAE was **−0.1708363 bps**, paired session-cluster bootstrap 95% CI **−0.2298769 to −0.1152015** (5,000 resamples, seed 90210). The CI is entirely below zero: the combined synthetic-forward/OI features worsen OOS magnitude prediction on this sample. No strategy was tested or promoted.

**Terminal Phase 92 decision:** close this fixed-sample factor-prediction screen at its registered stopping boundary. Do not search extra years or tune features for a positive outcome. Reopen only for a materially new preregistered hypothesis or authorized execution-grade exact-contract data. See the [cross-phase synthesis](results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md). [Cross-feature results](results/phase92/PHASE92_RESULTS.md) · [Coverage ledger](results/phase92/coverage.csv) · [Error log](PHASE92_ERROR_LOG.md).
