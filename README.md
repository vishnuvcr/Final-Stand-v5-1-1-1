# Final Stand v5 1-1-1-1

Systematic options-strategy research repository.

## Latest research status

**Dynamic-n corrected primary research is complete. Stop-loss research is complete through Phase 19.**

### Locked dynamic-n primary

- 190 trades
- Net P&L: **₹138,937.12**
- Net win rate: **94.21%**
- 178 target exits
- 12 expiry exits
- 11 losing trades, all expiry exits
- Maximum drawdown: **₹27,321.08**

Controlled n-selection ablation showed that the 95%-band dynamic-n preference did **not** add incremental aggregate P&L versus fixed n=6 on the same trade universe: fixed n=6 returned ₹139,543.97 versus ₹138,937.12 for dynamic n.

### Stop-loss research

Phase 17 tested 108 pre-registered hard, expiry-day, stagnation, trailing and combined stop rules. No rule both preserved all baseline-positive trades and improved validation P&L.

Phase 18 and Phase 19 tested a narrower expiry-day conditional stop. The final **research candidate for paper/forward validation** is:

> **At 13:30 IST on expiry day, exit all three legs when combined strategy MTM is negative and running MFE since entry is below 0.50 × the original target.**

Walk-forward results for this candidate:

| Period | Net uplift | Baseline-positive trades affected | Stops |
|---|---:|---:|---:|
| Training through 2023-12-31 | +₹1,963.67 | 0 | 1 |
| Validation 2024-01-01 to 2025-12-31 | +₹1,923.59 | 0 | 2 |
| Holdout 2026-01-01 to 2026-09-30 | +₹6,305.15 | 0 | 2 |
| Full sample | +₹10,192.41 | 0 | 5 |

The candidate changes five exits, all baseline losing trades, and leaves every historically profitable baseline trade untouched. It does **not** eliminate any loss completely; it truncates selected expiry losses earlier.

The formal train-selected 13:30 / MFE < 1.0× rule was **not promoted** because its 2026 holdout maximum drawdown increased materially. The 0.50× version is retained as the more conservative robustness candidate.

The no-stop dynamic-n strategy remains the locked primary until the stop candidate is tested with forward/paper execution and real broker fills.

## Phase artifacts

- Phase 17 stop-loss research: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-17-stop-loss-research
- Phase 18 conditional-stop refinement: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-18-conditional-stop-refinement
- Phase 19 walk-forward confirmation: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-19-stop-walk-forward-confirmation
- Final stop-loss conclusion: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/STOP_LOSS_CONCLUSION.md
- Stop-loss manuscript supplement: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/manuscript/STOP_LOSS_EXTENSION_SUPPLEMENT.md
- Walk-forward report: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/results/dynamic_n_corrected/phase19_walk_forward/WALK_FORWARD_SUMMARY.md

## Research governance

All previous superseded dynamic-n numerical results remain marked as obsolete. Execution errors and corrections are logged in `ERROR_LOG.md`; research-phase progress is tracked in `RESEARCH_LOG.md`; the research protocol is maintained in `DYNAMIC_N_RESEARCH_PLAN.md`.

**Phase 19 is the final stop-loss research phase under the current plan.**


## Latest completed phase — Phase 20

Phase 20 compared entry-time payoff-chart/green-area boundary stops against the fixed expiry-day conditional stop.

The boundary family tested 0/50/100/200/400 NIFTY-point buffers, 1/3-minute confirmation, and boundary/MTM/MFE variants. The training-safe selector was 400 points with 1-minute confirmation, but it lost **₹14,390.87** in 2024–2025 validation and **₹49,064.48** in the 2026 holdout, while materially worsening drawdown. Therefore **no payoff-boundary stop is included**.

The fixed Phase-19 comparator was independently reconstructed and cross-checked:
- 13:30 IST on expiry day;
- combined three-leg MTM < ₹0;
- running MFE < 0.50× original target.

Walk-forward uplift: +₹1,963.67 training, +₹1,923.59 validation, +₹6,305.15 holdout, +₹10,192.41 full sample, with zero baseline-positive trades affected.

