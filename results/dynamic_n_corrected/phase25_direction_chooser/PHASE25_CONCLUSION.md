# Phase 25 Conclusion — Alternative Direction Choosers

## Research question
Can the Phase-20 OTM6/7/8 direction chooser be replaced by another point-in-time signal without damaging the profitable trades and while improving net P&L out of sample?

## Scope
Phase 25 changed only the direction chooser. Dynamic-n selection, target, expiry-day conditional stop, expiry fallback, execution-cost model and all other rules were held constant.

The exact 190-trade universe was used, with training through 2023-12-31, validation in 2024–2025, and untouched 2026 holdout.

## Candidate families tested
- Raw premium-curvature selectors for k=6...15.
- Normalized premium-curvature selectors for k=6...15.
- Matched OTM call/put price ratios for k=6...15.
- Matched call-put IV spreads for k=6...10.
- OI PCR and volume PCR, with both momentum and contrarian sign conventions.
- NIFTY prior-session return, 10:00 return, overnight gap and global-equity median return.
- Fixed median premium-ratio and IV-spread signals.
- A fixed majority-vote directional signal.

## Main result
**No alternative direction chooser passed the preregistered training eligibility gate.** Therefore no alternative was allowed to advance as the selected OOS candidate and the Phase-20 OTM6/7/8 chooser remains unchanged.

Training eligibility required positive uplift, at least 95% winner retention, zero winner-to-loss conversions, at least 95% coverage and at least two improving opposite-side selections.

### Closest examples

**Curvature k=7 and k=8:**
- training uplift: +₹162.83;
- 100% training winner retention;
- one direction switch;
- validation uplift: −₹209.03;
- 2026 holdout uplift: ₹0.

**Overnight gap:**
- training uplift: +₹1,037.87;
- training winner retention: 95.83%;
- 3 training switches improved;
- failed training safety because 2 baseline winners became losses;
- validation uplift: −₹127,189.87;
- 2026 holdout uplift: −₹25,293.57.

**Global-equity median:**
- training uplift: −₹9,107.76;
- validation uplift: −₹31,734.34;
- 2026 holdout uplift: +₹8,221.91.
The positive holdout result does not rescue the rule because it failed the preregistered training and validation gates.

**Median call/put premium ratio and median IV spread:** both had very high retrospective agreement with the better historical side but poor trading performance because they switched too many profitable canonical trades. This is an important warning that retrospective direction accuracy is not equivalent to strategy profitability.

## Interpretation
The evidence suggests that the current OTM6/7/8 chooser is not simply a proxy that can be replaced by a generic bullish/bearish indicator. The exact premium geometry appears to be interacting with the payoff construction and dynamic-n selection.

Several economically motivated alternatives—relative option prices, IV spreads/skew, PCR, and cross-market direction—showed either strong in-sample associations or isolated holdout improvements, but none produced a stable improvement across the preregistered temporal sequence.

This is consistent with the broader literature being mixed: option prices, IV spreads/skew and option ratios can contain information about future returns, but the magnitude, horizon, market and implementation matter. NSE describes India VIX as an expected-volatility measure derived from NIFTY option prices, while academic studies document predictive content in relative option prices, IV spreads/skew and option volume ratios. These findings motivate testing but do not imply that any one signal should replace the present NIFTY weekly strategy's chooser.

## Decision
**Do not replace OTM6/7/8.**

The final direction-selection rule remains:
`X_call = CE(OTM8) + CE(OTM7) − CE(OTM6)`
`X_put = PE(OTM8) + PE(OTM7) − PE(OTM6)`

X_call > X_put selects the call-side bearish structure; X_put > X_call selects the put-side bullish structure.

## Strengths
- Direction-only isolation.
- Exact 190-trade universe.
- No lookahead.
- Training/validation/untouched-holdout separation.
- Explicit winner-retention and winner-to-loss protection.
- Alternative signals motivated by option-market and cross-market research.
- No post-result threshold relaxation.

## Limitations
- The final 2026 holdout contains only 15 trades.
- Reverse-side reconstruction is unavailable for five expiries; those selections were treated as no-trade rather than imputed.
- The direction candidates are intentionally simple; this phase did not search unrestricted machine-learning models.
- Some IV/PCR signals have missing historical observations, which reduces coverage.

## Final research implication
After Phase 22 entry filters, Phase 23 rich entry-state models, Phase 24 reversal triggers and now Phase 25 alternative direction choosers, the evidence increasingly supports retaining the original direction chooser rather than adding complexity.

Any future attempt to improve direction selection should require a genuinely new data source or structural hypothesis, not another permutation of the same entry-time variables.