# Phase 51-4 — Available-data partial-window continuation report

**Decision: PARTIAL-WINDOW DIAGNOSTIC COMPLETE; NO STRATEGY PROMOTION.**

## Abstract
At the user's direction, the analysis proceeds using the validated data available through 2026-07-21 and excludes the unresolved 2026-07-28 and 2026-08-04 expiry blocks. The original full-window Phase-51 preregistration (2026-04-21 to 2026-08-04) is not rewritten. The evidence is therefore an exploratory partial-window diagnostic, not a completed full-window OOS test.

## Research question and methodology
Question: How do the already-frozen and eligible strategies perform in the available interval after registered order-cost and +50% friction stress scenarios?

Method: reuse the authoritative source-faithful replay and frozen trade ledgers from [Actions run 37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283). No strategy parameters, entry/exit rules, source rows, or costs were changed. No prices were synthesized or forward-filled. Costs shown below are the existing engine's registered scenario outputs, not a newly estimated fee schedule.

## Data provenance
- Options source: `rissin/nse-options-intraday / upstox_intraday/NIFTY/NIFTY_2026.parquet`.
- SHA-256: `bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73`.
- Size: 394,805,617 bytes.
- Evaluation interval: 2026-04-21 through 2026-07-21 inclusive.
- Validated spot series: 23,625 observations from 2026-04-21 09:15 through 2026-07-21 15:29 IST.
- 14 weekly expiries observed directly in the option source.
- Two later expiry blocks are omitted from this partial analysis: 2026-07-28 and 2026-08-04.

## Results

### Net P&L sensitivity (₹)

| Strategy | Trades | ₹10/order | +50% friction | ₹20/order | ₹20/order +50% |
|---|---:|---:|---:|---:|---:|
| TT-02 | 13 | -1,341.12 | -2,936.31 | -3,701.12 | -6,476.31 |
| TT-04 | 62 | +13,271.51 | +10,287.26 | +10,345.11 | +5,897.66 |
| TT-05 | 62 | +17,098.15 | +14,239.72 | +14,171.75 | +9,850.12 |

All three candidates had 100% recorded execution coverage and zero row-level data errors in the authoritative run. Coverage is conditional on the available dataset and its audited eligible-candidate definition; it does not repair the missing expiry blocks.

### Descriptive trade statistics

| Strategy | Mean net/trade | Median net/trade | Win rate | Max cumulative trade-P&L drawdown |
|---|---:|---:|---:|---:|
| TT-02 | -₹103.16 | -₹1,530.71 | 38.5% | ₹27,015.52 |
| TT-04 | +₹214.06 | +₹884.94 | 67.7% | ₹12,024.81 |
| TT-05 | +₹275.78 | +₹1,056.82 | 66.1% | ₹12,217.19 |

Drawdown is the peak-to-trough decline of cumulative trade-level net P&L in trade order. It is not capital-normalized or a mark-to-market portfolio drawdown.

## Statistical analysis and inference
No new confirmatory hypothesis test was run in this continuation. The short interval, small trade counts, and dependence between trades make unadjusted point estimates insufficient for strategy promotion. No statistical significance, Sharpe ratio, CAGR, margin-adjusted return, or capital-normalized return is inferred.

## Interpretation
- **TT-05** has the largest positive net P&L in this partial interval across the four registered cost/friction scenarios. Under the most adverse listed case, it remains positive at ₹9,850.12.
- **TT-04** is also positive across all four listed scenarios, but its most adverse listed net result is lower at ₹5,897.66.
- **TT-02** is negative across all four scenarios and is not supported by this partial-window evidence.
- TT-03 remains non-informative in this interval because its frozen entry schedule yielded zero eligible campaigns under the observed Tuesday expiry schedule. TT-06 and TT-07 remain excluded after prior feasibility/coverage failures.

These results describe only the observed interval and are not a forecast or evidence of guaranteed future profitability. The relative ranking TT-05 > TT-04 > TT-02 is descriptive and can change when the missing expiry blocks are included.

## Strengths
- Exact primary options object pinned by SHA-256 and byte size.
- Spot series cached and range-checked.
- Expiry universe derived from primary option records.
- Frozen strategy definitions and registered cost/friction cases preserved.
- Explicit no-promotion rule and full-window limitation retained.

## Limitations
- The interval ends 2026-07-21, not the original 2026-08-04 endpoint.
- Two expiry blocks remain unresolved.
- Historical bid/ask observations are unavailable from the selected source; execution stress is not a true observed spread replay.
- Trade-level drawdown is not a mark-to-market or capital-normalized risk metric.
- Small sample and market-regime specificity limit generalization.
- This analysis does not independently establish live execution feasibility, margin efficiency, or future profitability.

## Conclusion
Proceeding with the available data is reasonable for a clearly labelled partial-window diagnostic. TT-05 is the descriptive leader in this interval, followed by TT-04; TT-02 is negative. **No strategy is promoted and this report does not close full Phase 51.** The original full-window OOS claim remains unresolved until the two missing blocks are sourced and replayed, or until the research owner explicitly changes the scientific question to accept a shortened interval.

## Future direction
1. Preserve this partial-window report as descriptive evidence.
2. If a later authorized source supplies the two missing blocks, rerun the original full-window protocol unchanged.
3. If the missing blocks remain unavailable, close Phase 51 with an explicit DATA-LIMITED / NO-PROMOTION conclusion rather than claiming full-window validation.
4. Continue only with the finite preregistered research chain; do not optimize parameters from this partial window.
