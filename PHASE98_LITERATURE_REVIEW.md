# Phase 98 Literature and Evidence Review

**Version:** 1.0  
**Reviewed:** 2026-10-10  
**Scope:** Opening-range breakout (ORB), intraday continuation, India VIX as a risk-state measure, transaction costs, inference and backtest overfitting.  
**Relationship to preregistration:** This is contextual literature; it does not alter the frozen Phase 98 hypotheses, dates, strategy rules, cost scenarios or stopping rule. The Phase 98 evaluation is a NIFTY options replay, while much of the cited ORB evidence concerns U.S. futures or other index futures. It must not be treated as a direct estimate of NIFTY-options profitability.

## Executive synthesis

The evidence is mixed rather than uniformly supportive of opening-range breakouts. Older peer-reviewed studies find intraday trend/ORB effects in some futures samples, but the same research reports that apparent full-sample profitability can weaken substantially across subperiods. A newer September 2026 SSRN preprint reports that none of 225 preregistered ORB configurations in nine U.S. futures markets met its prespecified positive criteria after costs. That preprint is not peer-reviewed and concerns different instruments, but it strengthens the case for a fixed, falsifiable test rather than a broad search over many range lengths, exits and filters.

The source for India VIX describes it as an option-order-book-derived estimate of expected volatility over the next 30 calendar days. It is not itself a directional forecast. Phase 98 therefore uses VIX only as a preregistered high-volatility exclusion, lagged to the prior session; it does not claim that high VIX predicts the sign of NIFTY returns.

Multiple-testing and backtest-overfitting research warns that evaluating many candidate strategies and selecting a winner inflates apparent significance. Phase 98 addresses this risk by testing one frozen breakout specification, one frozen prior-only VIX treatment, fixed development/validation dates, two declared primary tests with Holm adjustment and a protected 2026 holdout that remains sealed. This is necessary discipline, not a guarantee against all sources of bias.

The data are minute OHLC(+volume/open-interest where supplied), not a complete historical bid/ask/depth record. Fixed adverse slippage at bar-open prices is a sensitivity model, not a fill reconstruction. A profitable OHLC replay, if observed, would still require independent confirmation using verified contract metadata and more realistic executable-quote data before any paper/live consideration.

## Thematic review

### 1. Opening-range breakout evidence

**Holmberg, Lönnbark and Lundström (2013).** Their peer-reviewed article, “Assessing the profitability of intraday opening range breakout strategies,” proposes a way to examine ORB-like filters and reports evidence of intraday trending in U.S. crude-oil futures. The authors also report that results from the full sample were not robust to time splits and were largely explained by the most recent, more volatile subperiod. This is an important warning: an apparent full-sample effect may be regime- or period-dependent. The asset, market microstructure, holding horizon and price data differ from the NIFTY option vertical tested here, so the paper motivates robustness checks but does not validate this particular strategy.

Source: Holmberg, U., Lönnbark, C., & Lundström, C. (2013). *Assessing the profitability of intraday opening range breakout strategies*. Finance Research Letters, 10(1), 27–33. https://doi.org/10.1016/j.frl.2012.09.001

**Tsai et al. (2019).** “Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets” uses one-minute data for DJIA, S&P 500, NASDAQ, Hang Seng and TAIEX futures over 2003–2013. The published abstract reports statistically significant results in the examined setups and notes that the effective probing time differs by market. The finding supports treating opening-window definition as market-specific; it does not establish that a 15-minute NIFTY range or option debit spread is profitable. The study concerns index futures rather than options and predates newer market structure and fee conditions.

Source: Tsai, Y.-C., Wu, M.-E., Syu, J.-H., Lei, C.-L., Wu, C.-S., Ho, J.-M., & Wang, C.-J. (2019). *Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets*. IEEE Access, 7, 32061–32071. https://doi.org/10.1109/ACCESS.2019.2899177

**Fetna (2026 preprint).** “Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data” is a recent SSRN preprint (posted September 2026) that tests a large prespecified grid across nine U.S. futures markets. Its abstract reports that zero of its 225 cells met its positive decision rule and that aggregate confirmation-window gross profits became losses under its $25 round-trip-cost scenario. It argues that very small gross edges can be consumed by trading friction. This work is not peer-reviewed as of this review date and studies U.S. futures, so its numbers should not be imported into the NIFTY options analysis; its design and cost-aware falsification emphasis are relevant methodological context.

