# Phase 50B-6 — Statistical Inference Final Report

## Executive conclusion

Phase 50B-6 tested the frozen OTM350 geometry against the fixed source-faithful BASE control on the untouched 2024–2025 validation sample.

**Decision: NO PROMOTION.**

The primary paired expiry-level validation difference was:

- Mean OTM350 minus BASE net P&L: **−₹73.88 per expiry**
- Median difference: **−₹141.33**
- 95% deterministic paired-bootstrap CI: **−₹282.26 to +₹149.36**
- One-sided expiry-block sign-flip p-value: **0.7386**
- OTM350 beat BASE on only **10 of 76** validation expiries; BASE was ahead on **66 of 76**.

The result was consistently unfavorable to OTM350 under +50% friction stress, ₹20/order brokerage, and ₹20/order plus +50% stress. No holdout observations were used for selection or inference.

Therefore the far-OTM mutation is rejected as an improvement. The BASE geometry remains the control/canonical TT-03 geometry within this research chain.

## Research question

Does the preregistered OTM350 mutation produce a statistically defensible economic improvement over the fixed BASE TT-03 geometry on untouched validation data after realistic transaction costs?

## Frozen treatment and comparator

Treatment:
- OTM350: +350/+400/+450 CE ratio and -350/-400/-450 PE ratio.

Comparator:
- BASE: +300/+350/+400 CE ratio and -300/-350/-400 PE ratio.

The geometry was frozen in Phase 50B-4 before validation inference. No new strike distance or other strategy parameter was introduced.

## Data and pairing

The validation period was 2024-01-01 through 2025-12-31.

There were **76 common complete expiry/campaign blocks**.

The inferential unit was the expiry/campaign block rather than individual option legs. This preserves the dependence among the multiple legs within each strategy campaign.

The paired datasets had:
- identical expiry membership;
- identical entry timestamps;
- zero direction mismatches;
- 18 exit-timestamp mismatches.

The exit-timestamp differences are legitimate treatment outcomes: the two geometries can reach their exit conditions at different times. They were therefore not treated as data errors.

The protected 2026 HOLD was not used for selection or inference.

## Primary statistical analysis

The primary endpoint was the mean paired expiry-level net P&L difference under the standard cost model.

A deterministic paired bootstrap with **10,000 resamples** generated the confidence interval.

A deterministic expiry-block sign-flip Monte Carlo test with **100,000 resamples** evaluated the directional null.

The randomization unit remained the expiry block.

## Primary result

| Metric | OTM350 − BASE |
|---|---:|
| Validation expiries | 76 |
| Mean difference | **−₹73.88** |
| Median difference | **−₹141.33** |
| 95% bootstrap CI | **−₹282.26 to +₹149.36** |
| One-sided sign-flip p | **0.7386** |
| Expiries OTM350 > BASE | 10 / 76 |
| Expiries OTM350 < BASE | 66 / 76 |
| Probability OTM350 beats BASE | 13.16% |

The primary confidence interval includes zero and the directional p-value is far from the preregistered significance threshold. The point estimate itself favors BASE.

## Cost-stress robustness

| Endpoint | Mean difference | 95% bootstrap CI | One-sided p | Holm-adjusted p |
|---|---:|---:|---:|---:|
| Standard | −₹73.88 | −₹282.26 to +₹149.36 | 0.7386 | — |
| +50% friction stress | −₹73.03 | −₹283.40 to +₹152.07 | 0.7375 | 1.0000 |
| ₹20/order | −₹73.88 | −₹285.34 to +₹147.84 | 0.7409 | 1.0000 |
| ₹20/order +50% stress | −₹73.03 | −₹288.00 to +₹150.73 | 0.7381 | 1.0000 |

The economic ordering is stable across all registered cost scenarios. There is no hidden cost model under which the selected geometry becomes statistically supported.

## Chronological diagnostics

The unfavorable point estimate was present in both validation years:

| Period | Mean standard-cost difference | OTM350 wins |
|---|---:|---:|
| 2024 | −₹73.28 | 6 / 45 |
| 2025 | −₹74.74 | 4 / 31 |

