# Phase 89 Results — rolling-options feature study

Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38047775690  
Status: **COMPLETE WITH DATA-COVERAGE CAVEAT — OOS sample gate passed on available aligned records**  
Data period requested: 2025-01-01 through 2025-12-31 exclusive. Protected 2026 Phase 83 holdout not requested or loaded.

## Data-quality and sample summary
- Valid API window/side responses: 25/26.
- Unique CALL timestamps: 17207; unique PUT timestamps: 18555.
- Exact timestamp pairs before spot-consistency check: 17204.
- Spot-mismatch pairs excluded: 25.
- CALL/PUT ATM-strike mismatches excluded: 35.
- Paired rows after spot check: 17144 across 230 sessions.
- Confirmatory OOS complete observations: 2622 across 57 sessions.
- OOS inferential gate (at least 1,000 complete rows and 30 sessions): **PASS**.

## Four preregistered OOS tests
| ID | Feature | Target | N | Sessions | Beta (bps per 1 SD feature) | 95% clustered CI | Raw p | Holm-adjusted p |
|---|---|---|---:|---:|---:|---|---:|---:|
| P1 | iv_mean | fwd15_abs_bps | 4049 | 57 | 0.602 | 0.225 to 0.980 | 0.0018 | 0.0071 |
| P2 | iv_skew | fwd15_bps | 4049 | 57 | -0.218 | -0.652 to 0.216 | 0.3240 | 0.9720 |
| P3 | oi_imbalance | fwd15_bps | 4049 | 57 | -0.118 | -0.567 to 0.330 | 0.6046 | 1.0000 |
| P4 | oi_change_15m | fwd15_bps | 2622 | 57 | -0.076 | -0.456 to 0.303 | 0.6931 | 1.0000 |

Interpret these only as predictive associations in an ATM-relative data representation. They are not causality, options P&L, or an executable strategy. All four tests are two-sided; standard errors are clustered by trading session/date. Holm correction applies only to this frozen four-test OOS family.

## Chronological sign replication
- **P1 — Mean ATM CALL/PUT IV → absolute next-15-minute NIFTY spot return.** DEV: beta=0.900 bps/SD, n=8699, sessions=123; VALIDATION: beta=0.511 bps/SD, n=3600, sessions=50; CONFIRMATORY_OOS: beta=0.602 bps/SD, n=4049, sessions=57.
- **P2 — PUT IV − CALL IV → signed next-15-minute NIFTY spot return.** DEV: beta=0.246 bps/SD, n=8699, sessions=123; VALIDATION: beta=-0.388 bps/SD, n=3600, sessions=50; CONFIRMATORY_OOS: beta=-0.218 bps/SD, n=4049, sessions=57.
- **P3 — (CALL OI − PUT OI)/(CALL OI + PUT OI) → signed next-15-minute NIFTY spot return.** DEV: beta=0.153 bps/SD, n=8699, sessions=123; VALIDATION: beta=-0.025 bps/SD, n=3600, sessions=50; CONFIRMATORY_OOS: beta=-0.118 bps/SD, n=4049, sessions=57.
- **P4 — Trailing 15-minute percentage change in total CALL+PUT OI → signed next-15-minute NIFTY spot return.** DEV: beta=0.054 bps/SD, n=5124, sessions=123; VALIDATION: beta=-0.220 bps/SD, n=2404, sessions=50; CONFIRMATORY_OOS: beta=-0.076 bps/SD, n=2622, sessions=57.

## API/data issues
- 2025-09-10–2025-10-08 CALL: HTTP 0, candles=0, aligned=False, error=TimeoutError

## Main interpretation rule
- A feature is only considered a candidate for further independent replication if its OOS Holm-adjusted p-value is below 0.05 and its effect direction is consistent in DEV and VALIDATION. This still does **not** approve a trading strategy.
- If the sample gate fails, p-values and signs are descriptive and no confirmatory inference is made.
- No transaction-cost-adjusted strategy P&L is possible from these fields. Exact listed contracts, historical bid/ask/depth, executable fills, Greek data, futures/synthetic futures and VIX are not covered by this endpoint study.
- Paytm Money brokerage/statutory charges, spread, slippage and latency must be frozen before any separate execution-quality replay.
