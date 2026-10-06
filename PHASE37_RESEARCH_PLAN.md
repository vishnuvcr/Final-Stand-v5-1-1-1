# Phase 37 Research Plan — Corrected Model Direction Polarity

## Purpose
Correct and independently validate the Phase-36 model-selector overlay after identifying that model probabilities for an NIFTY up move were mapped to the wrong Continuous Delta 6x6 spread direction.

## Primary research question
When a model predicts NIFTY **bullish/up**, does entering the **PUT** credit spread, and when it predicts **bearish/down**, entering the **CALL** credit spread, improve the Continuous Delta 6x6 strategy relative to the frozen Phase-32 stateful direction control?

## Scientific correction
Phase 35 defines the prediction target as the sign of:
`log(expiry_close / reference_spot)`.
Therefore the model probability is interpreted as probability of an **up/bullish expiry move**.

The corrected trading mapping is:
- model probability >= 0.50 = bullish/up = PUT spread;
- model probability < 0.50 = bearish/down = CALL spread.

The Phase-36 mapping used the reverse. Phase-36 model-selector numerical results are therefore retained for audit but are not treated as a valid test of the intended model-to-spread hypothesis.

## Registered treatments
Only the five Phase-36 model selectors are rerun:
- CATBOOST
- DART
- WAVELET_TREE
- OOF_STACK
- MARKOV_REGIME_TREE

OTM678_FRESH and OTM789_FRESH are not changed or reinterpreted in this correction phase because their premium-curvature comparison is not a calibrated bullish-probability output.

## Frozen trading rules
All non-direction rules remain exactly those of the accepted Phase-32/Phase-36 execution engine:
- NIFTY 50 current weekly expiry.
- 6 lots per leg.
- 50-point vertical.
- Entry from 09:20 IST.
- No new entry on expiry day.
- No new entry at or after 15:28 IST.
- CALL: sell CE nearest +0.25 delta; buy CE at +50.
- PUT: sell PE nearest -0.25 delta; buy PE at -50.
- CALL exit: short CE delta >= +0.50 or <= +0.04.
- PUT exit: short PE delta <= -0.50 or >= -0.04.
- No universal daily square-off.
- No discretionary rollover.
- Chronological non-overlap.
- Same option-price slippage, brokerage, statutory/exchange charges and lot-size schedule as Phase 32/36.
- No forward filling or synthetic prices.

## Leakage controls
- Use the frozen Phase-35 cached probability for each expiry.
- Do not retrain or recalibrate models.
- Do not tune the 0.50 threshold after seeing Phase-37 results.
- Do not use previous trade P&L, direction or cumulative strategy P&L.
- Do not use future option prices or future trade outcomes.
- Preserve the untouched 2026 holdout definition.

## Evaluation
Primary sample: 2024-01-01 through 2026-06-30, matching Phase 36.

Report:
- trade count;
- gross P&L;
- costs;
- net P&L;
- win rate;
- profit factor;
- maximum drawdown;
- direction mix;
- yearly/subperiod performance;
- expiry-level selector-minus-control bootstrap intervals;
- selector coverage and skips.

The 2024-2025 period is the historical development/validation comparison; 2026 remains the untouched holdout for the model family.

## Promotion gate
No model is promoted from this correction phase solely on full-sample P&L. A candidate must:
1. execute reproducibly with complete audit artifacts;
2. use the corrected polarity exactly;
3. be positive post-cost;
4. show economically meaningful improvement over the stateful control;
5. remain credible on the 2026 holdout;
6. avoid evidence of leakage or implementation error.

Any further threshold, calibration or model change is a new registered phase.

## Expected artifacts
- PHASE37_RESEARCH_PLAN.md
- PHASE37_PRE_REGISTRATION.md
- PHASE37_STRATEGY_SPEC.md
- PHASE37_STATUS.md
- research/phase37_model_direction_polarity_correction.py
- .github/workflows/phase-37-model-direction-polarity-correction.yml
- results/phase37_model_direction_polarity_correction/
