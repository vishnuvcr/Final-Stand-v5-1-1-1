# Phase 54 status — OHLC-reference eligibility sensitivity

**Overall:** ACTIVE — non-executable coverage sensitivity only.

- **Branch:** phase-54-ohcl-reference-sensitivity
- **Parent:** Phase 53 source audit closed with NO-GO for free independent historical bid/ask/depth.
- **Input:** frozen Phase 52 v0.2.1 event replay CSV; expected 480 configuration-event rows.
- **Method:** vary only diagnostic OHLC range threshold across 11 preregistered values; preserve exact prior-minute OI >= 100 and existing entry status.
- **Forbidden:** P&L recalculation, exit/fill assumptions, holdout use, strategy ranking, promotion, live-execution recommendations.
- **Next gate:** confirm workflow tests, row reconciliation, artifact and persistence; then close Phase 54 and formulate research-wide conclusion.

## Run checkpoint 37987696866

- Run: [37987696866](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37987696866); workflow job status=success.
- Input rows=480; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Threshold sensitivity (eligibility only):

| Range threshold | Rows passing OI + entry-data + range | Planned share | OI/legs blocked | Range blocked |
|---:|---:|---:|---:|---:|
| 2% | 0 | 0.00% | 480 | 0 |
| 3% | 0 | 0.00% | 480 | 0 |
| 4% | 0 | 0.00% | 480 | 0 |
| 5% | 0 | 0.00% | 480 | 0 |
| 6% | 0 | 0.00% | 480 | 0 |
| 8% | 0 | 0.00% | 480 | 0 |
| 10% | 0 | 0.00% | 480 | 0 |
| 12% | 0 | 0.00% | 480 | 0 |
| 15% | 0 | 0.00% | 480 | 0 |
| 20% | 0 | 0.00% | 480 | 0 |
| 1000% | 0 | 0.00% | 480 | 0 |

- No P&L recomputed, no exits validated, no raw data downloaded, no holdout used, no strategy promoted.

## Run checkpoint 37987717687

- Run: [37987717687](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37987717687); workflow job status=success.
- Input rows=480; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Threshold sensitivity (eligibility only):

| Range threshold | Rows passing OI + entry-data + range | Planned share | OI/legs blocked | Range blocked |
|---:|---:|---:|---:|---:|
| 2% | 0 | 0.00% | 480 | 0 |
| 3% | 0 | 0.00% | 480 | 0 |
| 4% | 0 | 0.00% | 480 | 0 |
| 5% | 0 | 0.00% | 480 | 0 |
| 6% | 0 | 0.00% | 480 | 0 |
| 8% | 0 | 0.00% | 480 | 0 |
| 10% | 0 | 0.00% | 480 | 0 |
| 12% | 0 | 0.00% | 480 | 0 |
| 15% | 0 | 0.00% | 480 | 0 |
| 20% | 0 | 0.00% | 480 | 0 |
| 1000% | 0 | 0.00% | 480 | 0 |

- No P&L recomputed, no exits validated, no raw data downloaded, no holdout used, no strategy promoted.

## Run checkpoint 37987821260

- Run: [37987821260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37987821260); workflow job status=success.
- Input rows=480; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Threshold sensitivity (eligibility only):

| Range threshold | Rows passing OI + entry-data + range | Planned share | OI blocked | Missing leg detail | Range blocked |
|---:|---:|---:|---:|---:|
| 2% | 0 | 0.00% | 107 | 373 | 0 |
| 3% | 0 | 0.00% | 107 | 373 | 0 |
| 4% | 0 | 0.00% | 107 | 373 | 0 |
| 5% | 0 | 0.00% | 107 | 373 | 0 |
| 6% | 0 | 0.00% | 107 | 373 | 0 |
| 8% | 0 | 0.00% | 107 | 373 | 0 |
| 10% | 0 | 0.00% | 107 | 373 | 0 |
| 12% | 0 | 0.00% | 107 | 373 | 0 |
| 15% | 0 | 0.00% | 107 | 373 | 0 |
| 20% | 0 | 0.00% | 107 | 373 | 0 |
| 1000% | 0 | 0.00% | 107 | 373 | 0 |

- No P&L recomputed, no exits validated, no raw data downloaded, no holdout used, no strategy promoted.

## Run checkpoint 37987949045

- Run: [37987949045](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37987949045); workflow job status=failure.
- Input rows=480; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Threshold sensitivity (eligibility only):

| Range threshold | Rows passing OI + entry-data + range | Planned share | OI blocked | Missing leg detail | Range blocked |
|---:|---:|---:|---:|---:|
| 2% | 0 | 0.00% | 107 | 373 | 0 |
| 3% | 0 | 0.00% | 107 | 373 | 0 |
| 4% | 0 | 0.00% | 107 | 373 | 0 |
| 5% | 0 | 0.00% | 107 | 373 | 0 |
| 6% | 0 | 0.00% | 107 | 373 | 0 |
| 8% | 0 | 0.00% | 107 | 373 | 0 |
| 10% | 0 | 0.00% | 107 | 373 | 0 |
| 12% | 0 | 0.00% | 107 | 373 | 0 |
| 15% | 0 | 0.00% | 107 | 373 | 0 |
| 20% | 0 | 0.00% | 107 | 373 | 0 |
| 1000% | 0 | 0.00% | 107 | 373 | 0 |

- No P&L recomputed, no exits validated, no raw data downloaded, no holdout used, no strategy promoted.
