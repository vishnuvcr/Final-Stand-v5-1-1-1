# Phase 92 Results — synthetic-forward proxy and CALL/PUT OI imbalance

Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106  
Status: **NEGATIVE INCREMENTAL VALUE — synthetic-forward/OI feature block worsens OOS magnitude prediction in this sample**  
Sample: calendar 2022 only. Phase 90/91 cached payloads are not reused. The protected Phase 83 2026 holdout was not requested or loaded.

## Coverage and data-quality summary
- Options chunks valid: 54/54.
- India VIX chunks valid: 5/5.
- Instrument-master resolution: UNIQUE_MATCH; unique eligible India VIX IDs=1.
- Paired option rows after spot/strike validation: 18579 across 248 sessions.
- Mismatched spot rows excluded: 0; mismatched strike rows excluded: 1.
- Valid lagged IV coverage=0.9867; synthetic-gap coverage=0.9867; OI-imbalance coverage=0.9867.
- Lagged VIX row coverage=0.9832; OOS VIX coverage=0.9863.
- Complete OOS rows/sessions with the full predictor set: 3660/61.
- Minimum sample gate: PASS; India VIX gate: PASS.

## Frozen models
M0 = lagged spot realized movement, signed 15/60-minute returns and time-of-day terms.  
M1 = M0 + India VIX level and trailing 15-minute VIX change.  
M2 = M1 + mean ATM CALL/PUT IV.  
M3 = M2 + a lagged rolling-ATM synthetic-forward proxy gap, defined as (K + CALL close − PUT close − spot) / spot × 10,000 bps.  
M4 = M3 + lagged CALL/PUT OI imbalance, defined as (CALL OI − PUT OI) / (CALL OI + PUT OI), where the denominator is positive.

Option IV, close-derived synthetic proxy and OI features are lagged one full five-minute row to avoid using current-candle close/OI values before the candle is complete. VIX candles are conservatively lagged one row, too. The CALL and PUT strikes must match at the paired timestamp. All scaling and coefficients are fitted on DEV only; validation is report-only; predictions are clipped at zero. All compared models are scored on the same complete rows.

**Primary endpoint:** M2 MAE − M4 MAE. Positive values favour the combined synthetic-forward/OI feature block. The M2-to-M3 and M3-to-M4 differences are secondary descriptive model comparisons only; no separate subgroup significance tests are performed.

| Split | Model | N | Sessions | MAE (bps) | RMSE (bps) | R² |
|---|---|---:|---:|---:|---:|---:|
| VALIDATION | M0_spot_only | 3780 | 63 | 6.0337 | 7.7099 | 0.0425 |
| CONFIRMATORY_OOS | M0_spot_only | 3660 | 61 | 5.4719 | 6.9444 | -0.0269 |
| VALIDATION | M1_spot_plus_VIX | 3780 | 63 | 5.7791 | 7.5700 | 0.0770 |
| CONFIRMATORY_OOS | M1_spot_plus_VIX | 3660 | 61 | 4.7987 | 6.6109 | 0.0693 |
| VALIDATION | M2_spot_VIX_plus_IV | 3780 | 63 | 5.7788 | 7.5643 | 0.0783 |
| CONFIRMATORY_OOS | M2_spot_VIX_plus_IV | 3660 | 61 | 4.8214 | 6.6003 | 0.0723 |
| VALIDATION | M3_add_synthetic_forward_proxy | 3780 | 63 | 5.7763 | 7.5691 | 0.0772 |
| CONFIRMATORY_OOS | M3_add_synthetic_forward_proxy | 3660 | 61 | 4.8791 | 6.6208 | 0.0665 |
| VALIDATION | M4_add_synthetic_proxy_and_OI | 3780 | 63 | 5.7466 | 7.5783 | 0.0749 |
| CONFIRMATORY_OOS | M4_add_synthetic_proxy_and_OI | 3660 | 61 | 4.9922 | 6.6615 | 0.0550 |

## Figure 1 — out-of-sample MAE comparison

![Phase 92 OOS MAE comparison](OOS_MAE_COMPARISON.svg)

## Primary result
M2 MAE − M4 MAE = -0.1708 bps (paired session-cluster bootstrap 95% CI -0.2299 to -0.1152; bootstrap positive share 0.0000; 5000 resamples; seed 90210).

## Effect size
OOS MAE changes from 4.8214 to 4.9922 bps, a -3.5433% relative reduction. RMSE changes by -0.0612 bps; R² moves from 0.0723 to 0.0550. The confidence interval, not the point estimate alone, governs the registered conclusion.

Decision rule: claim added predictive value only if all data/sample gates pass and the entire 95% paired session-cluster bootstrap interval for M2 MAE − M4 MAE is above zero. If the entire interval is below zero, the feature block degraded prediction in this fixed sample; if it includes zero, no gain is established. Neither outcome is strategy P&L evidence and neither proves the features contain no information.

## Descriptive VIX regimes
VIX tertiles are determined on DEV data. The following are descriptive only and must not be used to select features or strategies:
- LOW_VIX: rows=3416, sessions=58, M2 baseline MAE=4.6693, M4 full-feature MAE=4.8550, delta=-0.1857 bps.
- MID_VIX: rows=244, sessions=6, M2 baseline MAE=6.9513, M4 full-feature MAE=6.9142, delta=0.0371 bps.

## API/data issues
- No API/network/schema failures.

## Interpretation limits
This is a predictor study of absolute next-15-minute spot-return magnitude, not a direction classifier, strategy P&L study, or executable futures/option strategy. The synthetic-forward proxy is calculated from rolling ATM CALL/PUT bar closes; it is **not** a traded NIFTY futures price or an arbitrage signal. The endpoint does not provide exact listed-contract bid/ask/depth, transaction latency, or executable fills. No direct historical FUTIDX basis is claimed, no strategy P&L is computed, and no strategy is promoted. Any later rule-level replay requires authorized exact-contract data and Paytm Money brokerage, statutory levies, spread, adverse slippage, latency and stress costs.
