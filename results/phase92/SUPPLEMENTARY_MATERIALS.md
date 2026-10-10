# Supplementary Materials — Rolling ATM Predictor Studies, Phases 89–92

Prepared 2026-10-10. These supplements accompany [MANUSCRIPT_DRAFT.md](MANUSCRIPT_DRAFT.md). All statistics below are transcribed from each phase's final aggregate report and summary artifacts; no raw market rows are reproduced here.

## Supplement S1. Sample and coverage summary

| Phase | Requested calendar period | Valid option windows | Valid VIX windows | Paired CALL/PUT rows after checks | Complete OOS rows / sessions | Notes |
|---|---|---:|---:|---:|---:|---|
| 89 | 2025 | 25/26 | Not joined in this phase | 17,144 | OOS count varies by feature: 4,049 for IV, skew, and OI imbalance; 2,622 for stable-strike OI-change | One CALL-window timeout; 25 spot mismatch rows and 35 strike mismatch rows excluded |
| 90 | 2024 | 54/54 | 5/5 | 18,554 | 3,604 / 60 | VIX row coverage 99.64%; OOS VIX coverage 99.73% |
| 91 | 2023 | 54/54 | 5/5 | 18,473 | 3,633 / 60 | VIX row coverage 99.984%; OOS VIX coverage 99.978%; zero spot/strike mismatch rows |
| 92 | 2022 | 54/54 | 5/5 | 18,579 | 3,660 / 61 | One strike-mismatch timestamp excluded; zero spot mismatches; 98.63% OOS VIX coverage; one weekend-only zero-row interval annotated as expected empty coverage |

Phase 89's complete-case count is feature-specific. The OI-change test required stable-strike observations and therefore has fewer observations than the other three tests. Phase 92's final 2022-12-31 to 2023-01-01 half-open interval contained no weekday market date and was annotated `NoWeekdayExpected`; it added no observation and was not imputed.

## Supplement S2. Phase 89 full registered test family

| Test | Feature | Target | N | Sessions | Beta (bps / 1 SD feature) | 95% session-cluster CI | Raw p | Holm-adjusted p |
|---|---|---|---:|---:|---:|---|---:|---:|
| P1 | Mean ATM IV | Absolute forward-15m spot return | 4,049 | 57 | +0.602 | +0.225 to +0.980 | 0.0018 | 0.0071 |
| P2 | PUT IV − CALL IV | Signed forward-15m spot return | 4,049 | 57 | −0.218 | −0.652 to +0.216 | 0.3240 | 0.9720 |
| P3 | CE/PE OI imbalance | Signed forward-15m spot return | 4,049 | 57 | −0.118 | −0.567 to +0.330 | 0.6046 | 1.0000 |
| P4 | Trailing 15-minute total OI change, stable-strike screen | Signed forward-15m spot return | 2,622 | 57 | −0.076 | −0.456 to +0.303 | 0.6931 | 1.0000 |

Holm correction applies to the four tests registered in Phase 89. This table does not imply that later model comparisons are independent of the research programme, nor does it demonstrate causality or profitability.

## Supplement S3. Phases 90–91 model metrics

### Phase 90 (2024)

| Split | Model | N | Sessions | MAE (bps) | RMSE (bps) | R² |
|---|---|---:|---:|---:|---:|---:|
| Validation | M0 spot/time | 3,825 | 64 | 4.6408 | 7.8210 | 0.1129 |
| Validation | M1 spot + VIX | 3,825 | 64 | 4.5953 | 7.7968 | 0.1183 |
| Validation | M2 spot + VIX + IV | 3,825 | 64 | 4.5888 | 7.7680 | 0.1248 |
| Confirmatory OOS | M0 spot/time | 3,604 | 60 | 6.0338 | 9.2211 | 0.0518 |
| Confirmatory OOS | M1 spot + VIX | 3,604 | 60 | 5.9953 | 9.2126 | 0.0536 |
| Confirmatory OOS | M2 spot + VIX + IV | 3,604 | 60 | 5.9623 | 9.1920 | 0.0578 |

Primary ΔMAE=MAE(M1)-MAE(M2)=+0.0330385 bps; 95% CI +0.0001393 to +0.0561543; bootstrap positive share 97.5%.

### Phase 91 (2023)

| Split | Model | N | Sessions | MAE (bps) | RMSE (bps) | R² |
|---|---|---:|---:|---:|---:|---:|
| Validation | M0 spot/time | 3,814 | 63 | 4.2052 | 5.5479 | 0.0033 |
| Validation | M1 spot + VIX | 3,814 | 63 | 4.0386 | 5.5503 | 0.0024 |
| Validation | M2 spot + VIX + IV | 3,814 | 63 | 4.0384 | 5.5397 | 0.0062 |
| Confirmatory OOS | M0 spot/time | 3,633 | 60 | 4.0192 | 5.5626 | 0.0563 |
| Confirmatory OOS | M1 spot + VIX | 3,633 | 60 | 3.9156 | 5.5163 | 0.0719 |
| Confirmatory OOS | M2 spot + VIX + IV | 3,633 | 60 | 3.9155 | 5.5135 | 0.0729 |

