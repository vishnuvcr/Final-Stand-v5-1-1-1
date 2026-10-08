# PHASE 51 RESEARCH PLAN — Broker-Calibrated Execution and Fresh OOS Validation

## Status
ACTIVE — finite new phase. Started only after terminal completion of Phase 50B.

## Research question
Does the strongest Phase-50B candidate, TT-03, and its frozen OTM350 variant retain economically meaningful edge when evaluated with broker-calibrated transaction costs, bid/ask-aware execution where available, capacity/liquidity constraints, and a genuinely fresh out-of-sample period that was not used anywhere in Phase 50B?

## Primary hypothesis
H1: At least one frozen candidate retains positive risk-adjusted net economics after broker-calibrated costs and fresh OOS evaluation.

H0: Neither candidate retains sufficient positive net economics under the preregistered execution model.

## Scope
Only two frozen candidates enter Phase 51:
1. TT-03 source-faithful.
2. TT-03 OTM350 frozen geometry.

No new strike, stop, exit, VIX threshold, DTE, width, timing or management parameter may be optimized in Phase 51.

## Phase sequence
51-0 Registry and data audit
51-1 Broker/statutory cost calibration
51-2 Bid/ask and liquidity execution model
51-3 Capacity/slippage stress
51-4 Fresh chronological OOS replay
51-5 Statistical inference and robustness
51-6 Final manuscript, decision and reproducibility package

## Temporal protocol
Phase-50B DEV/VAL/HOLD remain frozen historical evidence.
Phase 51 must define a new OOS window from data not used in Phase 50B selection/inference. The exact eligible window will be frozen before inspecting its strategy P&L.
If a truly untouched historical period is unavailable, the phase must stop and classify the limitation rather than silently reuse protected data.

## Execution-cost hierarchy
A. Paytm Money brokerage: ₹10 per unique executed F&O order, based on current official broker documentation.
B. Statutory/regulatory/exchange charges: current applicable schedules, including GST and STT where applicable.
C. Bid/ask execution: buy orders use ask and sell orders use bid when reliable quotes exist.
D. Slippage stress: deterministic basis-point/tick stresses registered before OOS P&L inspection.
E. Liquidity/capacity: reject or stress trades when quoted quantity is insufficient for the historical lot size or registered position size.

The model must distinguish brokerage from statutory charges rather than burying both inside a generic per-order proxy.

## Data sources
Priority order:
1. NSE historical contract-wise and order/trade data.
2. BSE where the strategy universe requires it.
3. Existing repository caches/artifacts.
4. Other open data sources only for gap analysis and never as silent substitutes for primary evidence.
All downloaded data must be cached and checksummed in the repository or GitHub Actions artifact store.

## Feasibility gates
- Mandatory-entry and mandatory-exit quote coverage >=95%.
- Zero unexplained data errors.
- Bid/ask availability reported separately from LTP availability.
- Historical lot size verified for every OOS contract.
- No forward fill or synthetic quote repair in primary evidence.
- Every excluded trade receives an explicit exclusion reason.

## Statistical protocol
The exact test family will be frozen in Phase 51-0 before OOS P&L inspection.
Candidate selection is prohibited after the fresh OOS window is opened.
Inference will use dependence-aware block methods and multiplicity correction if more than one primary hypothesis remains.
No capital-normalized return, Sharpe, CAGR or margin-adjusted return will be reported without a defensible common capital/margin denominator.

## Cost stress grid
At minimum:
1. Broker + statutory base.
2. Base + 25% execution slippage stress.
3. Base + 50% execution slippage stress.
4. Base + adverse bid/ask execution.
5. Combined adverse execution + 50% stress.

The exact numerical slippage convention must be frozen in 51-0 and must not be tuned from OOS results.

## Promotion rule
A candidate can only be promoted if:
- feasibility gate passes;
- all primary data-quality audits pass;
- fresh OOS net P&L is positive;
- adverse execution stress remains positive;
- statistical gate passes after multiplicity correction;
- no material capacity violation exists;
- no hidden parameter selection occurs;
- all major conclusions remain stable under registered sensitivity analyses.

Failure means NO PROMOTION, with no further tuning inside Phase 51.

## Required outputs
- Structured data manifest and checksums.
- Cost model specification.
- Execution/slippage model.
- OOS trade ledger.
- Coverage and exclusion audit.
- Chronological equity and drawdown.
- Cost-sensitivity tables/charts.
- Statistical inference.
- Full final manuscript with appendices and supplements.
- Updated README, research log, error log, chat/action log and phase status after every step.

## Finite stopping rule
Phase 51 ends after 51-6. It must not become an open-ended optimization loop.
