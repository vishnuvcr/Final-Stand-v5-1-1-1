# Phase 82 — Expiry-cluster inference

**Decision: no candidate passes predeclared gate. No strategy is promoted.**

- Paired rows: 11,163; registered primary tests: 20 (10 variants × DEV/VAL).
- Unique expiry clusters: 238; invalid numeric pairs dropped: 0.
- Primary inference: one-tick overnight-minus-intraday effect, expiry-cluster robust t test plus 10,000 cluster-bootstrap replicates.
- Multiplicity: Holm correction across all 20 primary tests; two-tick stress is robustness only.
- Defined-risk variants passing the frozen profitability gate: 0 of 18.
- The 2026 holdout was not loaded, scored, or ranked because candidate eligibility is the prerequisite.

## Inference results

| Split | Variant | N pairs | Expiry clusters | Mean difference (₹/pair) | Cluster-bootstrap 95% CI | Raw p | Holm p (20 tests) | Two-tick mean (₹/pair) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| development | short_atm_straddle | 635 | 135 | -259.92 | [-431.12, -78.87] | 0.00404 | 0.08074 | -259.92 |
| development | bear_call_credit_100_300 | 636 | 135 | -38.82 | [-134.04, 55.89] | 0.42724 | 1.00000 | -38.82 |
| development | bull_put_credit_100_300 | 636 | 135 | -5.07 | [-93.61, 84.92] | 0.91157 | 1.00000 | -5.07 |
| development | long_iron_fly_w100 | 635 | 135 | 8.98 | [-6.08, 24.36] | 0.24961 | 1.00000 | 8.98 |
| development | long_iron_fly_w200 | 635 | 135 | 26.67 | [-14.02, 66.23] | 0.19765 | 1.00000 | 26.67 |
| development | long_iron_fly_w300 | 635 | 135 | 52.66 | [-12.70, 117.44] | 0.12073 | 1.00000 | 52.66 |
| development | short_iron_condor_100_300 | 636 | 135 | -43.89 | [-98.36, 10.83] | 0.11347 | 1.00000 | -43.89 |
| development | short_iron_fly_w100 | 635 | 135 | -8.52 | [-23.99, 7.15] | 0.27579 | 1.00000 | -8.52 |
| development | short_iron_fly_w200 | 635 | 135 | -26.20 | [-66.40, 13.86] | 0.20597 | 1.00000 | -26.20 |
| development | short_iron_fly_w300 | 635 | 135 | -52.18 | [-115.95, 14.58] | 0.12424 | 1.00000 | -52.18 |
| validation | bear_call_credit_100_300 | 481 | 104 | -17.48 | [-147.77, 111.67] | 0.79021 | 1.00000 | -17.48 |
| validation | bull_put_credit_100_300 | 481 | 104 | -25.77 | [-162.95, 111.57] | 0.71093 | 1.00000 | -25.77 |
| validation | long_iron_fly_w100 | 480 | 104 | 15.33 | [-3.30, 34.88] | 0.11866 | 1.00000 | 15.33 |
| validation | long_iron_fly_w200 | 482 | 104 | 45.25 | [-8.55, 99.26] | 0.10911 | 1.00000 | 45.25 |
| validation | long_iron_fly_w300 | 481 | 104 | 64.56 | [-32.87, 159.43] | 0.19533 | 1.00000 | 64.56 |
| validation | short_atm_straddle | 482 | 104 | -331.66 | [-771.92, 74.22] | 0.12659 | 1.00000 | -331.66 |
| validation | short_iron_condor_100_300 | 480 | 104 | -47.89 | [-131.92, 32.80] | 0.26376 | 1.00000 | -47.89 |
| validation | short_iron_fly_w100 | 480 | 104 | -14.46 | [-33.36, 4.24] | 0.13373 | 1.00000 | -14.46 |
| validation | short_iron_fly_w200 | 482 | 104 | -44.46 | [-99.60, 10.47] | 0.11508 | 1.00000 | -44.46 |
| validation | short_iron_fly_w300 | 481 | 104 | -63.79 | [-160.27, 32.61] | 0.20031 | 1.00000 | -63.79 |

## Candidate gate

| Defined-risk variant / window | Passes profitability gate |
|---|---|
| bear_call_credit_100_300 / intraday | NO |
| bear_call_credit_100_300 / overnight | NO |
| bull_put_credit_100_300 / intraday | NO |
| bull_put_credit_100_300 / overnight | NO |
| long_iron_fly_w100 / intraday | NO |
| long_iron_fly_w100 / overnight | NO |
| long_iron_fly_w200 / intraday | NO |
| long_iron_fly_w200 / overnight | NO |
| long_iron_fly_w300 / intraday | NO |
| long_iron_fly_w300 / overnight | NO |
| short_iron_condor_100_300 / intraday | NO |
| short_iron_condor_100_300 / overnight | NO |
| short_iron_fly_w100 / intraday | NO |
| short_iron_fly_w100 / overnight | NO |
| short_iron_fly_w200 / intraday | NO |
| short_iron_fly_w200 / overnight | NO |
| short_iron_fly_w300 / intraday | NO |
| short_iron_fly_w300 / overnight | NO |

## Interpretation boundary

The estimated difference describes whether overnight net P&L differs from intraday net P&L in the registered historical OHLC-open proxy. It does not by itself identify a profitable strategy. Candidate eligibility separately requires positive net results in DEV and VAL, across both windows and both friction levels. Even positive results would need execution-grade quote/fill evidence.

## Files

- cluster_inference.csv: 20 primary tests and two-tick sensitivity.
- candidate_gate.csv: frozen defined-risk profitability gate.
- summary.json: machine-readable methods, coverage, decision and limitations.
