# Phase 51-3 Status

**State: CLOSED — PASS_AVAILABLE_OOS (partial diagnostic only; no promotion).**

Authoritative source-faithful orchestrator run: [37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283), completed successfully on 2026-10-09. All source, candidate-result, data-error and audit steps passed.

## Frozen source and interval

- Options: `rissin/nse-options-intraday / upstox_intraday/NIFTY/NIFTY_2026.parquet`
- SHA-256: `bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73`
- Size: 394,805,617 bytes
- Spot: validated Technovusin NIFTY 1-minute CSV source, cached by Actions
- Spot observations: 23,625; first 2026-04-21 09:15 IST; last 2026-07-21 15:29 IST
- Observed weekly expiry universe: 14 expiries, 2026-04-21 through 2026-07-21
- Evaluation window: **2026-04-21 through 2026-07-21**, explicitly partial OOS only

## Evidence-grade candidate summaries

| Candidate | Trades | Coverage | Data errors | Net ₹10/order | Net +50% friction | Net ₹20/order | Net ₹20/order +50% |
|---|---:|---:|---:|---:|---:|---:|---:|
| TT-02 | 13 | 100% | 0 | -1,341.12 | -2,936.31 | -3,701.12 | -6,476.31 |
| TT-04 | 62 | 100% | 0 | +13,271.51 | +10,287.26 | +10,345.11 | +5,897.66 |
| TT-05 | 62 | 100% | 0 | +17,098.15 | +14,239.72 | +14,171.75 | +9,850.12 |

Descriptive trade statistics from the saved chronological trade ledgers:

| Candidate | Mean net/trade | Median net/trade | Win rate | Max peak-to-trough drawdown of cumulative trade P&L |
|---|---:|---:|---:|---:|
| TT-02 | -₹103.16 | -₹1,530.71 | 38.5% | ₹27,015.52 |
| TT-04 | +₹214.06 | +₹884.94 | 67.7% | ₹12,024.81 |
| TT-05 | +₹275.78 | +₹1,056.82 | 66.1% | ₹12,217.19 |

Drawdown above is computed on cumulative trade-level net P&L in the saved trade order; it is not a capital-normalized drawdown and does not substitute for a mark-to-market portfolio equity curve. These figures are descriptive for this short partial interval only.

## Interpretation and decision

- TT-04 and TT-05 are positive in this partial diagnostic window under all four recorded cost/friction scenarios; this is not sufficient to promote either strategy.
- TT-02 is negative under all four scenarios and is not a leader in this window.
- TT-03 is not included in the sweep because the exact frozen entry rule yields no eligible campaigns for this observed Tuesday expiry schedule; Phase 51-2 already documented that non-informative outcome. TT-06 and TT-07 remain terminal feasibility/coverage failures from Phase 50B.
- No parameter tuning, hypothesis testing, or strategy promotion was performed.
- The finite Phase-51-3 diagnostic is complete. Its completion marker is set; manual workflow dispatch remains available.

## Remaining Phase-51 gate

This result **does not close full Phase 51**. The preregistered full OOS window remains 2026-04-21 through 2026-08-04. The 2026-07-28 and 2026-08-04 option blocks remain unresolved and must be recovered from an accepted raw-data source before final full-window OOS claims.

## Files

- [Final partial-OOS report](results/phase51/available_oos/PHASE51_3_AVAILABLE_OOS_REPORT.md)
- [Raw sweep summary](results/phase51/available_oos/sweep_summary.json)
- [Error log](PHASE51_3_ERROR_LOG.md)
- [Chat log](PHASE51_3_CHAT_LOG.md)
- [Research plan](PHASE51_3_RESEARCH_PLAN.md)
- [Authoritative Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283)
