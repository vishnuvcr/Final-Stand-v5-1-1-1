# Phase 92 Status

Date: 2026-10-10  
Status: **PREREGISTERED — awaiting one fixed 2022 run**  
Branch: `phase-92-synthetic-forward-oi-study-2022`  
Strategy promotion: **NONE**.

- [Research plan](PHASE92_RESEARCH_PLAN.md)
- [Error log](PHASE92_ERROR_LOG.md)
- [Auditable chat/decision log](PHASE92_CHAT_LOG.md)
- [Analysis engine](research/phase92/synthetic_forward_oi_study.py)
- [Phase branch workflow](.github/workflows/phase92-synthetic-forward-oi-2022.yml)
- [Default-branch runner + manual dispatch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/main/.github/workflows/phase92-pr-runner.yml)
- [Results report](results/phase92/PHASE92_RESULTS.md) — generated after a verified run

The single primary comparison is M2 (spot+VIX+IV) versus M4 (M2 plus a lagged synthetic-forward proxy gap and lagged CE/PE OI imbalance) on Q4 2022 OOS, using paired session-cluster bootstrap. Direct FUTIDX basis, Greeks and strategy P&L are out of scope because the rolling options data do not establish those exact historical inputs/executable fills. Protected 2026 holdout remains sealed.
