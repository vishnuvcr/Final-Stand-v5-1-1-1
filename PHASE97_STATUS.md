# Phase 97 Status — Risk-Adjusted Regime Selection

**Status:** COMPLETE — primary endpoint failed; NO PROMOTION  
**Date:** 2026-10-10

## Result
- Source fingerprint verified: `4208da2e1189a68af697e11d03dd7d4ac937ddf7`.
- LOW selected `call_backspread`: DEV score 2.827173; VAL net50 −₹73,980.97 (49 trades).
- NORMAL selected `put_backspread`: DEV score 1.183000; VAL net50 −₹82,413.19 (50 trades).
- HIGH selected `short_iron_butterfly`: DEV score 6.253377; VAL net50 −₹1,808.79 (3 trades; descriptive only).
- Aggregate selected validation net50: **−₹158,202.95**. All three validation cells negative.
- Latest successful workflow [38055041961](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38055041961).
- [Results report](results/phase97/selection_report.md), [CSV](results/phase97/risk_adjusted_results.csv), [JSON](results/phase97/validation_report.json).

## Gates
- [x] Preregistered score and fixed regimes.
- [x] Source fingerprint and split guard passed.
- [x] Result report/CSV/JSON persisted.
- [x] Status/error/chat logs updated.
- [x] Draft PR opened; remain unmerged.

Decision: NO PROMOTION. This is retrospective exploratory summary-table analysis, not a new market replay or independent blinded validation.
