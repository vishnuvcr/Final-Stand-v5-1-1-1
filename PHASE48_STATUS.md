# Phase 48 Status — Independent Multi-Expiry VIX Data Bridge

**CLOSED — NO PROMOTION / SUPPLEMENTARY INCONCLUSIVE EVIDENCE**

## Final evidence

- Corrected numerical run: 124 trade rows across three registered source-derived baselines.
- Validation working candidate: Covered Call 2.0 option-only proxy + LOW VIX.
- Validation: 30 trades, **+₹10,327 net**, **+₹6,786 at +50% fee/charge stress**, mean +₹344/trade, 53.3% win rate, PF 1.03, max DD ₹1.37 lakh.
- Active-vs-rest mean difference: **+₹5,325**; bootstrap 95% CI **−₹10,857 to +₹5,325**; one-sided permutation p **0.2718**; Holm-adjusted p **1.0**.
- Protected 2026 confirmation: 6 trades, **+₹2,754 net**, **+₹2,114 under charge stress**, 33.3% win rate, PF 1.05, max DD ₹13,053.
- Double Calendar Straddle and Monthly Wide-Range Hedge were negative in validation and were not frozen.
- **Holm statistical survivors: 0. Promotion: NO.**

## Self-audit corrections that materially affected evidence

1. Raw option timestamps were UTC-naive and required +05:30 normalization before applying 10:00 IST / 15:29 IST rules.
2. The independent option source has no NIFTY spot field; a point-in-time bridge to the canonical NIFTY index series was registered for ATM and Black-Scholes strike selection.
3. Historical NIFTY lot-size mapping was corrected using NSE's documented 2024–2026 transition schedule; the superseded late-2024 run is rejected.

## Interpretation

The LOW-VIX Covered Call 2.0 proxy is a **promising diagnostic**, not a validated trading strategy. The validation point estimate is positive and the 2026 confirmation remained positive, but the confidence interval crosses zero, the permutation test is not significant, Holm correction leaves no survivor, drawdown is very large relative to the mean trade, and the implementation is not the exact futures-based strategy described by the source.

Phase 48 therefore closes without changing the canonical Phase-20/42 strategy.

## Next research direction

A dedicated Phase 49 should only proceed as a separately preregistered study of the promising LOW-VIX Covered Call 2.0 mechanism, replacing the synthetic-future proxy with an exact historical NIFTY futures leg, adding the source's adjustment logic, and requiring an independent dataset with a longer development history before any promotion decision.