# Phase 37 Status — Corrected Model Direction Polarity

## Current state
**INITIALIZED — NUMERICAL EXECUTION PENDING**

A post-acceptance audit of Phase 36 found that the five model selectors were mapped in the opposite direction to the strategy's intended bullish/bearish economic meaning.

Phase 35 defines the prediction target as the sign of expiry-close relative to reference spot. Therefore:
- up/bullish prediction -> PUT spread;
- down/bearish prediction -> CALL spread.

Phase 37 is a clean correction-only rerun. No model, threshold, feature set, execution parameter or cost assumption is being retuned.

## Invalidated Phase-36 model interpretation
The Phase-36 model-selector P&L is retained as an audit artifact, but it is not valid evidence for the intended bullish/up -> PUT and bearish/down -> CALL hypothesis.

## Rerun selectors
- CATBOOST
- DART
- WAVELET_TREE
- OOF_STACK
- MARKOV_REGIME_TREE

## Sample
2024-01-01 through 2026-06-30, matching Phase 36.

## Acceptance
The corrected numerical results will be accepted only after:
1. successful GitHub Actions execution;
2. code audit of the polarity mapping;
3. complete trade/skip/summary/coverage artifacts;
4. validation of 2026 holdout reporting;
5. bootstrap comparison versus the stateful control.

## Current decision
No promotion decision has been made.


## Step 1 — workflow-trigger preparation — 2026-10-06
The corrected engine and manual-dispatch workflow are committed. A repository-path push trigger will be used for the numerical execution so the phase is reproducible without manual local execution.


## Step 2 — execution registration — 2026-10-06
- Corrected model-to-spread polarity is frozen: bullish/up probability >= 0.50 -> PUT; bearish/down probability < 0.50 -> CALL.
- No retraining, threshold tuning, selector reweighting or execution-rule changes are permitted.
- PR #11 is open for repository-level execution/audit: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/11
- The numerical workflow is configured for automatic push execution and manual dispatch; an audited PR-trigger path has also been registered.
- Numerical evidence has not yet been accepted; no model is promoted.
