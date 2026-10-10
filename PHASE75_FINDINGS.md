# Phase 75 — Exact expiry and contract identity audit
Date: 2026-10-10

## Decision: BLOCKED — exact expiry identity not exposed by current rolling response

The frozen Phase 51-1 source-gate record identifies the two missing expiry dates as **2026-07-28** and **2026-08-04**. Phase 74 passed its bounded stitching feasibility test across 16 groups and demonstrated complete 375-bar histories for some absolute strikes in each group.

That result does not solve expiry identity. DhanHQ describes its expired-options endpoint as rolling ATM-relative data and its request uses relative `expiryFlag` / `expiryCode` selectors. The response fields documented for this endpoint include timestamps, OHLC, IV, volume, OI, spot and strike; there is no explicit per-bar expiry-date field in the documented rolling response. Therefore the exact expiry cannot be inferred from timestamp counts, absolute-strike coverage, or code 1/2 alone. [DhanHQ documentation](https://dhanhq.co/docs/v2/expired-options-data/)

## What is resolved
- Fixed-strike stitching is mechanically feasible for some strikes: [Phase 74 run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38042154732).
- No further Phase 74 repeat is warranted.
- Frozen missing-expiry dates are confirmed in [`PHASE51_1_SOURCE_GATE_REFERENCE.json`](results/phase51/PHASE51_1_SOURCE_GATE_REFERENCE.json).

## What remains blocked
- Exact expiry-date binding for each requested historical leg.
- Contract-level identity verified against official expiry/contract records.
- Data retention rights for any raw data saved or cached.
- Execution-grade pricing; OHLC is not bid/ask/depth.

## Next source path
Use the [NSE historical contract-wise archive](https://www.nseindia.com/all-reports-derivatives) or another authorized fixed-contract dataset that explicitly identifies expiry date, strike and option type. Validate the source’s minute-level coverage and retention rights before use. If the archive is daily-only for the needed dates, it can validate contract identity but cannot replace missing intraday prices.

## Research decision
Do not replay affected frozen strategy legs or report P&L for these dates until expiry, strike, side and timestamp are mapped unambiguously. Any later replay must include Paytm Money brokerage/statutory charges and conservative slippage/spread stress. No strategy is promoted by this phase.
