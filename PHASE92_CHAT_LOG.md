# Phase 92 Chat / Decision Log

Date: 2026-10-10

## User request
User replied “Ok proceed” after completion of the Phase 91 temporal replication.

## Prior state checked
- Read current main README and Phase 91 plan/status/error/chat/synthesis.
- Read Phase 60 and Phase 61 source-sufficiency decisions before proposing the next phase.
- Phase 91 concluded no reliable replicated incremental ATM-IV predictor gain (latest run 38049680438). The IV-only line is closed at its registered stop.
- Phase 60/61 remain NO-GO for empirical execution-grade options strategy tests until documented data rights and exact contract/timestamp coverage are available. Do not repeat the same metadata-only source search.
- Official Dhan docs state rolling expired options history extends up to five years, allows up to 30 days per call, and `toDate` is non-inclusive. Historical candle timestamps are candle-start timestamps. This motivates 2022 rolling-option data with a one-bar feature lag.

## Phase 92 decision
Run one bounded 2022 study of a lagged ATM synthetic-forward proxy gap and CE/PE OI imbalance as predictors beyond spot/VIX/IV. Use Jan–Jun DEV, Jul–Sep reporting-only validation, Oct–Dec confirmatory OOS. One primary endpoint: M2 MAE minus M4 MAE; paired session-cluster bootstrap, 5,000 draws, seed 90210. This tests predictive contribution, not strategy P&L or actual futures arbitrage.

## Point-in-time control
Because source candle timestamps are candle-start time and close-derived features cannot be known at the candle start, option-derived IV, OI, and synthetic-proxy values are lagged one whole 5-minute row; VIX close is also lagged one row. This conservative design is registered before execution. Direct FUTIDX basis is omitted rather than guessed because exact historical futures contract mapping is not supplied by the rolling-options endpoint.

## Execution log

- Created branch `phase-92-synthetic-forward-oi-study-2022`, added the frozen plan/status/error/chat records, analysis engine, branch workflow, default-branch automation entry, and draft PR [#42](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/42). PR remains open/draft/unmerged.
- First run [38050580381](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050580381) completed the data request and statistical analysis but failed the publication push due a non-fast-forward branch race. The run emitted a negative primary estimate; that first report was not treated as final because its final weekend-only option chunk was classified incorrectly.
- A subsequent run [38050610192](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050610192) successfully published the report and exposed the weekend-only 2022-12-31 window as a false data-error classification.
- Static review confirmed 2022-12-31 was a Saturday and the half-open request interval 2022-12-31 through 2023-01-01 contains no weekday. The engine now reports aligned, empty windows with no weekday as `NoWeekdayExpected` and valid coverage, without fabricating or imputing rows. It also distinguishes an entirely negative confidence interval from an interval that merely crosses zero.
- Final accepted run [38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106) completed successfully using the fixed code. All 54 options windows and 5 VIX windows were valid; sample and train/validation gates passed.
- Primary result: M2 MAE − M4 MAE = −0.1708363 bps (95% session-cluster bootstrap CI −0.2298769 to −0.1152015; 5,000 resamples, seed 90210). The interval is wholly below zero, so the synthetic-forward/OI block made out-of-sample magnitude predictions worse on this fixed sample.
- Automation was changed to trigger on Phase 92 plan/engine pushes, with manual dispatch retained, while the PR runner reacts only to open/reopen to avoid retriggering on its generated output commit.
- Raw market responses/prices were not committed or uploaded. Phase 83's 2026 holdout was not requested.

<!-- PHASE92_RUNTIME_START -->
## Automated execution record — 38051908021
- Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38051908021
- Status: NEGATIVE INCREMENTAL VALUE — synthetic-forward/OI feature block worsens OOS magnitude prediction in this sample
- VIX ID resolved dynamically: True
- Options valid chunks=54/54; VIX valid chunks=5/5
- OOS rows/sessions=3660/61
- Primary result: M2 MAE − M4 MAE = -0.1708 bps (paired session-cluster bootstrap 95% CI -0.2299 to -0.1152; bootstrap positive share 0.0000; 5000 resamples; seed 90210).
- Option-derived close/IV/OI features were lagged one full five-minute row; no raw market responses were printed, committed, or uploaded as artifacts.
- Phase 83's 2026 holdout was not requested.
<!-- PHASE92_RUNTIME_END -->


## Terminal cross-phase conclusion

Created [CROSS_PHASE_FACTOR_SYNTHESIS.md](results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md) comparing Phase 89 (2025 feature associations), Phase 90 (small positive 2024 IV incremental gain), Phase 91 (2023 IV replication did not establish gain), and Phase 92 (2022 synthetic-forward/OI feature block worsened magnitude prediction). The specific rolling-ATM IV/synthetic-proxy/OI predictor line is closed at the registered one-sample replication stop. No additional year search, OOS tuning, or strategy promotion is warranted absent a materially new preregistered hypothesis or authorized exact-contract execution data.


## Manuscript / supplement package

Created [MANUSCRIPT_DRAFT.md](results/phase92/MANUSCRIPT_DRAFT.md), a structured research manuscript covering Phases 89–92 with abstract, literature review, questions/objectives, methods, statistics, results tables, discussion, strengths/limitations, conclusion, future directions, appendices and references. Added [SUPPLEMENTARY_MATERIALS.md](results/phase92/SUPPLEMENTARY_MATERIALS.md), [IV_INCREMENTAL_EFFECTS.svg](results/phase92/IV_INCREMENTAL_EFFECTS.svg), and [OOS_MAE_COMPARISON.svg](results/phase92/OOS_MAE_COMPARISON.svg). These use aggregate published results only; raw option/VIX payloads are not included.

- Manuscript references cross-checked against official/publisher sources and DOI pages, including Poon & Granger (2003), Christensen & Prabhala (1998), Christoffersen et al. (2013), Fodor et al. (2011), Jena et al. (2019), Harvey et al. (2016), Diebold & Mariano (1995), CME put-call parity guidance, NSE India VIX description, and Dhan API documentation. Cross-market/horizon differences are called out; literature results are not transferred as if they directly validate NIFTY 15-minute profitability.

## Literature expansion and final package audit

Expanded the manuscript literature review using publisher/official pages for Blair, Poon & Taylor (2001) on VIX versus intraday returns, Jiang & Tian (2005) on model-free IV, Bollerslev, Tauchen & Zhou (2009) on variance risk premia, and Novy-Marx & Velikov (2016) on trading costs. The manuscript now distinguishes these studies' targets/markets/horizons from the repository's 15-minute NIFTY spot-magnitude target. The manuscript's reference list includes DOI links; new figures are [IV_INCREMENTAL_EFFECTS.svg](results/phase92/IV_INCREMENTAL_EFFECTS.svg) and [OOS_MAE_COMPARISON.svg](results/phase92/OOS_MAE_COMPARISON.svg). No empirical model, sample, or result was changed during manuscript editing.
