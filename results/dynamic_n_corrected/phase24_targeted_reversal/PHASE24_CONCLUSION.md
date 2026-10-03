# Phase 24 Conclusion — Targeted Reversal Trigger

## Research question

Can a narrow entry-only reversal rule improve the frozen Phase-20 dynamic-n strategy by acting only when both canonical loss-risk and reverse-superiority are simultaneously high?

## Preregistered design

Two fixed families were tested:
- Family A: loss-probability threshold plus reverse-superiority threshold.
- Family B: Family A plus a fixed reverse-minus-loss probability margin.

Selection was based only on the 2021–2023 training period. The candidate grid, model family, and promotion gate were fixed before observing Phase-24 results.

## Results

No candidate satisfied the training safety gate.

The least-ineligible diagnostic candidate was:
- Family B;
- loss probability >= 0.85;
- reverse probability >= 0.85;
- margin >= -0.10.

Training performance:
- canonical net P&L: ₹63,931.74;
- policy net P&L: ₹89,134.08;
- uplift: +₹25,202.33;
- 2 canonical losses reversed;
- 2 profitable trades reversed;
- 100% winner retention;
- 7.18% of baseline-positive training P&L sacrificed.

Because the last quantity exceeded the preregistered 5% ceiling, the rule was not training-eligible.

Validation:
- uplift: ₹0;
- losses reversed: 0;
- winner retention: 100%.

2026 holdout:
- uplift: ₹0;
- losses reversed: 0;
- winner retention: 100%.

The OOS bootstrap uplift confidence intervals were degenerate at ₹0 because the selected diagnostic rule took no reversal actions in either OOS period.

## Decision

No Phase-24 reversal trigger is promoted.

The reversal hypothesis is therefore exhausted under the registered feature set, model class, threshold grid, execution-cost model, and train/validation/holdout design.

The complete strategy remains the Phase-20 canonical dynamic-n specification in FINAL_STRATEGY_RULES.md.

## Research implication

The research produced a useful but strictly retrospective finding: the 11 historical canonical losing trades all had profitable opposite-side reconstructions. Phase 23–24 did not find a point-in-time rule capable of exploiting that asymmetry without risking unacceptable profitable-trade sacrifice or failing OOS.

No further reversal-specific phase should be opened without a materially new data source or research question.