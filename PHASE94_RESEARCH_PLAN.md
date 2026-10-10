# Phase 94 — Complete Uploaded-Paper Method Replication Program

**Registered:** 2026-10-10  
**Branch:** `phase-94-paper-method-replication-program`  
**Parent:** `phase-93-uploaded-literature-audit`  
**Type:** bounded preregistration, method inventory, and orchestration plan  
**Status:** REGISTERED; execution queue defined; no new empirical results are claimed by this phase  
**Strategy promotion:** NONE

## Research question

Across all 14 uploaded papers, which forecasting methods and trading rules can be reconstructed from the papers, and do their reported predictive or trading results survive independent, time-ordered replication on appropriately matched data, baselines, statistical tests, and realistic trading costs?

## Why this phase exists

Phase 93 completed a bibliographic/evidence audit, not empirical reproduction. The previous wording could be read as if literature coverage meant every method had already been tested. This phase corrects that distinction. Every distinct method, baseline, trading rule and hybrid architecture described by the fixed 14-paper corpus is registered below. Where the paper gives insufficient operational detail, the implementation will be labelled a **transparent operationalization**, not an exact replication. Where source-period data or executable option data are unavailable, the outcome will be **blocked / partial replication**, never a fabricated result.

## Aims

1. Create a traceable paper-to-method register covering all uploaded PDFs U01–U14.
2. Reconstruct each source's target, sample period, inputs, algorithms, rules, metric definitions and reported claims as far as the PDF supports.
3. Reproduce forecasting models with the closest recoverable target, frequency, horizon, features and chronology, while adding a common comparison protocol.
4. Reproduce each operational option strategy where exact rules and eligible historical contracts can be identified.
5. Test whether apparent high accuracy or statistical significance survives naïve baselines, aligned out-of-sample dates, leakage controls, uncertainty intervals, multiple-comparison controls and sensitivity checks.
6. For options, calculate net results only from eligible contracts and realistic fill assumptions with Paytm Money brokerage, statutory levies, spread, adverse slippage, latency and cost stress.
7. Publish full aggregate results, coverage/exclusion ledgers, plots, per-paper decisions, limitations and manuscript updates. Never treat the authors' numbers as reproduced until independently regenerated.

## Research hypotheses

- **H1 — Forecast reproducibility:** each source method improves on the paper-matched naïve baseline for the same target and test dates, under correctly specified metrics.
- **H2 — Generalization:** any apparent benefit survives strictly chronological out-of-sample testing and at least one independent temporal test period.
- **H3 — Statistical reliability:** improvement intervals and pre-specified paired tests support the claimed direction after accounting for serial dependence and multiple comparisons.
- **H4 — Economic translation:** forecasting gains, if any, translate into positive risk-adjusted strategy returns only after executable-contract constraints and all-in trading costs.
- **H5 — Complexity value:** complex models/hybrids outperform simpler models on shared dates and equal information sets; complexity is not presumed beneficial.
- **H6 — Rules-based strategy reproduction:** source-specified indicator/seasonality/CCI rules produce report-consistent trade signals and performance only where all implementation details and contract data are identifiable.

## Registered paper-by-paper methods

The machine-readable inventory is `results/phase94/PAPER_METHOD_REGISTER.csv`; the narrative crosswalk is `results/phase94/PAPER_METHOD_REGISTER.md`. Those records are the scope authority. The inventory contains the following groups:

- **Index/equity forecast models:** KNN; linear regression; SVR/SVM; decision-tree regression; MLP/SLP; RBF network; Random Forest; XGBoost/gradient boosting; Lasso/Ridge/Elastic Net; AdaBoost; LSTM; RNN; GRU; CNN; TCN; BE-LSTM/backward feature elimination; LSTM-GRU, CNN-RNN, CNN-TCN and LSTM-TCN hybrids; Naïve persistence; plus the source-specified multi-window and feature-ablation comparisons.
- **Macro / options / sentiment feature methods:** OHLCV and turnover; simple technical indicators; 14-period RSI; SMA/EMA and technical-indicator augmentation; USD exchange rate and FII gross buys/sells; FII/DII flows; India VIX; near-expiry PCR; option Greeks, IV and underlying movements; BERT news sentiment combined with LSTM.
- **Trading rules/strategies:** Sherasiya's RF/XGBoost/LSTM buy-sell option signal pipeline versus basic momentum; Atheetha et al.'s simple-average/monthly-trend/seasonality method, one-month European option design, first-Thursday entry, three-day timing window and stop-loss as described; the moving-average crossover versus buy-and-hold comparison; each explicitly described payoff structure in the options-strategy overview that can be turned into unambiguous payoff/risk rules; Shaha's CCI-based NIFTY long-option system. Any mentioned strategy without a reproducible signal/exit is recorded as taxonomy-only until a rule can be derived from source text without inventing undocumented settings.

