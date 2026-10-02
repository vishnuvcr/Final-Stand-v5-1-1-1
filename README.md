# Final Stand v5 1-1-1-1

Research repository for systematic testing of NIFTY weekly-options directional 3-leg ratio strategies.

## Current research status

**Dynamic-n corrected research completed; Phase 17 broad stop-loss grid found no validation-improving safe stop; Phase 18 conditional refinement is in progress.**

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
