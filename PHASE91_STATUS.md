# Phase 91 Status

Date: 2026-10-10  
Status: **PREREGISTERED — awaiting automated 2023 replication run**  
Branch: `phase-91-iv-temporal-replication-2023`  
Strategy promotion: **NONE**.

- [Research plan](PHASE91_RESEARCH_PLAN.md)
- [Error log](PHASE91_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE91_CHAT_LOG.md)
- [Analysis engine](research/phase91/iv_incremental_study.py)
- [Workflow](.github/workflows/phase91-iv-temporal-replication-2023.yml)
- [Results report](results/phase91/PHASE91_RESULTS.md)

The primary endpoint is M1 MAE minus M2 MAE on fixed Oct–Dec 2023 OOS sessions. Phase 90 is the comparator only; its cache and raw payloads are not reused. 2025 phase data and the protected Phase 83 2026 holdout are excluded. No strategy P&L or live orders are in scope.
