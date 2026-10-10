# Phase 71 Status
Date: 2026-10-10
Status: BOUNDED LIVE PROBE PASSED; SOURCE-DATA INTEGRITY VALIDATION REQUIRED.

## Evidence from run 38041733380
- [Workflow run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38041733380) completed successfully.
- GitHub Actions confirmed the Actions secret was present without exposing its value.
- Decision: `PILOT_TARGET_ROWS_FOUND`; API returned rows for both target dates in all eight configured probes (WEEK/MONTH × CALL/PUT).
- 2026-07-28: 375 target-date timestamps per probe, 750 total timestamps returned per probe.
- 2026-08-04: 385 target-date timestamps per probe, 770 total timestamps returned per probe.
- The 10-row excess on 2026-08-04 and the doubled total count are unresolved integrity anomalies. No data-completeness claim is made until timestamps, duplicate counts, market-session boundaries, field lengths and expiry-code semantics are audited.

## Completed
- [x] Rechecked official DhanHQ price: ₹499 + applicable tax per 30 days (subject to current account terms).
- [x] Rechecked official endpoint capability: rolling ATM-relative expired-options OHLC/IV/volume/OI/spot at minute intervals, up to 30 days per request.
- [x] Documented strike coverage limitation and lack of historical bid/ask/depth in this endpoint.
- [x] Created bounded probe for 2026-07-28 and 2026-08-04.
- [x] Added workflow with manual dispatch and verified push-triggered execution.
- [x] Confirmed the two target dates return timestamped rows through the authenticated endpoint.
- [ ] Resolve timestamp/count anomaly, field-array alignment and exact date bounds.
- [ ] Verify expiryFlag/expiryCode and rolling ATM strike semantics against official contract definitions.
- [ ] Confirm research, local cache and derived-publication rights before retaining raw rows.
- [ ] Validate candidate strategy strike requirements before replay.

## Next gate
Continue to Phase 72 source-data integrity audit. Aggregate counts are public; raw provider rows and credentials must not be committed to this public repository. No strategy P&L is computed or promoted based solely on this probe.