The validation sample contained 76 CALL-ratio campaigns and no PUT-ratio campaigns. Therefore a separate PUT-ratio inference is not estimable from this validation window. This is a limitation, not evidence about PUT-ratio performance.

## Relation to Phase 50B-4 selection

Phase 50B-4 correctly selected OTM350 within the two preregistered mutations because OTM350 had the larger DEV +50% stress net.

That development selection did **not** imply superiority to BASE.

Phase 50B-6 supplied the protected control-relative test. It found no validation uplift and instead produced a negative point estimate.

This separation prevents a common research error: confusing “best among tested mutations” with “better than the established control.”

## Statistical interpretation

There is no evidence that OTM350 improves the TT-03 strategy relative to BASE.

The result is not merely a failure to reach statistical significance: the observed mean and median differences both favor BASE, and BASE wins on 66 of 76 validation expiry blocks.

The cost-stress results are almost unchanged, showing that the difference is not an artifact of the chosen brokerage assumption.

No holdout result was used to rescue, select, or reject the mutation.

## Strengths

- Treatment was frozen before validation inference.
- The comparator was a fixed source-faithful control.
- Expiry-block pairing preserved within-campaign dependence.
- 10,000 deterministic bootstrap resamples were used for the confidence interval.
- 100,000 deterministic sign-flip resamples were used for the directional test.
- Secondary cost endpoints were multiplicity-adjusted with Holm correction.
- ₹10/order, +50% stress, ₹20/order, and ₹20/order +50% scenarios were evaluated.
- 2026 HOLD remained protected.
- No geometry or trading-rule tuning occurred after seeing validation results.

## Limitations

1. The validation sample contains 76 expiry blocks.
2. The 2026 HOLD sample remains outside this inference and was not used to increase apparent statistical power.
3. The validation period contains no PUT-ratio campaigns, preventing meaningful directional inference for that subgroup.
4. The analysis evaluates historical source-faithful execution assumptions rather than live broker fills.
5. The test addresses the registered OTM350 mutation only; it does not prove that every conceivable alternative geometry is inferior.
6. The bootstrap confidence interval quantifies sampling uncertainty under the expiry-block resampling scheme and is not a guarantee about future market behavior.

## Reproducibility

Accepted statistical workflow:

**Actions run 37851668489**

The workflow:
- downloaded the frozen OTM350 Phase-50B-4 artifact;
- verified the BASE/OTM350 campaign pairing;
- executed the preregistered inference engine;
- passed the audit;
- uploaded the inference artifact;
- successfully published the inference results to the branch.

Primary output files:
- decision.json
- statistical_endpoints.csv
- validation_paired_expiry.csv
- subgroup_descriptives.csv
- pairing_identity_diagnostics.csv
- cumulative_paired_difference.csv

## Phase disposition

**CLOSED — NO PROMOTION**

OTM350 is rejected as an improvement over BASE.

No additional far-OTM distance search should be opened from this result.

The fixed BASE geometry remains the appropriate TT-03 control/canonical geometry for the current research chain.

## Conclusion

The preregistered hypothesis that OTM350 would improve TT-03 economics over BASE is not supported by the untouched 2024–2025 validation sample.

The estimated effect is negative, the confidence interval crosses zero, the one-sided p-value is 0.7386, and BASE outperforms OTM350 on 66 of 76 validation expiries.

**Final research conclusion: retain BASE; do not promote OTM350.**

## Future research

Future work should not simply search more strike distances. The more scientifically useful directions are:

1. resolve the outstanding Phase-51 endpoint data gap and perform the separately preregistered full-window OOS validation;
2. obtain broker-specific fill/latency evidence and test whether historical theoretical fills survive realistic execution;
3. investigate whether the economic difference is concentrated in particular market regimes only under a separately preregistered hypothesis;
4. maintain the 2026 HOLD as a genuinely untouched confirmation sample;
5. integrate the completed evidence into the final research manuscript rather than reopening rejected geometry search without a new preregistration.
