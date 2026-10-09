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
- The legacy factor-selector pilot is not the full Phase52 configuration sweep; futures/synthetic basis remains unavailable in its seed panel. No Phase52 candidate is promoted.


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

## 2026-10-09 18:23:31 IST — Automated run 37932520478

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 185,000–209,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Expiry timestamp coverage: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.

## 2026-10-09 18:49:09 IST — Automated run 37934719402

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 210,000–234,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Configuration event universe: CONFIGURATION_EVENT_UNIVERSE_BUILT_WITH_EXPLICIT_COVERAGE_GAPS; source expiries=267; expected grid events=1068; exact index entry ticks=1012; missing exact index ticks=56.
- Exact option bar coverage: OPTION_QUOTE_COVERAGE_AUDIT_COMPLETE; event rows audited=1068/1068; events with option rows at exact entry=1016; entries with OI-qualified contracts=1012; source file errors=0; config-specific legs still require replay-worker checks.
- Fixed 10:00 coverage audit: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; base matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.


## 2026-10-09 18:49 IST — Step 2.4: Exact option/OI broad event coverage audit

- **Workflow:** [37934719402](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934719402), completed successfully; 25,000 more configuration IDs enumerated only (checkpoint offset 235,000 of 9,379,584).
- **Pinned input:** `thetrademarkk/india-index-options-1m` revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`; all 267 option expiry files audited; zero source file errors.
- **Expected event universe:** 1,068 target-expiry × DTE {0,7} × entry-time {09:45,13:00} events. All 1,068 have broad option coverage audit records.
- **Counts:** exact index timestamp 1,012; any option rows at exact entry 1,016; both CE and PE 1,016; at least one contract with OI≥100 1,012; 15:15 same-day exit rows 1,016; target-expiry common-time CE+PE exit 1,040.
- **Intersections:** exact index + option rows + OI≥100 = 1,006; same plus broad expiry exit = 1,004. By split, stricter broad expiry-exit intersection is development 526/540, validation 404/416, holdout 74/112.
- **Interpretation:** This is only broad event/contract-universe coverage. It is not selected-strike coverage and not P&L. Every configured leg must still pass exact strike, expiry, timestamp, OHLC-range, OI, and exit-fill eligibility. No interpolation or nearest-tick substitution is permitted.
- **Important holdout limitation:** The pinned index source ends 2026-07-02. Although the option expiry-file inventory reaches 2026-08-04, several recent files have no corresponding exact entry/exit rows; 2026-07-28 and 2026-08-04 remain data-gated.
- **Decision:** Do not launch the full configuration-grid replay yet. Implement and validate the configuration-specific leg eligibility/fill engine first, and protect holdout from configuration tuning.


## 2026-10-09 18:52 IST — Step 2.5: Add selected-strike eligibility gate

- **Reason:** The completed broad event audit explicitly states it cannot establish exact strike/leg tradability.
- **Change:** Added `research/phase52/selected_strike_coverage_audit.py` and wired it into both main and phase-branch workflows. It checks nearest-ATM strike-rank offsets -6..+6 for CE/PE, exact entry bars, valid OHLC, OI≥100, exact 15:15 exit bars and common target-expiry exit bars. It writes a compressed event/offset/type matrix and source hashes, without P&L.
- **Data guard:** Absolute-delta selection is explicitly marked blocked until a validated point-in-time delta/IV resolver is implemented; no delta is guessed from close prices.
- **Engineering correction:** Timestamp lookup was changed to a per-file timestamp index to avoid repeated full-file scans; output directory is created before the workflow step so failure logging can persist.
- **Status:** Code is committed; self-test and end-to-end audit are pending the next Actions run. No result is accepted yet and no configuration P&L is calculated.


## 2026-10-09 — Pre-run audit correction: timestamp key normalization

During code review before accepting the selected-strike audit, I found that index spot-map keys used ISO `T` timestamps while lookup used `str(Timestamp)` with a space. Patched both sides to use `isoformat()` and added a self-test assertion. This correction occurred before the first accepted selected-strike result; run remains pending.
## 2026-10-09 18:59:45 IST — Automated run 37935663113
- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 235,000–259,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Configuration event universe: CONFIGURATION_EVENT_UNIVERSE_BUILT_WITH_EXPLICIT_COVERAGE_GAPS; source expiries=267; expected grid events=1068; exact index entry ticks=1012; missing exact index ticks=56.
- Exact option bar coverage: OPTION_QUOTE_COVERAGE_AUDIT_COMPLETE; event rows audited=1068/1068; events with option rows at exact entry=1016; entries with OI-qualified contracts=1012; source file errors=0; config-specific legs still require replay-worker checks.
- Fixed 10:00 coverage audit: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; base matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.


## 2026-10-09 — Pre-acceptance correction: point-in-time strike ladder

During review of the selected-strike auditor, changed ATM/rank-offset selection to use only strikes present at the exact entry timestamp. Using the entire expiry file could expose later-listed strikes and violate point-in-time selection. F52-026 records the correction. The currently active workflow may have checked out the earlier draft; its output will not be accepted unless provenance confirms the patched code. No P&L is affected because the audit is coverage-only.


## 2026-10-09 — Workflow persistence regression passed

Run 37935663113 completed successfully after the conflict-safe persistence change. The formerly failing checkpoint step now passes; no unresolved non-log conflict was auto-resolved. The selected-strike audit is separate: two earlier workflow runs are active on older snapshots and their output will not be accepted as evidence for the patched point-in-time strike ladder; run 37937318538 is queued to test the latest branch version.


## 2026-10-09 — Prevent stale audit output overwrite

Added a persistence guard to main and research-branch workflows: if the selected-strike auditor changed on the remote research branch after a run checked out its snapshot, that run's selected-strike output is discarded (or the remote result state restored) rather than overwriting corrected results. This protects against the two earlier in-flight runs. Verification remains pending; no selected-strike output is accepted until the patched self-test and provenance gate pass.


## 2026-10-09 — Stale-output pathspec correction

The stale-run guard now recreates the selected-strike output directory and adds a .gitkeep placeholder when no remote accepted result exists. This prevents the persistence step's explicit directory pathspec from failing after stale output is removed. Logged as F52-028; end-to-end verification remains pending.


## 2026-10-09 19:00 IST — Queue checkpoint after persistence fix

Run 37935663113 persisted the next 25,000 configuration IDs, moving the deterministic queue offset from 235,000 to 260,000 of 9,379,584. This is enumeration only, not backtesting. Its revised persistence step succeeded. The selected-strike audit still awaits a run with the latest point-in-time strike-ladder code.


## 2026-10-09 — Step 2.6: Reconcile Phase45 named strategy templates

- **Source audit:** Read the exact leg arrays in research/phase45_ready_made_sweep.py and the corresponding definitions in PHASE45_RESEARCH_PLAN.md on branch phase-45-exhaustive-ready-made-strategies.
- **Families resolved:** Long Iron Condor, Long Iron Butterfly, Bull Condor, Bear Condor, Bull Butterfly, Bear Butterfly, Reverse Jade Lizard, Range Forward, Bear Risk Reversal, Batman and Double Plateau.
- **Change:** Updated their strategy-specification rows to STANDARD_VARIANT_PREREGISTERED and documented source-defined geometry in PA-010. The named preset remains a separate baseline; variable configurations remain distinct IDs.
- **Impact:** Specification blockers fall from 15 families to four genuinely blocked families: Calendar Trap, Iron-Condor-to-Ratio transition, conversion/reversal, and futures-basis overlay. Three diagnostic-only families remain non-promotable. No P&L was calculated and grid domains did not change.
- **Verification:** Next workflow must validate the revised CSV/registry. In-flight runs checked out earlier specs and cannot be used as validation for this change.


## 2026-10-09 — Protect registry audit against stale source specifications

Because PA-010 changed 11 strategy-specification rows while older workflows were still running, added a persistence guard: if the specification CSV changed after checkout, the run cannot overwrite the registry audit for the new source snapshot. It restores the remote audit if present or discards the stale local summary. Logged as F52-030; end-to-end test pending.


## 2026-10-09 — Selected-strike audit first execution (stale source snapshot; not accepted)

Run 37937164472 reports the selected ATM-offset strike audit step itself as successful, but the run checked out the auditor before PA-026/F52-026 changed strike-ladder resolution to contracts present at the exact entry timestamp. Therefore its selected-strike output is explicitly not accepted as evidence. The persistence guard should discard that output when the source hash differs from the current branch. The queued run 37938099763 is expected to validate the patched script and the PA-010 specification snapshot.


## 2026-10-09 — Concurrent result collision and persistence correction

Run 37937164472's broad coverage and selected-strike steps completed at the process level, but the final persistence step failed because another run wrote the same generated files. This was not a strategy-test failure; no selected-strike result from its stale source snapshot is accepted. Restored one shared concurrency group and changed the resolver to preserve the already-persisted remote version for conflicts inside generated-result directories, while merging append-only logs and refusing source/code conflicts. F52-032 records the correction. The next queued run must verify end-to-end persistence.
## 2026-10-09 19:14:09 IST — Automated run 37936777969
- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 260,000–284,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Configuration event universe: CONFIGURATION_EVENT_UNIVERSE_BUILT_WITH_EXPLICIT_COVERAGE_GAPS; source expiries=267; expected grid events=1068; exact index entry ticks=1012; missing exact index ticks=56.
- Exact option bar coverage: OPTION_QUOTE_COVERAGE_AUDIT_COMPLETE; event rows audited=1068/1068; events with option rows at exact entry=1016; entries with OI-qualified contracts=1012; source file errors=0; config-specific legs still require replay-worker checks.
- Fixed 10:00 coverage audit: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; base matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.

## 2026-10-09 19:23:43 IST — Automated run 37938433270

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 285,000–309,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Configuration event universe: CONFIGURATION_EVENT_UNIVERSE_BUILT_WITH_EXPLICIT_COVERAGE_GAPS; source expiries=267; expected grid events=1068; exact index entry ticks=1012; missing exact index ticks=56.
- Exact option bar coverage: OPTION_QUOTE_COVERAGE_AUDIT_COMPLETE; event rows audited=1068/1068; events with option rows at exact entry=1016; entries with OI-qualified contracts=1012; source file errors=0; config-specific legs still require replay-worker checks.
- Fixed 10:00 coverage audit: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; base matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.

## 2026-10-09 19:52:13 IST — Automated run 37942202655

- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 310,000–334,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Configuration event universe: CONFIGURATION_EVENT_UNIVERSE_BUILT_WITH_EXPLICIT_COVERAGE_GAPS; source expiries=267; expected grid events=1068; exact index entry ticks=1012; missing exact index ticks=56.
- Exact option bar coverage: OPTION_QUOTE_COVERAGE_AUDIT_COMPLETE; event rows audited=1068/1068; events with option rows at exact entry=1016; entries with OI-qualified contracts=1012; source file errors=0; config-specific legs still require replay-worker checks.
- Selected ATM-offset leg audit: SELECTED_STRIKE_ATM_OFFSET_COVERAGE_AUDIT_COMPLETE; files=267/267; leg-event rows=27768; OI-qualified entries=11222; exact-index+OI+expiry-exit rows=11108; source errors=0; ABS_DELTA remains blocked; no P&L.
- Fixed 10:00 coverage audit: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; base matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.


## 2026-10-09 — Step 2.6: Correct selected-strike and delta-audit timing before replay

- Audited the selected ATM-offset artifact and delta resolver source line by line after the successful workflow step; that source review found two semantics errors despite a green workflow.
- **ATM_OFFSET:** old run 37942202655 computed coverage with ordinal strike ranks and index close at entry. Corrected to index open at exact entry timestamp, nearest ATM among exact-time option contracts, and the Phase43 modal strike-step rule; offsets are now arithmetic strike gaps. The old 27,768-row summary is superseded and must not be quoted as current coverage.
- **ABS_DELTA:** workflow 37944408314 failed at self-test before reading market data. Fixed `sigma=180` to `sigma=0.18` and changed the invalid negative premium fixture to a call with intrinsic value. Further removed same-bar-close lookahead: IV/delta now uses exact prior one-minute option/index close and prior-bar OI; current entry open is checked separately.
- **Plan impact:** added PA-011/PA-012 and amended replay protocol. Grid v1.3 domains and configuration IDs are unchanged; no P&L has been computed from these audits.
- **Next:** trigger corrected regression workflows; inspect their source hashes, exact-stamp/selected-leg coverage and delta-selection status summaries. Only after regression succeeds should a tiny hand-calculated replay engine test be built; do not start the full config queue yet.


## 2026-10-09 — Step 2.7: Gate ATM-offset OI with prior completed bar

- Source review of PA-011/PA-012 correction found current-bar OI was still used in the ATM-offset audit, despite open-fill semantics.
- Patched research/phase52/selected_strike_coverage_audit.py on main and research branch: exact prior timestamp is entry_ts minus one minute; prior_oi_gate must show a unique target-contract row and OI>=100; exact entry-time OHLC validity/open is a separate condition; current entry-bar OI is diagnostics only.
- Added plan/protocol amendment PA-013 and updated configuration execution semantics. v1.3 domains remain unchanged; no P&L calculated.
- The currently running factor workflow (37954806932) checked out the code before PA-013, so its selected-strike result must not be accepted as final. Wait for it to complete, then rerun; delta workflow 37954839508 is queued by concurrency and should use the updated branch code.
## 2026-10-09 21:34:23 IST — Automated run 37954806932
- Registry validation: PASS; hypotheses registered: 312; structure families: 52; selector modes: 6.
- Finite configurations in grid phase52-grid-v1.3: 9,379,584; this run enumerated 25,000 configurations at offsets 335,000–359,999.
- Source-discovery queries: 11; unique leads added: 0. Credential presence only (no values logged): {'HF_TOKEN': True, 'GITHUB_TOKEN': True, 'YOUTUBE_API_KEY': False}.
- Queue status: ENUMERATED_NOT_BACKTESTED; enumeration complete: False. Enumerated configs are NOT backtests.
- Pinned base replay: BASE_GEOMETRY_REPLAY_COMPLETE_NOT_FACTOR_PROMOTION; revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5; trade rows=9699; strategies=42; license gate=RESEARCH_ONLY_NONCOMMERCIAL_SOURCE.
- Configuration event universe: CONFIGURATION_EVENT_UNIVERSE_BUILT_WITH_EXPLICIT_COVERAGE_GAPS; source expiries=267; expected grid events=1068; exact index entry ticks=1012; missing exact index ticks=56.
- Exact option bar coverage: OPTION_QUOTE_COVERAGE_AUDIT_COMPLETE; event rows audited=1068/1068; events with option rows at exact entry=1016; entries with OI-qualified contracts=1012; source file errors=0; config-specific legs still require replay-worker checks.
- Selected ATM-offset leg audit: SELECTED_STRIKE_ATM_OFFSET_COVERAGE_AUDIT_COMPLETE; files=267/267; leg-event rows=27768; OI-qualified entries=11223; exact-index+OI+expiry-exit rows=11109; source errors=0; ABS_DELTA remains blocked; no P&L.
- Fixed 10:00 coverage audit: COVERAGE_AUDIT_COMPLETE_WINDOW_GATE_REVIEW_REQUIRED; source expiries=267; base matrix expiries=256; last source expiry=2026-08-04; last matrix expiry=2026-05-26; missing/unreplayed=11.
- Data capability audit: PASS_METADATA_AND_SAMPLE_AUDIT_WITH_REVIEW_GATES; sampled source files=2; factor availability and licensing limits retained.
- Prior-session NSE EOD factor build: DAILY_EOD_FACTOR_BUILD_WITH_COVERAGE_AUDIT; event coverage=100.0%; missing archive paths=0; file errors=0; not intraday futures basis.
- EOD selector pilot: EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION; matched events=256; fixed development baseline=buy_call; best validation uplift diagnostic=EOD_VOLUME_PCR uplift=923 INR/event, Holm p=1.0000; no promotion.
- Factor-selector pilot: FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION; PIT match=68.2%; risk-limited legacy templates=25; chosen features={'GLOBAL_SENTIMENT_PROXY': 'global_NASDAQ_ret1', 'GREEKS_SURFACE_ROUTER': 'atm_pe_iv', 'MULTI_FACTOR_ROUTER': 'TREND_X_IV_SKEW', 'OI_FLOW_ROUTER': 'near_atm_oi_pcr', 'SPOT_PROXY_ONLY': 'nifty_ma_gap_15m', 'VIX_ROUTER': 'India_VIX_state'}.
- The legacy factor-selector pilot is not the full Phase52 configuration sweep. No Phase52 candidate is promoted.


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


## 2026-10-09 — Step 2.8: Corrected strike/delta audits and deterministic kernel tests accepted

- **ATM_OFFSET run:** [37956261518](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956261518), successful. Corrected selected-strike summary hashes the current script and protocol. All 267 source option files were read without errors. Of 27,768 strike-offset/type rows, 10,552 had prior OI≥100, 10,501 had both prior OI and valid exact entry OHLC, and 10,405 also had exact-index and valid expiry-exit support.
- **ABS_DELTA run:** [37956675818](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956675818), successful. All 4,272 pre-registered target-delta/type checks across 267 expiry files were emitted with zero source errors. 232 rows had no exact prior-minute input; 148 had no prior-OI-qualified candidate; 3,892 passed the OI gate; 2,232 had valid exact entry bars. IV/delta is European Black–Scholes estimation at 6% rate, zero dividend yield, not exchange-published Greek.
- **Kernel run:** [37957753452](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957753452) passed synthetic exact-bar, common timestamp, OI, fill/slippage, cost, range proxy, TP and fail-closed tests. The first run 37957499754 was an infrastructure path failure after `SELF_TEST_PASS`, resolved by using the runner-temp environment variable.
- **Decision:** PA-011/012/013 audit fixes are verified. No Phase52 configuration P&L exists. Next is the source-reconciled family parser and end-to-end leg combination/exit/cost golden fixtures; the full finite grid remains a queue, not backtest results.


## 2026-10-09 — Step 2.8: Corrected strike/delta audits and deterministic kernel tests accepted

- **ATM_OFFSET run:** [37956261518](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956261518) passed. Fingerprinted selected-strike coverage over 267/267 source expiry files and 1,068 events. Of 27,768 offset/type rows, 10,552 had prior OI≥100, 10,501 had prior OI plus valid exact entry OHLC, and 10,405 also had exact-index and valid target-expiry exit support.
- **ABS_DELTA run:** [37956675818](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956675818) passed. 4,272 selection rows over 267/267 expiry files, zero source errors; 232 lack exact prior minute, 148 lack an OI-qualified candidate, 3,892 pass prior-bar OI, and 2,232 have an exact valid entry bar/open. These are model-based diagnostics, not exchange Greeks or P&L.
- **Kernel tests:** [37957753452](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957753452) passed synthetic tests for exact contracts/timestamps, common multi-leg timestamps, prior OI, adverse fills, date-aware charges, ₹10/₹20 brokerage × 0/50/100 slippage, OHLC-range liquidity proxy, TP next-open and eligibility block gates. The initial run 37957499754 failed only at the evidence-manifest path after the self-test passed; fixed and rerun successfully.
- **Current decision:** PA-011 to PA-013 implementation defects are closed. No Phase52 grid configuration P&L exists. Next is explicit family-template parsing and full multi-leg event replay golden tests; only then can a first limited real-data configuration shard be accepted.


## 2026-10-09 22:38 IST — Step 2.8: Template resolver and whole-position synthetic integration passed

- **Precondition:** Read Phase52 status, error log, research plan, replay protocol, config-space schema and README before resuming. No protocol/grid domain change was needed.
- **Resolver code fix:** Applied the frozen `reference_lots_per_leg` scale after ratio overrides in `strategy_template_resolver.py`; invalid nonpositive/noninteger inputs fail closed. This aligns implementation with protocol v1.0; the registered grid is unchanged.
- **Initial failed test:** run [37960340815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960340815) failed because the native butterfly lot-scale fixture mistakenly included explicit ratio [1,1]. Resolver stage passed. Corrected fixture in branch commit `c0c25dab78495098b7c43b7ad801c0480147df10`; failure logged as F52-022.
- **Successful integrated run:** [37960484240](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960484240) passed all steps and uploaded artifact `phase52-whole-position-integration-37960484240` (artifact ID 11631323294, 5,132 bytes; SHA256 zip `99dbb8486d95dfc8538f684249fa3b7cfde3300f41a576630bae33fa7d0a1253`).
- **Coverage:** 45 supported option-only templates resolved and were costed synthetically end to end, 6 scenario cases each (₹20 primary / ₹10 legacy sensitivity × 0/50/100% adverse slippage): 270 synthetic scenario records. Seven other family rows are fail-closed; futures hedge/basis templates remain blocked without real synchronized futures contract/quotes. Four templates in the synthetic set remain diagnostic-only and non-promotable.
- **Whole-position checks:** exact strike/expiry/type/timestamp, valid OHLC, exact prior-minute OI≥100, entry OHLC-range proxy, exact 15:15 bar for every leg, common exit timestamp, two orders per leg, brokerage per order, independent statutory fees, and no partial scenario if any leg is missing. Reference-lot × ratio tests and missing-entry/low-OI/missing-exit/no-common-time fixtures passed.
- **Fee parity:** canonical kernel remained PASS; one-leg fixture raw arithmetic ₹1,625 and after ₹0.05 adverse slippage per fill ₹1,618.50 before fees; 2-leg vertical raw ₹3,185 and after all leg slippage ₹3,172 before fees. Phase43 fee parity was ₹65.72656975 on its independent fixture.
- **Critical boundary:** all integration P&L is synthetic fixture arithmetic. No historical option data was accessed by this workflow, no Phase52 grid configuration P&L exists, and no candidate is promoted.
- **Formatting audit:** status/research log escaped newline issue corrected as F52-023.
- **Next planned stage:** implement a bounded historical replay pilot for a small preregistered sample of ATM_OFFSET, BASELINE, fixed 15:15 exit and exact source contracts. Before any historical P&L, require actual per-leg entry/exit validation on downloaded pinned option/index data, date-aware lot sizing/cost parity, explicit per-event exclusions and source-hash/engine-hash manifests. ABS_DELTA, selector routers, DTE/exit variants, unresolved specs and actual futures-dependent templates remain blocked until their dedicated gates are implemented.

## 2026-10-09T16:58:30.925413+00:00 — Bounded historical pilot run 37962192723

- **Run:** [37962192723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37962192723); job=failure; self-test=success; plan-only=success; replay=failure.
- **Frozen pilot preflight only:** configs=40; events=24; planned config-event rows=480; historical replay report missing.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Frozen plan: research/phase52/first_historical_pilot.json; runner: research/phase52/historical_pilot_runner.py.
- No hidden reasoning or secret values are recorded. Workflow logs/artifacts preserve operational errors.

## 2026-10-09T17:04:53.763259+00:00 — Bounded historical pilot run 37962948690

- **Run:** [37962948690](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37962948690); job=success; self-test=success; plan-only=success; replay=success.
- **Pilot result status:** HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS; configs=40; planned config-event rows=480; executed=1; excluded/errors=479; cost rows=6; source file errors=0.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Frozen plan: research/phase52/first_historical_pilot.json; runner: research/phase52/historical_pilot_runner.py.
- No hidden reasoning or secret values are recorded. Workflow logs/artifacts preserve operational errors.


## 2026-10-10 — PA-015: Historical pilot v0.2 exact-duplicate normalization

- Preserved pilot v0.1 outputs. Root cause: duplicate exact contract bars caused 274/480 planned config-event rows to fail closed; 205 additional rows failed the preregistered 2% high-low/open proxy; only one row executed.
- Updated `historical_pilot_runner.py` to drop only full-row identical records after normalized timestamp/type/numeric fields. Per-file audit logs source row count, exact duplicate rows removed and post-dedup rows. Conflicting duplicates are not resolved and remain blocked.
- Bumped the pilot version to v0.2 and updated its frozen plan before rerun. No config/event/cost/threshold change; no P&L ranking or selection. The 2% metric is explicitly described as an OHLC range proxy, not actual bid/ask spread.
- Next: self-test, run v0.2, reconcile exactly 480 statuses, inspect duplicate removals and conflicts, then decide whether a larger development/validation engineering pilot is possible. No holdout use.


## 2026-10-10 — Launch pilot v0.2 exact duplicate normalization

- Run [37980455805](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805) started after the runner, frozen pilot plan and workflow were updated.
- Self-test and frozen plan stages passed. Expected sample remains 40 configurations × 24 events = 480 config-event rows, with holdout untouched.
- Historical replay stage remained in progress at last check. No v0.2 report accepted yet; final status reconciliation pending.

## 2026-10-10 — Step 2.9: Historical BASELINE pilot v0.2 result and persistence failure

- **Run:** [37980455805](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805). Self-test=success; frozen preflight=success; replay=success; artifact upload=success; cache save=success; overall job=failure in final persistence.
- **Result reconciliation:** 40 configs × 24 events = 480 planned rows; EXCLUDED_OHLC_RANGE_PROXY=379; BLOCKED_LEG_ELIGIBILITY=100; REPLAY_PASS=1; total=480. The source reader audited 13 files with zero source-file errors and zero replay exceptions. Six cost-scenario rows were emitted for the single replayed row.
- **Input fingerprints:** dataset revision 0f4800e43e6f96cec0794369d78eb4d3c4211ef5; pilot plan SHA-256 714cdb7d8a4d47089b03df865a3d2261a5ae3171890640bc67177754118cb992; runner SHA-256 eabde2d0062a9ecde4b18bd8990cc9a4929f2549a38490bf18638519973cad48.
- **Persistence failure:** run output and artifact were generated, but the status-persistence script failed its rebase after concurrent updates produced conflicts in PHASE52_CHAT_LOG.md, PHASE52_RESEARCH_LOG.md and PHASE52_STATUS.md. Logged separately in PHASE52_ERROR_LOG.md. Do not describe this as replay failure; do not promote the replay as a performance result.
- **Interpretation:** duplicate-only normalization did not cure sparse eligibility: 479/480 rows are excluded or blocked. This is a source/coverage engineering result only. Holdout remains unused; no strategy ranking or factor-router inference is justified.

## 2026-10-10 — Step 2.10: OpenChart source feasibility audit and bounded probe registration

- Inspected the OpenChart README, core request code, response transformer, license and issue list at pinned upstream commit a207108890c96a9830b35a8d15442c896ea0a9d6.
- The client documents individual-instrument OHLCV and 1-minute intervals via NSE charting endpoints. The inspected response schema does not include OI, Greeks, bid/ask, order-book depth or trade-by-trade records; complete expired-contract and all-chain coverage is not demonstrated.
- The upstream transformer strips timestamp timezone metadata; returned clock conventions need independent session-anchor verification. Public issues contain reports of request failures/rate limiting and an open question about oldest backfill duration.
- NSE market-data usage policy is separate from the MIT license of client software. Raw bars will not be persisted to the public repository pending terms/storage review.
- Decision: probe OpenChart as an auxiliary candidate only. Add a rate-limited bounded workflow with aggregate diagnostics against current symbol search plus Phase 51 missing-session windows 2026-07-28 and 2026-08-04. No strategy-grid, event, cost or OOS boundary changes.

## 2026-10-10 — Step 2.11: OpenChart symbol-search capability probe completed

- **Pinned code:** marketcalls/openchart 0.2.0, upstream commit a207108890c96a9830b35a8d15442c896ea0a9d6.
- **Workflow runs:** initial probe [37982208116](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982208116); intermediate diagnostics [37982325565](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982325565) and [37982356068](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982356068); expanded final probe [37982534138](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982534138); final schema-corrected report [37982673873](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982673873). All workflow runs completed successfully; initial/intermediate report-schema shortcomings are separately logged in the error ledger.
- **Final request summary:** one homepage GET returned 403; six search POSTs to `/v1/exchanges/symbolsDynamic` returned 200. All six returned 20 rows, typed as Index in all 20 rows, with identical normalized result SHA-256 `6284a00ec2a8cc5c102d30f0b7e3dce5d5ccb9d8588b5c6a98b9a440d761d837`. FO and IDX queries for NIFTY were identical. A current-month option prefix, documented option example and both target-month prefixes had zero symbol/description matches.
- **Crucial limitation:** `historical_probes=[]`; zero history requests were made because no option contract/token was discovered. The two target-date windows were planned; zero were actually queried for historical option bars. The direct-token historical API was not tested.
- **Decision:** OpenChart's current public wrapper is **not accepted for all-options acquisition**. The underlying charting endpoint is reachable, but symbol discovery does not satisfy the source-universe requirement in this probe. Repair/verify request semantics or supply an independently verified contract/token master before a direct-token history test. Its documented OHLCV schema still does not cover OI, exchange Greeks, bid/ask or depth.
- **Data governance:** only aggregate metadata/fingerprints were persisted. No raw bars, full symbol list, contract token or market prices were added. NSE usage/storage rights remain a separate gate from the client's MIT software license.
- **Report:** [results/phase52/openchart_probe/runs/37982673873/probe_report.json](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/openchart_probe/runs/37982673873/probe_report.json). No strategy grid, cost model, validation split or holdout changed.

## 2026-10-10 — Step 2.12: Return to preregistered Phase 52 replay work

- User explicitly asked to forget OpenChart and resume the planned research. No further OpenChart probes are to be run; prior negative result is retained only as an audit record.
- The next work is engineering and coverage diagnosis, not strategy optimization: (1) repair pilot checkpoint persistence after run 37980455805's rebase conflicts; (2) decompose all 480 statuses by exact first failure and source/contract/time; (3) trace representative failures to pinned source rows; (4) only correct demonstrated source/mapping/software defects and rerun the same frozen sample.
- Current pilot remains 379/480 OHLC-range exclusions, 100/480 leg-eligibility blocks, 1/480 executed. Exclusions are not losses. No relaxation of the preregistered 2% OHLC proxy, no changes to the event/configuration/cost/split definitions, and no holdout access.
- Promotion, statistical inference and full-grid factor-router claims remain blocked until usable coverage and reproducible replay gates pass.


## 2026-10-10 — Evidence integrity checkpoint

Inspection of the committed historical-pilot report found a provenance inconsistency: `report.json` and its event CSVs identify `phase52-historical-base-pilot-v0.1` with counts 274 blocked / 205 excluded / 1 replay pass, while the later v0.2 checkpoint in conversation records 100 blocked / 379 excluded / 1 pass. The report and CSVs currently inspected agree with each other but are not enough to establish the v0.2 totals. Treat the counts as unresolved until the matching run artifact is reconciled. Do not infer profitability or loosen the frozen 2% OHLC proxy.

## 2026-10-10 — Step 2.13: Reconcile v0.2 artifact and diagnose pilot coverage

- Retrieved and extracted workflow artifact 11641042776 for run [37980455805](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805), digest `sha256:34b987e2fa19821898582145ae6d4403a64f6d9d085f588628a07b6e78da2aaa`. The artifact report and full event CSV both identify `phase52-historical-base-pilot-v0.2` and agree exactly: 480 rows = 379 OHLC-proxy exclusions + 100 prior-OI blocks + 1 replay pass. The older committed `report.json` and CSVs are v0.1, not a contradictory v0.2 output. Provenance mismatch is resolved by version separation.
- The 100 eligibility blocks all resolve to `PRIOR_OI_MISSING_OR_BELOW_GATE` with `prior_oi=0.0`; all belong to validation split, across five event IDs (20 each). This indicates missing/zero prior-bar OI coverage on the selected option contracts/timestamps; it is not a residual exact-duplicate failure.
- The 379 range-proxy exclusions show `(high-low)/open*100` from 2.38% to 44.44%. Bins: 34 in 2–5%, 149 in 5–10%, 167 in 10–20%, 29 above 20%. These are OHLC range values, not bid-ask spreads. They remain excluded under the frozen pilot; any future liquidity filter must use actual quote data rather than silently relabeling the proxy.
- One replay row is a development-split BUY_CALL on 2022-12-15 13:00 IST. Modeled net P&L is -₹166.19 to -₹194.79 across six cost/stress cases; the row is research-only and not an efficacy result. 13 source files audited, zero source-read errors, zero replay exceptions, 6 cost rows, no holdout used.
- Persistence helper now contains an allowlisted, append-only conflict union with bounded fetch/rebase/push retries and refuses source-code conflicts. A regression test exercises both malformed markers and a real local-Git concurrent rebase. Workflow run [37983999726](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37983999726) is the current test/replay validation.
- Decision: Phase 52 baseline pilot is technically auditable but has inadequate coverage (1/480 = 0.21%). No ranking, statistical claim, router efficacy statement or promotion. Next phase should source-test better OI + quote-quality inputs before a larger replay.
## 2026-10-09T20:04:16.938553+00:00 — Bounded historical pilot run 37983999726
- **Run:** [37983999726](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37983999726); job=success; self-test=success; plan-only=success; replay=success.
- **Pilot result status:** HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS; configs=40; planned config-event rows=480; executed=1; excluded/errors=479; cost rows=6; source file errors=0.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Frozen plan: research/phase52/first_historical_pilot.json; runner: research/phase52/historical_pilot_runner.py.
- No hidden reasoning or secret values are recorded. Workflow logs/artifacts preserve operational errors.

## 2026-10-09T20:11:32.785337+00:00 — Bounded historical pilot run 37984566094

- **Run:** [37984566094](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37984566094); job=success; self-test=success; plan-only=success; replay=success.
- **Pilot result status:** HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS; configs=40; planned config-event rows=480; executed=1; excluded/errors=479; cost rows=6; source file errors=0.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Frozen plan: research/phase52/first_historical_pilot.json; runner: research/phase52/historical_pilot_runner.py.
- No hidden reasoning or secret values are recorded. Workflow logs/artifacts preserve operational errors.

## Leg-evidence repair run \37989502259

- Run: [\37989502259](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/\37989502259)
- Job status: \failure
- Intended change: preserve all resolved-leg range diagnostics without changing the frozen 2% eligibility rule, costs, or event universe.
- Status counts and per-row leg completeness must be reviewed from the uploaded artifact before using it in Phase 54.

## Leg-evidence repair run \37989783135

- Run: [\37989783135](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/\37989783135)
- Job status: \failure
- Intended change: preserve all resolved-leg range diagnostics without changing the frozen 2% eligibility rule, costs, or event universe.
- Status counts and per-row leg completeness must be reviewed from the uploaded artifact before using it in Phase 54.


## F52-LEG-EVIDENCE-001 — First repair run failure

- Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37989502259
- Failure: frozen pilot manifest rejected `file_hashes` drift after the runner patch; artifact upload also failed because escaped GitHub expressions produced a backslash in the artifact name.
- Correction: Phase 52 workflow now refreshes the manifest only after checking 40 configurations and 24 frozen event identities, then replays; GitHub expression escaping and artifact missing-file handling were corrected.
- Verification queued: run 37989827840 on commit 75d1d3135831c42e93f617dab396cc58d8e33d80.
- Status: OPEN until replay and artifact validation succeed.
