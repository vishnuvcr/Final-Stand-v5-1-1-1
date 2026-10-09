# Phase 51-4 Error Log

Every material error, failed assumption, correction and evidence impact must be recorded here.

## E51-4-001 — Full-window data gaps persist
- **Date:** 2026-10-09
- **Observation:** Accepted primary options source stops at 2026-07-21; two expiry blocks (2026-07-28 and 2026-08-04) remain unavailable from a source passing the target-session gates.
- **Correction / scope:** User explicitly authorized proceeding with the available interval only. Created Phase 51-4 as a separately labelled partial-window continuation; the original full-window preregistration is unchanged.
- **Evidence impact:** Available-window analysis remains descriptive and cannot support a claim of full-window OOS performance. No strategy promotion.

## E51-4-002 — Lineage audit did not constitute a new replay
- **Date:** 2026-10-09
- **Observation:** GitHub Actions metadata confirmed prior run 37882057283 succeeded and its artifact exists, but this follow-up did not download and re-hash the artifact payload or execute the backtest again.
- **Correction:** Labelled the activity a metadata/lineage check only; preserved the original run as the authoritative replay and made no claim of new execution.
- **Evidence impact:** Results remain the already audited partial-window results. Do not represent the lineage check as independent reproduction or a second backtest.

## E51-4-003 — Small exploratory sample limits ranking claims
- **Date:** 2026-10-09
- **Observation:** TT-05 leads net P&L in the four cost/friction scenarios, but the sample contains 62 trades in a short time interval and is not an independent confirmatory comparison.
- **Correction:** Reported TT-05 only as the descriptive leader; no statistical-superiority claim, tuning, or promotion.
- **Evidence impact:** Further strategy selection requires preregistered validation beyond this partial interval.
