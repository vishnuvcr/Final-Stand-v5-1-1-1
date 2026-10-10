# Phase 96 Status — VIX-Regime-Adaptive Strategy Selection

**Status:** PREREGISTERED — not yet executed  
**Date:** 2026-10-10  
**Branch:** `phase-96-vix-regime-adaptive-strategy-test`  
**Promotion:** NONE

## Preflight
- [x] Read main README and Phase 94 final decision.
- [x] Read Phase 95 plan/status/error/chat/report.
- [x] Read Phase 92 cross-phase predictor synthesis and Phase 50B-7 terminal status.
- [x] Verified Phase 45 source CSV SHA: `4208da2e1189a68af697e11d03dd7d4ac937ddf7`.
- [x] Registered three fixed regimes (LOW/NORMAL/HIGH), defined-risk-only population, minimum trade thresholds and DEV-only selection rule.
- [ ] Run workflow and validate output.
- [ ] Update final decision and logs.
- [ ] Open draft PR and verify it remains unmerged.

## Frozen method
For each of LOW, NORMAL, HIGH, select the eligible strategy with highest development net50, requiring >=20 DEV and >=20 validation trades. Primary endpoint is sum of the three matching validation net50 values. Holdout rows are excluded before any fields are processed.
