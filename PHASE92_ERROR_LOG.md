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

## Runtime
No run has been verified yet. Append the sanitized runtime result after the workflow completes. A successful Actions job does not itself imply the predictive-gain hypothesis passed.

<!-- PHASE92_RUNTIME_START -->
## Runtime summary — 38050610192
- Status: NO INCREMENTAL GAIN ESTABLISHED — primary bootstrap interval includes or falls below zero
- Options valid chunks: 52/54
- VIX valid chunks: 5/5
- Instrument master: UNIQUE_MATCH; candidate count=1
- Paired rows: 18579; spot mismatches=0; strike mismatches=1
- OOS rows/sessions: 3660/61
- Primary result: M2 MAE − M4 MAE = -0.1708 bps (paired session-cluster bootstrap 95% CI -0.2299 to -0.1152; bootstrap positive share 0.0000; 5000 resamples; seed 90210).
- Issues:
- Options 2022-12-31–2023-01-01 CALL: schema or array-alignment gate failed.
- Options 2022-12-31–2023-01-01 PUT: schema or array-alignment gate failed.
- No token, raw response, row-level price, or hidden reasoning is logged.
<!-- PHASE92_RUNTIME_END -->
