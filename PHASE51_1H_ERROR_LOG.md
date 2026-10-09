# Phase 51-1H Error Log

No execution error yet.

Scientific boundary:
- No P&L inspection.
- No source selection by strategy outcome.
- No OOS window shortening.
- No synthetic or forward-filled prices.
- StockMock/StockMojo are treated as external oracle/context sources, not raw evidence.
## 2026-10-09 — Error P51-1H-001: validator assumed frozen schema before recording current columns

Actions run 37876578965 failed in the validator because the current downloaded Parquet did not contain the expected datetime column. The validator attempted to parse the missing field before recording the schema, which prevented a clean scientific gate result. No strategy P&L was produced and no source was accepted.

Correction: the validator now records the full column list and missing required fields first, then fails closed without attempting timestamp parsing when the schema is incomplete.
