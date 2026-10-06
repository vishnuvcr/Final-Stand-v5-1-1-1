# Phase 33 Literature Review and Data Audit

## 1. LSTM and NIFTY forecasting
Mehtab, Sen and Dutta (2020) evaluated NIFTY 50 forecasting with machine-learning regressors and LSTM models and reported a walk-forward design in which a univariate LSTM using one-week history performed best among their tested LSTM configurations. This supports testing LSTM on NIFTY, but the study is not evidence that the same model works at a D−6 expiry horizon. Source: https://arxiv.org/abs/2009.10819

A recent NIFTY-focused comparative study reports that plain LSTM, Random Forest and other models can differ substantially by metric; its reported NIFTY experiments show that more expressive attention architectures can outperform plain LSTM, while Random Forest can perform poorly for raw-price regression. This is a warning against importing headline model claims into a trading strategy without point-in-time OOS testing. Source: https://doi.org/10.3390/fintech5010004

## 2. GARCH and LSTM hybrids
Kim and Won (2018) combine LSTM with multiple GARCH-type models for index-volatility forecasting and report lower forecast errors for the hybrid approach on KOSPI 200. The paper directly motivates treating GARCH as a volatility-state model that can complement sequence learning rather than assuming GARCH predicts direction by itself. Source: https://doi.org/10.1016/j.eswa.2018.03.002

A 2026 stacking paper integrates GARCH and LSTM in a parallel/meta-learning framework for volatility prediction and reports improved metrics across several benchmarks. This is relevant to the proposed ensemble architecture, but its results are not NIFTY-specific and must not be treated as evidence of NIFTY tradability. Source: https://doi.org/10.1016/j.array.2026.100700

## 3. Sentiment and SOFNN
Bollen, Mao and Zeng (2011) used Twitter mood features with a Self-Organizing Fuzzy Neural Network for DJIA direction prediction and reported improved directional accuracy when selected mood variables were included. The result motivates sentiment-augmented fuzzy modeling but is an old DJIA study, not a NIFTY result. Source: https://doi.org/10.1016/j.jocs.2010.12.007

A review of sentiment/event-based stock forecasting summarizes evidence that sentiment can add information beyond price-only text-free baselines, while also emphasizing large variation by market, horizon and text source. Source: https://www.mdpi.com/2227-7390/10/14/2437

A NIFTY news-sentiment study focuses on topic-specific news effects on NIFTY movement, supporting point-in-time news as a candidate feature source while highlighting the importance of topic and timing. Source: https://arxiv.org/abs/2412.06794

## 4. Random Forest / ensemble
A 2026 NIFTY 50 technical-indicator Random Forest study reports a ROC-AUC only slightly above 0.50 in a large temporal holdout, illustrating the modest size of practical directional edges even when statistical significance is claimed. Source: https://rjpn.org/ijnti/viewpaperforall.php?paper=IJNTI2604008

A 2026 time-series-aware Indian-market framework combines LSTM/GRU with Random Forest and XGBoost and emphasizes leakage-aware normalization and temporal evaluation on NIFTY 50. Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6109409

## 5. Point-in-time data sources
The primary repository dataset thetrademarkk/india-index-options-1m contains 1-minute NIFTY, BANKNIFTY and SENSEX spot/option OHLCV(+OI) data for approximately 2021–2026. The dataset itself warns that option coverage is partial and should be verified against official exchange data. Source: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m

The sentiment cache candidate dixitdharmansh07/indic-finance contains approximately 9,960 dated Indian financial-news/social observations with sentiment probabilities and explicit forward-return columns. The Phase-33 implementation must ignore those forward-return/target columns and use only text/sentiment observations available before the reference cutoff. Source: https://huggingface.co/datasets/dixitdharmansh07/indic-finance

## 6. Methodological interpretation
The literature supports the candidate model families but does not establish that any one family is universally superior. The decisive test in this phase is therefore the registered NIFTY-specific, point-in-time D−6 experiment with untouched holdout and execution-cost-aware trading impact.
