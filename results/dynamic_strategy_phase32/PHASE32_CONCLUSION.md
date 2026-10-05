# Phase 32 Conclusion

**Classification: PROMISING BUT INSUFFICIENTLY ROBUST**

Final primary evidence: 478 trades, ₹83,820.48 net P&L, 63.60% win rate, 1.112 profit factor, ₹94,492.83 maximum drawdown, and 15.75% maximum drawdown versus the ₹6 lakh reference capital.

The mean trade P&L is ₹175.36 and the two-sided t-test p-value is approximately 0.293. The 95% bootstrap confidence interval for mean trade P&L is approximately -₹156 to +₹494. Thus the sample does not establish a statistically credible positive expected trade value.

Calendar performance is unstable: 2021 -₹35,811.73; 2022 -₹22,294.75; 2023 +₹75,763.63; 2024 +₹33,501.40; 2025 +₹32,937.58; available 2026 -₹275.65.

The strategy is execution-sensitive. With the same completed trades, modeled one-tick slippage gives ₹83,820.48 net; 2 ticks ₹54,378.48; 3 ticks ₹24,936.48; 4 ticks -₹4,505.52; 5 ticks -₹33,947.52. A ₹20/order brokerage sensitivity reduces net P&L to about ₹61,258.88.

The source sample is incomplete: 264 expected expiries, 239 available, 25 missing, one incomplete; the last complete trade-producing expiry is 19-May-2026. The largest missing block is April-August 2025 and overlaps a major NIFTY expiry-calendar transition.

**Decision:** do not promote this strategy to live/forward validation. Do not replace the Phase-20 canonical strategy. No new Phase-32 parameter, direction rule, delta threshold, spread width or stop rule is promoted.

The exact tested rule set remains:
- Entry from 09:20 IST, not expiry day; start CALL.
- CALL: short nearest +0.25 delta CE, long +50.
- PUT: short nearest -0.25 delta PE, long -50.
- Exit at short-leg delta 0.50 or 0.04 boundary.
- No daily universal square-off or discretionary rollover.
- Positive net trade keeps direction; negative flips; zero keeps.
- Fresh entry blocked in final 120 seconds.

This is the tested rule set, not a live-trading recommendation.

Final workflow: 37388261915 (run #41).
Final code revision: f89e1e5574aa26b69288ae93b9cf180bf9882242.
Final artifact: 11380124540.
