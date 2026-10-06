# Phase 37 Strategy Specification — Corrected Model Direction Polarity

Phase 37 is the Phase-36 independent model-selector overlay with exactly one correction: the polarity between an NIFTY up/down model probability and the credit-spread structure is inverted to match the economic direction of the strategy.

## Model-to-trade mapping
- **Bullish / up probability >= 0.50 -> PUT spread**
  - sell 6 lots of current-week PE nearest -0.25 delta;
  - buy 6 lots at short strike - 50 points.
- **Bearish / down probability < 0.50 -> CALL spread**
  - sell 6 lots of current-week CE nearest +0.25 delta;
  - buy 6 lots at short strike + 50 points.

## Remaining strategy rules
- NIFTY 50.
- Current weekly expiry.
- Earliest entry 09:20 IST.
- No entry on expiry day.
- Last eligible entry before 15:28 IST.
- Exit on short-leg delta reaching the same Phase-32 thresholds.
- No universal daily square-off.
- No discretionary rollover.
- No overlap between positions.
- 6 lots per leg.
- Historical lot-size schedule unchanged.
- Same slippage, brokerage and statutory/exchange charge model.
- Same 1-minute historical resolution.

## Direction independence
Previous trade P&L, previous direction, win/loss result and cumulative strategy P&L are not inputs to model selection.

## Model input
Use only the frozen Phase-35 cached probability for the corresponding expiry. The probability is not recalibrated or modified in Phase 37.
