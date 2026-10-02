# Final Stand v5 1-1-1-1

Research repository for systematic testing of the NIFTY weekly-options directional 3-leg ratio strategy.

## Current status

**Phase 9A — ALGO TEST RECONCILIATION AUDIT: REQUIRED BEFORE FINAL ROBUSTNESS INTERPRETATION**

The locked fixed-OTM15 research backtest is **not directly comparable** to the two newly uploaded AlgoTest reports. The corrected AlgoTest screenshots show the intended three-leg fixed OTM15/16/17 component strategies (separate call and put reports), with 09:35 entry and 15:14 expiry-day exit. The previously uploaded files were the wrong reports and are superseded. The corrected reports are structurally much closer to the research specification, but still differ from the locked research backtest in entry time, exit rule, conditional X_call-vs-X_put selection, and modeled execution-cost assumptions.

### Locked research strategy

At 10:00 IST, four trading sessions before expiry:
- X_call = OTM17 CE + OTM16 CE - OTM15 CE
- X_put = OTM17 PE + OTM16 PE - OTM15 PE
- X_call > X_put -> BEARISH call structure
- X_call < X_put -> BULLISH put structure
- equality -> no trade

Position:
- BULLISH: buy OTM15 PE, sell OTM16 PE, sell OTM17 PE
- BEARISH: buy OTM15 CE, sell OTM16 CE, sell OTM17 CE

Exit:
- target T = 0.90 * selected X * lot quantity;
- otherwise latest complete three-leg observation at or before 15:29 IST on expiry day;
- one adverse ₹0.05 tick per leg in the primary model;
- date-aware NIFTY lot size and six executed orders per trade;
- explicit modeled brokerage/statutory/transaction charges.

Specification: [STRATEGY_SPEC.md](STRATEGY_SPEC.md)
Research plan: [RESEARCH_PLAN.md](RESEARCH_PLAN.md)

## Fixed OTM15 primary backtest — current locked result

Validated executable sample: **2021-05-27 through 2026-09-30**.

- 195 completed trades; 8 expiries excluded/missing.
- Total net P&L: **-₹39,626.40**.
- Total gross P&L: **-₹24,976.75**.
- Modeled costs: **₹14,649.65**.
- Mean net P&L: **-₹203.21/trade**.
- Median net P&L: **-₹237.86/trade**.
- Net win rate: **25.13%**.
- Target exits: 49/195; expiry exits: 146/195.
- Direction: 191 BULLISH/put trades and 4 BEARISH/call trades.
- Bootstrap 95% CI for mean net P&L: **-₹481.66 to +₹135.74**.
- Profit factor: **0.609**.
- Maximum cumulative drawdown: **₹44,141.23**.

These are descriptive historical results under the locked primary assumptions; the confidence interval crosses zero, so the sample does not by itself establish a strictly negative population mean.

## AlgoTest reconciliation evidence

The corrected call report shows **218 trades and ₹43,267.25 overall profit** with 99.08% winning trades; the configuration shows 09:35 entry, 15:14 expiry-day exit, and three legs: buy OTM15 CE, sell OTM16 CE, sell OTM17 CE. fileciteturn547file0L2-L3

The corrected put report shows **218 trades and ₹138,258.25 overall profit** with 99.54% winning trades; its configuration shows 09:35 entry, 15:14 expiry-day exit, and three legs: buy OTM15 PE, sell OTM16 PE, sell OTM17 PE. fileciteturn547file1L2-L3

These are benchmark configurations to reproduce first, not evidence that the locked research strategy has those returns.

## Phase 9A reconciliation plan

1. Reproduce the corrected AlgoTest call configuration exactly.
2. Reproduce the corrected AlgoTest put configuration exactly.
3. Compare trade counts, dates, strikes, entry prices, exit prices and per-leg P&L against the exported/report rows.
4. Change one parameter at a time to the locked research definition: 09:35->10:00, fixed exit->target/expiry, four legs->three legs, static side->X selector, fixed 65->date-aware lots, 0 costs->modeled costs/slippage.
5. Only after this audit, execute/interpret Phase 9 robustness and final manuscript conclusions.

## Research history and artifacts

- Phase 6 fixed specification: [STRATEGY_SPEC.md](STRATEGY_SPEC.md)
- Phase 7 primary backtest artifacts: [results/fixed_otm15_v3/](results/fixed_otm15_v3/)
- Phase 8 statistical artifacts: [results/fixed_otm15_v3/phase8/](results/fixed_otm15_v3/phase8/)
- Phase 9 robustness implementation: [research/robustness_fixed_otm15.py](research/robustness_fixed_otm15.py)
- Research log: [RESEARCH_LOG.md](RESEARCH_LOG.md)
- Error log: [ERROR_LOG.md](ERROR_LOG.md)

## Superseded research

Earlier v2 results using OTM6-based Stage 1 and high-n selection are retained for audit only and are not evidence for the present fixed-OTM15 strategy. See repository history and [results/restarted_v2/](results/restarted_v2/).
