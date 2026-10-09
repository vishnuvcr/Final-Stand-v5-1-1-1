# Phase 54 research log

## Step 1 — 2026-10-10 — Plan and implementation
- Created separate branch phase-54-ohcl-reference-sensitivity.
- Added a Python sensitivity analyzer, regression tests and manual/automatic GitHub Actions workflow.
- Scope is limited to diagnostic eligibility counts from the committed Phase 52 event replay CSV. It does not run a strategy backtest, alter frozen Phase 52 results, download raw data, use holdout or recalculate P&L.
- Workflow execution and numerical outputs remain pending until a run artifact is verified.

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


## Step 2 — 2026-10-10 — Evidence completeness audit
- Final accepted workflow: [37988143410](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37988143410), all tests, artifact upload and checkpoint persistence passed.
- Parent input SHA-256: ca60e4b1757b1b6cb7fa94b495eff73e08da481fbe3952a19808a10dfdac19db; 480 rows; parent status counts 100 OI blocks, 379 range exclusions, 1 pass.
- Payload audit: 21 complete rows, 459 incomplete rows, 373 empty leg payloads, 86 partial payloads, and zero range-excluded rows with complete leg payload.
- Decision: no alternate threshold results accepted. The earlier numerical sensitivity output is invalidated because it used incomplete leg evidence. Phase 55 must repair and rerun the source runner before sensitivity can be computed.
