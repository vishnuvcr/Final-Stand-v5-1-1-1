# Phase 84 — Cross-phase evidence reconciliation

Date: 2026-10-10
Branch: `phase-84-cross-phase-evidence-reconciliation`
Status: PREREGISTERED / IN PROGRESS

## Purpose
Produce a bounded, source-traceable decision ledger separating (a) canonical strategies supported by prior frozen artifacts, (b) partial-window diagnostics, (c) rejected model overlays, and (d) the closed Phase 80–83 static-structure experiment. This is a reconciliation phase, not another strategy optimization or profitability backtest.

## Research questions
1. Which existing findings are canonical controls versus exploratory or partial-sample diagnostics?
2. What are the strongest documented net-performance and risk results, and under which sample/cost assumptions?
3. Which claims are statistically supported, and which remain descriptive, data-blocked, or rejected?
4. What is the smallest next finite study justified by existing evidence without repeating failed source searches or using the sealed holdout?

## Frozen evidence inputs
- Phase 83 manuscript, status, supplementary ledgers, and its registered closeout decision.
- Phase 38 frozen-control and model-selector comparison status.
- Phase 51-3 partial-OOS report and trade summaries.
- Phase 59–61 source sufficiency decisions and Phase 71–76 missing-session/contract-identity audits as linked from the repository README.
- Existing phase plans, status files, error logs and workflow evidence only. No new market-data acquisition is required.

## Method
1. Build an evidence inventory with branch, artifact, sample period, strategy/control identity, cost assumptions, completeness, inferential status and promotion decision.
2. Preserve incompatible samples as separate evidence strata; do not compare raw P&L across different capital, sample, or strategy definitions as if directly comparable.
3. Tag each statement as canonical/frozen, partial OOS, exploratory, statistically rejected, data-blocked, or terminal no-go.
4. Verify every key number against the originating report/ledger and record discrepancies as explicit errors rather than silently reconciling.
5. Define a ranked next-step decision using pre-existing evidence gaps. Do not reopen the Phase 83 holdout or modify any frozen strategy.
6. Publish the evidence matrix, status, error log, research log, and README checkpoint; validate links and arithmetic.

## Statistical and financial rules
- No new hypothesis tests or parameter search in Phase 84.
- Preserve existing expiry-cluster inference and Holm decisions; do not reinterpret unadjusted p-values as confirmation.
- Keep Paytm Money fees and existing adverse-slippage assumptions attached to the results they belong to.
- Clearly distinguish LTP/OHLC modeled outcomes from executable bid/ask/depth fills.
- Do not infer future performance from partial-window positive totals or cross-study P&L rankings.

## Acceptance criteria
- Every included claim has a direct repository source link.
- Each candidate/control is labeled with sample coverage, cost model, statistical status and promotion status.
- Conflicts and missing fields are explicitly logged.
- The next research recommendation is finite, conditional on evidence, and does not repeat rejected source probes.
- README and phase status reflect the same conclusion.

## Stop conditions
Stop after the reconciliation ledger and decision report pass automated/manual consistency checks. If evidence cannot be reconciled, record the gap and stop rather than manufacture a unified ranking. No live deployment or strategy promotion is within scope.

## Planned outputs
- `results/phase84_evidence_reconciliation/evidence_matrix.csv`
- `results/phase84_evidence_reconciliation/decision_report.md`
- `PHASE84_STATUS.md`
- `PHASE84_ERROR_LOG.md`
- `PHASE84_CHAT_LOG.md`
- Updated `README.md`

## Explicit exclusions
No holdout access; no paid data purchase; no raw market-data upload; no strategy-rule changes; no claims that all possible strategies were tested; no private hidden reasoning or chain-of-thought logging. The audit trail records decisions, methods, outputs, and errors only.
