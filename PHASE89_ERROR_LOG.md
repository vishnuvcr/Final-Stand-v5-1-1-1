# Phase 89 Error Log

Date opened: 2026-10-10  
Rule: log API/network/schema/data-quality and analysis-gate issues. Never log credentials, raw response bodies, raw market prices, or hidden reasoning.

## Preregistered guardrails
- E89-001 — Protected holdout: 2026 dates are prohibited; API request windows end before 2026-01-01.
- E89-002 — Rolling contract discontinuity: CALL/PUT data are ATM-relative, not a fixed listed contract; no option-premium return feature or executable trade P&L is inferred.
- E89-003 — Quote quality: historical bid/ask/depth/fill data are absent; no slippage/execution claim.
- E89-004 — Scope: endpoint does not supply the Greeks, futures/synthetic futures, VIX, DII/FII, news or corporate-action fields required for those separate hypotheses.
- E89-005 — Multiple testing: exactly four OOS primary hypotheses; Holm correction across the four; no post-hoc feature promotion.
- E89-006 — Cache/publication: raw payloads stay inside runner cache, not repository files, artifacts, summaries or logs.
- E89-007 — Initial workflow run stopped before data acquisition because setup-python pip caching required a dependency manifest; the unsupported pip-cache setting was removed. No data request occurred in that run.
- E89-008 — First completed run used 2026-01-01 as the final exclusive API boundary while filtering the returned rows to 2025. A stricter boundary is now enforced: all requests end no later than 2025-12-31 exclusive, using a new cache key.
- E89-009 — Audit identified potential ATM strike-roll contamination of trailing OI change. The corrected analysis excludes CALL/PUT ATM-strike mismatches and requires both strikes to remain unchanged over the trailing 15-minute window.

## Runtime issues
No run outcome recorded yet.

<!-- PHASE89_RUNTIME_START -->
## Runtime summary — 38047664790
- Status: COMPLETE — OOS sample gate passed; interpret only the four Holm-controlled feature associations
- API requests passing schema/alignment: 28/28
- Paired rows after timestamp and spot consistency checks: 18604
- OOS complete observations/sessions: 4224/62
- Issues:
- No API/network/schema failures were observed.
- No credential, raw response body, or raw price is recorded here.
<!-- PHASE89_RUNTIME_END -->
