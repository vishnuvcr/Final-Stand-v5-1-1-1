# Phase 54 status — OHLC-reference eligibility sensitivity

**Overall:** BLOCKED / HANDOFF TO PHASE 55 — verified workflow run 37988143410 completed the evidence-completeness audit; alternate-threshold estimates remain intentionally uncomputed.

- **Branch:** phase-54-ohcl-reference-sensitivity
- **Parent:** Phase 53 source audit closed with NO-GO for free independent historical bid/ask/depth.
- **Input:** frozen Phase 52 v0.2.1 event replay CSV; expected 480 configuration-event rows.
- **Audit result:** [run 37988143410](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37988143410) passed tests and persistence. Parent statuses reconcile to 100 OI blocks, 379 range exclusions and 1 replay pass. Family-level payload audit found 21 complete rows, 459 incomplete rows, 373 empty payloads and 86 partial payloads; zero range-excluded rows had a complete leg payload. The 21 complete rows are not enough to reconstruct all 480 rows.
- **Forbidden:** P&L recalculation, exit/fill assumptions, holdout use, strategy ranking, promotion, live-execution recommendations.
- **Next gate:** Phase 55 repairs the Phase 52 runner to preserve all selected legs for every status and reruns the same frozen pilot. Return here only after payload completeness passes.

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

## Run checkpoint 37987961994

- Run: [37987961994](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37987961994); workflow job status=failure.
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

## Run checkpoint 37988143410

- Run: [37988143410](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37988143410); workflow job status=success.
- Input rows=480; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Complete leg payload rows=21; incomplete=459; empty payloads=373; partial payloads=86.
- Range-excluded rows with complete leg payload=0.
- Sensitivity decision=OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE; alternate thresholds are not computed because parent output lacks complete leg-level evidence.
- No P&L recomputed, no exits validated, no raw data downloaded, no holdout used, no strategy promoted.

## Run checkpoint 37988153104

- Run: [37988153104](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37988153104); workflow job status=success.
- Input rows=480; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Complete leg payload rows=21; incomplete=459; empty payloads=373; partial payloads=86.
- Range-excluded rows with complete leg payload=0.
- Sensitivity decision=OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE; alternate thresholds are not computed because parent output lacks complete leg-level evidence.
- No P&L recomputed, no exits validated, no raw data downloaded, no holdout used, no strategy promoted.
