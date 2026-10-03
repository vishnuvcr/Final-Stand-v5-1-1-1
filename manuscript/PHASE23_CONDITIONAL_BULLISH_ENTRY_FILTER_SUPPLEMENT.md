# Phase 23 Supplement — Conditional BULLISH Entry Filter

## Research question

After Phase 22 showed that all 11 historical losing trades occurred in the BULLISH/put structure, can an entry-only filter applied only to BULLISH trades remove losses while preserving most winners?

## Directional subgroup

The 190-trade final strategy contains:
- BULLISH: 172 trades, 161 winners, 11 losses, net ₹113,161.72.
- BEARISH: 18 trades, 18 winners, 0 losses, net ₹35,967.81.

Thus the loss concentration is entirely in the BULLISH subgroup, but that subgroup also contains the great majority of profitable trades.

## Tested filters

Only BULLISH trades were eligible for filtering. BEARISH trades were always retained.

The pre-registered filters covered:
- direction-aligned 5-session NIFTY return;
- Stage-1 direction confidence;
- normalized expiry payoff-buffer distance;
- two-feature combinations of trend with direction confidence or payoff buffer.

Selection required at least 95% overall winner retention, removal of at least two training losses and positive training uplift.

## Result

No candidate satisfied the training safety screen.

The top unconstrained training diagnostic was:

**BULLISH direction margin >= 0.15**

It:
- reduced training P&L by ₹1,299.89;
- removed 12 profitable trades;
- removed only 1 losing trade;
- produced −₹44,201.97 uplift in 2024–2025 validation;
- produced −₹5,060.46 uplift in the 2026 holdout.

Therefore the directional asymmetry does not translate into a useful entry filter under the tested feature family.

## Interpretation

The fact that every historical loss is BULLISH is not enough to justify a BULLISH-side exclusion rule. The profitable BULLISH population overlaps heavily with the losing population in the entry-state variables tested.

In particular, the losing BULLISH trades can have:
- large payoff-buffer distance;
- strong Stage-1 direction margin;
- relatively large selected X;
- both positive and negative recent NIFTY returns.

This overlap explains why simple pre-entry thresholds sacrifice substantial profitable trades before they remove the tail losses.

## Conclusion

The Phase-20 entry rule remains unchanged.

The tested evidence does not support:
- excluding BULLISH trades wholesale;
- requiring a stronger Stage-1 BULLISH margin;
- requiring a simple recent-trend condition;
- requiring a simple normalized payoff-buffer condition.

## Research implication

The remaining scientifically distinct entry-filter opportunity is to incorporate information not contained in the existing 10:00 three-leg snapshot, such as:
- scheduled-event/event-gap risk;
- India VIX or implied-versus-realized volatility regime;
- overnight/global-market cross-asset regime;
- market-wide skew/tail-risk state.

These would require a separately registered phase and must use information available before the 10:00 decision point.

## References

Indian Nifty options research documents regime-dependent changes in option-implied volatility smiles, skewness and higher moments, including during major stress periods. citeturn198181search0turn198181search13

Recent Nifty research also reports that ATM and OTM skew-based option features can contain information about realized volatility, while work on Nifty variance risk premium highlights regime dependence. citeturn198181search4turn198181search3

More broadly, option-return literature finds that implied-volatility skew and risk-neutral skewness can contain information related to subsequent returns, although the direction and economic interpretation are context-dependent. citeturn967867search1turn967867search5
