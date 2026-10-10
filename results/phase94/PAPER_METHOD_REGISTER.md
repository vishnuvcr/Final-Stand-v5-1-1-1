# Paper-to-Method Registry — U01–U14

**Authority:** the 14 uploaded PDFs and the Phase 93 evidence audit. This registry distinguishes source-described methods from exact implementation details that must still be extracted. It is not a claim that any model has been rerun.

| ID | Source / target | Registered methods and comparisons | Feature/rule family | Reproduction assignment | Prior status / guardrail |
|---|---|---|---|---|---|
| U01 | Bansal, Goyal & Choudhary (2022), stock prices for 12 Indian companies | K-nearest neighbors; linear regression; support-vector regression; decision-tree regression; LSTM | Historical price sequences; preserve original company universe if recoverable | Phase 95 | If only NIFTY data are available, that is a domain-adapted partial replication, not exact paper replication. Recreate source metric definitions and add shared naïve baseline. |
| U02 | Sherasiya (2025), NIFTY option buy/sell signals | Random Forest; XGBoost; LSTM; basic-momentum comparator | Option Greeks, IV, underlying movement, option chain | Phase 97 | Paper-reported 90.10% LSTM accuracy, Sharpe 1.95 and total return ₹205,720 are source claims only. Requires no-look-ahead option data and exact contract/fill/cost gate. |
| U03 | Bumrah & Budhani (2023), daily NIFTY close | SVM; RBF; MLP; SLP; reported 65/35 and 70/30 train/test configurations | Dollar exchange rate, FII gross buys and sells, NIFTY daily average close | Phase 95 | Reproduce each reported split only as a secondary diagnostic; primary validation must be chronological and source-equivalent. Clarify any nonstandard split methodology from paper. |
| U04 | Sain & Singh (2026), NIFTY next-day open/close levels, 5/10/20-year windows | Naïve persistence; Linear Regression; Lasso; Ridge; Elastic Net; Decision Tree; Random Forest; Gradient Boosting; AdaBoost; XGBoost; plus all additional algorithms named in the paper's 12-model table | Raw OHLCV versus augmented SMA/RSI/daily-return/rolling-volatility features | Phase 95 | Same OOS date alignment must be added; paper's unequal test periods are not to be mistaken for an apples-to-apples comparison. Extract and verify full model list/configuration against PDF before final numerical run. |
| U05 | Atheetha et al. (2019), options on three FMCG stocks, three banking stocks and index context | Simple-average method; monthly trend/seasonality; first-Thursday entry; about one-month European-option context; timing window up to T+3; stated stop-loss | SMA/EMA and historical strike/option prices as described in source | Phase 96 and 99 | Paper's assumed capital/timing/stop logic must be source-faithfully extracted. Only quote-level P&L if underlying, expiry, strike, lot and option premiums exist. |
| U06 | Naik & Inamdar (2024), NIFTY trend prediction | LSTM + BERT sentiment framework | Time series plus news sentiment, FII/DII, India VIX, nearest-expiry PCR | Phase 95 | Point-in-time news timestamps and historic PCR/flow data are essential. If absent, run a price-only ablation and mark unavailable modalities; do not call it a replication of the full model. |
| U07 | Chatterjee et al. (2022), conceptual Indian options-strategy overview | Each source-explicit options structure and risk/hedging strategy enumerated in the paper | Payoff/risk taxonomy | Phase 99 | No unique signal rules are inferred from a conceptual overview. Payoff diagrams can be reproduced separately; historical profitability needs explicit entry/exit and premium data. |
| U08 | Harish et al. (2023), daily NIFTY prediction | LSTM; normalisation and sequence prediction as reported | NIFTY daily history; source reports ~83.88% accuracy | Phase 95 | “Accuracy” target/classification formula and model protocol must be recovered before comparing; reproduce its exact metric separately from common regression/direction metrics. |
| U09 | Kallimath et al. (2025/2026 as printed in PDF metadata), NIFTY price forecasting | Linear regression; LSTM; GRU; CNN; RNN; TCN; LSTM+GRU; CNN+RNN; CNN+TCN; LSTM+TCN hybrids | Common sequence windows and price-derived predictors described in source | Phase 95 | Register the PDF's actual metadata/target and environment. Hybrids run only if architecture can be reconstructed; undocumented hyperparameters lead to labelled partial replication. |
| U10 | Mahajan et al. (2025), NIFTY trend rules | SMA; EMA; crossover strategies; buy-and-hold comparator; paired-sample t-test used by source | Moving-average trend indicators, 2010–2023 per audit | Phase 96 | Correlation between price and its moving average is not return alpha. Rebuild signals without look-ahead, align the holding period, and report the source paired test plus dependence-aware analysis. |
| U11 | Fathali, Kodia & Ben Said (2022), NIFTY price forecasting | RNN; LSTM; CNN; source-described feature and sequence setting comparisons | Historical NIFTY index observations | Phase 95 | Match source target, look-back, horizon and feature settings as far as PDF permits. Use common rows and identical training cutoff for comparisons. |
| U12 | Kumar & Sharma (2016), next-day NIFTY OHLC prediction | Feed-forward MLP; back-propagation / multiple back-propagation variants including Levenberg–Marquardt where specified | OHLCV and turnover; source 2006-04-03 to 2016-05-16; normalized inputs/targets | Phase 95 | Reported 99.2152% accuracy and RMSE 0.0079 are scale-dependent source claims. Reproduce normalization/metric carefully and add unnormalized price metrics and naïve persistence. |
| U13 | Jafar et al. (2023), NIFTY close forecasting next 30 days | LSTM; backward-elimination LSTM; 14-period RSI; feature-selection ablation | Daily OHLCV + RSI | Phase 95 | Source-reported 95% accuracy is not taken at face value until the metric and 30-day target construction are verified. Feature selection occurs on training data only. |
| U14 | Shaha (SSRN working paper), NIFTY long options | CCI-based trigger/rule, strict-ITM call/put selection, fixed hold/exit and stop rules as fully described in paper | CCI and NIFTY spot/options | Phase 98 | Phase 66 previously had zero completed trades/coverage on an OHLC proxy. Reuse that finding; rerun only if a materially better authorized source resolves source-period/contract gaps. |