### Final entry-to-exit rules

The final historical rules are recorded on the Phase-20 branch:
- [Final strategy rules](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/FINAL_STRATEGY_RULES.md)
- [Final strategy specification](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/STRATEGY_SPEC.md)
- [Phase 20 supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/manuscript/PHASE20_PAYOFF_BOUNDARY_SUPPLEMENT.md)
- [Phase 20 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/results/dynamic_n_corrected/phase20_payoff_boundary/BOUNDARY_STOP_CONCLUSION.md)

Final historical result over 190 corrected trades:
- Net P&L: **₹149,129.53**
- Mean net/trade: **₹784.89**
- Net winning trades: **179/190 (94.21%)**
- Profit factor: **2.34**
- Maximum cumulative drawdown: **₹27,336.11**
- Target exits: **178**
- Conditional-stop exits: **5**
- Expiry-fallback exits: **7**

This is historical research evidence, not a guarantee of future or live performance. Forward/paper execution validation remains separate from the historical research.

## Phase 21 status — pre-expiry risk-control research

Phase 21 is being evaluated on isolated branch `phase-21-pre-expiry-adverse-move-risk-control`. It tests bounded early exits and one-lot OTM-(n+3) tail-hedge repairs against the frozen Phase-20 strategy. The canonical strategy remains unchanged unless the pre-registered walk-forward promotion screen is passed.


## Phase 21 final status — pre-expiry adverse-move control

Phase 21 is complete. The pre-registered 200–600 point direction-aware early-exit and one-lot OTM-(n+3) hedge families produced **no candidate that satisfied the training safety constraint of zero profitable baseline trades affected**. The closest candidate (600-point / 1-minute / spot-only early exit) improved training by ₹1,885.47 but lost ₹33,923.36 in 2024–2025 validation and ₹44,039.53 in the 2026 holdout, while full-sample maximum drawdown rose to ₹52,740.01. **No Phase-21 rule is promoted; the Phase-20 final strategy remains the canonical historical specification.**

Phase-21 research files are isolated on branch `phase-21-pre-expiry-adverse-move-risk-control` and draft PR #2.


## Phase 23 final status — entry-filter research

Phase 23 tested BULLISH-only entry filters after Phase 22 found that all 11 historical losses were in the BULLISH/put structure, while all 18 BEARISH/call trades were profitable. The BULLISH subgroup also contained 161 winners, and no pre-registered BULLISH-only filter could remove at least two training losses while retaining 95% of winners and improving training P&L. The top unconstrained diagnostic (BULLISH direction margin ≥ 0.15) removed 12 winners and only 1 loss and was strongly negative out of sample. **No entry filter is promoted; the Phase-20 strategy remains canonical.**

Phase 23 artifacts are isolated on branch `phase-23-conditional-bullish-entry-filter` and draft PR #4.

## Phase 22 final status — entry-filter research

Phase 22 tested pre-entry filters using payoff-buffer geometry, direction confidence, structure quality and pre-entry NIFTY regime. **No candidate passed the pre-registered safety screen.** No tested filter removed even one training loss without also removing a profitable training trade. The Phase-20 canonical strategy therefore remains unchanged.

See the Phase-22 draft PR and branch for the complete grid and manuscript supplement.


## Final research closeout — Phase 24 complete

The preregistered research phases are complete. Phase 23 and Phase 24 did not produce an out-of-sample improvement that passed the registered promotion gates. The **Phase-20 canonical dynamic-n strategy remains the final historical entry-to-exit specification**.

Final historical result: **190 trades, ₹149,129.53 net P&L, 179/190 profitable trades (94.21%), profit factor 2.34, maximum drawdown ₹27,336.11** under the research execution-cost model.

- [Final strategy rules](FINAL_STRATEGY_RULES.md)
- [Final strategy specification](STRATEGY_SPEC.md)
- [Final research manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/manuscript/FINAL_RESEARCH_MANUSCRIPT.md)
- [Phase 23 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/results/dynamic_n_corrected/phase23_entry_state/PHASE23_CONCLUSION.md)
- [Phase 24 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/results/dynamic_n_corrected/phase24_targeted_reversal/PHASE24_CONCLUSION.md)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/DYNAMIC_N_RESEARCH_PLAN.md)
- [Error log](ERROR_LOG.md)

