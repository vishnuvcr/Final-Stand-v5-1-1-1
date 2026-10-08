# Phase 50B-4 — Far-OTM Geometry Final Report

## Executive conclusion

Phase 50B-4 completed the preregistered TT-03 far-OTM geometry comparison.

The frozen universe was BASE, OTM350 and OTM400. Both mutations passed the feasibility and development gates. Under the preregistered development rule, OTM350 is the frozen mutation candidate because its DEV +50% cost-stress net (₹32,213.01) exceeded OTM400 (₹14,511.75).

This is not a claim that OTM350 is superior to BASE. BASE remained materially stronger on DEV, validation, 2026 HOLD, and aggregate cost-stress results. OTM350 is therefore frozen only as the mutation selected by the preregistered within-mutation gate and is handed to Phase 50B-6 for dependence-aware statistical comparison against the fixed BASE control.

## Research question

Does moving the symmetric TT-03 strike-distance geometry farther OTM improve development-period net performance after realistic execution costs while preserving at least 95% complete mandatory-exit coverage?

## Preregistered methodology

Only the strike-distance tuple changed. All other TT-03 semantics remained frozen: complete 10:00–10:05 entry window; call-ratio priority with put-ratio fallback; expiry-day negative-MTM conditional exit; hard close no later than 15:29; explicit coverage and session exclusions; historical lot sizes; no forward filling or synthetic quote repair; ₹10 and ₹20 brokerage scenarios; statutory charges; and +50% cost stress.

No new distance, DTE, entry time, stop, exit, VIX threshold, or other parameter was introduced.

Development selection was made using only DEV results, before interpreting validation/HOLD for selection.

## Coverage and data quality

| Geometry | Trades | Candidate campaigns | Coverage | Data errors | Session exclusions |
|---|---:|---:|---:|---:|---:|
| BASE | 200 | 201 | 99.50% | 0 | 1 |
| OTM350 | 200 | 201 | 99.50% | 0 | 1 |
| OTM400 | 200 | 201 | 99.50% | 0 | 1 |

The single coverage gap for both mutations was the 2022-03-10 campaign, where the scheduled 10:00–10:05 entry window had no entry observation. The shared session exclusion was the 2022-10-27 expiry campaign because its scheduled entry day, 2022-10-24, had no normal 09:15–15:30 session. Neither condition was repaired or silently dropped.

## Development selection

| Geometry | DEV trades | DEV net | DEV +50% stress |
|---|---:|---:|---:|
| BASE control | 121 | ₹50,041.37 | ₹45,548.93 |
| OTM350 | 121 | ₹36,634.92 | ₹32,213.01 |
| OTM400 | 121 | ₹18,891.16 | ₹14,511.75 |

Both mutations passed >=95% coverage, positive DEV net, and positive DEV +50% stress net. Therefore the preregistered selection rule selects OTM350.

## Chronological results

| Geometry | Split | Trades | Net | +50% stress | Win rate |
|---|---|---:|---:|---:|---:|
| BASE | DEV | 121 | ₹50,041.37 | ₹45,548.93 | 67.77% |
| BASE | VAL | 76 | ₹33,426.00 | ₹30,446.50 | 84.21% |
| BASE | 2026 HOLD | 3 | ₹6,201.79 | ₹6,078.68 | 100.00% |
| OTM350 | DEV | 121 | ₹36,634.92 | ₹32,213.01 | 66.94% |
| OTM350 | VAL | 76 | ₹27,811.50 | ₹24,895.99 | 84.21% |
| OTM350 | 2026 HOLD | 3 | ₹5,105.64 | ₹4,985.33 | 100.00% |
| OTM400 | DEV | 121 | ₹18,891.16 | ₹14,511.75 | 62.81% |
| OTM400 | VAL | 76 | ₹25,842.14 | ₹22,977.59 | 84.21% |
| OTM400 | 2026 HOLD | 3 | ₹4,265.28 | ₹4,147.29 | 100.00% |

Validation and HOLD are descriptive because the geometry decision was already frozen.

## Aggregate cost sensitivity

| Geometry | ₹10/order | ₹10/order +50% stress | ₹20/order | ₹20/order +50% stress |
|---|---:|---:|---:|---:|
| BASE | ₹89,669.15 | ₹82,074.11 | ₹75,509.15 | ₹60,834.11 |
| OTM350 | ₹69,552.06 | ₹62,094.34 | ₹55,392.06 | ₹40,854.34 |
| OTM400 | ₹48,998.58 | ₹41,636.62 | ₹34,838.58 | ₹20,396.62 |

All three geometries remained positive under the ₹20/order +50% stress scenario, but BASE remained the strongest control.

## Interpretation

The far-OTM mutation does not provide evidence of aggregate improvement over the source-faithful BASE geometry. Increasing the distance from BASE to OTM350 reduced aggregate net P&L, and OTM400 reduced it further.

The important scientific result is therefore not a promotion claim. OTM350 won the within-mutation development selection because it retained materially more development profit than OTM400, while BASE remained stronger overall.

## VIX descriptive context

No VIX state was used to select geometry in Phase 50B-4. For OTM350, aggregate net was ₹8,100.05 in HIGH, ₹9,019.77 in LOW, and ₹52,432.24 in NORMAL before cost-stress adjustment. These figures are descriptive only.

## Statistical analysis

No inferential p-value, confidence interval, bootstrap selection, or multiplicity-adjusted claim was made in Phase 50B-4. This was intentional. Geometry selection was frozen using the preregistered DEV rule. Phase 50B-6 will compare frozen OTM350 against fixed BASE using the registered dependence-aware framework and will keep 2026 HOLD protected from selection.

## Strengths

- Preregistered finite geometry universe.
- Source-faithful replay with only strike distance changed.
- Chronological DEV/VAL/HOLD separation.
- Complete mandatory-exit coverage above the 95% threshold.
- Zero unexplained data errors.
- Explicit coverage and session exclusions.
- ₹10 and ₹20 brokerage scenarios plus +50% friction stress.
- No synthetic prices, forward filling, or holdout-based selection.
- Raw workflow artifacts retained for both OTM mutations.

## Limitations

- The 2026 HOLD sample contains only three completed campaigns and is descriptive.
- Candidates are mutations of an existing TT-03 structure, not independently discovered strategies.
- The preregistered selection rule optimizes within OTM350/OTM400 and does not require a mutation to beat BASE.
- Results remain conditional on the audited source data and execution model.
- Statistical significance cannot be inferred from these descriptive results.

## Reproducibility artifacts

Numerical replays were executed in GitHub Actions run 37850091712 with engine revision 50B-TT03-OTM-DIST-V1.

OTM350 artifact ID 11580799729; SHA-256 cc492e9db61acea388c20b9f9340cdc492233643c73c2ddf4a40b2d95f9d3846.

OTM400 artifact ID 11581129072; SHA-256 1a5ec8c9b974049308b090bc9f980261c91c6c98e1eac0ff65e67f9e4b107c6a.

The branch contains the frozen development-selection JSON and geometry split comparison.

## Phase disposition

**CLOSED — PASS / FROZEN CANDIDATE**

- Selected mutation for statistical gate: OTM350.
- Fixed comparator: BASE.
- No additional strike distance is permitted.
- No VIX, DTE, entry-time, stop, exit, or hedge tuning is permitted in this phase.
- Next planned phase: Phase 50B-6 statistical inference.

## Conclusion

Within the preregistered far-OTM mutation family, OTM350 is the strongest candidate and is therefore frozen for formal statistical comparison. However, BASE remains economically superior in the observed sample. The defensible conclusion is candidate selected, not strategy promoted.
