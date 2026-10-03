# Phase 23 Manuscript Supplement — Rich Entry-State and Directional-Switch Study

## Methods

The Phase-23 study used the frozen Phase-20 dynamic-n strategy as comparator and expanded only entry-time information. The study was pre-registered before modeling and used a 2021–2023 training period, 2024–2025 validation period, and untouched 2026 holdout.

Feature domains included volatility, India VIX, realized NIFTY volatility, cross-market returns, overnight/opening state, option premiums/OI/volume, IV/skew proxies, and payoff geometry. All external daily variables were restricted to prior-session observations relative to the 10:00 IST entry.

Two balanced logistic models estimated canonical-loss probability and reverse-superiority probability. A fixed canonical/reverse/skip policy grid was selected on training data only.

## Main result

The training-selected policy produced +₹23,352.60 training uplift but −₹1,344.36 validation uplift and ₹0 holdout uplift. The promotion gate failed.

## Secondary observations

A reverse-only training-selected policy also failed out of sample. The reverse ledger reconstructed 185/190 trades.

The 11 historical canonical losses all had profitable opposite-side reconstructions. This is useful for hypothesis generation but is retrospective and not sufficient evidence of deployable predictability.

## Strengths

The study used a fixed temporal split, an untouched holdout, exact execution-cost treatment inherited from the canonical engine, point-in-time entry variables, a bounded model class, and an explicit universe-alignment check.

## Limitations

Only 11 canonical losses occurred in the 190-trade control sample. The 2026 holdout contains 15 trades, so estimates are statistically unstable. Cross-market/futures/FII-DII/event features were not all available with verified point-in-time historical timestamps and were not imputed into the model when unavailable. The model was deliberately kept simple to reduce overfitting.

## Conclusion

Phase 23 does not support changing the canonical Phase-20 direction/entry logic. The evidence motivates but does not validate a narrower reversal-trigger hypothesis, which is evaluated separately in Phase 24.
