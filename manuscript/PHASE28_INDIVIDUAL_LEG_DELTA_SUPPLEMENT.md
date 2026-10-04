# Phase 28 Supplement — Individual-Leg Delta Exit Research

## Research question
Can the delta of individual legs, especially the short OTM-(n+1) and OTM-(n+2) legs, provide a better profit-taking or risk-control signal than portfolio delta?

## Method
The Phase-20 strategy was frozen as control. For every minute with complete three-leg observations, implied volatility and delta were reconstructed independently for each leg using European Black-Scholes with r=0 and q=0. No interpolation or forward filling was used. Absolute delta was used for level comparisons across CE and PE structures.

NIFTY index options are European-style CE/PE contracts according to NSE's current contract specification. urlNSE NIFTY 50 F&O contract informationhttps://www.nseindia.com/static/products-services/equity-derivatives-nifty50

The experiment tested S1 and S2 separately:
- profit booking at 50/60/70/80/90% target crossed with delta thresholds;
- adverse stop at negative MTM with delta thresholds and 1/3-minute confirmation.

Temporal selection used training through 2023-12-31, validation 2024-01-01 to 2025-12-31 and untouched 2026 holdout.

## Results
The training selector chose S1 with 90% target and |delta|≤0.05 because it was the least negative training rule. It still lost ₹2,998.16 in training, ₹2,487.05 in validation and ₹35.91 in the 2026 holdout relative to control.

No adverse-delta stop was viable. The stop grid produced large negative P&L uplifts even at high delta thresholds.

The full-sample candidate net was ₹143,608.40 versus ₹149,129.53 control.

## Interpretation
Individual-leg delta contains structural information: the nearer short leg S1 is, on average, more delta-sensitive than S2. However, absolute delta level does not identify a robust point at which this strategy should exit. The result is consistent with the idea that delta is state-dependent and not, by itself, sufficient as a timing variable for this three-leg payoff.

## Decision
**Reject individual-leg absolute-delta exit rules. Do not alter Phase-20.**

A future delta phase, if justified, should be a materially different hypothesis such as delta acceleration/change, gamma or a jointly specified risk-state model, with a fresh pre-registration rather than another absolute-level sweep.
