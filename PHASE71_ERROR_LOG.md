# Phase 71 Error / Blocker Log
Date: 2026-10-10

## B71-001 — Authenticated API not run
- Status: OPEN / BLOCKED
- Cause: No DhanHQ access token was provided to this research environment; no Dhan subscription was purchased or assumed.
- Impact: Cannot truthfully confirm that the two missing sessions are available through Dhan's API.
- Safe handling: Workflow checks for DHAN_ACCESS_TOKEN and writes BLOCKED_NO_DHAN_ACCESS_TOKEN if absent. Credentials are never printed or committed.
- Resolution gate: User must have an active Dhan Data API subscription, add the access token as repository secret DHAN_ACCESS_TOKEN, and confirm the intended research/cache use is permitted.

## B71-002 — ATM-relative coverage is not full-chain
- Status: KNOWN LIMITATION
- Cause: Dhan endpoint uses rolling ATM-relative strikes; documented strike universe is limited.
- Impact: Cannot infer far-OTM/wide-wing coverage or claim full-chain historical data.
- Resolution: Validate candidate strategy strike needs against returned strike values; procure another source only if essential.

## B71-003 — No historical executable quote data in endpoint
- Status: KNOWN LIMITATION
- Cause: Endpoint documents OHLC/IV/OI/volume/spot, not historical bid/ask or depth.
- Impact: Execution-quality claims remain unsupported.
- Resolution: Use conservative slippage/spread sensitivity and keep execution-grade research explicitly blocked until quote data are available.
