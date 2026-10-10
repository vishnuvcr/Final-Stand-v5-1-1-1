# Phase 73 — DhanHQ expiry-code and rolling-strike mapping
Date opened: 2026-10-10
Status: IMPLEMENTED; bounded authenticated comparison running via GitHub Actions.

## Question
Which expiryCode variants return coherent rolling ATM-relative data on the two Phase 51 target dates, and what does the API actually establish about the target contracts?

## Frozen probe
- Target dates: 2026-07-28 and 2026-08-04 only.
- NIFTY index options, one-minute bars, ATM strike selector.
- expiryFlag WEEK/MONTH × expiryCode 0/1/2 × CALL/PUT = 24 probes.
- Aggregate-only output: counts, session bounds, strike range/distinct count, array alignment, duplicate timestamps.
- Request pacing 0.25 seconds; no raw rows or credentials committed.

## Grounded provider semantics
DhanHQ Annexure defines expiryCode 0=current/near expiry, 1=next expiry, 2=far expiry: https://dhanhq.co/docs/v2/annexure/
The expired-options API returns rolling ATM-relative data and supports only a bounded relative strike universe, not full-chain absolute-strike history: https://dhanhq.co/docs/v2/expired-options-data/

## Gates
1. Use this comparison to diagnose endpoint behavior only; aggregate strike range cannot prove a specific strategy leg is available at each trigger timestamp.
2. Map historical expiry dates and absolute strikes independently using a permitted source.
3. Reject off-session bars from session research; do not interpolate missing data.
4. Confirm caching/retention rights before storing raw provider responses.
5. No backtest until strategy leg mapping is exact. Any later OHLC fills remain modeled; include Paytm Money charges and conservative spread/slippage stress. No promotion based on data availability alone.
