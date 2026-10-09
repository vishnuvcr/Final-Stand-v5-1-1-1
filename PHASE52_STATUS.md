# Phase 52 Status — Factor-Conditioned Strategy Discovery

**Overall:** OPEN — bounded historical BASELINE pilot completed; descriptive only, no promotion; factor routers/full grid remain gated
**Branch:** phase-52-factor-conditioned-strategy-discovery  
**Plan versions:** phase52-grid-v1.3; replay protocol phase52-replay-v1.0; plan amendments PA-001 to PA-014  
**Latest checkpoint:** 2026-10-09 (Asia/Kolkata)
**Accepted finite grid:** phase52-grid-v1.3; 9,379,584 configurations (computed queue size, not tested count).

| Gate | State | Evidence / next action |
|---|---|---|
| Parent-plan/status/error-log audit | PASS | Read Phase 45 plan/status, Phase 46 plan/status, Phase 50B status, Phase 51-3 plan/status/error/chat logs and the current main README. |
| New branch | PASS | Dedicated branch exists. |
| User repository inventory | IN PROGRESS | 40 accessible repositories inventoried. Continue root-document/code search by repository; several do not expose a root README through the connected file API and require alternative-path inspection. |
| Literature/source discovery | IN PROGRESS | Initial sources include NSE India VIX/contract information, option-volume/OI literature, public GitHub strategy implementations and user-designated YouTube source tracks. Expand systematically and log each lead. |
| Candidate registry | VALIDATED / SPECIFICATION GATES OPEN | 312 hypotheses across 52 families × six selector modes pass registry checks. Four families remain specification-blocked (Calendar Trap, Iron-Condor-to-Ratio transition, conversion/reversal, futures-basis overlay); three diagnostic-only families cannot be promoted. Eleven previously blocked Phase45 named presets have now been reconciled to exact source leg maps under PA-010; registry revalidation is pending. |
| Data coverage and licensing | PARTIAL / PROMOTION BLOCKED | Run 37934719402 broad event gate remains 1,004/1,068 and holdout 74/112. Corrected selected ATM-offset audit run 37956261518 scanned all 267 option files with zero source errors: 27,768 offset/type rows; 10,552 pass prior-bar OI≥100; 10,501 also have valid exact entry OHLC; 10,405 additionally have exact-index and valid expiry-exit support. Corrected ABS_DELTA diagnostic run 37956675818 audited 4,272 target-delta/type rows with zero source errors: 3,892 pass prior OI, only 2,232 selected contracts have valid exact entry bars. These are coverage-only counts; no P&L. Index bars still end 2026-07-02; CC BY-NC source license blocks commercial promotion. |
| Finite-grid enumeration | IN PROGRESS — QUEUE ONLY | Grid v1.3 has 9,379,584 configurations. Run 37954806932 advanced the checkpoint to offset 360,000; emitted records are ENUMERATED_NOT_BACKTESTED, not P&L tests. Any replay must have its own offset-0 ledger and cost outputs. |
| Base-geometry replay | COMPLETE / DIAGNOSTIC ONLY | Pinned Phase43/45 replay: 9,699 rows, 42 strategy labels, 256 expiry events through 2026-05-26. It is not the 9,379,584-config variable replay, and the source window is partial. Empty Phase45 error file is now correctly recorded as zero rows. |
| Legacy factor-selector pilot | VALIDATION-ONLY COMPLETE — NO PROMOTION | Run 37927040268 passed end-to-end: 6,617/9,699 rows matched (68.2%); all six policies lost on validation, VIX router Holm p=0.985; 2026 holdout not evaluated (13 matched expiries). |
| Untouched OOS confirmation | NOT STARTED | Keep confirmation intervals protected before selection freeze. |
| Promotion / live readiness | NOT STARTED | No strategy is promoted or approved for live execution. |
| Manuscript and supplements | NOT STARTED | Produce after evidence and inference gates are complete. |
| Recurring automation | ACTIVE | Main workflow is manual + daily. Legacy/UDiFF+IDF parser tests pass; source audit and EOD adapter are corrected; factor-selector results remain no-promotion. Corrected ATM-offset audit passed in run 37956261518 under PA-011/013, and prior-bar ABS_DELTA audit passed in run 37956675818 under PA-012/013; both include runtime source/protocol hashes, zero source-file errors, and no P&L. Synthetic exact-bar/fill/cost kernel tests passed in run 37957753452. Full config-grid P&L remains blocked pending data-backed runner integration; synthetic whole-position integration is now PASS (run 37960484240). |

