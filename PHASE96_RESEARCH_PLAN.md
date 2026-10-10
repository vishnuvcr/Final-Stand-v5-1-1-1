# Phase 96 — Moving-Average and Seasonality Replication

**Branch:** `phase-96-moving-average-seasonality-replication`  
**Parent:** `phase-95-daily-forecast-model-replication`  
**Status:** PLAN REGISTERED; implementation and fixed out-of-sample run pending  
**Scope:** source-described SMA/EMA crossover, buy-and-hold comparison, simple-average/monthly-trend/seasonality and first-Thursday timing/three-day window/stop-loss rules from the Phase 94 paper-method register.

## Research question
Can the moving-average, monthly-trend, seasonality and timing rules described in the registered papers be operationalized without inventing material settings, and do their signals or returns reproduce the paper claims on a chronological out-of-sample sample?

## Source fidelity and hypotheses
1. Source-exact parameters and rules are implemented only when identifiable in the PDF/register. Any missing settings are explicitly marked as operationalized sensitivity variants, never exact reproduction.
2. H1: registered rules improve on buy-and-hold and a no-signal baseline on shared dates.
3. H2: any return advantage survives a strictly chronological holdout, realistic turnover, and transaction-cost stress.
4. H3: reported effect is not explained by parameter search or survivorship/look-ahead bias.

## Method
- Reuse validated cached Phase 95 daily NIFTY OHLCV only if its manifest, dates and checksum pass; otherwise reacquire transparently and record the source. Do not access the sealed 2026 Phase 83 holdout.
- Main fixed evaluation period: 2020-01-01 through 2025-12-31, with rule parameters frozen before scoring; additionally report the source paper's period only if its exact period and data can be reconstructed.
- Test close-based SMA( short/long ) and EMA crossover only as clearly labelled operationalizations when the PDF does not uniquely specify windows; use a small preregistered grid (5/20, 10/50, 20/100), not optimization over the test period.
- Compare with buy-and-hold and cash/no-position. Signals computed on completed close are executed no earlier than the next session open; no same-close fills.
- Atheetha-style month trend/simple average/seasonality and first-Thursday entry/three-day window/stop-loss are implemented only to the extent unambiguously stated by the source. Unspecified strike, option price, stop trigger or exit means option P&L is DATA-BLOCKED, not simulated from index levels.
- Include long-only index proxy gross and net results as a signal-level benchmark, explicitly not an investable NIFTY spot trade. If an authorized tradable proxy is used, disclose instrument, fees and slippage.
- Report signal count, exposure, turnover, CAGR where meaningful, total return, volatility, Sharpe (annualization disclosed), max drawdown, hit rate, average trade/holding period, and paired block-bootstrap uncertainty. Use date-aligned comparisons and correction for the preregistered rule-family comparisons.
- Cost sensitivities for any proxy trade: documented historical instrument charges where available, brokerage/levies, spread and adverse slippage. Paytm Money charges must be source-verified before stating a precise cost. No cost-free option P&L claim.

## Reproducibility labels
Every source method is marked REPRODUCED, PARTIAL, NOT REPRODUCED, INCONCLUSIVE, DATA-BLOCKED or NOT IDENTIFIABLE per Phase 94 definitions. A passing workflow is not a scientific result. Prediction skill does not imply profitable options trading.

## Acceptance and stopping
- Unit tests verify signal timing, no look-ahead, stop handling, missing-data behaviour and baseline alignment.
- One frozen parameterized run plus necessary bug fixes; no tuning to maximize the holdout.
- Every method gets an outcome, including failures and data blockers.
- Publish aggregate CSV, report, plot, data manifest, coverage/exclusion ledger, phase status, research log, error log and auditable decision/chat summary.
- Proceed to Phase 97 after the fixed run and reconciliation; do not expand the program beyond the finite Phase 100 stop boundary.
