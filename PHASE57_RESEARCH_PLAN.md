# Phase 57 research plan — cost-aware OHLC-range sensitivity replay

## Research question
When the frozen Phase 52 BASELINE configurations are replayed using the same exact entry/exit data and full cost model, how do modeled outcomes change across the 11 preregistered OHLC high-low/open thresholds?

## Purpose and boundary
Phase 54 established coverage sensitivity only and deliberately did not recalculate P&L. Phase 57 is a separate, explicitly authorized bounded exploratory replay that computes cost-aware modeled P&L across the same fixed threshold grid. It does not treat candle range as quoted spread, infer executable liquidity, or select a winning threshold.

## Frozen inputs
- Same 40 BASELINE configurations × 24 preselected development/validation events = 480 configuration-event rows.
- Pinned dataset `thetrademarkk/india-index-options-1m`, revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`, declared CC BY-NC 4.0.
- Exact selected contracts; exact entry bars and exact common 15:15 IST exits; no nearest-bar/strike fallback.
- Prior-minute OI minimum remains >= 100.
- Preregistered diagnostic thresholds: 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, and 1000 percent. The 1000% threshold is a diagnostic near-removal of the OHLC range gate, not a recommendation.
- Use the existing replay kernel and date-aware fee helper, with ₹20/order primary brokerage, ₹10/order sensitivity, applicable statutory charges, ₹0.05/leg-fill adverse slippage and 0/50/100% slippage stress.

## Method
1. Run the existing pinned Phase 52 loader and resolver; verify source revision and file hashes.
2. For each preregistered threshold, replay all 480 configuration-event pairs by changing only the OHLC range threshold. Preserve the OI gate, event set, configuration IDs, fill reference, exits, costs and splits.
3. Emit a row-level outcome ledger and six cost scenarios for each replay pass. Validate 480 outcomes per threshold and exactly six cost scenarios per pass.
4. Report descriptive results by threshold, family, split, brokerage and slippage stress. Record executed configuration-event count and unique event count separately because configurations on the same event are not independent trades.
5. Compare eligibility/replay counts with Phase 54. Investigate any disagreement without silently coercing it.
6. Run tests, upload artifacts and persist phase logs plus a main README checkpoint.

## Statistical analysis and interpretation
- Descriptive net P&L, mean/median per executed configuration-event, win rate and profit factor only.
- No p-values, confidence intervals, strategy ranking, winner selection or holdout access. The 40 configurations share event identities; rows are not independent observations.
- Do not treat the aggregate sum across configurations as a realizable portfolio return or compute portfolio drawdown/capital return from duplicated concurrent candidates.
- OHLC range is not bid/ask spread. Open-price fills plus fixed adverse slippage are modeled references, not tick/quote executable fills. These outputs cannot establish liquidity, live feasibility or commercial profitability.
- The data license is CC BY-NC 4.0; outputs are research-only.

## Acceptance criteria
- All 11 thresholds produce 480 rows with no replay exceptions.
- Threshold pass counts are non-decreasing; baseline 2% result reconciles to Phase 52.
- Each pass emits six cost scenarios; brokerage and slippage stress grid is complete.
- Source hashes match pinned provenance; holdout is untouched.
- No threshold/configuration is promoted from this descriptive sensitivity.
- Errors and all outputs are persisted; stop after this bounded grid.

## Status
Plan frozen before replay. Phase 57 is exploratory modeled-P&L sensitivity only; it is not the final strategy selection or execution validation.
 

## Plan amendment PA-57-001 — bounded endpoint replication (2026-10-10)

The full 11-threshold cost matrix has already been completed and accepted in Phase 56. Phase 57 is retained as an independent source-replay reproduction check, not a second full matrix. To avoid needlessly repeating the same 11-threshold workload, it now replays only two endpoints: 2% (frozen baseline) and 1000% (diagnostic near-removal). This checks the baseline result and upper-bound modeled P&L against the source-driven resolver and fee kernel. All 40 configurations, 24 events, strict OI gate, exact entry/exit rules, brokerage and slippage cases remain unchanged.

**Acceptance:** 960 configuration-event rows total (480 per endpoint), no replay exceptions, exactly six cost rows per replay pass, 2% baseline pass count=1, 1000% count reconciled against Phase 56, source hashes match pinned provenance, no holdout, no strategy ranking/promotion. Phase 56 remains the canonical 11-threshold result.