## Existing evidence carried forward (not Phase 52 evidence)

- Phase 45 reported 20 new ready-made structures plus prior structures and finished with NO PROMOTION after multiple-testing correction.
- Phase 46 registered YouTube/public-source strategy hypotheses, including long-volatility expansion versus post-spike reversal hypotheses; it did not run numerical backtests.
- Phase 51-3 partial-OOS replay was source-audited and complete only through 2026-07-21. TT-04 and TT-05 were descriptive positive candidates under its short-window cost scenarios; no promotion or confirmatory test occurred.
- The preregistered Phase 51 complete OOS window remains 2026-04-21 through 2026-08-04, and option data for 2026-07-28 and 2026-08-04 remains unresolved. No result from a shortened/missing window may be represented as full-window confirmation.

## Acceptance rules

A green workflow alone is not a scientific pass. Every numerical result needs a source manifest, candidate/configuration identity, quote and trade coverage, zero unresolved data errors, complete costs, reproducible artifacts and the applicable pre-registered statistical gates.

## Latest action

Fixed-template replay and EOD selector diagnostics exist, but the 9,379,584-config grid has not been backtested. No strategy is promoted. The exact timestamp audit proves the fixed-template replay is partial. A new event inventory for DTE={0,7} and entry times={09:45,13:00} is being generated on run 37934339579, with explicit missing-index timestamps and no P&L. The full protocol is `PHASE52_REPLAY_PROTOCOL.md`. Broad event/option coverage is 1,004/1,068 (94.0%), below the 95% promotion gate; holdout strict broad coverage is only 74/112 (66.1%). No Phase52 grid P&L has been computed.


## Bootstrap additions — 2026-10-09

- Registered 52 explicit strategy-family rows in `research/phase52/strategy_specifications.csv`; ambiguous native presets remain blocked for replay until source code/leg geometry is reconciled.
- Frozen finite grid version `phase52-grid-v1.3`; cost/stress scenarios are a per-configuration evaluation output, not an optimizable axis.
- Added deterministic Cartesian configuration enumerator and registry/specification audit. It does not calculate strategy P&L.
- Added recurring/manual discovery runner for public Hugging Face/GitHub catalogs and YouTube when `YOUTUBE_API_KEY` is configured.
- **Current gate:** source discovery + configuration queue bootstrap. Source-faithful numerical replay is still NOT STARTED; all 312 hypotheses remain REGISTERED_NOT_TESTED.


## 2026-10-09 — Gate failure recorded

First automatic workflow run 37924369419 failed in registry validation after its deterministic enumerator self-test passed. The strategy specification CSV had a data-row/header column mismatch. Corrected all 52 rows and hardened the validator. No numerical replay ran; no strategy has a profitability result. Next action is rerunning the workflow gate.

## Automated checkpoint — 2026-10-09 17:07:23 IST
- Workflow run: 37924369419
- Source leads newly recorded: 32.
- Configurations enumerated in this run: 10,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Numerical replay/data gate: OPEN / NOT PASSED. No strategy is promoted.


## Latest verified automation checkpoint — 2026-10-09

- GitHub Actions run [37924369419](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37924369419) was retried after the CSV schema fix.
- Deterministic Cartesian unranking self-test: PASS.
- Registry/specification/grid audit: PASS; 312 unique hypotheses, 52 structure families and 6 selector modes.
- Source discovery: PASS for 10 Hugging Face and GitHub searches; 32 unique source leads recorded. Fresh YouTube search was skipped because `YOUTUBE_API_KEY` is not configured. The existing Phase 46 video ledger is retained; a full-channel crawl is not claimed.
- Finite grid: `phase52-grid-v1.3`; 9,379,584 configurations total. First shard enumerated 10,000 records (offsets 0–9,999); checkpoint next offset 10,000.
- **Critical boundary:** all 10,000 are queued/enumerated configurations, not backtests. No P&L, factor uplift, profitability, drawdown or strategy ranking has been computed in Phase 52.
- Next gate: source/contract coverage and licensing, point-in-time data availability, and exact leg/transition reconciliation for blocked families. Numerical replay is not yet implemented or run.


