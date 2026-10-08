# Phase 50B-6 Status — Statistical Inference

**ACTIVE — preregistered inference**

Branch: `phase-50b-statistical-inference`

## Gate entry
Phase 50B-5 run **37828322922** passed all numerical, artifact, chronology and publication gates. The fixed universe is:
- TT-03 source-faithful
- TT-03 OTM350 frozen far-OTM variant
- TT-04 source-faithful
- TT-05 source-faithful

TT-06 and TT-07 remain terminal FAIL_COVERAGE and are excluded from all confirmatory inference.

## Frozen statistical protocol
- Inference population: DEV + VAL, 2021–2025 only.
- 2026 HOLD is protected and descriptive only.
- Four registered cost models: net, net50, net20, net20_50.
- 16 fixed strategy × cost hypotheses.
- Primary null: expected trade-level net P&L <= 0; alternative > 0.
- Primary p-value: 10,000 sign-randomization permutations with fixed trade magnitudes.
- Dependence robustness: 10,000 expiry-day block-bootstrap replicates and 95% percentile confidence interval for mean P&L.
- Secondary sign test: one-sided binomial test.
- Holm correction across all 16 primary hypotheses.
- No strategy/parameter/VIX/strike tuning is permitted.
- No capital-normalized return claim is permitted.

## Promotion statistical gate
A strategy-cost hypothesis is statistically positive only if:
1. mean P&L > 0;
2. 95% expiry-block bootstrap lower bound > 0; and
3. Holm-adjusted permutation p < 0.05.

A strategy is **robust across registered costs** only if all four cost models pass this gate. This is an inference gate, not a license to reopen optimization.

## Reproducibility
- RNG seed: 5062026
- Bootstrap: 10,000
- Permutations: 10,000
- Inputs are the published Phase 50B-5 trade artifacts.

## Next step
After this finite inference run is audited, advance exactly once to Phase 50B-7 final manuscript/figures/tables/appendices/final decision.


## 2026-10-09 — Controlled correction after run 37831453896
Run 37831453896 failed before statistical output because the block-bootstrap routine accidentally included expiry timestamps in the numeric sample (F50B-097). No inference result was accepted. The correction isolates the P&L vector while preserving expiry-day block membership; all preregistered hypotheses, cost models, seed, replicate counts, Holm family and protected holdout remain unchanged. A clean rerun is required.


## 2026-10-09 — Phase 50B-6 inference PASS, no robust promotion
Corrected run **37832396945** passed inference, audit and publication. Across 16 fixed strategy×cost hypotheses, Holm-adjusted primary inference identified positive evidence for TT-03 at net/net50/net20 and for TT-03 OTM350 at net/net50/net20. Neither strategy passed the registered net20_50 robustness gate. TT-04 and TT-05 had no primary-positive hypothesis after the bootstrap + Holm criteria. Therefore **no strategy is robust across all registered cost models and none is promoted**. The 2026 HOLD remained protected and was only reported descriptively.

Key DEV+VAL results:
- TT-03 mean P&L/trade: ₹423.69 net; ₹385.76 net50; ₹352.89 net20; ₹279.56 net20_50. The net20_50 Holm-adjusted p=0.08099 and bootstrap lower CI=₹36.65, so the strict statistical gate fails on multiplicity despite a positive bootstrap lower bound.
- TT-03 OTM350: ₹327.14; ₹289.89; ₹256.34; ₹183.69 respectively. net20_50 Holm-adjusted p=0.15928, so the strict gate fails.
- TT-04 and TT-05 have bootstrap CIs crossing zero at every cost model and no Holm-rejected primary hypothesis.

### Decision
**NO PROMOTION.** The finite Phase 50B research now advances exactly once to 50B-7 final manuscript/figures/tables/appendices/final decision. No further tuning is permitted inside this phase.
