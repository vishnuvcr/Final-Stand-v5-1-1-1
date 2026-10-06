# Phase 49 Research Plan — VIX Leader Parameter Tuning

## Research question

Can the strongest empirically observed VIX-conditioned NIFTY structures—LOW/NORMAL Bear Call Spread, LOW/NORMAL Bear Put Spread, and LOW Put Broken-Wing Butterfly—be improved by tuning strike geometry, hedge width, entry time and entry timing in a way that remains robust out of sample?

## Scientific premise

Phase 45 identified LOW-VIX Bear Call Spread as the strongest validation candidate (+₹24,742.59 net; +₹23,082 at +50% fee/charge stress), with LOW-VIX Bear Put Spread and LOW-VIX Put BWB also positive. NORMAL-VIX Bear Call and Bear Put were also positive. None survived the full Holm statistical gate. Phase 49 therefore treats them as hypotheses to optimize, not as validated strategies.

Parameter searching creates data-snooping risk. White-style Reality Check work shows that selecting the best strategy from a large rule universe requires correction for the full search family, while backtest-overfitting research shows that many tested configurations can create spuriously strong historical results. Phase 49 therefore separates tuning from confirmatory validation and uses a protected 2026 holdout. It also uses forward-fold consistency inside the development period rather than one full-sample optimum.

## Registered strategy families

1. Bear Call Credit Spread — LOW and NORMAL VIX.
2. Bear Put Debit Spread — LOW and NORMAL VIX.
3. Put Broken-Wing Butterfly — LOW and NORMAL VIX.

FALLING-VIX candidates are recorded as a secondary observation only and are not included in the primary optimization family because Phase 45 did not meet the 20-trade validation threshold for those states.

## Parameter universe

### Bear Call
- Short call offset from ATM: 1, 2, 3, 4 strike steps.
- Width: 1, 2, 3, 4 strike steps.
- Long call = short offset + width.
- Entry clock: 09:30, 10:00, 10:30, 11:00 IST.
- Entry distance: 3, 4, 5 trading sessions before expiry.

192 geometric/timing configurations per VIX state.

### Bear Put
- Long put offset: 0, +1, +2 strike steps (higher strike is closer to/above ATM).
- Width: 1, 2, 3, 4 strike steps.
- Short put = long offset − width.
- Entry clock: 09:30, 10:00, 10:30, 11:00 IST.
- Entry distance: 3, 4, 5 trading sessions before expiry.

144 configurations per VIX state.

### Put Broken-Wing Butterfly
- Short/body put offset: 0 or +1 strike steps.
- Upper long-put distance above the body: 1, 2, 3, 4 steps.
- Lower long-put distance below the body: 1, 2, 3, 4 steps.
- Structure: +1 PE at body+upper, −2 PE at body, +1 PE at body−lower.
- Entry clock: 09:30, 10:00, 10:30, 11:00 IST.
- Entry distance: 3, 4, 5 trading sessions before expiry.

384 configurations per VIX state.

Total primary search universe: **1,440 parameter×regime candidates**.

## Data splits

Development/tuning: 2021-05-27 through 2023-12-31.
Validation: 2024-01-01 through 2025-12-31.
Protected holdout: 2026.

Parameter selection is permitted only with development data.

## Internal development robustness

To avoid selecting a single-sample historical peak, development tuning uses forward folds:
- Fold A: 2021 data as parameter-selection history; evaluate candidates on 2022.
- Fold B: 2021–2022 history; evaluate candidates on 2023.

The primary development score is the average forward-fold stressed net P&L per trade, with hard requirements for positive stressed P&L and minimum opportunity count in each forward fold. A consistency bonus is applied when the candidate is positive in both folds.

Parameter candidates that are isolated peaks without neighboring support are flagged as overfit-risk even when their score is high.

## Robustness criteria

Within each strategy×VIX state, candidate ranking uses:
- average forward-fold net P&L per trade;
- average forward-fold +50% fee/charge stress P&L per trade;
- profit factor;
- maximum drawdown penalty;
- consistency across 2022 and 2023;
- neighborhood/plateau support in parameter space.

Minimum development eligibility:
- at least 10 forward-fold trades in each scoring fold;
- positive stressed mean/trade in each scoring fold;
- positive mean net/trade in both folds;
- no catastrophic drawdown multiple relative to cumulative stressed profit.

## Confirmatory validation

One top parameter configuration per strategy×VIX state is frozen from development only.

Validation is then run with the exact frozen parameters. No validation-based parameter adjustment is permitted.

A frozen candidate is considered confirmatory-working only if it has at least 20 validation trades, positive validation net, positive validation +50% charge-stress net, and positive active-vs-complement VIX advantage.

Formal statistical inference uses 10,000 bootstrap resamples and 10,000 one-sided permutation tests. Holm correction is applied across the six frozen primary strategy×VIX candidates.

## Holdout

Only validation-confirmed candidates are opened on the untouched 2026 holdout. Holdout cannot change parameters or definitions.

## Execution model

- Historical NIFTY lot sizes with the audited contract-specific schedule.
- ₹10 Paytm Money F&O brokerage per executed order.
- Date-aware Indian STT, exchange transaction charges, SEBI fee, IPFT, stamp duty and GST.
- One adverse ₹0.05 option tick per leg at entry and exit.
- +50% monetary fee/charge stress; the adverse ₹0.05 tick remains fixed.
- No forward filling, interpolation or synthetic option prices.
- Exact observed 10:00-style intraday snapshots are replaced by registered alternative entry clocks only for this tuning grid.

## Self-audit gates

1. Definition audit: every parameter combination expands to the intended ordered strikes and defined-risk payoff.
2. Point-in-time VIX audit.
3. Historical lot-size audit.
4. Entry/expiry calendar audit.
5. Duplicate/missing quote audit.
6. Development fold isolation audit.
7. Validation freeze audit.
8. Holdout contamination audit.
9. Multiple-testing and parameter-search-family audit.

Any failed gate invalidates the affected run until corrected and rerun; all failures are logged in ERROR_LOG.md.

## Stop condition

Phase 49 closes after all 1,440 primary candidates are tuned on development, one configuration per strategy×VIX state is frozen, confirmatory validation is complete, qualifying candidates receive untouched 2026 confirmation, and the final parameter surface/manuscript are stored.

Adaptive VIX-threshold tuning, dynamic intraday adjustments and portfolio-level multi-strategy routing are separate follow-up phases.