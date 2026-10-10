# Phase 92 Error Log

Opened: 2026-10-10. Never log credentials, raw response bodies, row-level market values or hidden reasoning.

## Registered guardrails
- E92-001 — Temporal independence: request calendar 2022 only, in a Phase 92-specific cache; do not reuse Phase 90/91 cached raw payloads.
- E92-002 — Protected holdout: do not request, load, cache or analyze Phase 83's 2026 holdout.
- E92-003 — Source bounds: rolling options requests are limited to 14-day chunks and the overall range is 2022-01-01 inclusive through 2023-01-01 exclusive.
- E92-004 — Instrument master: resolve India VIX security ID dynamically and require exactly one eligible match.
- E92-005 — Data quality: check all requested arrays aligned, timestamps bounded/deduplicated, exact CALL/PUT pair timestamps, spot consistency and matching strike.
- E92-006 — Point-in-time integrity: lag candle-close-derived synthetic proxy and options IV/OI predictors by one complete five-minute row; conservatively lag VIX by one row. Never use future information.
- E92-007 — Rolling-strike integrity: no OI changes across rolling ATM strikes; use only the contemporaneous paired CE/PE OI ratio with positive denominator.
- E92-008 — Statistics: one primary endpoint, fixed model definitions, 5,000 paired session-cluster bootstrap draws, seed 90210, no tuning or subgroup significance tests.
- E92-009 — Publication/privacy: raw payloads remain in the Actions cache; publish only aggregate outputs and sanitized issue records.
- E92-010 — Interpretation: synthetic-forward proxy is not actual traded futures price/arbitrage; no exact-contract execution/P&L claim; no strategy promotion.

## Static review notes
- Phase 92 uses a full one-bar feature lag to guard against Dhan's candle-start timestamp convention and avoid using candle close/OI/IV before a bar is complete.
- If API or sample coverage gates fail, return INCONCLUSIVE and preserve error details; no imputed rows.
- The default-branch workflow entry will run only on PR creation/reopening for this phase or via manual dispatch with the fixed branch. Its publication filters intentionally exclude generated status/result changes to avoid infinite workflow-trigger loops.

## Execution / reporting corrections

- E92-011 — Expected weekend-only window: initial runs marked the 2022-12-31 to 2023-01-01 zero-row CALL and PUT intervals as schema failures. Calendar check showed the only date in the half-open interval was Saturday; there was no weekday trading session. The engine now marks a well-formed zero-row window with no weekday in its bounds as `valid=true`, `error_class=NoWeekdayExpected`. No observation was imputed and the analytical sample did not change.
- E92-012 — Non-fast-forward publication failure: run [38050580381](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050580381) completed acquisition and analysis but failed to push result files because the branch head had changed concurrently. The next complete run published the aggregates successfully; latest result is run [38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106).
- E92-013 — Trigger wiring: an additional PR run was reported as `action_required` with no job exposed. The default-branch runner now uses a push trigger limited to Phase 92 plan/engine changes plus `workflow_dispatch`; the base-branch PR trigger is limited to open/reopen to avoid rerunning the study on its own generated result commit.
- The weekend-only coverage correction and outcome-label correction changed reporting/validation classification only; the data rows, split, features, fitting period, primary endpoint and bootstrap settings were unchanged.

## Final runtime result — accepted

- Actions run: [38050805106](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38050805106), overall conclusion `success`; analysis and result publication steps completed successfully.
- Options windows valid: 54/54 (the last CALL/PUT interval is correctly annotated `NoWeekdayExpected`, zero rows); India VIX windows valid: 5/5; exactly one India VIX instrument-master match.
- Paired options observations after checks: 18,579 across 248 sessions; zero spot mismatches, one strike-mismatch timestamp excluded.
- OOS: 3,660 observations across 61 sessions. Complete DEV and validation rows were 7,357 and 3,780. VIX coverage, OOS VIX, and sample/training gates passed.
- Primary M2 MAE − M4 MAE: −0.1708363 bps; paired session-cluster bootstrap 95% CI −0.2298769 to −0.1152015 bps; positive bootstrap share 0/5,000 (seed 90210). Because the entire interval is below zero, the added synthetic-forward/OI feature block worsened predictive MAE in this fixed sample.
- No API/network/schema failures in the accepted run. This is a spot-move predictor result, not exact futures-basis, executable-fill, or strategy P&L evidence. No strategy promoted; Phase 83 2026 holdout untouched.

<!-- PHASE92_RUNTIME_START -->
## Runtime summary — 38050805106
- Status: NEGATIVE INCREMENTAL VALUE — synthetic-forward/OI feature block worsens OOS magnitude prediction in this sample
- Options valid chunks: 54/54
- VIX valid chunks: 5/5
- Instrument master: UNIQUE_MATCH; candidate count=1
- Paired rows: 18579; spot mismatches=0; strike mismatches=1
- OOS rows/sessions: 3660/61
- Primary result: M2 MAE − M4 MAE = -0.1708 bps (paired session-cluster bootstrap 95% CI -0.2299 to -0.1152; bootstrap positive share 0.0000; 5000 resamples; seed 90210).
- Issues:
- No API/network/schema failures.
- No token, raw response, row-level price, or hidden reasoning is logged.
<!-- PHASE92_RUNTIME_END -->
