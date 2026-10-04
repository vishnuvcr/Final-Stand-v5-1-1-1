# Phase 30 Pre-Registration — Entry-Referenced Combined Short-Leg Delta Proportion Exit

## Research question
Can the target and stop of the corrected NIFTY weekly-options 3-leg strategy be determined entirely by the proportional change in the **combined deltas of the two short option legs**, measured from their delta at entry?

## Corrections to Phase 29
Phase 29 is rejected as methodologically nonresponsive to the intended definition because it:
1. used lookbacks from prior minutes;
2. used absolute delta differences rather than proportional change from entry;
3. used a MEAN of the two short-leg changes rather than adding the two short-leg delta values.

Phase 30 supersedes those calculations and does not reuse Phase 29 numerical evidence.

## Locked variable
For each trade, define the two short legs as S1=OTM-(n+1) and S2=OTM-(n+2).

At entry t0:
D0 = Delta_S1(t0) + Delta_S2(t0)

At minute t:
Dt = Delta_S1(t) + Delta_S2(t)

The entry-referenced proportional delta change is:
R(t) = (Dt - D0) / D0
     = Dt / D0 - 1

For put-side structures both deltas are normally negative; for call-side structures both are normally positive. Because the two legs have the same option type, the ratio above measures the proportional change in combined short-leg delta magnitude without averaging the legs. No absolute-delta difference is used.

Equivalent magnitude form:
R(t) = (|Delta_S1(t)| + |Delta_S2(t)|) /
       (|Delta_S1(t0)| + |Delta_S2(t0)|) - 1

The magnitude form is the operational representation used in the implementation to avoid sign-convention ambiguity.

## Exit rules
Target: exit when R(t) <= -threshold_target, meaning combined short-leg delta magnitude has fallen by the specified proportion from entry.

Stop: exit when R(t) >= +threshold_stop, meaning combined short-leg delta magnitude has risen by the specified proportion from entry.

No option-P&L target percentage, absolute-delta level, prior-minute lookback, portfolio-delta trigger, payoff-boundary trigger, or Phase-20 13:30 MFE stop is used inside the candidate.

Expiry fallback remains only as the final mandatory exit.

## Candidate grid
Target and stop thresholds:
5%, 10%, 15%, 20%, 25%, 30%, 40%, 50%, 60%.

Confirmation:
1 or 3 consecutive complete one-minute observations.

This gives 81 target/stop threshold pairs × 2 confirmations = 162 candidate rules.

The confirmation parameter does not change the entry reference: every observation remains compared with the original entry delta.

## Walk-forward selection
Training: through 2023-12-31.
Validation: 2024-01-01 through 2025-12-31.
Holdout: 2026-01-01 through 2026-09-30.

Select target/stop pair on training net uplift only, with candidate drawdown as secondary tie-break. The selected pair is frozen before validation and holdout.

## Promotion gate
A candidate must:
- improve validation net P&L versus the frozen Phase-20 canonical strategy;
- improve 2026 holdout net P&L versus Phase 20;
- not increase validation or holdout maximum drawdown by more than 5%;
- use no Phase-20 target or stop criterion.

The final decision is made against Phase 20, not the earlier no-stop diagnostic.

## Execution
The same corrected strike mapping, option-price handling, adverse one-tick-per-leg slippage, date-aware NIFTY lot size, six executed orders, Paytm Money brokerage assumption, statutory charges, and incomplete-observation rules remain locked.

## Data quality
Delta is reconstructed from observed option prices with European Black-Scholes implied volatility, r=q=0, using the same validated minute data and coverage procedure as the corrected research. No forward filling or interpolation is allowed.
