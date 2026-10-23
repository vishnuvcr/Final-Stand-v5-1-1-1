# Phase 111 Research Log

Append every step and outcome, including failed attempts. Do not overwrite failed attempts; corrections are new entries linked to the failure. Keep each record timestamped and identify the source revision, hashes, expected/eligible/excluded campaigns, tests, cost rows, outcome and remaining limitation. Never store credentials, private authenticated responses, raw bulk market data, or hidden chain-of-thought.

## 2026-10-24 — Registration and repository review
- User asked for a new test of the supplied ZigZag++ indicator, on a daily NIFTY 50 chart, no repainting, no tester review.
- Frozen rule: last confirmed low (HL/LL) at the prior weekly expiry close means sell a PE targeting absolute delta 0.10; last confirmed high (HH/LH) means sell a CE targeting absolute delta 0.10. Enter at 10:00 IST on the next trading session after prior expiry. Exit at 10:00 IST on the target weekly expiry unless absolute model delta reaches 0.50 first; a stop fills at the next exact minute open.
- Source selection uses the exact 09:59 completed bar's close for delta selection and the 10:00 exact opening price for the simulated entry; no selection based on future bar data.
- The supplied Pine source imports DevLucem/ZigLib/1, whose library body was not pasted. The Python engine therefore identifies its causal MT4-style signal path as a proxy, not an asserted byte-for-byte TradingView-library match.
- Repo review found the Phase 110 plan/code/workflow and a published report with 130 eligible/133 excluded, while other status checkpoints report 0/259. This is explicitly carried as a prior-phase discrepancy rather than reinterpreted.
- Workflow, exact source audit, causal indicator tests, no-look-ahead campaign replay, one-leg fees/slippage and paired no-stop benchmark are registered in PHASE111_RESEARCH_PLAN.md.
- No result or strategy promotion is claimed at registration.

## User specification
> Entry at 9 30 AM to 10 30 AM on the next trading day to the previous weekly expiry. As on the previous day end, when the last formed indication is low, sell a put of delta 0.1. When the last formed indication is high, sell a call of delta 0.1. Exit at 9 30 AM to 10 30 AM on the weekly expiry day. Universal stoploss is when the delta of the sold option reaches 0.5 or more. No repainting. No tester review needed.

## Run log
The automated workflow appends run IDs, source revision, coverage, metrics, pass/fail status and error details below after every run.

## Failed or blocked execution — run 40035215935 (2026-10-23T22:41:51.256128+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40035215935
- Outcomes: {"COMPILE_OUTCOME": "success", "JOB_STATUS": "failure", "REPLAY_OUTCOME": "skipped", "TEST_OUTCOME": "failure"}
- Error: No summary was produced; inspect the first failed Actions step. No P&L result is inferred.
- No accepted strategy result or promotion claim.


## Failed or blocked execution — run 40035279559 (2026-10-23T22:42:47.797264+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40035279559
- Outcomes: {"COMPILE_OUTCOME": "success", "JOB_STATUS": "failure", "REPLAY_OUTCOME": "skipped", "TEST_OUTCOME": "failure"}
- Error: No summary was produced; inspect the first failed Actions step. No P&L result is inferred.
- No accepted strategy result or promotion claim.


## Automated replay — run 40035385054 (2026-10-23T22:50:24.906414+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40035385054
- Outcome compile/tests/replay: success/success/success
- Dataset revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/142/121
- Costs: 24; status: EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION; promotion: NONE.


## Automated replay — run 40035279559 (2026-10-23T22:56:40.621926+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40035279559
- Outcome compile/tests/replay: success/success/success
- Dataset revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/142/121
- Costs: 24; status: EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION; promotion: NONE.
