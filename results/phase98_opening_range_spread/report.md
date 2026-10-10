# Phase 98 — NIFTY Opening-Range Debit-Spread Results

**Computation:** PASS. **Economic decision:** NO_PROMOTION. **Live/paper promotion:** NO.

- Dataset revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Option expiry files loaded (expiry <= 2025-12-31): 0
- Validation sessions: 497; Arm A trades: 0; Arm B trades: 0
- Arm A validation net P&L: base ₹0.00; severe stress ₹0.00
- Arm B validation net P&L: base ₹0.00; severe stress ₹0.00
- Unknown validation returns: H1=334; H2=334

## Frozen strategy
Arm A is the first observed close outside the 09:15–09:29 NIFTY range. Entry is the next minute's exact option open, using one-lot ATM long / two-strike-step OTM short debit vertical. Target/stop are evaluated on paired closes; fills are next-minute opens or the 15:15 time exit.
Arm B is identical but skips signals only when prior-session India VIX exceeds the prior-only trailing 252-close 75th percentile.

## Validation summary

| arm   | split      |   completed_trades |   base_net_pnl |   stress_net_pnl | mean_net_per_trade   | median_net_per_trade   | win_rate   | profit_factor   | max_drawdown_trade_order   | worst_trade   | expected_shortfall_95   |   stress_completed_trades |
|:------|:-----------|-------------------:|---------------:|-----------------:|:---------------------|:-----------------------|:-----------|:----------------|:---------------------------|:--------------|:------------------------|--------------------------:|
| arm_a | validation |                  0 |              0 |                0 |                      |                        |            |                 |                            |               |                         |                         0 |
| arm_b | validation |                  0 |              0 |                0 |                      |                        |            |                 |                            |               |                         |                         0 |

## Primary inference

{
  "seed": 980010,
  "resamples": 10000,
  "block_length_sessions": 5,
  "validation_sessions": 497,
  "h1_unknown_sessions": 334,
  "h2_unknown_sessions": 334,
  "arm_a_completed_trades": 0,
  "arm_b_completed_trades": 0,
  "H1_arm_A_positive_daily_net": {
    "status": "NOT_ESTIMABLE_UNKNOWN_SESSIONS",
    "mean": null,
    "ci95": null,
    "p": null,
    "p_holm_adjusted": null
  },
  "H2_filter_paired_daily_uplift": {
    "status": "NOT_ESTIMABLE_UNKNOWN_SESSIONS",
    "mean": null,
    "ci95": null,
    "p": null,
    "p_holm_adjusted": null
  }
}

## Coverage reasons

| reason                         |   count |
|:-------------------------------|--------:|
| INDEX_OPENING_RANGE_INCOMPLETE |       5 |
| INDEX_SIGNAL_SCAN_INCOMPLETE   |       4 |
| NO_ALLOWED_EXPIRY_BEFORE_2026  |       1 |
| NO_BREAKOUT                    |       6 |
| NO_CHAIN_ROWS_FOR_SESSION      |    1126 |

Source/schema issue events: 1126.

## Decision and limitations
- Option OHLC bar opens plus fixed slippage are modeled references, not full historical bid/ask/depth, latency, or guaranteed fills.
- Computation PASS is not proof of profitability. Unknown signal-session returns block an inferential claim.
- The protected Phase 83 2026 holdout was not loaded; Phase 98 cannot promote live or paper trading.

## Reproducibility files
- summary.csv, coverage_audit.csv, trade_ledger.csv, daily_returns.csv, monthly_stability.csv
- inference.json, decision.json, source_manifest.json, validation_report.json
