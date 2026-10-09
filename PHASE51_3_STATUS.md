# Phase 51-3 Status

**State:** SCIENTIFIC SOURCE-GATE FAILURE FOUND — correcting the adapter before accepting any Phase-51-3 P&L. The workflow run [37879953815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879953815) passed software execution, audit, upload, and publication, but the post-run research audit found that the inherited engines were still using the rejected alternative source and a stale expiry registry. Therefore **all numerical P&L from that run is NON-EVIDENCE**, despite the workflow's green status.

## Self-audit finding

- The Phase-51-3 plan freezes primary options source `rissin/nse-options-intraday / upstox_intraday/NIFTY/NIFTY_2026.parquet` and validated NIFTY spot source `technovusin/nifty50-historical-data`.
- The inherited Phase-50B engines instead call the Phase-43 loader for `thetrademarkk/india-index-options-1m` and obtain eligible expiries from `results/phase43_vix/strategy_trade_matrix_all_splits.csv`.
- That alternative source was already rejected in Phase 51-1 because its nominal July/August expiry files fail endpoint/overlap gates. The inherited expiry registry also failed to expose the complete frozen partial-window expiry schedule.
- Consistent with this defect, the supposedly 2026-04-21 through 2026-07-21 replay had no completed TT-02 or TT-04 rows after May and no candidate rows spanning the last two months. The mechanical engine coverage rate counted only entries that were visible to this incomplete universe; it did not prove window-wide opportunity coverage.

This is a research implementation error, not a strategy result. The green workflow status certifies only that the prior code executed and its local artifact checks passed; it does **not** validate source lineage or candidate completeness.

## Corrective work

The wrapper is being changed to inject the frozen RISSIN raw option file, the hash-locked validated spot source, and an expiry schedule derived from the actual primary dataset. The known missing 2026-07-28 chain will be an explicit terminal boundary; 2026-08-04 remains outside the partial window and unresolved for full Phase-51 validation. TT-02's denominator will be based on the preregistered expected weekly expiry campaigns so an absent entry chain cannot artificially inflate coverage.

## Current accepted evidence

There is **no accepted Phase-51-3 P&L yet**. The previous run's artifact is retained in GitHub Actions for audit at [run 37879953815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37879953815), artifact `phase51-3-available-oos-37879953815` (artifact ID 11594226978), but it is explicitly source-mismatched/non-evidence.

## Scientific boundaries

The diagnostic window remains **2026-04-21 through 2026-07-21**; it is not the final frozen OOS window of **2026-04-21 through 2026-08-04**. The missing expiries remain **2026-07-28 and 2026-08-04**. The phase is descriptive only, requires >=95% candidate coverage and zero data errors for an eligible candidate, and may not promote a strategy. No source gaps may be silently dropped or imputed.
