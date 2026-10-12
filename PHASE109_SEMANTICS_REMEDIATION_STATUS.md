# Phase 109 semantic remediation status

Updated: 2026-10-12  
Branch: `phase-109-strategy-semantics-remediation`  
State: **32 REGRESSION TESTS PASS; 90% HISTORICAL-CONTEXT GATE ACTIVE; V3 SHARD PENDING**  
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
- [ ] After source reacquisition, corrected evaluator publishes a v2 shard.
- [ ] Reconcile 24 cost rows/config, blockers, cursor and result SHA after the source gate allows empirical replay.
- [ ] Update final statistical report only after validation/holdout/multiple-testing gates.

## Latest checkpoint
<!-- SEMANTICS_LIVE_CHECKPOINT_START -->
The latest corrected test run [38225233888](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233888) passed **32/32 tests** after raising the expected official context density to 90% of weekdays. The previous context audit was insufficient: ~218 dates per series versus a multi-year trading history. The NSE context client now uses at most 60-calendar-day request windows and requires ≥90% weekday coverage; the evaluator is engine `phase109-eod-engine-v3-context-coverage`, refuses truncated input at runtime, and the source dispatch additionally checks option/index calendar overlap. Source reacquisition run [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723) is progressing through the Dhan historical-feature step; refreshed run [38225253211](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225253211) is queued. The v3 evaluation workflow [38225233884](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233884) is pending; no corrected v3 shard has been verified. No strategy profitability conclusion or promotion is available.
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


## 2026-10-12 08:38 UTC — Official context coverage gate added

- The previous three-year NSE index/VIX audit had only 218 observed dates per series and 526 valid option-archive dates without a corresponding NIFTY 50 observation. Its status was too permissive because PASS did not enforce a minimum date-density requirement.
- Corrected the endpoint windows to no more than 60 calendar days; added a coverage threshold of at least 60% of request-window weekdays per series, strict calendar reconciliation and a source gate requiring archive/index overlap.
- Bumped the evaluator to phase109-eod-engine-v3-context-coverage so v2 checkpoints produced with incomplete context cannot be reused. The evaluator now raises an explicit coverage error before scoring if the official India VIX, NIFTY 50 or NIFTY BANK history is truncated.
- Source acquisition run [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723) is active; v3 evaluator run [38224798595](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224798595) is pending. The old v2 run [38224200260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224200260) is diagnostic only and its results will be separated by the engine-version reset.
- Regression run [38224798558](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224798558) passed 32/32 tests; the immediately preceding staged test run failed only because the engine-version expectation still said v2 and was corrected before the passing run.


## 2026-10-12 08:43 UTC — 90% historical-context coverage threshold

- Tightened official index/VIX minimum observations from the first corrective 60% threshold to 90% of requested-window weekdays. This reduces the chance that materially incomplete context is allowed to score a regime family.
- The follow-up regression workflow [38225233888](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233888) passed 32/32 tests, including the expected-observation gate and fail-closed evaluator behavior.
- Source run [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723) still runs the earlier 60% revision, while [38225253211](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225253211) is queued for the latest 90% revision. The v3 evaluator is not eligible to use old v2 checkpoint rows.
- Main README updated in commit [1f808b5a30399108633584c75e7c19f01606f05e](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/1f808b5a30399108633584c75e7c19f01606f05e).
