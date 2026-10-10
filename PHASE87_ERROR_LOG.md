# Phase 87 Error Log

Date: 2026-10-10

| ID | Severity | Issue / evidence | Resolution or status |
|---|---|---|---|
| E87-001 | GUARDRAIL | Rolling expired-options data is ATM-relative and limited to a bounded strike range; it is not automatically a unique fixed-contract history. | Record strike/spot/timestamp fields and do not equate the rolling series with exact contract reconstruction. |
| E87-002 | GUARDRAIL | Historical OHLC/IV/OI/volume does not establish executable historical bid/ask or market depth. | Keep execution-quality profitability claims blocked without quote/depth evidence. |
| E87-003 | PENDING | The single historical options probe must be run before claiming access or coverage. | Inspect Actions output; log only status, field presence and counts. |
| E87-004 | GUARDRAIL | API data may be subject to Dhan's terms and entitlement; public docs alone do not grant raw-data redistribution rights. | No raw payload caching or publication until applicable terms are confirmed. |

Do not log credentials, raw option prices/payloads, personal account data, or hidden chain-of-thought. Log only auditable actions and outcomes.

| E87-003 | RESOLVED / PASS | Final Actions run 38047113250: endpoint HTTP 200; 150 five-minute rolling option candles; OHLC, IV, volume, strike, OI, spot and timestamp arrays present; requested array lengths aligned. | One-series data-shape gate passed. This is not proof of broad coverage or historical bid/ask/depth. |
| E87-005 | GUARDRAIL | The successful response is rolling ATM-relative data, not a guaranteed fixed listed contract history. | Require a separate date/expiry/strike coverage audit before strategy replay. |
