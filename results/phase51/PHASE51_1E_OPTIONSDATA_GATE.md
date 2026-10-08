# Phase 51-1E — OptionsData.shop Authorized Raw-Data Gate

## Purpose
Validate an authorized locally supplied OptionsData.shop archive before it can enter the frozen Phase-51 OOS replay.

## Newly confirmed catalog coverage
The current public catalog advertises a NIFTY 1-minute full-chain pack covering **29-Jun-2026 through 25-Sep-2026**. This period contains both missing frozen OOS expiry dates: **2026-07-28 and 2026-08-04**.

The advertised schema includes:
- datetime
- stock_code
- exchange_code
- product_type
- expiry_date
- strike_price
- right
- open/high/low/close
- volume
- open_interest

The source explicitly does **not** provide historical bid/ask, so it cannot satisfy the historical bid/ask requirement by itself.

## Gate
An authorized archive must pass, before any strategy P&L:
1. Archive integrity and SHA-256 capture.
2. Exact presence of both 2026-07-28 and 2026-08-04 expiry blocks.
3. Required-column/schema validation.
4. Timestamp and expiry parsing validation.
5. Duplicate contract-minute-key validation.
6. Trading-session continuity and endpoint validation.
7. Common-expiry equivalence against the frozen RISSIN source.
8. Minimum 95% replay coverage for mandatory strategy entries/exits.
9. Zero unexplained data errors.

## Evidence rule
The archive is not accepted merely because the vendor advertises coverage. The actual downloaded bytes must be audited and compared with the frozen source on common expiries.

No strategy P&L, tuning, source selection by profitability, or inference is permitted before the gate passes.

## Current state
**WAITING FOR AUTHORIZED ARCHIVE BYTES.**

The free public sample covers 15–17 Sep 2026 and is useful for schema inspection only; it does not contain the missing frozen OOS dates.

## Decision priority
If the authorized archive passes the common-expiry equivalence gate, it becomes the preferred missing-block raw source. If it fails, retain the data block and move to the next authorized source rather than altering the OOS window.
