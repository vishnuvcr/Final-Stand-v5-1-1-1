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

## Plan amendment — 2026-10-12: time-series context completeness

The initial source audit discovered that official NSE index/VIX queries over the requested multi-year window returned only 218 unique dates per series, while 743 official options archive dates were present. The former schema gate incorrectly accepted any non-empty, valid series and allowed materially incomplete context into model input. This invalidates VIX-regime/cross-index conclusions from that cache and prevents its use for promotion.

Additional preregistered data gates now apply before corrected evaluation:

1. Each official India VIX, NIFTY 50 and NIFTY BANK query window must span at most 60 calendar days to avoid observed long-window response truncation.
2. Across the full required window, each series must contain at least 90% of weekdays as unique, valid observations. The check is a minimum data-density safeguard, not a claim that every weekday was a trading session.
3. Compare index dates with official options-archive dates. Archive/index mismatches and observed-index sessions without valid options archives must remain reported and must not exceed the source workflow's bounded coverage tolerances; individual option trades are still excluded if entry/exit archives are absent.
4. Save the refreshed private data cache before dispatching any evaluation. Public commits/artifacts remain aggregates only.
5. The current evaluator version is `phase109-eod-engine-v3-context-coverage`. Any v1/v2 cursor or result shard is diagnostic only and cannot be reused as v3 progress. The evaluator independently fails closed if any official context series is below the 90% threshold.
6. Acceptance requires automated regression coverage for both insufficient and sufficient context, a successful source workflow, and one verifiable v3 shard whose attempted configurations reconcile to 24 cost cases/configuration. No profitability claim follows from the data gate alone.

This is a research-plan change because source-context completeness has become an explicit acceptance criterion. The parameter grid, transaction-cost design and untouched holdout remain unchanged.

## Plan amendment — 2026-10-12: special-session completeness and engine v4

The rebuilt official NSE index series has 748 observations per series, covering 2023-10-03 through 2026-10-08. The options archive has 743 dates because the downloader previously only probed Monday–Friday. Calendar reconciliation identified five dates with NIFTY 50 observations but no options archive in the previous request list: 2023-11-12, 2024-01-20, 2024-05-18, 2025-02-01 and 2026-02-01. These include special weekend sessions and must not silently disappear from the experiment.

The source acquisition step now reads the committed observed-session calendar and unions NIFTY 50-observed dates outside weekdays into the archive probe dates. All supplemental probes will be written to the same dated coverage table with an explicit NO_ARCHIVE_OR_FETCH_ERROR status if the official archive cannot be retrieved. A missing archive that was explicitly attempted is not converted into valid option data; trades needing it remain excluded.

A fourth evaluator generation phase109-eod-engine-v4-session-coverage supersedes v3, resets the cursor and writes a distinct engine-tagged result filename. Before scoring, it requires the 90% official VIX/index context density check plus reconciliation evidence that:
- all remaining NIFTY 50-observed dates without a valid option archive were explicitly attempted;
- those attempted archive gaps are within the bounded gap tolerance of max(5, ceil(1% of observed NIFTY 50 sessions)); and
- no option archive date lacks an NIFTY 50 index-session row.

This does not assert the gaps are harmless; every trade entry or exit needing absent data is excluded, and final coverage/audit reports will show the gaps. Only v4 results generated after this audit may be considered for selection. Prior v1/v2/v3 output remains diagnostic. Cost scenarios and the reserved holdout remain unchanged.
