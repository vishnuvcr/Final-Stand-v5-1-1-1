# Final Stand v5 1-1-1-1

Research repository for systematic testing of the OTMn / OTM(n+1) / OTM(n+2) NIFTY weekly-options strategy.

## Current status

**Phase 2 — Primary backtest: EXECUTED (validated May-2021–Sep-2026 sample)**

Phase 1 locked the strategy:
- 20 X candidates per entry: n=6..15 × Call/Put.
- Select the single highest X.
- Buy OTMn; sell OTM(n+1) and OTM(n+2).
- Target = 90% of initial credit X × actual lot quantity.
- Otherwise exit at 0 DTE / expiry.
- No stop-loss in the primary strategy.
- Gross and net P&L are both recorded.

Phase 2 now implements the global 20-candidate selector and date-aware NIFTY lot sizes for the validated May-2021–Sep-2026 research sample.

## Research files
- [Research Plan](RESEARCH_PLAN.md)
- [Strategy Specification](STRATEGY_SPEC.md)
- [Research Log](RESEARCH_LOG.md)
- [Error Log](ERROR_LOG.md)
- [Project Research Instructions](PROJECT_RESEARCH_INSTRUCTIONS.md)
- [Data Acquisition](DATA_ACQUISITION.md)
- [Zenodo 2019–2020 Validation](ZENODO_2019_2020_VALIDATION.md)
- Backtest: `research/backtest_otm_ratio.py`
- Zenodo validation: `research/validate_zenodo_2019_2020.py`
- Results: `results/`

## Phase structure
1. Phase 1 — Strategy definition and data validation
2. Phase 2 — Primary backtest **(current)**
3. Phase 3 — Statistical analysis
4. Phase 4 — Robustness and sensitivity
5. Phase 5 — Research manuscript

## External data references
The primary executable dataset is `thetrademarkk/india-index-options-1m`, with validated option files beginning 2021-05-27. The 2019–2020 Zenodo source was investigated and rejected for the primary weekly-contract test because it lacks row-level expiry identifiers. It provides 1-minute NIFTY spot and option-chain OHLC data, but explicitly notes partial coverage for illiquid/far strikes. Official NSE documentation is used to validate contract/lot-size conventions and option-chain structure.
