# Phase 109 semantic remediation plan

**Branch:** `phase-109-strategy-semantics-remediation`  
**Parent:** `phase-109-exhaustive-parameter-grid`  
**Opened:** 2026-10-12

## Purpose

Correct signal-engine validity before treating the 1,000+ strategy-family evaluation as evidence. This is an implementation-validation sub-phase, not a new parameter search.

## Research questions
1. Does every evaluated family map to its own explicitly implemented core rather than a similarly named proxy?
2. Are confirmation and regime gates implementable using verified point-in-time inputs?
3. After the corrected runner passes regression tests, what cost-adjusted daily-OHLC proxy candidates survive validation, multiple-testing control and an untouched holdout?
4. Which strategy families must remain blocked because input history, source rights, timestamps or execution evidence are inadequate?

## Findings that triggered this branch
- v1 used substring fallbacks in `core_method()`; this could map distinct architecture IDs such as `ATR_NORMALIZED_MOMENTUM` or `FUTURES_BASIS_MOMENTUM` to ordinary return momentum.
- v1 treated `CROSS_ASSET` confirmation as a move-sign check on the other Indian index. That is not a distinct, timestamp-aligned global/cross-asset series.
- `REALIZED_VOL_LOW_HIGH` calculated a state but admitted both states, with no preregistered target-state axis.
- EMA slope used a price-return threshold, while EMA crossover compared the current spread to zero rather than requiring a crossing event.

## Registered scope and acceptance gates
1. Use exact core-ID allowlisting. Unimplemented cores are blocked; no substring fallback, renamed proxy or imputed feature.
2. Current v2 daily-close allowlist: ROC momentum, EMA crossover, normalized EMA slope, return z-score fade, RSI rebound, Bollinger reversion, EMA-deviation fade and relative strength. Other cores stay blocked until their own rule/input/tests exist.
3. Retain only `NONE` / `OPTIONS_FLOW` confirmation and `NONE` / `TREND_RANGE` / `INDIA_VIX` regimes. Block cross-asset/basis/breadth confirmations and realised-vol low/high or event regimes until their definitions and source pipelines are preregistered and audited.
4. Add deterministic offline tests for core mapping, blocked confirmation/regime identifiers, EMA-slope and EMA-cross semantics, and engine-version separation.
5. Bump engine version and start a distinct v2 cursor at zero; do not mix v1 and v2 checkpoint ranges.
6. Preserve 24 cost cases: brokerage ₹10/₹15/₹20 per order × adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side × 1.0×/1.5× model fees. Keep the canonical dated cost model.
7. Run regression tests automatically and manually; evaluate bounded shards automatically and manually; persist result hashes, cursor, skipped/blocked reasons, status/error/research/chat logs, and README links.
8. Publish aggregate summaries only; keep raw authenticated market data and private cache out of public files.

## Methodology and statistics
Signals use data known by the signal close; selected option contracts are evaluated with next-session open and registered close/stop proxies. Exact-contract identity, expiry, positive volume, lot size and valid OHLC must pass. Daily OHLC is not bid/ask/depth or achieved-fill data. All costs and stress cases are mandatory. Selection is restricted to development/validation; reserve the 2026-04 onward holdout until a frozen shortlist exists. Apply session-cluster inference and Holm multiple-testing control before any confirmation claim.

## Explicit blocks
Opening-gap, VWAP/intraday-volume, ATR/true-range, futures basis, synthetic parity, IV/skew/Greek feature filters, global lead/lag, news/sentiment, corporate events, market breadth, sector rotation, and DII/FII families remain blocked until their own feature pipelines, source rights, point-in-time/publication lag and tests are satisfied. Model-derived Greeks are not observed exchange Greeks. User-specific Paytm Money charges and executable bid/ask, depth, latency and partial fills remain unverified.

## Bounded completion
This sub-phase stops after semantic tests and a bounded v2 shard create a verifiable checkpoint. It does not expand indefinitely. Completion means tests pass, v2 starts at cursor zero, rows reconcile to 24 costs per attempted eligible configuration, blocker reasons are visible and repository documentation is updated. It does not itself promote a strategy.
