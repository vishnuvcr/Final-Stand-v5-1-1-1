# Phase 83 Error / Limitation Log
Date: 2026-10-10

## E83-001 — Synthesis must preserve experiment boundary
- Status: CONTROL.
- Manuscript conclusions apply to the specific ten registered static structures and paired intraday/overnight experiment. They must not be generalized to every possible strategy or retroactively substitute for other Final Stand phase decisions.

## E83-002 — No executable quote evidence
- Status: KNOWN LIMITATION.
- Phase 81 uses option candle opens and modeled adverse ticks/charges. No historical bid/ask/depth, queue position or partial fill data were used.

## E83-003 — Holdout not opened
- Status: CONTROL / INTENTIONAL.
- Phase 82 identified zero defined-risk variant-window candidates that pass its frozen profitability gate. The 2026 holdout remains untouched rather than being used to rescue or tune a failed candidate.

## E83-004 — Literature findings are not project results
- Status: CONTROL.
- External-paper results are cited as reported by the source or as abstract-level leads. No paper's headline accuracy, Sharpe or P&L is copied into the project's empirical-results ledger.

## E83-005 — Manuscript builder schema mismatch
- Status: RESOLVED.
- Failed run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38045979044.
- Root cause: the builder required a column named profit_factor, while the frozen Phase 81 ledger correctly uses profit_factor_1tick.
- Correction: updated the schema guard to the source's actual column name; rerun 38046031945 passed figure build, validation, artifact upload, status/README update and persistence.
- Impact: no Phase 81/82 numerical results changed; the first attempt stopped before publishing figures or supplementary output.
