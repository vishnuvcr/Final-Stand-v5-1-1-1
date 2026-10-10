# Phase 98 Preregistration — Frozen Before Numerical Outcomes

Registered on 2026-10-10, before the Phase 98 strategy replay.

## Primary hypotheses
- H1 (Arm A net efficacy): on the validation calendar (2024-01-01–2025-12-31), Arm A has positive mean daily net P&L after base modeled all-in costs and one adverse ₹0.05 tick per leg-side fill.
- H2 (filter uplift): Arm B's prior-only high-volatility exclusion improves paired daily net P&L over Arm A on the identical session calendar, after the same base costs.

The two tests form one Holm-corrected primary family. Positive raw P&L alone does not pass either hypothesis. The confidence interval and Holm-adjusted p-value govern.

## Frozen rule IDs
- ORB15_DEBIT_V1: opening range uses exactly 09:15–09:29 one-minute NIFTY bars; first completed close outside the range from 09:30–14:45 defines side.
- Entries at next minute's exact observed option opens.
- Nearest expiry on/after date; one-lot ATM long plus two-step OTM short on the directional side.
- First observed target/stop trigger leads to next minute open exit. Target earns half the remaining maximum spread profit; stop triggers at 50% of entry debit; otherwise fixed time exit at 15:15.
- ORB15_DEBIT_VIX75_V1: same rules but skip if prior-session India VIX is strictly above its prior-only rolling 252-close 75th percentile.

## Frozen cost scenarios
- Base: ₹10 brokerage per executed leg-order, date-aware applicable statutory levies/GST, one adverse ₹0.05 tick each leg-side fill.
- Severe: ₹20 per executed order, 1.5× statutory/transaction fee rates, two adverse ₹0.05 tick each leg-side fill.

## Fixed calendar
- DEV: 2021-05-27–2023-12-31.
- VAL: 2024-01-01–2025-12-31.
- Never load 2026 data or an option expiry after 2025-12-31. No HOLD rows.
- Fixed sample source revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5.

## Minimum evidence
At least 100 completed validation trades per arm for its hypothesis to be inferentially interpreted. Otherwise report descriptive/underpowered. At least 95% paired minute-close coverage along each recorded active path; missing exit-open means incomplete campaign, excluded with reason. Missing bars are never filled.

## Statistics
Use seed 980010, 10,000 moving-block bootstrap samples with block length 5 sessions for 95% confidence intervals; use 10,000 one-sided sign-flip resamples for H1 (daily net) and H2 (paired B−A daily net). Adjust the two primary p-values with Holm step-down. Report exact n, estimates, CI, raw p and adjusted p. If methods cannot be estimated under the data gates, state so and do not tune.

## Stopping rule
One run per frozen specification plus engineering correction runs, all logged. No parameter sweep, no strategy promotion, no access to Phase 83's protected 2026 holdout.
