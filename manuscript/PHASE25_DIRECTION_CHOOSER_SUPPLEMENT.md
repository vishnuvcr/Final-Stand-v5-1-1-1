# Phase 25 Manuscript Supplement — Alternative Direction Choosers

## Objective
Test whether the Phase-20 OTM6/7/8 premium-curvature direction chooser can be replaced by other point-in-time option, volatility, positioning, opening-state or cross-market signals while holding the rest of the strategy fixed.

## Candidate design
Tested raw and normalized premium curvature at k=6...15, matched call/put price ratios, matched IV spreads, OI and volume PCR with both sign conventions, NIFTY/opening/overnight/global-equity direction, and fixed aggregate voting signals.

## Temporal methodology
Training through 2023-12-31; validation 2024-01-01 through 2025-12-31; untouched holdout 2026-01-01 through 2026-09-30.

## Result
No alternative passed the preregistered training eligibility gate. Therefore no alternative was promoted to an OOS-selected rule.

The closest premium-curvature alternatives (k=7 and k=8) improved training P&L by only ₹162.83 and then lost ₹209.03 in validation and ₹0 in holdout.

The overnight-gap chooser gained ₹1,037.87 in training but failed the winner-protection condition and subsequently lost ₹127,189.87 in validation and ₹25,293.57 in holdout.

The global-equity median lost ₹31,734.34 in validation despite gaining ₹8,221.91 in the small 2026 holdout. It therefore failed the preregistered OOS gate.

## Literature context
NSE documents India VIX as a NIFTY-option-derived expected-volatility measure. Academic literature reports predictive information in relative option prices, implied-volatility spreads/skew and option volume ratios, but these relationships vary by market, horizon, moneyness and investor population. Phase 25 therefore treated them as hypotheses rather than assumed trading signals.

Sources:
- https://www.nseindia.com/static/products-services/indices-indiavix-index
- https://doi.org/10.1093/rfs/hhj024
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=721345
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3440805
- https://www.sciencedirect.com/science/article/pii/S1062976921001812

## Conclusion
The OTM6/7/8 direction chooser remains the final historical direction-selection rule. Phase 25 found no evidence sufficient to replace it.