# Phase 17 Stop-Loss Research

## Baseline

The locked dynamic-n primary remains the no-stop strategy. This phase tests stop-loss extensions only.

## Candidate families

- Hard MTM stop after 0/24/48/72 elapsed hours at 0.50x to 2.00x target.
- Expiry-day negative-P&L cutoffs at 14:00, 14:30 and 15:00 IST.
- Stagnation stops after 24/48/72 hours.
- MFE-based trailing stops.
- Hard-stop plus expiry-day cutoff combinations.

Hard, expiry-day and stagnation families use 1-minute and 3-minute confirmation variants where applicable.

## Temporal split

- Development: through 2024-12-31.
- Validation: 2025-01-01 through 2026-09-30.

## Selection rule

Development-only selection:
1. zero baseline-positive trades affected;
2. maximize development net-P&L uplift;
3. maximize development loss reduction;
4. minimize affected winners as final tie-break.

Selected rule: **expiry_negative_cut_1400_c1**

### Development

- Net uplift: ₹7,712.75
- Loss reduction: ₹7,789.00
- Losses eliminated: 0
- Baseline-positive trades affected: 0

### Validation

- Net uplift: ₹-8,843.47
- Loss reduction: ₹11,872.98
- Losses eliminated: 0
- Baseline-positive trades affected: 0

### Full reconstructed sample

- Net uplift: ₹-1,130.72
- Loss reduction: ₹19,661.98
- Losses eliminated: 0
- Baseline-positive trades affected: 0

## Interpretation guard

The rule is not eligible for promotion to an operational stop unless:
- validation has zero baseline-positive trades affected;
- validation net-P&L uplift is positive;
- the reduction is not driven by a single anomalous trade;
- exact stop-time fees are included (they are);
- the rule remains plausible under nearby parameter changes.

