# Phase 90 Status

Date: 2026-10-10  
Status: PREREGISTERED — corrected independent-year IV incremental-value study pending automated run.  
Decision: no strategy promotion; the study is not an options P&L replay.

## Phase 89 motivation (not reused as Phase 90 OOS)
Phase 89's 2025 Dhan rolling-options study found a small positive mean-ATM-IV association with next-15-minute absolute spot move (beta +0.602 bps per feature SD, Holm p=0.0071), but a feature association is not incremental predictive value. Phase 90 uses a separate calendar-2024 Dhan sample and tests IV only after a frozen spot-movement + India VIX baseline.

## Preregistered outputs
- [Research plan](PHASE90_RESEARCH_PLAN.md)
- [Workflow](.github/workflows/phase90-iv-incremental-prediction.yml)
- [Engine](research/phase90/iv_incremental_study.py)
- [Error log](PHASE90_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE90_CHAT_LOG.md)
- [Detailed results](results/phase90/PHASE90_RESULTS.md)
- [Primary result JSON](results/phase90/summary.json)
- [Coverage ledger](results/phase90/coverage.csv)
- [Model metrics](results/phase90/model_metrics.csv)
- [OOS VIX-regime descriptive metrics](results/phase90/vix_regime_metrics.csv)

## Runtime result
Pending. Phase 89's 2025 sample and all 2026 Phase 83 holdout data are excluded from Phase 90 analysis.
