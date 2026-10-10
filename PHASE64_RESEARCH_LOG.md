# Phase 64 Research Log

## 2026-10-10 — Phase opened and rule frozen
- User instruction: “Continue And inspect PDFs of research papers from sources to add and test new strategies”.
- Reviewed existing Phase 49 research plan, frozen Phase-49 tuning code and decision artifact, Phase 50B research plan/strategy universe/source baseline audit/market-cost audit, Phase 48 inconclusive independent-data bridge, Phase 51-3 partial-OOS report and Phase 62 source status before designing this phase.
- Rendered and visually checked the first page of all fourteen user-uploaded PDFs; extracted searchable local text from the full papers. PDF indexing through the Files search layer returned no results, so the mounted PDFs were processed directly.
- Identified Pinkal Shaha (2019) CCI strategy as the most explicitly executable paper-derived rule. Read the full strategy, assumptions and results section, not just its abstract.
- Source paper claims 68 trades (43 profitable + 25 losses), ₹145,362 net and 63.25% win rate, but its table later lists 80 trades total. The original 2008–2018 period is not represented by the pinned intraday dataset. These are paper claims, not accepted evidence.
- Registered two variants only: CCI breakout long ITM option (A) and the same entry/exit rules with an EMA(50)/EMA(200) trend confirmation (B). Variant B is a newly hypothesized filter inspired by the uploaded moving-average paper, not a claim that that paper validated an option strategy.
- Frozen DEV through 2023, VAL 2024–2025; 2026 is explicitly protected and out of the Phase-64 runner. No parameter search on VAL, and no 2026 holdout testing.
- Dataset source planned at a fixed HF revision. License attribution and non-commercial restriction will be recorded. No raw data or secrets will be committed.
- Cost rules and data limitations are preregistered. No numerical strategy results are claimed at phase opening.


## 2026-10-10 — Pre-acceptance point-in-time strike correction
- Workflow run 38026911131 passed setup, dependency installation, py_compile and the current unit tests, but the numerical step was cancelled before any output was accepted.
- Re-inspected the entry implementation and identified a prospective temporal bug: the strike universe was built from every contract minute in the expiry file. This could let future contract availability influence ITM selection at the earlier breakout.
- Corrected to select the nearest strictly ITM contract from bars observed exactly at the breakout minute, then require the next exact minute's option close for entry. Added a regression test called test_strike_selection_uses_trigger_minute_availability_only.
- Run 38026911131 is explicitly non-evidence; no P&L from it is accepted. Latest code must pass unit tests and complete the frozen DEV/VAL test before any interpretation.

## 2026-10-10 — Corrected Phase 64 run completed
- Run 38027023283 completed successfully after the point-in-time strike-selection correction. Syntax/unit tests, numerical runner, report generation, output validation and publication passed; marker confirms zero 2026 option files downloaded.
- Aggregate results: 56 late-month expiry-file proxies (32 DEV, 24 VAL); CCI_BASE 0 completed trades despite 12 DEV/13 VAL breakout-trigger opportunities; CCI_EMA_FILTER 0 completed trades despite 4 DEV/1 VAL triggers.
- These zero-trade samples cannot estimate returns, win rate, expectancy, profit factor, or drawdown. Empty sums printed as 0 are not measured zero P&L. Both candidates fail >=20 validation trades and >=95% trigger coverage.
- Decision remains NO PROMOTION. Treat this as data/protocol coverage failure, not evidence that the CCI concept has negative expectancy. Next action is one bounded timestamp/contract-coverage audit; no parameter expansion or gate relaxation.
