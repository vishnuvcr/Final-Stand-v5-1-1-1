# Phase 50B-6 Research Plan — Dependence-Aware Statistical Inference

## Purpose

Test the frozen Phase-50B-4 mutation OTM350 against the fixed source-faithful BASE control without reopening geometry selection and without using the protected 2026 HOLD for selection.

## Research questions

1. Does OTM350 produce a positive paired economic uplift versus BASE on the untouched 2024–2025 validation sample?
2. Does the conclusion survive +50% transaction-cost stress and the ₹20/order brokerage scenario?
3. Is any observed uplift robust at the expiry/campaign level rather than being driven by a small number of individual trades?
4. Does the result remain consistent across calendar years and CALL/PUT structural directions?
5. Does the frozen candidate improve risk-adjusted outcomes or merely change the distribution of returns?

## Frozen hypothesis

Primary null hypothesis: the mean paired validation-period net P&L difference (OTM350 minus BASE) is not greater than zero.

Primary alternative: the mean paired validation-period net P&L difference is greater than zero.

The primary endpoint is the validation-period paired expiry-level net P&L difference under the preregistered standard cost model. The +50% stress and ₹20/order variants are secondary robustness endpoints.

## Data

- Frozen Phase-50B-4 OTM350 replay artifact.
- Frozen Phase-50B-4 BASE control artifact.
- Same 201 candidate campaigns and 200 complete trades for both geometries.
- One shared coverage gap and one shared session exclusion.
- Development: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- 2026 HOLD: descriptive only and excluded from selection/inference.

No new market-data acquisition is required unless an integrity check fails.

## Unit of analysis

The primary inferential unit is the expiry/campaign block, not an individual option leg or order. This preserves dependence among the multiple option legs and repeated observations within a campaign.

The paired comparison is formed by matching the same expiry/campaign across BASE and OTM350.

## Statistical methodology

1. Verify exact common campaign membership and timestamp/geometry integrity.
2. Compute paired expiry-level differences under each cost model.
3. Primary test: paired, dependence-aware bootstrap of the mean validation expiry-level difference with at least 10,000 deterministic resamples.
4. Complementary exact/randomization sign-flip test at the expiry-block level where assumptions permit.
5. Report two-sided 95% confidence intervals for effect size even though the preregistered directional hypothesis is one-sided.
6. Report one-sided p-values for the primary hypothesis.
7. Apply multiplicity control across the preregistered secondary economic endpoints using Holm correction.
8. Report effect size, median paired difference, probability that OTM350 beats BASE on a validation expiry, and bootstrap distribution diagnostics.
9. Repeat descriptively by 2024 and 2025 and by CALL-ratio versus PUT-ratio direction.
10. Compute paired maximum drawdown, cumulative net P&L, profit factor, mean/median trade, loss-tail statistics and return-to-drawdown diagnostics.
11. Repeat all economic comparisons under +50% friction stress and ₹20/order brokerage.
12. Do not inspect or use 2026 HOLD to choose any model, geometry, endpoint, threshold or conclusion.

## Promotion gate

OTM350 can only advance if the preregistered primary validation inference is favorable and the economic result remains robust under the registered cost-stress checks. A positive point estimate alone is insufficient.

A statistically favorable result that disappears under realistic cost stress is not a promotion.

If the primary inference is non-significant, contradictory across cost models, or economically inferior to BASE, the mutation is rejected and BASE remains the control.

## Outputs

- paired validation dataset;
- bootstrap distribution and confidence intervals;
- randomization/sign-flip results;
- multiplicity-adjusted endpoint table;
- yearly and direction subgroup diagnostics;
- cost-stress comparison;
- equity curves;
- drawdown curves;
- statistical decision JSON;
- final Phase-50B-6 manuscript section;
- error log and complete action log.

## Reproducibility

All computations must be deterministic, versioned, and run through GitHub Actions. No hidden parameter tuning is permitted after seeing the validation results.
