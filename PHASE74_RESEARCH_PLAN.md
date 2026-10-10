# Phase 74 — Fixed-strike stitching feasibility
Date opened: 2026-10-10
Status: IMPLEMENTED; bounded offset audit running.

## Question
Can DhanHQ's rolling ATM-relative options endpoint be reconstructed into a timestamp-complete series for one fixed absolute strike by querying multiple offsets and selecting rows by the returned absolute `strike` field?

## Frozen scope
- Dates: 2026-07-28 and 2026-08-04 only.
- Expiry flags: WEEK and MONTH; expiry codes 1 and 2 only (code 0 returned HTTP 400 in Phase 73).
- Both CALL and PUT.
- Offsets ATM-10 through ATM+10, 21 requests per group, 16 groups / 336 bounded requests.
- Regular session defined as 09:15:00 through 15:29:59 IST, expected 375 one-minute timestamps.
- Only aggregate per-strike coverage counts are persisted; no raw prices or credentials are committed.

## Method
For each date/flag/code/side group, combine valid response rows in memory keyed by timestamp and absolute strike. Measure distinct absolute strikes, timestamp union, field-array alignment, and the best/full-coverage fixed strikes. Do not persist prices.

## Decision gates
1. A full 375-timestamp absolute-strike series would establish only mechanical stitch feasibility for that code/flag/side.
2. Exact expiry date and strategy-specific absolute strike still require independent mapping; codes 1/2 alone do not establish contract expiry.
3. Missing data must remain missing; no interpolation.
4. Do not use off-session rows.
5. No P&L until the fixed strike and expiry match each frozen strategy leg, data-use rights are confirmed, and modeled execution costs include Paytm Money charges and conservative slippage/spread stress.
