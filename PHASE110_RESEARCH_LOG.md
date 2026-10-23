# Phase 110 Research Log

Append each completed step, including failures. Do not rewrite failed attempts; corrections must append a new note linked to the old result. Timestamp all empirical outputs with source revision, source/code hashes, expected and actual event counts, excluded rows and workflow run IDs.

## 2026-10-23 — Registration and baseline repository review

- **User specification:** “Entry 10 am on the next trading day to the previous weekly expiry / Sell 0.15 delta call and put current weekly / Exit at 2 pm on expiry day / I want you to find a stop loss criteria based on the greeks - delta, gamma, vega, theta / Start by testing SL when combined delta moves beyond 0.4. but test all combination”.
- **Interpretation:** NIFTY weekly options, inferred from the surrounding Final Stand research and available NIFTY minute options source. Entry is on the first NIFTY trading session after the previous observed expiry; target is the next listed weekly expiry.
- **Repository review:** read current main README phase summary, DYNAMIC_N_RESEARCH_PLAN.md, DATA_ACQUISITION.md, current Phase109 status/plan/log excerpts, Phase52 status/protocol/manifest and the Phase52 point-in-time IV/delta selector, plus Phase30 Greek-stop research implementation. Earlier branches remain untouched.
- **Source finding:** the preferred source is Hugging Face thetrademarkk/india-index-options-1m, minute OHLCV+OI, partially missing strikes, declared CC BY-NC 4.0. Minute data and model-estimated Black–Scholes Greeks are not tick quote/exchange Greek data.
- **Critical definition decision:** test both abs(signed net short-portfolio delta) and abs(call delta)+abs(put delta). Short-position portfolio Greeks are the negative of the two long-option Greek sums. The requested net-delta 0.40 threshold is preregistered explicitly.
- **Cost protocol:** 24 scenarios across ₹10/15/20 brokerage per executed order, ₹0/0.05/0.25/0.50 per-unit adverse slippage on entry and exit, and 1.0×/1.5× modelled-fee stress. Four order executions per campaign; date-effective lot, STT, GST, exchange/IPFT, SEBI and stamp-duty components are reported separately.
- **Anti-overfit protocol:** full grid on development/validation; candidate ordering only on validation after Holm correction; reserved holdout is restricted to a frozen shortlist (at most 20), baseline, and the preregistered 0.40-delta configs. No holdout-based parameter tuning.
- **Result state:** no data acquisition or strategy P&L has been accepted as of this entry. Phase 110 remains no-promotion.
- **Next gate:** implement the fixed Greek engine, exhaustive finite grid, source integrity gates, unit tests and cached/manual+automatic Actions workflow.

## Research record format for subsequent entries

For each run append: timestamp; branch and workflow URL/run ID; dataset repo + resolved revision SHA; each source-file hash; code/protocol SHA256; expected/eligible/excluded events; Greek coverage and time-gap counts; grid rows planned/attempted/completed/failed; cost cases reconciled; key metrics; tests; remaining blockers; promotion status. Do not store credentials, raw minute data, or hidden chain-of-thought.

## Phase 110 failure — run 39940933286 (2026-10-23T10:42:30.010393+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39940933286
- Outcomes: {"COMPILE_OUTCOME": "success", "JOB_STATUS": "failure", "REPLAY_OUTCOME": "failure", "TEST_OUTCOME": "success"}
- Failure detail: {
  "status": "RUNTIME_ERROR",
  "created_at_utc": "2026-10-23T10:42:29.854125+00:00",
  "error_type": "TypeError",
  "error": "HfApi.dataset_info() got an unexpected keyword argument 'repo_type'"
}

- No accepted P&L results or promotion claim.


## Phase 110 empirical checkpoint — run 39941034072 (2026-10-23T10:46:31.519648+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39941034072
- Overall job outcome: success; compile/tests/replay: success/success/success
- Research status: BLOCKED_NO_VALID_CAMPAIGNS
- Dataset revision SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/0/263
- Registered configurations/costs/grid rows: 4294/24/206112
- Validation positive paired-uplift rules / Holm-significant rules: 0/0
- Strategy promotion: NONE pending independent review.


## Phase 110 empirical checkpoint — run 39941360781 (2026-10-23T10:47:20.441431+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39941360781
- Overall job outcome: failure; compile/tests/replay: success/failure/skipped
- Research status: BLOCKED_NO_VALID_CAMPAIGNS
- Dataset revision SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/0/263
- Registered configurations/costs/grid rows: 4294/24/206112
- Validation positive paired-uplift rules / Holm-significant rules: 0/0
- Strategy promotion: NONE pending independent review.


## Phase 110 empirical checkpoint — run 39941568976 (2026-10-23T10:48:16.361431+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39941568976
- Overall job outcome: failure; compile/tests/replay: success/failure/skipped
- Research status: BLOCKED_NO_VALID_CAMPAIGNS
- Dataset revision SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/0/263
- Registered configurations/costs/grid rows: 4294/24/206112
- Validation positive paired-uplift rules / Holm-significant rules: 0/0
- Strategy promotion: NONE pending independent review.


## Phase 110 empirical checkpoint — run 39941628120 (2026-10-23T10:49:10.880597+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39941628120
- Overall job outcome: failure; compile/tests/replay: success/failure/skipped
- Research status: BLOCKED_NO_VALID_CAMPAIGNS
- Dataset revision SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/0/263
- Registered configurations/costs/grid rows: 4294/24/206112
- Validation positive paired-uplift rules / Holm-significant rules: 0/0
- Strategy promotion: NONE pending independent review.


## Phase 110 empirical checkpoint — run 39942088696 (2026-10-23T10:52:36.208597+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39942088696
- Overall job outcome: failure; compile/tests/replay: success/failure/skipped
- Research status: BLOCKED_NO_VALID_CAMPAIGNS
- Dataset revision SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/0/263
- Registered configurations/costs/grid rows: 4294/24/206112
- Validation positive paired-uplift rules / Holm-significant rules: 0/0
- Strategy promotion: NONE pending independent review.


## Phase 110 empirical checkpoint — run 39942123879 (2026-10-23T10:53:27.192586+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39942123879
- Overall job outcome: failure; compile/tests/replay: success/failure/skipped
- Research status: BLOCKED_NO_VALID_CAMPAIGNS
- Dataset revision SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/0/263
- Registered configurations/costs/grid rows: 4294/24/206112
- Validation positive paired-uplift rules / Holm-significant rules: 0/0
- Strategy promotion: NONE pending independent review.
