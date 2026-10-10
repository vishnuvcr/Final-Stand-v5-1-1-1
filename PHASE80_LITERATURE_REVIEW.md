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
