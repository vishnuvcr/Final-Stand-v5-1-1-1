# Phase 89 Results — rolling-options feature study

Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38047563119  
Status: **COMPLETE — OOS sample gate passed; interpret only the four Holm-controlled feature associations**  
Data period requested: 2025-01-01 through 2026-01-01 exclusive. Protected 2026 Phase 83 holdout not requested or loaded.

## Data-quality and sample summary
- Valid API window/side responses: 28/28.
- Unique CALL timestamps: 18632; unique PUT timestamps: 18630.
- Exact timestamp pairs before spot-consistency check: 18629.
- Spot-mismatch pairs excluded: 25.
- Paired rows after spot check: 18604 across 249 sessions.
- Confirmatory OOS complete observations: 4224 across 62 sessions.
- OOS inferential gate (at least 1,000 complete rows and 30 sessions): **PASS**.

## Four preregistered OOS tests
| ID | Feature | Target | N | Sessions | Beta (bps per 1 SD feature) | 95% clustered CI | Raw p | Holm-adjusted p |
|---|---|---|---:|---:|---:|---|---:|---:|
| P1 | iv_mean | fwd15_abs_bps | 4410 | 62 | 0.586 | 0.225 to 0.947 | 0.0015 | 0.0059 |
| P2 | iv_skew | fwd15_bps | 4410 | 62 | -0.065 | -0.514 to 0.384 | 0.7773 | 1.0000 |
| P3 | oi_imbalance | fwd15_bps | 4410 | 62 | -0.092 | -0.508 to 0.324 | 0.6651 | 1.0000 |
| P4 | oi_change_15m | fwd15_bps | 4224 | 62 | 0.380 | 0.102 to 0.658 | 0.0073 | 0.0219 |

Interpret these only as predictive associations in an ATM-relative data representation. They are not causality, options P&L, or an executable strategy. All four tests are two-sided; standard errors are clustered by trading session/date. Holm correction applies only to this frozen four-test OOS family.

## Chronological sign replication
- **P1 — Mean ATM CALL/PUT IV → absolute next-15-minute NIFTY spot return.** DEV: beta=0.940 bps/SD, n=8782, sessions=123; VALIDATION: beta=0.628 bps/SD, n=4608, sessions=64; CONFIRMATORY_OOS: beta=0.586 bps/SD, n=4410, sessions=62.
- **P2 — PUT IV − CALL IV → signed next-15-minute NIFTY spot return.** DEV: beta=0.260 bps/SD, n=8782, sessions=123; VALIDATION: beta=-0.121 bps/SD, n=4608, sessions=64; CONFIRMATORY_OOS: beta=-0.065 bps/SD, n=4410, sessions=62.
- **P3 — (CALL OI − PUT OI)/(CALL OI + PUT OI) → signed next-15-minute NIFTY spot return.** DEV: beta=0.056 bps/SD, n=8782, sessions=123; VALIDATION: beta=0.078 bps/SD, n=4608, sessions=64; CONFIRMATORY_OOS: beta=-0.092 bps/SD, n=4410, sessions=62.
- **P4 — Trailing 15-minute percentage change in total CALL+PUT OI → signed next-15-minute NIFTY spot return.** DEV: beta=0.145 bps/SD, n=8363, sessions=123; VALIDATION: beta=0.279 bps/SD, n=4416, sessions=64; CONFIRMATORY_OOS: beta=0.380 bps/SD, n=4224, sessions=62.

## API/data issues
- No API/network/schema failures were observed.

## Main interpretation rule
- A feature is only considered a candidate for further independent replication if its OOS Holm-adjusted p-value is below 0.05 and its effect direction is consistent in DEV and VALIDATION. This still does **not** approve a trading strategy.
- If the sample gate fails, p-values and signs are descriptive and no confirmatory inference is made.
- No transaction-cost-adjusted strategy P&L is possible from these fields. Exact listed contracts, historical bid/ask/depth, executable fills, Greek data, futures/synthetic futures and VIX are not covered by this endpoint study.
- Paytm Money brokerage/statutory charges, spread, slippage and latency must be frozen before any separate execution-quality replay.
