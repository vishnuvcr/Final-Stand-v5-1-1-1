# Phase 74 Error / Blocker Log
Date: 2026-10-10

## B74-001 — Exact expiry remains unresolved
- Status: OPEN.
- Codes 1 and 2 are next/far expiry; code 0 returned HTTP 400 in Phase 73.
- Even a stitched absolute-strike series does not prove the intended contract expiry date.
- Resolve only with independent historical expiry mapping; do not infer it from counts.

## B74-002 — API rate/response/field failures
- Status: MONITORING.
- The bounded audit records aggregate request errors and field-array mismatches.
- Do not retry indefinitely or store raw provider error bodies. One bounded run is sufficient to decide feasibility.