## Phase 25 — alternative direction chooser

Phase 25 tested alternative option-price, IV, OI/volume, NIFTY and cross-market direction choosers while holding the rest of the final strategy fixed. **No alternative passed the preregistered training/OOS gates; OTM6/7/8 remains the direction chooser.**

- [Phase 25 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-25-direction-chooser-alternatives/results/dynamic_n_corrected/phase25_direction_chooser/PHASE25_CONCLUSION.md)
- [Phase 25 manuscript supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-25-direction-chooser-alternatives/manuscript/PHASE25_DIRECTION_CHOOSER_SUPPLEMENT.md)

## Phase 27 — Delta-based exit research — COMPLETE

Phase 27 tested portfolio-delta-based profit booking and adverse-delta stops against the locked Phase-20 strategy. Delta coverage was **99.21%**. The training-selected rule (MTM ≥ 0.90×target and |portfolio delta| ≤ 0.05) produced **−₹2,334.04** validation uplift and **−₹1,108.04** 2026 holdout uplift. The holdout bootstrap 95% CI for mean trade-level uplift was **−₹141.92 to −₹13.82**. **No delta exit is promoted; Phase-20 remains canonical.**

- [Phase 27 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-27-delta-exit-research)
- [Phase 27 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-27-delta-exit-research/PHASE27_STATUS.md)
- [Phase 27 supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-27-delta-exit-research/manuscript/PHASE27_DELTA_EXIT_SUPPLEMENT.md)

## Phase 28 — individual-leg delta research — COMPLETE

Phase 28 directly tested **per-leg delta**, especially the short OTM-(n+1) and OTM-(n+2) legs, rather than portfolio delta. The Phase-20 strategy remained frozen as control.

- Delta coverage: **99.21%**.
- Training-selected rule: S1 |delta| ≤ 0.05 after MTM ≥ 90% of target.
- Training uplift: **−₹2,998.16**.
- 2024–2025 validation uplift: **−₹2,487.05**.
- 2026 holdout uplift: **−₹35.91**.
- Full-sample uplift: **−₹5,521.12**.
- No adverse short-leg delta stop was promoted.

**Decision: reject individual-leg absolute-delta exit rules. Phase-20 remains canonical.**

- [Phase 28 pre-registration](PHASE28_PRE_REGISTRATION.md)
- [Phase 28 status](PHASE28_STATUS.md)
- [Phase 28 supplement](manuscript/PHASE28_INDIVIDUAL_LEG_DELTA_SUPPLEMENT.md)
- [Phase 28 results](results/dynamic_n_corrected/phase28_leg_delta_exit/)


## Phase 29 — short-leg delta-change exit research — COMPLETE / REJECTED

Phase 29 tested the requested exit mechanism: target and stop entirely from individual or combined short-leg delta change, with the target-percentage criterion removed. No portfolio-delta or absolute-delta level trigger was used.

- Delta coverage: **99.21%**
- Selected target: **MEAN short-leg delta change, 5-minute lookback, 0.20 threshold, 3-minute confirmation**
- Selected stop: **S1 short-leg delta change, 1-minute lookback, 0.05 threshold, 3-minute confirmation**; zero uplift
- Versus canonical Phase 20: **−₹1,092.14 validation** and **−₹6,879.84 2026 holdout**
- **Decision: NO PROMOTION. Phase 20 remains canonical.**

Artifacts: [Phase 29 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-29-delta-change-exit-research) · [status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-29-delta-change-exit-research/PHASE29_STATUS.md) · [manuscript supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-29-delta-change-exit-research/manuscript/PHASE29_DELTA_CHANGE_SUPPLEMENT.md) · [conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-29-delta-change-exit-research/results/dynamic_n_corrected/phase29_delta_change_exit/PHASE29_CONCLUSION.md)


## Phase 30 — corrected entry-referenced delta-proportion research — OPEN

