# Phase 66 — OHLC-Based Paper Replication Plan

## Purpose
Independently reproduce the paper-derived NIFTY option strategy using the available minute OHLC data, while distinguishing a faithful replication from an adapted test. This phase does not claim to reproduce the original paper's source data or executable quotes.

## Research question
Can the published Shaha (2019) CCI monthly NIFTY options rules be independently reconstructed and evaluated using available historical OHLC bars, with causal timing, realistic cost sensitivities, and explicit coverage accounting?

## Scope and preregistration
1. Primary target: Shaha (2019), “An Empirical Study on Options Trading Strategy Using ‘Commodity Channel Index’ for NSE’s Nifty Options in India.”
2. Secondary candidate: the already-frozen CCI + EMA50/EMA200 filter; label it an adaptation, not a reproduction of the paper.
3. Data source: pinned community dataset `thetrademarkk/india-index-options-1m`, revision `3eacf762d401efd9a08e804592fa7882b354c4a2`, subject to its CC-BY-NC-4.0 license. Do not redistribute raw data.
4. Available sample does not span the paper's full Oct 2008–Sep 2018 period. Report actual coverage and do not imply exact replication.
5. OHLC bars only: fills are modeled reference prices, not bid/ask/depth-confirmed executable fills. No forward-filling missing option bars.
6. Exclude 2026 data from candidate selection; keep holdout untouched.
7. Reuse frozen Phase 64 entry/exit rules and date-aware cost code; no parameter tuning to match the paper.

## Work packages
- WP1: verify paper's exact rules, stated assumptions, metrics, sample-count inconsistency, and data period.
- WP2: audit available underlying/option file date coverage and contract/expiry mappings.
- WP3: reproduce the frozen rule causally on OHLC bars: signal after daily close; breakout on later spot minute; select only a strictly ITM option observed at trigger; entry only at exact next-minute observed bar; target 2x entry, stop 0.5x entry, time exit as specified by the frozen translation.
- WP4: report trigger-to-entry coverage and exclusion reasons before interpreting returns.
- WP5: calculate trade metrics only if completed trades exist; otherwise mark all performance metrics NOT ESTIMABLE.
- WP6: sensitivity analysis for one adverse tick, ₹10/order and ₹20/order, +50% fees/charges, and separate 10% adverse price-slippage scenario, preserving distinct assumptions.
- WP7: if sufficient trades exist, compare OHLC-derived outputs with paper claims and disclose non-comparable periods/assumptions. If zero/insufficient trades, conclude replication blocked by coverage and do not fabricate comparisons.
- WP8: publish aggregate-only outputs, update phase status/log/error log and main README; no raw market data in GitHub artifacts.

## Statistical plan
Only compute win rate, net P&L, expectancy, profit factor, drawdown, holding time and confidence intervals for actual completed trades. Report sample sizes and missingness. Do not treat zero-trade output as zero returns. Do not claim statistical significance without a valid trade sample and preregistered inference. Any multiple-candidate comparison must be acknowledged.

## Acceptance gates
- Reproducible run and unit tests pass.
- All exclusions and coverage denominators are reported.
- No look-ahead, no imputed fills, no use of 2026 holdout.
- Cost assumptions and data limitations are visible.
- A strategy cannot be promoted solely from this phase; require adequate validation coverage, sufficient trades, positive net performance under registered cost stresses, and separate review.

## Stop rule
Stop after the frozen candidate set and its registered coverage/cost checks have been evaluated. Do not expand into an endless parameter search. If OHLC coverage is inadequate, conclude that reproduction is blocked on the available data and identify the exact data requirement.

## Current phase status
Plan established. Phase 64's first implementation produced zero completed trades; Phase 65's follow-up audit found trigger/contract/entry coverage blockers. Phase 66 proceeds with OHLC as requested but must not relabel modeled fills as executable quotes.
