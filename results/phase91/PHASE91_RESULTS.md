# Phase 91 Results — incremental IV prediction beyond spot and India VIX

Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38049680438  
Status: **NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero**  
Sample: calendar 2023 only. Protected Phase 83 2026 holdout was not requested or loaded.

## Coverage and data-quality summary
- Options chunks valid: 54/54.
- India VIX chunks valid: 5/5.
- Instrument-master resolution: UNIQUE_MATCH; unique eligible India VIX IDs=1.
- Paired option rows after spot/strike validation: 18473 across 246 sessions.
- VIX row coverage=0.9998; OOS VIX coverage=0.9998.
- Complete OOS rows/sessions: 3633/60.
- Minimum sample gate: PASS; India VIX coverage gate: PASS.

## Frozen model comparison
M0 = lagged realized movement, signed 15/60-minute returns and time-of-day terms.  
M1 = M0 + India VIX level + its trailing 15-minute percentage change.  
M2 = M1 + mean ATM CALL/PUT IV.  
All model scaling and coefficients are fit on DEV only. Validation cannot tune the model. Nonnegative predictions are clipped at zero for both compared models.

| Split | Model | N | Sessions | MAE (bps) | RMSE (bps) | R² |
|---|---|---:|---:|---:|---:|---:|
| VALIDATION | M0_spot_only | 3814 | 63 | 4.2052 | 5.5479 | 0.0033 |
| CONFIRMATORY_OOS | M0_spot_only | 3633 | 60 | 4.0192 | 5.5626 | 0.0563 |
| VALIDATION | M1_spot_plus_VIX | 3814 | 63 | 4.0386 | 5.5503 | 0.0024 |
| VALIDATION | M2_spot_VIX_plus_IV | 3814 | 63 | 4.0384 | 5.5397 | 0.0062 |
| CONFIRMATORY_OOS | M1_spot_plus_VIX | 3633 | 60 | 3.9156 | 5.5163 | 0.0719 |
| CONFIRMATORY_OOS | M2_spot_VIX_plus_IV | 3633 | 60 | 3.9155 | 5.5135 | 0.0729 |

## Preregistered primary endpoint
M1 MAE − M2 MAE = 0.0001 bps (paired session-cluster bootstrap 95% CI -0.0111 to 0.0103; bootstrap positive share 0.5240; 5000 resamples).

## Effect size and caution
The OOS MAE falls from 3.9156 to 3.9155 bps, a 0.0028% relative reduction; RMSE falls by 0.0028 bps and R² moves from 0.0719 to 0.0729. The lower confidence limit (-0.0111 bps) is very close to zero, so the gain is small and should be independently replicated before strategy use.

Decision rule: only claim incremental predictive value if the sample and VIX gates pass and the 95% bootstrap interval for M1 MAE − M2 MAE is wholly above zero. Otherwise the registered test does not establish a gain; that is not proof IV has no information.

## Descriptive out-of-sample VIX regimes
DEV VIX tertiles define LOW/MID/HIGH; results below are descriptive only, with no subgroup hypothesis tests.
- HIGH_VIX: rows=449, sessions=10, M1 MAE=5.1859, M2 MAE=5.2215, delta=-0.0356 bps.
- LOW_VIX: rows=2302, sessions=42, M1 MAE=3.5942, M2 MAE=3.5896, delta=0.0046 bps.
- MID_VIX: rows=882, sessions=22, M1 MAE=4.1078, M2 MAE=4.1012, delta=0.0065 bps.

## API/data issues
- No API/network/schema failures.

## Interpretation limits
A positive primary result means improved prediction of near-term spot move magnitude in this 2023 sample conditional on lagged spot features and India VIX. It does not establish directional skill, causality, strategy profitability or executable fills. The rolling ATM-relative endpoint does not provide historical exact-contract bid/ask/depth. Any later trading replay must include Paytm Money charges, spreads, slippage and latency. No strategy is promoted.
