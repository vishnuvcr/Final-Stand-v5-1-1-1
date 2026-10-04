# Final Stand v5 1-1-1-1

Research repository for systematic testing of NIFTY weekly-options directional 3-leg ratio strategies.

## Current research status

**Dynamic-n corrected research completed through Phase 20. Final entry-to-exit rules are frozen; payoff-boundary stops are rejected and the 13:30 expiry-day MFE stop is retained.**

The dynamic-n branch was restarted from the raw option-data workflow after two critical implementation errors were discovered during AlgoTest reconciliation:
1. OTM strikes had initially been selected by ordinal availability instead of exact ₹50 strike distance.
2. Long/short P&L signs had initially been inverted.

All prior dynamic-n numerical results and trade ledgers are superseded and were not reused.

### Corrected dynamic-n primary

Validated executable sample: **2021-05-27 to 2026-09-30**

- **190 completed trades**
- Gross P&L: **₹154,742.25**
- Modeled costs: **₹15,805.13**
- Net P&L: **₹138,937.12**
- Mean net/trade: **₹731.25**
- Median net/trade: **₹814.85**
- Net win rate: **94.21%**
- Profit factor: **2.14**
- Maximum cumulative drawdown: **₹27,321.08**
- Target exits: **178/190**
- Expiry exits: **12/190**
- Mean selected n: **6.04**
- Median selected n: **6**

### Higher-n weightage criterion

The locked n-selection rule was:

- evaluate n=6..15;
- compute X_n for each n;
- identify max(X_n);
- consider n eligible when X_n >= 95% of max(X_n);
- **prefer the highest eligible n**.

The corrected sample selected:
- n=6: **183 trades**
- n=7: **6 trades**
- n=8: **1 trade**
- n=9..15: **0 trades**

Thus the dynamic mechanism operated essentially as n=6 in this historical sample, with occasional higher-n selections.

### Corrected fixed OTM15 comparison

Corrected fixed OTM15 primary:

- 183 completed trades
- Gross P&L: **₹112,080.50**
- Costs: **₹13,520.46**
- Net P&L: **₹98,560.04**
- Mean net/trade: **₹538.58**
- Median net/trade: **₹195.35**
- Net win rate: **99.45%**
- Maximum cumulative drawdown: **₹3,593.39**

Across **180 common expiry dates**:

- Dynamic-n net: **₹132,977.71**
- Fixed OTM15 net: **₹88,176.60**
- Dynamic-minus-fixed net difference: **₹44,801.11**
- Dynamic-n net exceeded fixed OTM15 on **93.89%** of common expiry dates.

This is a descriptive comparison, not a pure causal test of n-selection, because the direction selectors differ: dynamic-n uses OTM6/7/8 while fixed OTM15 uses OTM15/16/17.

## Key dynamic-n findings

The positive historical result is concentrated in target exits:

- Target exits: **₹258,460.02 net**
- Expiry exits: **-₹119,522.91 net**

The high 94.21% win rate therefore does not remove tail-loss risk.

Bootstrap results:
- Mean-net 95% CI: **₹145.58 to ₹1,252.17**
- Win-rate 95% CI: **90.53% to 97.37%**

All pre-registered robustness families remained positive in the tested scenarios, including target fraction, slippage, entry time, DTE, brokerage and higher-n threshold sensitivity.

## Research artifacts

- [Final corrected manuscript](manuscript/DYNAMIC_N_CORRECTED_MANUSCRIPT.md)
- [Dynamic-n research plan](DYNAMIC_N_RESEARCH_PLAN.md)
- [Dynamic-n specification](DYNAMIC_N_SPEC.md)
- [Dynamic-n primary backtest](research/backtest_dynamic_n_corrected.py)
- [Primary dynamic-n results](results/dynamic_n_corrected/phase10_primary/)
- [Dynamic-n statistics](results/dynamic_n_corrected/phase11_statistics/)
- [Dynamic-n robustness](results/dynamic_n_corrected/phase12_robustness/)
- [Dynamic-n vs fixed comparison](results/dynamic_n_corrected/phase13_comparison/)
- [Research log](RESEARCH_LOG.md)
- [Error log](ERROR_LOG.md)

