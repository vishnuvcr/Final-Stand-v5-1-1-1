# Phase 79 — Current Hugging Face revision recheck

**Decision: BLOCKED_CURRENT_SOURCE_INCOMPLETE**

Dataset revision: `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`

## Target expiry-session coverage

| Expiry | File rows | Explicit expiry rows | Expiry-session rows | Regular rows | Complete 375-bar groups | OHLC valid | SHA-256 |
|---|---:|---:|---:|---:|---:|---|---|
| 2026-07-28 | 320359 | 320359 | 0 | 0 | 0 | True | `f9c3a6d1e4498274644ccbfeb8aeb3d545fc2ce1a12b908f450360a643e40d17` |
| 2026-08-04 | 2646 | 2646 | 0 | 0 | 0 | True | `8de2f08cef1456c448c4fc4be0d9d586a1b26af30bf67990171385361af92f9c` |

## Interpretation

This audit checks the current dataset revision rather than Phase 76’s older pinned revision. Only aggregate diagnostics are retained; raw Parquet files remain ephemeral. Even if coverage passes, OHLC bars do not prove executable fills or spread/depth quality. The dataset is marked CC-BY-NC-4.0 and must not be treated as cleared for commercial use.

## Errors

- None.
