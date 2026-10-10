# Phase 78 — Temporal stability reconciliation
Date: 2026-10-10
Status: PLAN FROZEN

## Question
Do the positive TT-04/TT-05 results in the short April–July 2026 partial-OOS sample agree with the strategies' existing frozen DEV/VAL/HOLD results, especially the HOLD split?

## Method
1. Read only committed, frozen Phase 50B strategy summaries and Phase 51-3 partial-OOS summaries.
2. Reconcile strategy identity and engine revision; compare the four registered cost/friction cases across DEV, VAL, HOLD and the newer partial interval.
3. Preserve the two missing expiries (2026-07-28 and 2026-08-04) as exclusions.
4. Treat temporal sign disagreement as a stability failure, not as a reason to tune parameters.
5. No new data, strategy variants, or outcome-driven filtering. No promotion.

## Gates
- Missing or mismatched summary/engine: audit fails.
- A positive partial sample cannot override a negative historical HOLD split.
- If the existing HOLD split is negative at base and stress costs, classify as unstable and do not promote.
- This is an evidence reconciliation, not a new independent validation sample.

## Deliverables
`scripts/phase78_temporal_stability.py`, `results/phase78_temporal_stability/report.md`, `summary.json`, status/error logs and manual GitHub Actions workflow.
