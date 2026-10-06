# Phase 36 Manuscript — Independent Per-Trade Direction Selector Overlay for Continuous Delta 6x6

## Abstract
This phase tested whether the Continuous Delta 6x6 NIFTY 50 vertical-spread strategy benefits from removing its prior-trade state dependence. In the control strategy, a winning trade retains direction and a losing trade reverses direction. Phase 36 instead makes every new trade's direction an independent decision, using seven preregistered selectors: OTM678 fresh premium curvature, OTM789 fresh premium curvature, CatBoost, LightGBM-DART, Wavelet-tree, OOF stack, and Markov-regime tree. All non-direction rules were frozen, including 6 lots per leg, 50-point width, ±0.25 entry delta, ±0.50/±0.04 exits, expiry rules, adverse option slippage, brokerage and statutory transaction costs.

Across 2024-01-01 to 2026-06-30, the stateful control generated ₹63,672.58 net P&L over 206 trades. Every independent selector was net negative. The best was OTM789_FRESH at -₹39,122.38; the worst was CatBoost at -₹92,977.93. The 2026 holdout was decisive: all independent selectors lost ₹68,854 to ₹89,078, while the control was approximately flat at -₹276. Per-expiry bootstrap comparisons also favored the stateful control for every selector. The independent-direction hypothesis is rejected.

## 1. Research question
Does removing the previous trade's P&L/status/direction from the Continuous Delta 6x6 direction state machine improve post-cost performance and robustness?

## 2. Aims and objectives
The aim was to isolate the contribution of direction-state dependence while freezing all execution parameters.

Objectives:
- test seven preregistered direction selectors;
- prevent previous trade status from entering the next direction decision;
- preserve identical entry, exit and transaction-cost rules;
- compare with the published stateful Phase-32 control;
- examine 2024-2025 validation behavior and untouched 2026 holdout behavior;
- preserve all accepted ledgers and error logs in the repository.

## 3. Scientific methodology
### Experimental unit
Each completed Continuous Delta 6x6 trade is an execution unit; expiry-level blocks are used for the primary robustness comparison.

### Frozen strategy
NIFTY 50 current weekly expiry, ₹6,00,000 reference capital, 6 lots per leg, 50-point vertical, entries from 09:20 IST, no expiry-day new entries, last-entry cutoff 15:28 IST, short option nearest ±0.25 delta, 50-point protective leg, delta exits at ±0.50 or ±0.04, carry across sessions, and identical Phase-32 cost/slippage logic.

### Direction treatments
OTM678_FRESH and OTM789_FRESH are recomputed from the current option snapshot before each eligible entry. The five model selectors use frozen Phase-35 forecasts for the corresponding expiry. No model selector is updated with a Phase-36 outcome.

### Independence constraint
The selection function never consumes previous trade P&L, previous win/loss status, prior direction, or cumulative strategy P&L. The only retained state is the chronological cursor needed to prevent overlapping positions.

## 4. Data and coverage
The primary window is 2024-01-01 through 2026-06-30. There were 128 expected expiries, 104 corresponding historical option files available, and one additional expiry incomplete. The final treatments processed 103 available expiry files. The Phase-35 selector cache contains 117 event forecasts from 2024-01-11 through 2026-06-30.

## 5. Statistical analysis
Primary metrics: net P&L, gross P&L, costs, win rate, profit factor and maximum drawdown. Temporal robustness is assessed by 2024-2025 versus 2026. A bootstrap over common expiry blocks estimates uncertainty in selector-minus-control P&L differences.

## 6. Results

### 6.1 Primary sample
| Strategy | Trades | Net P&L | Costs | Win rate | PF | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| Stateful control | 206 | ₹63,672.58 | ₹20,381.42 | 65.53% | 1.203 | ₹61,960.87 |
| OTM789 fresh | 213 | -₹39,122.38 | ₹22,653.88 | 61.03% | 0.898 | ₹102,707.29 |
| OTM678 fresh | 210 | -₹62,665.27 | ₹22,885.27 | 60.00% | 0.841 | ₹120,108.87 |
| DART | 189 | -₹54,475.24 | ₹19,586.74 | 57.14% | 0.853 | ₹78,949.87 |
| OOF stack | 189 | -₹59,868.85 | ₹20,118.85 | 55.56% | 0.845 | ₹91,212.84 |
| Wavelet-tree | 192 | -₹66,398.02 | ₹20,471.02 | 55.73% | 0.825 | ₹97,508.24 |
| Markov-regime tree | 190 | -₹88,163.44 | ₹20,399.44 | 55.26% | 0.773 | ₹106,087.37 |
| CatBoost | 184 | -₹92,977.93 | ₹20,406.43 | 54.89% | 0.757 | ₹114,550.42 |

