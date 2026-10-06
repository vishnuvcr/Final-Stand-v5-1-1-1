# Research Log — main branch

## 2026-10-03 — Phase 20 isolated runner trigger
- Added a temporary main-branch execution bridge that checks out only `phase-20-payoff-boundary-stop-research`, executes the pre-registered boundary-stop research, and persists outputs back to that phase branch.
- The strategy code and research artifacts remain isolated on the Phase-20 branch.
- Phase history and detailed step logs continue on the phase branch.
[RUN_PHASE20_BRIDGE]

## 2026-10-03 — Phase 20 optimized execution trigger
- Optimized Phase 20 to reuse the locked 190-trade ledger and NIFTY spot file, loading option files only for expiry dates capable of breaching the entry payoff boundary.
- Corrected strike-column access in the option-path reconstruction before triggering the run.
[RUN_PHASE20_BRIDGE_OPTIMIZED]


## 2026-10-03 — Main-branch Phase 20 final status
- Phase 20 payoff-boundary research completed on isolated branch `phase-20-payoff-boundary-stop-research`.
- Boundary-stop family rejected after negative validation and 2026 holdout results.
- Final historical exit rule: target → 13:30 expiry-day negative-MTM/MFE<0.50×target stop → 15:29 expiry fallback.
- Final historical result: ₹149,129.53 net P&L across 190 trades; 179/190 positive net trades; 5 conditional stops; 0 baseline-positive trades stopped.
- Canonical final rules: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/FINAL_STRATEGY_RULES.md
- Detailed Phase 20 log, errors and artifacts remain on the isolated research branch.


## Final research closeout — 2026-10-03
- Phase 23 complete; no OOS strategy adjustment promoted.
- Phase 24 complete; no reversal trigger promoted.
- Final strategy remains the Phase-20 canonical dynamic-n specification.
- Final manuscript and evidence package are retained on branch phase-24-targeted-reversal-trigger.


## 2026-10-04 — Phase 27 final status
- Phase 27 delta-based exit research completed on isolated branch `phase-27-delta-exit-research`.
- Training-selected delta profit rule: MTM ≥ 0.90×target and |portfolio delta| ≤ 0.05.
- Validation uplift: −₹2,334.04. 2026 holdout uplift: −₹1,108.04.
- Holdout bootstrap 95% CI for mean trade-level uplift: −₹141.92 to −₹13.82.
- No adverse-delta stop selected.
- **No Phase-27 rule promoted; Phase-20 remains canonical.**


## Phase 28 — individual-leg delta research — COMPLETE — 2026-10-04

Phase 28 tested S1=short OTM-(n+1) and S2=short OTM-(n+2) deltas independently. Coverage was 99.21%. The least-bad training rule was S1 |delta|≤0.05 after 90% target, but it lost ₹2,998.16 training, ₹2,487.05 validation and ₹35.91 in the 2026 holdout. No adverse short-leg delta stop passed. **No promotion; Phase-20 remains canonical.**


## 2026-10-05 — Phase 29 complete: short-leg delta-change exits
- Tested target and stop entirely from individual/combined short-leg delta change; removed target-percentage criteria.
- Delta coverage 99.21%; 480 preregistered rules.
- Training-selected target: MEAN, 5-minute, 0.20 threshold, 3-minute confirmation.
- Training-selected stop: S1, 1-minute, 0.05 threshold, 3-minute confirmation; zero uplift.
- Versus canonical Phase 20: +₹18,251.49 training, −₹1,092.14 validation, −₹6,879.84 2026 holdout, +₹10,279.51 full.
- **Decision: no promotion; Phase 20 remains canonical.**
- Artifacts persisted on the Phase-29 branch.


## 2026-10-06 — Phase 32 initialized: Continuous Delta 6x6 Vertical Spread
- Created isolated branch `phase-32-continuous-delta-6x6-backtest` from the successful Phase-31 head.
- Registered a new strategy research question rather than modifying the canonical Phase-20 strategy.
- Frozen the user-specified entry, exit, direction-state and no-daily-square-off rules.
- Added Phase-32 research plan, pre-registration, strategy specification, status file, backtest entry point scaffold and manual GitHub Actions workflow.
- Numerical execution has **not** yet been accepted as evidence.


## 2026-10-06 — Phase 32 specification audit correction
- While the numerical CI job was running, an implementation audit identified a mismatch between the frozen rule current weekly expiry and the expiry enumeration.
- The engine had excluded the last expiry of every calendar month. This would have omitted monthly expiry weeks from the research sample.
- The affected numerical runs are explicitly marked invalid and will not be used.
- Corrected the expiry enumeration to include every weekly expiry file, including monthly expiries.
- Corrected execution started as GitHub Actions run 37383091606 from commit d1b44be28b87b2d6a264cc6ddcd72d3a551a9a2f.


