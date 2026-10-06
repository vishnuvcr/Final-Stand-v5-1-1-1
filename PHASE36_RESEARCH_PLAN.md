# Phase 36 Research Plan — Independent Per-Trade Direction Selectors

## 1. Purpose
Test whether the Continuous Delta 6x6 Vertical Spread performs differently when the direction of every new trade is selected independently at that trade's entry opportunity, with no dependence on the previous trade's profit/loss or previous direction.

Phase 32 is the frozen execution-control specification. This phase changes only the direction-selection mechanism.

## 2. Primary research question
When the Continuous Delta 6x6 strategy is kept otherwise identical, does removing the prior-trade win/loss state machine and using a point-in-time direction selector before each entry improve robustness after realistic slippage, brokerage and statutory costs?

## 3. Experimental principle
For every eligible fresh entry:
1. Confirm no position is open.
2. Evaluate the registered direction selector using only information available at that entry.
3. Select CALL or PUT independently.
4. Enter the same 6-lot, 50-point vertical spread defined in Phase 32.
5. After exit, do not use the trade's P&L to retain or reverse direction.
6. The next eligible entry performs a new selector decision.

A losing trade therefore does not force the next trade to reverse, and a winning trade does not force the next trade to retain direction.

## 4. Selectors registered
Fresh point-in-time option selectors:
- OTM678_FRESH: X_call = CE8 + CE7 − CE6; X_put = PE8 + PE7 − PE6.
- OTM789_FRESH: X_call = CE9 + CE8 − CE7; X_put = PE9 + PE8 − PE7.

Frozen Phase-35 prediction selectors:
- CATBOOST
- DART
- WAVELET_TREE
- OOF_STACK
- MARKOV_REGIME_TREE

The five model signals are cached in data/phase36_selector_predictions.csv. They are frozen pre-entry forecasts for the corresponding expiry and are never updated from Phase-36 trade outcomes.

## 5. Frozen Continuous Delta 6x6 rules
- Underlying: NIFTY 50.
- Capital reference: ₹6,00,000.
- Position size: 6 lots per leg.
- Spread width: 50 NIFTY points.
- Current weekly expiry.
- New entries from 09:20 IST.
- No new entry on expiry day.
- Fresh entry blocked at or after 15:28 IST.
- CALL: short CE nearest +0.25 delta; long CE at short strike +50.
- PUT: short PE nearest −0.25 delta; long PE at short strike −50.
- CALL exit: short CE delta >= +0.50 or <= +0.04.
- PUT exit: short PE delta <= −0.50 or >= −0.04.
- No universal daily square-off.
- No discretionary rollover.
- Carry across sessions until delta exit or contract termination.
- Historical/date-aware lot-size schedule unchanged.
- One adverse ₹0.05 option tick per leg unchanged.
- Six executed orders per completed spread unchanged.
- Brokerage ₹10 per executed F&O order.
- Existing audited statutory/exchange charges unchanged.
- No forward fill, interpolation or synthetic option prices.
- Chronological cursor advances strictly beyond realized exit before the next entry is evaluated.

## 6. Control
Published Phase-32 strategy is the control:
- initial CALL;
- positive net P&L -> retain direction;
- negative net P&L -> flip direction;
- zero -> retain.

The Phase-32 control is not re-optimized here.

## 7. Analysis
For each selector report trade count, gross/net P&L, total costs, win rate, profit factor, mean/median trade, maximum drawdown, direction mix, direction changes, holding time, delta-exit vs contract termination, yearly/subperiod results, cost contribution, and selector coverage/skips.

## 8. Promotion gate
No selector is promoted solely for higher full-sample P&L. Promotion requires successful reproducible execution, complete ledger, no leakage/implementation gaps, positive post-cost performance, economically meaningful improvement versus the Phase-32 control, and stability across temporal subperiods.

Any new parameter search after observing these results is a new registered phase.

## 9. Required artifacts
- PHASE36_RESEARCH_PLAN.md
- PHASE36_PRE_REGISTRATION.md
- PHASE36_STRATEGY_SPEC.md
- PHASE36_STATUS.md
- research/phase36_independent_direction_overlay.py
- .github/workflows/phase-36-independent-direction-selector-overlay.yml
- data/phase36_selector_predictions.csv
- results/phase36_independent_direction/