## Corrected fixed OTM15 artifacts

- [Corrected fixed primary](results/fixed_otm15_v3/phase7d/)
- [Corrected fixed statistics](results/fixed_otm15_v3/phase8b/)
- [Corrected fixed robustness](results/fixed_otm15_v3/phase9/)

## Research integrity status

Previous dynamic-n and earlier fixed-OTM15 numerical outputs produced before the strike-mapping and P&L corrections remain in Git history for audit only. They are explicitly superseded and are not used as evidence in the final manuscript.

The primary conclusion is historical and in-sample. No claim is made that future performance will match the backtest.


## Controlled n-selection ablation — final audit

A controlled ablation held the OTM6/7/8 Stage-1 direction selector and all execution assumptions constant:

- Fixed n=6: **₹139,543.97 net**, 190 trades, 94.21% win rate.
- Dynamic 95%-band: **₹138,937.12 net**, 190 trades, 94.21% win rate.
- Fixed n=15: **₹87,322.86 net**, 190 trades, 99.47% win rate.

The dynamic rule therefore produced **₹606.85 less net P&L than fixed n=6** on the identical trade universe. It selected n=7 only 6 times and n=8 once; n=6 was selected on 183/190 trades. This means the positive primary result should not be interpreted as evidence that the higher-n preference adds incremental value. The controlled ablation isolates n-selection from the separate OTM6/7/8 versus OTM15/16/17 direction-selector difference.

The final manuscript has been revised accordingly.
## Phase 17 — stop-loss extension

The locked dynamic-n primary remains unchanged: **190 trades, ₹138,937.12 net P&L, 94.21% net win rate, 178 target exits and 12 expiry exits**.

A stop-loss extension is being tested on the exact minute-level three-leg P&L paths. The research goal is stricter than simply reducing drawdown: the development screen requires **zero baseline-positive trades to be stopped before their original exit**, and the selected rule is then frozen for temporal validation.

Development period: **2021-05-27 through 2024-12-31**.  
Validation period: **2025-01-01 through 2026-09-30**.

### Phase 17 artifacts

- [Stop-loss research code](research/stop_loss_research.py)
- [Phase 17 workflow](.github/workflows/phase-17-stop-loss-research.yml)
- [Updated dynamic-n research plan](DYNAMIC_N_RESEARCH_PLAN.md)

The baseline remains the no-stop strategy until a stop rule demonstrates improvement under the pre-registered protocol.  

## Phase 18 — conditional stop refinement

Phase 17 found six candidates that affected zero baseline-positive trades in both development and validation, but none improved validation net P&L. Phase 18 tests a narrower condition: an expiry-day negative trade is stopped only when its earlier running MFE is still below a fixed fraction of the target.

- [Phase 18 code](research/conditional_stop_refinement.py)
- [Phase 18 workflow](.github/workflows/phase-18-conditional-stop-refinement.yml)
- [Phase 18 results](results/dynamic_n_corrected/phase18_conditional_stop/)

## Phase 19 — walk-forward stop confirmation

Phase 18 found a candidate stop that improved the full sample while leaving every profitable baseline trade untouched. Phase 19 now checks whether that result survives an earlier training split and a 2026 holdout.

- [Phase 19 code](research/stop_walk_forward.py)
- [Phase 19 workflow](.github/workflows/phase-19-stop-walk-forward.yml)
- [Phase 19 results](results/dynamic_n_corrected/phase19_walk_forward/)


## Final Phase 19 stop-loss conclusion

The research did not find a fixed hard stop that could safely cut the expiry-loss tail without disturbing profitable baseline trades. The robust candidate is instead a late expiry-day conditional exit:

**At 13:30 IST on expiry day, exit all three legs when combined strategy MTM is negative and running MFE since entry is below 50% of the original target.**

Historical walk-forward result:

| Period | Net uplift | Baseline-positive trades affected | Stops |
|---|---:|---:|---:|
| Training | +₹1,963.67 | 0 | 1 |
| Validation | +₹1,923.59 | 0 | 2 |
| 2026 holdout | +₹6,305.15 | 0 | 2 |
| Full sample | +₹10,192.41 | 0 | 5 |

