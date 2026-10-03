# Phase 23 — Rich Entry-State Model and Opposite-Direction Test

## Motivation

Phase 22 tested simple entry filters and found no robust rule that removed losses without sacrificing profitable trades. Phase 23 therefore tests whether the missing information is the **joint market state at 10:00 IST**, and whether that state should (a) retain the canonical direction, (b) skip the trade, or (c) reverse the Stage-1 direction.

This phase does not assume that reversal is valid. Reversal is a competing hypothesis and must beat the unchanged canonical strategy out of sample.

## Research questions

1. Do volatility, VIX, cross-market, futures-basis, option-premium, option-open-interest/volume, skew and term-structure variables available by 10:00 IST explain the 11 historical losing trades better than the Phase-22 feature families?
2. Can a compact, pre-registered entry-state rule reduce losses while retaining most profitable trades?
3. When the canonical Stage-1 direction is wrong, can an opposite three-leg structure produce positive incremental P&L?
4. Is a three-way action policy — **canonical / reverse / skip** — more stable than skip-only filtering?
5. Does any apparent edge survive temporal validation, untouched holdout testing and realistic execution costs?

## Frozen control

The Phase-20 canonical strategy remains the control:
- 10:00 IST entry;
- Stage-1 direction from X_call vs X_put;
- dynamic n=6..15 with 95%-of-maximum higher-n preference;
- buy OTM-n, sell OTM-(n+1), sell OTM-(n+2);
- 90% target;
- 13:30 expiry-day MTM<0 and MFE<0.50×target conditional stop;
- 15:29 expiry fallback;
- identical slippage, brokerage, statutory charges and lot-size rules.

No Phase-23 result changes the control unless it passes the promotion gate.

## Data domains to include

All variables must be timestamped and demonstrably available no later than the 10:00 IST decision point.

### A. India volatility
- India VIX level;
- India VIX 1/3/5/10-session change;
- VIX percentile/rank using training history only;
- NIFTY realized volatility (5/10/20 sessions);
- intraday opening-range volatility where a timestamped pre-10:00 series exists.

### B. Cross-market state
Where synchronized historical data exists:
- S&P 500, Nasdaq-100 and Dow Jones prior-session returns;
- major Asian index returns available before 10:00 IST;
- USD/INR return/change;
- US Treasury yield proxy;
- Brent crude and gold returns;
- GIFT NIFTY / SGX NIFTY overnight return where historically available;
- cross-market risk-on/risk-off composite built only from the above pre-entry observations.

### C. NIFTY/futures microstructure
- NIFTY spot overnight gap;
- first 5/15/30/60-minute return and range, only when strictly before 10:00;
- NIFTY futures basis and basis change;
- futures volume/open-interest change when timestamped;
- India VIX/NIFTY divergence.

### D. Option surface and flow
For the entry expiry and, when available, adjacent expiries:
- call/put premiums across OTM6..OTM17;
- call/put implied-volatility proxies;
- IV skew across OTM wings;
- put-call premium ratios;
- option open interest by strike;
- change in open interest;
- option volume by strike;
- call/put volume and OI concentration;
- distance between spot and high-OI strikes;
- max-pain-like descriptive measures, without using post-entry information.

### E. Strategy geometry
- X_call, X_put, selected direction margin;
- X_selected;
- X_selected / long-leg premium;
- selected n and X_n curve shape;
- payoff boundary distance;
- expected move and boundary-distance z-score.

### F. Event/flow context
Only if reliable timestamped historical data exists:
- scheduled macro events before/after entry;
- RBI/NSE expiry/event flags;
- FII/DII net-flow data available before entry;
- major corporate-action/index-rebalance flags.

No text/news feature is allowed unless historical publication timestamp and reproducible point-in-time availability can be established.

## Data integrity rules

- No look-ahead.
- No forward-filled prices for entry features.
- Every feature must have a source timestamp <= 10:00 IST.
- Features unavailable for a trade are marked missing; they are not silently imputed from future data.
- Any imputation used by a model must be fit on training data only and documented.
- Cross-market timestamps are converted to a common timezone before the cutoff test.
- The existing 190-trade executable sample remains the primary strategy universe; adding a feature must not silently change the trade universe.

