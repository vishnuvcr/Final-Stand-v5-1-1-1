# Phase 50B Pre-Registration

## Frozen universe
Use the candidate registry in PHASE50B_STRATEGY_UNIVERSE.md.

## Chronology
Development 2021–2023.
Validation 2024–2025.
Protected holdout 2026.

## VIX
Reuse the accepted parent-phase VIX state definitions without threshold changes after seeing results.

## Mutations
Only source-semantic dimensions may be varied:
- strike distance;
- delta target where the source already uses delta;
- explicit spread width or hedge distance;
- entry time or DTE only where preregistered for that strategy.

Management triggers, stops and expiry rules remain source-faithful unless a separate finite variant is preregistered.

## Statistics
Use active-VIX versus complement bootstrap inference, two-sided permutation inference, Holm correction, paired common-expiry baseline comparisons, annual/regime breakdowns, drawdown and expected-shortfall diagnostics.

## Promotion
Require economic validation positivity, doubled-friction positivity, adequate execution coverage, statistical gate passage and protected 2026 confirmation.
## Execution coverage rule
For source-faithful baselines using historical option-chain data, mandatory exit observations must be available simultaneously for all open legs. At least 95% of opened positions must have a complete observed exit quote at or after the source-defined exit trigger for the strategy to pass the feasibility gate. Coverage gaps are excluded from primary P&L statistics, never forward-filled or imputed, and are reported separately. A candidate below 95% complete-exit coverage fails feasibility and does not advance to confirmatory inference.

## Explicit non-claims
A Tradetron report, repository README, video, or earlier backtest does not establish a durable edge.

## Brokerage robustness
The preregistered primary execution model remains ₹10/order for continuity with the parent research program. Because current Paytm Money public materials indicate a flat ₹20/order rate from 15 January 2025 while an older F&O FAQ still displays ₹10, every candidate that reaches promotion must also report a ₹20/order brokerage robustness scenario. This secondary scenario cannot be used to select or tune candidates and cannot be omitted from the final cost-sensitivity table. citeturn157124search2turn157124search0


## 2026-10-07 — Statistical-gate fail-closed hardening
The statistical gate now requires the preregistered ₹10 and ₹20 cost outputs (net, net50, net20, net20_50) instead of substituting missing fields. All seven Phase-50B strategy slots are registered in the execution gate; unavailable artifacts are skipped rather than fabricated.


## Statistical holdout protection clarification — 2026-10-07
The preregistered bootstrap/permutation VIX-regime inference family is explicitly defined on **DEV+VAL (2021 through 2025)**. The protected 2026 HOLD is excluded from hypothesis testing, Holm-family construction, threshold selection and candidate ranking. HOLD is used only for final out-of-sample confirmation/descriptive performance after all pre-holdout decisions are frozen.
