# Phase 21 Supplement — Pre-Expiry Adverse-Move Risk Control

## Abstract

The frozen Phase-20 NIFTY weekly-option strategy has a known tail-loss exposure because its three-leg structure contains two short options against one long option. Phase 21 tested whether a large adverse NIFTY move before expiry could be managed with a deterministic early exit or with a one-lot farther-OTM protective option. The test was pre-registered and evaluated on the corrected 190-trade minute-level dataset using the Phase-20 comparator, exact strike mapping, historical lot sizes, modeled slippage, brokerage and audited statutory charges.

No candidate passed the required training safety condition of zero baseline-positive trades affected. The closest candidate—an adverse 600-point move with one-minute confirmation and a spot-only early exit—improved training P&L by ₹1,885.47 but produced −₹33,923.36 uplift in 2024–2025 validation and −₹44,039.53 uplift in the 2026 holdout. Full-sample maximum drawdown increased from ₹27,336.11 to ₹52,740.01. The closest OTM-(n+3) hedge produced the same qualitative failure. Therefore no pre-expiry adverse-move adjustment is promoted.

## Research question

Can a large adverse NIFTY move before expiry be converted into a reliable risk-control signal that materially reduces tail losses without damaging profitable trades?

## Aims

1. Test whether direction-aware NIFTY displacement from the 10:00 entry spot predicts an unacceptable deterioration in the existing three-leg position.
2. Compare an early-exit response with a farther-OTM tail-hedge response.
3. Require temporal out-of-sample evidence before changing the frozen strategy.

## Hypotheses

H1: A sufficiently large adverse move should identify a subset of tail-loss trades early enough to improve realized P&L.

H2: Adding one OTM-(n+3) option after the adverse move should reduce the far-tail loss without requiring the original position to be closed immediately.

H3: A valid operational rule should not systematically sacrifice trades that would have reached the frozen target or otherwise finished profitably under the Phase-20 comparator.

## Methodology

### Comparator

The frozen strategy exits by target first, then by the 13:30 IST expiry-day condition (combined MTM < 0 and running MFE < 0.50× target), and finally by the 15:29 IST expiry fallback.

### Adverse-move definition

For the BEARISH call structure:

$$A_t=S_t-S_0$$

For the BULLISH put structure:

$$A_t=S_0-S_t$$

where $S_0$ is the NIFTY spot at 10:00 IST on entry.

### Candidate grid

Thresholds: 200, 300, 400, 500, 600 points.

Confirmation: 1, 5, 15 consecutive complete minutes.

Signal filters:
- spot-only;
- spot plus combined MTM < 0;
- spot plus MTM < 0 plus MFE < 0.50× target.

Actions:
- close all three original legs;
- buy one OTM-(n+3) option on the adverse side.

Hedge exits:
- continue until original target or frozen comparator exit;
- or continue until repaired gross P&L reaches zero or frozen comparator exit.

### Costs and data

The same corrected research engine was used as the final Phase-20 strategy:
- exact NIFTY ₹50 strike ladder;
- no ordinal strike substitution or forward filling;
- one adverse ₹0.05 option tick per leg;
- historical NIFTY lot sizes;
- ₹10 brokerage per executed F&O order;
- audited date-aware statutory and transaction charges;
- exact common-minute NIFTY/option observations.

### Temporal validation

Training/selection: through 2023-12-31.

Validation: 2024-01-01 through 2025-12-31.

Holdout: 2026-01-01 through 2026-09-30.

No candidate was promoted from validation or holdout performance.

## Statistical analysis

The primary selection constraint was structural rather than purely statistical: zero profitable comparator trades could be affected in training.

For each candidate, the research records:
- net P&L uplift;
- maximum drawdown;
- number of adjustments;
- profitable baseline trades affected;
- loss reduction;
- losses eliminated;
- worst trade;
- fifth-percentile trade P&L;
- hedge execution gaps.

The closest training candidate was then examined across validation and holdout as a fixed, unreoptimised rule.

## Results

### Baseline

The frozen Phase-20 comparator has:
- 190 trades;
- net P&L ₹149,129.53;
- maximum drawdown ₹27,336.11.

### Training safety screen

No candidate satisfied the requirement of zero baseline-positive trades affected.

The closest candidates all arose at the 600-point threshold. The best unconstrained training candidate was:

**600 points / 1-minute confirmation / spot-only early exit**

Training uplift: +₹1,885.47.

Training profitable trades affected: 1.

Training loss reduction: ₹13,590.83.