Primary ΔMAE=MAE(M1)-MAE(M2)=+0.0001111 bps; 95% CI −0.0110700 to +0.0102532; bootstrap positive share 52.4%.

## Supplement S4. Phase 92 all-model out-of-sample metrics

| Model | Feature set added cumulatively | N | Sessions | MAE (bps) | RMSE (bps) | R² |
|---|---|---:|---:|---:|---:|---:|
| M0 | Spot/time | 3,660 | 61 | 5.4719 | 6.9444 | −0.0269 |
| M1 | M0 + India VIX | 3,660 | 61 | 4.7987 | 6.6109 | 0.0693 |
| M2 | M1 + mean ATM IV | 3,660 | 61 | 4.8214 | 6.6003 | 0.0723 |
| M3 | M2 + lagged synthetic-forward proxy gap | 3,660 | 61 | 4.8791 | 6.6208 | 0.0665 |
| M4 | M3 + lagged CE/PE OI imbalance | 3,660 | 61 | 4.9922 | 6.6615 | 0.0550 |

Primary ΔMAE=MAE(M2)-MAE(M4)=−0.1708363 bps; 95% CI −0.2298769 to −0.1152015; bootstrap-positive share 0/5,000.

## Supplement S5. Reproducibility and safeguards

1. **Chronological split:** models fit only on the first six calendar months. Validation is reporting-only. OOS is the final three months of each calendar sample.
2. **Point-in-time control:** Phase 92 lags option-derived IV, close-based proxy and OI by one full five-minute row; it also lags VIX. This is conservative relative to candle-start timestamps.
3. **Complete-case rule:** all candidate models in a comparison are scored on the same rows that have complete features and the forward target; no imputation is used.
4. **Cluster unit:** the confidence interval resamples trading-session clusters, retaining all rows inside selected sessions. This respects within-session grouping but is not an unlimited guarantee of future generalization.
5. **Protected holdout:** no Phase 90–92 run requested, loaded or analyzed the Phase 83 2026 holdout.
6. **Raw data handling:** raw Dhan responses were kept in Actions caches for the study and are not included in this public manuscript/supplement. Only aggregates, coverage ledgers and sanitized errors are published.
7. **No trading backtest:** there was no exact-contract entry/exit engine in Phases 89–92; Paytm Money brokerage, statutory charges, spread, slippage and latency costs are therefore not estimable from these predictor tests.

## Supplement S6. Figures

- [Figure S1: IV incremental effect across 2024 and 2023](IV_INCREMENTAL_EFFECTS.svg)
- [Figure S2: Phase 92 OOS model MAE comparison](OOS_MAE_COMPARISON.svg)

## Supplement S7. Important interpretive terms

- **Association:** a regression relationship between a feature and the target; it can exist without improved multivariate forecasting.
- **Incremental predictive value:** lower forecast loss than a baseline on data not used for fitting.
- **Rolling-ATM synthetic-forward proxy:** (K+C-P) built from rolling ATM bar closes. It is not validated as the actual traded FUTIDX price and cannot be interpreted as an executable arbitrage residual.
- **OOS:** fixed confirmatory evaluation window, not used for fitting/tuning.
- **Strategy evidence:** requires exact contract identity, realistic order/fill assumptions, costs and independent P&L validation. None of Phases 89–92 establishes it.

## Supplement S5. Audit of the 14 user-uploaded research PDFs

The supporting bibliography was expanded using a bounded audit of all 14 uploaded PDFs. The paper-by-paper extraction, classifications, author-reported findings, and limitations are documented in [Uploaded Literature Evidence Audit](../phase93/UPLOADED_LITERATURE_AUDIT.md).

| Evidence group | Sources | Main contribution to synthesis | Boundary |
|---|---|---|---|
| Daily NIFTY/index price forecasting | Bumrah & Budhani (2023); Sain & Singh (2026); Harish et al. (2023); Fathali et al. (2022); Kumar & Sharma (2016); Jafar et al. (2023); Kallimath et al. (2025); Bansal et al. (2022) | Daily price targets, deep/linear baseline comparisons, FII/USD features, feature selection and forecast evaluation | Not intraday option-strategy P&L; accuracy/RMSE metrics are not directly comparable to the phase 89–92 absolute 15-minute-return target |
| Context-rich forecasting | Naik & Inamdar (2024) | Candidate contexts: news sentiment, FII/DII, India VIX and put-call ratio | Context presence in a model does not prove incremental contribution or tradability |
| Moving-average evidence | Mahajan et al. (2025) | Example where index/EMA correlation is high but crossover outperformance versus passive investing is not statistically established in the authors' conclusion | Index-level test; not options execution |
| Options-strategy evidence | Atheetha et al. (2019); Shaha (SSRN); Sherasiya (2025) | Holding-period/timing risk, CCI momentum strategy, Greeks/IV/ML feature hypotheses | Reported returns are author claims and were not reproduced here; execution details and all project-standard costs are not established |
| Conceptual strategy reference | Chatterjee et al. (2022) | Background strategy/payoff taxonomy | Not an empirical executable backtest |

No estimates in Phases 89–92 were recomputed or changed by this audit. The full references list contains these sources as references 16–29.

