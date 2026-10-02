# Final Stand v5 1-1-1-1

Systematic options-strategy research repository.

## Latest research status

**Dynamic-n corrected primary research is complete. Stop-loss research is complete through Phase 19.**

### Locked dynamic-n primary

- 190 trades
- Net P&L: **₹138,937.12**
- Net win rate: **94.21%**
- 178 target exits
- 12 expiry exits
- 11 losing trades, all expiry exits
- Maximum drawdown: **₹27,321.08**

Controlled n-selection ablation showed that the 95%-band dynamic-n preference did **not** add incremental aggregate P&L versus fixed n=6 on the same trade universe: fixed n=6 returned ₹139,543.97 versus ₹138,937.12 for dynamic n.

### Stop-loss research

Phase 17 tested 108 pre-registered hard, expiry-day, stagnation, trailing and combined stop rules. No rule both preserved all baseline-positive trades and improved validation P&L.

Phase 18 and Phase 19 tested a narrower expiry-day conditional stop. The final **research candidate for paper/forward validation** is:

> **At 13:30 IST on expiry day, exit all three legs when combined strategy MTM is negative and running MFE since entry is below 0.50 × the original target.**

Walk-forward results for this candidate:

| Period | Net uplift | Baseline-positive trades affected | Stops |
|---|---:|---:|---:|
| Training through 2023-12-31 | +₹1,963.67 | 0 | 1 |
| Validation 2024-01-01 to 2025-12-31 | +₹1,923.59 | 0 | 2 |
| Holdout 2026-01-01 to 2026-09-30 | +₹6,305.15 | 0 | 2 |
| Full sample | +₹10,192.41 | 0 | 5 |

The candidate changes five exits, all baseline losing trades, and leaves every historically profitable baseline trade untouched. It does **not** eliminate any loss completely; it truncates selected expiry losses earlier.

The formal train-selected 13:30 / MFE < 1.0× rule was **not promoted** because its 2026 holdout maximum drawdown increased materially. The 0.50× version is retained as the more conservative robustness candidate.

The no-stop dynamic-n strategy remains the locked primary until the stop candidate is tested with forward/paper execution and real broker fills.

## Phase artifacts

- Phase 17 stop-loss research: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-17-stop-loss-research
- Phase 18 conditional-stop refinement: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-18-conditional-stop-refinement
- Phase 19 walk-forward confirmation: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-19-stop-walk-forward-confirmation
- Final stop-loss conclusion: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/STOP_LOSS_CONCLUSION.md
- Stop-loss manuscript supplement: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/manuscript/STOP_LOSS_EXTENSION_SUPPLEMENT.md
- Walk-forward report: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/results/dynamic_n_corrected/phase19_walk_forward/WALK_FORWARD_SUMMARY.md

## Research governance

All previous superseded dynamic-n numerical results remain marked as obsolete. Execution errors and corrections are logged in `ERROR_LOG.md`; research-phase progress is tracked in `RESEARCH_LOG.md`; the research protocol is maintained in `DYNAMIC_N_RESEARCH_PLAN.md`.

**Phase 19 is the final stop-loss research phase under the current plan.**


## Latest completed phase — Phase 20

Phase 20 compared entry-time payoff-chart/green-area boundary stops against the fixed expiry-day conditional stop.

The boundary family tested 0/50/100/200/400 NIFTY-point buffers, 1/3-minute confirmation, and boundary/MTM/MFE variants. The training-safe selector was 400 points with 1-minute confirmation, but it lost **₹14,390.87** in 2024–2025 validation and **₹49,064.48** in the 2026 holdout, while materially worsening drawdown. Therefore **no payoff-boundary stop is included**.

The fixed Phase-19 comparator was independently reconstructed and cross-checked:
- 13:30 IST on expiry day;
- combined three-leg MTM < ₹0;
- running MFE < 0.50× original target.

Walk-forward uplift: +₹1,963.67 training, +₹1,923.59 validation, +₹6,305.15 holdout, +₹10,192.41 full sample, with zero baseline-positive trades affected.

### Final entry-to-exit rules

The final historical rules are recorded on the Phase-20 branch:
- [Final strategy rules](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/FINAL_STRATEGY_RULES.md)
- [Final strategy specification](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/STRATEGY_SPEC.md)
- [Phase 20 supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/manuscript/PHASE20_PAYOFF_BOUNDARY_SUPPLEMENT.md)
- [Phase 20 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/results/dynamic_n_corrected/phase20_payoff_boundary/BOUNDARY_STOP_CONCLUSION.md)

Final historical result over 190 corrected trades:
- Net P&L: **₹149,129.53**
- Mean net/trade: **₹784.89**
- Net winning trades: **179/190 (94.21%)**
- Profit factor: **2.34**
- Maximum cumulative drawdown: **₹27,336.11**
- Target exits: **178**
- Conditional-stop exits: **5**
- Expiry-fallback exits: **7**

This is historical research evidence, not a guarantee of future or live performance. Forward/paper execution validation remains separate from the historical research.

## Phase 21 status — pre-expiry risk-control research

Phase 21 is being evaluated on isolated branch `phase-21-pre-expiry-adverse-move-risk-control`. It tests bounded early exits and one-lot OTM-(n+3) tail-hedge repairs against the frozen Phase-20 strategy. The canonical strategy remains unchanged unless the pre-registered walk-forward promotion screen is passed.
