# Phase 109 semantic remediation status

Updated: 2026-10-12  
Branch: `phase-109-strategy-semantics-remediation`  
State: **38 REGRESSION TESTS PASS; 90% CONTEXT GATE PASS; SPECIAL-SESSION REACQUISITION RUNNING; V4 SHARD QUEUED**  
Promotion: **NONE**

## Remediation
- [x] Inspected Phase 109 plan/status/log/error/chat, evaluator workflow, checkpoint and source audits.
- [x] Created isolated branch to leave the parent sweep untouched.
- [x] Replaced substring-based core mapping with an exact allowlist.
- [x] Changed EMA slope to measure normalized EMA change and EMA crossover to require a sign crossing.
- [x] Blocked unsupported confirmation and unparameterized realised-volatility target regimes.
- [x] Bumped engine to `phase109-eod-engine-v2-semantics` so v1 cursor state is not reused.
- [x] Added semantic regression tests.
- [x] Dedicated test workflow passed 26/26 offline tests (run [38221129326](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221129326)).
- [x] Evaluator resolved v2 cursor to zero; first attempt failed before scoring because the private branch-local NSE cache was missing ([run 38221168260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221168260)).
- [x] Corrected v2 publishes one diagnostic shard: 2,000 configurations / 48,000 cost rows; not eligible for promotion because it used incomplete official index/VIX context.
- [x] Replaced v3 with v4 session-coverage gate and unique result filenames.
- [ ] Reconcile 24 cost rows/config, blockers, cursor and result SHA after the source gate allows empirical replay.
- [ ] Update final statistical report only after validation/holdout/multiple-testing gates.

## Latest checkpoint
<!-- SEMANTICS_LIVE_CHECKPOINT_START -->
The official index/VIX history now has 748 unique dates each for India VIX, NIFTY 50 and NIFTY BANK across 2023-10-03–2026-10-08 (minimum 711, 90% of 789 weekdays); zero failed chunk-series calls, duplicate dates and invalid/missing OHLC rows. Calendar reconciliation identified five NIFTY 50-observed special sessions without an option archive (2023-11-12, 2024-01-20, 2024-05-18, 2025-02-01, 2026-02-01). The acquisition workflow has been reordered to acquire the official session calendar before probing NSE option archives, and the archive request now unions weekday probes with observed weekend/special sessions. Source run [38227481409](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227481409) is active on this corrected order; the obsolete source run [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) was cancelled as stale. Engine v4 independently requires the 90% context-density and explicit options/index session reconciliation gates. Regression workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed 38/38 tests. The v4 evaluation run [38227487048](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227487048) is pending behind diagnostic v3 run [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004), which had processed 800/2,000 configurations at the last log checkpoint. Workflow concurrency is now configured to replace obsolete in-flight runs when newer commits arrive; the old evaluation job has not yet reported a terminal state. No v4 result shard has been verified and no strategy is promoted.
<!-- SEMANTICS_LIVE_CHECKPOINT_END -->

## Links
- [Plan](PHASE109_SEMANTICS_REMEDIATION_PLAN.md)
- [Audit](results/phase109/SEMANTICS_REMEDIATION_AUDIT.md)
- [Semantic tests](research/phase109/test_phase109_strategy_semantics.py)
- [Semantic test workflow](.github/workflows/phase109-implementation-tests.yml)
- [Resumable evaluator workflow](.github/workflows/phase109-evaluate-grid.yml)

## Automated failure checkpoint — 2026-10-12 08:02 UTC

- [Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221168260) failed before successful publication. No profitability result inferred.

## Verified implementation checkpoint — 2026-10-12

- Semantic regression run [38221129326](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221129326): PASS, 26 tests.
- v2 evaluator run [38221168260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221168260): FAILED before scoring because the private cache was unavailable on the new branch; exact cursor resolved to 0, no configuration results were emitted.
- Source cache warmup [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273): RUNNING. It will dispatch the evaluator after completion only if the audited source gate passes.
- Current decision: implementation tests pass; empirical v2 evaluation pending. No strategy is promoted.

