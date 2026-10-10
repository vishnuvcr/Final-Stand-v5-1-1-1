# Phase 80 — Literature review: external and user-supplied papers
Audit date: 2026-10-10

This synthesis separates claims reported by sources from results independently reproduced by Final Stand. Predictive accuracy is not evidence of profitable option execution after costs.

## 1. Published empirical research relevant to strategy axes

### Bhat, Pandey & Rao (2024) — option returns by market clock
- Citation: “The asymmetry in day and night option returns: Evidence from an emerging market,” Journal of Futures Markets 44(8), 1320–1337. DOI: https://doi.org/10.1002/fut.22512
- Reported result: delta-hedged short NIFTY option strategies show positive/significant overnight returns and negative intraday returns; the gap is weaker on underlying jump days.
- Design implication: holding clock is an independent research dimension. Do not apply this directly to static straddles, iron flies or spreads; hedging, jumps and execution costs differ.
- Evidence status: literature motivation; this repo has not directly replicated the finding.

### Mutum (2020) — volatility forecasting and sentiment
- Citation: “Volatility Forecast Incorporating Investors’ Sentiment and its Application in Options Trading Strategies: A Behavioural Finance Approach at Nifty 50 Index,” Vision: The Journal of Business Perspective 24(2), 217–227. DOI: https://doi.org/10.1177/0972262920914117
- Reported inputs: absolute returns, daily high-low range, realized volatility, India VIX, advance-decline ratio and put-call open-interest ratio/changes.
- Reported result: the abstract says sentiment variables improve volatility forecasting and reports simulations of straddle strategies 15 days before maturity based on volatility forecasts, with potential improvement when sentiment, particularly IVIX, is included.
- Design implication: preregister volatility forecast/VRP and sentiment as selector features. Features must be lagged to when known; option-specific IV/OI must be point-in-time and contract-identified.
- Evidence status: abstract-level finding; exact costs, tables, data definitions and trade ledger have not been independently reproduced.

### Hora (2025) — variance risk premium
- Citation: “Does the variance risk premium (VRP) from NIFTY options drive excess returns in a volatility-selling strategy?” DOI: https://doi.org/10.69889/9035hn40
- Abstract describes five years of daily NIFTY and India VIX data and reports implied variance exceeding realized variance regularly, producing statistically positive VRP.
- Design implication: positive implied-minus-realized volatility is a feature, not proof that a static short-volatility trade earns positive net return. Fix the realized-volatility estimator ex ante and separately test net outcomes/tail risk.
- Evidence status: abstract-level claim; venue quality, detailed data and robustness require appraisal.

### Pillai (2026) — NIFTY short-volatility strategies after frictions
- Citation: “Trading the Volatility Risk Premium on Nifty 50: Strategy Backtest with Realistic Frictions,” SSRN abstract 6876580, posted 24 June 2026: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6876580
- Abstract reports 119 monthly expiry cycles (Jan 2015–Apr 2025), testing ATM short straddle, crash-neutral spread, put-write at multiple moneyness levels, and delta-hedged straddle. It reports all four variants negative annualized net of its stated costs; the 0.94-moneyness put-write is least adverse (reported 91.6% monthly win rate but -0.9% annualized return / Sharpe -0.37).
- Design implication: report tail risk, capital/margin and return on capital; win rate is not the success criterion.
- Limitations: working paper, not peer-reviewed in the cited record; cost inputs differ from Paytm Money, and we have not reproduced it. Treat as outside benchmark, not our data.

### Patra (2025) — machine-learning volatility forecast
- Citation: “Volatility Modelling for Indian Markets,” SSRN, posted 1 December 2025: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5748922
- Abstract reports using daily NIFTY options data (2020–2025) to forecast 30-day realized variance with linear models and a feed-forward neural network; ATM and OTM skew features carry predictive information.
- Design implication: ATM/skew and IV/RV could be tested as frozen volatility selectors only after rights and point-in-time surface coverage are proven. Forecast error and option strategy net P&L must be reported separately.
- Evidence status: working-paper abstract; not independently reproduced.

