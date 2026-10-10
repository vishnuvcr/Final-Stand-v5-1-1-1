# Phase 94 — Final Strategy Evidence Audit and Promotion Gate

**Registered:** 2026-10-10  
**Branch:** `phase-94-strategy-evidence-audit`  
**Parent:** `phase-93-uploaded-literature-audit`  
**Type:** bounded audit of prior strategy evidence; no new trading or model experiment  
**Initial status:** IN PROGRESS — inventory and source reconciliation

## Research question
Across strategies previously tested in Final Stand, which candidates have reproducible, sufficiently covered, genuinely out-of-sample net trading results after realistic costs, and which are merely promising, non-estimable, proxy-based, or not eligible for promotion?

## Aim
Produce a source-traceable, non-inflated candidate register and an evidence-gated decision. Do not manufacture a leaderboard when the primary result ledgers cannot be reconciled.

## Objectives
1. Read the latest main README and the most recent relevant phase plans, statuses, error logs, chat/decision logs, and canonical results before every continuation.
2. Build an inventory from canonical repository artifacts, prioritizing strategy backtest result ledgers rather than predictor studies, manuscript claims, or chat summaries.
3. For every candidate, record exact source phase/path, run ID, dataset and period, DEV/validation/OOS separation, completed trade count, coverage/exclusions, gross/net P&L, net profit per completed trade, return denominator, drawdown, win rate, expectancy, profit factor, cost assumptions, and execution fidelity.
4. Distinguish numeric zero from empty-sample placeholders and non-estimable statistics. Do not rank candidates missing essential denominators or completed trades.
5. Include Paytm Money brokerage, statutory levies, bid/ask spread, adverse slippage, latency and stressed-cost results only where source data and the frozen backtest support them; mark absent cost components explicitly.
6. Reconcile strategy-level findings with Phase 83 multiple-testing / defined-risk gates and the protected 2026 holdout boundary. Never access or infer results from the sealed holdout.
7. Produce a ranked shortlist only for comparable, verified candidates. Otherwise publish an auditable missing-evidence register and no-go/hold decisions.
8. Add automated structural validation, bounded push triggers and a manual workflow-dispatch button.
9. Update phase status, error log, auditable decision log and branch README after every material step. Keep PR draft/unmerged.

## Method
- Source hierarchy: canonical machine-readable result ledger and successful workflow artifact; phase results report; phase status; README; manuscript; chat summary. Lower-ranked sources cannot override a contradictory canonical ledger.
- Verify run IDs and source file paths. Record unresolved disagreements as errors; do not silently reconcile them.
- Compute derived metrics only from complete, source-verified numerators and denominators. For example, net profit per trade = net P&L / completed trades only when completed trades > 0 and net P&L is a valid realized sum.
- Separate strategy backtests from spot-magnitude predictors, indicator associations, literature-reported claims, and no-trade/empty-sample tests.
- Preserve fixed splits; never tune on OOS or reopen closed predictor sweeps to seek a positive result.
- No new market data is acquired and no trading rule is rerun in this phase. If a candidate lacks exact listed contract identity and defensible fills, it remains execution-ineligible.

## Evidence grades
- **A — promotion-review eligible:** canonical result ledger and successful run; adequate completed-trade coverage; independent OOS; all-in realistic cost accounting and stress; drawdown/risk and denominator fully defined; no unresolved leakage or data integrity defect. This grade allows review, not automatic live approval.
- **B — research-only:** some reproducible strategy evidence, but one or more material execution, cost, coverage, statistical, or independent validation gates remain.
- **C — not estimable / incomplete:** zero completed trades, empty sample, missing denominator, missing canonical ledger, unresolved run, or material coverage gaps.
- **D — not a strategy-P&L test:** predictor association, spot forecasting, conceptual article, or unreplicated literature claim.

## Statistical reporting
- Report per-strategy metrics with their denominator and period.
- Use paired/session-cluster uncertainty only where the existing registered design supports it; do not invent confidence intervals from aggregate summaries.
- Avoid naive cross-strategy comparisons where periods, sizing, risk, costs, and return denominators differ.
- If a comparable shortlist exists, treat its ranking as descriptive and explicitly account for selection/multiple-testing risk; do not promote a winner solely because it is the best of many candidates.

## Phase gates and stopping rule
1. **Gate 1 — repository/source inventory:** identify canonical strategy-result artifacts and reconcile recent phase state.
2. **Gate 2 — candidate ledger:** extract verified values, label every missing field, and classify candidate evidence.
3. **Gate 3 — cost/risk comparability:** establish whether all-in net comparisons are supportable.
4. **Gate 4 — decision:** publish either an evidence-supported shortlist or a no-go/hold decision with precise missing prerequisites.
5. **Gate 5 — QA and publication:** workflow validation passes; README/status/logs point to exact outputs.

Stop after Gate 5. Do not add arbitrary years, repeat already failed source searches, or create new indicator combinations. A new empirical phase requires a materially new preregistered hypothesis or authorized exact-contract quotes/depth/fill data.

## Required safeguards
- Phase 83's protected 2026 holdout stays sealed.
- No strategy is promoted by this audit alone.
- Never call zero completed trades a zero-return profitable backtest.
- Do not present rolling ATM candles or synthetic-forward proxies as exact-contract executable prices.
- Cost model must name Paytm Money brokerage and statutory charges, spread, adverse slippage, latency and stress. If unavailable, do not label a result fully cost-adjusted.
- Log only user-visible requests, source checks, reproducible errors, fixes, decisions and outcomes; never log hidden reasoning or secrets.

## Deliverables
- `results/phase94/strategy_evidence_register.csv`
- `results/phase94/audit_report.md`
- `results/phase94/validation_report.json`
- `research/phase94/validate_strategy_evidence.py`
- `.github/workflows/phase94-strategy-evidence-audit.yml`
- `PHASE94_STATUS.md`, `PHASE94_ERROR_LOG.md`, `PHASE94_CHAT_LOG.md`, and this plan
- Branch README checkpoint and draft pull request

## Current known evidence boundary
Phase 66's CCI adaptations had zero completed trades in all four candidate/split rows, so profitability metrics are not estimable. Phases 89–92 are predictor studies, not options strategy P&L. Phase 83 reported no defined-risk candidate passing its registered primary gate; the 2026 holdout remains sealed. Historical TT strategy metrics must be traced to canonical result artifacts before any ranking or promotion claim is made.
