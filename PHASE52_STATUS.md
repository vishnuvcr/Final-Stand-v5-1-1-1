# Phase 52 Status — Factor-Conditioned Strategy Discovery

**Overall:** OPEN — base replay and EOD factor build complete; exact intraday coverage audit rerun pending  
**Branch:** phase-52-factor-conditioned-strategy-discovery  
**Plan version:** 1.3 (pre-test amendments PA-001 to PA-003)  
**Latest checkpoint:** 2026-10-09 (Asia/Kolkata)
**Accepted finite grid:** phase52-grid-v1.3; 9,379,584 configurations (computed queue size, not tested count).

| Gate | State | Evidence / next action |
|---|---|---|
| Parent-plan/status/error-log audit | PASS | Read Phase 45 plan/status, Phase 46 plan/status, Phase 50B status, Phase 51-3 plan/status/error/chat logs and the current main README. |
| New branch | PASS | Dedicated branch exists. |
| User repository inventory | IN PROGRESS | 40 accessible repositories inventoried. Continue root-document/code search by repository; several do not expose a root README through the connected file API and require alternative-path inspection. |
| Literature/source discovery | IN PROGRESS | Initial sources include NSE India VIX/contract information, option-volume/OI literature, public GitHub strategy implementations and user-designated YouTube source tracks. Expand systematically and log each lead. |
| Candidate registry | IN PROGRESS | 312 unique structure × selector hypothesis IDs: 52 families × 6 selector modes (not 300 claimed structural families); validate IDs, source lineage and risk tags. |
| Data coverage and licensing | PARTIAL / REVIEW GATES OPEN | Base replay is complete only through expiry 2026-05-26 from the pinned CC BY-NC dataset; exact timestamp coverage audit is being rerun. Lagged daily EOD factor panel has 256/256 event rows and 0 archive path/file errors, but it is not intraday basis and NSE data rights still require review. |
| Finite-grid enumeration | IN PROGRESS | Grid v1.3 has 9,379,584 configurations; 25,000 per day implies about 376 enumeration runs. Enumeration is not replay. |
| Base-geometry replay | COMPLETE / DIAGNOSTIC ONLY | Existing Phase43/45 engines replayed at HF revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`; 9,699 rows, 42 strategy labels, 256 expiries. This is not the 9,379,584-config variable replay. The full source expiry window is not yet reconciled. |
| Legacy factor-selector pilot | VALIDATION-ONLY COMPLETE — NO PROMOTION | Run 37927040268 passed end-to-end: 6,617/9,699 rows matched (68.2%); all six policies lost on validation, VIX router Holm p=0.985; 2026 holdout not evaluated (13 matched expiries). |
| Untouched OOS confirmation | NOT STARTED | Keep confirmation intervals protected before selection freeze. |
| Promotion / live readiness | NOT STARTED | No strategy is promoted or approved for live execution. |
| Manuscript and supplements | NOT STARTED | Produce after evidence and inference gates are complete. |
| Recurring automation | ACTIVE / REPAIR CYCLE | Main branch workflow is manual + daily. Parser fixtures now pass for legacy and UDiFF schemas; run 37929888516 built the EOD factor panel. Coverage run 37930010915 stopped because the audit script was absent from the branch checkout; copied in commit `43e8ae1a9a4c5acf5c6be4c0f4a83bb74455f50b`; rerun pending. |

## Existing evidence carried forward (not Phase 52 evidence)

- Phase 45 reported 20 new ready-made structures plus prior structures and finished with NO PROMOTION after multiple-testing correction.
- Phase 46 registered YouTube/public-source strategy hypotheses, including long-volatility expansion versus post-spike reversal hypotheses; it did not run numerical backtests.
- Phase 51-3 partial-OOS replay was source-audited and complete only through 2026-07-21. TT-04 and TT-05 were descriptive positive candidates under its short-window cost scenarios; no promotion or confirmatory test occurred.
- The preregistered Phase 51 complete OOS window remains 2026-04-21 through 2026-08-04, and option data for 2026-07-28 and 2026-08-04 remains unresolved. No result from a shortened/missing window may be represented as full-window confirmation.

## Acceptance rules

A green workflow alone is not a scientific pass. Every numerical result needs a source manifest, candidate/configuration identity, quote and trade coverage, zero unresolved data errors, complete costs, reproducible artifacts and the applicable pre-registered statistical gates.

## Latest action

New phase branch created; plan version 1.0 and its seed logs are being committed. No numerical Phase 52 P&L has been calculated yet.


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