## Finite execution phases (separate branches)

| Planned phase | Branch | Scope | Closure rule |
|---|---|---|---|
| 94 | `phase-94-paper-method-replication-program` | Inventory, preregistration, validation and orchestration | 14/14 PDFs mapped; each method has an explicit implementation/reproduction status and acceptance gate |
| 95 | `phase-95-daily-forecast-model-replication` | Daily NIFTY price-level/return forecasting methods from U01, U03, U04, U06, U08, U09, U11, U12, U13; common data and paper-specific windows/features where recoverable | All implementable variants run, blocked variants documented, baseline-relative metrics and tests published |
| 96 | `phase-96-moving-average-seasonality-replication` | SMA/EMA crossover, buy-and-hold comparison, Atheetha simple-average/monthly-trend/seasonality and timing/stop rules | Signal-level replication and source-period limitations audited; executable P&L only where instruments/data permit |
| 97 | `phase-97-ml-options-strategy-replication` | Sherasiya ML options classifier/strategy: RF, XGBoost, LSTM, option features and momentum comparator | Exact contract/feature availability gate; otherwise a clearly labelled proxy/prediction-only partial replication and quantified blocker |
| 98 | `phase-98-cci-options-paper-replication-gate` | Shaha CCI rule, including an explicit assessment of whether materially better authorized data enables the original period/contract replay | Reuse Phase 66 evidence unless better eligible source data exist; no identical zero-coverage rerun |
| 99 | `phase-99-options-strategy-taxonomy-replay` | Operationalize source-explicit payoff strategies from U05/U07 and price/risk comparisons | Only strategies with complete written entry, exit, expiry, position and cost rules progress to backtest |
| 100 | `phase-100-cross-paper-reproducibility-synthesis` | Cross-paper robustness, evidence grading, unified tables/figures, complete manuscript/supplements | All 14 papers and all registered methods have a final state: reproduced, not reproduced, inconclusive, partial, or data-blocked |

Phase boundaries are finite. A phase cannot continue parameter-searching to force a positive result. The program ends after Phase 100's audit and manuscript synthesis, even if some methods remain data-blocked.

## Shared methodology

### 1. Source-faithful extraction
For every method preserve the paper's target variable, sampling frequency, features, forecast horizon, sample dates, split procedure, preprocessing, model family, architecture/parameters when reported, baseline, metrics, and limitations. When any component is unavailable in the PDF, use a labelled approximation only for a supplemental comparable test. Do not assert exact replication in that case.

### 2. Data hierarchy and provenance
Prefer author-linked data/code and the paper's stated source, then official NSE/BSE/SEBI/RBI/India VIX sources, licensed/authorized sources available to the repository, and transparent free alternatives for partial replication. Record retrieval date, source URL, version/revision/hash, adjusted/unadjusted definition, timezone, missingness, and allowed reuse. Hugging Face may be used through the existing `HF_TOKEN` Actions secret; never emit secrets or commit credentials. Cached data are reused when provenance/coverage/hash pass. Do not scrape access-controlled services or infer missing quotes.

