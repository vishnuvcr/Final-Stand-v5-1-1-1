# Uploaded Literature Evidence Audit — U01–U14

**Prepared:** 2026-10-10  
**Use:** source map and critical synthesis for the Final Stand v5 1-1-1 manuscript  
**Corpus:** 14 PDFs uploaded in this conversation  
**Evidence type:** literature audit, not a new experiment

The papers were text-extracted with pdftotext -layout. The summaries below reflect the uploaded PDF text. Where the source reports performance numbers, they are marked as the paper's own claim; Final Stand did not independently reproduce these papers' models or P&L. The uploaded PDFs themselves are not redistributed from this repository.

## Classification key

- **A — direct strategy evidence:** a rule/strategy and option-market outcomes are reported.
- **B — strategy/context:** discusses option signals or strategy construction, but evidence is not sufficiently comparable to an executable, fully costed replay.
- **C — index-price forecasting:** stock/index price prediction, not option strategy P&L.
- **D — conceptual/limited reproducibility:** descriptive strategies, proposed model, or weakly reproducible result.

## Per-paper audit

### U01 — Bansal, Goyal & Choudhary (2022)
- **Uploaded filename:** 1-s2.0-S1877050922020993-main.pdf
- **Citation:** Bansal, M., Goyal, A., & Choudhary, A. (2022). “Stock Market Prediction with High Accuracy using Machine Learning Techniques.” *Procedia Computer Science*, 215, 247–265. DOI: [10.1016/j.procs.2022.12.028](https://doi.org/10.1016/j.procs.2022.12.028).
- **Scope/design:** compares K-nearest neighbours, linear regression, support-vector regression, decision-tree regression and LSTM using price histories for 12 Indian companies over roughly 2015–2021.
- **Paper-reported findings:** the paper's conclusion favours LSTM among tested methods. The extracted results include an example with SMAPE 1.59, RMSE 22.55 and R² -0.11 for LSTM, illustrating that one favourable error measure does not guarantee positive explained variance.
- **Use in this project:** supports inclusion of naïve/linear baselines and multiple metrics instead of relying on one advertised “accuracy” number.
- **Limitations / interpretation:** daily equity-price prediction is not options-strategy evidence; metrics vary with target scaling and sample; the paper does not establish this project's intraday option fills or cost-adjusted returns.
- **Classification:** C.

### U02 — Sherasiya (2025)
- **Uploaded filename:** 50375.pdf
- **Citation:** Sherasiya, F. A. (2025). “Developing A Machine Learning-Based Options Trading Strategy for the Indian Market.” *International Journal for Multidisciplinary Research*, 7(4), July–August 2025.
- **Scope/design:** NIFTY options; describes features from option Greeks, implied volatility and underlying movements; compares Random Forest, XGBoost and LSTM. The paper describes daily end-of-day option-chain/spot observations for January 2020–December 2024.
- **Paper-reported findings:** the result table reports LSTM accuracy 90.10%, Sharpe ratio 1.95 and total return ₹205,720; XGBoost and Random Forest are also reported as profitable.
- **Use in this project:** directly relevant as a hypothesis source for testing Greeks/IV/spot features and comparing ML signals with simpler baselines.
- **Limitations / interpretation:** figures are transcribed as source claims, not independently replicated here. The PDF does not establish a comparable, point-in-time intraday quote/depth record and auditable fill/cost treatment meeting the repository's gate. The reported Sharpe/return cannot be generalized to the current strategies.
- **Classification:** A/B (reports a strategy backtest, but executable reproducibility is not established).

### U03 — Bumrah & Budhani (2023)
- **Uploaded filename:** 9472-Article Text-11108-2-10-20231228.pdf
- **Citation:** Bumrah, K. S., & Budhani, S. K. (2023). “An Efficient Approach to Forecasting the NIFTY-50 Indian Stock Market's Daily Closing Price with Artificial Neural Networks.” *International Journal on Recent and Innovation Trends in Computing and Communication*, 11(11).
- **Scope/design:** daily average NIFTY-50 closing prices over 2018–2023; considers dollar exchange-rate changes and FII gross purchases/sales; compares SVM, RBF, MLP and SLP neural approaches.
- **Paper-reported findings:** the paper reports correlations among NIFTY, dollar and FII flow variables and describes MLP as the stronger model in its comparison.
- **Use in this project:** motivates testing global-market and FII/DII context where justified by a separate hypothesis.
- **Limitations / interpretation:** daily close prediction/correlation does not establish an intraday signal, causal effect, or option-strategy P&L; its reported design is not directly comparable to the project's 15-minute magnitude target.
- **Classification:** C.

### U04 — Sain & Singh (2026)
- **Uploaded filename:** CureusJournals_1986620261002-185337-d4go5h.pdf
- **Citation:** Sain, R. K., & Singh, A. K. (2026). “Open and Close Price Forecasting of the NIFTY 50 Stock Index Using Machine Learning: A Multi-Window Study of Feature Engineering and Model Tuning.” *Cureus Journal of Computer Science*, article es44389-026-00306-5. DOI: [10.7759/s44389-026-00306-5](https://doi.org/10.7759/s44389-026-00306-5). The first page says published 1 October 2026.
- **Scope/design:** compares 12 regression algorithms to a naïve persistence baseline for next-day open/close price levels, using 5-, 10- and 20-year windows, raw OHLCV versus added technical indicators and chronological 80/20 splits.
- **Paper-reported findings:** linear models (including Linear Regression, Ridge and Lasso) generalize more consistently on 10- and 20-year windows; Random Forest/XGBoost are competitive in the 5-year window but weaker on longer histories in the reported setup.
- **Use in this project:** supports explicit naïve and linear baselines and cautions against assuming a complex model always wins.
- **Limitations / interpretation:** the authors note that test periods differ between the historical-window configurations and recommend aligned OOS periods, walk-forward validation and statistical testing. The target is daily index price, not returns or options P&L.
- **Classification:** C.

### U05 — Atheetha et al. (2019)
- **Uploaded filename:** D0801051829.pdf
- **Citation:** Atheetha, S., Mondal, S., Dhanusha, N., & Raghunandan, H. J. (2019). “Options Trading Strategy: A quantitative study from an Investor's POV.” *International Journal of Business and Management Invention*, 8(1), Version V, 18–29.
- **Scope/design:** simple-average/monthly-trend and seasonality approach on three FMCG stocks, three banking stocks and an index context; one-month European options; assumes ₹300,000 capital, entry on the first Thursday and a three-day timing window, with a stated stop-loss assumption.
- **Paper-reported findings:** the authors emphasize timing risk: several profitable outcomes, where present, reportedly occurred within about T+3 days; beyond that, losses were more frequent in the chosen sample.
- **Use in this project:** a hypothesis source for holding period, timing risk and predefined exit rules.
- **Limitations / interpretation:** the paper itself notes a limited three-year period, limited underlying coverage and omitted fundamental factors. Its assumed capital and stop-loss do not demonstrate modern brokerage/statutory costs or executable historical fills.
- **Classification:** A/B.

### U06 — Naik & Inamdar (2024)
- **Uploaded filename:** IJCSE-V11I10P106.pdf
- **Citation:** Naik, P. P., & Inamdar, V. G. (2024). “Bridging Temporal Dependencies and Sentiment: A Comprehensive Approach to NIFTY 50 Index Prediction.” *SSRG International Journal of Computer Science and Engineering*, 11(10), 46–53. DOI: [10.14445/23488387/IJCSE-V11I10P106](https://doi.org/10.14445/23488387/IJCSE-V11I10P106).
- **Scope/design:** proposes LSTM temporal modelling plus BERT-based news sentiment, with FII/DII activity, India VIX and near-expiry put-call ratio as additional information.
- **Paper-reported findings:** the paper presents an integrated framework and model evaluation for NIFTY prediction.
- **Use in this project:** identifies sentiment, institutional flow, VIX and PCR as candidate explanatory inputs in a future preregistered study when reliable point-in-time data and a precise target are available.
- **Limitations / interpretation:** forecast architecture and index prediction are not proof that each factor adds incremental value, and the paper does not establish exact-contract, executable option returns after costs.
- **Classification:** C/B.

### U07 — Chatterjee et al. (2022)
- **Uploaded filename:** IJNRD2205074.pdf
- **Citation:** Chatterjee, P., Chatterjee, J., Baidya, R., Das, A., & Das, J. (2022). “Options Trading Strategies for the Indian Market—An effective Financial Derivative Tool.” *International Journal of Novel Research and Development*, 7(5), May 2022.
- **Scope/design:** descriptive overview of option-market purpose, risk management and common options strategies.
- **Paper-reported findings:** argues that informed selection and use of appropriate derivative strategies can help hedging/speculation.
- **Use in this project:** background taxonomy for defining payoff/risk profiles before a quantitative test.
- **Limitations / interpretation:** it is not an auditable, registered options backtest with executable fills or cost-adjusted strategy statistics.
- **Classification:** D.

### U08 — Harish B. G. et al. (2023)
- **Uploaded filename:** IJSDR2309053.pdf
- **Citation:** Harish, B. G., ChetanKumar, G. S., Radder, R., & Manoj, K. (2023). “NIFTY-50 Stock Prediction Master.” *International Journal of Scientific Development and Research*, 8(9), September 2023.
- **Scope/design:** describes ten years of daily NIFTY data (10 December 2011 to 10 December 2021), normalisation and an LSTM approach.
- **Paper-reported findings:** the abstract reports 83.88% prediction accuracy. The conclusion/future-work narrative also describes further testing and development, which limits clarity about the final validated experiment.
- **Use in this project:** illustrates the need to specify exactly what “accuracy” means and reconcile a paper's stated result with its validation protocol.
- **Limitations / interpretation:** the accuracy metric is not a trading return; the PDF does not provide enough reproducible detail to use the result as cost-adjusted options evidence.
- **Classification:** C/D.

### U09 — Kallimath, Darapaneni & Paduri (2025)
- **Uploaded filename:** ISMLA+7481.pdf
- **Citation:** Kallimath, S. P., Darapaneni, N., & Paduri, A. R. (2025). “Deep Learning Approaches for Stock Price Prediction: A Comparative Study on Nifty 50 Dataset.” *EAI Endorsed Transactions on Intelligent Systems and Machine Learning Applications*, 1. DOI: [10.4108/eetismla.7481](https://doi.org/10.4108/eetismla.7481). Published 28 February 2025.
- **Scope/design:** compares linear regression, LSTM, GRU, CNN, RNN, TCN and hybrid combinations on historical NIFTY-50 data with MAE, MSE, RMSE, MAPE and R².
- **Paper-reported findings:** the abstract reports that deep architectures capture nonlinear/time-varying data and hybrid models show promise; this is a broad architecture comparison rather than strategy evaluation.
- **Use in this project:** motivates strong baseline comparisons and model simplicity checks.
- **Limitations / interpretation:** multiple model/metric comparisons can create selection risk; index-price metrics alone do not identify a monetizable option signal or account for execution costs.
- **Classification:** C.

### U10 — Mahajan et al. (2025)
- **Uploaded filename:** JIER-+Vol.+5+No.+3+(2025)+-+Dr.+Deepesh.Formated.pdf
- **Citation:** Mahajan, D. Y., Tanted, N., Rewadikar, S., & Chhabra, J. S. (2025). “A Study of the Impact of Moving Averages on Predicting Stock Market Trends: A Study of NIFTY 50.” *Journal of Informatics Education and Research*, 5(3). [Publisher article page](https://jier.org/index.php/journal/article/view/3254).
- **Scope/design:** compares SMA/EMA trend indicators and crossover rules on NIFTY-50 historical data; includes correlation and paired t-test versus buy-and-hold.
- **Paper-reported findings:** the paper reports high correlation between the NIFTY index and EMA series, but its conclusion says the crossover return test did not show statistically significant outperformance over passive investing.
- **Use in this project:** direct caution that an indicator's correlation with price does not establish incremental return.
- **Limitations / interpretation:** findings are for index-level crossover/buy-and-hold rules, not intraday options; correlations are expected for moving averages derived from the index itself.
- **Classification:** B/C.

### U11 — Fathali, Kodia & Ben Said (2022)
- **Uploaded filename:** Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques.pdf
- **Citation:** Fathali, Z., Kodia, Z., & Ben Said, L. (2022). “Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques.” *Applied Artificial Intelligence*, 36(1), article 2111134. DOI: [10.1080/08839514.2022.2111134](https://doi.org/10.1080/08839514.2022.2111134).
- **Scope/design:** compares RNN, LSTM and CNN forecasting approaches on NIFTY-50 index data across different input features and sequence settings.
- **Paper-reported findings:** reports differences in error metrics depending on model, feature set and look-back configuration.
- **Use in this project:** reinforces that target construction, input feature choice and baseline metrics matter more than a model label.
- **Limitations / interpretation:** index-level forecast errors are not directly comparable to this project's 15-minute absolute-return MAE and do not establish options returns.
- **Classification:** C.

### U12 — Kumar & Sharma (2016)
- **Uploaded filename:** Stock_Market_Index_Forecasting_of_Nifty.pdf
- **Citation:** Kumar, G., & Sharma, V. (2016). “Stock Market Index Forecasting of Nifty 50 Using Machine Learning Techniques with ANN Approach.” *International Journal of Modern Computer Science*, 4(3), June 2016.
- **Scope/design:** multilayer perceptron/back-propagation forecasting of daily OHLC using data from 3 April 2006 to 16 May 2016, including volume and turnover.
- **Paper-reported findings:** reports high accuracy and an RMSE figure after preprocessing/normalisation.
- **Use in this project:** historical example of neural OHLC forecasting and the importance of clearly defining normalization and metric scale.
- **Limitations / interpretation:** normalized prediction accuracy is not a direct measure of economic return, drawdown, or options strategy profitability; no modern exact-contract options execution test is supplied.
- **Classification:** C.

### U13 — Jafar et al. (2023)
- **Uploaded filename:** jrfm-16-00423.pdf
- **Citation:** Jafar, S. H., Akhtar, S., El-Chaarani, H., Khan, P. A., & Binsaddig, R. (2023). “Forecasting of NIFTY 50 Index Price by Using Backward Elimination with an LSTM Model.” *Journal of Risk and Financial Management*, 16(10), 423. DOI: [10.3390/jrfm16100423](https://doi.org/10.3390/jrfm16100423).
- **Scope/design:** compares LSTM and backward-elimination LSTM on roughly 15 years of daily NIFTY data, using OHLCV and RSI-type predictors for close-price forecasting.
- **Paper-reported findings:** the abstract reports the backward-elimination model performed better for the next-30-day price-forecast task and states 95% accuracy.
- **Use in this project:** motivates ablation/feature-selection tests only where a new hypothesis and data gate exist.
- **Limitations / interpretation:** daily index close forecasts and a paper-defined accuracy metric do not establish incremental intraday option profitability; model selection can overfit unless evaluation is strictly time-separated.
- **Classification:** C.

### U14 — Shaha (SSRN working paper)
- **Uploaded filename:** ssrn-3323746.pdf
- **Citation:** Shaha, P. “An Empirical Study on Options Trading Strategy Using ‘Commodity Channel Index’ for NSE’s Nifty Options in India.” SSRN abstract 3323746. [SSRN record](https://ssrn.com/abstract=3323746).
- **Scope/design:** reports a CCI-based long-option strategy for NIFTY options, using in-the-money contracts and a roughly two-week horizon, with results presented through return, maximum loss zone, average-gain-to-average-loss and strike-rate measures.
- **Paper-reported findings:** the paper reports about 232% annual return, 63.25% strike rate and a 1.69 average-gain-to-average-loss ratio. It also reports a 58.65% maximum loss zone relative to initial investment and warns that two consecutive losses could require 117.30% of initial capital.
- **Use in this project:** relevant as a direct strategy hypothesis and as a risk warning; results must be independently reproduced before any adoption.
- **Limitations / interpretation:** these are author-reported historical results, not verified by Final Stand. They do not satisfy our present gate without independently audited exact-contract entries/exits, fill timing, brokerage/statutory charges, spread, slippage, and temporally independent OOS performance.
- **Classification:** A (author-reported strategy study; not independently validated here).

## Cross-paper synthesis

1. **Most sources forecast daily price levels**, using OHLCV or indicator inputs. Their reported percentage “accuracy”, RMSE, MAE or R² values are not interchangeable, and they do not predict the same target as the Final Stand phases 89–92 (absolute next-15-minute spot return).
2. **Feature context is diverse**: FII flows, dollar/FX, VIX, put-call ratio and news sentiment occur in the uploaded work. Those are sensible hypotheses, not validated factors. The Phase 89–92 registered tests were much narrower and do not test all such drivers.
3. **Direct option-strategy papers report large returns but are not sufficient as executable evidence**. Shaha's CCI paper reports high annual return while also indicating very large loss exposure. Sherasiya's ML paper reports a positive Sharpe/return table. Neither result was independently reproduced in this project, and their source-reported metrics should not be used as promoted-strategy claims.
4. **Moving-average correlation does not imply excess returns**. The JIER paper itself reports no statistically significant crossover outperformance versus passive investing in its paired test.
5. **Complexity is not automatically better**. The recent multi-window Cureus study reports stronger long-window generalization for linear models than for some tree ensembles, illustrating the importance of simple baselines and aligned evaluation windows.
6. **Evidence decision unchanged**: the 14 uploads enrich hypothesis framing and show the need for stronger validation, but do not close the missing exact-contract executable-quote/depth and cost-adjusted replay gate.

## What this audit does not do

- It does not re-run or independently verify any uploaded paper's model or trading returns.
- It does not pool heterogeneous result statistics.
- It does not claim any predictor is causal or profitable.
- It does not use the sealed Phase 83 2026 holdout.
- It does not promote a strategy or authorize live trading.