## 2026-10-06 — Phase 32 execution-convention audit correction
- A further specification audit found that the 1-minute engine did not implement the live strategy's final 120-second action cutoff for new entries.
- Entries at 15:28 and 15:29 are now blocked; existing positions remain eligible for delta-triggered exits through the permitted contract path.
- Runs before this correction are not accepted as evidence.


## 2026-10-06 — Phase 32 state-machine audit correction
- A serious chronological state-machine defect was found before evidence acceptance.
- The engine could re-enter before a future exit timestamp because it calculated the future exit path inside the entry loop but did not advance the global cursor to the exit.
- Replaced this with an explicit chronological cursor and post-exit advancement.
- Corrected engine commit df8f9c0ca6e3fd3f84bcd6bd9c432f0b03ea171e.
- All prior Phase-32 runs remain non-evidence.


## 2026-10-06 — Phase 32 implementation regression correction
- The chronological state-machine rewrite introduced a non-numerical regression by removing the `expiry_ts` dataframe column needed by the delta-inversion helper.
- Corrected before evidence acceptance; no result from run 37384048259 is used.


## 2026-10-06 — Phase 32 historical lot-size audit correction
- Historical contract-size validation found that NIFTY lot-size changes must be applied by expiry cycle, not only by a single calendar cutoff.
- NSE's 2024 revision specifies the first revised weekly expiry on 02-May-2024; the November-2024 revision specifies the last weekly expiry at the old lot on 19-Dec-2024 and first revised weekly expiry on 02-Jan-2025, with the January-2025 monthly expiry still on the old lot and first revised monthly expiry on 27-Feb-2025.
- NSE's 2025 revision specifies the last weekly old-lot expiry on 23-Dec-2025, first weekly 65-lot expiry on 06-Jan-2026, last monthly old-lot expiry on 30-Dec-2025, and first monthly 65-lot expiry on 27-Jan-2026.
- Corrected commit: a29a17470b751c947ba1aa0f8c7ed6d3abfc6e13.


## 2026-10-06 — Phase 32 zero-net state correction
- Final pre-result state-machine audit found zero-P&L handling inconsistent with the pre-registration.
- Corrected before numerical evidence acceptance; the preceding candidate run is invalid for evidence.


## 2026-10-06 — Phase 32 historical contract-size audit correction
- Historical lot-size rules were cross-checked against NSE circulars.
- Corrected the single 30-Jan-2025 monthly NIFTY expiry exception: 25 lots, despite revised weekly contracts using 75 from 02-Jan-2025.
- Earlier numerical runs remain invalid for evidence.


## 2026-10-06 — Phase 32 current-week expiry audit correction
- A contract-selection audit found that the 14-day historical slice was incompatible with the rule current weekly expiry.
- The corrected engine uses adjacent-expiry windows, preventing the future week's contract from being traded while an earlier weekly contract is still current.
- The first in-sample expiry is treated as a warm-up/coverage boundary rather than an executable trade window.
- Corrected commit: 1675f86b8a71add7a73c03479731e3a5623716b.


## 2026-10-06 — Phase 32 computational optimization
- Vectorized the exit-delta inversion across future minute paths.
- Preserved exact first-hit chronology and all frozen thresholds; optimization changes execution speed only.
- Corrected commit: c0ec4b90fd33eee75ed0515343e28d431aee924a.


## 2026-10-06 — Phase 32 primary data-coverage correction
- Run #31 completed successfully but its result was rejected after artifact audit.
- The artifact contained contract-termination trades whose option data stopped well before the nominal expiry, and a July-2026 contract was traded across a period with missing intervening weekly expiry files.
- NSE circulars confirm NIFTY weekly expiry was Thursday through contracts expiring on/before 28-Aug-2025 and Tuesday for contracts expiring on/after 01-Sep-2025; holiday expiry uses the previous trading day. citeturn751823search12turn751823search13turn751823search0
- The engine now uses that expected weekly calendar and a strict contiguous-complete-data rule. A machine-readable coverage.json is produced with the results.


## 2026-10-06 — Phase 32 historical lot-size audit correction #2
- Cross-check of the initial sample boundary found that the July-2021 monthly NIFTY expiry used the revised 50-lot contract before the August weekly transition.
- Corrected the 29-Jul-2021 monthly exception and invalidated all prior numerical runs.


## 2026-10-06 — Phase 32 final expiry-calendar correction
- Added the historically correct 2025 Monday transition before the permanent Tuesday expiry schedule.
- NSE Circular 33/2025 changed NIFTY weekly expiry from Thursday to Monday effective April 04, 2025; NSE Circular 111/2025 later changed it to Tuesday for contracts expiring on/after September 01, 2025. 
- Final reproduction run will establish the accepted evidence on the final engine revision.


