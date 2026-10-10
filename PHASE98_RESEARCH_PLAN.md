# Phase 98 — CCI Options Paper Replication Gate

**Branch:** `phase-98-cci-options-paper-replication-gate`  
**Parent:** `phase-97-ml-options-strategy-replication`  
**Status:** PLAN REGISTERED; evidence reconciliation pending  
**Strategy promotion:** NONE

## Research question
Is there materially better, authorized source data than the Phase 66 input that permits a source-faithful reconstruction of Shaha's CCI-based NIFTY long-option method on the paper's period and exact contracts?

## Preregistered steps
1. Inspect Phase 66's final report, its coverage/exclusion outcome and exact CCI rule implementation; do not rerun identical rules on identical data.
2. Inspect Phase 85's data-source qualification decision and Phase 87–89 Dhan rolling-options results. Distinguish rolling ATM-relative bars from exact contract identity, and distinguish field presence from historical bid/ask/depth or executable fills.
3. Compare candidate new sources against minimum requirements: original-period coverage, timestamp/session integrity, exact contract/expiry/strike/right, OHLC/quotes, lot size/corporate-action adjustments where relevant, CCI input bars, expiry/entry/exit rule recoverability, provenance/licensing and reproducible retrieval.
4. Only if a new eligible source closes the previous blocker, implement a distinct source-faithful replay. If not, close as DATA-BLOCKED with a quantified evidence matrix and explicit stop decision.
5. Any viable options P&L must include Paytm Money brokerage, statutory levies, spread, adverse slippage, latency and +50% friction stress. Missing bid/ask/fill evidence prohibits profitability claims.
6. Preserve the sealed 2026 holdout and proceed to Phase 99 regardless of gate outcome.

## Hypotheses
- H1: original CCI signals can be regenerated on the paper's stated sampling period without undocumented rule changes.
- H2: complete eligible trade coverage meets the preregistered coverage gate.
- H3: costed results survive out-of-sample and friction stress only if the data permit valid execution reconstruction.

## Stop rule
No identical zero-coverage rerun, no proxy option fills, no parameter tuning to force coverage or profit. The phase ends with either a new qualified replay or a documented data blocker.
