# Phase 71 — DhanHQ low-cost historical options pilot
Date opened: 2026-10-10
Status: BOUNDED CONNECTIVITY PROBE PASSED; DATA-INTEGRITY AUDIT PENDING.

## Question
Can DhanHQ's Data API return minute-level expired NIFTY option observations for the two sessions blocking Phase 51, at lower cost than a static historical-data pack?

## Source evidence
- Official support: Data API subscription price and billing terms: https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/
- Official endpoint documentation: https://dhanhq.co/docs/v2/expired-options-data/
- Endpoint exposes rolling ATM-relative expired options data (OHLC, IV, volume, OI and spot) and allows up to 30 days per call.
- Rolling ATM-relative data are not full-chain data; the endpoint does not document historical bid/ask/depth.
- Dhan's documentation specifies `toDate` as non-inclusive, minute interval as 1 and fields including open/high/low/close/iv/volume/strike/oi/spot.

## Frozen test and outcome
Target sessions: 2026-07-28 and 2026-08-04.
Probe: one-minute NIFTY index options, expiryFlag WEEK and MONTH, expiryCode=1, ATM strike, CALL and PUT.
Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38041733380
Decision: `PILOT_TARGET_ROWS_FOUND`.
- Every one of the eight configured probes returned 375 target-date timestamp rows for 2026-07-28 and 385 for 2026-08-04.
- The overall response included 750 and 770 timestamps respectively, so another 375/385 timestamp rows in each response require date/bounds clarification.
- This is evidence of endpoint connectivity and target-date observations, not proof of complete or valid candles, expiry mapping, full chain, or profitability.

## Phase gates
1. No authenticated requests unless the user provides an active token via GitHub Actions secret; never print or commit credentials.
2. Confirm vendor terms permit intended research, caching/storage and derived-result publication before retaining raw responses.
3. Validate target date, timestamp bounds, duplicates, field-array alignment, session completeness, data validity, strike offsets and expiry-code semantics.
4. Use only strategy-relevant strikes that are fully represented; never synthesize missing rows.
5. No historical bid/ask/depth means execution remains modeled. Include Paytm Money brokerage/statutory costs and adverse slippage/spread sensitivity in any later replay.
6. No strategy promotion from a data-source probe.

## Phase 72 handoff
Audit the eight probe combinations again and report aggregate quality metrics only. Keep raw responses transient in the runner because this repository is public and data-retention/publication rights are not yet established.