## 2026-10-06 — Phase 32 coverage reconciliation and correction
- External audit of the Hugging Face dataset showed the NIFTY option repository contains later expiry files beyond the first missing week, despite the prior run stopping at the first gap.
- The successful run was therefore reclassified as an execution-valid but sample-truncated diagnostic, not final evidence.
- The engine now continues across missing expiry files and records the exact missing dates.
- The first expiry now uses a seven-day pre-expiry spot window so the entry opportunity is not artificially removed.


## 2026-10-06 — Phase 32 calendar-boundary correction after gap continuation
- The gap-continuation implementation is retained, but contract windows are now bounded by the expected weekly expiry calendar rather than available-file sequence.
- This preserves the current-week definition even when the historical source has a missing expiry file.
- Run #39 is reclassified as diagnostic/non-evidence.
- Corrected commit: cb0001f0e12376d27fa40b113ca47715a15c12cc.


## 2026-10-06 — Phase 38 final control-relative robustness

- Phase 38 was initialized on branch phase-38-corrected-model-robustness to test five Phase-37 polarity-corrected direction selectors against the canonical stateful Phase-32 control.
- GitHub Actions run 37432966945 completed successfully, but its regenerated control did not match the previously accepted canonical artifact. It produced 205 trades / 103 expiries / +₹65,945.47 instead of 206 / 102 / +₹63,672.58.
- Error F38-001 was logged. The accepted Phase-32 control was frozen by SHA-256 artifact fingerprint and expiry-level P&L cache.
- The corrected workflow run 37433424224 used the frozen canonical control for all primary treatment comparisons and independently retained the regenerated control as an audit result.
- Final paired common-expiry sample: 93 expiry blocks.
- Mean selector-minus-control differences were negative for all five selectors; bootstrap probabilities of beating control ranged from 18.11% to 37.63%.
- All five selectors remained positive in the 2026 holdout and remained positive at +50% cost stress, but all failed the incremental-control promotion test.
- All five selectors showed CALL-positive / PUT-negative asymmetry; OOF_STACK was especially asymmetric at 80.8% PUT trades.
- Final decision: reject all five corrected model selectors; retain the canonical stateful direction rule.
- Full manuscript: PHASE38_MANUSCRIPT.md.
- Final status: PHASE38_STATUS.md.


## 2026-10-06 — Phase 38 secondary risk-adjusted comparison

- Calculated cumulative net P&L divided by maximum drawdown for the six strategies.
- Markov-regime tree ranked first at 1.309, CatBoost second at 1.173, and the stateful control third at 1.028.
- The risk-adjusted ranking does not override the preregistered control-relative test; no selector is promoted.
- Saved to results/phase38_corrected_model_robustness/risk_adjusted_summary.csv and added to PHASE38_MANUSCRIPT.md.


## 2026-10-06 — Phase 39 advanced prediction-model discovery initiated

- Phase 35 was audited before opening the new search. It already covered a broad tree/decomposition/probabilistic/adaptive model family, so Phase 39 deliberately changes the prediction formulation instead of repeating a generic classifier sweep.
- Created branch phase-39-advanced-direction-models.
- Registered the primary novel formulation: direct counterfactual CALL-versus-PUT spread P&L margin prediction.
- Registered the Control-Relative Counterfactual Override Learner (CROL): the Phase-38 stateful control remains default and a learned model may override it only when predicted incremental spread P&L is positive with sufficient safety margin and low uncertainty.
- Added candidate families: Bayesian counterfactual margin regression, Bradley-Terry preference learning, dynamic Bayesian logistic/DMA, Gaussian processes, sparse GAM/GA2M, kNN/DTW analogs, BOCPD gates, online Hedge/DMA, foundation-model exploratory track and constrained symbolic regression.
- Added PHASE39_LITERATURE_REVIEW.md, PHASE39_PRE_REGISTRATION.md, PHASE39_RESEARCH_PLAN.md and the candidate-method registry.
- Added an automated preflight workflow with manual dispatch.
- Numerical results have not yet been accepted.


## 2026-10-06 — Phase 40 exhaustive ensemble direction research initiated

- Created branch `phase-40-ensemble-direction-models`.
- Registered the hypothesis that previously tested individual selectors may contain complementary information when combined.
- Registered six experts: CATBOOST, DART, WAVELET_TREE, OOF_STACK, MARKOV_REGIME_TREE and VIX.
- Registered all 63 non-empty expert subsets, four fixed aggregators and seven VIX routing modes: 1,764 candidates.
- Added automatic GitHub Actions workflow with manual dispatch and India VIX caching.
- India VIX is aligned point-in-time using the previous session's close/change; validation freezes the top 10 before untouched 2026 holdout replay.
- Initial engine construction correction F40-001 was logged before numerical evidence.
