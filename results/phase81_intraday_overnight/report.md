# Phase 81 — Paired intraday vs overnight option-structure sweep

**Decision: exploratory comparison complete; no strategy promotion from this phase.**

- Pinned source revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
- Declared structure variants: 10; paired windows: intraday and overnight.
- Expiry files loaded: 238; complete paired rows: 10286; paired date×variant differences: 5143.
- Assigned sessions before completeness exclusions: 1139; exclusion records: 6202; file errors: 0.
- Temporal window: development through 2023-12-31, validation through 2025-12-31. No 2026 holdout rows are loaded, scored or ranked.
- Primary prices are 09:20/15:20 candle opens with common 09:19 spot-based ATM anchor; require all exact expiry/strike/side bars and nonzero volume at entry/exit.
- Costs include assumed Paytm Money brokerage of ₹10 per executed order, historical statutory fees, one adverse ₹0.05 tick per leg/fill and a two-tick stress. OHLC-only fills do not prove executable prices.

## Highest-level results (descriptive only)

See summary_by_split_variant_window.csv for every structure and time window; paired_window_differences.csv for matched overnight-minus-intraday comparisons; descriptive_lagged_vix_summary.csv for lagged regime counts and outcomes; exclusions.csv for omitted observations.

## Method boundary

The holding-window test is a static-structure adaptation motivated by published delta-hedged overnight/intraday evidence; it is not a direct replication. The 10 declared structure variants are a bounded test basket, not all possible options strategies/parameter combinations. No candidate has been promoted; Phase 82 must perform paired/expiry-cluster inference and multiple-testing correction before any holdout confirmation.

## File errors
None logged.
