# Stop-Loss Research Conclusion

## Research question

Can an expiry-day stop-loss reduce the dynamic-n strategy's large expiry losses without cutting any trade that would otherwise finish profitable?

## Locked primary baseline

The corrected dynamic-n primary has:
- 190 trades;
- ₹138,937.12 net P&L;
- 94.21% net win rate;
- 178 target exits;
- 12 expiry exits;
- 11 losing trades, all expiry exits.

## What the research tested

Phase 17 tested 108 pre-registered stop rules covering hard MTM stops, expiry-day negative-P&L cutoffs, stagnation exits, MFE trailing rules, and combinations.

Only six Phase-17 rules left every baseline-positive trade untouched in both development and validation; none improved validation net P&L.

Phase 18 therefore tested a narrower hypothesis: on expiry day, stop only when the three-leg MTM is negative and the running maximum favorable excursion remains below a fixed fraction of the original target.

Phase 19 then tested the same candidate family with a walk-forward split:
- training/selection: through 2023-12-31;
- validation: 2024-01-01 through 2025-12-31;
- holdout: 2026-01-01 through 2026-09-30.

## Candidate stop criterion

**Research candidate:**

At **13:30 IST on expiry day**, evaluate the combined three-leg strategy MTM.

Exit all three legs when both are true:
1. the combined MTM is below ₹0; and
2. the running MFE since entry is below **0.50 × the original target amount**.

Use the first minute whose close satisfies both conditions. Continue to use the same one-tick adverse slippage per leg, six-order brokerage and the date-aware fee model already used in the primary backtest.

A trade that has already reached target has already exited under the baseline rules; therefore the MFE condition is an additional filter on still-open trades.

## Historical result of the 0.50× candidate

Across the 190-trade sample, using the Phase 19 train/validation/holdout partitions:

| Period | Net uplift | Positive trades affected | Max drawdown |
|---|---:|---:|---:|
| Training | +₹1,963.67 | 0 | ₹19,799.56 vs ₹21,763.23 |
| Validation | +₹1,923.59 | 0 | ₹27,336.11 vs ₹27,321.08 |
| Holdout (2026 YTD) | +₹6,305.15 | 0 | ₹17,890.35 vs ₹17,890.35 |
| Full sample | +₹10,192.41 | 0 | see note below |

The candidate changes **5 of 190 exits**, all of them baseline losing trades. It does not eliminate a historical loss completely; it truncates the loss earlier.

The combined full-sample loss reduction is approximately **₹11,281.55**, while net P&L increases by approximately **₹10,192.41**. The difference is the higher exit costs/price differences created by closing earlier.

## Interpretation

This is the first stop rule tested in this extension that simultaneously:
- leaves every historically profitable baseline trade untouched;
- produces positive net-P&L uplift in the development, validation and 2026 holdout periods;
- does not increase maximum drawdown in the 2026 holdout;
- reduces the size of several large expiry losses.

The more aggressive 13:30 / 1.00× target-MFE rule produced a larger full-sample uplift (₹11,974.88) but increased 2026 holdout maximum drawdown from ₹17,890.35 to ₹22,756.00. It is therefore not the preferred research candidate.

## Important limitation

The 0.50× candidate was part of the Phase 18 pre-registered grid, but Phase 19's formal train-only selection chose the 1.00× variant. The 0.50× choice is therefore a **robustness-based candidate**, not a completely untouched final holdout selection. The 2026 result is encouraging but should not be treated as proof of future performance.

There is also no guarantee that a live broker will fill a stop at the one-minute close used in the backtest. Fast moves, bid/ask spread, partial fills and execution latency can increase realized losses.

## Operational interpretation

For paper trading / forward validation, use the 0.50× criterion as the stop-loss candidate while leaving the core dynamic-n entry and target logic unchanged.

Do not reinterpret the rule as a guarantee of avoiding losses. Its historical role is to reduce the size of selected expiry losses while preserving the historical profitable exits in this dataset.

## Future research

The next useful test is live or paper-trading validation with actual Paytm Money execution and observed bid/ask spreads, followed by a frozen out-of-sample period in which the stop threshold is not changed.

No stop rule should replace the locked no-stop dynamic-n result in the primary research ledger until that forward test is completed.


## Phase 20 final disposition

Phase 20 then tested entry-time payoff-boundary/green-area stops. The training-safe boundary candidate used a 400-point buffer with one-minute confirmation, but it produced negative validation and 2026 holdout uplift and materially worsened drawdown. The combined boundary-plus-expiry-stop rule also failed out of sample.

Therefore the final historical strategy retains the 13:30 IST expiry-day conditional stop and **does not use a payoff-boundary stop**.

See [FINAL_STRATEGY_RULES.md](FINAL_STRATEGY_RULES.md) and [Phase 20 supplement](manuscript/PHASE20_PAYOFF_BOUNDARY_SUPPLEMENT.md).
