# Phase 62 status — OptionsData sample and target-date validation

**Overall:** IN PROGRESS — new vendor lead accepted for a bounded sample/schema check only; exact OOS target-session acceptance remains pending.

- Branch: `phase-62-optionsdata-sample-validation`
- Parent: Phase 61 source restart audit.
- New source: https://optionsdata.shop/
- Public sample: 2026-09-15 to 2026-09-17; 1-minute contract OHLCV + OI; no bid/ask/depth.
- Public terms permit own research/backtesting and derived analysis; prohibit raw-data redistribution; vendor disclaims completeness.
- Exact missing Phase 51 sessions: 2026-07-28 and 2026-08-04. The public sample does not cover them; broad coverage metadata is not exact sample proof.
- No purchase, no credentials, no raw data committed, no P&L, no holdout use.
- Workflow: `.github/workflows/phase62-optionsdata-sample-validation.yml`
- Plan: [PHASE62_RESEARCH_PLAN.md](PHASE62_RESEARCH_PLAN.md)

## Decision rule
Do not reopen Phase 51 replay until both missing dates and the required contract rows are validated from authorized data. If exact-session data requires a paid pack, stop before checkout and request explicit authorization. No strategy is promoted by passing a schema test.


## Implementation checkpoint — 2026-10-10

- Added ephemeral sample/schema validator at `scripts/phase62_validate_optionsdata_sample.py`.
- Added `.github/workflows/phase62-optionsdata-sample-validation.yml` with branch-push trigger and `workflow_dispatch` manual run.
- Raw Parquet files remain in the temporary runner directory; only aggregate diagnostics are uploaded. No data artifacts are committed.
- The workflow was configured by a branch push; its runtime result has not yet been independently verified in this checkpoint. Exact target-date gate remains BLOCKED.


## Live catalog review — 2026-10-10

The vendor's public coverage page advertises NIFTY 1-minute options from January 2023 through October 2026. The target dates are within the overall advertised span, but exact daily file and contract coverage for 2026-07-28 and 2026-08-04 remains unverified. The 1-minute full-chain pack is listed at ₹7,249; no purchase was made. Local network access could not resolve the sample host, so the automated Actions run must be inspected before accepting the sample schema test. Current decision remains BLOCKED pending exact target sample and rights confirmation.
