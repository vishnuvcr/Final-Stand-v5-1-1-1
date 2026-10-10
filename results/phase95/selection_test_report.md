# Phase 95 — Frozen-Universe Strategy Selection Test Results

**Primary outcome: FAIL — development winner did not retain positive stressed P&L in validation.**  
**Strategy promotion: NONE.**  
**Protected Phase 83 2026 holdout: not accessed.**

## Method followed
Using the frozen Phase 45 summary CSV, we filtered to `state=ALL`, `defined_risk=True`, both DEV and VAL rows present, and at least 50 completed development trades. We selected exactly one candidate by highest DEV `net50` (the source's recorded 50%-friction stress), with alphabetical tie-breaking. The primary endpoint is that selected candidate's VAL `net50`. HOLD rows were explicitly excluded from the computation.

## Primary result

| Measure | Result |
|---|---:|
| Frozen source strategy labels | 42 |
| Eligible defined-risk candidates after minimum-DEV-trade filter | 22 |
| Selected by development net50 | `call_backspread` |
| DEV trades | 133 |
| DEV net50 | +₹27,393.35 |
| VAL trades | 101 |
| VAL base net | −₹19,536.99 |
| VAL net50 (primary endpoint) | **−₹24,261.74** |
| VAL max drawdown (source metric) | ₹112,975.51 |
| Eligible candidates with positive VAL net50 | 3 / 22 |
| Eligible candidates with zero/negative VAL net50 | 19 / 22 |

**Primary hypothesis not supported.** The development-selected defined-risk strategy's stressed validation P&L is negative. The source reports a large drawdown relative to its point-estimate performance. Three positive validation cells among 22 candidates do not establish a robust strategy, especially given broad prior candidate exploration.

The three candidates with positive VAL net50 were `bear_call_spread` (+₹29,639.11), `bear_put_spread` (+₹13,416.09), and `put_broken_wing_butterfly` (+₹2,700.51). These are descriptive results only; they were not selected by the preregistered development rule and must not be promoted by selecting winners after looking at validation.

## Interpretation and limitations
- This is a **retrospective selection-stability test on a previously explored summary table**, not an independent blinded experiment and not a new market-data backtest.
- The 50% friction column is the source's stress scenario; it is not proof that every Paytm Money statutory levy, exact-contract spread, adverse slippage, latency and fill risk is fully captured.
- No capital denominator exists in the source summary; no return percentage is inferred.
- No confidence interval is calculated because the summary table does not provide a trade-level series here for valid resampling.
- Phase 83's protected 2026 holdout and all `holdout` rows were not used by this script.
- This does not reopen the closed Phase 50B strategy universe or justify new parameter tuning.

## Decision
**NO PROMOTION.** The frozen DEV-to-VAL selection rule failed its primary endpoint. The next useful empirical step requires a genuinely new preregistered hypothesis or materially better authorized exact-contract quote/depth/fill data. Any future strategy test must account for Paytm Money brokerage and statutory charges, spread, adverse slippage, latency, stressed costs, sufficient coverage, drawdown, and independent OOS evaluation.

## Reproducibility
- [Frozen input table](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-95-nested-strategy-selection-test/results/phase45_ready_made/strategy_vix_summary.csv)
- [Research plan](../../PHASE95_RESEARCH_PLAN.md)
- [Selection script](../../research/phase95/run_selection_test.py)
- [Machine validation report](validation_report.json)
- [Selected-candidate register](selection_results.csv)