The candidate increases the reconstructed full-sample net P&L from ₹138,937.12 to approximately ₹149,129.53. It changes five exits, all baseline losers, and changes no historically profitable exit.

This is not a guarantee against losses. The stopped trades remain losses, and live execution can differ because of spreads, partial fills, latency and slippage. The candidate remains paper/forward-validation only.

### Final Phase 19 artifacts

- [Stop-loss conclusion](STOP_LOSS_CONCLUSION.md)
- [Stop-loss manuscript supplement](manuscript/STOP_LOSS_EXTENSION_SUPPLEMENT.md)
- [Walk-forward summary](results/dynamic_n_corrected/phase19_walk_forward/WALK_FORWARD_SUMMARY.md)
- [Walk-forward grid](results/dynamic_n_corrected/phase19_walk_forward/walk_forward_grid.csv)
- [Selected full trade ledger](results/dynamic_n_corrected/phase19_walk_forward/selected_full_trade_level.csv)

The locked primary no-stop strategy is unchanged.


## Phase 20 — payoff-boundary stop research

Phase 20 tests whether the entry-time payoff chart's expiry zero-P&L boundary is useful as an early risk-control signal when NIFTY moves beyond the green/profit region before expiry.

Pre-registered boundary buffers are **0/50/100/200/400 NIFTY points**, with 1-minute and 3-minute confirmation. Three boundary conditions are tested: boundary-only; boundary + negative combined MTM; and boundary + negative MTM + MFE below 50% of target. The fixed Phase-19 expiry-day rule remains the comparator.

- [Phase 20 research plan](DYNAMIC_N_RESEARCH_PLAN.md)
- [Phase 20 research code](research/payoff_boundary_stop_research.py)
- [Phase 20 workflow](.github/workflows/phase-20-payoff-boundary-stop-research.yml)
- [Phase 20 results](results/dynamic_n_corrected/phase20_payoff_boundary/)

Phase 20 is the final planned historical comparison needed to decide whether payoff-boundary information belongs in the complete entry-to-exit specification.


## Final strategy — entry to exit

The complete historical research specification is now frozen:

- [Final strategy rules](FINAL_STRATEGY_RULES.md)
- [Final strategy backtest wrapper](research/final_strategy_backtest.py)
- [Final strategy result](results/final_strategy/FINAL_STRATEGY_RESULT.md)
- [Canonical strategy specification](STRATEGY_SPEC.md)
- [Dynamic-n specification](DYNAMIC_N_SPEC.md)

### Final exit logic

1. Exit at the 0.90×X_selected×lot target when reached.
2. From 13:30 IST on expiry day, exit when combined three-leg MTM < ₹0 and running MFE < 0.50×original target.
3. Otherwise exit at the latest complete three-leg observation at or before 15:29 IST on expiry day.
4. Do **not** exit merely because NIFTY crosses the entry-time payoff green-area/zero-P&L boundary.

### Final historical result

Across 190 corrected trades, the final exit specification produced:

| Metric | Final result |
|---|---:|
| Net P&L | **₹149,129.53** |
| Mean net/trade | **₹784.89** |
| Net winners | **179/190 (94.21%)** |
| Profit factor | **2.34** |
| Maximum cumulative drawdown | **₹27,336.11** |
| Target exits | **178** |
| Conditional-stop exits | **5** |
| Expiry-fallback exits | **7** |
| Baseline-positive trades stopped early | **0** |

### Phase 20 — payoff-boundary conclusion

The training-safe boundary candidate was a 400-point breach with 1-minute confirmation. It improved training P&L by ₹711.91, but reduced validation P&L by ₹14,390.87 and 2026 holdout P&L by ₹49,064.48, while materially worsening drawdown. The combined boundary-plus-13:30 stop also failed out of sample.

Therefore the payoff chart's green-area boundary is **not** part of the final strategy.