![Primary net P&L](figures/PHASE36_NET_PNL.svg)

### 6.2 2024-2025
The stateful control produced ₹63,948.22. OTM789 and OTM678 were the strongest independent selectors but still returned only ₹37,147.02 and ₹26,413.08. The best model selector was OOF stack at ₹18,277.28. CatBoost and Markov-regime tree were negative even in this earlier period.

### 6.3 2026 holdout
All independent selectors were negative:
- OTM789 fresh: -₹76,269.40
- OTM678 fresh: -₹89,078.35
- DART: -₹68,854.50
- Markov-regime tree: -₹71,769.89
- CatBoost: -₹78,854.87
- Wavelet-tree: -₹80,577.21
- OOF stack: -₹78,146.12

The control was approximately flat at -₹275.65.

![2026 holdout net P&L](figures/PHASE36_2026_HOLDOUT.svg)

### 6.4 Control-relative bootstrap
All seven mean per-expiry differences were negative and their 95% bootstrap intervals were entirely below zero. The least negative was OTM789, with approximately -₹1,069.73 per common expiry block and 95% CI [-₹2,068.22, -₹101.27].

### 6.5 Drawdown
All independent selectors had larger maximum drawdown than the control. OTM678 reached approximately ₹1.20 lakh and CatBoost approximately ₹1.15 lakh versus ₹61,961 for the stateful control.

![Maximum drawdown](figures/PHASE36_MAX_DRAWDOWN.svg)

## 7. Discussion
The experiment isolates a nontrivial result: the prior-trade outcome is economically useful state in this strategy. Replacing the existing state transition with independent point-in-time selectors reduced the historical edge even when those selectors included the strongest predictive candidates from Phase 35.

The fact that the five model selectors also failed in 2026 argues against simply choosing a better predictive classifier as a drop-in replacement. The two fresh OTM selectors likewise failed despite using contemporaneous option-premium information at every entry.

This does not prove that the state machine is causal in an economic sense. It shows that, under the audited execution model and the tested historical sample, removing it makes the strategy materially worse.

## 8. Strengths
- single conceptual experimental change;
- explicit independence constraint;
- frozen preregistration;
- realistic historical slippage and costs;
- 2026 holdout preserved from the Phase-35 development process;
- complete per-selector artifacts and error logs;
- automated GitHub Actions with manual workflow dispatch.

## 9. Limitations
- historical option-source gaps: 24 expected files unavailable and one additional file incomplete;
- 2026 holdout has only 34-43 selector trades;
- historical fills use the Phase-32 cost/slippage model rather than full order-book latency simulation;
- model selectors are frozen per expiry rather than re-estimated after each intraday event;
- the stateful control ledger has no realized trade after 2026-05-19 even though the calendar window extends to 2026-06-30.

## 10. Conclusion
**The independent-direction overlay is rejected.**

For this Continuous Delta 6x6 strategy, the previous trade's status/P&L transition should remain part of the canonical direction rule. None of the seven independent selectors improves post-cost performance, drawdown, or holdout robustness.

No Phase-36 selector is promoted to live trading.

## 11. Future research
The next highest-value research phase is forward/paper validation of the canonical stateful strategy with full bid/ask spreads, fill probability, latency and Paytm Money-specific transaction costs. Any attempt to redesign the direction state machine should be separately preregistered and must not retune parameters from the Phase-36 results.

## Appendix A — Repository artifacts
Each selector directory contains trades.csv, skips.csv, summary.csv, yearly_statistics.csv, direction_statistics.csv, selector_usage.csv, coverage.json and run.log.

## Appendix B — Audit trail
- F36-001: mixed audit-row widths, corrected before accepted evidence.
- F36-002: duplicate same-timestamp strike rows in fresh selectors, corrected before final evidence.
- Final run #4 completed successfully and published all selector artifacts.
