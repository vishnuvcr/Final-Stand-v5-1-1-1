# Phase 26 Conclusion — Direct OTM7/8/9 Structure Test

## Result

The fixed **OTM7/8/9** structure (buy OTM7, sell OTM8 and OTM9) was reconstructed on the same 190-trade corrected executable universe, with the locked OTM6/7/8 Stage-1 direction chooser and identical target, slippage, brokerage, statutory charges and lot-size assumptions.

| Metric | Locked dynamic-n | Fixed OTM7/8/9 |
|---|---:|---:|
| Trades | 190 | 190 |
| Net P&L | ₹138,937.12 | ₹129,567.71 |
| Net winners | 179 | 180 |
| Net losses | 11 | 10 |
| Max drawdown | ₹27,321.08 | ₹24,081.63 |
| Profit factor | — | 2.29 |

The fixed 789 structure therefore **avoided 1 of the 11 historical losing trades, not 2**.

### The one loss that changed into a winner

- Expiry: **2026-03-17**
- Dynamic-n result: **−₹632.58**
- Fixed OTM7/8/9 result: **+₹5,850.83**
- Improvement: **+₹6,483.41**
- Dynamic-n exit: expiry
- Fixed-789 exit: target

### What happened to the other 10 losses?

All remained losses under fixed 789, although each was less negative than the dynamic-n result. No historical dynamic-n winner was converted into a fixed-789 loss.

The fixed 789 structure nevertheless produced **₹9,369.41 less net P&L** over the full 190-trade sample because changing from the dynamically selected n to fixed n=7 reduced profits on many otherwise successful trades.

## Interpretation

The claim that “789 saved us from 2 losses” is **not supported by the corrected 190-trade direct structure test**. The corrected evidence shows one loss-to-win conversion.

This does not mean OTM7/8/9 is intrinsically inferior in every respect: it produced fewer losing trades and lower maximum drawdown in this historical reconstruction. But its aggregate net P&L was lower by ₹9,369.41, so the loss-count improvement did not compensate for the profit sacrificed elsewhere.

## Important scope limitation

This Phase-26 first reconstruction uses the corrected engine's standard target/expiry fallback. It is a direct **structure** test and does not silently replace the frozen Phase-20 expiry-day conditional stop. Therefore it should not be interpreted as a final replacement for the complete Phase-20 entry-to-exit specification.

If the research question is specifically whether fixed 789 combined with the **complete Phase-20 exit stack** saves two losses, that is a separate, explicitly registered follow-up rather than a post-hoc reinterpretation.

## Decision

No change is made to the canonical Phase-20 strategy. OTM6/7/8 direction selection and dynamic-n construction remain frozen.

Phase 26 is complete for the preregistered direct-structure question.
