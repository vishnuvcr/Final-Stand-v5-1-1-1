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

## 2026-10-09 — Phase 51-0 data/source freeze

### Fresh OOS window
The fresh OOS window is frozen as **2026-04-21 through 2026-08-04**, inclusive. It begins after the last Phase-50B TT-03 cached campaign on 2026-04-13 and is therefore not part of the Phase-50B selection/inference evidence. No OOS P&L was inspected before this window was frozen.

### Frozen external data sources
1. **Options:** Hugging Face dataset `rissin/nse-options-intraday`, NIFTY 1-minute Upstox expired-option candles, 2026 shard. The dataset documents NIFTY 1-minute coverage from October 2024 onward and columns for expiry, strike, option type, OHLC, volume and source.
2. **Spot:** Hugging Face dataset `thetrademarkk/india-index-options-1m`, `index/NIFTY.parquet`, 1-minute NIFTY spot OHLC. This source is used only for ATM/strike selection and is not used to estimate option execution.
3. **Primary exchange validation:** NSE historical contract-wise price/volume data and official derivatives reports remain the preferred validation source where directly accessible.

### Execution-data limitation
Neither selected public intraday dataset supplies historical bid/ask quotes. Therefore no synthetic bid/ask spread will be labelled as observed. Phase 51 may use deterministic adverse execution stresses, but a true historical bid/ask test remains unavailable unless a separately sourced order-book dataset passes the data audit.

### Broker/cost freeze
For 2026 OOS trades, the registered broker scenarios are:
- legacy Paytm Money F&O brokerage: ₹10 per executed unique order;
- current standard Paytm Money scenario: ₹20 per executed order for new accounts, retained as a conservative sensitivity scenario because Paytm Money's historical/current public pages document different client cohorts;
- NSE equity-options transaction charge: ₹3,553 per crore of premium turnover (effective 2026-03-01);
- STT on sale of options: 0.15% of premium for transactions on/after 2026-04-01;
- SEBI turnover fee: 0.0001% of turnover;
- equity-options stamp duty: 0.003% on buyer;
- GST: 18% on broker services/eligible service charges.
These rates are frozen before OOS replay. Exercise-related STT is not applied because the strategy exits intraday before exercise.

### Cost/slippage stress freeze
Execution stress will be represented as:
- base observed-bar execution;
- base + 25% execution-cost stress;
- base + 50% execution-cost stress;
- deterministic adverse one-tick-per-leg execution where a valid tick-size rule is available;
- combined adverse tick + 50% stress.
Because historical bid/ask is absent, these are stress models, not reconstructed bid/ask fills.


### 2026-10-09 — Phase 51-1 spot-source replacement rule

The first frozen spot source failed endpoint coverage before OOS P&L inspection. To avoid either silent data repair or P&L-driven source selection, Phase 51-1 now permits an independent pre-P&L source replacement/triangulation gate only under these fixed rules:

1. The source must be independent of the failed source and publicly reproducible.
2. It must cover the full frozen OOS window at the required endpoint, have deterministic timestamp/duplicate integrity, and pass the same session-quality checks.
3. Its common-period price series must agree with the already-frozen source at the preregistered overlap thresholds before it is used as the replay spot source.
4. The replacement decision must be made entirely from data-quality evidence, before any strategy OOS P&L is inspected.
5. If no source passes, Phase 51-4 stops with a data-availability limitation; the OOS window is not shortened.

Independent triangulation source registered: public GitHub repository technovusin/nifty50-historical-data, cleaned NIFTY50 1-minute files for 2026-04 through 2026-08. It is a validation source only until the above gate passes.


### 2026-10-09 — Phase 51-1 options-source augmentation rule

The initial option source does not reach the frozen OOS endpoint. Before any strategy P&L is calculated, Phase 51-1 may augment only the missing expiry blocks from an independently published 1-minute NIFTY options source, under a fixed data-quality rule:

1. The frozen OOS window and all existing expiry blocks remain unchanged.
2. Missing expiry blocks must be identified from the source manifest, not from strategy P&L.
3. The supplemental source must contain explicit 1-minute files for each missing expiry and pass schema/timestamp integrity.
4. Common expiry blocks must be compared against the original rissin source before supplementation is accepted.
5. No P&L-based choice among data sources or expiry blocks is permitted.
6. If the augmented source still fails the registered 95% replay coverage gate, Phase 51 stops with a data-availability/feasibility conclusion; the OOS window is not shortened.

Independent augmentation candidate registered: thetrademarkk/india-index-options-1m, options/NIFTY/2026-07-28.parquet and options/NIFTY/2026-08-04.parquet.


### 2026-10-09 — Phase 51-1B common-expiry equivalence threshold correction
The common-expiry source-equivalence gate uses a scale-invariant minimum of 10,000 exact matched quote rows plus at least 80% coverage of the original source's comparable rows. The prior 100,000-row cutoff was removed because weekly expiries have materially different strike/contract populations; the correction was made before any OOS P&L or strategy selection.


### 2026-10-09 — Phase 51-1B data gate
The frozen OOS period remains 2026-04-21 through 2026-08-04. The primary option file reaches only 2026-07-21. The public supplemental files checked for 2026-07-28 and 2026-08-04 end on 2026-07-02, so they cannot fill the missing endpoint. Minute-level replay is blocked until a full-coverage source is acquired.
