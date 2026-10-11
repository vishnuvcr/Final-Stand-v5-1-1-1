# Phase 109 — Strategy-Family Discovery and Exhaustive Validation Plan

Branch: phase-109-exhaustive-parameter-grid. Parent: Phase 108. Registration only; no 1,000-family screen has run yet.

## Clarification of user's requirement
The requirement is **at least 1,000 distinct strategy families**, not merely 1,000 parameter configurations. Each family must be a meaningfully different, explicitly specified rule architecture or hypothesis, not a renamed parameter tuple. Parameter tuning happens only after a family is defined. Each family must also receive at least 1,000 unique configurations of its own and every declared variable combination must be enumerated. The 1,000,000 family-configuration pairs / 24,000,000 cost rows are minimum compliance thresholds, not caps. The implemented Cartesian compiler produced 1,025 registered architecture combinations, 325,124,800 applicable family-configuration tuples, and 7,802,995,200 cost-adjusted rows across 3,902 deterministic shards (registry build, not backtests; see the generated compiler report). The execution plan must therefore distinguish the full registered universe from data-feasible, attempted, completed, failed and not-run rows, use resumable checkpoints/manifest hashes and publish the exact remainder. Never imply all rows were tested unless audit counts prove it.

## Research questions
1. Which rule architectures across trend, mean-reversion, volatility, options flow, Greeks, cross-asset, market breadth, regime, event and risk-control families are testable using legally available historical data?
2. Which families survive costs, multiple-testing corrections, chronological validation and a single untouched OOS evaluation?
3. Which families are not testable because required historical inputs (e.g., Greeks, intraday quotes, global cross-asset timestamps) are unavailable or rights-restricted?

## Family registry and definition
Create a versioned strategy-family registry with stable family IDs, unique human-readable hypotheses, exact mathematical rule definitions, input fields, temporal availability, applicable instrument universe, trade direction, exit/position sizing, risk rules, data prerequisites, costs, and exclusion reasons. Require independent tests for duplicate/near-duplicate rules; a family cannot be counted toward 1,000 just because a threshold changes. Register at least 1,000 distinct hypotheses across categories such as:
- trend/momentum and breakouts;
- mean-reversion and reversal;
- realized-volatility/regime and range expansion;
- option chain OI/volume/put-call structure;
- Greeks/implied-volatility and skew/term structure where valid historical data exist;
- spot/futures/basis/synthetic-futures relationships;
- cross-index, global-market and cross-asset lead/lag;
- breadth, sector rotation and constituent dispersion;
- DII/FII flows and positioning;
- event/corporate-action/news/sentiment where point-in-time data exist;
- expiry/roll/microstructure and risk-budget/portfolio-construction overlays.
These are research categories, not evidence that all data are available. Each family gets an explicit feasibility gate. Families requiring unavailable inputs are marked blocked, not approximated silently.

## Minimum experiment count
- At least 1,000 unique strategy families, verified by registry IDs and distinct rule fingerprints.
- At least 1,000 unique valid parameter configurations per family, with full Cartesian enumeration for the frozen finite grid.
- All registered cost cases applied to every evaluated family/configuration tuple.
- At least 1,000,000 family-configuration pairs and ≥24,000,000 cost rows as minimum thresholds; the current registered full Cartesian grid contains 325,124,800 tuples and 7,802,995,200 cost rows. Exact counts must be reported by feasible, blocked, attempted, completed, failed and not-run status; do not count blocked or merely registered families as tested.
- If computation/data volume exceeds workflow limits, split into deterministic shards with persisted manifests and resumable checkpoints; total coverage is complete only when every shard hash/count reconciles.

