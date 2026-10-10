# Phase 95 — Frozen-Universe Strategy Selection Test

**Registered:** 2026-10-10  
**Branch:** `phase-95-nested-strategy-selection-test`  
**Parent:** `phase-94-strategy-evidence-audit`  
**Type:** bounded retrospective test of a frozen existing strategy universe; no new market data or 2026 protected holdout  
**Status:** preregistered before running the script

## Research question
When the existing Phase 45 VIX/ready-made strategy universe is selected using development-split net P&L under the recorded 50%-friction stress, does the development winner remain profitable in the already registered validation split?

## Hypothesis
**Primary H1:** the single top-ranked eligible defined-risk strategy selected only on development net50 P&L has positive validation net50 P&L. The null/decision baseline is that the selection rule does not demonstrate positive stressed validation performance.

## Fixed source and population
- Input: `results/phase45_ready_made/strategy_vix_summary.csv`, canonical blob SHA `4208da2e1189a68af697e11d03dd7d4ac937ddf7`.
- Universe: strategy rows where `state=ALL` and `defined_risk=True`.
- Eligibility: development split must contain at least 50 completed trades; this excludes sparse calendar rows with one trade and no validation coverage.
- Selection: highest development `net50`; ties resolved alphabetically by strategy name.
- Confirmatory evaluation: the selected strategy's validation `net50` and `max_dd`. Do not inspect the HOLD split or any Phase 83 2026 holdout data.
- Secondary descriptive result: count eligible strategies with positive validation `net50`; no hypothesis tests or winner promotion based on this count.

## Metrics and method
- Report DEV/VAL trade counts, base net P&L, net50 P&L and max drawdown as supplied by the source table.
- Use validation stress result as the primary endpoint. Do not infer a capital-normalized return because the source table has no capital denominator.
- The 50% friction stress is the source's existing scenario and is not claimed to include every Paytm Money statutory fee, exact-contract spread, latency and fill risk. Missing execution-cost components remain a limitation.
- This is a selection-stability test on an already available historic table, not an independent fresh-market validation. Because the dataset has previously been explored in the wider project, interpret as a bounded retrospective robustness audit, not as a newly blinded confirmatory trial.

## Stop rules
- One frozen candidate universe, one selection rule, one primary endpoint.
- No parameter tuning, VIX subgroup fishing, strategy-specific exceptions, extra years, or use of the HOLD split.
- No new strategy backtest, no external market data acquisition, and no Phase 83 holdout access.
- Stop after reproducible output and QA; do not promote any strategy from this phase.

## Deliverables
- `results/phase95/selection_results.csv`
- `results/phase95/selection_test_report.md`
- `results/phase95/validation_report.json`
- `research/phase95/run_selection_test.py`
- `.github/workflows/phase95-selection-test.yml`
- status, error and visible-chat logs; README checkpoint; draft PR

## Decision gate
A positive validation `net50` is necessary but not sufficient for promotion. A negative selected validation result fails this frozen selection rule. Regardless of outcome, no live promotion without independent future OOS, trade-level audit, full Paytm Money cost accounting, realistic execution and drawdown/risk limits.