### Bailey & López de Prado (2014) — multiple testing
- Citation: “The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality,” The Journal of Portfolio Management 40(5), 94–107. DOI: https://doi.org/10.3905/jpm.2014.40.5.094
- Core point: selecting the best from many parameterizations inflates apparent performance; multiple trials and non-normality need to be accounted for.
- Design implication: do not brute-force every signal/threshold/structure then report the winner. Freeze limited families, log trials, use Holm correction and cluster-aware intervals, then validate once on a sealed holdout.

## 2. User-uploaded papers reviewed

### 50375.pdf — Sherasiya (2025), “Developing A Machine Learning-Based Options Trading Strategy for the Indian Market”
- Reported recipe: features reportedly include Greeks, IV, spot, strike proximity, time to expiry, OI/change, volume, RSI/MACD. Random Forest, XGBoost and LSTM are compared; the reported trading rule buys an ATM call on “Buy” and an ATM put on “Sell”, with next-day exit.
- Reported results include LSTM accuracy 90.10%, Sharpe 1.95 and total return ₹205,720; the paper describes initial ₹100,000, “₹50 per trade” costs and 0.25% slippage.
- Reproducibility concerns: the accessible methods describe an 80:20 split/grid search but do not establish purged/embargoed chronological splits, a clear model freeze before final test, exact contract/expiry mapping for every trade, full statutory charges or a reproducible trade ledger. A one-day prediction target does not guarantee net option profitability.
- Decision: hypothesis only; do not import the reported metrics into this repo’s result ledger.

### ssrn-3323746.pdf — Shah (2019), CCI NIFTY option strategy
- Reported idea: CCI momentum selects long ITM options seeking large premium rises on a roughly two-week horizon; annexes include older trades and state a 10% slippage estimate.
- Prior Final Stand replication: Phase 66 translated CCI_BASE and CCI_EMA_FILTER candidates both generated zero completed trades. Performance is not estimable. Rule mapping and coverage need diagnosis before reusing; do not loosen thresholds because the sample is empty.
- Decision: documented replication gap, not proven success/failure.

### JIER, Vol. 5 No. 3 (2025) — Mahajan et al., moving averages on NIFTY 50
- Abstract reports SMA/EMA/crossover trend prediction on 2010–2023 data and comparison with buy-and-hold.
- Decision: possible simple directional baseline, not a validated option strategy; the source does not establish exact option contracts and net return after all costs.

### D0801051829.pdf — “Options Trading Strategy: A quantitative study from an Investor’s POV” (2019)
- Appears to study selected securities, trends, multiyear averages and seasonality rather than run a complete per-contract option-chain backtest.
- Decision: weak support for seasonality hypotheses only; not a costs-aware options P&L benchmark.

### IJNRD2205074.pdf — “Options Trading Strategies for the Indian Market—An effective Financial Derivative Tool” (2022)
- Primarily explains option structures with payoff/breakeven tables and qualitative context.
- Decision: useful for validating payoff signs and max-risk definitions in code; not realized-profit evidence.

### Forecast-only NIFTY papers in the supplied packet
- IJCSE-V11I10P106.pdf (“Bridging Temporal Dependencies and Sentiment…”), 1-s2.0-S1877050922020993-main.pdf, 9472-Article Text-11108-2-10-20231228.pdf, CureusJournals_1986620261002-185337-d4go5h.pdf, IJSDR2309053.pdf, ISMLA+7481.pdf, Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques.pdf, Stock_Market_Index_Forecasting_of_Nifty.pdf, and jrfm-16-00423.pdf focus principally on index-price prediction/error metrics or application demonstrations rather than a reproducible net option trading ledger.
- Common limitation: classification accuracy, RMSE/MAE and predicted close price do not guarantee profitable option selection after strike selection, theta, spread, slippage, fees, and drawdowns.
- Possible ideas: sentiment/news if timestamps can be aligned; simple MA/RSI/CCI and temporal models only as preregistered baselines. No complexity is accepted without incremental out-of-sample net P&L and calibration checks.

