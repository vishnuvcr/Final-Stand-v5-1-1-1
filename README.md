## Phase 50B — Expanded Prior-Strategy Universe — IN PROGRESS

Phase 50B is the bounded continuation after Phase 50. It includes the user's seven supplied Tradetron strategies and previously developed strategy lineages discovered across the user's GitHub repositories.

- [Phase 50B research plan](PHASE50B_RESEARCH_PLAN.md)
- [Phase 50B strategy universe](PHASE50B_STRATEGY_UNIVERSE.md)
- [Phase 50B pre-registration](PHASE50B_PRE_REGISTRATION.md)
- [Phase 50B status](PHASE50B_STATUS.md)
- [Phase 50B source/baseline audit](PHASE50B_SOURCE_BASELINE_AUDIT.md)
- [Phase 50B literature review](PHASE50B_LITERATURE_REVIEW.md)
- [Phase 50B chat log](PHASE50B_CHAT_LOG.md)
- [Phase 50B 2026 execution-cost audit](PHASE50B_2026_COST_AUDIT.md)
- [TT-04 source audit](PHASE50B_TT04_SOURCE_AUDIT.md)

### Current strongest new VIX hypothesis

**TT-02 — 0.20/0.10 Delta Calendar Hedge Spread v4**

Its finished native Tradetron report shows a positive HIGH-VIX outcome-day diagnostic, but the report uses a different coverage/cost model and therefore is not accepted Final Stand evidence. The canonical common-cost TT-02 replay is currently running under Actions run **37572837253**; registry preflight has passed. The current replay includes the performance-only delta-selection correction logged as F50B-012; no result from the superseded slower run is accepted.

Older duplicate Phase-50B runs are classified **SUPERSEDED / NON-EVIDENCE**. The standalone TT-02 workflow is now manual-only to avoid repeated automatic executions.

### Prior strategy universe now included

The registry explicitly includes:
Dynamic Ratio Reversals; 0.20/0.10 Delta Calendar Hedge Spread v4; Corrected Dynamic-n NIFTY Weekly Options; Profit Breakout Premium Match Straddle; Simple Intraday Short Straddle; Intraday Asym Premium; Dynamic IC to Ratio; Iron-condor-to-ratio v1/v2; Option-intraday-v1; NoDip-Stage-1; BATMAN MC1/MC2/MC3; Final-stand-v4/v2; and the relevant Daily-Options VIX/weekly strategy lineages.

---

## Phase 50 — VIX × Far-OTM Tail Geometry — CLOSED / NO PROMOTION

Phase 50 is closed. The authoritative numerical run **37567632928** completed successfully; its generic workflow audit failed only on sparse-HIGH early-stop packaging and was independently reconciled from artifact **11459959883**.

No confirmatory candidate survived. HIGH VIX had only **6 development opportunities** under the fixed 10:00 / 4-DTE control, below the registered 15-observation gate. Five sparse-HIGH exploratory cells were carried forward.

The most interesting exploratory result was far-OTM Put BWB. In the protected 2026 holdout, distance 4 produced **+₹9,814.49 net / +₹9,521.73 stressed across 4 trades**, but this remains strictly exploratory. Far-OTM Iron Condors were negative in both validation and holdout.

- [Phase 50 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50-vix-far-otm-tail-geometry/PHASE50_STATUS.md)
- [Phase 50 closeout reconciliation](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50-vix-far-otm-tail-geometry/PHASE50_CLOSEOUT_RECONCILIATION.md)

---
## Phase 49 — VIX Leader Parameter Tuning — CLOSED / NO PROMOTION

Phase 49 is complete. The study evaluated 720 raw geometries, expanded to 1,440 geometry×VIX-regime candidates across LOW and NORMAL India-VIX states, using 133 development expiry blocks (2021–2023), 102 validation expiry blocks (2024–2025), and 21 protected holdout expiry blocks.

Final gate: 2 candidates frozen, 1 validation economic pass, 0 Holm-adjusted statistical survivors, 1 protected holdout confirmation, and NO PROMOTION. The canonical strategy is unchanged.

The strongest research candidate was the LOW-VIX Bear Put Debit Spread: 09:30 IST, 5 trading sessions before expiry, buy PE +1 modal strike step, sell PE -3 steps, width 4 steps. Validation net was ₹28,848.48 and +50% cost-stress net was ₹27,246.47 across 42 active LOW-VIX trades. Active-vs-complement inference remained non-confirmatory (p=0.2260; Holm p=0.4520; 95% CI crossed zero). The protected holdout had 5 trades, ₹27,278.50 net, ₹27,051.63 stressed, and 80% wins; this is encouraging but underpowered.

The tuned Put Broken-Wing Butterfly was rejected: -₹43,963.84 validation net and -₹16,356.40 on the 2026 holdout.

