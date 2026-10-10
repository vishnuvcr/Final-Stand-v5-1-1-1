# Phase 96 — VIX-Regime-Adaptive Selection Test

Registered 2026-10-10. Parent: Phase 95. Status: preregistered before execution.

## Question
Does selecting one defined-risk candidate per LOW, NORMAL and HIGH volatility regime using development results lead to positive combined validation P&L under the existing 50%-friction scenario?

## Frozen method
- Input: results/phase45_ready_made/strategy_vix_summary.csv; expected Git blob SHA 4208da2e1189a68af697e11d03dd7d4ac937ddf7.
- Fixed states: LOW, NORMAL, HIGH only. Exclude ALL and overlapping directional/spike labels.
- Keep only defined-risk candidates with both DEV and VAL rows and at least 5 trades in each.
- Select the highest development net50 candidate within each state; alphabetical tie-break.
- Primary endpoint: sum of the three selected validation net50 cells.
- Do not read or retain holdout rows. Do not access Phase 83 protected 2026 holdout.

## Limitations and guardrails
This is a retrospective method on previously explored summary data, not independent blinded evidence or a fresh strategy replay. Source net50 is not proof of full Paytm Money fees, statutory levies, spread, slippage, latency or executable fills. The three state cells may overlap in exposure and lack capital allocation; their sum is not a deployable portfolio return. No parameter tuning, extra states, years or strategy variants. No promotion.

## Deliverables
Research script, workflow with manual run, CSV/JSON results, report, status/error/chat logs and README update. Stop after reproducible result and QA.

Execution note: the registered workflow is triggered by pushes to the plan/script/input paths and also has a manual workflow_dispatch entry point.


## Preregistered feasibility amendment — 2026-10-10
The initial run found no eligible HIGH-regime candidate at the 20-trade minimum. Before inspecting any strategy's profitability output, the minimum was reduced to 5 trades in both DEV and VAL for all three fixed regimes so the method can be evaluated at all. This lowers precision and increases small-sample risk; trade counts are reported per state and no promotion is permitted.