## Current automation and pilot state — 2026-10-09

- Registry/grid validation PASSED on run 37925891660: 312 hypotheses, 52 families, six selector modes, and 15 structure variants requiring source-spec reconciliation.
- The deterministic queue has 9,379,584 finite configurations in grid v1.3; the prior checkpoint was at 10,000 enumerated combinations under the previous workflow version. The current scheduled runner aims at 25,000 configurations per run. None of these enumeration counts represent completed replay results.
- The first factor-selector pilot checked out the Phase45 legacy trade matrix and Phase39 feature panel, installed pandas/numpy, then failed at the self-test on a quantile-bin boundary assumption. The data analysis did not run. The test now uses fixed values away from the threshold boundaries. Waiting for automatic workflow rerun.
- **Research result status:** no Phase52 factor-selection profitability or uplift result has yet been accepted. Legacy risk-limited template outcomes will be tested after the self-test passes and the as-of join reaches at least 90% coverage. Futures basis, true synthetic-future divergence, timestamped news and corporate actions remain data-gated.


## Coverage gate revision — PA-004 (2026-10-09)

- Workflow run 37926165354 passed selector self-tests but reported 68.2% as-of feature match overall. No selector metrics were calculated; the pilot stopped at the coverage gate.
- Coverage does not imply an incorrect price or failed strategy. The legacy outcome matrix contains expiry sessions for which the Phase39 option-factor panel has no same-expiry feature snapshot.
- The pilot now records coverage by development/validation/holdout; it may proceed only when each split is at least 50% matched and validation/holdout have at least 20 matched expiry sessions. Every reported comparison uses the same matched expiry keys for selector and baseline, and there is no imputation. Otherwise a coverage-only report is written without factor P&L.
- This is a documented exploratory matched-sample protocol, not a claim of full feature coverage. Futures/synthetic-futures remain untested until source data exist.


## PA-005 — holdout coverage policy

The existing Phase39 feature file ends on 2026-04-24; Phase45 outcome rows extend through 2026-09-30. Therefore the 2026 holdout is not assumed to meet the 20-expiry/50% factor-feature coverage rule. The revised pilot can publish matched-sample development-tuning and 2024–25 validation comparisons only if those splits meet their gates; undercovered 2026 holdout is explicitly unevaluated, never imputed. A strategy still cannot be promoted without adequate untouched OOS confirmation.

## Automated checkpoint — 2026-10-09 17:28:57 IST
- Workflow run: 37927040268
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.


## Latest verified checkpoint — 2026-10-09, run 37927040268

- **Workflow:** [37927040268](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37927040268) completed successfully. Registry validation, selector pilot self-test, source discovery, finite-grid checkpoint, status/log append and branch persistence all passed.
- **Source-feature leakage audit:** PASS. Existing point-in-time rules prohibit option-chain timestamp mismatch, interpolation, forward fill and use of control-direction/outcome fields as features.
- **Legacy selector pilot input:** 9,699 Phase45 outcome rows; 477 Phase39 feature snapshots; 6,617 rows matched point-in-time to a same-expiry feature record (68.22%). Matched coverage: development 76.63%/102 expiries; validation 58.47%/60 expiries; 2026 holdout 61.90%/13 expiries.
- **Validation-only conclusion:** All six selected factor policies had negative total validation net P&L. The VIX router was least bad with net `-₹63,547` and legacy 1.5× all-cost stress `-₹64,634`; paired mean stress-uplift versus the fixed baseline was `+₹1,411/expiry`, 95% block-bootstrap CI `[-₹915, +₹4,290]`, one-sided p `0.1642`, Holm-adjusted p `0.9850`. Its uplift is not statistically significant; its total net remains negative. Other policies also failed to outperform the baseline with adjusted significance.
- **2026 holdout:** Not evaluated. Only 13 expiry sessions have matched legacy feature snapshots, below the preregistered 20-expiry threshold. No holdout or confirmation claim.
- **Interpretation:** This is an exploratory legacy-outcome selector screen, not a test of all 312 hypotheses or the 9,379,584 registered variable configurations. No candidate is promoted.
- **Next gate:** implement the source-faithful variable-configuration replay engine. The finite queue advances from offset 35,000 to 60,000 in this run; its records are still enumeration, not backtests.
- **Known limits:** current seed factor panel includes VIX, IV/Greeks, OI/PCR, spot, global-market and sentiment proxies, but it does not supply verified intraday traded-futures basis or a true synthetic-futures lead/lag panel. Current 2026 RISSIN intraday OI is not available for OI-based replay; legacy HF data license is CC BY-NC 4.0 and is research-only pending rights review.