Source: Fetna, M. (2026). *Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data*. SSRN preprint, posted 14 September 2026. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428398

**Synthesis.** ORB evidence depends on market, sampling period, session alignment, exit conventions and costs. The available literature does not justify assuming that the ORB effect transfers to NIFTY options. Phase 98 therefore tests a single predeclared instrument expression and does not tune opening lengths or thresholds after observing validation outcomes.

### 2. India VIX: what it measures and what it does not

The National Stock Exchange describes India VIX as a near-term expected-volatility measure derived from best bid/ask prices in NIFTY options and calibrated to indicate expected volatility over the next 30 calendar days. A high value signals greater expected magnitude of market fluctuation, not a reliable up/down direction.

Official source: NSE India, *India VIX Index*. https://www.nseindia.com/static/products-services/indices-indiavix-index  
Methodology background: NSE, *India VIX white paper*. https://nsearchives.nseindia.com/s3fs-public/inline-files/white_paper_IndiaVIX.pdf

Phase 98's filter is deliberately narrow: compare the prior trading session's VIX close with a 75th percentile calculated from the preceding 252 available closes. It uses the prior close only and fails closed when sufficient VIX history is unavailable. This tests a specified risk-state exclusion, not whether VIX is generally predictive, and not a family of quantile or window choices.

### 3. Multiple testing and backtest overfitting

**Harvey, Liu and Zhu (2016).** Their Review of Financial Studies paper addresses the proliferation of claimed factors and argues that ordinary significance thresholds are too permissive after many tests; their framework proposes materially higher hurdles for newly mined findings. While focused on the cross-section of returns rather than ORB specifically, the lesson applies to iterative strategy research: the number of tried configurations is part of the evidence, and a nominal p-value from a selected winner can be misleading.

Source: Harvey, C. R., Liu, Y., & Zhu, H. (2016). *… and the Cross-Section of Expected Returns*. Review of Financial Studies, 29(1), 5–68. https://doi.org/10.1093/rfs/hhv059  
Public working paper: https://www.nber.org/papers/w20592

**Bailey et al. (2017).** “The Probability of Backtest Overfitting” proposes combinatorially symmetric cross-validation to estimate the risk that a selected backtest winner is overfit. The paper emphasizes that a single holdout can be unreliable when many alternatives have been compared and selected. Phase 98 does not implement the full PBO framework because it is not evaluating a large candidate matrix in this phase; instead, it reduces researcher degrees of freedom by freezing one rule and using a separate time validation sample. This is a mitigation, not proof that PBO is zero.

Source: Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2017). *The Probability of Backtest Overfitting*. Journal of Computational Finance. https://doi.org/10.21314/JCF.2016.322  
Open repository copy: https://escholarship.org/uc/item/4w1110bb

### 4. Transaction costs, quote quality and executable fills

For an option vertical, gross spread P&L can be small relative to the friction on four leg-side fills (long and short at entry and exit), particularly with option bid–ask spread, market impact and fast price movement. Brokerage and statutory levies are only part of execution friction; an OHLC dataset cannot reconstruct the exact spread, queue position, available depth, latency or whether both legs could execute at the modeled prices.

Phase 98 therefore uses one and two adverse ticks on each leg-side fill, explicit brokerage assumptions, date-aware charges and a severe statutory-fee multiplier. These costs are a transparent stress test, not a claim that they encompass every execution cost. For exact practical inference, the account's applicable broker tariff and complete historical bid/ask or trade/quote data are necessary. The account category is not specified here, so the registered ₹10/order base case must be interpreted as the frozen legacy-tariff assumption; the ₹20/order stress case is not guaranteed to represent the maximum possible friction.

Paytm Money's published notice describes brokerage changes for new users from 25 August 2023 and continuation of the old rate for existing-user cohorts. That means one flat account-agnostic fee cannot be asserted as the actual rate for every account. This does not change the preregistered computation; the limitation is carried into interpretation.

