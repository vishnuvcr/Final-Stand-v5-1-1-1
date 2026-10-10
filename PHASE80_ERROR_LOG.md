# Phase 80 Error / Limitation Log
Date: 2026-10-10

## E80-001 — Strategy-space completeness cannot be proven
- Status: DOCUMENTED LIMITATION.
- The repo includes broad prior searches but no possible finite combination universe; this search therefore defines a limited, pre-registered next experiment rather than claiming literal exhaustiveness.

## E80-002 — External dataset rights ambiguity
- Status: OPEN FOR ZENODO / artist-23 / rissin leads.
- Exact metadata shows blank/unclear rights for Zenodo, no clear license on artist-23, and “other” plus Upstox terms on rissin. No raw files downloaded or retained from these sources.

## E80-003 — Static option holding does not replicate delta-hedged literature
- Status: DOCUMENTED METHODOLOGY LIMITATION.
- Bhat et al. (2024) examines delta-hedged option returns. Proposed Phase 81 baskets are static multi-leg positions with entry/exit between candle opens. Results must not be presented as direct replication.

## E80-004 — OHLC data does not prove executable fills
- Status: OPEN.
- The current primary dataset lacks historical bid/ask/depth. Nonzero volume and adverse tick adjustments are necessary screens but do not establish exact fillability.

## E80-005 — Historical search multiplicity
- Status: OPEN.
- Multiple prior phases explored many variants; final manuscript must disclose known variant counts and use multiple-testing correction for new confirmatory claims. Historical total trials are incompletely enumerable, so Deflated Sharpe inputs may require conservative bounds and explicit limitation.
