# Phase 103.1 — Dhan Data API smoke test

**Status:** PROBE_ABORTED_AFTER_FIRST_INVALID_RELATIVE_STRIKE
**Target window (IST):** 2026-08-03 inclusive to 2026-08-10 exclusive (7 days)
**Dhan request dates:** fromDate=2026-08-03; toDate=2026-08-09 (empirically inclusive; target end remains exclusive)
**Panels:** ICICIBANK:CALL, RELIANCE:CALL, RELIANCE:PUT, SBIN:CALL
**Relative strikes:** ATM, ATM+1, ATM+2, ATM+3, ATM-1, ATM-2, ATM-3
**Probe limit:** 28
**Run:** 38127361683
**Exact contract identity:** BLOCKED_EXPIRY_EOD_CROSSCHECK (request expiry selectors do not supply a returned expiry date or immutable contract ID)

This is a multi-session data-feasibility audit, not a strategy P&L test. Panels were selected from the prior one-session alignment screen. The token and raw rows are not published.

| Symbol | Side | Offset | HTTP | Status | Error code | Safe message | Rows | Arrays consistent | Distinct actual strikes | Strike changes | First strike | Last strike | First UTC | Last UTC | IST-date row counts | Rows outside dates |
|---|---|---|---:|---|---|---|---:|---|---:|---:|---|---|---|---|---|---:|
| ICICIBANK | CALL | ATM | 400 | HTTP_400_BAD_REQUEST | DH-905 | expiryCode is required | 0 | False | 0 | 0 |  |  |  |   | {} | n/a |

## Relative-strike surface / fixed-contract continuity audit

| Symbol | Side | Offsets returned | Common timestamps | Union timestamps | Min distinct strikes/minute | Max distinct strikes/minute | Distinct actual strikes | Strikes seen every minute | Duplicate timestamp-strike keys | Surface gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

### Exact actual-strike coverage (diagnostic only)

This is the deduplicated union of timestamp/actual-strike observations across rolling offsets. It does not establish expiry identity or executable quotes.

| Symbol | Side | Actual strike | Observed minutes | Union coverage % | First UTC | Last UTC | IST-date counts |
|---|---|---:|---:|---:|---|---|---|

## Independent expiry identity cross-check

**Result:** BLOCKED_NO_FULL_SESSION_EXACT_STRIKE_PROFILES
**NSE trade dates downloaded:** 0/0
**Eligible full-session exact-strike profiles:** 0
**Unique exact OHLC matches:** 0
**Matches to expected expiryCode=1 selection:** 0
**Selector mismatches / ambiguous / unmatched:** 0 / 0 / 0
**Supporting volume/OI agreement counts:** 0 / 0
**Aggregate matched expiry counts:** {}
**Duplicate keys deduplicated / conflicting duplicate keys:** 0 / 0
**Raw row persistence:** False
Only aggregate counts and expiry dates are published; raw minute bars and NSE row-level data remain ephemeral.


## Underlying ID mapping

| Symbol | ID resolved | Status |
|---|---|---|
| HDFCBANK | yes | MATCHED |
| ICICIBANK | yes | MATCHED |
| RELIANCE | yes | MATCHED |
| SBIN | yes | MATCHED |
| INFY | yes | MATCHED |

## Limitations

- Rolling strikes can change actual strike over time.
- This endpoint documents OHLC, IV, volume, OI, strike and spot, not historical bid/ask/depth.
- Observed response schema does not return contract expiry date or immutable option contract ID; expiryFlag/expiryCode are request selectors, not an audited returned identity.
- One stock/side probe does not establish full-history completeness or independent test sufficiency.
- Empirical diagnostic showed Dhan included toDate in returned rows despite documentation describing it as non-inclusive; requests therefore pass target_end_exclusive minus one day and still audit every timestamp in the original half-open target window.
