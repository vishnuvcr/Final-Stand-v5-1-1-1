# Phase 75 Error / Blocker Log
Date: 2026-10-10

## B75-001 — Exact expiry identity not established
- Status: OPEN; source-path blocker.
- Phase 73 returned data for expiry codes 1/2 but did not establish exact historical expiry dates; code 0 requests returned HTTP 400.
- Phase 74 proved mechanical fixed-strike stitching feasibility, not expiry identity.
- DhanHQ's documented rolling response has no explicit expiry-date field per bar. Never infer expiry from row counts or the relative code alone.
- Evidence and decision: [PHASE75_FINDINGS.md](PHASE75_FINDINGS.md).

## B75-002 — Exact frozen-leg inventory remains to be bound
- Status: OPEN.
- The next authorized fixed-contract source must be joined to actual frozen strategy leg requirements, not assumed from an ATM-relative series.

## B75-003 — Official contract archive may not provide intraday pricing
- Status: OPEN.
- NSE historical contract-wise archives may establish expiry/strike/type and daily OHLC but may not provide the minute-level prices needed for the existing replay. If daily-only, use only for identity validation.

## B75-004 — Execution-quality data and rights
- Status: OPEN; downstream gate.
- OHLC does not establish executable bid/ask, depth, or fills. Confirm retention rights before caching raw rows; include Paytm Money charges and conservative slippage/spread assumptions in any eventual replay.
