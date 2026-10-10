# Phase 67 Research Plan — Contract/Minute Coverage Diagnostic

## Purpose
Diagnose why Phase 66's frozen CCI strategy produced breakout triggers but no completed trades. This is a data-quality and timestamp/contract-mapping phase, not a strategy optimization phase.

## Research questions
1. At each of the 18 recorded breakout triggers (CCI_BASE and CCI_EMA_FILTER audit rows), does the source option file contain bars at the trigger minute and the exact next minute?
2. Which columns identify timestamp, strike, call/put type, expiry/contract, and OHLC prices, and are strike/type values parseable and plausible?
3. Is the missing strictly-ITM candidate explained by absent timestamps, no eligible strike, schema/units mismatch, or mapping uncertainty?
4. Are there duplicate/conflicting bars, timestamp timezone issues, or gaps around trigger minutes?

## Frozen scope and safeguards
- Source: `thetrademarkk/india-index-options-1m`, revision `3eacf762d401efd9a08e804592fa7882b354c4a2`; reuse pinned revision and HF cache.
- Audit only the Phase 66 trigger events in DEV/VAL. Do not scan/use 2026 files or holdout.
- Never infer a fill from a nearest bar, forward-fill, interpolate, or change Phase 66 entry criteria.
- Any nearest-available-bar analysis is labelled diagnostic-only and cannot create trades or enter P&L.
- Do not commit raw option/index files. Publish aggregate counts, schema summaries, hashes, and event-level derived diagnostics only.
- Preserve source license/attribution; no claims of executable fills without quote/depth evidence.
- Costs (Paytm Money brokerage/fees, adverse tick, and slippage) remain mandatory if a later valid trade replay is possible.

## Phases / finite stopping rule
1. **Input integrity:** load Phase 66 audit + source manifest, validate unique event keys and pinned revision.
2. **Schema inspection:** report normalized column names, inferred role candidates, types, timestamp timezone/coverage.
3. **Event-window audit:** for each recorded trigger inspect only trigger minute and exact next minute, plus bounded ±2-minute diagnostic context; count exact bars and eligible strike/type candidates.
4. **Mapping audit:** report plausible strike/type/expiry mapping, duplicates and missing/invalid OHLC; do not silently repair values.
5. **Independent validation:** unit tests cover timezone conversion, exact-minute matching, strike/side filtering and duplicate detection.
6. **Decision:** classify the dominant blockers and state whether the source is adequate for a rule-faithful replay. Stop after this phase; no parameter tuning or new strategy sweep.

## Deliverables
- `results/phase67_contract_coverage/summary.json`
- `results/phase67_contract_coverage/event_diagnostics.csv`
- `results/phase67_contract_coverage/schema_audit.json`
- `results/phase67_contract_coverage/report.md`
- `PHASE67_STATUS.md`, research/error/chat logs, and README status/link update.

## Success criteria
A successful workflow means the audit is reproducible and outputs validated; it does **not** imply the data is sufficient or a strategy is profitable. A usable conclusion must distinguish source coverage failure from mapping ambiguity. If the schema cannot support a reliable mapping, conclude INSUFFICIENT and stop without relaxing rules.

## Status
Plan frozen at phase start. Change only if a substantive scope/method change is approved and logged.