## Automated checkpoint — 2026-10-09 17:51:46 IST
- Workflow run: 37928216137
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.

## Automated checkpoint — 2026-10-09 17:58:30 IST
- Workflow run: 37929888516
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.


## 2026-10-09 — Base replay + daily source coverage checkpoint

- **Successful workflow:** [37929888516](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929888516).
- **Pinned replay:** option dataset revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`; 9,699 rows across 42 strategies and 256 expiries, 2021-06-03 to 2026-05-26. This is fixed geometry, not all Phase52 parameter-grid combinations. Source licence is CC BY-NC 4.0; research-only pending rights review.
- **Daily EOD supplement:** 256/256 event rows have a strictly prior-session factor row; 512 archive sessions were processed with zero missing archive paths, file errors, or feature gaps. It is daily EOD OI/volume and front-future basis, not intraday futures basis or a substitute for missing one-minute option data. Factor-level non-null coverage and the patched contract-matched futures-OI change metric will be refreshed on rerun with cached archives.
- **Coverage audit attempt:** run [37930010915](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37930010915) failed before it could emit a coverage conclusion because `research/phase52/expiry_coverage_audit.py` existed on main but was missing from the checked-out research branch. That script has now been copied to this branch (commit `43e8ae1a9a4c5acf5c6be4c0f4a83bb74455f50b`). No coverage numbers are accepted from that failed run.
- **Strategy decision:** reproduced LOW-VIX Bear Call Spread validation net ₹24,743, legacy 1.5× all-cost net ₹23,082. Phase45's multiple-testing decision remains zero Holm-adjusted statistical survivors; no promotion.
- **Next gate:** rerun exact-10:00 entry-spot coverage audit and inspect daily factor-level coverage before any factor-selector or parameter replay.

## Automated checkpoint — 2026-10-09 18:08:24 IST
- Workflow run: 37931097834
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.

## Automated checkpoint — 2026-10-09 18:10:17 IST
- Workflow run: 37931305395
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.

## Automated checkpoint — 2026-10-09 18:20:49 IST
- Workflow run: 37932492241
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.

## Automated checkpoint — 2026-10-09 18:23:31 IST
- Workflow run: 37932520478
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.


## Verified selector/source checkpoint — 2026-10-09

- EOD selector run [37932492241](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37932492241) completed with 256 matched base events and eight EOD modes. Best validation relative uplift diagnostic was volume-PCR +₹923/event, 95% block-bootstrap interval [-₹1,454,+₹3,436], Holm p=1.000; no selector is promoted. Holdout is unstable and several modes lose materially.
- UDiFF `IDF` index-futures parsing is corrected and regression-tested. The corrected EOD manifest reports basis and futures OI available on 256/256 events, with same-contract futures OI change available on 255/256; this is lagged daily EOD only, not intraday traded-futures basis.
- Replay protocol v1.0 and plan amendment PA-007 have been committed before configuration-grid P&L. Grid v1.3 domains were not changed.
- Workflow [37934339579](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934339579) is running the new event universe: 267 expiry files × two DTE values × two exact entry times = 1,068 expected date/time events. This inventory checks exact index timestamps only; it does not count option-leg quotes as valid until each configuration's selected strikes are checked.

## Automated checkpoint — 2026-10-09 18:49:09 IST
- Workflow run: 37934719402
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.


## Configuration-grid coverage gate — 2026-10-09 (verified)

- **Run:** [37934719402](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934719402), success.
- **Pinned source:** `thetrademarkk/india-index-options-1m`, revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`; 267 target-expiry files.
- **Expected events:** 1,068 = 267 expiries × DTE {0,7} × entry times {09:45,13:00}. Index has exact entry timestamp for 1,012; 56 missing.
- **Option files:** 267/267 audited, zero file errors. Option data has some row at exact entry for 1,016 events and at least one OI≥100 contract for 1,012. Strict intersection with exact index entry is 1,006; adding target-expiry exit bar gives 1,004/1,068 (94.0%).
- **Split gate:** strict broad coverage is development 526/540 (97.4%), validation 404/416 (97.1%), holdout 74/112 (66.1%). Holdout fails both the 95% coverage gate and the minimum 20-event holdout gate after exclusions.
- **Data warning:** The source index/option history ends 2026-07-02 even though expiry files have names through 2026-08-04. The files labeled 2026-07-28 and 2026-08-04 contain no target entry-day quotes. No silent date rolling or interpolation allowed.
- **Meaning:** These are event/broad-contract-universe counts, not per-configuration selected-leg fills or P&L. Variable grid replay is not yet run.
- **Cost amendment:** PA-008 sets ₹20/order primary and ₹10/order legacy sensitivity; no parameter grid dimensions changed.


