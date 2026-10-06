# Phase 43 Chat/Decision Log

## User request — 2026-10-06
User requested testing of all options strategies on an India-VIX basis.

## Research decision
A finite preregistered strategy universe was chosen rather than an unbounded search. The study keeps the Phase-20/42 canonical strategy untouched as control and tests broad NIFTY weekly structures under point-in-time VIX regimes.

## Scope registered
- Entry: 4 trading sessions before expiry, 10:00 IST.
- Primary structural exit: latest complete observation <=15:29 on expiry day.
- Strategies: straddles, strangles, debit/credit verticals, butterflies, iron butterfly/condor, broken-wing butterflies, ratio/backspreads and calendars/reverse calendars.
- VIX regimes: ALL, LOW, NORMAL, HIGH, SPIKE, FALLING, RISING, HIGH+RISING.
- Costs: one adverse 0.05 tick per leg, Paytm Money brokerage ₹10/order, date-aware statutory charges.
- Chronology: development, validation, untouched 2026 holdout.
- Inference: 10,000 expiry-level bootstrap and sign-flip tests, with multiple-comparison adjustment.
- Router: development-frozen VIX-conditioned strategy selection; top candidates frozen before holdout.

## Current state
Registration is complete. Numerical execution remains pending.
