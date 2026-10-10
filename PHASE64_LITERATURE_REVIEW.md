# Phase 64 Literature Review — Uploaded Papers and External Evidence

## Review scope and grading approach

Fourteen user-provided PDFs were locally text-extracted in full and their first-page title layouts visually checked. For the directly relevant CCI study, the complete rules, assumptions, result tables and conclusion were read. The review separates: (a) a deterministic trading rule, (b) a model that forecasts an index price, and (c) an empirical claim of profitability after realistic execution. Those are different evidence types.

**Decision:** only the CCI monthly long-option breakout is sufficiently specified to implement directly from the PDFs. One additional CCI + EMA confirmation variant is frozen as a novel hypothesis. Price-prediction papers are useful for modeling cautions and future work, but do not themselves provide trading rules or justify trusting price-prediction accuracy as trading profitability.

## 1. Direct strategy candidate — CCI on NIFTY options

### Shaha, Pinkal (2019)
**“An Empirical Study on Options Trading Strategy Using ‘Commodity Channel Index’ for NSE’s Nifty Options in India.”** Proceedings of 10th International Conference on Digital Strategies for Organizational Success; SSRN 3323746. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3323746 (DOI link in SSRN: 10.2139/ssrn.3323746).

**Rule stated in the supplied PDF**
- Uses daily NIFTY CCI (normally 20-period).
- Call: on/between calendar days 3–15 of the month, same-month expiry; CCI rises above -100; then buy the nearest in-the-money call on the day spot NIFTY breaks the high of the CCI signal day.
- Put: on/between days 3–15; CCI falls below +100; then buy the nearest in-the-money put when spot NIFTY breaks the low of the signal day.
- Exit when option price reaches 2× entry price, falls to 0.5× entry price, or at the close of the second-last day of the contract period.
- Assumptions in the paper: lot size 50, brokerage/taxes ₹100, 10% slippage.