## Hypotheses

### H0 — canonical direction
The Phase-20 Stage-1 direction remains the appropriate direction conditional on the richer entry state.

### H1 — skip
Some identifiable entry states have sufficiently high conditional loss risk that skipping them improves net P&L after costs.

### H2 — reverse
Some identifiable entry states have sufficiently high probability that the Stage-1 direction is wrong that reversing the side improves net P&L after costs.

### H3 — three-way policy
A constrained canonical/reverse/skip policy improves out-of-sample net P&L and risk metrics without materially sacrificing the baseline winners.

## Model/search restrictions

Because only 11 control trades are losses, unrestricted ML is prohibited.

The primary model family is deliberately low-complexity:
1. univariate feature diagnostics;
2. signed/quantile state bins;
3. penalized logistic loss-risk model;
4. penalized logistic probability-of-reversal model where the opposite-direction outcome can be reconstructed without look-ahead;
5. a small decision-rule layer with thresholds frozen on training data.

At most **8 pre-specified feature groups** may enter the multivariable model:
- VIX/volatility;
- cross-market;
- overnight/opening state;
- futures basis;
- option premium geometry;
- option OI/volume;
- IV/skew;
- event/flow context.

No unrestricted tree/boosting/neural-network search.

## Reverse-direction construction

For every qualifying 10:00 entry, calculate the alternative side using the same dynamic-n engine and the same n-selection rule, but with the opposite Stage-1 direction.

The reverse trade must use:
- the same 10:00 entry timestamp;
- exact opposite-side option quotes;
- the same one-adverse-tick-per-leg model;
- the same 90% target definition for the reverse structure;
- the same expiry-day conditional stop;
- the same 15:29 fallback;
- the same six-order cost model.

If the reverse structure lacks complete OTM6..17 data, the reverse result is **not** fabricated or substituted.

## Temporal protocol

- Training/selection: 2021-05-27 through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Untouched holdout: 2026-01-01 through 2026-09-30.

All model fitting, feature scaling, missing-data handling and threshold selection occur inside training only.

## Promotion gate

A candidate policy may be promoted only if:

1. validation net-P&L uplift versus control > 0;
2. 2026 holdout net-P&L uplift versus control > 0;
3. validation and holdout retain >=90% of control-positive trades, unless the candidate is a reversal policy whose replacement trade is independently profitable;
4. validation and holdout maximum drawdown is not materially worse than control;
5. the policy does not depend on future data;
6. execution costs are identical to control;
7. the result is not driven by one trade or one calendar regime;
8. the selected rule was frozen before validation/holdout.

For a reversal policy, winner-retention is assessed on the **replacement portfolio** rather than mechanically treating every reversed control winner as a lost winner. Both control-trade and replacement-trade ledgers must be reported.

## Statistical analysis

Report:
- trade-level net P&L;
- bootstrap 95% CI for P&L difference;
- paired bootstrap for canonical vs reverse trade P&L;
- win rate;
- profit factor;
- maximum drawdown;
- worst trade;
- CVaR/expected shortfall at 5%;
- annual/yearly regime breakdown;
- reversal hit rate;
- conditional loss rate by state;
- calibration/Brier score for probabilistic models;
- permutation sensitivity for the final compact feature set.

Multiple-testing protection:
- the model family and feature groups are fixed before training;
- only training is used for model selection;
- validation and holdout are one-way tests;
- no threshold expansion after observing holdout results.

## Phase outputs

1. point-in-time feature availability audit;
2. feature dataset with provenance and timestamps;
3. canonical-vs-reverse trade ledger;
4. univariate state analysis;
5. compact model diagnostics;
6. three-way canonical/reverse/skip candidates;
7. train/validation/holdout comparison;
8. final Phase-23 conclusion;
9. manuscript supplement;
10. updated final strategy specification only if promotion criteria are satisfied.

## Stop condition

Phase 23 ends after the registered feature/model families are exhausted. It must not expand into unrestricted feature mining merely because no candidate passes.

If no candidate passes, the canonical Phase-20 strategy remains the research baseline and the final conclusion explicitly states that the tested entry-state information did not provide a validated directional switch.
