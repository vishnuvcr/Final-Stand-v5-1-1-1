# Phase 32 — Final Results Index

## Decision

**PROMISING BUT INSUFFICIENTLY ROBUST — NO LIVE PROMOTION**

## Accepted evidence

- Final engine revision: `f89e1e5574aa26b69288ae93b9cf180bf9882242`
- Final GitHub Actions run: [37388261915 / #41](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37388261915)
- Final artifact: ID 11380124540
- Artifact SHA-256: `c97657e5ec4acd4023e133e82cb586b242f030f7ef76985638fcdbcf0b84943`
- Trades: 478
- Net P&L: ₹83,820.48
- Win rate: 63.60%
- Profit factor: 1.112
- Maximum drawdown: ₹94,492.83

## Core documents

- [Phase 32 research manuscript](../../manuscript/PHASE32_CONTINUOUS_DELTA_MANUSCRIPT.md)
- [Phase 32 conclusion](PHASE32_CONCLUSION.md)
- [Statistical summary](PHASE32_STATISTICAL_SUMMARY.csv)
- [Evidence figures](figures/PHASE32_FIGURES.svg)
- [Frozen strategy rules](PHASE32_STRATEGY_RULES.md)
- [Literature review supplement](PHASE32_LITERATURE_REVIEW.md)

## Interpretation

The strategy is profitable on the available historical sample, but the evidence is not strong enough for live promotion because:

- the trade-level mean P&L is not statistically separated from zero;
- 2021–2022 was materially negative while 2023–2025 supplied most of the profit;
- maximum drawdown exceeded cumulative net profit;
- 4 ticks of slippage remove the edge;
- the public option source is incomplete, including 25 missing expected expiries and one incomplete later expiry.

Phase 20 remains the canonical historical strategy.

## Data and reproducibility

The complete machine-readable trade ledger and raw workflow outputs remain preserved in the final GitHub Actions artifact. This branch contains the phase manuscript, statistical summary, conclusion, rule card, literature supplement and repository-hosted figures.
