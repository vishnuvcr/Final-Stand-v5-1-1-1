# Phase 36 Status — Independent Per-Trade Direction Selector Overlay

## Final state
**COMPLETE — REJECTED — NO LIVE-TRADING PROMOTION**

The previous trade's status, P&L, win/loss result and prior direction remain part of the Continuous Delta 6x6 direction mechanism. Removing that state and using an independent selector before every new trade worsened net performance and holdout robustness.

## Accepted final evidence
- Final GitHub Actions run: **37428502722 / #4**
- Corrected source revision: `c8963bcded49ae15cf5b059394f3471ec1c3f2a4`
- All seven selector jobs: success
- Artifact publication job: success
- Per-selector numerical artifacts persisted in the Phase-36 branch.

## Primary sample
2024-01-01 through 2026-06-30.
128 expected expiries; 104 corresponding option files available; 1 additional expiry file incomplete; 103 expiry files processed in final treatments.

## Final performance
| Selector | Net P&L | Trades | Win rate | Profit factor | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Stateful control | ₹63,672.58 | 206 | 65.53% | 1.203 | ₹61,960.87 |
| OTM789_FRESH | -₹39,122.38 | 213 | 61.03% | 0.898 | ₹102,707.29 |
| DART | -₹54,475.24 | 189 | 57.14% | 0.853 | ₹78,949.87 |
| OOF_STACK | -₹59,868.85 | 189 | 55.56% | 0.845 | ₹91,212.84 |
| OTM678_FRESH | -₹62,665.27 | 210 | 60.00% | 0.841 | ₹120,108.87 |
| WAVELET_TREE | -₹66,398.02 | 192 | 55.73% | 0.825 | ₹97,508.24 |
| MARKOV_REGIME_TREE | -₹88,163.44 | 190 | 55.26% | 0.773 | ₹106,087.37 |
| CATBOOST | -₹92,977.93 | 184 | 54.89% | 0.757 | ₹114,550.42 |

## 2026 holdout
All seven independent selectors were negative. The stateful control was approximately flat at **-₹275.65** over 34 trades.

## Statistical comparison
The per-expiry selector-minus-control bootstrap comparison was negative for every selector. The 95% bootstrap interval for every selector was entirely below zero; the least negative was OTM789_FRESH at approximately -₹1,069.73 per common expiry block with CI [-₹2,068.22, -₹101.27].

## Error and correction history
- **F36-001:** mixed skip-record widths in the initial engine run; corrected to a fixed audit schema.
- **F36-002:** duplicate same-timestamp strike rows in fresh selectors; corrected with deterministic per-strike quote collapse.
- **F36-003:** final artifact-manifest blob mapping error; corrected in repository and logged as a packaging-only, non-evidence mistake.
- Final corrective run #4 completed successfully.

## Final recommendation
Retain the Phase-32 stateful direction rule. Do not promote any Phase-36 independent selector. The next research priority is forward/paper validation of the canonical stateful strategy with full execution realism, including bid/ask, latency, fill probability and broker-specific Paytm Money charges.
