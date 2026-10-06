# Phase 43 Status — VIX-Conditioned NIFTY All-Strategy Sweep

**COMPLETE — NO PROMOTION**

## Final evidence

- Strategies declared: **22**
- Defined-risk promotion universe: **18**
- Expiry opportunities: **262**
- Strategy observations: **4,597**
- Development / validation / untouched 2026 holdout observations: **2,398 / 1,821 / 378**
- Data exclusions: **2** expiries (`2026-06-02`, `2026-08-04`) due missing modal strike-step information.
- Frozen strategy×VIX candidates: **0**
- Frozen VIX routers: **0**
- Stage 5 active-exit extension: **not run**
- Final decision: **NO PROMOTION**

## Statistical result

The first inference implementation was invalid because it compared a VIX-regime subset with the same rows from the ALL sample. That output is retained as non-evidence.

The corrected analysis compares each VIX regime with the complementary non-regime validation observations for the same strategy. The corrected regime table contains **36 strategy×regime tests** with sufficient sample size. **No test survived Holm adjustment at p < 0.05; all corrected 95% bootstrap confidence intervals crossed zero.**

## Router result

After enforcing the preregistered promotion universe (defined-risk strategies only; insufficiently sampled calendars excluded), the best development benchmark was **call_backspread**, with development mean trade P&L of approximately **₹247.08**. Its validation result was negative, and no VIX-conditioned router passed the registered development/validation/cost-stress gate.

Because no router passed the validation freeze gate, **no holdout router promotion was permitted** and Stage 5 active-exit optimization was correctly skipped.

## Interpretation

India VIX did not demonstrate a robust, statistically defensible strategy-selection edge within this preregistered NIFTY weekly strategy universe under the audited cost/slippage model.

Some unbounded structures showed positive historical P&L, but they are diagnostic-only under the preregistration and are not eligible for promotion.

The canonical Phase-20/42 strategy remains unchanged.