A new isolated research phase was registered after correcting the intended delta definition. Phase 30 uses the **sum of the two short-option deltas at entry** as the fixed reference and measures later movement as a **proportion of that entry value**. It does not use prior-minute lookbacks, delta differences, or a mean of the short legs.

- [Phase 30 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-30-entry-delta-proportion-exit)
- [Phase 30 pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/PHASE30_PRE_REGISTRATION.md)
- [Phase 30 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/PHASE30_STATUS.md)

The numerical phase remains open pending successful GitHub Actions execution. No result is inferred from workflow-dispatch unavailability.


## Phase 30 — COMPLETE / REJECTED

Phase 30 tested entry-referenced proportional movement in the combined absolute delta of the two short option legs. GitHub Actions execution completed successfully (run 37228084351), with 99.21% delta coverage. The training-selected rule failed both validation and 2026 holdout against the frozen Phase-20 canonical strategy and is rejected.

- [Phase 30 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-30-entry-delta-proportion-exit)
- [Phase 30 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/PHASE30_STATUS.md)
- [Phase 30 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/results/dynamic_n_corrected/phase30_entry_delta_proportion_exit/PHASE30_CONCLUSION.md)


## Phase 32 — Continuous Delta 6x6 Vertical Spread — INITIALIZED

A separate research branch has been created for the user-specified Tradetron strategy:

- Branch: [phase-32-continuous-delta-6x6-backtest](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-32-continuous-delta-6x6-backtest)
- Strategy: 6-lot-per-leg, 50-point weekly vertical spread using a +0.25 CE / -0.25 PE short-leg delta entry and short-leg delta exits at 0.50 or 0.04 magnitude boundaries.
- Direction engine: start CALL; keep direction after a winning trade; flip after a losing trade.
- Entries: from 09:20 IST, blocked on weekly expiry day.
- No universal 15:25 daily square-off.
- No discretionary rollover.
- Primary historical backtest resolution: 1-minute, because the public primary data used by this repository are 1-minute.

Phase-32 artifacts:
- [Research plan](PHASE32_RESEARCH_PLAN.md)
- [Pre-registration](PHASE32_PRE_REGISTRATION.md)
- [Strategy specification](PHASE32_STRATEGY_SPEC.md)
- [Status](PHASE32_STATUS.md)
- [Manual workflow](.github/workflows/phase-32-continuous-delta-6x6-backtest.yml)

**Numerical backtest has not yet been accepted as evidence.** The branch is initialized and the strategy specification is frozen before numerical execution. The Phase-20 dynamic-n strategy remains the canonical historical strategy for the main research line.


### Phase 32 execution correction — 2026-10-06
- An implementation audit found that the initial expiry enumeration excluded monthly expiries. Because the frozen rule is current weekly expiry, monthly expiry weeks must be included.
- The affected runs are not accepted as evidence.
- Corrected engine commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/d1b44be28b87b2d6a264cc6ddcd72d3a551a9a2f
- Corrected run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37383091606
- Phase 32 remains open pending a successful corrected numerical run and audit of its artifacts.


### Phase 32 execution-convention correction — 2026-10-06
- The 1-minute engine initially allowed fresh entries in the final 120 seconds before market close, contrary to the live execution convention.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/1513a1c00df8693ea630f6dae52d67a28164c1c7
- All earlier Phase-32 runs remain non-evidence.


### Phase 32 state-machine correction — 2026-10-06
- A serious lookahead/re-entry flaw was discovered and corrected before accepting any numerical evidence.
- The engine now enforces strict chronological occupation of a position and only permits the next entry after the realized exit timestamp.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/df8f9c0ca6e3fd3f84bcd6bd9c432f0b03ea171e
- All earlier Phase-32 runs are invalid and will not be used.


### Phase 32 implementation regression correction — 2026-10-06
- Run 37384048259 failed before numerical execution because the state-machine rewrite omitted the option `expiry_ts` field.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/81b83fb4af8f075a9fec2bab42304a7c8964b45a
- No evidence from the failed run is used.


