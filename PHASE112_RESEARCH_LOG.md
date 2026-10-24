# Phase 112 Research Log

Append every completed step, including failures and corrections. Keep source SHA, source file hashes, code/protocol revision, expected/eligible/excluded denominators, test results, cost cases and run URL. Do not store credentials, raw minute data, or hidden chain-of-thought.

## 2026-10-24 — Registration
- User asked to test Greek stop-loss combinations following the Phase 111 ZigZag strategy.
- Kept the fixed entry rule unchanged: confirmed daily low (HL/LL) sells PE, confirmed daily high (HH/LH) sells CE, absolute model Delta target 0.10, exact 10:00 entry next observed session after previous expiry.
- Fixed scheduled exit at exact 10:00 on target expiry. Stop triggers use completed one-minute close and next observed minute open.
- Registered normalized Delta, Gamma, Vega, Theta and Rho stop criteria, single-Greek threshold sweeps, all multi-Greek subsets, ANY/ALL logic, no-stop reference, 24 cost cases and chronological splits in PHASE112_RESEARCH_PLAN.md before replay.
- Phase 111 first replay summary was 259 scheduled / 142 eligible / 121 excluded, split 96/45/1. The source used a Python confirmed-only ZigZag proxy because the supplied source omitted the imported ZigLib body; that caveat carries forward.
- No Greek-combination P&L has yet been accepted at registration.