## Parameter dimensions (family applicability declared up front)
- Signal lookback: 1, 2, 3, 4, 5, 7, 10 sessions.
- Return/move threshold: 0%, 0.25%, 0.5%, 0.75%, 1%, 1.5%, 2%.
- Volatility lookback: 3, 5, 7, 10, 15 sessions.
- Regime definition: rolling median; lower-/upper-third with middle no-trade; fixed quantiles only if preregistered.
- Strike target: ATM, 0.5% ITM, 0.5% OTM, 1% ITM, 1% OTM.
- Holding/exit: same-session close, 2-session close, 3-session close, expiry-aware close only if data permit.
- Risk: none, 10%/20%/30% premium stop, 10%/20%/30% target and preregistered combined pairs.
- OI confirmation: off, total near-ATM OI increase, same-side OI increase where valid.
- Cost cases: 3 brokerage levels × 4 adverse-slippage levels × 2 modeled fee multipliers.
Each family explicitly declares applicable dimensions; inapplicable dimensions are NA and are not falsely represented as tested. Any family with fewer than 1,000 valid distinct configurations must expand its grid before evaluation or be marked non-compliant.

## Data, splits and execution
- Approved public NSE daily UDiFF data are adequate only for daily OHLC proxy families. They do not supply all historical intraday bid/ask, option Greeks, India VIX, global timestamp-aligned feeds, historical news or DII/FII variables.
- Seek data for all registered categories from official NSE/BSE sources, documented open datasets, Hugging Face/Kaggle/GitHub and published research, subject to license and point-in-time validity. Keep data provenance, revision, hashes and rights status.
- Phase 106–108 month is development/debug only. Build chronological development, validation and untouched test splits from a longer dataset. If valid source history is unavailable, block affected family and do not fabricate/forward-fill unavailable inputs.
- Require exact contract identity, observed target prices, positive volume, valid OHLC and consistent lot size. OHLC remains proxy, not verified executable fills.

## Statistics and anti-overfit
Publish all families/configurations and failure reasons, not just winners. Outcomes: net P&L after brokerage/fees/slippage, return on premium, drawdown, expectancy, profit factor, trade count, coverage and regime stability. Use session-cluster bootstrap, family-wise/multiple-testing correction (Holm or a justified alternative), and disclose total search size. Do not select on final holdout. Test only once after family and parameter selection freeze.

## Acceptance gates
1. 1,000 distinct family registry entries and duplicate/near-duplicate audit.
2. At least 1,000 unique parameter tuples per family and complete Cartesian manifest.
3. All cost cases evaluated for each eligible tuple; shard counts and hashes reconcile.
4. Data and contract identity gates pass for any claimed empirical result.
5. Accounting reconciles gross less adverse execution adjustment and fees to net.
6. Publish registry, feasibility matrix, all-run manifest, aggregate results, logs, figures, README and final research manuscript.
7. No strategy promoted without independent OOS, multiple-testing control and credible execution evidence.

## Bounded phases
109.0 register requirement; 109.1 build 1,000-family registry and novelty/feasibility audit; 109.2 deterministic 1,000-configuration-per-family generator and shard manifest; 109.3 source acquisition/chronological splits; 109.4 execute all feasible family/configuration/cost rows; 109.5 statistical/accounting audit; 109.6 publish reports and stop. If resource or data gates prevent completion, report exact tested count and block promotion rather than claim exhaustive completion.


## 2026-10-12 — Registered-manifest scale update (counts are not results)

The first deterministic compiler run and self-test passed. It registered 1,025 unique fingerprints with zero exact fingerprint duplicates, minimum 78,400 and maximum 705,600 applicable configurations per family, 325,124,800 family-configuration tuples and 7,802,995,200 cost-adjusted rows across 3,902 shards of at most 2,000,000 cost rows each. Manifest hashes and the full shard ledger are published in [the Phase 109 compiler report](results/phase109/PHASE109_GRID_COMPILER_REPORT.md). This materially exceeds the minimum declared workload; the plan therefore requires execution to proceed by bounded, deterministic shards with an exact denominator and stop at phase 109.6, rather than attempting a giant single-job run. A compiled shard is only *registered*, not *evaluated*. If available runtime or usable historical data cannot support full execution, the final output must show completed and remaining counts explicitly and block strategy promotion; do not claim exhaustive evaluation based on manifest coverage.

The Dhan credential/schema probe succeeded (231 rows, HTTP 200 over a two-day probe) for rolling strike-relative options data. This does not demonstrate fixed-contract identity or adequate holdout history. Hugging Face initial discovery identified one India VIX daily-candle dataset; all candidates remain subject to source-card, license, schema, timestamp and point-in-time checks before use. See the source-access audit and error log for gaps/resolved workflow errors.