Source: Paytm Money, *Brokerage charges increase from 25th Aug ’23; existing users will continue on old brokerage charges*. https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/

#### 6. Practitioner video and independent online backtest material (low evidential weight)

The targeted search also found practitioner explainers and self-published NIFTY/Bank NIFTY analyses. These are useful for documenting what retail traders mean by a “15-minute ORB” and for discovering alternate hypotheses, but they are not peer-reviewed evidence. Their strategy definitions, fee assumptions, dataset quality, survivorship/selection risks, source data, and complete trade ledgers are not uniformly independently reproducible. They should not be assigned the same weight as a peer-reviewed paper or an audited replay.

- **Stock Menthol (YouTube, 13 September 2026):** a video description titled around the 15-minute opening-range breakout discusses marking the first 15-minute range and adds a Fair Value Gap filter. The listing references a funded-trader service and a backtesting feature; the search listing alone does not establish independent net profitability. It is a description of a popular retail rule, not validation. https://www.youtube.com/watch?v=_PQHVKKGeB4
- **Trader Swami (YouTube, 8 February 2023):** a “15 minute ORB” tutorial describes an intraday breakout and scanner for Bank Nifty, Nifty and stocks. Its description is educational and makes broad promotional claims; no verified source-faithful option-level results are established by the listing. https://www.youtube.com/watch?v=cLLEKlvplVQ
- **Finance With Sai (19 March 2025):** a self-published Bank Nifty ORB backtest page explicitly says it compares results before and after slippage/charges. It is closer to the execution-cost question than a pure chart tutorial, but trades the index/spot signal and discusses implementation in F&O; its assumptions and sample still differ from this Phase 98 long/short option vertical. https://financewithsai.com/orb-backtest-on-banknifty/
- **Intraday Lab (1 April 2026):** a self-published article reports an analysis of NIFTY's first 15-minute candle over 2017–2026. It states that popular breakout interpretations can fail, but the article is not peer reviewed and Phase 98 does not import its reported figures as ground truth. https://intradaylab.com/blog/nifty-first-15-minute-candle-analysis
- **Intraday Lab (7 May 2026):** a separate practitioner article says it compared NIFTY breakout rules on about 12 months of data, including false-breakout observations. Because the search result does not provide a reproducible full data/ledger package, use it only as practitioner context. https://intradaylab.com/blog/breakout-trading-nifty-what-actually-works

Across practitioner sources, the repeated warning is that an appealing chart rule is not equivalent to a tested, post-cost option strategy. Their claims are not aggregated or meta-analyzed here because the designs and evidence quality are not sufficiently comparable.

### 7. Indian-market microstructure, option efficiency and intraday volatility evidence

**Aggarwal and Gupta (2009).** Using daily NIFTY 50 index-option closing data from January 2006 to March 2009, this paper examines call/put spreads, box spreads and butterfly convexity relationships while incorporating bid–ask, brokerage and taxes. It reports frequent and large box-spread relationship violations, but fewer violations in call/put spreads and convexity, and emphasizes that market frictions materially affected arbitrageurs' ability to capture violations. This is Indian options-market evidence, but it studies no-arbitrage relationships using older daily closes—not an intraday directional ORB strategy or modern weekly expiry verticals.

Source: Aggarwal, N., & Gupta, M. (2009). *Empirical Evidence on the Efficiency of Index Options Market in India*. Asia-Pacific Journal of Management Research and Innovation, 5(3). https://doi.org/10.1177/097324700900500311

**Vipul (2009).** “Box-spread arbitrage efficiency of Nifty index options: The Indian evidence” uses time-stamped transactions to identify box-spread mispricing. Its abstract reports that cost-adjusted opportunities could occur frequently but generally did not persist even for two minutes; liquidity/immediacy risk and volatility were related to observed mispricing. This supports strict timestamp-matched trading and skepticism about acting on stale or asynchronous option quotes. It does not directly validate the ORB signal.

Source: Vipul (2009). *Box-spread arbitrage efficiency of Nifty index options: The Indian evidence*. Journal of Futures Markets, 29(6), 544–562. https://doi.org/10.1002/fut.20376

