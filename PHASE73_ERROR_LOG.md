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


## B73-004 — expiryCode 0 rejected by API
- Status: OPEN / provider semantics unresolved.
- Evidence: all eight expiryCode=0 requests returned HTTP 400; response bodies were intentionally not persisted to avoid logging provider/account details.
- Impact: current/near-expiry code cannot be used in this bounded historical request as configured. Codes 1/2 returned rows, but their exact expiry date remains unverified.
- Next action: no repeated blind retries. Use official documentation/support or a source that exposes exact historical contract identifiers if exact expiry mapping is essential.

## B73-005 — Rolling absolute strike changes through time
- Status: CONFIRMED LIMITATION; blocks fixed-contract replay.
- Evidence: the returned `strike` arrays contained only 7 unique absolute strikes on 2026-07-28 and 5 on 2026-08-04 over each multi-session response; API documentation explicitly describes rolling ATM-relative strikes.
- Impact: OHLC values may splice different absolute option strikes through time. That is not a valid held-contract price series for calculating entry-to-exit P&L unless each position's contract is separately mapped.
- Resolution: reject this endpoint as a standalone source for frozen fixed-contract P&L replay. Only use for research that explicitly accommodates rolling-relative data, after licence checks.
