# Phase 97 — ML Options Strategy Replication

**Branch:** `phase-97-ml-options-strategy-replication`  
**Parent:** `phase-96-moving-average-seasonality-replication`  
**Status:** PLAN REGISTERED; source-data gate pending  
**Strategy promotion:** NONE

## Research question
Can the Sherasiya paper's Random Forest, XGBoost and LSTM buy/sell option signal pipeline, its Greek/IV/underlying features, and its basic-momentum comparator be reconstructed on point-in-time, exact-contract data and independently evaluated after execution costs?

## Hypotheses
- H1: each ML signal improves on the paper's momentum comparator and a no-skill baseline on shared out-of-sample dates.
- H2: any improvement survives chronological splits, calibration checks and multiple-comparison correction.
- H3: signal performance translates to net executable P&L only with exact contracts, contemporaneous bid/ask or credible fills, expiry/strike/lot rules, and Paytm Money charges, statutory levies, spread, slippage and latency stress.

## Preregistered protocol
1. Re-read the Phase 94 paper/method register and the Phase 85 source-qualification outcome; reuse Phase 89 rolling-options coverage only as evidence of rolling-series field availability, not as exact-contract execution coverage.
2. Run a fail-closed data gate: required fields include timestamp, underlying/expiry/strike/right/contract identifier, OHLC or executable bid/ask, IV, Greeks, spot/underlying context, label-generation rule, and source/licensing provenance. Each row must be time-aligned and point-in-time. Never synthesize option quotes or treat rolling ATM-relative observations as a fixed contract.
3. If exact-contract training data and paper labels are unavailable, publish a quantified DATA-BLOCKED outcome and an auditable partial-replication map. Do not train on fabricated labels or unrelated Yahoo index prices. A prediction-only proxy is permitted only if an authorized, genuinely aligned feature/target dataset is available and it is clearly separated from the paper-exact experiment.
4. If data gate passes, freeze chronological DEV/VAL/OOS splits before fitting. Train Random Forest, XGBoost and LSTM with source-reported settings where recoverable; any undocumented setting is explicitly a sensitivity operationalization. Compare with basic momentum and no-skill baselines; all preprocessing, scaling and feature selection fit only on training data.
5. Evaluate classification metrics (balanced accuracy, precision/recall, F1, ROC-AUC where defined, Brier score/calibration) and signal turnover. For option economics, simulate only exact eligible contracts and apply contemporaneous bid/ask or validated fill assumptions, Paytm Money brokerage/levies, spread, slippage, latency and +50% cost stress. Missing execution fields means no P&L claim.
6. Record every paper method's final status and limitations. No access to Phase 83's sealed 2026 holdout.

## Acceptance and stopping
- Automated schema/provenance/data-leakage tests pass.
- Every source requirement receives PASS, PARTIAL or BLOCKED with evidence.
- One fixed run and bounded correction cycle; do not search for a positive result.
- Publish report, field gate, paper-method status ledger, logs and README checkpoint. Proceed to Phase 98 regardless of negative or blocked outcomes.