**Patnaik and Thomas (2004).** “Profitability of Trading Strategies on High-Frequency Data, with Trading Costs” tests Indian equity-market momentum and contrarian rules on high-frequency order-book data for 1996–2002, with explicit execution/price-impact costs. The abstract reports short-run momentum profitability in some strategies but declining profits as the formation period lengthened, after controlling for microstructure effects. This is an older single-stock equity sample, not current NIFTY options, but it illustrates why signal horizon and executable prices matter.

Source: Patnaik, T. C., & Thomas, S. (2004). *Profitability of Trading Strategies on High-Frequency Data, with Trading Costs*. SSRN working paper. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=568363

**Chakrabarti and Kumar (2020).** This peer-reviewed study investigates the high-frequency (five-minute) relationship between NIFTY returns and model-free implied volatility. It reports a negative and asymmetric short-term relationship, with negative return innovations particularly associated with sharp rises in India VIX; its authors caution that simple VAR behavior does not fully explain extreme joint movements. The paper supports treating volatility and market direction as distinct quantities; it does not establish that a prior-day VIX percentile identifies profitable ORB sessions.

Source: Chakrabarti, P., & Kumar, K. K. (2020). *High-Frequency Return-Implied Volatility Relationship: Empirical Evidence from Nifty and India VIX*. Journal of the Developing Areas, 54(3), 53–68. https://ideas.repec.org/a/jda/journl/vol.54year2020issue3pp53-68.html

### 8. Data-source provenance and coverage limitations

The upstream *India Index & Options — 1-minute OHLC* dataset identifies its files as one-minute OHLCV(+OI) bars for NIFTY and other Indian index spot/option chains. Its dataset card cautions that option coverage is partial, with illiquid or far-out strikes often sparse or absent, and presents the data as educational/as-is rather than an exchange-certified quote record. This matches the main Phase 98 operational risk: a signal can exist while one or both selected option legs or exit opens are absent. The Phase 98 code therefore uses exact timestamp-and-strike matches, does not impute gaps, records exclusions, pins a source revision, and requires coverage and source-read gates.

Source: Hugging Face dataset card and source revision tree: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/tree/0f4800e43e6f96cec0794369d78eb4d3c4211ef5

The dataset schema uses timezone-aware IST timestamps and exposes an `open_interest` field in its documented schema; this is why the runner must match Parquet's actual Arrow timestamp type and normalize the OI alias only when present. Neither OHLCV nor OI guarantees that a two-leg order could have filled at the modeled bar opens.

## Review of the user-supplied PDF literature set

I also reviewed the 13 PDFs supplied in this project conversation. These papers cover Indian options trading, derivative strategies, NIFTY price-level forecasting, machine learning, moving averages, investor flows, sentiment and volatility. They are not all direct ORB studies. Their reported classification accuracy or index-price error metrics cannot be converted into expected option-strategy profitability without a leakage-safe signal definition, executable contract selection, leg-specific fills, costs and a complete out-of-sample trade ledger.

### Direct options / strategy papers

**Sherasiya (2025), “Developing A Machine Learning-Based Options Trading Strategy for the Indian Market”** (file: `50375.pdf`, *International Journal for Multidisciplinary Research*, Vol. 7, Issue 4). The paper describes NIFTY weekly/monthly EOD option-chain data over January 2020–December 2024, features including Greeks, IV, strike proximity, OI and volume, and Random Forest, XGBoost and LSTM. Its table reports LSTM accuracy 90.10%, Sharpe 1.95 and total return ₹205,720; it reports XGBoost at 89.20% / 1.78 / ₹196,450 and Random Forest at 87.40% / 1.53 / ₹182,300. Its backtest assumptions are ₹50 per trade and 0.25% slippage on initial capital ₹1 lakh, and it maps predictions to ATM calls or puts with one-day holding. These numbers are claims made by the uploaded article, not independently replicated results. The paper gives a general 80:20 split and mentions cross-validation, but does not provide a complete reproducible dated trade ledger in the supplied document. The exact chronological order of splitting, option-leg execution prices, contract selection, and whether each reported metric is strictly out-of-sample are not sufficiently documented to establish tradable edge. It is exploratory input for future ML research—not validation of this Phase 98 fixed ORB rule.

