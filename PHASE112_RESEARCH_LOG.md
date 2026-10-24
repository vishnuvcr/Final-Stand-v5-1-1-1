# Phase 112 Research Log

Append every completed step, including failures and corrections. Keep source SHA, source file hashes, code/protocol revision, expected/eligible/excluded denominators, test results, cost cases and run URL. Do not store credentials, raw minute data, or hidden chain-of-thought.

## 2026-10-24 — Registration
- User asked to test Greek stop-loss combinations following the Phase 111 ZigZag strategy.
- Kept the fixed entry rule unchanged: confirmed daily low (HL/LL) sells PE, confirmed daily high (HH/LH) sells CE, absolute model Delta target 0.10, exact 10:00 entry next observed session after previous expiry.
- Fixed scheduled exit at exact 10:00 on target expiry. Stop triggers use completed one-minute close and next observed minute open.
- Registered normalized Delta, Gamma, Vega, Theta and Rho stop criteria, single-Greek threshold sweeps, all multi-Greek subsets, ANY/ALL logic, no-stop reference, 24 cost cases and chronological splits in PHASE112_RESEARCH_PLAN.md before replay.
- Phase 111 first replay summary was 259 scheduled / 142 eligible / 121 excluded, split 96/45/1. The source used a Python confirmed-only ZigZag proxy because the supplied source omitted the imported ZigLib body; that caveat carries forward.
- No Greek-combination P&L has yet been accepted at registration.


## Run 40072066860 (2026-10-24T07:03:47.012097+00:00)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40072066860
- Compile/tests/replay: success/success/success
- Dataset SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Scheduled/eligible/excluded: 259/139/124
- Candidates/costs/grid rows: 72/24/5184
- Status: EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION; promotion: NONE.


## Final empirical checkpoint — workflow 40072066860 (2026-10-24T07:03:47Z)
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40072066860
- Compile/tests/replay: success/success/success. The registered Greek-sign, candidate-grid, ANY/ALL trigger and cost-reconciliation tests passed.
- Dataset revision SHA: \`0f4800e43e6f96cec0794369d78eb4d3c4211ef5\`; 267 expiry files, 2021-05-27 through 2026-08-04.
- Scheduled/eligible/excluded: 259/139/124. Split eligible counts: development 93, validation 45, holdout 1.
- Candidate/cost/grid rows: 72/24/5,184. No raw minute data was committed.
- At primary cost B20_S0.25_F1.0, no-stop validation net P&L was ₹10,854.87; Delta 0.50 was ₹7,066.39; Gamma 0.30 was ₹7,567.34; Theta 0.50 was ₹10,367.11; Delta 0.50 + Gamma 0.20 (ANY) was ₹2,669.21.
- Paired comparison: 0/52 multi-Greek combinations and 0/19 single-Greek threshold variants produced positive validation uplift versus no-stop across any of the 24 registered cost cases. For combinations, 15 rules never triggered and exactly matched no-stop; 37 had negative uplift in every cost case.
- The Gamma 0.30 variant reduced observed validation max drawdown versus no-stop by about ₹508 but sacrificed ₹3,287.53 net P&L. Delta+Gamma ANY reduced drawdown to ₹1,963.18 but sacrificed ₹8,185.66 net P&L. Vega/Rho registered thresholds triggered on 100% of validation campaigns, with net P&L -₹3,186.70.
- Inference: **no stop is promoted**. Current stop grid did not improve validation net P&L; one eligible holdout event cannot determine robustness. Results remain proxy-based pending exact ZigLib parity and realistic quote/execution data.
- Final report: \`results/phase112/PHASE112_REPORT.md\`; manuscript: \`results/phase112/PHASE112_MANUSCRIPT.md\`; complete 5,184-row grid: \`results/phase112/candidate_cost_grid.csv\`.
- Finite Phase 112 gates 112.0–112.6 are complete; study stopped here as registered. No tester review was run, per user instruction.