### Phase 32 lot-size audit correction — 2026-10-06
- Historical NIFTY lot-size transitions are now applied by expiry cycle using NSE's published transition dates rather than a coarse calendar cutoff.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/a29a17470b751c947ba1aa0f8c7ed6d3abfc6e13
- Earlier Phase-32 numerical runs are not evidence.


### Phase 32 zero-net state correction — 2026-10-06
- Corrected a final state-machine mismatch: exact zero net P&L now preserves direction as pre-registered.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/559f520ba7feb795e2b09fd6ab17bfc083fd7ba0
- The pre-correction candidate is not accepted as evidence.


### Phase 32 historical lot-size correction — 2026-10-06
- Corrected the 30-Jan-2025 NIFTY monthly contract multiplier from 75 to the actual 25-lot existing monthly size.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/29458cacb40eab39cdd96c1b57881a70b1829b74
- All pre-correction Phase-32 runs remain non-evidence.


### Phase 32 current-week expiry correction — 2026-10-06
- The engine was corrected so a weekly option contract is only traded after the previous expiry has terminated and before the current expiry, matching the literal current-week rule.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/1675f86b8a71add7a73c03479731e3a5623716b
- All prior Phase-32 runs remain invalid/non-evidence.


### Phase 32 computational optimization — 2026-10-06
- Exit-delta calculation was vectorized across each trade's future 1-minute path without changing the frozen strategy rules.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/c0ec4b90fd33eee75ed0515343e28d431aee924a


### Phase 32 primary-sample coverage correction — 2026-10-06
- Run #31 completed successfully but was rejected after artifact audit because missing/incomplete expiry files contaminated the later current-week windows.
- The corrected engine now uses the NSE expiry-day calendar and stops at the first missing or incomplete weekly expiry path.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/a529ed4bd2519f2a47607ad53dd09ff522068c3b
- Run #31 artifacts remain retained for audit only.


### Phase 32 July-2021 lot-size correction — 2026-10-06
- Corrected the 29-Jul-2021 NIFTY monthly contract multiplier from 75 to 50 in accordance with NSE Circular 28/2021.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/d13af44516adec61ea0015eca2ab361fad5c9c2c
- All pre-correction Phase-32 runs remain non-evidence.


### Phase 32 final expiry-calendar correction — 2026-10-06
- Historical NIFTY weekly expiry logic now includes the temporary Monday schedule in April-August 2025 before the permanent Tuesday schedule.
- Final reproduction is being run on the corrected engine; the accepted 2021 result is not affected by this out-of-sample calendar correction.


### Phase 32 coverage reconciliation — 2026-10-06
- The first successful run was sample-truncated because the engine stopped at the first missing 04-Nov-2021 expiry even though later expiries exist.
- Corrected engine: process all available expiries and log missing/incomplete dates; first expiry now has a valid pre-expiry window.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/977913fa176bc5c826bb00bcb5684e61bc6c912f
- Prior P&L remains non-evidence for the phase conclusion.


### Phase 32 calendar-boundary correction — 2026-10-06
- Run #39 was rejected because missing expiry files could enlarge the next contract's historical window.
- Corrected engine: every contract window is anchored to the immediately preceding expected expiry date, not the last processed file.
- Corrected commit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/cb0001f0e12376d27fa40b113ca47715a15c12cc

## Phase 37 — corrected model direction polarity

**Initialized — numerical execution pending.** A post-acceptance audit found that Phase 36 mapped model probability of an NIFTY up/bullish expiry move to the CALL spread. The corrected mapping is **bullish/up -> PUT spread; bearish/down -> CALL spread**.

Phase 37 reruns only CATBOOST, DART, WAVELET_TREE, OOF_STACK and MARKOV_REGIME_TREE with the cached Phase-35 forecasts. No model, threshold, feature, execution rule, cost assumption or holdout definition is changed.

- [Phase 37 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-37-model-direction-polarity-correction)
- [Research plan](PHASE37_RESEARCH_PLAN.md)
- [Pre-registration](PHASE37_PRE_REGISTRATION.md)
- [Strategy specification](PHASE37_STRATEGY_SPEC.md)
- [Status](PHASE37_STATUS.md)
- [Corrected engine](research/phase37_model_direction_polarity_correction.py)
- [Workflow](.github/workflows/phase-37-model-direction-polarity-correction.yml)

