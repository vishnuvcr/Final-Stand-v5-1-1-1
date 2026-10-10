# Phase 101 — Full PDF Strategy Replication Gap-Fill

**Status:** COMPLETED_WITH_EXPLICIT_LIMITATIONS  
**Decision:** no strategy promoted  
**Pinned dataset revision:** 3eacf762d401efd9a08e804592fa7882b354c4a2  
**Data end:** 2025-12-31 15:59:00+05:30  
**2026 options holdout:** not downloaded or evaluated.

## 1. Research question and scope
This bounded follow-up tests U02 (RF/XGBoost/LSTM Buy/Sell options method) and U05 (monthly seasonality options procedure) where modern historical data allow proxy replay. Other methods are reconciled from the verified earlier phase outputs; they are not mislabelled as new tests.

## 2. Data/provenance
- Historical option dataset: thetrademarkk/india-index-options-1m, pinned revision 3eacf762d401efd9a08e804592fa7882b354c4a2, CC-BY-NC-4.0. Raw data are not published.
- Eligible monthly expiry files: 56; underlying minute rows: 436424; sessions: 1142.
- Last underlying timestamp used: 2025-12-31 15:59:00+05:30; latest selected expiry: 2025-12-30.
- Yahoo daily history for monthly-return calculation: 2015-01-02 through 2025-12-31 (2708 observations).

## 3. U05 — monthly seasonality options rule
Source wording uses an ambiguous expression equivalent to opening price plus average return. This run uses Wednesday open × (1 + the mean of the preceding three annual returns for the same calendar month). The first calendar Wednesday supplies the forecast; entry is on the first calendar Thursday strictly after that Wednesday to prevent look-ahead. No holiday substitution is made. Positive mean selects CE and negative mean selects PE. Entry strike is closest to the expected index level at the first 09:15–09:20 opening-window minute with matching underlying and option bars; only contemporaneous OI/volume can break ties.
The test uses the paper’s ₹3,00,000 initial capital, deploying no more than 90% of current equity per monthly trade; equity is carried forward and 10% is held as a safety reserve. Target is a 20% premium gain and a 30% premium stop that activates on the third subsequent trading session. If target and stop are both crossed inside one minute, stop is prioritized. Trigger exits require the exact next-minute bar; absent a target/stop, exit uses an observed penultimate-session bar before expiry.

- Months audited: 56; completed trades: 10; status: COMPUTED.
- Initial/ending account equity: ₹300,000.0000 / ₹24,678.2846; account return: -91.7739%; max account drawdown: ₹315,787.9353.
- Mean net P&L/trade 95% circular moving-block bootstrap interval: not estimable to not estimable; status: SKIPPED_LT20_TRADES.
- Net P&L at ₹10/order: -275,321.7154; mean/trade: -27,532.1715; median: -15,869.3201; win rate: 0.4000; PF: 0.2649; max trade drawdown: 315,787.9353.
- Net at ₹20/order: -275,521.7154; +50% charges stress: -276,558.8231; ₹20/order + stress: -276,858.8231; extra hypothetical 0.25% each-side impact plus ₹50/trade (not specified by U05): -249,051.5562.
- A zero-trade sample is NOT ESTIMABLE, never reported as evidence of zero return. This does not recreate the original source period.

## 4. U02 — machine-learning Buy/Sell option method
The source label is implemented as next-session NIFTY close return greater than 1% = Buy; otherwise Sell. Train window ends in 2023; validation is 2024–2025. RF, XGBoost and a 5-session LSTM use fixed settings and no validation tuning. Features include past returns, moving-average gaps, RSI, realized volatility/range, ATM call/put premium ratios, straddle/spot ratio, days-to-expiry and log OI/volume if available. IV/Greeks are used only when they exist and are sufficiently populated in the training sample; missing features are not fabricated.
A predicted Buy buys the nearest available ATM call; predicted Sell buys the nearest available ATM put on the next trading session. Entry uses the first matching underlying-option timestamp within 09:15–09:20; exit uses the last available 15:25–15:30 bar for that contract. Each model has a separate ₹1,00,000 account; position size compounds trade-by-trade, premium deployment is capped at 95% of current equity, and entry is blocked if one lot cannot be funded while preserving the 5% fee reserve.

### Prediction metrics
| Model | Status | Train rows | Validation rows | Accuracy | Balanced accuracy | Buy precision | Buy recall | F1 | ROC AUC | Always-sell accuracy |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RF | COMPLETED | 362 | 449 | 0.9154 | 0.5229 | 0.3333 | 0.0556 | 0.0952 | 0.5350 | 0.9198 |
| XGBOOST | COMPLETED | 362 | 449 | 0.9131 | 0.5090 | 0.2000 | 0.0278 | 0.0488 | 0.5424 | 0.9198 |
| LSTM5 | COMPLETED | 260 | 432 | 0.6574 | 0.5732 | 0.1164 | 0.4722 | 0.1868 | 0.6011 | 0.9167 |

### Costed options results
| Model | Trades | Net P&L ₹10/order | Mean/trade 95% block-bootstrap CI | Ending account equity ₹ | Account return % | Net ₹20/order sensitivity | +50% fee stress | Win rate | Max account drawdown ₹ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LSTM5 | 62 | -99,981.5392 | -34,662.6960 to 41,663.9601 | 18.4608 | -99.9815 | -101,221.5392 | -116,327.3088 | 0.2742 | 1,353,180.1863 |
| RF | 49 | -99,994.9604 | -8,475.4343 to 4,162.0952 | 5.0396 | -99.9950 | -100,974.9604 | -102,266.1906 | 0.2857 | 320,187.8184 |
| XGBOOST | 53 | -99,991.4677 | -24,246.6369 to 20,524.2444 | 8.5323 | -99.9915 | -101,051.4677 | -103,043.4516 | 0.2642 | 980,242.1479 |