**Shaha, “An Empirical Study on Options Trading Strategy Using ‘Commodity Channel Index’ for NSE’s Nifty Options in India”** (file: `ssrn-3323746.pdf`; SSRN manuscript). It examines October 2008–September 2018 and reports a CCI-based long ITM call/put rule on monthly options, using a 100% premium gain target, a 50% premium-loss stop and a near-expiry time exit. It reports 68 trades in narrative sections, a 63.25% strike rate, average gain/loss ratio 1.69, and annualized return 232.16%, with assumptions of lot size 50, brokerage/taxes ₹100 and 10% slippage. The article reports p=0.029 for a strike-rate test and p=0.034 against a 100% annual return benchmark. However, its statistical table contains internal count inconsistencies (for example, the summary refers to 68 trades while parts of a table show different totals), the lot-size and fee model is fixed across a decade despite market-rule changes, and the very high return benchmark and long-option methodology require careful interpretation. There is no source-faithful independent rerun in Phase 98, and this is a different monthly CCI strategy, not evidence for ORB.

**Atheetha et al. (2019), “Options Trading Strategy: A quantitative study from an Investor’s POV”** (file: `D0801051829.pdf`, *International Journal of Business and Management Invention*, Vol. 8, Issue 1). It studies seven underlyings (three FMCG shares, three banking shares and one index) with a ₹3 lakh assumed account, monthly European options, a first-Thursday entry rule informed by prior three-year average performance, a 20% target and 30% stop. Reported overall outcomes vary by underlying; examples in the article include 22.99% for Godrej Consumer Products, 18% for Britannia and 6.13% for Dabur, while individual month returns can be very large in both directions. The authors themselves list limited sample length, a narrow set of underlyings, and omitted fundamental aspects as limitations. The method is not a modern high-frequency chain replay; the supplied paper does not establish quote-executable two-sided fills or a complete, account-specific statutory cost model. It is useful as a retail-strategy example and as a reminder of path-dependent drawdowns, not a directly comparable benchmark.

**Chatterjee et al. (2022), “Options Trading Strategies for the Indian Market—An Effective Financial Derivative Tool”** (file: `IJNRD2205074.pdf`, *International Journal of Novel Research and Development*, Vol. 7, Issue 5). This is primarily a descriptive overview of derivative concepts and strategy payoffs (calls, puts and spread/hedging structures). Its conclusion encourages selecting strategies according to market conditions, but it does not provide a reproducible source-pinned trade-level backtest, uncertainty analysis or realistic net P&L. Use it for terminology/strategy taxonomy only, not as profitability evidence.

### NIFTY price forecasting and feature studies

**Bansal, Goyal and Choudhary (2022), “Stock Market Prediction with High Accuracy using Machine Learning Techniques”** (file: `1-s2.0-S1877050922020993-main.pdf`, *Procedia Computer Science*, 215, 247–265). It compares ML/DL approaches for stock-price forecasting and reports stronger predictive performance for selected deep-learning approaches in its experiment. Its target is price prediction rather than a fully costed option strategy; the headline accuracy cannot be treated as evidence of positive NIFTY option returns.

**Kumar and Sharma (2016), “Stock Market Index Forecasting of Nifty 50 Using Machine Learning Techniques with ANN Approach”** (file: `Stock_Market_Index_Forecasting_of_Nifty.pdf`, *International Journal of Modern Computer Science*, Vol. 4, Issue 3). It models next-day OHLC with an ANN and reports average “accuracy” of 99.2152%. Since that metric is reported for price prediction, not a net return simulation, its economic interpretation depends on the accuracy definition, scaling, chronological evaluation and benchmark. The article does not show a Paytm Money costed options ledger.

