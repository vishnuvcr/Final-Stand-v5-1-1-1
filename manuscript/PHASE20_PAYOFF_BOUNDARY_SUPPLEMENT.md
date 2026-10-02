# Phase 20 Supplement — Payoff-Boundary Stop Research

## Research question

Does the entry-time expiry zero-P&L boundary from the payoff chart provide a robust early-warning exit when NIFTY moves materially beyond the green/profit region before expiry, and does it add information beyond the fixed 13:30 expiry-day conditional stop?

## Pre-registered methodology

The study used the corrected 190-trade dynamic-n ledger and exact common-minute observations of NIFTY spot and all three selected option legs.

For the selected structure, after the same one-tick entry execution adjustment:

- call-side upper expiry zero-P&L boundary = K_(n+1) + K_(n+2) − K_n + entry credit;
- put-side lower expiry zero-P&L boundary = K_(n+1) + K_(n+2) − K_n − entry credit.

Tested buffers:
0, 50, 100, 200 and 400 NIFTY points.

Tested confirmation:
1 or 3 consecutive complete minutes.

Tested condition families:
1. boundary crossing only;
2. boundary crossing + current combined MTM < 0;
3. boundary crossing + current MTM < 0 + running MFE < 0.50×target.

Selection used training data only with zero baseline-positive trades affected.

The fixed comparator was not re-optimized:
**13:30 IST on expiry day + combined MTM < 0 + running MFE < 0.50×original target.**

## Walk-forward result

The training-safe boundary selector was:

**400-point buffer / 1-minute confirmation / boundary-only**

| Period | Phase-19 0.50× MFE stop | Selected boundary stop |
|---|---:|---:|
| Training uplift | +₹1,963.67 | +₹711.91 |
| Validation uplift | +₹1,923.59 | −₹14,390.87 |
| 2026 holdout uplift | +₹6,305.15 | −₹49,064.48 |
| Full-sample uplift | +₹10,192.41 | −₹62,743.44 |

The selected boundary rule affected zero baseline-positive trades, but its out-of-sample P&L was strongly negative and its maximum drawdown rose to ₹41,711.94 in validation and ₹65,371.18 in the 2026 holdout.

The combined boundary-or-Phase-19 rule also failed out of sample.

## Why the boundary rule is rejected

The expiry zero-P&L boundary is a structural expiry payoff level. Before expiry, option time value, implied volatility and the joint response of the three legs can allow an apparent expiry-region breach to recover.

The data therefore do not support treating a payoff-chart green-area boundary crossing as an automatic intraday exit.

## Final exit implication

No pre-expiry payoff-boundary stop is included in the final strategy.

The final historical strategy exits by:
1. target;
2. 13:30 expiry-day conditional stop when current combined MTM < 0 and MFE < 0.50×target;
3. latest complete three-leg observation at or before 15:29 expiry-day fallback.

## Final-rule historical result

The final exit specification produced:

- 190 completed trades;
- ₹149,129.53 net P&L;
- ₹784.89 mean net per trade;
- 179/190 positive net trades (94.21%);
- profit factor 2.34;
- ₹27,336.11 maximum cumulative drawdown;
- 178 target exits;
- 5 conditional-stop exits;
- 7 expiry-fallback exits;
- zero baseline-positive trades stopped early.

These are historical backtest results with modeled transaction costs and one-tick adverse slippage. They are not a guarantee of future performance or live execution.
