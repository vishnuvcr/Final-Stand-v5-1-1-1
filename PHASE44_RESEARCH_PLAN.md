# Phase 44 Research Plan — VIX Candidate Tuning

## Research question

Can the most interesting Phase-43 India-VIX-conditioned NIFTY weekly option structures be improved by disciplined tuning of strike geometry, VIX regime thresholds and entry time, while preserving strict chronological out-of-sample testing and realistic costs?

## Primary aim

Turn the Phase-43 promising-but-unstable VIX observations into a controlled candidate-tuning experiment, without using the untouched 2026 holdout for parameter selection.

## Secondary aims

1. Tune only the strongest Phase-43 defined-risk candidates rather than reopening the 22-family universe.
2. Tune VIX thresholds on prior observations only.
3. Tune strike geometry and entry time within small, economically meaningful grids.
4. Test robustness to +50% transaction-cost stress.
5. Add a second-stage active-exit screen only for candidates that survive the first validation gate.
6. Compare tuned VIX candidates against their own unconditional tuned structure on common expiries.
7. Preserve the Phase-20/42 canonical strategy as an untouched external benchmark.
8. Produce a fully reproducible manuscript and machine-readable candidate ledger.

## Phase-43 candidates carried forward

Primary tuning families:
- bear_call_credit
- bear_put_debit
- put_backspread
- put_broken_wing
- iron_butterfly
- call_backspread

These were selected from Phase-43 because they showed the strongest validation/holdout diagnostics or represented important structural comparators. Unbounded Phase-43 structures remain excluded.

## Development / validation / holdout discipline

- Development: expiry <= 2023-12-31 — parameter search only.
- Validation: 2024-01-01 through 2025-12-31 — confirmation of frozen candidates.
- Untouched holdout: 2026 — opened only after candidate rules are frozen.

No 2026 value may influence candidate selection, threshold selection, strike choice, entry time or exit rule.

## Tuning dimensions

### 1. Strike geometry

Economically meaningful widths only.

- Bear call credit: short call +1 step; long call +2/+3/+4/+5 steps.
- Bear put debit: long ATM put; short put -1/-2/-3/-4 steps.
- Put backspread: short ATM put; long 1x2 at -1/-2/-3 steps.
- Put broken-wing: long ITM put +1/+2/+3, short 2x ATM puts, long OTM put -1/-2/-3; equal-width butterflies excluded from the broken-wing family.
- Iron butterfly: symmetric wings 1/2/3/4/5 steps.
- Call backspread: short ATM call; long 1x2 at +1/+2/+3 steps.

### 2. Entry time

9:30, 10:00, 10:30 and 11:00 IST on the registered entry day (four trading sessions before expiry).

The 10:00 IST Phase-43 convention is retained as a reference.

### 3. VIX threshold families

Low/high level quantiles:
- low: 15%, 20%, 25%, 30%
- high: 70%, 75%, 80%, 85%

Directional-change quantiles:
- rising: 80%, 85%, 90%, 95%
- falling: 5%, 10%, 15%, 20%
- spike positive-change threshold: 80%, 85%, 90%, 95%

Thresholds use only VIX observations strictly before the entry date.

Supported tuned states:
- LOW
- NORMAL
- HIGH
- SPIKE
- FALLING
- RISING
- HIGH_RISING

### 4. Active exits — Stage 2 only

Only for first-stage candidates that pass validation screening:
- profit targets: 25%, 50%, 75%, 100% of entry-defined gross premium/credit target where meaningful;
- stops: 0.5x, 1.0x, 1.5x the initial defined-risk amount;
- expiry fallback at 15:29;
- one-minute path; first trigger wins;
- no same-minute look-ahead.

## First-stage selection rules

A tuned candidate must satisfy all of:
1. development net P&L >= 0;
2. validation net P&L > 0;
3. validation +50% cost-stress net P&L > 0;
4. >= 20 validation trades;
5. validation maximum drawdown <= 1.25x the corresponding unconditional tuned-structure drawdown;
6. positive validation uplift versus the same tuned structure without a VIX filter;
7. no single expiry contributes >40% of validation uplift;
8. no missing or reconstructed entry/exit observation;
9. no unbounded risk structure;
10. no holdout-based parameter selection.

The top candidates will be frozen before the 2026 holdout.

## Statistical analysis

Primary unit: expiry.

For each frozen candidate:
- paired common-expiry uplift versus its unconditional comparator;
- 10,000 sign-flip / bootstrap resamples;
- 95% confidence interval for mean uplift;
- Holm adjustment across the frozen candidate family;
- maximum drawdown, profit factor, win rate and tail loss;
- +50% and +100% cost stress;
- contribution concentration;
- sensitivity to nearby parameter values.

The tuning search itself is exploratory; validation is the principal protection against development overfit.

## Execution model

- Same option data hierarchy and cached India VIX as Phase 43.
- Historical NIFTY lot sizes.
- ₹10 Paytm Money F&O brokerage per order.
- Date-aware STT, exchange charges, SEBI fee, IPFT, stamp duty and GST.
- One adverse ₹0.05 option tick per leg at entry and exit.
- No forward filling or synthetic option prices.

## Stage plan

### Stage 0 — governance and cache audit
Read Phase-43 status, errors, logs, matrix, VIX cache and canonical benchmark.

### Stage 1 — tuned structural screen
Evaluate all registered strike/entry/VIX variants on development; freeze only validation-eligible candidates.

### Stage 2 — validation confirmation
Run the frozen shortlist on 2024–2025, cost stress and paired-expiry inference.

### Stage 3 — active-exit tuning
Only for Stage-2 survivors. Tune target/stop families using development, then confirm frozen exits on validation.

### Stage 4 — untouched 2026 holdout
Run only frozen final candidates. No parameter changes after seeing holdout.

### Stage 5 — manuscript and closeout
Produce figures, full candidate ledger, results, inference, strengths/limitations, conclusion and future directions.

## Stop condition

Close Phase 44 after the registered tuning and active-exit stages are complete, or earlier only if the data cannot support a valid test. New strategy families, new VIX state definitions outside this pre-registration, or new holdout-driven tuning require Phase 45.
