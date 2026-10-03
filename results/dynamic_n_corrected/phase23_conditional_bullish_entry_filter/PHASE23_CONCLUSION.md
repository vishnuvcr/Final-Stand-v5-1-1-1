# Phase 23 — Conditional BULLISH Entry Filter Conclusion

## Directional asymmetry

All **11** baseline losing trades in the 190-trade final strategy were BULLISH/put-structure trades.

All **18** BEARISH/call-structure trades were profitable.

That is a strong subgroup pattern, but BULLISH trades also contain **161 winners**, so rejecting the BULLISH side wholesale is not acceptable.

## Result

**No BULLISH-only filter passed the training safety screen.**

The screen required at least 95% overall winner retention, removal of at least 2 training losses, and positive training uplift.

The top unconstrained candidate was **bullish_direction_margin_ge_0.15**.

Training uplift: ₹-1299.89  
Training losses removed: 1  
Training winners removed: 12  
Validation uplift: ₹-44201.97  
2026 holdout uplift: ₹-5060.46

## Decision

The BULLISH/put entry should **not** be excluded as a whole.

The Phase-20 entry rule remains unchanged.
