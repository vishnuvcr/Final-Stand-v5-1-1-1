# Phase 75 Error / Blocker Log
Date: 2026-10-10

## B75-001 — Exact expiry identity not established
- Status: OPEN.
- Phase 73 returned data for expiry codes 1/2 but did not establish exact historical expiry dates; code 0 requests returned HTTP 400.
- Phase 74 proved mechanical fixed-strike stitching feasibility, not expiry identity.
- Resolution path: source-backed contract/expiry mapping against official exchange records and frozen strategy legs. Never infer expiry from row counts or the relative code alone.

## B75-002 — Canonical frozen leg inventory not yet audited
- Status: OPEN.
- The audit must enumerate actual legs from frozen strategy artifacts before mapping. No strategy legs are to be invented or assumed.

## B75-003 — Execution-quality data and rights
- Status: OPEN; downstream gate.
- OHLC does not establish executable bid/ask, depth, or fills. Confirm retention rights before caching raw rows; include Paytm Money charges and conservative slippage/spread assumptions in any eventual replay.
