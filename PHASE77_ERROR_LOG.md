# Phase 77 Error / Blocker Log
Date: 2026-10-10

## B77-001 — Small expiry-cluster sample
- Status: OPEN as an evidence limitation.
- TT-04 has 13 expiry clusters and TT-05 has 14; 95% percentile intervals for total net include zero. Bootstrap outputs are descriptive and cannot establish a persistent edge.

## B77-002 — Missing late-window expiries
- Status: CLOSED as source decision; exclusion remains.
- Expiries 2026-07-28 and 2026-08-04 are absent from the validated primary options source, and the alternative files are stale. No imputation is allowed.

## B77-003 — Ledger reconciliation
- Status: CLOSED.
- Workflow 38043011951 reconciled TT-02 (13 trades), TT-04 (62), and TT-05 (62) against the frozen summary totals. No schema/count/net mismatches were detected; the tiny TT-05 floating-point difference is less than ₹0.01.

## B77-004 — Initial bootstrap implementation runtime
- Status: CLOSED; optimized.
- The first implementation completed successfully but took longer than desired because resampling was performed in nested Python loops. The final script vectorizes the 10,000 cluster resamples. The final workflow is the bounded implementation; both runs are logged, and both completed successfully.

## B77-005 — Result persistence
- Status: CLOSED by workflow hardening.
- Initial run published aggregate outputs as a workflow artifact only. The workflow now also commits `results/phase77_partial_oos_inference/summary.json` and `report.md` to this phase branch, with a manual `workflow_dispatch` trigger retained.

## B77-006 — Strategy promotion gate
- Status: CLOSED for this phase.
- No strategy promoted. TT-04 and TT-05 remain diagnostic candidates only; TT-02 is negative across the four registered cost/friction cases.
