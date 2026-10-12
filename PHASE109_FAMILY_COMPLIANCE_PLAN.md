# Phase 109 — Family Compliance Audit and Full-Scope Recovery Plan

Branch: `phase-109-family-compliance-audit`  
Parent: `phase-109-exhaustive-parameter-grid`  
Status: **AUDIT OPEN — NO NEW STRATEGY RESULTS CLAIMED**  
Date opened: 2026-10-12

## Purpose
Restore the user's explicit requirement that the research evaluate at least 1,000 meaningfully distinct strategy families, with at least 1,000 valid configurations per family, rather than allowing the narrower eight-core remediation evaluator to become the de facto research scope.

## Research questions
1. Does the registry contain at least 1,000 distinct rule hypotheses, not merely combinations created by confirmation/regime labels?
2. Does each registered family have a unique, human-readable rule definition, stable ID, input list, point-in-time semantics and distinct fingerprint?
3. Which families are fully implementable with audited sources, which require additional source acquisition, and which are blocked by unavailable or non-point-in-time inputs?
4. Can all valid configurations and 24 cost cases per configuration be executed without mixing engine versions or branch checkpoints?
5. Which candidates survive development/validation, multiple-testing correction and the reserved holdout?

## Baseline facts from repository audits
- The compiled registry contains 1,025 architecture combinations and 1,025 distinct fingerprints, built from 41 core IDs × 5 confirmation structures × 5 regime gates.
- The full registered Cartesian universe contains 3,719,520 family/configuration tuples and 89,268,480 cost-adjusted rows across 45 shards. These are manifest counts, not backtests.
- The original source-feasibility audit classified 689 families as missing required inputs, 300 as having declared inputs present but execution/split gates pending, and 36 as having proxy/execution gates. This feasibility report used an older official index/VIX snapshot and must be refreshed before being used as a current gate.
- The semantic-remediation branch currently implements only eight core signal families and has 172,800 source-/implementation-feasible configurations. Its successful 2,000-configuration shard is not evidence that the full 1,025-family requirement has been completed.
- The remediation branch fixed semantic defects and official session coverage; those fixes must be ported or independently reconciled with the broad family registry before the full sweep can be trusted. Do not merge old v1 results with v4 results.

## Phases and acceptance criteria
### F109-A — Registry novelty audit
- Reconcile all registry rows, IDs, descriptions, core/confirmation/regime components and exact fingerprints.
- Audit structural near-neighbours and classify which are genuinely distinct hypotheses versus mere relabelings.
- Acceptance: at least 1,000 distinct rule hypotheses remain after the documented novelty audit; all excluded duplicates remain in the audit table with reasons.

### F109-B — Semantics and implementation coverage
- Build a family-by-family implementation matrix with explicit method IDs, signal equation, direction, lag/availability, options selection, exit/risk semantics, tests and code owner/module.
- Unsupported families must be BLOCKED, not mapped to a proxy by substring or name.
- Acceptance: each family has exactly one status: implemented-and-tested, blocked-input, blocked-source-rights, blocked-semantics, blocked-execution, or rejected-as-duplicate; no family silently disappears.

### F109-C — Data feasibility refresh
- Refresh official NSE index/VIX context and options-session reconciliation before recalculating feasibility.
- Re-audit NSE/BSE, Dhan, Hugging Face, Kaggle, GitHub and documented open sources as relevant. Keep source/license/coverage/publication-lag records.
- Explicitly cover option-chain OI/volume, model versus observed IV/Greeks, spot/futures/synthetic-forward/basis, global overnight lead/lag, India VIX/regimes, DII/FII/participant positioning, breadth/sector, corporate actions, news/sentiment and expiry/microstructure overlays.
- Acceptance: each input field has a source, date range, point-in-time lag, license/status and completeness gate; no forward-filling or synthetic replacement of unavailable history.

### F109-D — Full configuration manifest
- At least 1,000 valid unique parameter tuples per eligible family, with only applicable axes and deterministic full Cartesian enumeration.
- Every tuple receives all 24 cost scenarios: brokerage ₹10/₹15/₹20 per order × adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side × modeled fees 1.0×/1.5×.
- Acceptance: compiler totals, family counts, manifest hashes, shard coverage and status counts reconcile exactly.

### F109-E — Bounded empirical execution
- Use only the semantically audited engine version; use deterministic shards, resumable cursor and branch-specific checkpoints.
- Track registered, eligible, blocked, attempted, completed, failed and not-run counts separately.
- Keep development/validation for selection; do not score the 2026-04-01 onward holdout until a shortlist is frozen.
- Acceptance: every eligible tuple/cost case is reconciled, failures are logged, costs are dated, and execution is explicitly described as OHLC proxy where bid/ask/depth/fills are unavailable.

### F109-F — Statistical audit and publication
- Report net P&L, return on premium, expectancy, profit factor, drawdown, trades, coverage, cost sensitivity and regime stability.
- Apply session-cluster inference and family-wise/multiple-testing correction (Holm or preregistered alternative); disclose the entire search size and all exclusions.
- Publish aggregate tables, figures, appendices, manuscript, source/limitations, logs and README links.
- Stop at this phase. Promote no strategy without credible holdout and execution evidence.

## Branch isolation and no-mixing rules
- Parent v1 grid results remain historical diagnostics and must not be combined with remediation-v4 shards.
- Eight-core v4 results are a narrow implementation subset, not completion of the full registry.
- Any broader engine generation must have a unique version tag, output filenames, cursor and hashes. A source or semantics change resets the relevant cursor.
- The holdout remains untouched until shortlist and validation rules are frozen.

## Current decision
No strategy is promoted. This branch is an audit/coordination phase; it does not claim to implement all 1,025 families or produce new trading P&L. Next actions are to reconcile the registry novelty audit and implementation matrix, then implement and test families in bounded, explicit groups.