## Configuration-wide broad option/OI audit — 2026-10-09

- Run: [37934719402](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934719402), success.
- Frozen input: `thetrademarkk/india-index-options-1m` revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`; 267 expiry files, no source file read errors.
- Expected events: 1,068 = 267 target expiries × DTE calendar days {0,7} × exact entry times {09:45,13:00}. All 1,068 received an audit row.
- Broad coverage counts: exact index entry=1,012; any option rows at exact entry=1,016; both CE and PE present=1,016; any contract with OI≥100=1,012; any 15:15 same-day exit rows=1,016; target-expiry exit with both option types at a common timestamp=1,040.
- Conservative intersections: exact index + entry option rows + OI≥100 = 1,006/1,068; additionally requiring broad expiry exit = 1,004/1,068. These are broad event gates, not proof that each chosen strike/leg has valid entry and exit OHLC.
- Split: development 526/540 pass exact-index + entry-option + OI gate; validation 404/416; holdout 76/112. With broad target-expiry exit additionally required: 526/540, 404/416, and 74/112 respectively.
- Holdout limitation: pinned index bars end 2026-07-02; source expiry labels run through 2026-08-04, but recent expiry files do not imply complete recent index/option coverage. The July 28/Aug 4 sessions remain unresolved.
- No P&L was calculated. Next mandatory gate: per-configuration selected-strike/leg OHLC eligibility and executable fill pricing; do not use the broad event counts as the replay sample size.


## Selected-strike audit implementation — pending validation

- Added `research/phase52/selected_strike_coverage_audit.py` to the branch and wired it into the scheduled/manual workflow.
- Scope: for each of the 1,068 registered events, resolve nearest listed ATM strike and audit offsets -6 through +6 for both CE and PE, using exact entry timestamps, OHLC consistency, OI≥100, exact 15:15 bars and common-time expiry exits. Outputs are coverage diagnostics only; no P&L.
- A code-path optimization indexes rows by exact timestamp to avoid repeatedly scanning full expiry files. Self-test and end-to-end run are pending the queued Actions execution.
- ABS_DELTA configurations are explicitly blocked. Minute option close alone is not treated as a validated delta; a point-in-time IV/Greeks resolver and its own tests are required before those configurations can replay.

- **Pre-run self-audit:** Found and patched a timestamp string-key mismatch in the new selected-strike audit before accepting any result. F52-023 logs the defect; self-test/full audit remain pending.
## Automated checkpoint — 2026-10-09 18:59:45 IST
- Workflow run: 37935663113
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.

- **Point-in-time strike ladder review:** Found and patched a pre-run issue where strike ranks were sourced from the entire expiry file rather than contracts listed at the exact entry timestamp. Logged as F52-026. Any result from a workflow that checked out the earlier script draft is not accepted; a patched-commit run is required.

- **Persistence regression:** Run 37935663113 completed successfully with the revised fetch/rebase/push logic, confirming the append-only status/log conflict path can persist checkpoints. New selected-strike audit results remain pending; runs 37936777969 and 37937164472 are active on earlier workflow/code snapshots, while 37937318538 is queued for the latest point-in-time strike-ladder correction.

- **Stale-result protection:** Workflow persistence now checks whether the selected-strike audit source changed after checkout; stale selected-strike outputs are discarded/restored instead of overwriting corrected evidence. Verification is pending the next run.

- **Stale-output pathspec self-audit:** Added a .gitkeep placeholder after discarding stale outputs so the workflow's later git-add step cannot fail merely because the directory is empty; F52-028 records this. End-to-end verification remains pending.

- **Latest queue checkpoint:** 260,000/9,379,584 deterministic configuration IDs enumerated (run 37935663113); still zero configurations backtested by this queue.

- **PA-010 source reconciliation:** 11 named Phase45 presets now have exact leg maps recorded in the spec CSV and are no longer blocked on source ambiguity. This is a specification correction only; registry validation must pass before replay.

- **Stale registry protection:** The workflow now checks the specification CSV revision before persisting registry_audit.json and preserves the remote audit if an older run used the pre-PA-010 file. Verification is pending.

- **First selected-strike run:** The selected-strike step in run 37937164472 completed at the process level, but it used the pre-correction strike ladder and is explicitly NOT ACCEPTED. The persistence guard and queued run 37938099763 are intended to enforce the corrected point-in-time source and PA-010 registry.

- **Concurrent persistence correction:** Run 37937164472 completed audit steps but failed while persisting overlapping generated artifacts. The workflow is back on one shared concurrency group; generated-result conflicts now preserve the remote version while append-only logs are merged, and source/code conflicts still fail closed. Verification pending.
## Automated checkpoint — 2026-10-09 19:14:09 IST
- Workflow run: 37936777969
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.

## Automated checkpoint — 2026-10-09 19:23:43 IST
- Workflow run: 37938433270
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.

## Automated checkpoint — 2026-10-09 19:52:13 IST
- Workflow run: 37942202655
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Selected ATM-offset audit: SELECTED_STRIKE_ATM_OFFSET_COVERAGE_AUDIT_COMPLETE; 27,768 leg-event rows; strict exact-index/OI/expiry-exit rows=11,108; no P&L.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.


## Audit-implementation correction — PA-011/PA-012 (2026-10-09)

- **ATM-offset audit:** Previous counts generated by run 37942202655 are superseded. Its coverage-only script mapped `atm_offset_steps` to rank positions among available strikes and used the index close at the entry timestamp. The corrected code uses exact-time index open, modal strike step from the exact-time option snapshot, and exact `ATM + offset × step` targets. Rerun required.
- **ABS_DELTA audit:** Run [37944408314](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37944408314) failed at self-test before reading market data. Corrected `sigma=0.18` and the negative IV fixture. The resolver now selects only from the exact `entry_ts − 1 minute` option/index closes and predecision OI; entry bar open is separately checked. Rerun required.
- **No parameter-grid changes:** v1.3 domains and IDs remain frozen. The corrected audits contain no strategy P&L and cannot by themselves promote or reject a strategy.
- **Next gate:** successful selected ATM-offset audit, successful point-in-time IV/delta audit, then a small generic single-/multi-leg fill engine test with hand-calculated fixtures before the 9.38M config queue is allowed to produce P&L.


## PA-013 — prior-bar OI gate correction (2026-10-09)

- A further audit found that the ATM-offset screen used current entry-bar OI to gate a trade simulated at that same bar's open. This timing is not accepted.
- The selected-strike script now requires OI>=100 at exact entry_ts minus one minute, along with a unique OHLC-valid exact entry-time contract bar. Current-bar OI is diagnostics only.
- The current factor workflow run 37954806932 checked out the earlier PA-011/PA-012 commit before PA-013 and is not an acceptance run for the final selected-strike audit. Its broad option event scan remains separable from this selected-leg change; any old selected-strike output from it is stale.
- Delta resolver workflow 37954839508 is queued behind the factor workflow; it will check out the corrected prior-bar code when its job starts.
- No P&L has been calculated and no v1.3 grid domain/ID changed. Fresh selected-strike and delta audit results remain mandatory.
## Automated checkpoint — 2026-10-09 21:34:23 IST
- Workflow run: 37954806932
- Source leads newly recorded: 0.
- Configurations enumerated in this run: 25,000 of 9,379,584 finite-grid combinations. This is queue enumeration only, not strategy testing.
- Selected ATM-offset audit: SELECTED_STRIKE_ATM_OFFSET_COVERAGE_AUDIT_COMPLETE; 27,768 leg-event rows; strict exact-index/OI/expiry-exit rows=11,109; no P&L.
- Daily EOD factor-selector: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; validation diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; report at results/phase52/daily_eod_selector/REPORT.md.
- Legacy factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION (PIT match 68.2%); report at research/phase52/results/factor_attribution/REPORT.md.


## Focused selected-strike audit — run 37956261518 (2026-10-09T16:11:45.775659+00:00)
- Source revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Audit source SHA256: 49f0b09b3fd61b102bcc232686c842d6fd22534b6d1207d10a017befb1322f55
- Protocol SHA256: f3e910a064cc7af18885617f9e4c25cf5ef901c491a6f40ffd124808cb71e6f6
- Expected/audited events: 1068/1068
- Expiry files audited/errors: 267/0
- OI eligible prior-bar rows: 10552
- Entry-bar valid AND prior-OI-eligible rows: 10501
- Exact-index + entry-open + prior-OI eligible rows: 10501
- This is coverage only; no P&L or strategy promotion.


## Point-in-time delta audit — run 37956675818 (2026-10-09T16:14:15.196036+00:00)
- Status: MODEL_DELTA_AUDIT_COMPLETE
- Dataset revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Audit source SHA256: 9d343d1f53338a6fe5741ba8c0d560a8ebfe783a2565c860f6873235a61b4ce3
- Replay protocol SHA256: f3e910a064cc7af18885617f9e4c25cf5ef901c491a6f40ffd124808cb71e6f6
- Expiry files audited/errors: 267/0
- Expected/actual selection rows: 4272/4272
- Rows with prior-OI-qualified selections: 3892
- Exact entry fill bars available: 2232
- Model delta is diagnostic only; no P&L or promotion.


## Verified selected-strike, model-delta and replay-kernel checkpoint — 2026-10-09

- **ATM_OFFSET:** run [37956261518](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956261518) completed successfully with the corrected PA-011/PA-013 code. Source and protocol fingerprints are in `results/phase52/selected_strike_coverage/summary.json`. Of 27,768 offset/type rows, 10,552 passed prior-bar OI≥100, 10,501 also had valid exact entry OHLC, 10,405 also had exact-index and target-expiry exit support. These are offset/type audit rows, not trades or P&L.
- **ABS_DELTA:** run [37956675818](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956675818) completed successfully with prior-completed-minute inputs and code/protocol fingerprints. All 4,272 expected delta/type checks across 267 expiry files were emitted; 232 lacked an exact prior minute, 148 had no prior-OI-qualified candidate, 3,892 passed the prior-OI gate, and only 2,232 had valid exact entry fill bars. Black–Scholes outputs are model Greeks only. This selector remains ineligible for P&L until the end-to-end resolver consumes these exact gates and reports excluded rows.
- **Replay kernel:** run [37957753452](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957753452) passed synthetic golden tests for exact bars, common timestamps, prior-bar OI, fill price/slippage, six cost scenarios, liquidity-range proxy, next-open TP and fail-closed gates. First run [37957499754](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957499754) passed the test but failed writing the evidence manifest to an unexpanded `$RUNNER_TEMP` path; fixed and verified.
- **Current decision:** no strategy promotion. No Phase52 variable-grid configuration has yet been backtested. The next stage is strategy-template parsing/family resolution and integration testing before first real-data configuration shard.


## Latest verified checkpoint — 2026-10-09 22:38 IST

- **Template resolver tests:** [run 37959442745](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37959442745) passed source-binding and synthetic exact-chain checks for all 52 family rows: 45 option-only templates resolvable and 7 explicitly blocked, with zero historical market data or P&L used.
- **Replay kernel / fee parity:** [run 37958266044](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37958266044) passed canonical exact-bar, prior-OI, common-exit, hand-calculated fill, six brokerage/slippage scenario and Phase43 fee-parity fixtures. The one-leg hand calculation gives ₹1,618.50 after adverse slippage before fees; the two-leg vertical gives ₹3,172.00 after slippage before fees.
- **Reference lots:** code review found `reference_lots_per_leg` was recorded but not multiplied into resolved quantities after optional ratio overrides. Corrected before any historical configuration P&L, with tests for both ratio×reference-lot scaling and native 1:2:1 butterfly scaling.
- **Synthetic whole-position integration:** [run 37960484240](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960484240) passed end-to-end resolution and costed replay on synthetic exact bars for all 45 supported option-only templates (45 positions × six cost scenarios = 270 synthetic scenario rows). It also passed missing-entry, low-prior-OI, missing-exit, no-common-time, ratio/lot-scaling and date-aware cost controls. The all-position output flags no historical P&L and no candidate is promotable.
- **Test-harness correction:** initial whole-position run [37960340815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960340815) failed because the base butterfly fixture accidentally overrode the native leg ratio with `[1,1]`; the fixture was corrected and [rerun 37960484240](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960484240) passed. The failed run is retained in the error log.
- **Grid:** v1.3 remains 9,379,584 finite configurations; 360,000 have been enumerated, and zero historical Phase52 grid configurations have been backtested. Queue enumeration is not strategy evidence.
- **Data / rights gates:** pinned intraday index history ends 2026-07-02, the 2026-07-28 and 2026-08-04 sessions remain unresolved, and the primary historical options data is CC BY-NC 4.0. Results are research-only; no commercial/live-readiness conclusion is allowed.
- **Next:** implement a data-backed limited runner and exact configuration-specific strike/exit/cost manifest. Do not launch the finite grid until non-supported selectors and exits fail closed, option legs have exact coverage, and runner/inference artifacts are reproducible.

## Bounded historical pilot checkpoint

- **Run:** [37962192723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37962192723); job=failure; self-test=success; plan-only=success; replay=failure.
- **Frozen pilot preflight only:** configs=40; events=24; planned config-event rows=480; historical replay report missing.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.

## Bounded historical pilot checkpoint

- **Run:** [37962948690](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37962948690); job=success; self-test=success; plan-only=success; replay=success.
- **Pilot result status:** HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS; configs=40; planned config-event rows=480; executed=1; excluded/errors=479; cost rows=6; source file errors=0.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.


## PA-015 — 2026-10-10 — Exact duplicate row normalization for the historical pilot

- The v0.1 pilot executed 1 of 480 planned config-event rows; 274 were blocked by duplicate exact contract bars and 205 failed the preregistered 2% high-low/open proxy gate.
- Change: v0.2 removes only rows identical across all columns after canonical timestamp/type/numeric normalization. Conflicting rows with the same contract key are not averaged or arbitrarily selected; they remain blocked. The frozen 40 configurations, 24 events, splits, costs and OHLC proxy threshold are unchanged.
- Interpretation: this is a source-normalization/coverage engineering rerun, not a performance retest. The 2% high-low/open test is an OHLC-range proxy, not an observed bid/ask spread; it remains a conservative data-quality exclusion and cannot establish executable liquidity.
- The v0.1 report is preserved. v0.2 must report per-file original normalized row counts, exact duplicate rows removed, conflicts remaining, and complete 480-row status reconciliation before it can pass.


## Pilot v0.2 execution in progress — 2026-10-10 IST

- Workflow run: [37980455805](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805).
- Self-test passed, including exact full-row duplicate normalization fixture and preservation of conflicting same-key rows.
- Frozen config/event planning passed: 40 configurations, 24 events, 480 planned config-event rows; no holdout events.
- Historical replay step is still in progress at last status check. No v0.2 output has been accepted yet. Preserve v0.1 output and do not infer profitability until report, hashes, costs and full 480-row reconciliation are verified.
