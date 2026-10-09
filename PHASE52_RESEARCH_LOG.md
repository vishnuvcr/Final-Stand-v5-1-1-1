# Phase 52 Research Log

Append every completed research step, regardless of outcome. Preserve source refs, commit/workflow IDs, input fingerprint, outputs, exclusions and next gate. Never rewrite history; corrections append a new entry referencing the superseded entry.

## 2026-10-09 — Step 0.1: Parent research audit

- **Completed:** Read Phase 45 research plan and status; Phase 46 research plan/status/chat log; Phase 50B status; Phase 51-3 research plan/status/error log/chat log/report; current main README latest Phase 51 checkpoints.
- **Finding:** Phases 45–46 covered ready-made structures and YouTube discovery, but Phase 45's final decision was no promotion; Phase 46 was discovery-only. Phase 51-3 gives descriptive positive results for TT-04/TT-05 only on a partial window through 2026-07-21.
- **Data limitation preserved:** 2026-07-28 and 2026-08-04 option records remain missing; no full-window claim.
- **Decision:** Create a separate factor-conditioned selector study instead of repeating the old VIX-only sweep.

## 2026-10-09 — Step 0.2: GitHub account repository inventory

- **Completed:** Connected account inventory returned 40 user repositories, including Final Stand versions, Daily-Options, Iron_condor, Iron-condor-to-ratio v1/v2, Option-intraday-v1, Naked-option-v1, Nifty, Timesfm-trading, MC option verification projects and general market/ML strategy projects.
- **Finding:** Several high-priority README docs expose strategy rules and prior negative/positive results; some root README fetches returned 404 and cannot be deemed complete audits.
- **Decision:** Registry lineage includes explicit links to the user's strategy repositories; maintain a per-repository audit status rather than claiming all source paths were read.

## 2026-10-09 — Step 0.3: Public literature/source scan seed

- **Sources inspected:** NSE India VIX methodology, NSE contract information, Bollen & Whaley (2004), Pan & Poteshman (2006), Gârleanu, Pedersen & Poteshman (2009), and public GitHub NIFTY option backtesting examples.
- **Finding:** Prior literature supports testing volatility surfaces and option volume/order-flow information as hypotheses, but evidence from other markets is not proof of NIFTY profitability. Public repository performance claims require independent reproduction and costs/data audits.
- **Decision:** Factor candidates will be preregistered and compared against paired controls; videos and GitHub claims remain discovery leads, not results.

## 2026-10-09 — Step 0.4: Phase 52 branch bootstrap

- **Action:** Created phase-52-factor-conditioned-strategy-discovery from main.
- **State:** No Phase 52 backtest results exist yet. The next step is to finish the 300-candidate registry, finite config domains, repository source ledger and validation/automation code.


## 2026-10-09 — Step 0.5: Candidate and configuration registry

- **Candidate matrix:** `research/phase52/strategy_registry.csv` contains 312 unique candidate hypothesis IDs (52 structure families × six selector modes: baseline, VIX, Greeks/surface, OI/flow, spot/futures/synthetic, multivariate context).
- **Structure source specs:** `research/phase52/strategy_specifications.csv` contains 52 family templates. Several native presets and transitions are flagged for exact-source reconciliation rather than guessed; they cannot enter numerical replay until resolved.
- **Configuration space:** `research/phase52/configuration_space.json`, grid `phase52-grid-v1.1`. It is a finite coarse grid, with conditional strike-selection branches and deterministic IDs. Paytm Money cost scenarios are outputs per configuration, not a tuned variable.
- **Code:** `research/phase52/validate_registry.py` includes schema validation, deterministic mixed-radix indexing and optional resumable shard emission.
- **Interpretation:** Registry and queue are not backtests; P&L, win rate, return, drawdown or factor uplift has not been calculated for Phase 52.


## 2026-10-09 — First Actions gate failure and correction

Run 37924369419: deterministic Cartesian unranking self-test passed. Registry validation then failed because the first strategy-specification CSV had a missing `family_name` column in data rows. No source-discovery or configuration-enumeration step ran. The CSV was rebuilt to six columns for all 52 rows and the validator hardened against null fields. Rerun still required; no backtest evidence was generated.

