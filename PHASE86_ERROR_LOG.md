# Phase 86 Error Log

Date: 2026-10-10

| ID | Severity | Issue / evidence | Resolution or status |
|---|---|---|---|
| E86-001 | GUARDRAIL | A configured secret cannot be inspected directly by the GitHub connector. | Validate only inside Actions; never print or retrieve the secret value. |
| E86-002 | GUARDRAIL | Dhan's documented historical candle API returns OHLC/volume and may return OI; this does not prove historical executable bid/ask or depth. | Keep execution-quality claims blocked until quote/depth evidence is independently established. |
| E86-003 | GUARDRAIL | User supplied the secret name `DHAN_ACCESS_TOKEN`; token alone may be expired or data-plan entitlement may be inactive. | Use profile endpoint and record only status/boolean outcomes; do not infer access before a successful run. |
| E86-004 | PENDING | The new workflow must execute in GitHub Actions before any connectivity claim is made. | Verify run status and update log from actual output; no claim of success before evidence. |

Do not log credentials, raw profile responses, client identifiers, raw market-data responses, or hidden chain-of-thought. Record only auditable actions, outcomes and errors.
