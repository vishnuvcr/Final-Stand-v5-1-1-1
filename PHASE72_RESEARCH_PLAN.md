# Phase 72 — DhanHQ target-date data-integrity audit
Date opened: 2026-10-10
Status: IMPLEMENTED; authenticated audit awaiting workflow result.

## Research question
Do the DhanHQ rolling-option responses for the two previously missing sessions have internally consistent timestamps, regular-session coverage, field-array lengths, and price values—and can their expiry/strike semantics be safely used for a frozen historical replay?

## Frozen scope
- Dates: 2026-07-28 and 2026-08-04.
- Same NIFTY index, one-minute rolling ATM-relative options endpoint.
- WEEK/MONTH flags, expiryCode=1, CALL/PUT.
- Same endpoint and target-date bounds as Phase 71; no widening to new dates.
- Only aggregate diagnostics are persisted. No raw response rows or credentials are committed.

## Diagnostics
For each of the eight date/flag/side combinations, record:
- returned timestamp count; target-date count; unique and duplicate timestamp counts;
- first/last IST timestamp and count within 09:15–15:30 IST;
- out-of-session count and gaps between unique in-session timestamps exceeding one minute;
- required array lengths and mismatches versus timestamp count;
- valid OHLC price rows, invalid/non-positive rows, and basic OHLC consistency counts where fields are available.

## Official semantic clarification\nThe DhanHQ Annexure defines expiryCode 0=current/near expiry, 1=next expiry, 2=far expiry. Phase 71 used code 1 only, so its successful rows do not prove that the target strategy expiry was returned. See https://dhanhq.co/docs/v2/annexure/.\n\n## Gates
1. A workflow pass means the audit ran, not that the data are accepted.
2. A session is only coverage-eligible if timestamps and fields are aligned, session boundaries are understood, strike/expiry semantics are validated, and the needed strategy strikes are covered.
3. The response uses rolling ATM-relative strikes; never infer full-chain coverage.
4. No historical bid/ask/depth is provided by this endpoint. Any later backtest must label fills as modeled and include Paytm Money costs plus conservative slippage/spread sensitivity.
5. Do not write raw vendor data into the public repository unless the licence explicitly permits that retention/publication. Aggregate-only outputs are the default.
6. No strategy promotion from source diagnostics.

## Deliverables
- `scripts/phase72_dhan_integrity_audit.py`
- `.github/workflows/phase72-dhan-data-integrity-audit.yml`
- aggregate JSON/Markdown report, updated status and error log.
