# Phase 96 — VIX-Regime-Adaptive Selection Results

**Computation:** PASS. **Primary endpoint:** FAIL. **Decision:** NO PROMOTION.  
**Source:** frozen Phase 45 strategy-by-regime summary, Git blob SHA `4208da2e1189a68af697e11d03dd7d4ac937ddf7`.

## Frozen rule
For each of LOW, NORMAL and HIGH, select the defined-risk strategy with highest development `net50`, requiring at least 3 trades in both DEV and VAL. Evaluate only the selected candidate's validation `net50`. The initial 20-trade and amended 5-trade gates failed feasibility in HIGH; the minimum was reduced to 3 after a coverage-only audit. The HIGH result consequently has only 3 validation trades and is extremely low-power.

## Results

| Regime | Selected strategy | DEV trades | DEV net50 | VAL trades | VAL net50 | VAL max drawdown |
|---|---|---:|---:|---:|---:|---:|
| LOW | `strap` | 83 | +₹131,358.41 | 49 | **−₹187,009.45** | ₹295,870.22 |
| NORMAL | `strip` | 44 | +₹62,823.99 | 49 | **−₹113,665.57** | ₹164,903.92 |
| HIGH | `short_iron_condor` | 6 | +₹9,519.01 | 3 | **−₹2,760.10** | ₹1,838.51 |

Primary endpoint: sum of selected validation net50 cells = **−₹303,435.13**. All three selected state-specific candidates were negative in validation. The LOW and NORMAL selected strategies had particularly large validation drawdowns; HIGH is too sparse for a reliable inference.

## Interpretation
The registered regime-adaptive selection method fails. Strong development net50 did not transfer to matching validation regimes. The computation status PASS only means the code ran; the primary economic endpoint is negative.

This is a retrospective summary-table analysis, not a new strategy replay or independent blinded test. The three regime cells are not a deployable portfolio: trade overlap and capital allocation are unavailable. The source's 50%-friction scenario does not prove full Paytm Money brokerage/statutory charges, exact-contract spreads, adverse slippage, latency or executable fills are included. No capital-normalized return is inferred.

No HOLD rows were used, Phase 83's protected 2026 holdout was not accessed, no new market data was acquired, and no strategy was promoted.

## Reproducibility
- [Research plan](../../PHASE96_RESEARCH_PLAN.md)
- [Status](../../PHASE96_STATUS.md)
- [Error log](../../PHASE96_ERROR_LOG.md)
- [Selection script](../../research/phase96/run_regime_selection.py)
- [Selected rows](regime_selection_results.csv)
- [Machine report](validation_report.json)
- [Successful workflow run 38054856414](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38054856414)
