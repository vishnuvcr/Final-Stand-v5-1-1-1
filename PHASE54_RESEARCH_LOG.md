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