### Model statuses
- RF: COMPLETED — 
- XGBOOST: COMPLETED — 
- LSTM5: COMPLETED — 

- Training/validation feature rows: 362 / 449.
- Option bars are OHLC, not bid/ask/depth. This is a proxy model and not the original paper's exact reproduction.

## 5. Reconciled coverage of every uploaded PDF
| ID | Paper/method | Phase 101 status | Evidence and limitation |
|---|---|---|---|
| U01 | Bansal multi-regressor stock-price forecasts | PARTIAL | Phase 95 common-data screen; original universe/protocol not matched. |
| U02 | Sherasiya RF/XGBoost/LSTM NIFTY options signals | PROXY_TESTED | Phase 101 fixed chronological proxy; exact IV/Greeks and source configuration may be absent. |
| U03 | Bumrah/Budhani ANN with USD/INR and FII inputs | PARTIAL | Phase 95 price-only screen; FX/FII inputs not matched. |
| U04 | Sain/Singh multi-window NIFTY forecast | PARTIAL | Phase 95 common-data screen; exact source protocol not matched. |
| U05 | Atheetha monthly trend/seasonality options rule | PROXY_TESTED | Phase 101 modern-sample proxy; dimensionally ambiguous expected-price formula operationalized. |
| U06 | Naik/Inamdar sentiment/news plus LSTM | DATA_BLOCKED_SOURCE_MODALITIES | Point-in-time news/sentiment, FII/DII, VIX/PCR/Greeks not fully sourced as a joined feature panel. |
| U07 | Chatterjee options payoff structures | PARTIAL_ANALYTICAL | Phase 99 checked 13 expiry-payoff structures over nine illustrative spot values; no historical entry strategy. |
| U08 | Fathali/Kodia/Ben Said NIFTY forecast | PARTIAL | Phase 95 common-data screen; source-period and data split not fully matched. |
| U09 | Kallimath deep-learning model family | PARTIAL | Phase 95 common-data screen; source-specific dataset/settings not matched. |
| U10 | NIFTY moving-average paper | PARTIAL | Phase 96 descriptive SMA/EMA screen; not inferentially confirmed and not options P&L. |
| U11 | NIFTY RNN/LSTM/CNN comparison | PARTIAL | Phase 95 common-data screen, not exact source replication. |
| U12 | MLP/backprop OHLC forecast | PARTIAL | Phase 95 common-data screen; exact OHLC label construction not matched. |
| U13 | LSTM backward feature elimination/RSI | PARTIAL | Phase 95 price-only screen; exact source feature-elimination protocol not matched. |
| U14 | Shaha CCI NIFTY options rule | DATA_BLOCKED_ZERO_COMPLETED_TRADES | Phase 66 zero completed trades; Phases 67-68 found insufficient exact timing/contract coverage. |

## 6. Costs and statistical inference
The mean net P&L/trade confidence interval uses a deterministic circular moving-block bootstrap (5-trade blocks, 3,000 resamples), and is reported only for at least 20 completed trades. The seasonality sample has fewer than 20 trades, so no bootstrap precision is claimed. Fee-stress totals are alternative charge scenarios on the primary simulated position path, not separately re-sized equity curves.
Baseline uses the repository’s date-effective charge helper, ₹10/order brokerage, one ₹0.05 adverse tick per fill, statutory/exchange fees and GST where implemented. Sensitivities add ₹20/order brokerage, +50% charge stress, and a paper-specific 0.25% adverse price impact per side plus ₹50/trade. These are simulated costs, not verified historical Paytm Money contract notes or proof of executable fills.
Classification accuracy alone is not evidence of profitable trading. U02 accounting is sequential per-model equity rather than reusing the initial ₹1 lakh on every trade. Sparse trades, missing coverage and confidence intervals crossing zero are not robust evidence. No strategy is promoted.

## 7. Strengths and limitations
Strengths: pinned provenance; chronological development/validation split; no 2026 option data; explicit opportunity exclusions; training-only feature eligibility/imputation; conservative handling of bars that hit both target and stop.
Limitations: U02 and U05 do not recreate original paper periods or every undocumented choice; U05 expected-price arithmetic is ambiguous; full IV/Greeks/news inputs may be absent; OHLC cannot reproduce spread, depth, queue position, latency or broker contract notes; U06 remains blocked without point-in-time sentiment/news/FII/DII modalities.

## 8. Conclusion and future work
Phase 101 adds two source-informed options strategy proxy tests to the previous forecasting, SMA/EMA, CCI and payoff-algebra screens. If no strategy satisfies coverage, sample-size, positive cost-stress and uncertainty criteria, no strategy is promoted. This is insufficient evidence, not proof that every PDF method is unprofitable. Future work requires authorized exact-period contracts, quote/depth data, verified broker charges, point-in-time external modalities and a new bounded plan.

## 9. Output files
See paper_test_matrix.csv; u05_opportunity_audit.csv; u05_trade_ledger.csv; u05_summary.csv; u02_model_metrics.csv; u02_model_status.csv; u02_predictions.csv; u02_coverage_audit.csv; u02_trade_ledger.csv; u02_strategy_summary.csv; phase101_source_manifest.json; validation_report.json; net_pnl_comparison.svg.
