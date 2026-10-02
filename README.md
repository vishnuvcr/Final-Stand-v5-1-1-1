# Final Stand v5 1-1-1-1

Research repository for systematic testing of the restarted NIFTY weekly-options 3-leg ratio strategy.

## Current status

**Phase 3 — STATISTICAL ANALYSIS: COMPLETE**

The latest two-stage strategy was tested on the validated executable sample. Prior global-selector results are superseded.

### Locked strategy

At 10:00 IST, four trading sessions before expiry:
- X_call6 = OTM8 CE + OTM7 CE - OTM6 CE
- X_put6 = OTM8 PE + OTM7 PE - OTM6 PE
- X_call6 > X_put6 -> user-defined BEARISH call structure
- X_call6 < X_put6 -> user-defined BULLISH put structure
- On the selected side, X(n) is calculated for n=6..15.
- Primary high-n rule: X(n) >= 95% of selected-side X_max, then choose highest n.
- Target: T = 0.9 * X_selected * lot quantity.
- Otherwise exit at expiry.
- One adverse tick per leg plus explicit transaction costs/brokerage.

## Phase 2 primary result

Sample: **2021-05-27 through 2026-09-30**.

- 196 trades
- Net win rate: 37.24%
- Mean net P&L: -₹303.48/trade
- Median net P&L: -₹448.21/trade
- Total net P&L: -₹59,481.78
- Total gross P&L: -₹42,880.50
- Modeled costs: ₹16,601.28
- Target exits: 73/196 (37.24%)
- Expiry exits: 123/196 (62.76%)

## Phase 3 statistical findings

- Profit factor: **0.719**
- Net-P&L standard deviation: **₹2,797.64/trade**
- Cumulative max drawdown: **₹80,224.28**
- Mean credit-normalized trade return: **-31.38%**
- Trade-level credit-normalized Sharpe (non-annualized): **-0.266**
- Bootstrap 95% CI for mean net P&L: **-₹702.98 to ₹86.52**
- Bootstrap 95% CI for win rate: **30.61% to 44.39%**

Yearly total net P&L:
- 2021: -₹7,813.05
- 2022: -₹1,314.54
- 2023: -₹9,536.07
- 2024: -₹4,283.23
- 2025: -₹47,088.19
- 2026: +₹10,553.30 (partial year through Sep-2026)

Exit-path decomposition is notable: all 73 target exits were profitable after modeled costs, while all 123 expiry exits were losses in this sample. This is a descriptive decomposition of the backtest, not evidence that future target exits will behave the same way.

Direction:
- BEARISH: 19 trades; mean net -₹632.24
- BULLISH: 177 trades; mean net -₹268.19

Selected n distribution:
- n=6: 188 trades
- n=7: 6
- n=8: 1
- n=15: 1

The single n=15 trade was profitable, but its sample size is one and therefore is not a reliable estimate of n=15 performance.

## Phase 3 artifacts

- results/restarted_v2/phase3/overall_statistics.csv
- results/restarted_v2/phase3/by_year_bootstrap.csv
- results/restarted_v2/phase3/by_direction.csv
- results/restarted_v2/phase3/by_n.csv
- results/restarted_v2/phase3/by_exit_reason.csv
- results/restarted_v2/phase3/selection_diagnostics.csv
- results/restarted_v2/phase3/equity_curve.csv
- results/restarted_v2/phase3/equity_curve.png
- results/restarted_v2/phase3/net_pnl_distribution.png
- results/restarted_v2/phase3/annual_net_pnl.png

## Research phases

1. Phase 1 — Restarted specification/audit **complete**
2. Phase 2 — Restarted primary backtest **complete**
3. Phase 3 — Statistical analysis **complete**
4. Phase 4 — Robustness and sensitivity **next**
5. Phase 5 — Final manuscript

Prior global-selector results remain in repository history for audit purposes only.
