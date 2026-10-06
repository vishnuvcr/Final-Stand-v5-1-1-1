# Phase 49 Status — VIX Leader Parameter Tuning

**CLOSED — NO PROMOTION**

## Final evidence gate

- Authoritative numerical run: **37542636969 (#12)**.
- Numerical calculation: **PASS**.
- Artifact self-audit: **PASS**.
- Automatic artifact reconciliation: **PASS** — closeout run **37544951498**.
- Raw geometries: **720**.
- Regime-expanded candidates: **1,440** (720 × LOW/NORMAL VIX).
- Development expiry blocks: **133** (2021–2023).
- Validation expiry blocks: **102** (2024–2025).
- Protected holdout expiry blocks: **21**.
- Frozen candidates: **2**.
- Validation economic passes: **1**.
- Holm-adjusted statistical survivors: **0**.
- Holdout confirmations: **1**.
- Canonical strategy changed: **No**.
- Promotion decision: **NO PROMOTION**.

## Frozen candidates

1. **Bear Put / LOW VIX**
   - Entry: **09:30 IST**
   - Entry horizon: **5 trading sessions before expiry**
   - Buy PE: **+1 modal strike step relative to point-in-time ATM**
   - Sell PE: **−3 modal strike steps**
   - Spread width: **4 modal strike steps**
   - Development trades: 79
   - Validation: 42 active LOW-VIX trades; +₹28,848.48 net; +₹27,246.47 at +50% cost stress.
   - Active-vs-complement bootstrap mean difference: +₹780.86; 95% CI [−₹1,369.81, +₹2,909.48].
   - One-sided permutation p=0.2260; Holm-adjusted p=0.4520.
   - Paired uplift vs registered Bear Put LOW baseline on 41 common validation expiries: +₹21,521.89 net; +₹21,469.09 at +50% costs.
   - Protected holdout confirmation: 5 active LOW-VIX trades, +₹27,278.50 net; +₹27,051.63 at +50% costs; 80% win rate.
   - **Status: research candidate only.**

2. **Put BWB / LOW VIX**
   - Entry: **11:00 IST**
   - Entry horizon: **3 trading sessions before expiry**
   - Body: 1 modal strike step
   - Upper wing: 1 step
   - Lower wing: 4 steps
   - Development trades: 85
   - Validation: 50 active LOW-VIX trades; −₹43,963.84 net; −₹47,238.89 at +50% cost stress.
   - Active-vs-complement mean difference: −₹254.48; permutation p=0.6162; Holm p=0.6162.
   - **Status: rejected as a tuned candidate.**

## VIX routing definition

For each entry date, the prior available India VIX close is compared with the historical distribution available before that date. **LOW** means the prior close is at or below the historical 25th percentile; **NORMAL** lies between the 25th and 75th percentiles. The state is determined point-in-time and is not recalculated using future observations.

## Cost and execution realism

The accepted engine uses historical NIFTY lot sizes, brokerage of ₹10 per order, historical STT/exchange/SEBI/IPFT/stamp/GST components, one adverse ₹0.05 option tick per leg on execution, and a +50% charge-stress P&L. The protected holdout was not used for parameter selection or validation.

## Scientific conclusion

The tuning exercise found an economically attractive LOW-VIX Bear Put configuration, but it did **not** produce statistically confirmatory evidence after the frozen active-vs-complement test and Holm correction. The positive five-trade holdout is encouraging but underpowered.

**Phase 49 therefore closes with NO PROMOTION. The canonical strategy remains unchanged.**

## Final files

- results/phase49_vix_tuning/PHASE49_MANUSCRIPT.md
- results/phase49_vix_tuning/phase49_final_decision.json
- results/phase49_vix_tuning/phase49_parameter_summary.csv
- results/phase49_vix_tuning/phase49_paired_baseline_comparison.csv
- results/phase49_vix_tuning/phase49_annual_breakdown.csv
- results/phase49_vix_tuning/development_parameter_trade_matrix.csv
- results/phase49_vix_tuning/validation_frozen_trade_matrix.csv
- results/phase49_vix_tuning/holdout_frozen_trade_matrix.csv
- results/phase49_vix_tuning/*.svg
