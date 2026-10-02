# Final Stand v5 1-1-1-1

Research repository for systematic testing of the **OTMn / OTM(n+1) / OTM(n+2)** NIFTY weekly-options strategy.

## Current status

**Phase 1 — Strategy definition and data validation: IN PROGRESS**

The strategy specification is now locked to the requested rules:
- Calculate X for **n=6..15** for both Calls and Puts: **20 candidates per entry**.
- Select the single highest X.
- Buy OTMn and sell OTM(n+1) and OTM(n+2), on the selected side.
- Profit target: **90% of X × lot quantity**.
- Otherwise exit at **0 DTE / expiry**.
- No stop-loss in the primary strategy.
- Report gross and net P&L, including slippage and transaction costs.

## Research files

- [Research Plan](RESEARCH_PLAN.md)
- [Strategy Specification](STRATEGY_SPEC.md)
- [Research Log](RESEARCH_LOG.md)
- [Error Log](ERROR_LOG.md)
- [Project Research Instructions](PROJECT_RESEARCH_INSTRUCTIONS.md)
- Phase 2 backtest code: `research/backtest_otm_ratio.py`
- Phase 2 results: `results/`

## Phase structure

1. Phase 1 — Strategy definition and data validation
2. Phase 2 — Primary backtest
3. Phase 3 — Statistical analysis
4. Phase 4 — Robustness and sensitivity
5. Phase 5 — Research manuscript

Each phase is maintained on a separate branch and has a manually runnable workflow where applicable.

## Reproducibility

Historical data sources, transformations, missing observations, assumptions, errors, and results are recorded in the repository. Hidden model chain-of-thought is not stored; only concise reproducible research decisions are archived.
