# Phase 73 Error / Blocker Log
Date: 2026-10-10

## B73-001 — Target expiry mapping unresolved
- Status: OPEN.
- Cause: Phase 71 only queried expiryCode=1. Official DhanHQ Annexure defines code 0=current/near expiry, 1=next expiry, 2=far expiry: https://dhanhq.co/docs/v2/annexure/
- Impact: successful data responses cannot be assumed to match the exact expiry used by a frozen strategy.
- Resolution: bounded 0/1/2 comparison followed by independent mapping of target expiry dates and absolute strikes.

## B73-002 — Rolling ATM data are not fixed-contract historical data
- Status: KNOWN LIMITATION.
- Impact: a rolling ATM-relative strike can change absolute strike over time; row availability alone does not establish coverage of a particular absolute option leg.
- Resolution: verify actual strike series against every frozen trigger and strategy leg before replay; do not infer or interpolate unavailable legs.

## B73-003 — No executable historical quote/depth
- Status: KNOWN LIMITATION.
- Impact: OHLC cannot establish executable bid/ask fills.
- Resolution: if the source passes mapping, use clearly labeled modeled fills and Paytm Money fees plus conservative spread/slippage stress; keep execution-grade claims blocked.