- [Phase 20 supplement](manuscript/PHASE20_PAYOFF_BOUNDARY_SUPPLEMENT.md)
- [Phase 20 conclusion](results/dynamic_n_corrected/phase20_payoff_boundary/BOUNDARY_STOP_CONCLUSION.md)
- [Phase 20 result summary](results/dynamic_n_corrected/phase20_payoff_boundary/phase20_status.csv)
- [Final trade-level ledger](results/dynamic_n_corrected/phase20_payoff_boundary/phase19_expiry_stop_full_trade_level.csv)

### Final research status

Phase 20 is the final planned historical exit-rule comparison. No further historical stop optimization is scheduled under the current research plan. The remaining research step before any live deployment is forward/paper execution validation under live bid/ask, spread, latency, partial-fill and broker-execution conditions.


## Phase 21 — pre-expiry adverse-move risk-control research

The Phase-20 historical strategy remains frozen. A separate Phase-21 branch is testing whether a very large adverse NIFTY move before expiry can be handled by a deterministic early exit or by adding one OTM-(n+3) tail hedge.

- [Phase 21 pre-registration](PHASE21_PRE_REGISTRATION.md)
- [Phase 21 research code](research/preexpiry_adverse_move_risk_control.py)
- [Phase 21 workflow](.github/workflows/phase-21-preexpiry-adverse-move-risk-control.yml)

Phase 21 does not change the final strategy unless a candidate passes the frozen walk-forward promotion screen. Until then, the canonical strategy remains the Phase-20 specification.

## Phase 21 completion — pre-expiry risk control

Phase 21 tested pre-expiry adverse NIFTY moves of 200–600 points with 1/5/15-minute confirmation, spot/MTM/MFE filters, early exits, and one-lot OTM-(n+3) tail hedges. No candidate passed the training requirement of zero profitable baseline trades affected. The closest candidate (600-point / 1-minute / spot-only early exit) improved training by ₹1,885.47 but lost ₹33,923.36 in 2024–2025 validation and ₹44,039.53 in the 2026 holdout. It also increased full-sample max drawdown to ₹52,740.01. **No Phase-21 adjustment is promoted; the Phase-20 strategy remains frozen.**

- [Phase 21 pre-registration](PHASE21_PRE_REGISTRATION.md)
- [Phase 21 conclusion](results/dynamic_n_corrected/phase21_adverse_move_risk_control/PHASE21_CONCLUSION.md)
- [Phase 21 full candidate grid](results/dynamic_n_corrected/phase21_adverse_move_risk_control/phase21_full_grid.csv)

## Phase 22 — entry filter research

Phase 22 tests whether entry-time information can avoid the strategy's losing trades before entry. Pre-registered filters cover payoff-buffer geometry, direction confidence, structure quality and pre-entry NIFTY regime, with controlled two-feature combinations.

- [Phase 22 pre-registration](PHASE22_PRE_REGISTRATION.md)
- [Phase 22 research code](research/entry_filter_loss_avoidance.py)
- [Phase 22 workflow](.github/workflows/phase-22-entry-filter-loss-avoidance.yml)

No Phase-22 filter changes the canonical strategy unless it passes the frozen training/validation/holdout promotion screen.

## Phase 22 completion — entry-filter research

Phase 22 tested pre-entry filters based on payoff-buffer geometry, direction confidence, structure quality and pre-entry NIFTY regime. **No candidate passed the pre-registered safety screen.** The zero-winner-loss-removal frontier was empty: no tested filter removed even one training loss without also removing a profitable training trade. The closest loss-removing rule retained only 85.26% of training winners and failed validation. **The Phase-20 canonical entry and exit rules remain unchanged.**

- [Phase 22 pre-registration](PHASE22_PRE_REGISTRATION.md)
- [Phase 22 conclusion](results/dynamic_n_corrected/phase22_entry_filter_loss_avoidance/PHASE22_CONCLUSION.md)
- [Phase 22 full filter grid](results/dynamic_n_corrected/phase22_entry_filter_loss_avoidance/phase22_full_filter_grid.csv)
- [Phase 22 manuscript supplement](manuscript/PHASE22_ENTRY_FILTER_SUPPLEMENT.md)


## Phase 23 — rich entry-state and directional-switch research

