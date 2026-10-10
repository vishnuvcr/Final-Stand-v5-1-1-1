# Phase 68 final result

Status: COMPLETE — BLOCKED_STALE_OR_MISSING_TARGET_ROWS.

The pinned Hugging Face revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5` was audited from actual Parquet bytes.

- `options/NIFTY/2026-07-28.parquet`: 320,359 rows; timestamps 2026-06-15 09:15 through 2026-07-02 15:30 IST; 0 rows for 2026-07-28.
- `options/NIFTY/2026-08-04.parquet`: 2,646 rows; timestamps 2026-06-24 10:08 through 2026-07-02 15:29 IST; 0 rows for 2026-08-04.

Aggregate evidence: `results/phase68_hf_target_date_audit/summary.json` and `results/phase68_hf_target_date_audit/report.md`.

Decision: reject this source for the two missing sessions. No Phase 51 replay, P&L, parameter change, holdout access, or strategy promotion. Reopen only on a genuinely new authorized sample with exact target-date bytes.