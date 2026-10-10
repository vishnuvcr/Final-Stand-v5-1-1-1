# Phase 85 Error Log

Date: 2026-10-10

| ID | Severity | Issue | Resolution/status |
|---|---|---|---|
| E85-001 | GUARDRAIL | Official NSE historical EOD and historical order/trade products are described as subscription-based; public report pages are not proof that the required intraday quote/depth history is freely downloadable. | Do not label NSE historical execution data as free; use public reports only for what they explicitly expose. |
| E85-002 | GUARDRAIL | Public GitHub dataset documentation describes large bulk datasets and licensed-user access; public repository visibility does not prove bulk data is free or redistributable. | No bulk download, HF_TOKEN use, raw-data caching or redistribution until rights and exact sample access are confirmed. |
| E85-003 | GUARDRAIL | Daily contract OHLC/LTP and open interest cannot establish executable fills at historical decision times. | Require historical bid/ask, quantities/depth and a frozen fill/cost model for execution-quality claims. |

Any additional issue must include the observed evidence, impact and resolution. Do not log hidden chain-of-thought; record auditable actions and decisions only.
