# Phase 44 Pre-registration

## Frozen baseline

Phase 43 is the baseline. Its accepted corrected matrix and execution-cost model are reused without altering historical P&L definitions.

## Locked candidates

bear_call_credit, bear_put_debit, put_backspread, put_broken_wing, iron_butterfly, call_backspread.

## Locked timing

Primary entry day: fourth trading session before weekly expiry.
Tuned entry times: 09:30, 10:00, 10:30 and 11:00 IST.
Structural expiry fallback: latest complete observation <= 15:29 IST.

## Locked strike grids

See PHASE44_RESEARCH_PLAN.md. No arbitrary continuous optimization is permitted.

## Locked VIX threshold grid

Level low/high quantiles and change quantiles are finite and fixed before numerical execution. Current VIX never enters the threshold history used to classify the current expiry.

## Locked data/cost rules

Same as Phase 43:
- repository/cache first;
- cached India VIX;
- Hugging Face only for missing historical option data;
- historical lot size;
- ₹10/order brokerage;
- date-aware statutory charges;
- one adverse ₹0.05 tick per leg on entry and exit.

## Statistical discipline

- Development is the search set.
- Validation is the selection-confirmation set.
- 2026 is untouched until the final candidate and active-exit rules are frozen.
- Primary inference unit is expiry.
- 10,000 resamples.
- Multiple-testing adjustment reported with Holm correction.

## Holdout rule

No statistic, ranking, parameter, threshold, strike geometry, entry time or exit rule may be changed because of 2026 holdout results.

## Evidence rejection

Any look-ahead, wrong expiry, wrong lot size, missing-data substitution, cost omission, stale VIX threshold, silent workflow failure or unpersisted result invalidates the run.