**Fathali, Kodia and Ben Said (2022), “Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques”** (file: `Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques.pdf`, *Applied Artificial Intelligence*, 36(1), article 2111134, DOI: https://doi.org/10.1080/08839514.2022.2111134). It examines forecasting methods and feature preparation for index-price prediction. It is a useful model-design reference, but forecasts and RMSE-style metrics are not trading returns. It does not directly test a NIFTY debit spread, the Phase 98 entry/exit, leg fill uncertainty or the current cost schedule.

**Bumrah and Budhani (2023), “An Efficient Approach to Forecasting the NIFTY-50 Indian Stock Market’s Daily Closing Price with Artificial Neural Networks”** (file: `9472-Article Text-11108-2-10-20231228.pdf`, *International Journal on Recent and Innovation Trends in Computing and Communication*, Vol. 11, Issue 11). It uses daily data from 1 April 2018 to 31 March 2023 (reported 1,183 observations), including NIFTY, FII inflow/outflow and the dollar exchange rate, and reports MLP as the strongest of the compared neural-network models. It has a small daily-price forecasting sample and no costed trade-level options analysis. Data relations involving FII and FX are candidate features for other research, not for changing Phase 98 after its rules are frozen.

**Kallimath, Darapaneni and Paduri (2025), “Deep Learning Approaches for Stock Price Prediction: A Comparative Study on Nifty 50 Dataset”** (file: `ISMLA+7481.pdf`, *EAI Endorsed Transactions on Intelligent Systems and Machine Learning Applications*). It compares linear regression, LSTM, GRU, CNN, RNN, TCN and hybrid architectures with MSE, R², RMSE, MAE and MAPE. It is a forecasting-model comparison, not a net-return test. The abstract describes some non-linear and hybrid models as stronger, but the result cannot be ranked economically against the different-window naïve-baseline results in the newer Cureus study without aligning sample periods, targets, data preprocessing and forecast horizons.

**Jafar et al. (2023), “Forecasting of NIFTY 50 Index Price by Using Backward Elimination with an LSTM Model”** (file: `jrfm-16-00423.pdf`, *Journal of Risk and Financial Management*, 16, 423, DOI: https://doi.org/10.3390/jrfm16100423). It uses roughly 15 years of daily Bloomberg data and compares LSTM with backward-elimination LSTM for next-30-day closing-price forecasting; it reports “95% accuracy” for BE-LSTM. The study is a price-level prediction exercise, not proof of 95% correct trades or 95% return. Without an independently evaluated signal-to-trade translation, realistic costs and a trade-ledger replay, the number is not actionable strategy evidence.

**Harish B. G. et al. (2023), “NIFTY-50 Stock Prediction Master”** (file: `IJSDR2309053.pdf`, *International Journal of Scientific Development and Research*, Vol. 8, Issue 9). It reports an LSTM prediction accuracy of 83.88% using NIFTY history from December 2011 to December 2021. The supplied article gives broad algorithm descriptions and limited methodological detail for an independent replication; it does not demonstrate cost-adjusted option performance.

**Naik and Inamdar (2024), “Bridging Temporal Dependencies and Sentiment: A Comprehensive Approach to NIFTY 50 Index Prediction”** (file: `IJCSE-V11I10P106.pdf`, *SSRG International Journal of Computer Science and Engineering*, 11(10), 46–53; DOI: https://doi.org/10.14445/23488387/IJCSE-V11I10P106). It proposes LSTM plus BERT sentiment and adds FII/DII, India VIX and near-expiry put-call ratio. This directly aligns with the broader project’s feature classes (where data are reliable and available), but the article emphasizes predicted market direction/trend and qualitative comparative graphics rather than a fully specified, cost-aware strategy ledger. Its abstract does not establish that any feature improves net options returns after multiple-testing adjustment. The model/feature idea is context for separately preregistered work, not a reason to add features to Phase 98.

**Mahajan et al. (2025), “A Study of the Impact of Moving Averages on Predicting Stock Market Trends: A Study of NIFTY 50”** (file: `JIER-+Vol.+5+No.+3+(2025)+-+Dr.+Deepesh.Formated.pdf`, *Journal of Informatics Education and Research*, Vol. 5, Issue 3). It studies SMA/EMA and crossover/trend confirmation over 2010–2023, with a stated paired-sample comparison against buy-and-hold. Its text also cites very high prediction-accuracy figures from multiple other studies/models, which are not commensurate with a standalone strategy return. A high “accuracy” in a price/trend target is not sufficient evidence without clear target definitions, a truly untouched chronological evaluation, a complete transaction-cost model, exposure controls and net P&L. This broadens the indicator literature but does not establish an ORB edge.

**Sain and Singh (2026), “Open and Close Price Forecasting of the NIFTY 50 Stock Index Using Machine Learning: A Multi-Window Study of Feature Engineering and Model Tuning”** (file: `CureusJournals_1986620261002-185337-d4go5h.pdf`, *Cureus Journal of Computer Science*, published 1 October 2026, DOI: https://doi.org/10.7759/s44389-026-00306-5). It compares 12 models against naïve persistence on 5-, 10- and 20-year chronological windows for next-day open/close. Its reported results show linear models (Linear Regression, Ridge and Lasso) are more stable than Random Forest/XGBoost on the 10- and 20-year windows; tuned complex models often generalize worse than the naïve baseline on long windows. This recent multi-window result is a useful caution against complexity and supports strong naïve baselines, but it still predicts index prices, not option P&L. Its own limitations note that test periods differ across historical windows and recommend aligned out-of-sample periods and walk-forward validation.

### Cross-paper evidence assessment

The user-supplied PDFs contribute feature ideas—Greeks, IV, OI/volume, spot/futures relationships, VIX, PCR, FII/DII, FX, sentiment—and a range of directional/price-prediction approaches. The directly option-focused papers are more relevant to trading, but their sample periods, rule definitions, slippage models, cost assumptions and reproducibility differ substantially. The predictive-model papers report accuracy/error metrics, but most do not bridge the gap from price forecast to feasible, fully costed options execution.

For Phase 98, these sources therefore inform hypotheses and interpretation only. They do **not** justify changing the already-registered ORB/VIX rules, selecting a threshold after observing results, or promoting an unreplicated published claim. For future separate phases, promising hypotheses include adding FII/DII/VIX/PCR or sentiment only with point-in-time data availability, strict walk-forward splits, ablation tests, multiple-testing correction, option-leg trade ledgers and full friction stress; each requires its own pre-registration.

## 5. Research design consequences

These sources support the following fixed safeguards, all consistent with the Phase 98 preregistration:

1. **Avoid validation tuning.** Strategy parameters, split dates, target/stop rules and VIX threshold remain frozen.
2. **Keep the time boundary intact.** Development covers 2021–2023; validation covers 2024–2025; protected 2026 data are not opened.
3. **Use exact observed bars.** No interpolation, forward-filling, signal-close fill or inferred missing exit price.
4. **Separate code success from evidence acceptance.** A workflow can pass while source coverage is invalid; only data, coverage, source-manifest and audit gates allow a performance report to be accepted.
5. **Treat missing signal-session returns as unknown, not zero.** No-breakout sessions are zero-return sessions; sessions with a signal but unavailable data are unknown and block confirmatory inference.
6. **Apply declared cost and statistical rules.** Use the fixed base and stress cost models, adequate trade gates, moving-block confidence intervals, one-sided sign-flip tests and Holm correction for the two primary tests.
7. **Do not promote from this phase.** A positive historical replay remains a research lead because OHLC fills cannot establish executable live fills.

## Applicability map

| Evidence source | Evidence type | Relevant implication | Key transfer limitation |
|---|---|---|---|
| Holmberg et al. (2013) | Peer-reviewed ORB/futures | Subperiod instability can overturn a full-sample result | U.S. crude futures; not NIFTY options |
| Tsai et al. (2019) | Peer-reviewed intraday index-futures study | Opening/probing windows may vary by market | Futures, 2003–2013 sample; no direct option-vertical result |
| Fetna (2026) | SSRN preprint, not peer-reviewed | Costs and preregistration can reverse apparent ORB profitability | U.S. futures and its fee assumptions |
| NSE India VIX page/white paper | Official methodology | VIX is expected volatility, not direction | Does not validate this particular 75th-percentile filter |
| Harvey et al. (2016) | Peer-reviewed multiple-testing methodology | Ordinary p-values are weak after broad searches | Broad asset-pricing factor context, not a direct ORB test |
| Bailey et al. (2017) | Backtest-overfitting methodology | Selection across many variants inflates winner's apparent reliability | Phase 98 fixes one variant and does not estimate full PBO |
| Hugging Face index/options data card | Dataset documentation | Establishes schema and warns about partial option coverage | Public educational dataset, not official exchange quote tape |
| Aggarwal & Gupta (2009) | Indian NIFTY index-option efficiency | Costs affect ability to exploit option pricing relationships | Daily data from 2006–2009; not directional ORB |
| Vipul (2009) | Indian NIFTY option box-spread microstructure | Timestamp precision and short-lived mispricing matter | Arbitrage relation, not ORB strategy |
| Chakrabarti & Kumar (2020) | NIFTY/India VIX five-minute evidence | Return–volatility relation is asymmetric; VIX is not a simple direction forecast | Does not test this specific filter |
| Patnaik & Thomas (2004) | Indian equity intraday strategies with order-book costs | Execution and price impact affect high-frequency strategy returns | Older single-stock sample, not options |
| Paytm Money tariff notice | Official broker communication | Brokerage can vary by account cohort | Account cohort/tariff not individually verified |

## Review limits and outstanding research gaps

- The cited ORB papers are not direct NIFTY option-vertical replications. Indian instrument-level evidence with transparent option fills and costs remains the key gap this experiment addresses.
- The recent 2026 cost-aware futures result is a preprint, not peer-reviewed; it is included as timely methodological context, not settled consensus.
- This is a targeted, source-quality-stratified review rather than an exhaustive systematic review of every database and video. Searches covered indexed academic/official sources and targeted YouTube/practitioner searches; inaccessible or non-reproducible source claims were not treated as evidence. Additional systematic screening and deduplication would be required before describing it as exhaustive.
- The current dataset does not supply a full historical NBBO/depth tape; exact executable P&L remains unverified.
- Broker charges need to be reconciled with the user's actual account tariff before interpreting net returns as personally realizable.

## References

1. Aggarwal, N., & Gupta, M. (2009). Empirical Evidence on the Efficiency of Index Options Market in India. *Asia-Pacific Journal of Management Research and Innovation, 5*(3). https://doi.org/10.1177/097324700900500311
2. Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2017). The Probability of Backtest Overfitting. *Journal of Computational Finance*. https://doi.org/10.21314/JCF.2016.322
3. Chakrabarti, P., & Kumar, K. K. (2020). High-Frequency Return-Implied Volatility Relationship: Empirical Evidence from Nifty and India VIX. *The Journal of Developing Areas, 54*(3), 53–68. https://ideas.repec.org/a/jda/journl/vol.54year2020issue3pp53-68.html
4. Fetna, M. (2026). Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data. SSRN preprint, posted 14 September 2026. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428398
5. Harvey, C. R., Liu, Y., & Zhu, H. (2016). … and the Cross-Section of Expected Returns. *Review of Financial Studies, 29*(1), 5–68. https://doi.org/10.1093/rfs/hhv059
6. Holmberg, U., Lönnbark, C., & Lundström, C. (2013). Assessing the profitability of intraday opening range breakout strategies. *Finance Research Letters, 10*(1), 27–33. https://doi.org/10.1016/j.frl.2012.09.001
7. National Stock Exchange of India. India VIX Index and white paper. https://www.nseindia.com/static/products-services/indices-indiavix-index
8. Paytm Money. Brokerage rate change notice effective 25 August 2023. https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/
9. Patnaik, T. C., & Thomas, S. (2004). Profitability of Trading Strategies on High-Frequency Data, with Trading Costs. SSRN working paper. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=568363
10. Tsai, Y.-C., Wu, M.-E., Syu, J.-H., Lei, C.-L., Wu, C.-S., Ho, J.-M., & Wang, C.-J. (2019). Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets. *IEEE Access, 7*, 32061–32071. https://doi.org/10.1109/ACCESS.2019.2899177
11. Vipul (2009). Box-spread arbitrage efficiency of Nifty index options: The Indian evidence. *Journal of Futures Markets, 29*(6), 544–562. https://doi.org/10.1002/fut.20376

**Access date for web sources:** 2026-10-10.
