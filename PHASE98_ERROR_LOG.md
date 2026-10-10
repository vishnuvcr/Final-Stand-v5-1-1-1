# Phase 98 Error / Limitation Log

## Existing limitations
- Phase 66: zero completed trades; profitability is not estimable from that replay.
- Phase 85: no-go for a new execution-quality replay using then-verified free sources.
- Phase 87–89: rolling ATM-relative fields on limited samples do not prove source-period exact-contract bid/ask/depth or executable fills.
- CCI signal bars, original-period contract mappings and exact entry/exit/fill evidence may remain unavailable. Never invent trades to fill coverage.

## Runtime errors
- None at phase start. Add all audit/workflow errors and fixes.

- 2026-10-10, Actions run 38072909482: CCI gate test failed because the test searched only one CSV tuple column for the phrase describing rolling ATM-relative coverage; the evidence phrase was in another field. Corrected the assertion to inspect the full row. The gate itself did not run in that failed attempt; no output from it is accepted until the rerun passes.
