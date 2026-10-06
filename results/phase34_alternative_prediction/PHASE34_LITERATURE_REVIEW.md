# Phase 34 Literature and Model-Family Review

## Rationale for the tested families

Recent NIFTY-specific work continues to use regime models and nonlinear machine learning. A 2025 NIFTY regime study used Gaussian HMMs with Monte Carlo paths for short-horizon forecasting, while a 2026 NIFTY intraday study reported useful out-of-sample volatility improvements from unsupervised regime conditioning. These findings motivate a regime-aware HMM component rather than another generic volatility model.

Transformer-based approaches are also being explored directly on NIFTY. A recent 2026 NIFTY-50 study reports a multivariate Transformer benchmarked against LSTM, and a public Hugging Face model card describes a Temporal Fusion Transformer trained for Nifty50 return forecasting with price and news sentiment features. These results motivate testing a deliberately small Transformer sequence model under the much stricter D−6 point-in-time setup used here.

The broader NIFTY literature has used SVM, logistic regression and tree ensembles alongside recurrent networks. Phase 34 therefore adds margin-based and regularized-linear models and multiple tree-boosting families to determine whether Phase 33's Random Forest result is an artifact of model choice.

## Key sources
- MDPI, “Forecasting of NIFTY 50 Index Price by Using Backward Elimination with an LSTM Model” (2023): https://www.mdpi.com/1911-8074/16/10/423
- MDPI, “Modeling and Forecasting the Volatility of NIFTY 50 Using GARCH and RNN Models” (2022): https://www.mdpi.com/1609106
- 2025 HMM/Monte Carlo NIFTY study: https://internationalpubls.com/index.php/cana/article/view/6029
- 2026 NIFTY intraday regime study: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6316139
- 2026 Transformer-based NIFTY-50 study: https://www.svedbergopen.com/index.php/ijaiml/article/view/2170
- Public Nifty50 Temporal Fusion Transformer model card: https://huggingface.co/mveen3/TFT_Model_For_Stock_Price_Prediction
- 2026 regime-dependent Indian equity/HMM study: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7017321

## Research interpretation
Literature is heterogeneous and often evaluates different horizons, data frequencies and leakage controls. Therefore these sources justify candidate-family selection, not expected performance. Phase 34 uses the project's stricter chronological D−6 design as the decisive evidence.