## Cross-paper implementation register

| Registry ID | Method/variant | Main question | Primary output | Status at Phase 94 |
|---|---|---|---|---|
| M01 | Persistence / last-observation baseline | Is any model better than predicting the last observed level? | MAE, RMSE, R² | Must run for every comparable price-level task |
| M02 | KNN regressor | Does local-neighbor prediction reproduce U01? | Paper metric + common metrics | Planned |
| M03 | Linear Regression | Does a linear baseline explain the source result? | Paper metric + common metrics | Planned |
| M04 | SVR/SVM | Do margin-based models reproduce source forecasts? | Paper metric + common metrics | Planned |
| M05 | Decision Tree regression | Does tree-based regression reproduce the paper? | Paper metric + common metrics | Planned |
| M06 | MLP / SLP / RBF ANN | Do feed-forward architectures reproduce the source? | Paper metric + common metrics | Planned |
| M07 | Random Forest | Can option/index predictions be reproduced? | Prediction metrics; option net P&L only if eligible | Planned |
| M08 | XGBoost / gradient boosting / AdaBoost | Does boosted-tree performance hold OOS? | Prediction metrics | Planned |
| M09 | LSTM | Does the common recurrent method reproduce? | Paper metric + common metrics | Planned |
| M10 | RNN | Does a vanilla recurrent model reproduce? | Paper metric + common metrics | Planned |
| M11 | GRU | Does gated recurrence reproduce? | Paper metric + common metrics | Planned |
| M12 | CNN | Does convolutional sequence modelling reproduce? | Paper metric + common metrics | Planned |
| M13 | TCN | Does causal convolutional sequence modelling reproduce? | Paper metric + common metrics | Planned |
| M14 | LSTM+GRU | Does the hybrid improve on constituents on same OOS rows? | Paired delta + CI | Planned |
| M15 | CNN+RNN | Same | Paired delta + CI | Planned |
| M16 | CNN+TCN | Same | Paired delta + CI | Planned |
| M17 | LSTM+TCN | Same | Paired delta + CI | Planned |
| M18 | Backward-elimination LSTM | Does feature elimination improve the fixed OOS metric? | Paired loss delta + CI | Planned |
| M19 | LSTM+BERT sentiment | Does point-in-time news sentiment add incremental value? | Matched-row ablation | Data/modality gate pending |
| M20 | SMA/EMA crossover | Does indicator rule beat buy-and-hold after costs? | Return, drawdown, turnover, paired inference | Planned |
| M21 | Simple-average/monthly seasonality | Does paper timing rule reproduce? | Signal and net strategy metrics | Planned |
| M22 | CCI long option | Do source rules and result reproduce? | Coverage first; net P&L only if valid fills | Prior test exists; data-gated |
| M23 | RF/XGBoost/LSTM options signal | Does ML signal beat momentum after cost? | Net P&L, Sharpe, drawdown, calibration | Exact-option data gate pending |
| M24 | Options payoff structures in U05/U07 | Can payoffs/risk be reproduced from premiums? | Payoff graph; backtest only with trade rules/data | Source-by-source rule extraction pending |

## Status vocabulary

- **Planned:** registered, not run.
- **Running:** an identified workflow/model execution is in progress.
- **Reproduced / Not reproduced / Inconclusive / Partial / Data-blocked / Not identifiable:** final evidence states, defined in `PHASE94_RESEARCH_PLAN.md`.

## Citation trail

See [Phase 93 literature audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-93-uploaded-literature-audit/results/phase93/UPLOADED_LITERATURE_AUDIT.md). The original PDF uploads stay in the project attachment area; the repository keeps only concise evidence summaries and method registrations.
