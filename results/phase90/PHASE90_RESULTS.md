# Phase 90 Results — incremental IV prediction beyond spot and India VIX

Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38048410498  
Status: **PASS — IV improves out-of-sample magnitude prediction beyond lagged spot features and India VIX**  
Sample: calendar 2024 only. Protected Phase 83 2026 holdout was not requested or loaded.

## Coverage and data-quality summary
- Options chunks valid: 54/54.
- India VIX chunks valid: 5/5.
- Instrument-master resolution: UNIQUE_MATCH; unique eligible India VIX IDs=1.
- Paired option rows after spot/strike validation: 18554 across 248 sessions.
- VIX row coverage=0.9964; OOS VIX coverage=0.9973.
- Complete OOS rows/sessions: 3604/60.
- Minimum sample gate: PASS; India VIX coverage gate: PASS.

## Frozen model comparison
M0 = lagged realized movement, signed 15/60-minute returns and time-of-day terms.  
M1 = M0 + India VIX level + its trailing 15-minute percentage change.  
M2 = M1 + mean ATM CALL/PUT IV.  
All model scaling and coefficients are fit on DEV only. Validation cannot tune the model. Nonnegative predictions are clipped at zero for both compared models.

| Split | Model | N | Sessions | MAE (bps) | RMSE (bps) | R² |
|---|---|---:|---:|---:|---:|---:|
| VALIDATION | M0_spot_only | 3825 | 64 | 4.6408 | 7.8210 | 0.1129 |
| CONFIRMATORY_OOS | M0_spot_only | 3604 | 60 | 6.0338 | 9.2211 | 0.0518 |
| VALIDATION | M1_spot_plus_VIX | 3825 | 64 | 4.5953 | 7.7968 | 0.1183 |
| VALIDATION | M2_spot_VIX_plus_IV | 3825 | 64 | 4.5888 | 7.7680 | 0.1248 |
| CONFIRMATORY_OOS | M1_spot_plus_VIX | 3604 | 60 | 5.9953 | 9.2126 | 0.0536 |
| CONFIRMATORY_OOS | M2_spot_VIX_plus_IV | 3604 | 60 | 5.9623 | 9.1920 | 0.0578 |

## Preregistered primary endpoint
M1 MAE − M2 MAE = 0.0330 bps (paired session-cluster bootstrap 95% CI 0.0001 to 0.0562; bootstrap positive share 0.9750; 5000 resamples).

Decision rule: only claim incremental predictive value if the sample and VIX gates pass and the 95% bootstrap interval for M1 MAE − M2 MAE is wholly above zero. Otherwise the registered test does not establish a gain; that is not proof IV has no information.

## Descriptive out-of-sample VIX regimes
DEV VIX tertiles define LOW/MID/HIGH; results below are descriptive only, with no subgroup hypothesis tests.
- HIGH_VIX: rows=299, sessions=11, M1 MAE=6.3325, M2 MAE=6.2952, delta=0.0372 bps.
- LOW_VIX: rows=897, sessions=21, M1 MAE=4.6276, M2 MAE=4.5847, delta=0.0428 bps.
- MID_VIX: rows=2408, sessions=46, M1 MAE=6.4629, M2 MAE=6.4340, delta=0.0289 bps.

## API/data issues
- No API/network/schema failures.

## Interpretation limits
A positive primary result means improved prediction of near-term spot move magnitude in this 2024 sample conditional on lagged spot features and India VIX. It does not establish directional skill, causality, strategy profitability or executable fills. The rolling ATM-relative endpoint does not provide historical exact-contract bid/ask/depth. Any later trading replay must include Paytm Money charges, spreads, slippage and latency. No strategy is promoted.
