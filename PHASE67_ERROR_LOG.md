# Phase 67 Error and Limitation Log

## E67-001 — Phase 66 schema/mapping cause not fully determined
- Status: OPEN limitation.
- Impact: zero completed trades cannot be attributed solely to sparse source coverage versus contract-mapping mismatch.
- Evidence: Phase 67's bounded audit confirms exact-time coverage is limited, but it does not establish a reliable event-by-event ITM/side/expiry mapping.
- Mitigation: do not infer fills or relax the frozen rules. Any follow-on mapping audit must be a separate bounded phase.

## E67-002 — OHLC is not execution-grade quote data
- Status: OPEN limitation.
- Impact: OHLC bars do not establish bid/ask, depth, queue priority or market impact.
- Mitigation: require authorized quote/depth evidence before execution-quality claims; apply Paytm Money charges and slippage only in a valid later replay.

## E67-003 — Source period differs from paper period
- Status: OPEN limitation inherited from Phase 66.
- Impact: data does not reproduce the paper's 2008–2018 sample.
- Mitigation: conclusions remain limited to the available 2021–2025 sample.

## E67-004 — Workflow publication referenced a missing chat log
- Status: RESOLVED.
- Detection: workflow staged PHASE67_CHAT_LOG.md but the file was absent.
- Correction: added the file and regression tests.
- Verification: end-to-end run 38033174754 succeeded and published outputs.

## E67-005 — GitHub Actions Python setup failed before audit
- Status: RESOLVED.
- Evidence: [run 38032877348](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38032877348) failed at setup-python.
- Correction: removed pip caching while no tracked dependency manifest/cache-dependency path was configured.
- Verification: setup and all later workflow steps passed in run 38033174754.

## E67-006 — Derived-output publication failed after successful audit
- Status: RESOLVED.
- Evidence: [run 38033032907](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38033032907) passed computation and output validation but failed at publication; exact git error was unavailable.
- Correction: added pull/rebase before pushing derived outputs.
- Verification: [run 38033174754](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38033174754) completed successfully, including publication. Concurrent-update race was a plausible cause, not a confirmed diagnosis.

## E67-007 — Sparse exact-minute observations in Phase 67 audit
- Status: CLOSED as a bounded diagnostic finding; underlying source limitation remains.
- Evidence: published `summary.json` reports 30 trigger rows, 8 exact trigger-minute rows, 5 exact next-minute rows, and 8 rows with ±2-minute context.
- Impact: nearest/context bars cannot be used as fills; counts do not prove eligible ITM contract availability.
- Mitigation: stop this phase; no P&L, strategy promotion, or entry-rule relaxation.