### Out-of-sample result for the closest candidate

2024–2025 validation uplift: −₹33,923.36.

2026 holdout uplift: −₹44,039.53.

Full-sample uplift: −₹76,077.42.

Full-sample candidate net P&L: ₹73,052.11.

Full-sample maximum drawdown: ₹52,740.01.

The closest OTM-(n+3) hedge candidate had:
- training uplift +₹1,078.84;
- validation uplift −₹32,168.32;
- 2026 holdout uplift −₹44,400.51;
- full-sample uplift −₹75,490.31;
- full-sample maximum drawdown ₹52,924.61.

## Interpretation

The pre-expiry NIFTY-point trigger contains useful information about some tail losses, but that information is not stable enough to form a robust trading rule under the required safety constraint.

The important empirical result is not simply that a hard stop loses money. The stronger observation is that large adverse moves can occur in trades that later recover. A signal that reacts too early therefore sacrifices the strategy's original positive-expectancy mechanism.

The one-lot farther-OTM hedge also did not solve the problem. The additional option reduces the asymptotic tail slope, but the hedge is purchased after an adverse move, so the new premium and execution cost occur precisely when protection is more expensive and the original position has already deteriorated.

## Relation to existing literature

Ratio spreads are structurally exposed because they contain more short options than long options; standard descriptions of call and put ratio spreads identify a substantial or unlimited adverse-direction risk. citeturn179563search0

Theoretical and empirical hedging literature also emphasizes that dynamic hedging is a trade-off among diffusion risk, jump risk and transaction costs rather than a free reduction in tail risk. Forsyth and Vetzal explicitly model jump risk and transaction costs in dynamic hedging, while Clewlow and Hodges study optimal delta hedging under transaction costs. citeturn179563search3turn179563search5

Research on NIFTY option hedging likewise describes delta-based neutralisation as requiring rebalancing as deltas change. citeturn179563search4

These findings are consistent with Phase 21: a fixed NIFTY-point trigger is simpler than a dynamic hedge, but simplicity does not make the trigger stable. A future hedge phase should therefore be based on option sensitivities, volatility regime and transaction costs rather than only spot displacement.

## Strengths

The phase used the corrected 190-trade strategy ledger, exact minute observations, walk-forward temporal separation and the same modeled execution costs as the frozen strategy. Both an exit mechanism and a repair mechanism were tested under a pre-registered threshold family.

## Limitations

The sample contains only 190 executable trades, so tail-event inference remains statistically limited. The hedge test was intentionally narrow: one additional OTM-(n+3) option, one trigger, and fixed post-trigger exit policies. It did not test continuous delta hedging, gamma-aware hedging, volatility-state filters, or multi-step rebalancing.

Minute data also cannot reproduce live bid/ask depth, partial fills, latency, or overnight/event gaps between observations.

## Conclusion

**No pre-expiry stop-loss or OTM-(n+3) repair from the pre-registered Phase 21 family is supported for promotion.**

The final historical specification remains:

**10:00 entry → 90% target → 13:30 expiry-day MTM/MFE condition → 15:29 fallback.**

The research therefore answers the user's risk-control question with a negative result for fixed 200–600 point pre-expiry triggers: they do not provide a robust way to convert adverse trades into profit or to drastically reduce losses without damaging the strategy.

## Future research

A separately registered Phase 22 could test a genuinely dynamic repair architecture:
- delta-band triggers based on the full three-leg position;
- volatility-regime conditioning;
- jump/event filters;
- one-step versus multi-step farther-OTM hedges;
- hedge quantity chosen from target portfolio delta rather than a fixed one-lot rule;
- transaction-cost-aware no-trade bands.

Such a phase should again use train/validation/holdout separation and should not be promoted unless the hedge improves out-of-sample tail-risk measures without giving back a substantial fraction of profitable trades.

## Reproducibility appendix

Primary artifacts:
- `PHASE21_PRE_REGISTRATION.md`
- `results/dynamic_n_corrected/phase21_adverse_move_risk_control/phase21_full_grid.csv`
- `results/dynamic_n_corrected/phase21_adverse_move_risk_control/phase21_training_selection_grid.csv`
- `results/dynamic_n_corrected/phase21_adverse_move_risk_control/top20_unconstrained_training_diagnostic.csv`
- `results/dynamic_n_corrected/phase21_adverse_move_risk_control/family_selected_summary.csv`
- `results/dynamic_n_corrected/phase21_adverse_move_risk_control/PHASE21_CONCLUSION.md`

