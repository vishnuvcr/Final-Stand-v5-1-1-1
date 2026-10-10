# Phase 97 Error Log

- E97-001: Never retain/use HOLD rows or Phase 83 protected 2026 data.
- E97-002: Selection uses development-only net50/max drawdown; validation is evaluation only.
- E97-003: Source 50%-friction scenario does not establish full Paytm Money all-in costs or executable fills.
- E97-004: State-cell sums are not deployable portfolio returns without overlap and capital allocation.
- E97-005: Retrospective, previously explored data; no promotion.

## E97-006 — Risk-adjusted selection failed (2026-10-10)
The successful run [38055041961](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38055041961) selected LOW call_backspread, NORMAL put_backspread, HIGH short_iron_butterfly. Validation net50 was −₹73,980.97, −₹82,413.19, and −₹1,808.79; aggregate −₹158,202.95. HIGH has only three validation trades. No strategy promoted.
