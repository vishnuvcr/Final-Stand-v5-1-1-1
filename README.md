# Final Stand v5 1-1-1-1

Research repository for systematic testing of the restarted NIFTY weekly-options 3-leg ratio strategy.

## Current status

**RESTARTED — Phase 1 strategy specification and implementation audit**

The prior Phase 2 global-selector experiment is superseded. This restart uses the latest strategy definition.

### Restarted algorithm

1. At exactly 10:00 IST, **4 trading sessions before expiry**, calculate:
   - X_call6 = CE8 + CE7 - CE6
   - X_put6 = PE8 + PE7 - PE6
2. If X_call6 > X_put6, select the **BEARISH call strategy**.
3. If X_call6 < X_put6, select the **BULLISH put strategy**.
4. On the selected side, calculate X(n) for n=6..15.
5. Primary high-n preference: retain n with X(n) >= 95% of the selected-side maximum X, then choose the highest n.
6. Trade the selected 3-leg ratio.
7. Exit at T = 0.9 * X_selected * lot quantity when gross P&L first reaches T; otherwise exit at expiry.

The 95% threshold is the transparent primary implementation of the requested preference for higher n while retaining significant X. Thresholds 90% and 97.5% will be tested in Phase 4.

## Research files

- [Research Plan](RESEARCH_PLAN.md)
- [Strategy Specification](STRATEGY_SPEC.md)
- [Research Log](RESEARCH_LOG.md)
- [Error Log](ERROR_LOG.md)
- [Project Research Instructions](PROJECT_RESEARCH_INSTRUCTIONS.md)
- [Data Acquisition](DATA_ACQUISITION.md)
- [Zenodo 2019–2020 Validation](ZENODO_2019_2020_VALIDATION.md)
- Restarted backtest implementation: `research/backtest_restarted_v2.py`
- Restarted workflow: `.github/workflows/phase-2-restarted-backtest.yml`
- Restarted results: `results/restarted_v2/`

## Data provenance

The primary public dataset documents 1-minute NIFTY index and option-chain OHLCV(+OI), with option files containing strike, option type and expiry fields; it warns that far/illiquid strikes can be sparse or absent.

The executable primary source begins 2021-05-27. The previously investigated Zenodo 2019–2020 source is not used for the weekly-contract backtest because its row-level option records did not provide a defensible expiry identifier.

## Research phases

1. Phase 1 — Restarted specification and audit **(current)**
2. Phase 2 — Restarted primary backtest
3. Phase 3 — Statistical analysis
4. Phase 4 — Robustness and sensitivity
5. Phase 5 — Final manuscript

Prior global-selector results are retained for audit history only and are not valid results for this restarted strategy.