## 3. Synthesis and implications
1. A key new dimension is exposure clock: the literature finds day/night asymmetry in delta-hedged option returns. Phase 81 tests static structures in matched windows, but is not a direct replication.
2. VRP, IV skew and sentiment are plausible selectors: India VIX, IV/RV, skew, advance-decline breadth and put-call OI are cited in literature. Phase 40–50B already tested VIX-conditioned structures without promotion; new selector testing requires new, aligned feature data rather than repeating thresholds.
3. Forecast metrics and trading P&L are different endpoints.
4. Liquidity and tail risk are first-order; outside working-paper results report negative cost-adjusted returns despite high win rates. Report expected shortfall, drawdown, margin/capital and stressed costs.
5. No outside or uploaded paper establishes a winning strategy for this repo's exact rules, data and costs.

## 4. Actionable follow-up hypotheses (not automatically launched during Phase 81)
- Could point-in-time skew/IV-RV/VIX sentiment improve selection against a frozen simple baseline?
- Does overnight exposure add return after adverse gaps, volume filters, charges and drawdowns?
- Can the CCI source rules be mapped deterministically to the project’s data frequency without retrofitting thresholds?
- Do the 2017–2020 Zenodo and 2024–2026 HF intraday datasets have rights permitting research and storage? Do not ingest until cleared.

## Overall judgement
This literature review justifies further structured testing but not a claim that all combinations have been tried. It records reproducible hypotheses and evidence boundaries. Finish the bounded registered phases before considering another hypothesis.


## 5. Paper-by-paper addendum from the uploaded PDFs

This section adds a more granular evidence map for the papers attached to this project. Across the forecast-centric papers, the reported endpoint is generally index-price prediction (accuracy, R², RMSE, MAE or MAPE), not option P&L under exact contracts and realistic fills.

### Bansal et al. (2022), Procedia Computer Science 215, 247–265
- Title: “Stock Market Prediction with High Accuracy using Machine Learning Techniques.” The PDF compares classic machine-learning forecasting methods including KNN, linear regression and support-vector approaches.
- Research value: a baseline-method catalogue for index direction/price prediction.
- Major boundary: price prediction accuracy alone cannot select the correct option expiry/strike, handle theta/IV changes, or measure after-cost profitability. The headline "high accuracy" must be interpreted against a naive persistence/majority-class baseline and chronological evaluation.
- Decision: no direct option strategy result is imported.

### Bumrah & Budhani (2023), International Journal on Recent and Innovation Trends in Computing and Communication
- Title: “An Efficient Approach to Forecasting the NIFTY-50 Indian Stock Market's Daily Closing Price with Artificial Neural Networks.”
- Data/factors reported: NIFTY daily average closing price, dollar exchange rate, FII gross purchase and sale; models include SVM, RBF and single-/multi-layer perceptrons, with MLP reported best.
- Research value: suggests dollar/foreign-institutional-flow features, if lagged and independently sourced, as possible forecast covariates.
- Boundary: correlation/regression of daily index prices is not evidence FII data adds incremental net-options alpha. FII flows are published aggregate data, and timestamp alignment matters.

### Fathali, Kodia & Ben Said (2022), Applied Artificial Intelligence
- Title: “Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques.” DOI: https://doi.org/10.1080/08839514.2022.2111134
- Research value: a comparatively prominent journal treatment of supervised NIFTY price prediction.
- Boundary: even a well-performing index forecaster still needs a separate option policy, calibrated probabilities, transaction-cost treatment and out-of-sample trading evaluation before it becomes evidence for a strategy.

### Sain & Singh (2026), Cureus Journal of Computer Science
- Title: “Open and Close Price Forecasting of the NIFTY 50 Stock Index Using Machine Learning: A Multi-Window Study of Feature Engineering and Model Tuning.” DOI: https://doi.org/10.7759/s44389-026-00306-5; published 1 October 2026.
- Design: 12 supervised models against Naïve Persistence, forecasting next-day index open/close across 5-, 10- and 20-year windows, with chronological train/test split and a TimeSeriesSplit tuning setup.
- Reported result: linear models (Linear Regression, Ridge and Lasso) generalize more consistently than RF/XGBoost across longer windows; RF/XGBoost can be worse than naive on 10/20-year samples. The paper explains tree extrapolation ceilings as the index makes new highs.
- Research value: supports retaining naive/linear baselines and varying training-window length, rather than assuming complex ML is superior.
- Boundary: forecast errors on index levels still do not establish options profits; the article itself recommends rolling-origin/walk-forward follow-up.