Phase 23 is now registered as a separate research phase. It expands entry information beyond the Phase-22 simple filters to include **India VIX, realized/implied volatility, cross-market returns, overnight/global risk state, NIFTY futures basis and OI/volume, option premiums/OI/volume, IV/skew/term structure, and timestamp-safe event/flow variables where data are available**. It also explicitly tests the opposite direction as a competing action rather than assuming every weak canonical signal should simply be skipped.

The preregistered action space is **canonical / reverse / skip**, with the reverse trade reconstructed through the same dynamic-n, 90% target, expiry-day conditional stop, expiry fallback, slippage and Paytm Money transaction-cost engine. Model complexity is capped because the historical control has only 11 losing trades. Training, 2024–2025 validation and untouched 2026 holdout remain mandatory.

- [Phase 23 preregistration](PHASE23_PRE_REGISTRATION.md)
- [Phase 23 status](PHASE23_STATUS.md)

### Research-source rationale

NSE documents India VIX as a 30-day expected-volatility measure derived from NIFTY option bid/ask order-book information, making it directly relevant to an entry-state model. NSE also exposes historical VIX, index, derivatives and option-chain/OI/volume data sources. Academic option-return research supports examining volatility, moneyness, open interest/liquidity and higher-moment/implied-volatility variables rather than relying only on spot direction. These sources motivate the registered feature families; they do **not** establish that any Phase-23 feature improves this particular strategy.


## Phase 23 completion — rich entry-state and directional-switch research

Phase 23 completed with the exact 190-trade universe aligned and 185 reconstructed reverse trades available. The final low-complexity canonical/reverse/skip policy passed its training screen but **failed OOS promotion**: 2024–2025 validation uplift was **-₹1,344.36** and the untouched 2026 holdout uplift was **₹0.00**. The Phase-20 canonical strategy therefore remains unchanged.

- [Phase 23 conclusion](results/dynamic_n_corrected/phase23_entry_state/PHASE23_CONCLUSION.md)
- [Phase 23 manuscript supplement](manuscript/PHASE23_ENTRY_STATE_SUPPLEMENT.md)
- [Phase 23 model walk-forward](results/dynamic_n_corrected/phase23_entry_state/phase23_mode_walkforward_summary.csv)

## Phase 24 — targeted reversal-trigger research

Phase 24 is a separately preregistered, narrower reversal study. It tests whether reversal should occur only when both canonical loss-risk and reverse-superiority probabilities are simultaneously high, optionally with a fixed probability-margin gate. It uses the same 190-trade feature universe and execution-cost assumptions and introduces no new feature family.

- [Phase 24 pre-registration](PHASE24_PRE_REGISTRATION.md)
- [Phase 24 status](PHASE24_STATUS.md)
- [Phase 24 research code](research/phase24_targeted_reversal.py)
- [Phase 24 workflow](.github/workflows/phase-24-targeted-reversal-trigger.yml)


## Phase 24 completion — targeted reversal trigger

Phase 24 exhausted the preregistered reversal-trigger grid. **No candidate passed the training safety gate.** The closest diagnostic rule (Family B, L=0.85, R=0.85, M=-0.10) produced +₹25,202.33 training uplift but sacrificed 7.18% of baseline-positive training P&L and produced **₹0 validation uplift and ₹0 2026 holdout uplift**, with zero OOS losses reversed. **No reversal adjustment is promoted.**

The complete historical strategy therefore remains the Phase-20 canonical dynamic-n specification:
- [Final strategy rules](FINAL_STRATEGY_RULES.md)
- [Strategy specification](STRATEGY_SPEC.md)
- [Final research manuscript](manuscript/FINAL_RESEARCH_MANUSCRIPT.md)
- [Phase 24 conclusion](results/dynamic_n_corrected/phase24_targeted_reversal/PHASE24_CONCLUSION.md)


## Final research closeout — Phase 24 complete

The preregistered research phases are complete. Phase 23 and Phase 24 did not produce an out-of-sample improvement that passed the registered promotion gates. The **Phase-20 canonical dynamic-n strategy remains the final historical entry-to-exit specification**.

