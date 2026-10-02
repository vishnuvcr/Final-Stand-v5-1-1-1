# Final Stand v5 1-1-1-1

Research repository for systematic testing of the restarted NIFTY weekly-options 3-leg ratio strategy.

## Current status

**Phase 2 — RESTARTED PRIMARY BACKTEST: COMPLETE**

The research was restarted to exactly implement the latest two-stage strategy definition. Prior global-selector results are superseded.

### Restarted algorithm

1. At exactly 10:00 IST, 4 trading sessions before expiry:
   - X_call6 = OTM8 CE + OTM7 CE - OTM6 CE
   - X_put6 = OTM8 PE + OTM7 PE - OTM6 PE
2. X_call6 > X_put6 selects the user-defined **BEARISH** call structure.
3. X_call6 < X_put6 selects the user-defined **BULLISH** put structure.
4. On the selected side, calculate X(n) for n=6..15.
5. Primary high-n rule: retain n with X(n) >= 95% of selected-side maximum X, then choose the highest n.
6. Entry is the selected three-leg ratio.
7. Exit when gross P&L reaches T = 0.9 * X_selected * lot quantity; otherwise exit at expiry.

### Phase 2 primary result

Validated executable sample: **2021-05-27 through 2026-09-30**, using the public 1-minute dataset. The run produced **196 eligible trades**.

- Net win rate: **37.24%**
- Mean net P&L/trade: **-₹303.48**
- Median net P&L/trade: **-₹448.21**
- Total net P&L: **-₹59,481.78**
- Total gross P&L: **-₹42,880.50**
- Total modeled costs: **₹16,601.28**
- Target-exit rate: **37.24%**
- Mean selected n: **6.09**

Direction breakdown:
- BEARISH/call: 19 trades; mean net **-₹632.24/trade**
- BULLISH/put: 177 trades; mean net **-₹268.19/trade**

Selected n was predominantly 6: 188/196 trades used n=6; n=7 was used 6 times, n=8 once, and n=15 once.

These are backtest observations under the stated data, slippage and fee assumptions, not a forward-performance claim.

## Research files

- [Research Plan](RESEARCH_PLAN.md)
- [Strategy Specification](STRATEGY_SPEC.md)
- [Research Log](RESEARCH_LOG.md)
- [Error Log](ERROR_LOG.md)
- [Project Research Instructions](PROJECT_RESEARCH_INSTRUCTIONS.md)
- [Data Acquisition](DATA_ACQUISITION.md)
- [Zenodo 2019–2020 Validation](ZENODO_2019_2020_VALIDATION.md)
- Backtest: `research/backtest_restarted_v2.py`
- Workflow: `.github/workflows/phase-2-restarted-backtest.yml`
- Results: `results/restarted_v2/`

## Research phases

1. Phase 1 — Restarted specification/audit **complete**
2. Phase 2 — Restarted primary backtest **complete**
3. Phase 3 — Statistical analysis **next**
4. Phase 4 — Robustness and sensitivity
5. Phase 5 — Final manuscript

Prior global-selector results remain in repository history for audit purposes only and are not evidence for this restarted strategy.
