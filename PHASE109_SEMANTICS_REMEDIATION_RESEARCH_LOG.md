# Phase 109 semantic remediation research log

## 2026-10-12 — Source audit
- Read current Phase 109 plan, status, research/error/chat logs, evaluator/workflow, shard summary/progress and source-feasibility reports before editing.
- Parent evaluator run [38216687089](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38216687089) completed successfully, and its automatic continuation [run 38219270449](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38219270449) was observed in progress during resume.
- The latest parent v1 published checkpoint is two completed ranges: 4,000 configurations, 96,000 cost rows, 590,000 remaining. That is workflow progress, not a profitability conclusion.
- Static review discovered name-substring fallback, invalid cross-asset confirmation semantics, undefined target state for realised-volatility regimes, EMA slope aliasing and lack of a crossing condition for EMA crossover.
- Opened an isolated branch so the parent workflow and published checkpoint remain preserved.
- V2 exact allowlist, semantic tests and engine-version cursor reset are implemented; actual Actions execution and empirical metrics are not yet verified.
- Transaction-cost assumptions remain 24 scenarios; OHLC fills are execution proxies; no strategy is promoted.

## 2026-10-12 — Semantic test pass and cache-gated restart

- Automated semantic test run [38221129326](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221129326) passed 26/26 tests (offline Phase 109 test suite).
- The first corrected v2 evaluator run [38221168260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221168260) resolved its cursor to 0 but stopped before loading/evaluating strategies because the sibling branch could not restore the parent's private Actions cache: `Private NSE data cache is missing`. This is not a performance result.
- Corrected the branch-local source acquisition workflow to rebuild/cache official NSE/index/VIX/Dhan features once, publish aggregate reports only, and dispatch the evaluator after the cache-producing job ends and source gates pass. Acquisition run [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) is the current source gate.
- Continue only with the bounded evaluator if exact-option rows, historical lot sizes and nonempty official index/VIX context pass; otherwise preserve a blocked decision. No strategy promoted.

## 2026-10-12 — Risk-profile parser correction
- Found an additional variable-application defect in the stop/target parser while reviewing the registered risk grid. Fixed parsing for `STOP_10/20/30PCT`, `TARGET_10/20/30PCT` and combined profiles using `parse_risk_profile()`.
- Added a regression test for stop-only, target-only, combined and no-barrier configurations. Updated test workflow run [38221764332](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221764332) is queued at log time; no PASS claim yet.
- The source acquisition remains in progress in [run 38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273). No v2 configuration P&L has been scored.

## 2026-10-12 08:08 UTC — Corrected semantic tests passed
- [Run 38221764332](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221764332) passed **27/27** offline tests, including stop/target percentage parsing. This is code verification, not empirical profitability evidence.
- The v2 evaluator remains pending usable source cache: acquisition run [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) is still in progress. No v2 returns have been generated.

## 2026-10-12 08:31 UTC — Chain-feature throughput correction

- Reviewed the remediation plan/status/error/chat logs, current evaluator implementation, and active Actions runs before editing.
- Identified duplicated aggregate_chain_features work inside the per-configuration loop. Replaced it with a shard-start precomputation for the supported NIFTY and BANKNIFTY feature series; each configuration reuses the same point-in-time aggregated feature mapping.
- Added a regression test for one aggregation call per supported symbol. Workflow [38224068522](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224068522) passed 29/29 offline tests.
- Acquisition workflow [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) completed NSE options acquisition, Dhan rolling-options acquisition and index futures extraction; IV/Greeks is the active step, with index/VIX context and reconciliation still pending.
- The current v2 grid has not yet been empirically scored. No strategy results are inferred from a running job or registered configuration count.

## 2026-10-12 08:38 UTC — Truncated historical context detected and gated

- Reviewed the completed NSE acquisition output, calendar reconciliation, evaluator runtime and active Actions runs. The previous official index/VIX request path used near-annual windows; each request returned around 70 observations. Across the three-year range that produced only 218 dates per series while 743 option-archive dates were available. The old audit reported PASS because it checked schema quality and nonzero rows, not date density.
- Changed the source client to disjoint windows no longer than 60 calendar days, which should keep each API response below the observed row cap. Added an explicit minimum context density equal to at least 60% of weekdays in the requested range and recorded per-series coverage status.
- Added an independent fail-closed check to the evaluator and bumped engine version to phase109-eod-engine-v3-context-coverage so incomplete-context v2 checkpoints are never reused. Tightened dispatch to require complete VIX/index coverage and low option/index session-gap counts. Changed the source cache workflow to save the refreshed cache before dispatch.
- The corrected source workflow [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723) is running. The v3 evaluation run [38224798595](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224798595) is pending; the older v2 run [38224200260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224200260) is not eligible for promotion.
- Latest regression workflow [38224798558](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224798558) passed 32/32 tests. No profitability claim is based on context acquisition alone.

## 2026-10-12 08:43 UTC — Raise context-density gate to 90%

- Raised minimum expected official index/VIX coverage to 90% of weekdays after the initial 60% threshold was judged too permissive for a multi-year options comparison.
- Source-client and evaluator-runtime checks now use that stronger threshold, and a test verifies short series at the previous 218-date scale fail closed while sufficiently covered series pass.
- Regression run [38225233888](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233888) passed 32/32 tests.
- The existing source run [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723) began before the threshold was raised; the updated source run [38225253211](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225253211) is queued. The v3 evaluator workflow is pending and will refuse the old v2 cursor.
