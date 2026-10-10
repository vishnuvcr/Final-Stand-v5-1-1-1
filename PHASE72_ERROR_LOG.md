# Phase 72 Error / Blocker Log
Date: 2026-10-10

## B72-001 — Phase 71 count anomaly
- Status: OPEN pending Phase 72 run.
- Evidence: 2026-07-28 returned 750 timestamps overall and 375 target-date timestamps; 2026-08-04 returned 770 overall and 385 target-date timestamps, consistently across WEEK/MONTH and CALL/PUT probes.
- Risk: possible out-of-session timestamps, timestamp duplication, API bound semantics, or endpoint behavior not represented by the aggregate-only pilot.
- Resolution: compute unique/duplicate timestamp counts, regular-session coverage, timestamp bounds, field-array alignment and OHLC validity from fresh bounded requests.

## B72-002 — expiry/strike semantics not independently confirmed
- Status: OPEN.
- Risk: returned bars may not map to the exact expiry/strike required by frozen strategies.
- Resolution: verify official API semantics and compare actual returned strike/expiry metadata where available; do not assume WEEK/MONTH flags or expiryCode=1 map to the intended contract without evidence.

## B72-003 — data retention and public publication rights
- Status: OPEN.
- Risk: authenticated access does not by itself establish rights to cache raw rows or publish derived datasets.
- Resolution: retain only aggregate diagnostics in this public repo until provider terms are verified.

## B72-004 — no historical bid/ask/depth
- Status: KNOWN LIMITATION.
- Impact: source bars cannot support observed executable fills. Later P&L must be modeled and stress tested with Paytm Money fees and conservative spread/slippage; label limitations explicitly.
