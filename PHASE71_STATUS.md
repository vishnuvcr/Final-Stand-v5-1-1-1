# Phase 71 Status
Date: 2026-10-10
Status: IMPLEMENTED; LIVE DATA TEST BLOCKED BY ACCESS REQUIREMENT.

- [x] Rechecked official DhanHQ price: ₹499 + applicable tax per 30 days.
- [x] Rechecked expired-options endpoint: up to five years, rolling ATM-relative, up to 30 days per request, minute data with OHLC/IV/volume/OI/spot.
- [x] Documented strike coverage limitation and the no-bid/ask limitation.
- [x] Created a bounded probe for 2026-07-28 and 2026-08-04.
- [x] Added manual GitHub Actions workflow and aggregate-only report output.
- [ ] Live probe: requires active Data API subscription and DHAN_ACCESS_TOKEN GitHub secret.
- [ ] Confirm vendor licence/retention terms before subscribing or caching responses.
- [ ] Inspect target rows and schema before expanding any data pull.

No subscription or purchase has been made. A blocked result is not a data failure; it means authenticated access was unavailable.
