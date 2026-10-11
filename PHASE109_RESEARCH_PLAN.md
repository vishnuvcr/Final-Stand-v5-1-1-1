# Phase 109 — Exhaustive Finite Parameter-Grid Research Plan

Branch: phase-109-exhaustive-parameter-grid. Parent: Phase 108. Registration only; execution is not complete until audited outputs are committed.

## Research question
Across ten registered strategy families, which parameter configurations survive broad prespecified search after conservative costs, and do any survive a genuinely untouched chronological holdout?

## Mandatory search size
- Minimum 1,000 unique configurations per strategy family; at least 10,000 unique strategy-configuration pairs overall.
- Enumerate every registered value for every variable by Cartesian product, not random sampling or post-result hand selection.
- Save configuration IDs and the full finite search-space manifest before replay. Duplicate tuples prohibited. If a family has fewer than 1,000 distinct valid combinations, expand the preregistered finite grid before running; never pad counts with duplicates.
- Evaluate every cost configuration for every parameter tuple. Report unique configurations separately from cost-scenario rows.

## Frozen grid dimensions
1. Signal lookback sessions: 1, 2, 3, 4, 5, 7, 10.
2. Absolute-return/move threshold: 0%, 0.25%, 0.5%, 0.75%, 1%, 1.5%, 2%.
3. Volatility lookback: 3, 5, 7, 10, 15 sessions.
4. Volatility classification: rolling median; lower-/upper-third, with middle bucket no-trade.
5. Strike target: ATM, 0.5% ITM, 0.5% OTM, 1% ITM, 1% OTM.
6. Entry delay: next-session open only; no same-bar lookahead.
7. Holding/exit: same-session close, 2-session close, 3-session close, expiry-aware close only if chronology/data permit.
8. Stop/target: none; 10%/20%/30% premium stop; 10%/20%/30% premium target; combined pairs only where explicitly represented.
9. OI confirmation: off, total near-ATM OI increase, same-side OI increase only where valid prior-day comparisons exist.
10. Costs: brokerage ₹10/₹15/₹20 per order; adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per unit per side; modeled fees 1×/1.5×.

The full Cartesian product may be large. Enumerate in bounded chunks and fail closed if any registered tuple is skipped. Declare strategy-family applicability masks before replay; inapplicable dimensions must be marked NA in the manifest. Ensure at least 1,000 unique valid tuples per family and evaluate all cost configurations for each.

## Data and validation
- Use approved public NSE daily UDiFF source unless a separate rights-approved source is registered.
- Phase 106–108 month is development/debug data only, never an independent holdout.
- Acquire longer data where available; split chronologically into development, validation and untouched test periods before viewing grid results. Persist source hashes, coverage, missingness and archive manifest. Raw rows remain ephemeral unless redistribution rights are confirmed.
- If sufficiently long, contract-consistent data cannot be acquired, the grid is a development diagnostic only; explicitly block OOS efficacy conclusions and stop without promotion.
- Require exact same contract identity, observed target-session data, positive volume, valid OHLC and consistent lot size. OHLC remains a proxy, not executable bid/ask fills.

## Statistics and anti-overfit
- Record every configuration, not only winners; publish aggregate metrics and exclusions.
- Primary outcomes: net P&L after brokerage, modeled statutory charges and adverse slippage; return on premium; drawdown; expectancy; profit factor; trade count and coverage.
- Use session-cluster bootstrap intervals and a declared multiple-testing procedure (e.g. Holm for confirmatory tests); report total configurations. Naive best-of-grid P-values are not valid inference.
- Compare development and validation without changing the frozen grid. Touch the final holdout once only after selection is frozen; if unavailable, mark blocked.
- Include base and strict cost scenarios. Paytm Money charges remain estimates until compared to a real user-provided contract note.

## Acceptance gates
1. Tests prove deterministic grid generation, unique IDs, at least 1,000 unique tuples per family and full Cartesian enumeration.
2. Evaluated count equals manifest count × declared cost scenarios; no missing combinations.
3. Source and contract identity gates pass.
4. Accounting reconciles gross minus slippage minus fees to net within ₹0.10 aggregate tolerance.
5. Commit results, coverage, skipped-configuration reasons, figures, manifest, logs and README links.
6. No strategy promotion without untouched chronological OOS, multiple-testing control and conservative costs. A grid run alone cannot justify live deployment.

## Bounded phases
109.0 register grid; 109.1 implement enumerator/manifest/tests; 109.2 data feasibility and chronological split; 109.3 run all configurations and costs; 109.4 statistical/accounting audit; 109.5 publish reports, manifest, aggregates, logs and README. Stop after 109.5 or a documented data/rights gate; do not search endlessly or relax gates to force a winner.
