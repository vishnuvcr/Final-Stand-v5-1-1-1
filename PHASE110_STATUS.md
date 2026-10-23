# Phase 110 Status — Greek Stop-Loss Research

Updated: 2026-10-23 (Asia/Kolkata)  
Branch: phase-110-greek-stoploss-short-strangle  
Parent: main  
Research state: registration/source audit in progress  
Promotion status: **NONE — NO STRATEGY PROMOTED**

## Current checkpoint

- [x] Reviewed the main README, global research/data acquisition plan, historical source policy, Phase 52 dataset and exact-minute/Greek-selection implementation, and prior stop-loss research code.
- [x] Created isolated Phase 110 branch without changing prior research branches.
- [x] Frozen user-specified strategy: entry at 10:00 on next trading day after the previous observed weekly expiry; sell current week's approximately 0.15-absolute-delta call and put; expiry-day exit at 14:00.
- [x] Registered net-delta and gross-combined-delta interpretations; fixed 0.40 threshold is explicitly tested.
- [x] Registered all non-empty Greek rule combinations and the finite research phase plan.
- [ ] Commit engine, regression tests and automatic/manual GitHub Actions workflow.
- [ ] Resolve and record source dataset revision and maximum available expiry.
- [ ] Validate source/calendar/selected-leg/path coverage; exclude, rather than synthesize, gaps.
- [ ] Complete full development/validation combination grid under 24 cost scenarios.
- [ ] Apply multiple-testing correction; freeze validation shortlist.
- [ ] Test only frozen shortlist plus baseline and preregistered 0.40-delta rules on reserved holdout.
- [ ] Create developer/tester branches after empirical result acquisition.
- [ ] Publish independently audited manuscript, charts, tables, supplements, README links and final decision.

## Gate policy

A registered rule is not an evaluated rule; an attempted replay is not automatically a valid result. No strategy promotion occurs before exact contract/data coverage, Greek sign/unit tests, one-minute exit timing, date-effective lot/fee accounting, full grid denominator reconciliation, validation multiple-testing control, reserved holdout checks, and independent tester approval.

## Primary data constraints

Primary source is Hugging Face thetrademarkk/india-index-options-1m, declared CC BY-NC 4.0. Its OHLC is not bid/ask or guaranteed executable. Source revision and file list must be resolved during execution; the true cutoff will be recorded. No forward fill/interpolation is allowed. If coverage is missing, report it and retain no-promotion status.

## Phase completion states

| Phase | Purpose | State |
|---|---|---|
| 110.0 | Plan, repo/source audit, specification registration | COMPLETE |
| 110.1 | Historical source/calendar/coverage gate | PENDING |
| 110.2 | Greek engine and regression tests | PENDING |
| 110.3 | Development/validation grid, all costs | PENDING |
| 110.4 | Inference, multiple testing, shortlist freeze | PENDING |
| 110.5 | Holdout of frozen shortlist | PENDING |
| 110.6 | Independent developer/tester audit | PENDING |
| 110.7 | Final manuscript/publication/stop | PENDING |

Developer next instruction: finish the engine/workflow and execute Phase 110.1–110.5 without using holdout results to tune thresholds. Tester next instruction after result acquisition: independently reproduce the control metrics and inspect Greek signs, event joins, time causality, exact fills, fees, lot sizes, split use, grid completeness and manuscript-to-data reconciliation before any promotion decision.

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


## Phase 110 empirical checkpoint — run 39942294075 (2026-10-23T10:54:23.509195+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/39942294075
- Overall job outcome: failure; compile/tests/replay: success/failure/skipped
- Research status: BLOCKED_NO_VALID_CAMPAIGNS
- Dataset revision SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded campaigns: 259/0/263
- Registered configurations/costs/grid rows: 4294/24/206112
- Validation positive paired-uplift rules / Holm-significant rules: 0/0
- Strategy promotion: NONE pending independent review.
