# Stop-Loss Extension — Research Supplement

## Abstract

The corrected dynamic-n NIFTY options strategy produced 190 historical trades with ₹138,937.12 net P&L, but 11 expiry losses created a disproportionate share of drawdown. A stop-loss extension was therefore evaluated under strict constraints: a profitable baseline trade must not be exited early, while transaction costs and one-tick adverse slippage must remain in the calculation.

A broad 108-rule grid found no stop that both preserved all profitable trades and improved validation net P&L. A targeted expiry-day/MFE family was then evaluated under walk-forward splits. The research candidate was a 13:30 IST expiry-day exit when the three-leg MTM is negative and running MFE is below 0.50 times the original target.

The candidate improved net P&L by ₹1,963.67 in training, ₹1,923.59 in 2024-2025 validation, and ₹6,305.15 in the 2026 holdout. Zero baseline-positive trades were affected in all three periods. Maximum drawdown was lower in training, essentially unchanged in validation, and unchanged in the 2026 holdout. The candidate changed five of the 190 exits, all of which were baseline losing trades, but did not convert any historical loss into a profit.

## Research question

Can a rule-based exit criterion reduce adverse expiry losses without changing the set of historically profitable baseline trades?

## Aim

To identify a simple, reproducible stop criterion for the corrected dynamic-n strategy that reduces the tail-loss burden while preserving baseline-positive trades.

## Objectives

1. Reconstruct the exact minute-level three-leg strategy MTM using the corrected dynamic-n engine.
2. Test predefined stop families with identical execution costs.
3. Enforce zero early exits of baseline-positive trades as the primary safety constraint.
4. Validate candidate rules temporally rather than selecting thresholds from the same sample used for final evaluation.
5. Identify a candidate suitable for paper-trading validation.

## Methodology

Entry and dynamic-n selection are unchanged from the locked primary strategy. The stop extension is evaluated only after entry.

The baseline target is 0.90 × selected X × lot. Execution uses one adverse option tick per leg, six option orders, ₹10/order brokerage and the date-aware statutory fee model already audited in the primary research.

The Phase 17 grid tested hard stops, expiry-day negative cutoffs, stagnation exits, MFE trailing exits and combinations.

Phase 18 added an expiry-day filter combining negative MTM with a running MFE threshold.

Phase 19 used:
- training: through 2023-12-31;
- validation: 2024-01-01 to 2025-12-31;
- holdout: 2026-01-01 to 2026-09-30.

## Primary candidate

At 13:30 IST on expiry day, exit the three-leg position when:
- current combined MTM < ₹0; and
- running MFE < 0.50 × the original target.

The condition is evaluated on minute closes. If the condition is not met, the baseline target/expiry logic remains in force.

## Results

| Period | Net uplift | Winner affected | Stops | Loss reduction | Max DD change |
|---|---:|---:|---:|---:|---:|
| Training | ₹1,963.67 | 0 | 1 | ₹1,963.67 | −₹1,963.67 |
| Validation | ₹1,923.59 | 0 | 2 | ₹1,938.63 | +₹15.03 |
| 2026 holdout | ₹6,305.15 | 0 | 2 | ₹7,379.25 | ₹0.00 |

The historical full-sample uplift is approximately ₹10,192.41.

## Statistical interpretation

This is a small-loss-tail intervention rather than a broad win-rate enhancer. The important empirical constraint is not merely the average P&L increase but the absence of early exits on baseline-positive trades.

Because only five trades are changed, the result is necessarily sensitive to a small number of expiry observations. That is both a strength—limited intervention—and a limitation—the statistical power to establish a stable future effect is low.

## Discussion

The main evidence against a simple fixed stop is that losing and profitable trades can both experience large temporary adverse excursions. Hard stops therefore cut many eventual winners.

The expiry/MFE condition is different. It waits until late in the life of the trade and requires both current loss and insufficient prior favorable movement. In the historical sample this selectively truncated five losing expiries without changing profitable baseline exits.

However, this is not equivalent to eliminating the losing trades. The stopped trades remained negative; the rule reduced their realized loss.

## Strengths

- Uses the same corrected engine as the primary strategy.
- Uses exact minute-level three-leg MTM paths.
- Includes slippage, brokerage and date-aware statutory charges.
- Separates development, validation and 2026 holdout periods.
- Applies a strict no-winner-interference criterion.
- Tests a broad grid before narrowing the hypothesis.

## Limitations

- Only 11 baseline losing trades exist in the 190-trade sample.
- The candidate choice is informed by the Phase 18/19 grid, so it is not an untouched discovery-free estimate.
- Minute-close execution may differ from live stop-market fills.
- Bid/ask microstructure and order-book effects are not fully observable in the historical close-based path.
- The stop reduces some losses but does not eliminate loss events.
- A future market regime may behave differently.

## Conclusion

The research does not support a claim that a stop-loss can guarantee avoidance of the dynamic-n strategy's losing trades.

It does support a specific historical candidate: a 13:30 IST expiry-day exit when the three-leg MTM is negative and running MFE is below 0.50 × target. It preserved every historically profitable baseline trade in the tested sample and improved net P&L in training, validation and the 2026 holdout.

The candidate should remain an extension to the primary no-stop strategy and be validated in paper trading before any live deployment.
