# Phase 36 Pre-Registration — Independent Per-Trade Direction Selectors

## Hypothesis
The prior-trade P&L state machine may be unnecessarily path-dependent. A fresh point-in-time direction decision before every entry may produce a more robust Continuous Delta 6x6 equity curve and improve net performance after costs.

## Null hypothesis
Removing prior-trade state dependence does not improve net risk-adjusted historical performance.

## Frozen selector set
| Selector | Decision rule |
|---|---|
| OTM678_FRESH | CE8+CE7−CE6 vs PE8+PE7−PE6 at each entry |
| OTM789_FRESH | CE9+CE8−CE7 vs PE9+PE8−PE7 at each entry |
| CATBOOST | Phase-35 cached probability >= 0.50 -> CALL |
| DART | Phase-35 cached probability >= 0.50 -> CALL |
| WAVELET_TREE | Phase-35 cached probability >= 0.50 -> CALL |
| OOF_STACK | Phase-35 cached probability >= 0.50 -> CALL |
| MARKOV_REGIME_TREE | Phase-35 cached probability >= 0.50 -> CALL |

## Leakage controls
- OTM selectors use only the current entry snapshot.
- Model selectors use only the cached precomputed forecast for the current expiry.
- Previous Phase-36 trade P&L/status/direction is never an input to the next direction decision.
- No future minute, future option price, future trade outcome or future expiry observation may influence entry.
- Missing selector observations are logged, never imputed.

## Primary execution
Use the validated Phase-32 one-minute engine and cost model with the direction state machine replaced by an independent selector call at every new entry.

## Evidence acceptance
Only successful GitHub Actions runs persisting complete ledgers and diagnostics are accepted as numerical evidence.

## Decision
A positive candidate may advance only to a separately registered forward/paper execution phase with live bid/ask, fills, latency and broker costs.
