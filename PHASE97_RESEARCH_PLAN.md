# Phase 97 — Drawdown-Normalized Regime Selection

Registered 2026-10-10, before running Phase 97. Parent Phase 96. Status: preregistered.

## Question
Does selecting strategies by a development-only risk-adjusted score improve regime-matched validation outcomes versus selecting by raw stressed P&L?

## Frozen method
- Source: Phase 45 summary CSV, Git blob SHA 4208da2e1189a68af697e11d03dd7d4ac937ddf7.
- Regimes: LOW, NORMAL, HIGH only; never retain/use holdout rows.
- Defined-risk candidates only, DEV and VAL rows required.
- Eligibility: LOW/NORMAL require >=20 DEV and >=20 VAL trades; HIGH requires >=3 in each because the audited source has only 3 matching validation trades for defined-risk HIGH candidates.
- Score: DEV net50 / DEV max drawdown, requiring DEV net50 >0 and DEV max drawdown >0. Select the highest score within each regime; alphabetical tie-break.
- Primary endpoint: sum of the selected candidates' matching validation net50 values. No validation metrics are used for selection.
- This is a retrospective follow-on to Phase 96 using previously explored summary data, not independent/blinded confirmation. No promotion allowed.

## Stop and limitations
One run, fixed three regimes, no tuning. The source net50 is not proof of complete Paytm Money costs or executable fills. State-cell P&L cannot be called a deployable portfolio return without trade overlap and capital allocation. HIGH is extremely sparse. Stop after report, QA and PR.
