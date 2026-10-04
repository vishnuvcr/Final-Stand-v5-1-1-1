# Phase 27 Status — Delta-Based Exit Research

**Status: COMPLETE — NO DELTA EXIT PROMOTED**

## Control
Locked Phase-20 final historical strategy:
- 190 trades
- ₹149,129.53 net P&L
- 179/190 profitable
- profit factor 2.34
- maximum drawdown ₹27,336.11

## Delta reconstruction
- 1-minute portfolio delta reconstructed from observed option prices.
- European Black-Scholes implied volatility, r=0, q=0 baseline.
- Delta coverage: **99.21%** of reconstructed minute observations.
- Portfolio delta uses actual three-leg signs.
- No price interpolation or forward filling.

## Walk-forward result

Training-selected profit rule:
**gross MTM >= 0.90×original target AND |portfolio delta| <= 0.05**

No adverse-delta stop was selected because the pre-registered training screen did not produce a useful candidate.

| Period | Control net | Delta candidate net | Uplift |
|---|---:|---:|---:|
| Training | ₹62,905.98 | ₹57,140.07 | **−₹5,765.91** |
| Validation | ₹75,809.78 | ₹73,475.74 | **−₹2,334.04** |
| 2026 holdout | ₹10,413.76 | ₹9,305.72 | **−₹1,108.04** |
| Full sample | ₹149,129.53 | ₹139,921.53 | **−₹9,208.00** |

Bootstrap 95% CI for mean trade-level uplift:
- Validation: −₹30.31 [−₹98.23, +₹86.97]
- Holdout: −₹69.25 [−₹141.92, −₹13.82]
- Full: −₹48.46 [−₹78.99, +₹5.25]

## Decision
**Reject delta-based profit booking and adverse-delta stopping for the canonical strategy.**

The Phase-20 strategy remains unchanged.

## Interpretation
The result does not mean delta is useless. It means that, under this structure and holding period, simple threshold rules on reconstructed portfolio delta did not improve the already-validated exit framework. The strategy's existing target and expiry-day MFE stop are superior to the tested delta-triggered exits in the registered walk-forward experiment.

## Strengths
- Exact observed option prices and NIFTY minute observations.
- Portfolio rather than single-leg delta.
- Same slippage, brokerage and statutory cost model as the control.
- Train/validation/2026 holdout separation.
- Bootstrap paired trade-level inference.
- All implementation errors were logged and corrected before evidence acceptance.

## Limitations
- Delta is model-implied, not exchange-published historical Greek data.
- Baseline uses r=0 and q=0; alternative volatility-surface specifications were not needed for promotion because the registered candidate failed out of sample.
- 2026 holdout contains only 16 trades.
- LTP/close data do not reproduce live bid/ask/latency/partial fills.

## Future direction
Do not add a delta exit to the live candidate from this phase. If delta is revisited, test a substantially different information design rather than another threshold sweep: smile-adjusted/model-free delta, regime-conditioned delta, delta acceleration, gamma-adjusted exposure, or interaction with VIX/cross-market state. Any such study must be preregistered as a new phase.
