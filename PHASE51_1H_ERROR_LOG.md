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

## 2026-10-09 — Correction P51-1H-002: source schema differs but is canonically mappable

The current public files use timestamp/expiry/strike/option_type rather than datetime/expiry_date/strike_price/right. This is a schema-label difference, not by itself a scientific data failure. The validator was corrected to record the raw schema and apply a transparent column-name mapping only for validation. Raw bytes are unchanged and no values are synthesized.


## 2026-10-09 — P51-1H-004: Public dataset freshness change — RE-AUDIT REQUESTED

A current public Hugging Face index shows a visible newer commit `51ca58c` with the path `options/NIFTY/2026-08-04.parquet`. This does not establish that the target trading date is present: the prior accepted file had the expiry value but observations ended 2026-07-02. To avoid relying on stale byte evidence, the trigger marker was advanced and a new Actions byte audit requested for both 2026-07-28 and 2026-08-04. Until that run's raw timestamps, schema, hashes and duplicate-key counts are reviewed, the existing DATA-BLOCKED decision remains in force and no P&L is permitted.
