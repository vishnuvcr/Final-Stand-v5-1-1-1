# Phase 71 — DhanHQ low-cost historical options pilot
Date opened: 2026-10-10
Status: IMPLEMENTED; LIVE TEST BLOCKED until account/token and subscription are available. No subscription or purchase made.

## Question
Can DhanHQ's ₹499 + tax monthly Data API return valid minute-level expired NIFTY option rows for the two sessions blocking Phase 51, at lower cost than a static historical-data pack?

## Source evidence
- Official support says Data API costs ₹499 plus applicable taxes monthly and auto-renews every 30 days: https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/
- Official API documentation describes up to five years of minute-level rolling ATM-relative expired options, 30 days per call, OHLC, IV, volume, OI and spot: https://dhanhq.co/docs/v2/expired-options-data/
- Strike universe is not full-chain: near-expiry index options can be ATM ±10; other contracts ATM ±3. This cannot automatically support far-OTM or wide-wing strategies.
- No historical bid/ask/depth is documented in this endpoint.

## Frozen test
Target sessions: 2026-07-28 and 2026-08-04.
Probe: one-minute ATM-relative NIFTY index options; WEEK and MONTH expiry flags, expiryCode=1, CALL and PUT; session-local date rows are counted in Asia/Kolkata.
Only aggregate row counts/status are written. No raw market rows or credentials are committed.
Script: scripts/phase71_dhan_pilot.py
Workflow: .github/workflows/phase71-dhan-low-cost-api-pilot.yml

## Gates
1. No live requests unless DHAN_ACCESS_TOKEN secret exists and the Data API subscription is active.
2. Before subscribing, user/vendor terms must permit intended research and retained private cache. No assumption about retention after subscription expiry.
3. Validate target session rows, timestamps, strike offsets, OHLC/IV/OI/volume, expiry-code semantics and completeness.
4. If data are partial, only accept them for strategies whose required strike universe is fully covered; do not fill gaps synthetically.
5. Even a passing result does not provide quote-quality execution; backtests still need conservative spread/slippage and Paytm Money costs.
6. No strategy promotion based on this source probe alone.

## Current result
Implementation complete. No authenticated run is possible in this environment because no Dhan account token was supplied and no subscription was purchased. Workflow produces BLOCKED_NO_DHAN_ACCESS_TOKEN rather than fabricating success.
