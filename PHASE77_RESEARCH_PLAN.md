# Phase 77 — Partial-OOS inference and exclusion audit
Date: 2026-10-10
Status: PLAN FROZEN

## Research question
How robust are the previously reported TT-04 and TT-05 partial-OOS outcomes when uncertainty is assessed at the expiry-cluster level and the two missing expiry dates are explicitly excluded?

## Scope
- Frozen existing Phase 51-3 outputs only; no rule changes and no new price acquisition.
- Primary window remains 2026-04-21 through 2026-07-21, comprising 14 observed expiry dates.
- 2026-07-28 and 2026-08-04 remain explicit unavailable exclusions; they are not imputed or represented as tested.
- TT-02 is retained as a negative control; TT-04 and TT-05 are descriptive candidates only.

## Method
1. Validate existing trade CSV schemas and reconcile trade counts, expiry coverage and net totals against Phase 51-3 summary values.
2. Calculate mean/median net P&L, win rate, maximum cumulative trade-P&L drawdown and all four registered cost/friction cases.
3. Quantify uncertainty by expiry-cluster bootstrap (10,000 resamples, fixed seed), resampling expiry clusters rather than individual trades. Report 95% percentile intervals for total net P&L and mean trade net under the base and highest-friction case.
4. Report the fraction of bootstrap total-net samples above zero; this is descriptive resampling evidence, not a calibrated posterior probability or confirmatory p-value.
5. Explicitly report that only 14 expiry clusters are observed and that the two later expiry dates are absent. No claim of full-window OOS validation is permitted.
6. Do not tune parameters, select a winner for deployment, or promote a strategy.

## Frozen decision gates
- Any schema/count/total mismatch: fail audit and log the discrepancy.
- Any absent expiry dates: maintain explicit exclusion; no synthesis.
- If a candidate is negative in base costs or highest-friction costs, flag robustness concern.
- Even if bootstrap intervals are positive, keep the result diagnostic because the sample is short and non-independent.

## Deliverables
- `scripts/phase77_partial_oos_inference.py`
- `results/phase77_partial_oos_inference/summary.json` and `report.md`
- `PHASE77_STATUS.md`, `PHASE77_ERROR_LOG.md`
- GitHub Actions workflow with automatic branch-path trigger and manual `workflow_dispatch`.
- README checkpoint updated after verified workflow output.

## Costs and execution
Use already-recorded frozen outputs with Paytm Money ₹10/order and ₹20/order scenarios and +50% friction stresses. No new cost assumptions are introduced. OHLC-based results are not a guarantee of executable fills.
