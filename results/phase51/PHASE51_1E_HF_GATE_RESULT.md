# Phase 51-1E — Hugging Face supplemental options gate result

## Decision
**REJECT_SUPPLEMENTAL_SOURCE.**

The live files for the two missing frozen expiries were downloaded successfully from thetrademarkk/india-index-options-1m, but the actual bytes do not contain the required 2026-07-28 or 2026-08-04 sessions and the common-expiry equivalence gate fails on coverage.

## Target-file evidence

| Named expiry | Rows | Min timestamp | Max timestamp | Expiry-day observations | Result |
|---|---:|---|---|---|---|
| 2026-07-28 | 320,359 | 2026-06-15 09:15 IST | 2026-07-02 15:30 IST | No | Reject |
| 2026-08-04 | 2,646 | 2026-06-24 10:08 IST | 2026-07-02 15:29 IST | No | Reject |

The actual files therefore stop on 2-Jul-2026 despite their filenames referring to later expiries.

## Common-expiry equivalence

| Common expiry | Matched rows | Coverage vs RISSIN | p95 relative error | Gate |
|---|---:|---:|---:|---|
| 2026-07-07 | 336,794 | 34.57% | 14.79 bp | FAIL |
| 2026-07-14 | 153,174 | 14.95% | 0 bp | FAIL |
| 2026-07-21 | 38,578 | 4.60% | 0 bp | FAIL |

The registered equivalence threshold requires at least 10,000 matched rows, at least 80% coverage of the RISSIN comparable rows, median absolute difference <=0.05, p99 absolute difference <=1.00, p95 relative error <=10 bp, and absolute mean signed difference <=0.05.

The price-level differences are often small on matched observations, but the coverage deficit is decisive; 7-Jul additionally fails the p95 relative-error threshold.

## Scientific consequence

This source is **not** a drop-in replacement for the frozen missing OOS blocks. No OOS strategy P&L, strike tuning, or inference has been calculated from it.

The frozen OOS window remains unchanged at 2026-04-21 through 2026-08-04.

Full structured result: results/phase51/phase51_1e_hf_options_gate_result.json