### Jafar et al. (2023/2024), Journal of Risk and Financial Management 16(4), 423
- Title: “Forecasting of NIFTY 50 Index Price by Using Backward Elimination with an LSTM Model.”
- Reported result: backward-feature-elimination LSTM outperforms a plain LSTM in next-30-day closing-price prediction; the abstract reports 95% “accuracy.”
- Research value: supports feature selection as a possible dimensionality-control method.
- Boundary: price-level “accuracy” is not directly comparable to a trading return metric and can be inflated by index-level persistence; no options trade ledger is reported in the reviewed abstract.

### Kumar (2025), SSRN — reinforcement learning
- Title: “Proximal Policy Optimization for Intraday Trading of NIFTY Index Call Options: A Deep Reinforcement Learning Study.” https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5768582 (working paper).
- Abstract describes a long-only one-lot call-option policy trained on 2015–2023 and tested 2024–Aug 2025 under base and 3x slippage, with rewards based on mark-to-market equity net of modeled costs. It reports high risk-adjusted performance in a stylized simulator.
- Research value: a distinct family not equivalent to the existing static-shape sweeps.
- Limitations: SSRN working paper, no cited references shown in the search record, one asset/direction and stylized simulator; claimed results are not independently reproduced. It must not be added midway to Phase 81 or treated as validation.
- Decision: record as a future independently specified replication lead, not a promoted candidate.

### Agarwal (2026), SSRN — NIFTY variance-risk-premium anatomy
- Title: “The Variance Risk Premium in Nifty 50: A Structural Anatomy Across Nine Empirical Filters.” https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6530119 (working paper).
- Abstract reports 43M+ one-minute option bars from Aug 2022 to Mar 2026 (887 sessions), ATM IV derived via Black-76 and realized volatility using Yang–Zhang; reported VRP is positive on 74.9% of days with mean +1.208 volatility points, AR(1) 0.7861 and 25.1% inversions.
- Research value: reinforces use of point-in-time IV/RV, a preregistered estimator, and tail-aware inference; reported serial dependence may be useful for forecasting.
- Limitations: self-reported working-paper result and source/rights/contract coverage must be verified; positive measured VRP does not imply capturable net strategy P&L.

### Additional uploaded ML and index-forecasting papers
- ISMLA+7481.pdf: compares Linear Regression, LSTM, GRU, CNN, RNN, TCN and hybrids using MSE, R², RMSE, MAE and MAPE on a NIFTY dataset. Useful as an algorithm-benchmark catalogue, not options-performance evidence.
- Stock_Market_Index_Forecasting_of_Nifty.pdf (Kumar & Sharma, 2016): MLP/ANN forecast of index levels; its reported 99.2152% “accuracy” is not a net trading return. Requires understanding the error definition and persistence baseline.
- IJSDR2309053.pdf: reports 83.88% forecast accuracy and studies NIFTY / financial-sector index series using historical-price methods and Granger/impulse-response framing. The forecast metric does not test option fills.
- IJCSE-V11I10P106.pdf (Naik & Inamdar, 2024): combines temporal ML and news/sentiment for NIFTY prediction. Potential idea only if news publication timestamps and point-in-time text are auditable; no option-execution proof.
- D0801051829.pdf (Atheetha et al., 2019): compares selected stocks/sectors and seasonality/trend/returns using options concepts and statistical metrics. It does not provide a modern, contract-complete intraday options-chain execution ledger; any seasonality result is exposed to multiple-testing risk.
- IJNRD2205074.pdf (2022): mostly educational/qualitative option-structure survey, useful to validate payoff logic rather than to claim an edge.

### Shah (2019), CCI source paper — additional risk detail
- The supplied SSRN paper reports about 9–10 signals/year and roughly nine-day average holding, describes maximum risk around 58.65% of initial investment, and notes two consecutive losing trades could require a 117.30% loss buffer relative to one starting trade allocation.
- The source claims attractive CCI-based ITM-option performance, but the Phase 66 Final Stand translation had zero completed trades for both CCI_BASE and CCI_EMA_FILTER. An empty replication cannot validate or falsify profitability; deterministic source-rule translation and sample coverage would need diagnosis without tuning to get trades.

