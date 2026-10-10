# Phase 73 Status
Date: 2026-10-10
Status: LIVE COMPARISON EXECUTED; NO-GO FOR FROZEN FIXED-CONTRACT REPLAY FROM THIS ENDPOINT.

## Why this phase exists
Phase 72 run [38041988143](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38041988143) confirmed clean basic data structure but found 10 off-session rows on 2026-08-04 and did not establish exact contract expiry. Phase 71 used expiryCode=1, which official documentation defines as next expiry—not a guarantee of the intended target contract.

## Checklist
- [x] Created a 24-probe comparison for expiryCode 0, 1 and 2.
- [x] Added workflow_dispatch and push triggers.
- [x] Verified all 24 response outcomes: 16 returned data; 8 expiryCode=0 probes returned HTTP 400.
- [x] Compared row/session/strike metadata across expiry codes.
- [x] Identified unresolved exact-expiry mapping and rolling-strike splice limitation; fixed-contract replay remains blocked.
- [ ] Reconcile status and error log after workflow result.

No P&L is computed in this phase. No strategy is promoted.


## Phase 73 result — run 38042070177
- 16/24 probes returned data; all eight expiryCode=0 requests returned HTTP 400.
- expiryCode 1 and 2 returned data on both dates; counts were mostly 750 rows (2026-07-28) and 770 rows (2026-08-04), with minor count variation in two probes.
- Returned `strike` arrays had only 7 distinct absolute strikes on 2026-07-28 (range ₹23,950–₹24,300) and 5 on 2026-08-04 (range ₹24,450–₹24,650), across each probe's full multi-session response.
- These are rolling ATM-relative series. The absolute strike changes over time; they are not continuous history for one fixed option contract. Exact expiry dates are not returned in the audited response fields.
- **Decision:** NO-GO for frozen position P&L replay from these rolling series unless fixed-contract continuity can be independently established. Do not infer profitability from these probes.
