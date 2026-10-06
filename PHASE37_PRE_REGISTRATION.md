# Phase 37 Pre-Registration — Corrected Model Direction Polarity

## Hypothesis
A model probability for an NIFTY up/bullish expiry move should be converted to the opposite Continuous Delta 6x6 spread direction: bullish/up -> PUT spread; bearish/down -> CALL spread.

## Null hypothesis
Correcting the model-to-spread polarity does not improve post-cost performance or robustness relative to the frozen stateful control.

## Why this phase exists
Phase 36 discovered after acceptance that the model-selector implementation used:
`p >= 0.50 -> CALL` and `p < 0.50 -> PUT`.
Phase 35's target definition is an up/down expiry move, so this is the inverse of the intended economic mapping.

## Frozen selector rules
For each model selector:
- CATBOOST
- DART
- WAVELET_TREE
- OOF_STACK
- MARKOV_REGIME_TREE

Use the cached Phase-35 probability for the corresponding expiry:
- `p >= 0.50` -> bullish/up -> PUT;
- `p < 0.50` -> bearish/down -> CALL.

No retraining, threshold search, calibration, or post-hoc polarity selection is permitted.

## Frozen execution
All entry, delta selection, exits, timing, expiry handling, position sizing, slippage and transaction-cost conventions are identical to Phase 36.

## Exclusions
OTM678_FRESH and OTM789_FRESH are excluded from this correction because their selector values are premium-curvature comparisons, not model probabilities for NIFTY direction.

## Statistical analysis
Compare each corrected selector with the Phase-32 stateful control using:
- net P&L and profit factor;
- maximum drawdown;
- temporal split;
- common-expiry bootstrap of selector-minus-control P&L;
- direction counts and trade-level diagnostics.

## Evidence rule
Only a successful GitHub Actions run with complete persisted artifacts is accepted.


## Execution trigger record — 2026-10-06
The preregistration is now frozen and the push-triggered GitHub Actions workflow is registered for numerical execution. No further parameter changes are permitted after this record except corrections of execution defects that are independently logged.