- [Phase 49 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/PHASE49_RESEARCH_PLAN.md)
- [Phase 49 pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/PHASE49_PRE_REGISTRATION.md)
- [Phase 49 final status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/PHASE49_STATUS.md)
- [Phase 49 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/results/phase49_vix_tuning/PHASE49_MANUSCRIPT.md)
- [Phase 49 final decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/results/phase49_vix_tuning/phase49_final_decision.json)
- [Automatic closeout reconciliation run #2](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37544951498)

---
## Phase 48 — Independent Multi-Expiry VIX Data Bridge — CLOSED / NO PROMOTION

Phase 48 successfully repaired the multi-expiry data limitation identified in Phase 47 by using an independent NIFTY intraday option source with multiple expiries on the same trade date. The final corrected run contains **124 accepted trade rows** across three registered baselines.

One validation working candidate survived the economic screen: **Covered Call 2.0 option-only proxy + LOW VIX** (30 validation trades, +₹10,327 net; +₹6,786 at +50% fee/charge stress). The protected 2026 confirmation was +₹2,754 net / +₹2,114 stressed across 6 trades.

However, the active-vs-rest bootstrap 95% CI crossed zero, permutation p=0.2718, Holm-adjusted p=1.0, and drawdown was very large relative to the mean trade. The other two baselines were negative in validation. **No strategy is promoted and the canonical Phase-20/42 strategy is unchanged.**

Critical self-audits that materially affected validity included UTC-to-IST timestamp normalization, point-in-time spot bridging, and historical NIFTY lot-size correction. Earlier Phase-48 numerical results were explicitly rejected and only the post-correction run is accepted.

- [Phase 48 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-48-multiexpiry-vix-source-bridge)
- [Phase 48 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-48-multiexpiry-vix-source-bridge/PHASE48_STATUS.md)
- [Phase 48 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-48-multiexpiry-vix-source-bridge/PHASE48_RESEARCH_PLAN.md)
- [Phase 48 final decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-48-multiexpiry-vix-source-bridge/results/phase48_multiexpiry/final_decision.json)
- [Phase 48 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-48-multiexpiry-vix-source-bridge/results/phase48_multiexpiry/PHASE48_MANUSCRIPT.md)

---

## Phase 47 — VIX source-strategy numerical backtest — CLOSED / DATA FEASIBILITY

Phase 47's self-audited numerical work established a key data limitation: the cached thetrademarkk/india-index-options-1m source does not provide next-expiry entry-time observations for most historical dates, preventing a scientifically complete test of Calendar and Monthly Wide-Range Hedge structures. The Covered Call 2.0 option-only proxy produced only 20 rows and is not promotable.

Two attempted numerical runs were explicitly rejected by self-audit; no incomplete result entered the evidence base.

Phase 47 therefore closes with **NO PROMOTION**. The next phase uses an independent multi-expiry intraday dataset for a supplementary 2024Q4/2025/2026 study.

- [Phase 47 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-47-vix-source-strategy-backtest)
- [Phase 47 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-47-vix-source-strategy-backtest/PHASE47_STATUS.md)
- [Phase 47 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-47-vix-source-strategy-backtest/PHASE47_RESEARCH_PLAN.md)

---
## Phase 47 — VIX source-strategy numerical backtest — INITIALIZED

Phase 47 converts a finite subset of the Phase-46 YouTube discoveries into reproducible NIFTY tests while retaining **LOW, NORMAL and FALLING** VIX states alongside **RISING, HIGH, SPIKE and HIGH_RISING**.

Registered candidates:
- Double Calendar Straddle.
- Profit Breakout Monthly Wide-Range Hedge (30-delta reconstruction with next-month ATM hedge).
- Profit Breakout Covered Call 2.0 option-only synthetic-future proxy (diagnostic until futures equivalence is verified).

The workflow is staged with compile, preflight, numerical, artifact and holdout audits. Four pre-numerical defects were already caught and corrected: timezone normalization, multi-window cache keys, variant grouping, and nondeterministic inference seeds. No numerical evidence from those superseded snapshots is accepted.

- [Phase 47 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-47-vix-source-strategy-backtest)
- [Phase 47 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-47-vix-source-strategy-backtest/PHASE47_RESEARCH_PLAN.md)
- [Phase 47 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-47-vix-source-strategy-backtest/PHASE47_STATUS.md)
- [Phase 47 literature review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-47-vix-source-strategy-backtest/PHASE47_LITERATURE_REVIEW.md)
- [Phase 47 numerical engine](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-47-vix-source-strategy-backtest/research/phase47_vix_source_backtest.py)
- [Phase 47 workflow](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-47-vix-source-strategy-backtest/.github/workflows/phase-47-vix-source-strategy-backtest.yml)

---

## Phase 46 scope expansion — Profit Breakout + full VIX panel

The user-designated **Profit Breakout** YouTube channel has been incorporated as a dedicated source stream. Nine directly relevant indexed videos were added to the Phase-46 source ledger, including explicit India-VIX strategy selection, Batman/VIX filtering, Iron Fly versus Iron Condor by volatility, adaptive Iron Fly→Iron Condor management, VIX-adapted monthly strategy, hedged weekly/monthly credit structures and longer-duration NIFTY income structures.

**Research scope correction:** the new search will **not abandon LOW/NORMAL VIX**. Every reconstructable candidate from Profit Breakout and the broader video search will be evaluated across **ALL, LOW, NORMAL, FALLING, RISING, HIGH, SPIKE and HIGH_RISING**, with routing/transition rules tested only after the cross-regime baseline is established. This avoids assuming in advance that a strategy belongs only to a high-VIX regime.

Key new hypotheses include Put Ratio Backspread, Calendar Trap/Calendar Spread, Long Straddle/Strangle, Reverse Iron Condor/Long Iron Butterfly, post-spike VIX-reversal short-volatility structures, Batman with VIX filter, Iron Fly↔Iron Condor adaptive switching, VIX-adapted monthly option structures, and skew/IV-VIX divergence routing.

- [Updated Phase 46 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-46-vix-youtube-strategy-discovery/PHASE46_RESEARCH_PLAN.md)
- [Profit Breakout + video source ledger](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-46-vix-youtube-strategy-discovery/PHASE46_YOUTUBE_SOURCE_LEDGER.md)
- [Phase 46 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-46-vix-youtube-strategy-discovery/PHASE46_STATUS.md)

---

# Phase 46 — YouTube/Public-Video VIX Strategy Discovery — COMPLETE (Discovery Only)

Phase 46 was opened to address the remaining **RISING, HIGH, SPIKE and HIGH_RISING** India-VIX gaps after Phases 43–45 found their strongest evidence in LOW/NORMAL VIX.

A broad indexed YouTube/web search was performed across India VIX, high/rising VIX, high IV, VIX spikes, backspreads, calendar/diagonal structures, long volatility, iron condors/iron butterflies, volatility skew and VIX term-structure queries. Ten directly relevant video/public-source leads were recorded.

### Highest-priority new hypotheses

1. **Put Ratio Backspread / Put Backspread + RISING/HIGH VIX**
2. **Calendar Trap / Calendar Spread + HIGH/RISING VIX**
3. **Long Straddle / Long Strangle + HIGH/RISING/SPIKE VIX**
4. **Reverse Iron Condor / Long Iron Butterfly + volatility expansion**
5. **High-VIX spike followed by VIX reversal → defined-risk short-volatility structures**
6. **Volatility-skew routing** and **IV-versus-VIX divergence** as secondary filters

No Phase-46 numerical backtest has been run and no strategy has been promoted. YouTube claims are discovery inputs only; they do not enter the evidence hierarchy until independently tested under the project's development/validation/untouched-2026 framework.

**Important:** the scan is broad and reproducible but cannot literally guarantee retrieval of every YouTube video because public search exposes indexed/ranked results rather than a complete corpus.

- [Phase 46 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-46-vix-youtube-strategy-discovery)
- [Phase 46 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-46-vix-youtube-strategy-discovery/PHASE46_RESEARCH_PLAN.md)
- [YouTube/source ledger](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-46-vix-youtube-strategy-discovery/PHASE46_YOUTUBE_SOURCE_LEDGER.md)
- [Phase 46 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-46-vix-youtube-strategy-discovery/PHASE46_STATUS.md)
- [Phase 46 literature/source review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-46-vix-youtube-strategy-discovery/PHASE46_LITERATURE_REVIEW.md)

---

## Phase 41 — COMPLETE / NO PROMOTION

Phase 41 tested 24 pre-registered regime-conditional economic-margin policies. Zero candidates passed the development/validation selection gate. The three frozen diagnostics produced zero overrides across the entire 477-opportunity development/validation/2026 counterfactual panel, so exact sequential replay was identical to the canonical control. The canonical strategy remains unchanged.

See PHASE41_MANUSCRIPT.md and results/phase41_regime_policy/final_decision.json.

# Final Stand v5 1-1-1-1

Systematic options-strategy research repository.

## Latest research status


### Phase 39 — FINAL CLOSEOUT: counterfactual direction learning rejected for promotion

Phase 39 completed the advanced direction-selection program on `phase-39-advanced-direction-models`.

**Accepted strongest candidate:** Sparse-GAM Control-Relative Counterfactual Override policy.

| Metric | Result |
|---|---:|
| Fixed opportunities | 477 |
| Development / validation / holdout | 271 / 172 / 34 |
| Sequential policy trades | 479 |
| Overrides | 7 |
| 2024–2025 validation uplift | **+₹17,983.53** |
| 2026 holdout uplift | **+₹7,390.39** |
| Holdout drawdown: policy vs control | **₹29,936 vs ₹37,327** |
| +50% cost-stress uplift: validation / holdout | **+₹17,799 / +₹7,546** |
| +100% cost-stress uplift: validation / holdout | **+₹17,615 / +₹7,702** |
| Development uplift | **−₹18,175.07** |

**Decision: no promotion.** The positive out-of-sample contribution comes from only seven overrides, the development contribution is negative, and the paired-expiry validation interval crosses zero. The canonical Phase-32 stateful direction rule therefore remains unchanged.

The new economic-margin idea is retained as a research candidate for a future phase/forward-validation study.

- [Phase 39 status](PHASE39_STATUS.md)
- [Phase 39 pre-registration](PHASE39_PRE_REGISTRATION.md)
- [Phase 39 research plan](PHASE39_RESEARCH_PLAN.md)
- [Phase 39 manuscript](manuscript/PHASE39_MANUSCRIPT.md)
- [Phase 39 error log](ERROR_LOG.md)
- [Phase 39 propensity-matched scoring](results/phase39_propensity/summary.json)

[Phase 39 final conclusion](PHASE39_CONCLUSION.md)

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


## Phase 40 — exhaustive ensemble direction selection with VIX — COMPLETE / NOT PROMOTED

Phase 40 exhaustively screened **1,764 pre-registered combinations**: 63 non-empty subsets of five prior direction selectors plus India VIX × four aggregators × seven VIX routing modes. Equivalent expiry-level signal sequences were deduplicated to 306 unique validation policies before the untouched holdout.

- [Phase 40 manuscript](PHASE40_MANUSCRIPT.md)
- [Phase 40 status](PHASE40_STATUS.md)
- [Phase 40 research plan](PHASE40_RESEARCH_PLAN.md)
- [Phase 40 pre-registration](PHASE40_PRE_REGISTRATION.md)
- [Phase 40 literature review](PHASE40_LITERATURE_REVIEW.md)
- [Phase 40 automated workflow](.github/workflows/phase-40-ensemble-direction-models.yml)
- [Exhaustive validation grid](results/phase40_ensemble/grid_validation.csv)
- [Fixed-opportunity inference](results/phase40_ensemble/inference_top10.csv)
- [Exact stateful replay](results/phase40_ensemble/sequential_top10.csv)
- [India VIX cache](data/phase40_vix/india_vix.csv)

**Final finding:** The strongest validation policy was **CATBOOST + HIGH India VIX gate with canonical fallback**. Exact stateful replay produced **+₹20,691.98** validation uplift and **+₹13,072.75** untouched 2026 holdout uplift versus the frozen control. The holdout 95% confidence interval crosses zero and the one-sided sign-flip p-value is **0.4006**. No policy passed the promotion gate.

**Phase 40 decision: PROMISING / INCONCLUSIVE — NOT PROMOTED.** The canonical stateful strategy remains unchanged.

## Phase 39 — advanced counterfactual direction models — ACTIVE

Phase 39 changes the prediction target from NIFTY expiry direction to the actual economic decision: the post-cost P&L difference between CALL and PUT Continuous Delta 6x6 spreads at the same entry opportunity.

- [Phase 39 research plan](PHASE39_RESEARCH_PLAN.md)
- [Phase 39 pre-registration](PHASE39_PRE_REGISTRATION.md)
- [Phase 39 literature review](PHASE39_LITERATURE_REVIEW.md)
- [Phase 39 status](PHASE39_STATUS.md)
- [Phase 39 workflow](.github/workflows/phase-39-advanced-direction-models.yml)
- [Phase 39 fixed-opportunity engine](research/phase39_counterfactual_engine.py)
- [Phase 39 Step 1 conclusion](results/phase39_counterfactual/PHASE39_STEP1_CONCLUSION.md)
- [Phase 39 counterfactual summary](results/phase39_counterfactual/summary.json)

**Step 1 — COMPLETE / ACCEPTED.** The corrected engine generated 477 fixed opportunities: 271 development trades / 135 expiries, 172 validation trades / 82 expiries, and 34 untouched 2026 holdout trades / 20 expiries. The exact frozen validation+holdout control remains **₹63,672.5753**, with maximum control reconstruction error below **2e-12 rupees**.

The action-aware counterfactual panel shows a strong regime shift: mean CALL-minus-PUT net P&L is **-₹320.53** in development, **+₹386.77** in validation, and **+₹3,386.31** in the untouched holdout. This does **not** constitute a model or trading-policy result; it is the fixed-opportunity target used for chronological model fitting.

The canonical Phase-38 stateful strategy remains unchanged. Model training now proceeds; no strategy promotion is allowed until the preregistered sequential-policy and holdout gates are passed.


## Phase 43 — VIX-conditioned NIFTY all-strategy sweep — REGISTERED

Phase 43 is the new isolated research phase requested on 2026-10-06. It tests a finite broad universe of major NIFTY weekly option structures across point-in-time India-VIX regimes, with realistic Paytm Money costs, one-adverse-tick slippage, historical lot sizes, development/validation/untouched-2026 holdout chronology, preregistered router selection and 10,000-resample inference. The canonical Phase-20/42 strategy remains unchanged.

- [Phase 43 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-43-vix-all-options-strategies)
- [Phase 43 research plan](PHASE43_RESEARCH_PLAN.md)
- [Phase 43 pre-registration](PHASE43_PRE_REGISTRATION.md)
- [Phase 43 literature review](PHASE43_LITERATURE_REVIEW.md)
- [Phase 43 status](PHASE43_STATUS.md)

**Current phase state: registration complete; numerical execution pending.**


## Phase 44 — VIX candidate tuning — INITIALIZED

A new isolated research phase, branched from the completed Phase-43 VIX sweep, is registered to tune the strongest defined-risk Phase-43 candidates. The phase tunes only finite strike geometries, entry times and prior-only VIX percentile thresholds, with development/validation/untouched-2026 discipline and the same Paytm Money transaction-cost/slippage model.

- [Phase 44 research plan](PHASE44_RESEARCH_PLAN.md)
- [Phase 44 pre-registration](PHASE44_PRE_REGISTRATION.md)
- [Phase 44 literature review](PHASE44_LITERATURE_REVIEW.md)
- [Phase 44 status](PHASE44_STATUS.md)
- [Phase 44 chat log](PHASE44_CHAT_LOG.md)
- [Phase 44 workflow](.github/workflows/phase-44-vix-candidate-tuning.yml)

The canonical Phase-20/42 strategy remains unchanged while Phase 44 is evaluated.

## Phase 45 — exhaustive ready-made strategy comparison — COMPLETE / NO PROMOTION

Phase 45 completed the requested broad comparison of the option-builder structures shown in the supplied screenshots. Twenty structures required new numerical execution; twenty corresponding Phase-43 families were reused from accepted evidence, giving 5,102 new trade rows and 9,699 unified rows.

**Key finding:** LOW-VIX Bear Call Spread was the strongest validation candidate (49 trades, ₹24,742.59 net, ₹23,082.00 at +50% cost stress, 63.3% win rate). LOW-VIX Bear Put Spread and Put Broken-Wing Butterfly were next. In NORMAL VIX, Bear Call Spread and Bear Put Spread were positive in validation. None of the twenty newly added families produced a positive defined-risk validation state meeting the minimum-20-trade/+50%-cost screen.

Six validation candidates were frozen and checked on the untouched 2026 data. Five were profitable; NORMAL-VIX Call Backspread failed the holdout with −₹86,270.78 net. No strategy/state survived Holm-adjusted inference, so **no VIX-conditioned ready-made strategy is promoted**.

- [Phase 45 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-45-exhaustive-ready-made-strategies)
- [Research plan](PHASE45_RESEARCH_PLAN.md)
- [Pre-registration](PHASE45_PRE_REGISTRATION.md)
- [Literature review](PHASE45_LITERATURE_REVIEW.md)
- [Status](PHASE45_STATUS.md)
- [Chat log](PHASE45_CHAT_LOG.md)
- [Workflow](.github/workflows/phase-45-exhaustive-ready-made-strategies.yml)
- [Manuscript](results/phase45_ready_made/PHASE45_MANUSCRIPT.md)
- [Final decision](results/phase45_ready_made/final_decision.json)
- [Strategy × VIX summary](results/phase45_ready_made/strategy_vix_summary.csv)
- [Validation inference](results/phase45_ready_made/validation_regime_inference.csv)
- [Frozen candidates](results/phase45_ready_made/validation_freeze_top3.csv)
- [2026 holdout confirmation](results/phase45_ready_made/holdout_frozen_top3_confirmation.csv)

The canonical Phase-20/42 strategy remains unchanged.

## Phase 49 — FINAL CLOSEOUT

**Decision: NO PROMOTION.** The corrected numerical run #12 completed successfully; artifact self-audit passed; the raw artifact was independently reconciled and the complete manuscript/evidence package is persisted.

- Source numerical run: `37542636969`.
- 720 raw geometries → 1,440 LOW/NORMAL-VIX candidates.
- 2 frozen candidates; 1 validation economic pass; 0 Holm-adjusted statistical survivors; 1 small holdout confirmation.
- Best research candidate: LOW-VIX Bear Put — 09:30 IST, 5 trading sessions before expiry, buy PE +1 modal step and sell PE −3 modal steps, four-step width.
- Validation: +₹28,848.48 net / +₹27,246.47 at +50% cost stress on 42 active LOW-VIX trades; permutation p=0.2260; Holm p=0.4520.
- Holdout: +₹27,278.50 net / +₹27,051.63 stressed on 5 active LOW-VIX observations.
- Canonical strategy remains unchanged.

Key evidence: [Phase 49 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/results/phase49_vix_tuning/PHASE49_MANUSCRIPT.md), [final decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/results/phase49_vix_tuning/phase49_final_decision.json), [parameter summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/results/phase49_vix_tuning/phase49_parameter_summary.csv), [status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/PHASE49_STATUS.md), [error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-49-vix-leader-parameter-tuning/ERROR_LOG.md).


## Phase 50B — Expanded prior-strategy universe — ACTIVE

Current canonical numerical run: **GitHub Actions 37572837253**. Registry/preflight has passed; TT-02 common-cost replay is still in progress, so **no Phase-50B numerical result or promotion claim is accepted yet**.

- [Phase 50B status](PHASE50B_STATUS.md)
- [Phase 50B research plan](PHASE50B_RESEARCH_PLAN.md)
- [Phase 50B pre-registration](PHASE50B_PRE_REGISTRATION.md)
- [Phase 50B strategy universe](PHASE50B_STRATEGY_UNIVERSE.md)
- [Phase 50B chat/decision log](PHASE50B_CHAT_LOG.md)
- [TT-02 replay specification](PHASE50B_TT02_REPLAY_SPEC.md)
- [TT-04 source audit](PHASE50B_TT04_SOURCE_AUDIT.md)
- [Phase 50B branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-expanded-strategy-universe)
- [Current Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37572837253)

The frozen execution order is **TT-02 → TT-03 → TT-04 → remaining registered controls → statistical correction → protected holdout/manuscript**. The canonical Phase-20/42 strategy remains unchanged.


### Phase 50B workflow hardening
The canonical chain is now explicitly gated **TT-02 → TT-03 → TT-04**. [TT-04 workflow](.github/workflows/phase-50b-tt04-premium-match.yml) is manual-capable and will also accept the protected TT-04 trigger emitted only after an audited TT-03 success. No trigger is created while the current TT-02 replay remains incomplete.


## 2026-10-07 — Automation audit correction
- Discovered and corrected a workflow-only TT-04 trigger placement defect before it could affect any numerical evidence.
- The active run 37572837253 remains on its original execution head and is unaffected.
- The corrected branch workflow now places TT-04 triggering strictly after audited TT-03 publication; the dedicated TT-04 workflow remains manually dispatchable.
## 2026-10-07 — TT-02 fallback performance audit
- The active canonical run **37572837253** remains in progress and remains the only numerical evidence candidate.
- Static profiling identified a second avoidable hot loop in the replay: repeated full NIFTY-index equality scans for every minute.
- Prepared `research/phase50b_tt02_calendar_replay_v3.py` as a **performance-only fallback** that pre-indexes spot by timestamp and trading-day timestamps.
- The Black–Scholes/European-delta definition, quote selection, state machine, entry/exit rules, slippage, brokerage, statutory charges and +50% stress are unchanged.
- The v3 fallback has **not** been executed and is not evidence; it exists only to avoid repeating an unnecessarily slow run if the current execution fails or times out.


## 2026-10-07 — Resume checkpoint / live-state audit
- Phase 50B was rechecked after user resume.
- Canonical Actions run **37572837253** remains in progress at TT-02 numerical replay; no result is accepted until artifact audit passes.
- No duplicate numerical run was launched.


## 2026-10-07 — TT-04 F50B-020 correction
- Static audit found and corrected an expiry-day quote-series bug before TT-04 execution: new expiry-day entries use next-week options, while an existing current-week position must continue to be marked/exited on its original current-week series.
- No TT-04 numerical evidence was produced from the defective code.
- TT-04 remains blocked until audited TT-03 evidence exists.


## 2026-10-07 — Phase 50B TT-02 audit correction
- Canonical run 37572837253 completed the numerical loop but failed the audit because five expiry blocks did not have an exact 15:15 option quote; its diagnostic P&L is **not evidence**.
- The implementation had incorrectly treated “at/after 15:15” as “exactly 15:15”. This was corrected so the exit uses the earliest common observed quote time at or after 15:15 for all open legs, without forward-filling.
- Corrected v2 automatically started Actions run 37589199743 from commit 6a11b859c646dccdacc03a68a22fe7a2be3a842f; no result is accepted until the artifact audit passes.
- [Phase 50B status](PHASE50B_STATUS.md) and [error log](ERROR_LOG.md) contain the full correction record.


## 2026-10-07 — Phase 50B workflow gate correction
- Run 37589199743 failed before numerical execution because the registry publisher was missing a closing `fi`; registry validation itself passed.
- Corrected workflow commit e0d4bda09bb943272bac591d68aafa051d7b9f94 restores the shell closure and passes a structural shell-balance audit.
- No numerical evidence was produced by run 37589199743.


## 2026-10-07 — Phase 50B active run checkpoint
- Canonical run **37589400281** is the sole active Phase-50B numerical run; TT-02 has passed compilation/cache setup and is executing.
- Operational polling timeout F50B-023 had no research impact. Direct Actions state checks remain authoritative.


## 2026-10-07 — Phase 50B monitoring checkpoint
- Canonical TT-02 run **37589400281** remains active.
- A transient live-log 404 was recorded as F50B-024; no numerical inference has been made from it.
- The artifact audit remains the sole acceptance gate for TT-02 evidence.


## 2026-10-07 — Phase 50B TT-02 coverage feasibility correction
- TT-02 run 37589400281 completed but failed the original audit because five opened positions lacked a complete common exit quote after 15:15.
- This is now treated as a documented historical option-coverage limitation, not a model/code failure; the source dataset itself warns that option coverage is partial and illiquid/far strikes may be sparse or absent. citeturn551023search2turn551023search4
- A 95% complete-exit coverage feasibility gate is now pre-registered. Coverage gaps are separately logged, excluded from primary P&L, and never imputed.
- The observed coverage was about 98.0% (247 complete / 252 opened positions), so the corrected rerun remains eligible for the feasibility gate.


## 2026-10-07 — Phase 50B corrected TT-02 rerun active
- Canonical run **37593965525** is active after the coverage-feasibility and zero-error audit corrections.
- The revised workflow only launches numerics from `trigger/phase50b.start`, preventing duplicate runs from documentation/code commits.


## 2026-10-07 — TT-03 pre-execution correction
- Corrected TT-03 to honor the full 10:00–10:05 entry window before numerical execution.
- No TT-03 evidence existed before this correction.


## 2026-10-07 — Phase 50B stale-evidence protection
- TT-03 now carries engine revision `50B-TT03-WINDOW-V2` and downstream gates reject older revisions.
- Future chained runs refresh the TT-03 source from the branch before execution, preventing pre-execution corrections from being silently omitted.


## 2026-10-07 — Phase 50B TT-04 audit hardening
- TT-04 now records missing exit-leg observations as explicit coverage exclusions and must clear the 95% complete-exit coverage gate before evidence is accepted.


## 2026-10-07 — Phase 50B TT-02 denominator safeguard
- TT-02 corrected engines now explicitly account for terminal open positions so the candidate denominator cannot silently lose trades.
- The active pre-safeguard run remains diagnostic until a latest-code rerun passes the full audit.


## 2026-10-07 — Phase 50B TT-02 revision gate
- TT-02 evidence now requires engine revision `50B-TT02-COVERAGE-V3`; pre-correction artifacts cannot be promoted.


## 2026-10-07 — Phase 50B cost robustness update
- Reverified current NSE statutory charges and Paytm Money brokerage information. [NSE STT schedule](https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax); [NSE stamp duty schedule](https://www.nseindia.com/static/invest/first-time-investor-stamp-duty-charges-taxes); [Paytm Money F&O FAQ](https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web); [Paytm Money pricing update](https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/)
- The primary research model remains ₹10/order for comparability; a ₹20/order Paytm robustness scenario is now preregistered for promotion sensitivity.


## 2026-10-07 — Phase 50B TT-03 evidence gate hardened
- TT-03 now records incomplete exits as coverage exclusions and requires >=95% coverage plus the current-cost robustness outputs before evidence is accepted.


## 2026-10-07 — Phase 50B TT-04 revision gate
- TT-04 evidence now requires engine revision `50B-TT04-COVERAGE-V2`.


## 2026-10-07 — Phase 50B workflow serialization
- Canonical Phase-50B numerical runs use `cancel-in-progress: true` within their strategy-specific concurrency groups so superseded retries cannot overlap; evidence is still accepted only from audited artifacts.


## 2026-10-07 — Phase 50B TT-05 control prepared
- TT-05 Simple Intraday Short Straddle now has a source-faithful replay engine and dependency-gated workflow following audited TT-04 evidence.


## 2026-10-07 — TT-02 fallback audit
- v3 has been audited as a performance-only equivalent of canonical v2 and will be used only after a genuine v2 timeout/failure.


## Phase 50B — Expanded Prior-Strategy Universe — IN PROGRESS

Phase 50B is the bounded continuation after Phase 50. It includes the user's seven supplied Tradetron strategies and previously developed strategy lineages discovered across the user's GitHub repositories.

- [Phase 50B research plan](PHASE50B_RESEARCH_PLAN.md)
- [Phase 50B strategy universe](PHASE50B_STRATEGY_UNIVERSE.md)
- [Phase 50B pre-registration](PHASE50B_PRE_REGISTRATION.md)
- [Phase 50B status](PHASE50B_STATUS.md)
- [Phase 50B source/baseline audit](PHASE50B_SOURCE_BASELINE_AUDIT.md)
- [Phase 50B literature review](PHASE50B_LITERATURE_REVIEW.md)
- [Phase 50B chat log](PHASE50B_CHAT_LOG.md)
- [Phase 50B 2026 execution-cost audit](PHASE50B_2026_COST_AUDIT.md)

### Current execution state — 2026-10-07
- TT-02 evidence is accepted from run 37598918723: 247/252 completed coverage (98.02%), primary net -₹3,387.42, +50% cost stress -₹32,226.76, ₹20/order robustness -₹47,212.62, and ₹20/order +50% stress -₹97,964.56. The baseline is not promoted.
- The overall parent workflow run 37598918723 is now completed with failure because its TT-03 child replay failed during chronological accounting; the TT-02 replay and artifact publication jobs succeeded.
- The TT-03 timezone defect was corrected and a dedicated gated replay was triggered by commit f7f01c5265203ad27b33d28d0633a93609a4538d. Its commit status is currently pending, no corrected TT-03 result directory is published, and no TT-04 trigger exists. No duplicate TT-03 replay is being launched.
- TT-07's runtime-variable lifecycle ambiguity is resolved from current official Tradetron documentation: strategy-level runtime variables persist through the current counter and remain until Universal Exit unless manually reset. The replay therefore treats ic_entered/state as counter-scoped.
- TT-07 source audit/replay specification, engine, and gated workflow are now prepared. Two additional pre-execution integrity defects were caught and corrected: transition checks now use the actual held short-leg strike, and transition cash mutation is transactional.
- TT-05 and TT-06 remain dependency-gated behind audited TT-04/TT-05 evidence; TT-07 is dependency-gated behind audited TT-06 evidence.
- The statistical gate remains fail-closed on all four required cost outputs and registers TT-01 through TT-07.

No Phase-50B strategy has been promoted.


### Phase 50B — Current control links — 2026-10-07

- [TT-03 corrected replay workflow](.github/workflows/phase-50b-tt03-dynamic-n.yml)
- [TT-07 source audit](PHASE50B_TT07_SOURCE_AUDIT.md)
- [TT-07 replay specification](PHASE50B_TT07_REPLAY_SPEC.md)
- [TT-07 replay engine](research/phase50b_tt07_dynamic_ic_ratio_replay.py)
- [TT-07 gated workflow](.github/workflows/phase-50b-tt07-dynamic-ic-ratio.yml)

### Phase 50B — Newly frozen replay specifications
- [TT-06 replay specification](PHASE50B_TT06_REPLAY_SPEC.md)
- [TT-07 replay specification](PHASE50B_TT07_REPLAY_SPEC.md)


### 2026-10-07 — TT-02 contract hardening
- Corrected an undefined runtime engine-revision constant in TT-02 and added a static AST guard. The active pre-fix execution is non-evidence; a fresh corrected rerun is required.


### 2026-10-07 — TT-06 control prepared
- Added [TT-06 replay engine](research/phase50b_tt06_intraday_asym_replay.py) and [TT-06 workflow](.github/workflows/phase-50b-tt06-intraday-asym.yml), dependency-gated behind audited TT-05 evidence.
- No TT-06 result exists yet.


### 2026-10-07 — TT-07 source-lock blocker — RESOLVED LATER
- Direct inspection of the original [Dynamic IC to Ratio export](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1) initially left the `ic_entered` runtime scope ambiguous. Numerical replay was correctly blocked at that point.
- The ambiguity was subsequently resolved from current official Tradetron Runtime Variable documentation; see the current execution section above and [TT-07 source audit](PHASE50B_TT07_SOURCE_AUDIT.md).


### 2026-10-07 — TT-02 authoritative replay — HISTORICAL CHECKPOINT
- Superseded pre-fix run 37596743408 was cancelled and excluded.
- Corrected run [37598918723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37598918723) completed the TT-02 numerical and artifact-publication jobs successfully.
- The parent workflow later finished with failure because its TT-03 child replay failed; the TT-02 artifact itself remains accepted evidence.


### 2026-10-07 — Historical execution state — SUPERSEDED
- At this checkpoint the corrected TT-02 run was still in progress; it subsequently completed and its TT-02 artifact was accepted.
- The workflow uses `cancel-in-progress: true` and only the explicit `trigger/phase50b.start` push path for automatic numerical launches; manual dispatch remains available.
- No Phase-50B strategy has been promoted.


## 2026-10-07 — Phase 50B execution status
- TT-02 authoritative evidence is now published and audited: 247/252 coverage, 98.02%; primary net -₹3,387.42; +50% cost stress -₹32,226.76; ₹20/order robustness -₹47,212.62; ₹20/order +50% stress -₹97,964.56.
- TT-03 first execution failed in chronological summary accounting because of timezone-naive/aware comparison; this was corrected before accepting any result.
- Dedicated TT-03 replay workflow added and gated on the published TT-02 evidence.


### 2026-10-07 — TT-03 trigger refresh
- The corrected TT03 workflow remained non-observable through the available commit-status endpoint, so its trigger file was refreshed in commit `28722b5204166199f91353d793f2840fe2022812`.
- The dedicated TT03 workflow uses serialized `cancel-in-progress: true` concurrency; no overlapping TT03 evidence is permitted.
- The new commit status is pending and no TT03 result is accepted yet.


### 2026-10-07 — TT-03 replay contract frozen
- Added [TT-03 replay specification](PHASE50B_TT03_REPLAY_SPEC.md) documenting the exact entry window, symmetric ratio sets, expiry-day P&L exit, coverage rules, cost model, chronology and finite far-OTM mutation boundary.
- The dedicated workflow remains the sole numerical execution path for corrected TT-03.
- Current trigger refresh commit: `28722b5204166199f91353d793f2840fe2022812`; no TT-03 result artifact is accepted until its complete artifact/coverage/cost audit passes.


### 2026-10-07 — Statistical gate protection correction
- The execution-only VIX inference gate was audited before first execution.
- Its inferential sample is now explicitly restricted to DEV+VAL (2021–2025); the protected 2026 HOLD cannot influence bootstrap/permutation tests, Holm correction, ranking or tuning.
- No inference result from the superseded implementation is accepted.


### 2026-10-07 — VIX inference-family correction
- The statistical gate now reconstructs LOW/NORMAL/HIGH plus SPIKE/RISING/FALLING/HIGH_RISING directly from the frozen cached India VIX series and each trade's entry timestamp.
- Trades without adequate VIX lookback are excluded from both regime and complement inference rather than being misclassified as complements.
- No statistical result from the superseded gate is accepted.

### 2026-10-07 — TT-03 preflight dependency correction
- The latest TT03 dedicated run failed before numerical replay because pandas was missing from the preflight environment.
- The workflow now installs the required scientific/data dependencies before its TT02 evidence gate, and the trigger has been refreshed.
- No TT03 numerical evidence has been accepted yet.

### 2026-10-07 — TT-03 semantic corrections before evidence acceptance
- The TT03 replay was audited while running and two source-semantic defects were found: hard-close selection could cross 15:29, and a non-source modal strike-step gate could exclude valid entries.
- Both were corrected before result publication; no superseded TT03 output is accepted.

### 2026-10-07 — TT-03 coverage denominator correction
- Eligible TT03 campaigns that cannot complete the source-defined 10:00–10:05 entry are now retained as explicit coverage exclusions.
- This prevents silent loss of candidate observations and is required for the 95% feasibility gate.

### 2026-10-07 — TT-03 corrected numerical rerun
- Dedicated TT03 run 37611676386 is currently executing on the corrected engine after passing dependency, compilation, static-contract and HF-cache controls.
- No TT03 result has been accepted yet; TT04 remains downstream-gated on a complete TT03 artifact audit.


### 2026-10-07 — TT-03 feasibility failure and diagnostic capture
- Corrected TT03 run 37611676386 produced 187/202 complete campaigns (92.57%) and therefore failed the frozen 95% feasibility gate. Its positive P&L remains diagnostic only and is not eligible for promotion or VIX/parameter tuning.
- Diagnostic capture rerun 37612856834 is now executing only to persist the raw trade and coverage tables and classify the terminal feasibility state.
- The candidate-local stopping rule allows the independent TT04 candidate to proceed after TT03 terminal classification without consuming TT03 P&L as evidence.


### 2026-10-07 — TT-03 terminal classification and TT-04 continuation
- TT03 diagnostic run 37613416831 completed and persisted its raw replay/coverage data. The corrected baseline remains **FEASIBILITY FAIL** at 187/202 = 92.57% coverage, below the frozen 95% gate; its positive P&L is diagnostic only.
- TT04 independent run 37614211996 passed the TT03 terminal-feasibility gate and is now executing the corrected V3 engine. No TT04 result is accepted until artifact/coverage/cost audits pass.


### 2026-10-07 — TT-03 V2 feasibility rejection and V3 correction
- TT03 V2 replay 37611676386 produced 187/202 complete campaigns (92.57%) and therefore failed the preregistered 95% feasibility gate; no P&L was accepted.
- A subsequent hard-close self-audit found a partial-quote timestamp issue that could create artificial coverage gaps. V3 now searches backward to the latest timestamp at or before 15:29 with complete quotes for every live leg.
- The V3 workflow is retriggered and TT04 remains strictly gated on a V3 artifact passing the full evidence audit.


### 2026-10-07 — TT-03 V4 session-calendar and provenance controls
- The V4 replay distinguishes regular-session data failures from scheduled-entry dates that had no normal 09:15–15:30 session (e.g. 2022-10-24 Muhurat evening session). Such dates are recorded as session exclusions, not missing-data coverage gaps. citeturn282531search15turn282531search21
- TT04 routing now requires a current-run V4 feasibility PASS artifact, preventing stale diagnostic artifacts from advancing the research chain.


### 2026-10-07 — Active TT-03 V4 execution
- Current controlled TT03 run **37617012372** is executing the V4 engine; preflight/static controls have passed and numerical replay is still in progress.
- TT04 run **37617256820** was fail-closed at preflight because only the older V2 FAIL_COVERAGE diagnostic exists in the branch. No TT04 numerical evidence was generated from that run.
- TT04 remains blocked until a same-run TT03 V4 feasibility `PASS` artifact is produced.


### 2026-10-07 — TT-03 V4 rejected; V5 active
- TT03 V4 produced 186 completed campaigns out of 187 coverage candidates (99.47%) but 14 engine/data errors. The evidence gate therefore rejected V4 despite strong nominal coverage.
- V5 retains the exit snapshot for both negative-P&L and hard-close exits and validates it before settlement. No strategy/cost parameter changed.
- Current TT03 V5 replay is the only active evidence path; TT04 remains blocked until V5 passes with zero data errors and >=95% coverage.


### 2026-10-07 — TT-03 V5 final-routing preparation
- V2 baseline failed coverage at 187/202 (92.57 percent) and is non-evidence.
- V4 reached 99.47 percent nominal coverage but had 14 engine errors and is non-evidence.
- V5 fixed the V4 negative-exit snapshot defect and is the active source-faithful engine.
- The dedicated workflow now produces one terminal feasibility artifact with PASS, FAIL_COVERAGE, or INVALID_ENGINE and marks P&L evidence eligibility explicitly.
- Independent TT04 continuation is allowed after any persisted TT03 terminal classification, while failed/invalid TT03 P&L is never consumed as evidence.