## Regression-test verification — 2026-10-12 08:08 UTC

- [Run 38221764332](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221764332) completed successfully: **27 tests passed**, including exact core mappings, unsupported confirmation/regime rejection, EMA semantics and stop/target-profile parsing.
- This validates tested code paths only. The evaluator still requires the private source cache and source-quality gate before any v2 configuration is scored.
- [NSE acquisition/cache warmup run 38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) remains the active data prerequisite at log time.


## 2026-10-12 08:31 UTC — Performance optimization and regression verification

- Static profiling review found daily option-chain aggregation was repeated inside each configuration iteration although it is invariant across parameters.
- Updated the v2 evaluator to precompute the daily options-flow feature aggregates once per supported underlying per shard, then reuse those aggregates across configurations. This is intended to reduce duplicated row scanning without changing the feature definition.
- Automated regression run [38224068522](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224068522) passed **29/29 tests**, including the new one-precomputation-per-symbol test.
- Acquisition run [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) has completed options, Dhan and index-futures acquisition steps; IV/Greeks derivation remains active at this checkpoint. V2 results are still pending source gate and evaluator dispatch.
- No strategy is promoted; cost, execution realism, validation, multiple-testing and holdout requirements remain unchanged.

## Automated checkpoint — 2026-10-12 08:48 UTC

- [Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224200260)
- Engine: phase109-eod-engine-v2-semantics; status: PARTIAL_SHARD_COMPLETE; cursor [0,2,000).
- This shard: 2,000 configurations; 48,000 cost rows. Cumulative: 2,000 configurations; 170,800 remaining.
- This is workflow/evaluation progress only. OHLC execution proxies are not verified fills; no strategy promoted.


## 2026-10-12 09:03 UTC — Official context gate passed; v4 queued

- Refreshed official context summary reports 748 unique dates for India VIX, NIFTY 50 and NIFTY BANK, all above the minimum 711 observations (90% of 789 weekdays). There are zero failed chunk-series calls, duplicate date rows, invalid OHLC rows or missing OHLC rows.
- Calendar reconciliation reports 743 valid options archive dates, all with a NIFTY 50 observation; five observed NIFTY 50 sessions lack valid option archives and are excluded rather than synthesized.
- The current engine version is `phase109-eod-engine-v4-session-coverage`; prior v1/v2/v3 progress is ineligible for cursor reuse. Latest test workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed. The updated acquisition run [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) is running and v4 evaluator run [38227220343](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227220343) is pending. The older run [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004) was launched on an earlier checkout and cannot certify v4.
- No strategy has been promoted and no profitability conclusion is inferred from coverage completion.


## 2026-10-12 09:04 UTC — Reorder source dependency and supersede stale runs

- The first special-session implementation read the committed session calendar before the same workflow had refreshed it. Fixed acquisition order so official NSE Indices history and its observed-session calendar are generated before the NSE option archive probe, ensuring the five special dates are available to that same run.
- Enabled replace-obsolete-run concurrency in the source and evaluator workflows. A source refresh on the latest workflow [38227481409](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227481409) is active. The prior run [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) was cancelled, then superseded by the corrected workflow. The v4 evaluator workflow [38227487048](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227487048) remains queued behind a diagnostic v3 run.
- Verified previous context: 748 dates per official series; minimum expected 711. The option archive table is being rebuilt to explicitly attempt special observed NIFTY 50 sessions.
- Last complete regression workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed 38/38 tests.
- No strategy result or promotion is inferred from pending workflows.

## Automated checkpoint — 2026-10-12 09:39 UTC

- [Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38228843868)
- Engine: phase109-eod-engine-v4-session-coverage; status: PARTIAL_SHARD_COMPLETE; cursor [0,2,000).
- This shard: 2,000 configurations; 48,000 cost rows. Cumulative: 2,000 configurations; 170,800 remaining.
- This is workflow/evaluation progress only. OHLC execution proxies are not verified fills; no strategy promoted.
