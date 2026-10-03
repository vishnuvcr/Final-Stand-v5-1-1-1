# Phase 22 Supplement — Entry Criteria for Avoiding Losing Trades

## Research question

Can entry-time information available at 10:00 IST distinguish trades that will eventually lose under the frozen Phase-20 strategy, while preserving most profitable trades?

## Method

The corrected 190-trade dynamic-n ledger was used. The final Phase-20 exit logic remained unchanged. Entry-only features were tested in four families:

1. payoff-boundary distance and normalized distance;
2. direction-selection confidence;
3. structure-quality measures;
4. pre-entry NIFTY return and realized-volatility regimes.

Controlled two-feature combinations were also pre-registered.

Training selection used 2021-05-27 through 2023-12-31. Validation used 2024–2025. The 2026 sample through 2026-09-30 was held out.

The training safety screen required at least 95% winner retention, at least two losses removed, and positive P&L uplift. Promotion additionally required positive validation and holdout uplift, at least 90% winner retention in both, and no more than 5% maximum-drawdown deterioration.

## Results

No candidate passed the training screen.

More strongly, no tested rule removed even one training loss while retaining all profitable training trades. No candidate removed at least two losses while retaining at least 95% of winners.

The closest loss-removing rule was direction-margin >= 0.15:
- training P&L uplift: −₹2,300.22;
- training winner retention: 85.26%;
- training losses removed: 1;
- validation uplift: −₹70,498.06;
- 2026 holdout uplift: −₹11,906.12.

The 20-day realized-volatility <= training 80th-percentile rule removed two training losses but retained only 82.11% of winners. Its validation uplift was −₹41,885.62; its 2026 holdout uplift was +₹6,148.49. The isolated holdout improvement is therefore not sufficient evidence for promotion.

## Interpretation

The tested entry-state variables do not provide a stable low-cost way to identify the strategy's tail losses.

The losses are heterogeneous with respect to the tested payoff geometry, direction confidence, structure quality and recent NIFTY regime. Stronger filters generally remove profitable trades before they remove enough losses to improve the strategy.

Combined with Phase 21's failure of fixed pre-expiry NIFTY-point risk controls, the current evidence suggests that the loss mechanism is not captured by a single simple spot/structure threshold.

## Implication for future research

A richer entry-risk phase could test information that the present phase deliberately excluded:
- full option implied-volatility surface and skew;
- India VIX;
- NIFTY futures basis;
- overnight/global-market return and gap state;
- pre-10:00 event/news regime;
- FII/DII and index-flow proxies available before entry;
- cross-asset risk regime.

Because only 11 of 190 trades are losses, an unrestricted machine-learning classifier would have substantial overfitting risk. Any future model should therefore be strongly regularized, economically interpretable where possible, and evaluated with walk-forward temporal validation and a completely untouched holdout.

## Conclusion

No Phase-22 entry criterion is promoted. The Phase-20 entry and exit rules remain unchanged.

