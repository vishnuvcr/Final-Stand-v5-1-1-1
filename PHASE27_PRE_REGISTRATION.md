# Phase 27 Pre-registration — Delta-Based Exit Research

## Research question
Can portfolio delta, reconstructed from observed NIFTY option prices, improve the locked Phase-20 dynamic-n exit logic by (a) booking profits when the three-leg portfolio delta becomes sufficiently small and (b) stopping adverse trades when direction-aware adverse delta becomes sufficiently large?

## Locked control
The Phase-20 canonical strategy is the control: 190 corrected trades, target = 0.90×selected X×lot, 13:30 expiry-day negative-MTM/MFE<0.50×target stop, then 15:29 expiry fallback, with the audited slippage/cost model. The control is never altered in this phase.

## Delta methodology
For each complete minute common to NIFTY spot and all three selected option legs, infer strike-specific implied volatility from the observed option close using European Black-Scholes with r=0 and q=0 baseline. Compute Black-Scholes delta for each leg and aggregate with actual position signs:
portfolio_delta = delta(long OTM-n) - delta(short OTM-(n+1)) - delta(short OTM-(n+2)).
For call structures, positive portfolio delta is directionally adverse; for put structures, negative portfolio delta is adverse. Therefore:
- absolute_delta = |portfolio_delta|;
- adverse_delta = portfolio_delta for CE structures, -portfolio_delta for PE structures;
- favorable_delta = -adverse_delta.

No option price is interpolated or forward-filled. If an implied-volatility/delta calculation is numerically invalid, that minute is excluded from delta decisions and logged.

NSE describes NIFTY index options as European-style CE/PE contracts and documents Black-Scholes as the theoretical option-pricing framework. The empirical literature cautions that implied-Black-Scholes delta is model-dependent and can differ from minimum-variance deltas; therefore this phase treats delta as a decision feature, not as a claim of true instantaneous hedge ratio.

## Pre-registered families

### A. Delta-aware profit booking
For target fractions {0.50, 0.60, 0.70, 0.80, 0.90} and absolute-delta thresholds {0.05, 0.10, 0.15, 0.20, 0.25, 0.30}:
exit at the first minute where gross MTM >= target_fraction×original target AND |portfolio_delta| <= delta_threshold.
The existing target remains a hard ceiling: gross MTM >= original target always exits.

### B. Delta adverse stop
For adverse-delta thresholds {0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50} and confirmations {1,3} minutes:
before the locked expiry-day stop, exit when gross MTM < 0 AND adverse_delta >= threshold for the required consecutive exact minutes.

### C. Combined delta exit
Combine the training-selected profit-booking rule and adverse-stop rule, retaining the original target and Phase-20 expiry-day stop as precedence controls.

## Walk-forward protocol
- Training: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Holdout: 2026-01-01 through 2026-09-30.
- Candidate parameters are selected using training only.
- Holdout is not used for parameter selection.

## Promotion gates
A delta rule can be promoted only if:
1. validation and holdout net uplift are both positive versus the locked control;
2. validation and holdout maximum drawdown are not more than 5% worse than control;
3. no material degradation in profit factor;
4. all execution costs/slippage remain identical to control;
5. delta coverage is high enough to make the rule operationally reproducible, with coverage and invalid-IV counts reported;
6. the result is not dependent on one isolated threshold: neighboring parameter values must show comparable direction.

For adverse-stop-only candidates, the training screen additionally prefers zero profitable control trades stopped early.

## Statistical analysis
Report trade-level paired P&L differences, bootstrap 95% confidence intervals for mean uplift, win rate, profit factor, maximum drawdown, MFE capture, time-in-trade, exit-reason counts, and year-wise results. Sensitivity to the delta reconstruction model is required before any promotion.

## Literature/data basis
NSE contract specifications; Hull & White (2017) on practitioner Black-Scholes delta and minimum-variance delta; Alexander et al. on smile-adjusted delta; and later empirical work on model/regime dependence. These sources motivate the robustness checks rather than serving as evidence that a delta exit must work for NIFTY.
