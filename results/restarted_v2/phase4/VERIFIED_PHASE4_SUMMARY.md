# Phase 4 Robustness — Verified Summary

Run: GitHub Actions run 37048711849  
Execution result: SUCCESS; 15 robustness scenarios completed.  
Primary sample: 2021-05-27 through 2026-09-30.

The runner produced the following verified summary rows in its job log. The original automated persistence push was rejected because the branch advanced concurrently; therefore these values are reconstructed directly from the successful run log and persisted here for audit.

| Scenario | Trades | Win rate | Mean net ₹ | Total net ₹ | Target exit rate |
|---|---:|---:|---:|---:|---:|
| threshold 90%, slip 0 | 196 | 36.735% | -310.99 | -60,953.24 | 36.735% |
| threshold 90%, slip 1 | 196 | 37.245% | -294.03 | -57,629.69 | 37.245% |
| threshold 90%, slip 2 | 196 | 37.245% | -283.03 | -55,473.32 | 37.245% |
| threshold 95%, slip 0 | 196 | 36.735% | -320.44 | -62,805.33 | 36.735% |
| threshold 95%, slip 1 (primary) | 196 | 37.245% | -303.48 | -59,481.78 | 37.245% |
| threshold 95%, slip 2 | 196 | 37.245% | -292.18 | -57,268.13 | 37.245% |
| threshold 97.5%, slip 0 | 196 | 37.245% | -318.22 | -62,371.46 | 37.245% |
| threshold 97.5%, slip 1 | 196 | 37.755% | -301.61 | -59,115.13 | 37.755% |
| threshold 97.5%, slip 2 | 196 | 37.755% | -290.59 | -56,956.48 | 37.755% |
| entry 09:45 | 197 | 35.025% | -232.54 | -45,810.99 | 35.025% |
| entry 10:00 (primary) | 196 | 37.245% | -303.48 | -59,481.78 | 37.245% |
| entry 10:15 | 197 | 37.056% | -299.84 | -59,069.11 | 37.056% |
| DTE 3 | 197 | 31.980% | +13.21 | +2,603.15 | 31.980% |
| DTE 4 (primary) | 196 | 37.245% | -303.48 | -59,481.78 | 37.245% |
| DTE 5 | 198 | 37.879% | -483.14 | -95,661.78 | 37.879% |

### Brokerage sensitivity

This is an exact re-costing of the 196 primary trades:

| Brokerage/order | Mean net ₹/trade | Total net ₹ | Total modeled costs ₹ |
|---:|---:|---:|---:|
| ₹0 | -243.48 | -47,721.78 | 4,841.28 |
| ₹10 | -303.48 | -59,481.78 | 16,601.28 |
| ₹20 | -363.48 | -71,241.78 | 28,361.28 |

### Interpretation

- The 95% threshold remains the locked primary specification.
- Across 90%, 95% and 97.5%, the strategy remained negative on net P&L in this historical sample.
- The DTE sensitivity is material: DTE=3 produced a small positive aggregate result in this backtest, whereas DTE=4 and DTE=5 were negative. This is a sensitivity finding, not a selection rule, because DTE=4 was pre-registered as primary.
- Entry-time changes did not materially change the overall negative result.
- Brokerage materially reduces net P&L, as expected from six modeled orders per trade.
- These are historical backtest diagnostics and do not establish future profitability.

### Audit note

The GitHub Actions runner successfully executed all 15 scenarios. The first persistence push was rejected due to a concurrent remote update. The persistence workflow was then corrected to fetch/rebase before pushing, and the Phase 4 workflow has now been restored to manual-only operation.
