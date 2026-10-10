# Phase 103 Status — Novel Intraday NIFTY Options Strategy Discovery

**State:** INITIALIZED — RULES PREREGISTERED; REPLAY NOT YET RUN  
**Branch:** `phase-103-novel-intraday-strategy-discovery`  
**Decision:** no strategy promoted; data/engineering checks pending.

## Registered candidates

1. S103-A — Cross-market-confirmed opening-range breakout debit spread (XAC-ORB).
2. S103-B — Failed-breakout reclaim reversal debit spread (FBR).
3. S103-C — Prior-range-compression / low-India-VIX iron condor (RC-VIX-IC).

Rules, data windows, costs, statistical tests and stopping criteria are frozen in [PHASE103_RESEARCH_PLAN.md](PHASE103_RESEARCH_PLAN.md). The test uses the pinned non-commercial 2021–2025 option dataset, trades only 2024–2025, and excludes 2026 options.

## Required gates

- [ ] Run syntax/unit tests.
- [ ] Verify data schema and source revision.
- [ ] Replay all three candidates without parameter tuning.
- [ ] Calculate date-effective charges, slippage and two cost stresses.
- [ ] Audit missing entries/exits and ledger reconciliation.
- [ ] Compute five-session block bootstrap and Holm correction on 2025 results.
- [ ] Publish report and update root README, root logs and error log.

No candidate can be approved for live use based on this phase alone.