Final historical result: **190 trades, ₹149,129.53 net P&L, 179/190 profitable trades (94.21%), profit factor 2.34, maximum drawdown ₹27,336.11** under the research execution-cost model.

- [Final strategy rules](FINAL_STRATEGY_RULES.md)
- [Final strategy specification](STRATEGY_SPEC.md)
- [Final research manuscript](manuscript/FINAL_RESEARCH_MANUSCRIPT.md)
- [Phase 23 conclusion](results/dynamic_n_corrected/phase23_entry_state/PHASE23_CONCLUSION.md)
- [Phase 24 conclusion](results/dynamic_n_corrected/phase24_targeted_reversal/PHASE24_CONCLUSION.md)
- [Research plan](DYNAMIC_N_RESEARCH_PLAN.md)
- [Error log](ERROR_LOG.md)

## Phase 25 — alternative direction chooser — complete

Phase 25 tested alternatives to the OTM6/7/8 direction chooser while holding the rest of the strategy fixed. No alternative passed the preregistered training and out-of-sample gates.

- [Phase 25 pre-registration](PHASE25_PRE_REGISTRATION.md)
- [Phase 25 status](PHASE25_STATUS.md)
- [Phase 25 conclusion](results/dynamic_n_corrected/phase25_direction_chooser/PHASE25_CONCLUSION.md)
- [Phase 25 manuscript supplement](manuscript/PHASE25_DIRECTION_CHOOSER_SUPPLEMENT.md)
- [Phase 25 full candidate grid](results/dynamic_n_corrected/phase25_direction_chooser/phase25_direction_chooser_grid.csv)

**Decision: retain OTM6/7/8 as the final direction chooser.**

## Phase 26 — direct OTM7/8/9 (789) structure test — COMPLETE

A direct corrected-engine test evaluated fixed **buy OTM7 / sell OTM8 / sell OTM9** against the locked dynamic-n construction on the same 190-trade universe, keeping the OTM6/7/8 Stage-1 direction chooser and execution-cost model unchanged.

- Dynamic-n losses: **11**
- Fixed 789 losses: **10**
- Losses avoided: **1**, not 2
- Winner-to-loss conversions: **0**
- Dynamic-n net P&L: **₹138,937.12**
- Fixed 789 net P&L: **₹129,567.71**
- Fixed 789 maximum drawdown: **₹24,081.63** versus **₹27,321.08** for dynamic-n
- The single loss-to-win conversion was expiry **2026-03-17**: −₹632.58 to +₹5,850.83.

The direct test therefore does not support a two-loss-saving claim. It also does not justify replacing dynamic-n because fixed 789 sacrificed ₹9,369.41 of aggregate net P&L. The Phase-20 canonical strategy remains unchanged.

- [Phase 26 conclusion](results/dynamic_n_corrected/phase26_fixed789/PHASE26_CONCLUSION.md)
- [Phase 26 manuscript supplement](manuscript/PHASE26_789_STRUCTURE_SUPPLEMENT.md)
- [Phase 26 status](PHASE26_STATUS.md)


## Phase 27 — Delta-based exit research — COMPLETE

Phase 27 tested whether reconstructed **portfolio delta** could improve exits. Delta coverage was 99.21%. The training-selected rule was **MTM ≥ 0.90×target and |portfolio delta| ≤ 0.05**, but versus the locked Phase-20 strategy it produced **−₹2,334.04 validation uplift** and **−₹1,108.04 2026 holdout uplift**. The holdout bootstrap 95% CI for mean trade-level uplift was **−₹141.92 to −₹13.82**. No adverse-delta stop was selected. **No delta rule is promoted; Phase-20 remains canonical.**

- [Phase 27 status](PHASE27_STATUS.md)
- [Phase 27 pre-registration](PHASE27_PRE_REGISTRATION.md)
- [Phase 27 manuscript supplement](manuscript/PHASE27_DELTA_EXIT_SUPPLEMENT.md)
- [Phase 27 conclusion](results/dynamic_n_corrected/phase27_delta_exit/PHASE27_CONCLUSION.md)
