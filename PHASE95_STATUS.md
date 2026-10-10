# Phase 95 Status — Frozen-Universe Selection Test

**Date:** 2026-10-10  
**Status:** COMPLETE — preregistered DEV-to-VAL selection test failed its primary endpoint  
**Branch:** `phase-95-nested-strategy-selection-test`  
**Strategy promotion:** NONE

## Prior checks
- Phase 94 final decision/status/error/chat records and main README were checked.
- Phase 50B-7 terminal status confirms its finite phase is closed; this phase does not reopen its strategy tuning.
- Frozen Phase 45 source CSV blob SHA: `4208da2e1189a68af697e11d03dd7d4ac937ddf7`.
- Phase 83's protected 2026 holdout remains sealed. The script excludes non-DEV/VAL rows before retaining any row and never uses HOLD outcomes.

## Registered test result
- 42 strategy labels in the source; 23 eligible defined-risk candidates after requiring both DEV and VAL rows and at least 50 DEV trades.
- The rule selected `call_backspread` using DEV net50: 133 DEV trades, +₹27,393.35 net50.
- Primary endpoint failed: VAL net50 was −₹24,261.74 over 101 trades, with source max drawdown ₹112,975.51.
- Only 3 of 23 eligible candidates had positive VAL net50; this secondary count is descriptive and was not used for selection.
- No HOLD rows used; no Phase 83 holdout accessed; no market data downloaded; no strategy replay performed.
- The test is retrospective on a previously explored summary table, not an independent blinded experiment.

## Gates
- [x] Plan and source/population frozen before execution.
- [x] Script ran against fingerprint-verified source.
- [x] Primary result reconciled against the source CSV.
- [x] Latest workflow run [38054487643](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38054487643) passed after the source fingerprint and JSON newline fixes.
- [x] Result CSV and JSON generated; final report records the negative primary outcome.
- [x] Status, error/chat logs and README checkpoint updated.
- [x] Draft PR opened and verified unmerged.

## Decision
**NO PROMOTION.** Development winner selection did not transfer to stressed validation. The summary-level stress does not prove complete Paytm Money all-in execution costs; exact-contract fill evidence and independent future OOS remain prerequisites for any new strategy evaluation.