**Reported outcomes (paper's claims, not accepted evidence):** period 1 Oct 2008–30 Sep 2018; 68 trades in narrative (42 put + 26 call), summary reports 43 wins + 25 losses = 68, net profit ₹145,362, mean annual profit ₹14,536, reported mean annual ROI 232.16%, 63.25% win rate, AGAL 1.69 and average holding 9 days. It reports a chi-square p=0.029 and an independent two-sample t-test comparing winners' mean profit to losers' mean absolute loss.

**Important quality issues:** the paper's chi-square table labels total trades as 80 even though 43+25=68 and adjacent prose says 68. The independent t-test of mean winning-trade size versus mean losing-trade size is not a valid test that the strategy's mean expectancy is positive. A positive win rate is not a complete risk-adjusted result. The period and instrument history differ from the available source used in this phase. The old paper's 10% slippage is not reproduced by quoting its reported totals; it is tested as an additional adverse sensitivity.

**Phase-64 use:** the rule is registered as candidate A. The rule is translated into a strictly causal minute-level execution model: the CCI signal is known only after signal-day close; breakout trigger is assessed on a later minute; entry occurs at a subsequent observed option price; exits are next-minute fills following close-based target/stop signals. Missing bars are not filled forward.

## 2. Trend filter candidate — moving-average evidence

### Mahajan, Deepesh Y.; Tanted, Nitin; Rewadikar, Siddharth; Chhabra, Jasdeep Singh (2025)
**“A Study of the Impact of Moving Averages on Predicting Stock Market Trends: A Study of NIFTY 50.”** Journal of Informatics Education and Research 5(3), published 17 July 2025. https://jier.org/index.php/journal/article/view/3254.

Uses NIFTY 50 daily data from roughly 2010–2023; examines SMA/EMA, including 50/200 EMA and crossover or trend-confirmation signals. Its stated result is not that crossovers reliably beat buy-and-hold: the paired test does not find significant evidence of higher crossover returns. Correlation between EMA and index level is not evidence that an option strategy is profitable.

**Phase-64 use:** informs candidate B's fixed filter only: calls require close > EMA50 > EMA200, puts require close < EMA50 < EMA200 as of the CCI signal-day close. This is a new adaptation, not the same as the article's crossover test. No filter lengths are tuned.

## 3. Options-specific machine-learning claims

### Sherasiya, Firoz A. (2025)
**“Developing A Machine Learning-Based Options Trading Strategy for the Indian Market.”** International Journal for Multidisciplinary Research 7(4), DOI 10.36948/ijfmr.2025.v07i04.50375. https://www.ijfmr.com/research-paper.php?id=50375.

Describes NIFTY options, option Greeks, implied volatility and underlying-price features, and compares Random Forest, XGBoost and LSTM. Its performance table reports: Random Forest accuracy 87.4%, Sharpe 1.53, total return ₹182,300; XGBoost accuracy 89.2%, Sharpe 1.78, total return ₹196,450; LSTM accuracy 90.1%, Sharpe 1.95, total return ₹205,720. These are the paper's own claims, not reproduced results. Data split, exact feature timestamp alignment, source reconstruction, model selection, and executable fill assumptions are not documented sufficiently to independently reproduce the result. Reported accuracy or Sharpe claims are therefore not accepted as evidence.

**Phase-64 use:** motivates future option-specific feature models only after point-in-time Greeks/IV and execution-grade data pass source gates. Not added to the current numerical candidate universe because Phase 52 has not established sufficient source data and right-to-use evidence for historical prior-minute Greeks/OI/quotes.

## 4. Indian equity technical rules

### Tadas, Harikrishna; Nagarkar, Jeevan; Malik, Sushant; Mishra, Dharmesh K.; Paul, Dipen (2023)
**“The effectiveness of technical trading strategies: Evidence from Indian equity markets.”** Investment Management and Financial Innovations 20(2), 26–40. DOI 10.21511/imfi.20(2).2023.03. https://doi.org/10.21511/imfi.20%282%29.2023.03.

Tests SMA, EMA–RSI and Bollinger Bands–RSI on hourly prices of 14 large NIFTY-50 constituent companies over Jan–Aug 2022. Reported cross-section: SMA was net profitable for 8/14 and beat buy-and-hold for 6/14; EMA–RSI net profitable for 6/14 and beat buy-and-hold for 5/14; Bollinger Bands–RSI net profitable for 11/14 and beat buy-and-hold for 10/14. The short window and equity—not index-options—setting limit direct transferability.

**Phase-64 use:** potential future equity-signal cross-check, but not added as a third option strategy; the current source/strategy test stays finite. A follow-up could test a fixed BB–RSI underlying signal only as a preregistered later phase and must not be presented as already supported for NIFTY options.

## 5. Forecasting papers — useful methodological lessons, not trade rules

### Bansal, Malti; Goyal, Apoorva; Choudhary, Apoorva (2022)
**“Stock Market Prediction with High Accuracy using Machine Learning Techniques.”** Procedia Computer Science 215 (2022), 247–265. DOI and publisher landing page: https://www.sciencedirect.com/science/article/pii/S1877050922020993.

Compares KNN, linear regression, support vector regression, decision-tree regression and LSTM for price prediction. The paper reports LSTM as strongest among its compared methods, including an SMAPE of 4.16, R² around -0.35 and RMSE 22.55, with SVR second by its reported SMAPE/RMSE. Negative R² complicates claims of high prediction quality. Index/price prediction is not option-return prediction, and predictive accuracy alone does not establish after-cost returns.

**Use:** methodological context only; no direct strategy specification.

### Bumrah, Kuljinder Singh; Budhani, Sandeep Kumar (2023)
**“An Efficient Approach to Forecasting the NIFTY-50 Indian Stock Market's Daily Closing Price with Artificial Neural Networks.”** International Journal on Recent and Innovation Trends in Computing and Communication 11(11), DOI 10.17762/ijritcc.v11i11.9472.

Uses daily NIFTY-related information and exogenous USD/FII gross purchases and sales, with SVM/RBF and neural-network variants (MLP/SLP); reports MLP as the best forecasting setup within its experiments. Data period is about April 2018–March 2023. Forecasting design and data-time alignment matter; the article does not provide an independently verified cost-aware option backtest.

**Use:** motivates FII/FX features for a later point-in-time signal study; do not add now because those variables are not present as validated synchronized inputs in the selected data files.

### Sain, Rohit K.; Singh, Amresh K. (2026)
**“Open and Close Price Forecasting of the NIFTY 50 Stock Index Using Machine Learning: A Multi-Window Study of Feature Engineering and Model Tuning.”** Cureus Journal of Computer Science, DOI 10.7759/s44389-026-00306-5. Published 1 Oct 2026. https://doi.org/10.7759/s44389-026-00306-5.

Compares multiple regressors across 5-, 10- and 20-year windows with chronological 80/20 splits, TimeSeriesSplit tuning, engineered moving averages/RSI/returns/volatility, and a naive persistence baseline. Its main conclusion is that linear/ridge/lasso models are comparatively stable across longer windows; XGBoost/random forest strengths are not stable across windows, and feature engineering adds limited gains. The authors note results are specific to the chosen datasets/splits/targets and recommend walk-forward testing and return/direction targets rather than prices.

**Use:** strong caution against building a complex ML strategy without a persistence baseline and walk-forward test. Not a specific options strategy.

### Fathali, Zahra; Kodia, Zahra; Ben Said, Lamjed (2022)
**“Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques.”** Applied Artificial Intelligence 36(1), 2111134. DOI 10.1080/08839514.2022.2111134. https://doi.org/10.1080/08839514.2022.2111134.

Compares neural sequence methods (RNN/LSTM/CNN) and different input/feature configurations for NIFTY index forecasting. The experiments report regression metrics and differing performance by model/features. This is a prediction benchmark, not an option execution system; forecast metrics are not directly comparable to net P&L or drawdown.

**Use:** modelling context, not an executable rule.

### Jafar, Syed Hasan; Akhtar, Shakeb; El-Chaarani, Hani; Khan, Parvez Alam; Binsaddig, Ruaa (2023)
**“Forecasting of NIFTY 50 Index Price by Using Backward Elimination with an LSTM Model.”** Journal of Risk and Financial Management 16(10), 423. DOI 10.3390/jrfm16100423. https://www.mdpi.com/1911-8074/16/10/423.

Uses 3,986 daily observations (2005–2021), OHLCV plus additional fields/RSI, feature backward elimination and LSTM. The paper reports stronger price-forecast metrics for BE-LSTM than LSTM alone. The target remains the index price; high classification-style accuracy does not establish a tradable option edge and can be inflated by high persistence of price levels.

**Use:** reinforces use of chronological splits and baselines; not added to the strategy universe.

### Naik, Pranav P.; Inamdar, Vadiraj G. (2024)
**“Bridging Temporal Dependencies and Sentiment: A Comprehensive Approach to NIFTY 50 Index Prediction.”** SSRG International Journal of Computer Science and Engineering 11(10), 46–53. DOI 10.14445/23488387/IJCSE-V11I10P106.

Combines LSTM sequence modelling with BERT-based sentiment for NIFTY index prediction. The supplied article concerns model prediction, and does not define a reproducible option entry/exit and cost model. News timestamps, source survival and sentiment availability at trade time would need strict timestamp controls before future use.

**Use:** future research lead only; no sentiment strategy added here.

### Kumar, Gourav; Sharma, Vinod (2016)
**“Stock Market Index Forecasting of Nifty 50 Using Machine Learning Techniques with ANN Approach.”** International Journal of Modern Computer Science 4(3), June 2016.

Uses a feed-forward neural network/MLP and RMSE comparisons to forecast NIFTY values. The paper reports satisfactory forecasting results, but does not specify an option strategy or realistic trading cost/execution assumptions.

**Use:** historical forecast context only.

### Kallimath, Sushma P.; Darapaneni, Narayana; Paduri, Anwesh Reddy (year/issue as indicated in supplied PDF)
**“Deep Learning Approaches for Stock Price Prediction: A Comparative Study on Nifty 50 Dataset.”** EAI Endorsed Transactions on Intelligent Systems and Machine Learning Applications.

Compares LR, LSTM, GRU, CNN, RNN, TCN and hybrid networks, with results depending on preprocessing/optimizer and model setup. Predictive regression metrics do not establish economic value after execution costs and data leakage controls.

**Use:** model-comparison background; no new model promoted.

### Harish, B. G.; ChetanKumar G. S.; Radder, Raghavendrareddy; Manoj K. (2023)
**“NIFTY-50 STOCK PREDICTION MASTER.”** International Journal for Science and Development Research 8(9), Sept 2023.

A project-style overview of forecasting/time-series methods, concluding neural models can provide useful forecasts. It lacks the detail needed to freeze a deterministic option strategy and verify costs, point-in-time data lineage, and independent validation.

**Use:** not an evidence-grade trading strategy; model context only.

## 6. Descriptive options research and educational material

### Atheetha S.; Mondal, Simran; Dhanusha, N.; Raghunandan H. J. (2019)
**“Options Trading Strategy: A quantitative study from an Investor's POV.”** International Journal of Business and Management Invention 8(1), 18–29.

Studies monthly options with a small collection of stocks/indices and a simple average of prior three years' returns to select near-the-money/out-of-the-money positions. It considers return, Sharpe-like comparisons, monthly/seasonality effects and timing risk; the PDF notes many cases where investors lost and concludes timing risk matters. The approach is descriptive, limited in asset/sample scope and does not provide a robust independent OOS process directly reusable for NIFTY intraday options.

**Use:** supports the need to measure timing risk and full trade lifecycle rather than just entry signals.

### Chatterjee, Partha, et al. (2022)
**“Options Trading Strategies for the Indian Market—An effective Financial Derivative Tool.”** IJNRD 7(5), May 2022.

Primarily an educational survey/examples of common positions (including straddles, spreads and other structures) rather than a reproducible backtest with a frozen dataset and execution model.

**Use:** vocabulary/strategy taxonomy only; no P&L claim accepted.

## 7. External source findings

### Dataset source
The data source used for this phase is the community dataset https://huggingface.co/datasets/thetrademarkk/india-index-options-1m, pinned to commit 3eacf762d401efd9a08e804592fa7882b354c4a2. The source provides minute-level NIFTY index data and option contract files keyed by expiry. Its published license is CC-BY-NC-4.0 and the documentation warns of incomplete observations, especially in less liquid strikes. Attribution is required and the non-commercial restriction applies; this phase does not redistribute raw data and never treats absent OHLC rows as quotes.

### Overfitting and trading evidence
Phase 49's literature review includes White's Reality Check / Hansen SPA and backtest-overfitting work. These sources support preregistering the exact strategy family and correcting for the number of candidates instead of selecting the best observed result post hoc. This phase therefore tests only two frozen variants and keeps 2026 outside candidate selection.

## 8. Cross-paper conclusions and strategy decisions

1. **Use the CCI strategy because it has explicit entry and exit rules.** Its published results have count inconsistency and methodological limitations; only a fresh independent test can support its value.
2. **Add one trend filter, not a grid.** The EMA study does not establish that crossovers significantly outperform buy-and-hold; the filter is an uncertain, fixed hypothesis.
3. **Do not start deep learning here.** Many supplied ML papers predict price levels, and the latest multi-window article cautions that complex models are often inconsistent and persistence is strong. Phase 52 has also not passed its feature-source gate for a Greeks/OI-based options ML model.
4. **Distinguish forecast quality from net trading value.** Any later model must convert forecasts to a preregistered tradable signal and assess net P&L after the same execution/cost model.
5. **No paper result is imported into Final Stand as validated P&L.** The new Phase-64 test is exploratory/validation evidence with explicit coverage and statistical gates and cannot change the canonical strategy.

## References and links

- Shaha (2019), CCI options strategy: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3323746
- Mahajan et al. (2025), NIFTY moving averages: https://jier.org/index.php/journal/article/view/3254
- Sherasiya (2025), ML-based NIFTY options: https://www.ijfmr.com/research-paper.php?id=50375
- Tadas et al. (2023), Indian equity technical trading: https://doi.org/10.21511/imfi.20%282%29.2023.03
- Bansal et al. (2022), stock market prediction: https://www.sciencedirect.com/science/article/pii/S1877050922020993
- Bumrah & Budhani (2023), NIFTY ANN forecasting: https://doi.org/10.17762/ijritcc.v11i11.9472
- Sain & Singh (2026), multi-window NIFTY ML study: https://doi.org/10.7759/s44389-026-00306-5
- Fathali, Kodia & Ben Said (2022), NIFTY ML prediction: https://doi.org/10.1080/08839514.2022.2111134
- Jafar et al. (2023), backward-elimination LSTM: https://doi.org/10.3390/jrfm16100423
- Naik & Inamdar (2024), LSTM/BERT sentiment: https://doi.org/10.14445/23488387/IJCSE-V11I10P106
- Dataset source: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