## 2026-10-09 17:07:23 IST — Automated run 37924369419

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 10,000 configurations at offsets 0–9,999.
- Source-discovery queries: 11; unique leads added: 32. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Numerical replay remains gated until explicit leg specs, point-in-time data coverage/licensing and a source-faithful replay engine pass their audits. No P&L or strategy promotion is inferred from this run.


## 2026-10-09 — Retry passed and discovery/queue bootstrap completed

- GitHub Actions run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37924369419
- The initial CSV field-alignment failure was corrected and the job retried.
- Deterministic enumeration self-test and registry/specification/grid validation passed.
- Hugging Face and GitHub search calls completed; 32 unique public source leads were added to the durable source ledger. No fresh YouTube API crawl was performed because `YOUTUBE_API_KEY` is absent.
- Grid `phase52-grid-v1.3`: 9,379,584 applicable combinations; 10,000 configuration records emitted and checkpointed for offsets 0–9,999.
- These are candidate configurations, not tested trades or backtests. The numerical replay engine/data coverage gate remains open. No strategy is promoted.


## 2026-10-09 — Step 0.6: First factor-selector workflow execution

- **Workflow:** run 37925891660; job 113804605666.
- **Passed:** Registry/spec/grid consistency validation and deterministic configuration ID self-test. Validator reported 312 hypotheses, 52 families and grid v1.3 with 9,379,584 finite configurations.
- **Blocked:** Factor-selector pilot self-test failed on strict expected quantile labels. It stopped before loading/analysing the Phase45 trade matrix. No factor or strategy performance conclusion was produced.
- **Correction:** Unit test now uses explicit edges [1.5, 2.5] so LOW/MID/HIGH labels are unambiguous and independent of quantile conventions. Root cause recorded as F52-005; automatic rerun pending.

## 2026-10-09 — Step 0.7: Configuration-space feasibility check

- **Finding:** v1.1 197,842,176 candidates, v1.2 36,008,064; current v1.3 9,379,584 configurations.
- **Decision:** Keep all combinations in current grid but use bounded 25,000-row shards. Clearly distinguish enumeration from actual replay, and do not claim full config test count until a source-faithful replay result exists.
- **Next:** pass the selector pilot unit test, validate as-of feature coverage and chronology, run validation/holdout comparisons, then integrate replay engine for the registered variable configurations.



## 2026-10-09 — Step 0.8: As-of factor-panel coverage diagnosis

- **Run:** 37926165354 (self-test passed; selector analysis stopped before metrics).
- **Observed:** 68.2% of all legacy outcome rows had a prior as-of feature record for the same expiry within 24 hours. The source feature panel is a separate 477-row panel, while the legacy matrix includes additional expiries without matched option-factor rows.
- **Decision:** Added PA-004 using only coverage metadata: matched-sample pilot, minimum 50% in each split, at least 20 matched expiries in validation/holdout, identical matched expiries for selector and baseline. Missing feature rows are never imputed.
- **Operations:** That run's branch checkpoint push failed due to a remote update after checkout. Workflow is patched to rebase before push. Its failed run and impact remain logged.
- **Next:** Rerun, inspect coverage by split, and only then determine whether the exploratory pilot has enough admissible matched observations for numerical selector analysis.


## 2026-10-09 — Step 0.9: Factor-pilot sample policy and strategy aliases

- **Source inspection:** Phase45 canonical template map uses outcome labels distinct from some human-readable family names (`iron_condor`, `iron_butterfly`, `call_calendar`, `long_call_butterfly`, `bull_call_debit`, etc.).
- **Correction:** Whitelist amended to reflect source outcome names while continuing to exclude naked/undefined-tail structures.
- **Coverage policy:** Phase39 factor panel ends on 2026-04-24 but the Phase45 matrix extends through 2026-09-30. PA-005 lets the pilot report validation-only selector metrics if its matched sample passes, while withholding holdout inference when coverage/sample is insufficient.
- **Inference:** Pilot uses circular moving-block bootstrap and block-level sign flips (block length 3 consecutive expiry observations) to account for short-range serial dependence. Results remain exploratory and subject to Holm correction across preregistered router families.

## 2026-10-09 17:28:57 IST — Automated run 37927040268

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 35,000–59,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep; futures/synthetic basis remains unavailable in its seed panel. No Phase52 candidate is promoted.\n

