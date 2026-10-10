# Phase 101 — Full PDF Strategy Replication Gap-Fill

**Branch:** `phase-101-full-pdf-strategy-replication`  
**Parent:** `phase-100-cross-paper-reproducibility-synthesis`  
**Status at registration:** OPEN — implementation and runtime replay pending  
**Promotion:** NONE; research-only

## Research question

After reconciling all 14 uploaded PDFs against Phases 95–100, can the remaining source-described options methods be tested with available historical NIFTY data, point-in-time contract bars, and realistic cost/slippage sensitivities, and what is the strongest conclusion each PDF supports?

## Aims and bounded scope

1. Create a one-row-per-paper audit that distinguishes exact replication, common-data/proxy testing, analytical payoff checks, data blockers, and unidentifiable source specifications.
2. Run two additional fixed, source-derived tests on the available 2021–2025 historical NIFTY index/options dataset:
   - **U05 (Atheetha et al., 2019):** first-Thursday monthly seasonality rule using the prior three years of same-calendar-month returns, target-price-based strike selection, a 20% option-premium target, a 30% stop activated after T+3, and an exit no later than the penultimate session before expiry.
   - **U02 (Sherasiya, 2025):** RF, XGBoost and a short-sequence LSTM proxy for the paper's >1% next-day-index-return Buy label; predicted Buy buys an ATM call and predicted Sell buys an ATM put, with one-session holding.
3. Carry forward the accepted Phase 95 forecasting screen, Phase 96 SMA/EMA screen, Phase 66 CCI replay and Phase 99 payoff-algebra tests; do not mislabel any of these as exact paper reproduction.
4. Apply chronological DEV (through 2023-12-31) and VALIDATION (2024-01-01 through 2025-12-31) reporting. No tuning on validation and no use/download of 2026 option observations.
5. Model one-tick adverse fills and date-effective statutory/exchange charges, a ₹20/order brokerage sensitivity, +50% charge stress, and the paper's 0.25% per-side price-impact sensitivity where applicable. These are modelled execution costs, not a guarantee of real fills or exact historical broker contract notes.
6. Publish complete method/status ledgers, opportunity and trade audits, paper-level metrics, tests, report, data provenance, errors, figures and a finite terminal decision.

## Source-faithful limits (must remain explicit)

- U05 describes an expected-price formula dimensionally ambiguously (“opening price + average return”). This phase will operationalize it as Wednesday open × (1 + mean of the previous three returns for the same calendar month). The signal is therefore a transparent proxy, not a perfect transcription. The first Thursday must be strictly after the forecast Wednesday; no entry is allowed before the forecast is observable. Source selection between CE and PE is inferred from the sign of the expected move; this inference will be disclosed.
- U05 says “highest liquidity” but gives no numerical liquidity cutoff. Strike-distance to expected price is the primary ranking; available entry-time OI/volume breaks ties. No future-session liquidity is allowed.
- The available options archive begins in 2021 and ends in 2025, not the U05 source period. A modern-sample replay is not an exact historical reproduction.
- U02 omits a complete reproducible feature schema and model configuration. The test must use only features observable in the pinned data at signal time; missing IV/Greeks/news modalities are recorded and not fabricated. A proxy win is not the paper's exact result.
- U07 contains payoff illustrations, not a complete entry-signal system; its 13 structures are tested algebraically in Phase 99. No synthetic premiums or invented trading signals will be presented as historical profitability.
- Forecast papers do not all describe trading systems. Phase 95's shared-data model-family screen remains PARTIAL for source claims whose original datasets, modalities or splits were not matched.
- No source claim can be promoted to “profitable” merely because a workflow passes. Any strategy requires sufficient completed validation trades, coverage, positive net results across registered cost stresses, and uncertainty/robustness checks. Underpowered results are INCONCLUSIVE.
- No purchase of paid data and no redistribution of raw Hugging Face data.

## Method and steps

1. Re-read Phase 100 synthesis, this plan, statuses and logs before execution.
2. Pin the existing accepted options data revision and reuse its cache; inspect only option files dated through 2025-12-31.
3. Verify schema, duplicate contract-minute keys, timestamp/time-zone handling, date coverage, strike/right, OI/volume and required OHLC values.
4. Run the U05 monthly rule on the pinned modern sample, recording every planned month and exclusion/failure reason, selected contract, entry/exit, lot sizing and cost cases.
5. Run U02 chronological RF/XGBoost/LSTM-proxy predictions and the corresponding one-session ATM call/put simulation. Report both predictive classification quality and costed option results; neither substitutes for the other.
6. Run deterministic tests for target timing, T+3 stop activation, no-lookahead strike selection, capital/lot sizing, fee arithmetic, temporal split and payoff sign.
7. Reconcile all U01–U14 against prior verified branch outputs and Phase 101 results in a paper-level matrix. If a previous phase output is unavailable, retain its prior documented status and do not manufacture data.
8. Generate the manuscript-style report, CSV/JSON ledgers, equity/drawdown figures, source manifest, validation report and logs. Report circular moving-block bootstrap 95% intervals for mean net trade P&L only when at least 20 completed trades are available; otherwise mark precision NOT ESTIMABLE. If a test fails, preserve the error and fix only the root cause; no rule changes or result-driven tuning.
9. Stop after one corrected, validated run and status reconciliation. Any additional research needs a new bounded plan.

## Acceptance criteria

- 14 paper rows in the master matrix, with explicit evidence class, sample, costs, result/limitation, and report link.
- Every U05 monthly opportunity ends in an explicit completed/excluded/blocked state.
- U02 gives a row for each RF/XGBoost/LSTM run, classification metrics, coverage, trades and cost scenarios; failed/blocked models have explicit reasons.
- Validation trades are strictly dated through 2025-12-31; no 2026 option file is downloaded.
- No use of future bars to choose entry strike, infer entry-time liquidity, or set entry price.
- Net P&L is not estimated if no completed trades; zero-trade samples are labelled NOT ESTIMABLE.
- Unit tests pass; reports match machine-readable ledgers.
- No strategy promotion unless every evidence and economic gate passes. Default decision remains NO PROMOTION.

## Finite stopping rule

Phase 101 ends after the two additional strategy tests, the 14-paper reconciliation and output validation complete, or after the bounded run records an explicit data/schema blocker. Do not run endless source searches, widen rules, tune against validation, access the 2026 holdout, or imply a blocked test is a negative efficacy result.
