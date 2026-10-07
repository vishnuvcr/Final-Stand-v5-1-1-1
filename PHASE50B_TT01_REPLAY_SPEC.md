# Phase 50B — TT-01 Common-Cost Replay Specification

## Strategy
Dynamic Ratio Reversals.

## Frozen source state machine
1. Initial state: put ratio.
   - Buy monthly PE at -0.50 delta.
   - Sell two monthly PE at -0.40 delta.
   - Buy one monthly PE at -0.10 delta.
2. Directional exit/transition is driven only by the defining short-leg delta thresholds in the source.
3. Continuation states:
   - Call: buy +0.40 CE, sell two +0.30 CE, buy +0.08 CE.
   - Put: symmetric -0.40 / -0.30 / -0.08.
4. Reversal states occur when the defining 0.10-delta short leg reaches an absolute delta of at least 0.60.
5. Every state has a universal monthly-expiry exit at/after 15:15 IST.

## Replay mechanics
- Use exact historical monthly expiry dates from the persisted option calendar.
- Reconstruct deltas from the exact observed option close using the common Black-Scholes/European-delta convention already registered for Phase 50B.
- Never interpolate missing quotes.
- Preserve the source state-machine order; do not infer discretionary exits from MFE or other diagnostics.
- Historical NIFTY lot sizes, ₹10/order brokerage, statutory charges, 0.05-point adverse option slippage and +50% total-cost stress are mandatory.

## Coverage rule
Every opened position must resolve to either:
- a completed source-faithful trade with all exit-leg quotes observed at/after the source trigger; or
- an explicit coverage exclusion.

No trade may disappear from the denominator.

## Statistical role
TT-01 remains a source-faithful control before any VIX conditioning. Any mutation must be separately preregistered and selected only on development data.
