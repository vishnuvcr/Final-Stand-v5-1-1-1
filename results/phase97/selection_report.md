# Phase 97 — Risk-Adjusted Regime Selection Results

**Computation:** PASS. **Primary endpoint:** FAIL. **Decision:** NO PROMOTION.

## Frozen method
Select one defined-risk candidate per LOW/NORMAL/HIGH regime by maximizing development `net50 / max_dd`, requiring positive development net50 and max drawdown. LOW/NORMAL require at least 20 DEV/VAL trades; HIGH requires at least 3 due source coverage. Validation results are evaluation only.

## Results

| Regime | Selected strategy | DEV risk-adjusted score | DEV net50 | VAL trades | VAL net50 | VAL max drawdown |
|---|---|---:|---:|---:|---:|---:|
| LOW | `call_backspread` | 2.827173 | +₹91,461.70 | 49 | **−₹73,980.97** | ₹110,033.02 |
| NORMAL | `put_backspread` | 1.183000 | +₹49,132.85 | 50 | **−₹82,413.19** | ₹79,300.42 |
| HIGH | `short_iron_butterfly` | 6.253377 | +₹8,449.54 | 3 | **−₹1,808.79** | ₹1,134.14 |

Primary endpoint (sum of selected validation net50 cells): **−₹158,202.95**. All three regime selections were negative in validation. The HIGH result is based on only three trades and is descriptive only.

## Interpretation
Risk-adjusted development ranking did not transfer to validation. This is retrospective exploratory work on a previously explored summary dataset, not independent blinded confirmation or a new strategy replay. State cells are not a deployable portfolio without trade overlap/capital allocation. Source net50 does not establish complete Paytm Money brokerage/statutory charges, exact-contract spreads, adverse slippage, latency or executable fills.

No HOLD rows or Phase 83 protected 2026 holdout were used. No new market data was acquired. No strategy was promoted.

- [Plan](../../PHASE97_RESEARCH_PLAN.md)
- [Status](../../PHASE97_STATUS.md)
- [Error log](../../PHASE97_ERROR_LOG.md)
- [Script](../../research/phase97/run_risk_adjusted.py)
- [CSV](risk_adjusted_results.csv)
- [JSON](validation_report.json)
- [Successful workflow 38055041961](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38055041961)
