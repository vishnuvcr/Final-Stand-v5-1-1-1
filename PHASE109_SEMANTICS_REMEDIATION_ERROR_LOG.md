# Phase 109 semantic remediation error/limitation log

## 2026-10-12
- **E109-S01 — Core substitution:** v1 substring mapping could score a distinct registered strategy as ordinary price momentum. Corrective action: exact allowlist; unsupported strategies blocked.
- **E109-S02 — Confirmation provenance:** v1 mapped cross-asset confirmation to the other domestic index. Corrective action: block unimplemented confirmation families.
- **E109-S03 — Undefined volatility target:** v1 computed realised-volatility state without enforcing a preregistered target-state dimension. Corrective action: block that regime.
- **E109-S04 — Rule semantics:** EMA slope was return momentum and EMA crossover was spread sign, not a crossing event. Corrective action: explicit implementations with regression fixtures.
- **E109-S05 — Missing rule/input implementations:** futures basis, synthetic parity, IV/skew/Greeks, VWAP, opening-gap, volume, global, news/event, breadth and DII/FII families remain blocked; do not count as successful tests.
- **E109-S06 — Execution evidence:** EOD OHLC, even with positive volume, does not verify fills, spread, depth, latency or partial fills; user-specific Paytm Money contract-note charges remain unverified.
- **Parent sweep checkpoint:** at resume, the v1 cursor had completed 4,000 configurations / 96,000 cost rows and had 590,000 eligible configurations remaining. This is a count checkpoint only.
- No secret or authenticated raw response was copied to public logs.

## 2026-10-12 08:02 UTC — v2 evaluation workflow failure
- Run 38221168260 failed before a verified shard checkpoint. Inspect the Actions job log; do not infer performance results.

## 2026-10-12 — Root cause for first v2 evaluator failure

- Run [38221168260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221168260) passed compilation and all 26 offline tests and resolved `start_config=0`, then failed in `load_market()` with `Private NSE data cache is missing; run the official NSE acquisition workflow first.`
- Cause: GitHub Actions caches are branch-scoped for this pipeline; the new remediation branch did not have the parent's private source archive cache. No strategy configuration was scored and no v2 metrics were emitted.
- Correction: enabled the official NSE acquisition workflow for the remediation branch, allowed safe aggregate report publication there, and added a cost-window/source-gated evaluator dispatch after acquisition completes. Run [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) is running. If row/lot-size/index-context gates fail, the evaluator must remain blocked rather than use partial rows.
- This is a source-cache setup issue, not evidence that the strategies won or lost. No raw response or token was published.

## 2026-10-12 — E109-S07 risk-profile parsing defect
- Static review found the v2 `simulate_trade()` stop/target regex used doubled escaping, which can leave stop/target percentages unset and falsely execute a barrier configuration as a plain close trade.
- Correction: introduced `parse_risk_profile()` with standard digit groups and added regression assertions for stop-only, target-only, combined stop-target and no-barrier profiles. Updated v2 source and test file commits are `d78a68e9` and `4ded4700` respectively.
- The new semantic-test run is queued; do not treat this correction as validated until that run passes. The source acquisition and data gate are still running; no v2 P&L result exists.

## 2026-10-12 08:08 UTC — Regression retest passed
- Run [38221764332](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221764332) passed 27/27 unit tests after the risk-profile parsing fix. This closes the code-regression check for the listed paths only; data acquisition and corrected empirical evaluation remain open.

## 2026-10-12 08:31 UTC — E109-S08 — Repeated feature aggregation overhead

- Observation: aggregate_chain_features was called once for every configuration, despite depending only on cached source rows, symbol and date range. That repeated work across the grid and risked exhausting the bounded workflow time budget.
- Correction: precompute per-symbol feature maps once immediately after loading the source data and reuse them inside every task. The intended feature values and strategy decisions are unchanged.
- Regression evidence: [run 38224068522](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224068522) passed all 29 offline tests, including the precomputation-call-count test.
- Limitation: no full-shard runtime comparison has yet been observed, so the actual wall-time reduction is not quantified. The active acquisition/evaluation workflows remain authoritative for empirical checkpoints.

## 2026-10-12 08:38 UTC — E109-S09 — Truncated official index/VIX history passed a weak gate

- Observation: near-annual NSE historical API requests yielded about 70 rows per series; the previously published three-year context contained only 218 unique dates per series against 743 option archive dates. Although the OHLC schema was clean, source context was not temporally complete and 526 archive dates had no corresponding NIFTY 50 date. The prior gate incorrectly treated any nonempty series as sufficient.
- Correction: split requests into 60-calendar-day windows, set a minimum of 60% of weekday observations per series, mark low-coverage audit output as PARTIAL_OR_FAILED, enforce archive/index calendar overlap before dispatch and add a runtime fail-closed gate in the evaluator.
- Version control: moved the evaluator to phase109-eod-engine-v3-context-coverage so partial v2 checkpoint ranges cannot be reused with the repaired context. Existing v2 output is diagnostic only.
- Run [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723) is re-acquiring context. No v3 empirical checkpoint has been verified yet.

## 2026-10-12 08:38 UTC — E109-S10 — Staged engine-version test mismatch

- Run [38224769569](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224769569) failed because the evaluator had already been bumped to v3 while the version regression assertion still expected v2. The test fixture was updated to v3 and new tests were added for truncated/sufficient context.
- Follow-up run [38224798558](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224798558) passed **32/32 tests**. No runtime data output was implicated in the mismatch.

## 2026-10-12 08:43 UTC — E109-S11 — Context-density cutoff strengthened

- The first corrective proposal used a 60% weekday threshold; that can still permit too much missing historical context for regime filtering.
- Updated the official source and evaluator gates to require at least 90% of weekdays per official series and added tests for truncated-context rejection and adequate-context acceptance.
- Regression [38225233888](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233888) passed 32 tests. This verifies code behavior only; the updated API re-acquisition still needs to pass its coverage gate.