### Mahajan et al. (2025), moving averages — result nuance
- The uploaded Journal of Informatics Education and Research paper analyzes NIFTY 50 SMA/EMA trends over 2010–2023 and reports very high correlation/regression fit to the index level. However, it also says the paired test did not find statistically significant evidence that Golden Cross/Death Cross improves returns over a passive approach.
- This is a cautionary null for interpreting high regression R²/correlation as a tradable signal. Index-level forecast results are not option P&L.

## 6. New official regulatory context and source leads (10 October 2026)

- SEBI published updated official reports on 20 August 2026 titled “Study - Profitability of Individual Traders in the Equity Derivatives Segment (FY25–FY26)” and “Study - Trading Behaviour of Individual Traders in the Equity Derivatives Segment (FY25–FY26)”. Links: [profitability study](https://www.sebi.gov.in/reports-and-statistics/research/aug-2026/study-profitability-of-individual-traders-in-the-equity-derivatives-segment-fy25-fy26-_103835.html) and [trading behaviour study](https://www.sebi.gov.in/reports-and-statistics/research/aug-2026/study-trading-behaviour-of-individual-traders-in-the-equity-derivatives-segment-fy25-fy26-_103836.html). This review confirms their existence/date, but detailed figures have not been extracted into the project's data ledger yet and are not quoted here.
- A prior SEBI release (23 Sep 2024) said 93% of individual traders lost money in equity F&O from FY22–FY24 and aggregate losses exceeded ₹1.8 lakh crore across those three financial years: https://www.sebi.gov.in/media-and-notifications/press-releases/sep-2024/updated-sebi-study-reveals-93-of-individual-traders-incurred-losses-in-equity-fando-between-fy22-and-fy24-aggregate-losses-exceed-1-8-lakh-crores-over-three-years_86906.html. This is population-level context, not proof about any particular strategy.
- A separate data route surfaced in Bhat et al.'s data-availability statement: the Zenodo one-minute NIFTY dataset (2017–2020), 320.9 MB, with spot, front futures and per-strike option OHLCV: https://zenodo.org/records/10899828. Its license field is blank, so contents are metadata-only until rights are clarified. Do not ingest or redistribute raw bars without permission.

## 7. Literature-to-project mapping
| Research theme | Existing project coverage | New lead | Current action |
|---|---|---|---|
| Intraday vs overnight option returns | New Phase 81 paired static-structure horizon sweep | Bhat et al. (2024) delta-hedged result | Compare only with explicit method caveat |
| IV/RV / volatility-risk premium | India VIX regime work Phase 40–50B; no promoted strategy | Mutum (2020), Patra (2025), Agarwal (2026), Pillai (2026) | Keep IV/RV as future frozen selector study after source/rights validation |
| Direction/sentiment | Feature and ensemble/selector work | Mutum ADR/PCOI; Naik & Inamdar news sentiment; FII/USD factors | Require timestamped point-in-time inputs and incremental net P&L |
| RL / policy learning | Existing ensemble/selector policy research is not identical to learned position-action policy | Kumar (2025) PPO | Future replication lead only, not added after Phase 81 freeze |
| Moving averages / classical indicators | Prior indicator tests and CCI replication issue | Mahajan (2025), older ML price predictors | Do not equate correlation/accuracy with options profitability |
| All-strategy search completeness | Phase 45 tests 20 new shapes plus 22 reused families; other phases test regime/selector/exit axes | New papers add distinct hypotheses, not proof of an edge | Maintain a finite registered test matrix; no endless expanding grid |

## 8. Literature review conclusion
The review does not identify a robust, reproducibly proven net-profitable NIFTY options strategy that can simply be adopted unchanged. It identifies useful research axes—holding horizon, correctly estimated VRP/IV-RV, sentiment/flow features, and a separately controlled learned policy—but several newer claims are working papers or forecast-only research. The current registered Phase 81 comparison should be completed and inferred before launching another family. All new claims remain external hypotheses until a dated trade ledger with exact contracts, fees, slippage, risk, and validation is reproducibly generated.