## 2026-10-09 — Step 0.9: Legacy selector pilot completed with validation-only evidence

- **Authoritative run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37927040268 (successful end-to-end).
- **Inputs:** 9,699 frozen Phase45 strategy outcomes and 477 point-in-time Phase39 feature rows; feature leakage audit status PASS. Joined 6,617 outcomes (68.22%) without interpolation/forward-fill. Matched expiries: development 102; validation 60; 2026 holdout 13.
- **Development fit/tuning:** training ended 2023-02-17; tuning began 2023-02-24. Selected features: VIX = India_VIX_state; Greeks/surface = atm_pe_iv; OI/flow = near_atm_oi_pcr; spot = nifty_ma_gap_15m; multivariate = TREND_X_IV_SKEW; global/sentiment proxy = global_NASDAQ_ret1.
- **Validation results:** all policies net negative. VIX router net -₹63,547, legacy all-modelled-cost 1.5× stress net -₹64,634, mean stress uplift +₹1,411/expiry; CI [-₹915,+₹4,290], one-sided p=0.1642 and Holm-adjusted p=0.9850. This is not statistically significant, and the absolute P&L remains negative.
- **2026 holdout:** not evaluated; only 13 matched expiries, below the 20-expiry pre-registered threshold. No confirmation is claimed.
- **Operational repairs:** run 37926550040 and run 37926908847 failed after analysis due to a stray workflow Python-heredoc line and/or concurrent append-only log rebase conflict. Run 37927040268 corrected the workflow and successfully persisted artifacts. Failed runs remain documented.
- **Conclusion:** no factor selector is promoted. The current legacy panel supports only a negative/insufficient-evidence exploratory screen. Next phase is true variable-configuration replay, with traded-futures basis and 2026 OI gates still open.

## 2026-10-09 17:51:46 IST — Automated run 37928216137

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 60,000–84,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.

## 2026-10-09 17:58:30 IST — Automated run 37929888516

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 85,000–109,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.


## 2026-10-09 — Step 0.10: Pinned Phase43/45 base replay and EOD factor-source run

- **Run:** [37929888516](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929888516), end-to-end success.
- **Pinned market source:** `thetrademarkk/india-index-options-1m` at `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`, declared `cc-by-nc-4.0`.
- **Replay outputs:** 9,699 result rows; 42 strategy labels; 256 expiry events; first expiry 2021-06-03; last expiry 2026-05-26. Base matrix SHA256 `76b12c6723affbd33cdd736b04e5bba4172cdd5a1ffe9c04b081f69038a081d1`. These are fixed base templates and do not constitute a 9,379,584-configuration grid test.
- **Candidate status:** LOW-VIX Bear Call Spread validation net ₹24,743 and legacy all-cost 1.5× stress net ₹23,082; inherited Phase45 gate had zero Holm-adjusted survivors. No promotion.
- **Daily EOD factor supplement:** NSE F&O archive commit `0ef4988629d52ca4ca83853b5def1d157f5453d4`; 512 prior-session ZIPs processed, 256 of 256 replay events received EOD factor rows, 0 missing paths, file errors, or gap rows. This is daily EOD only and NSE data rights remain a gate. The corrected factor-coverage build will rerun with cached archives.
- **Coverage-gate failure:** run [37930010915](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37930010915) stopped because `expiry_coverage_audit.py` was not present on the workflow branch checkout. Fixed by copying the source file to the Phase52 branch (commit `43e8ae1a9a4c5acf5c6be4c0f4a83bb74455f50b`). This failed run has no coverage conclusion; rerun is required.
- **Next:** exact expiry/entry coverage; refresh replay manifest's empty-error-file count/provenance; inspect actual factor non-null rates; then decide whether available data support variable-configuration replay.

## 2026-10-09 18:08:24 IST — Automated run 37931097834

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 110,000–134,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Expiry timestamp coverage: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.

## 2026-10-09 18:10:17 IST — Automated run 37931305395

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 135,000–159,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Expiry timestamp coverage: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.

## 2026-10-09 18:20:49 IST — Automated run 37932492241

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 160,000–184,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Expiry timestamp coverage: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.