### 3. Leakage controls
Use chronological splits only. Fit scalers, feature selectors, missing-value handling and hyperparameters on training data only. Create technical indicators from information available at the forecast timestamp; lag end-of-bar inputs until after the bar is complete. Prevent overlapping target windows across split boundaries. Preserve a sealed holdout (the existing Phase 83 2026 holdout remains sealed unless that phase's existing release rules explicitly permit use; this program does not request access). No random shuffled train/test splits for time-series claims.

### 4. Common metrics and baselines
For price level: MAE, RMSE and R², with the naïve persistence predictor on identical target dates. For return/direction: MAE/RMSE in basis points, directional accuracy, balanced accuracy, precision/recall where applicable, Brier/log loss for probabilities, calibration and base-rate comparisons. Report target scale, all denominators and exact observations. Never compare a paper-defined “accuracy” percentage with another source's percentage unless the label and metric are identical. Publish source-metric replication and a standardized common-metric comparison separately.

### 5. Statistical inference
Predeclare one primary metric per paper/phase before outcome inspection. Use paired forecast-error tests (Diebold–Mariano where assumptions and loss series allow), HAC/session-cluster or block-bootstrap uncertainty for dependence, and confidence intervals rather than point metrics alone. For directional claims compare with base-rate-adjusted binomial or suitable block-resampling inference. Apply Holm correction within predeclared families of confirmatory comparisons; identify all other scores as exploratory. Report effect sizes, confidence intervals, p-values, sample/sessions, and sensitivity to test window. Statistical significance alone is not economic value.

### 6. Trading P&L gate
Do not compute an options P&L from index prices or rolling-ATM proxies alone. Require explicit listed contract identity (underlying, CE/PE, strike, expiry, lot size), tradable timestamp, entry/exit price convention, exact data coverage, and a documented corporate-action/contract-spec policy. Prefer historical bid/ask/depth; if only OHLC exists, any bar-based approximation must be labelled and must not be presented as executable. Include contemporary Paytm Money brokerage and statutory charges for each leg/order, exchange/clearing charges, GST, STT, stamp duty, spread, adverse slippage and latency assumptions as applicable to the historical period; disclose fee schedules and run base/adverse stress. Do not invent missing quotes or treat OHLC highs/lows as fills. Options trades with insufficient contract/fill coverage are excluded and counted, not imputed.

### 7. Reproduction decisions
Each paper/method gets one final label:
- **REPRODUCED:** source procedure and reported result metric are regenerable within declared tolerance on the matching sample, and leakage/metric checks pass.
- **PARTIAL:** some method components tested but source universe, time window, inputs or execution assumptions differ.
- **NOT REPRODUCED:** valid comparable data and faithful procedure were available, but the stated result did not reproduce within the preregistered tolerance.
- **INCONCLUSIVE:** data/test power or uncertainty cannot resolve the claim.
- **DATA-BLOCKED:** required data, contract mapping, code or permissions unavailable.
- **NOT IDENTIFIABLE:** paper lacks sufficient procedural detail to uniquely implement the method; any reasonable operationalization is explicitly separate.
Successful workflow execution is not evidence of successful scientific reproduction.

## Statistical and scientific acceptance gates

- 14/14 source mappings; each model/rule has a registry ID, a written implementation plan, data need, target/metric, current prior-test reference and phase assignment.
- Exact paper-metric tests and standardized-baseline tests kept separate.
- All comparisons use shared dates/rows for model ranking or explain deviations.
- Zero leakage tests fail; missingness, dates, target alignment and split boundaries are unit-tested.
- Test sample and session counts are reported; no metric is emitted as meaningful for an empty test/trade set.
- Options result gates include >=95% required entry/exit coverage and at least 20 completed OOS trades unless a source-faithful paper requires a different explicitly preregistered minimum; below-gate findings cannot establish profitability.
- Strategy findings must survive base costs and report adverse-cost/slippage sensitivities. No strategy promotion from prediction accuracy alone.
- 2026 holdout remains sealed under existing Phase 83 rules.
- Automated workflow has push and `workflow_dispatch`; each downstream phase runs on its own branch.
- README, phase status, research log, chat/decision log and error log updated after each step and outcome.
- Full manuscript has methods, results, discussion, strengths, limitations, appendices, source claims versus independent findings, tables and figures.

## Decisions already fixed (prevent repeat failures)

1. Phase 66's CCI adaptation had zero completed trades and zero entry/exit coverage. Do not call its zero summary fields zero return or a failed expectancy. Do not rerun unchanged rules without materially better data.
2. Phase 92's IV/synthetic-proxy/OI predictor line has reached its finite stopping boundary and was negative for the registered incremental target. Do not extend the same hypothesis across years or tune for a positive result.
3. Phase 60/61/68 evidence says metadata-only option data source searches and stale Hugging Face files do not supply exact contract rows. Validate bytes and event dates; don't repeat failed sources.
4. Reported “95%/99% accuracy” on normalized price levels is not comparable to direction accuracy or trade returns. Replicate the metric exactly, then evaluate shared OOS baselines.
5. Daily index forecasting does not imply option strategy profitability. Keep predictive performance and executable net P&L as separate endpoints.
6. Do not reproduce hidden model reasoning in repository files. Store auditable decisions, actions, outcomes and concise rationale only.

## Completion / stopping rule
Stop after Phases 94–100 have been run or explicitly closed as data-blocked/inconclusive with evidence. Do not add phases indefinitely. If no executable options data are legally available, still finish all prediction-model replications and source-faithful signal-level tests, record option P&L as blocked, and complete the manuscript without claiming a usable strategy.

## Outputs
- `results/phase94/PAPER_METHOD_REGISTER.csv`
- `results/phase94/PAPER_METHOD_REGISTER.md`
- `PHASE94_STATUS.md`, `PHASE94_RESEARCH_LOG.md`, `PHASE94_ERROR_LOG.md`, `PHASE94_CHAT_LOG.md`
- `.github/workflows/phase94-literature-replication-registry.yml`
- README current checkpoint
