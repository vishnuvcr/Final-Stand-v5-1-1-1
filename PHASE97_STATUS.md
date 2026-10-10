# Phase 97 Status — ML Options Strategy Replication

**Updated:** 2026-10-10  
**Branch:** `phase-97-ml-options-strategy-replication`  
**Status:** PLAN REGISTERED; source-data gate pending  
**Strategy promotion:** NONE

## Scope
Sherasiya ML options strategy: Random Forest, XGBoost, LSTM, option Greeks/IV/underlying features and basic-momentum comparator.

## Required gate
Exact-contract identity, point-in-time feature/label alignment, source provenance, and executable quote/fill fields. Rolling ATM-relative coverage alone is not sufficient.

## Pending
- Audit Phase 85 source qualification, Phase 89 coverage evidence, and Phase 94 method register.
- Publish a field-by-field data gate, explicit blocked/partial statuses and a bounded result.
- Train models only if eligible real labels/features pass the gate.
- Update logs and README; do not access the 2026 holdout.

## Records
- [Plan](PHASE97_RESEARCH_PLAN.md)
- [Research log](PHASE97_RESEARCH_LOG.md)
- [Error/limitation log](PHASE97_ERROR_LOG.md)
- [Decision/chat log](PHASE97_CHAT_LOG.md)
- [Workflow](.github/workflows/phase97-ml-options-strategy-replication.yml)
- Results: results/phase97/