Phase 36 model-selector P&L remains retained as an audit artifact but is not treated as a valid test of the intended polarity hypothesis.


## Phase 38 — corrected model robustness vs stateful control — COMPLETE / REJECTED

Phase 38 tested the five Phase-37 polarity-corrected model direction selectors against the frozen canonical Phase-32 stateful control. The phase used 10,000 deterministic paired expiry bootstrap resamples, 2024/2025/2026 splits, +25/+50/+100% cost stress, and CALL/PUT asymmetry analysis.

**Final result: none of the five selectors is promoted. The canonical stateful direction rule remains unchanged.**

| Selector | Net P&L | 2026 holdout | Mean Δ vs control / expiry | P(selector > control) |
|---|---:|---:|---:|---:|
| CATBOOST | ₹57,874.80 | ₹49,054.33 | -₹200.98 | 37.63% |
| MARKOV_REGIME_TREE | ₹53,060.31 | ₹41,969.35 | -₹252.75 | 34.37% |
| WAVELET_TREE | ₹31,294.89 | ₹50,776.68 | -₹486.79 | 23.19% |
| OOF_STACK | ₹24,765.71 | ₹48,345.59 | -₹557.00 | 20.18% |
| DART | ₹19,372.11 | ₹39,053.96 | -₹614.99 | 18.11% |

All five selectors were positive in the 2026 holdout and at +50% transaction-cost stress, but every paired point estimate favored the control and every bootstrap interval crossed zero. Every selector also showed positive CALL-side P&L and negative PUT-side P&L.

A control-reproducibility discrepancy was detected and logged as F38-001: a fresh Phase-32 reconstruction produced 205 trades / 103 expiries / ₹65,945.47 rather than the frozen canonical 206 / 102 / ₹63,672.58. The frozen canonical artifact is therefore authoritative for Phase-38 treatment comparisons.

- [Phase 38 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-38-corrected-model-robustness)
- [Phase 38 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/PHASE38_STATUS.md)
- [Phase 38 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/PHASE38_MANUSCRIPT.md)
- [Phase 38 paired bootstrap](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/results/phase38_corrected_model_robustness/paired_bootstrap.csv)
- [Phase 38 cost stress](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/results/phase38_corrected_model_robustness/cost_stress.csv)
- [Phase 38 control audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/results/phase38_corrected_model_robustness/control_validation.json)
- [Phase 38 pull request #12](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/12)

**Next research priority:** Phase 39 robustness of the canonical stateful strategy with broker-realistic bid/ask, latency, fill probability, and expanded cost/slippage stress.


## Phase 39 — advanced counterfactual direction models — ACTIVE

Phase 39 changes the prediction target from NIFTY expiry direction to the actual economic decision: the post-cost P&L difference between CALL and PUT Continuous Delta 6x6 spreads at the same entry opportunity.

- [Phase 39 research plan](PHASE39_RESEARCH_PLAN.md)
- [Phase 39 pre-registration](PHASE39_PRE_REGISTRATION.md)
- [Phase 39 literature review](PHASE39_LITERATURE_REVIEW.md)
- [Phase 39 status](PHASE39_STATUS.md)
- [Phase 39 workflow](.github/workflows/phase-39-advanced-direction-models.yml)
- [Phase 39 fixed-opportunity engine](research/phase39_counterfactual_engine.py)

**Step 1 is under corrected rerun:** the first 206-trade counterfactual calculation reconstructed the frozen control essentially exactly, but it was superseded before model training because the preregistered development period extends through 2023. The corrected engine now combines 271 development trades from the accepted Phase-32 artifact with the exact frozen 206-trade validation/holdout panel, while excluding the 2024-01-04 trade to preserve comparator identity. It also uses deterministic stable quote-row deduplication.

No model training or strategy promotion is permitted until the corrected panel passes its control reconstruction audit.

The canonical Phase-38 stateful strategy remains unchanged and authoritative during this phase.
