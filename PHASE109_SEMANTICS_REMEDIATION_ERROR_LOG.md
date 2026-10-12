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

## 2026-10-12 08:48 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 08:50 UTC — E109-S12 — Cost-rate report precision regression

- Run [38225233884](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233884) failed before configuration evaluation because an added source-check test expected 0.0003552 from a rate field that the cost-model serializer rounded to six decimal places. The underlying fee calculation used the full rate already; this was a reporting/test-contract defect, not a fee calculation mismatch.
- Corrected canonical cost-model reporting to preserve 12 decimal places for fields with names containing rate, leaving currency amounts rounded to 6 decimal places. Regression runs [38225975745](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225975745) and [38226082378](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226082378) passed 33 and 34 tests respectively.
- The workflow's automatic failure-log push for 38225233884 was rejected due to a concurrent branch update; this manual entry restores the visible error record. No configuration rows were scored by that failed v3 attempt.

## 2026-10-12 08:50 UTC — E109-S13 — Preserve engine-specific result artifacts

- Before v3 scoring, found that versioned progress would write the first v3 shard to the same filename as the prior v2 shard. That risks overwriting diagnostic evidence even though the engine-version cursor resets.
- Added an engine-tagged shard filename (phase109_eval_v3_context_coverage_...csv.gz) and an automated test; v2 and v3 outputs now use distinct names.
- Latest regression test [38226082378](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226082378) passed. No conclusion about profitability follows from file naming or test success.

## 2026-10-12 08:59 UTC — E109-S14 — Weekday-only option archive probes omitted observed special sessions

- The repaired index history exposed five observed NIFTY 50 sessions without an option archive: 2023-11-12, 2024-01-20, 2024-05-18, 2025-02-01 and 2026-02-01. They were absent from the request table because archive discovery enumerated weekdays only.
- Corrected by using the observed NIFTY 50 session calendar as an additional acquisition list. Any unavailability remains an explicit gap, not synthetic option data.
- Added runtime v4 reconciliation validation. Unattempted gaps fail the source gate; explicitly attempted gaps remain visible and are limited to at most max(5, ceil(1% of observed sessions)); archive dates without a corresponding index row must be zero.
- The prior v3 shard run [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004) can still finish but is diagnostic-only. Regression workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed 38 tests.

## 2026-10-12 09:03 UTC — E109-S12 — Historical context coverage recovered; old jobs remain stale

- Earlier source context had only 218 dates per series due long-window truncation; the corrected short-window query now yields 748 dates per series with zero malformed/duplicate OHLC rows and passes the 90% weekday-density threshold (711 required).
- Calendar audit still shows five observed NIFTY 50 sessions without valid option archives. They are explicit coverage exclusions, not fabricated prices. No valid option archive date lacks a NIFTY 50 observation.
- Workflow concurrency allowed an evaluator launched on an earlier source/engine checkout to remain active while v4 was queued. Such earlier jobs cannot certify v4 and their results must not be combined. The evaluator workflow checks the exact engine version and resets the cursor on mismatch.
- Updated source run [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) is active; v4 run [38227220343](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227220343) is pending. No v4 empirical checkpoint yet.

## 2026-10-12 09:04 UTC — E109-S15 — Option archive step used a potentially stale index session calendar

- Observation: the supplemental-session helper read results/phase109/niftyindices_session_calendar.csv, but the source workflow originally ran the NSE option archive backfill before refreshing that file. The source request could therefore omit newly observed special-session dates even though the later reconciliation knew about them.
- Correction: reordered the workflow so official NSE Indices context acquisition produces the current session calendar before the NSE archive probe. The date builder unions weekdays and NIFTY 50-observed dates outside Monday-Friday; unavailability remains explicit.
- Regression run [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed 38 tests. Latest corrected source job [38227481409](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227481409) is active; no special-session results are claimed until it finishes.

## 2026-10-12 09:04 UTC — E109-S16 — Obsolete Actions runs occupied branch concurrency groups

- Observation: source and evaluation runs built against earlier workflow commits held their branch concurrency slots, leaving the current special-session source refresh and v4 evaluation pending. Repeated code updates also produced superseded/cancelled pending attempts.
- Correction: enabled cancel-in-progress for the corresponding source/evaluator workflow groups so new commits replace obsolete in-flight versions. Obsolete source run [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) was cancelled, and corrected source run [38227481409](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227481409) is active.
- Caveat: the diagnostic v3 evaluator [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004) was still running at last check while the v4 evaluator run [38227487048](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227487048) remained pending. Do not claim cancellation of that evaluator until its API state changes.

## 2026-10-12 09:39 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 10:35 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 11:57 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.


## 2026-10-12 — E109-S17 — Automatic continuation dispatch returned HTTP 422

- Run [38235043545](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38235043545) successfully published cursor [4,000,6,000) and its checkpoint, then failed in `Dispatch the next shard automatically` with HTTP 422.
- The logged command builds JSON inside a single-quoted Python heredoc containing `"ref":"${GITHUB_REF_NAME}"`. Shell expansion is suppressed, so the request likely sends the literal expression instead of a valid branch ref. Fix by passing the branch through an environment variable and add a payload regression test.
- Consequence: the shard is published; resume from the committed cursor 6,000, with 166,800 supported configurations remaining. Do not rerun the completed range or mix parent-v1 results with the isolated v4 branch.
- Developer next: repair dispatch serialization, test branch routing, then resume bounded shards. Tester next: independently assert active-branch routing, 24 cost rows/config, engine-specific cursor isolation and untouched holdout.
- Status: OPEN pending fix and successful follow-on run.

## 2026-10-12 13:13 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 13:22 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 13:36 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 13:51 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 14:04 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 14:22 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 14:36 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 14:45 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 14:49 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 14:53 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 14:57 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:00 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:04 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:09 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:14 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:18 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:22 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:25 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:33 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:46 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:50 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 15:59 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:05 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:16 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:21 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:28 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:33 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:39 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:46 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 16:54 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 17:05 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 17:20 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 17:30 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 17:45 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 17:50 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 18:01 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 18:15 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 18:31 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 18:39 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.

## 2026-10-12 18:52 UTC — v2 shard audit
- Archive parse/duplicate warnings: 0; skipped reasons: {}. No raw records or secrets published. No profitability assertion from shard completion.
