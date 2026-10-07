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
Use active-VIX versus complement bootstrap inference, one-sided permutation inference, Holm correction, paired common-expiry baseline comparisons, annual/regime breakdowns, drawdown and expected-shortfall diagnostics.

## Promotion
Require economic validation positivity, doubled-friction positivity, adequate execution coverage, statistical gate passage and protected 2026 confirmation.
## Execution coverage rule
For source-faithful baselines using historical option-chain data, mandatory exit observations must be available simultaneously for all open legs. At least 95% of opened positions must have a complete observed exit quote at or after the source-defined exit trigger for the strategy to pass the feasibility gate. Coverage gaps are excluded from primary P&L statistics, never forward-filled or imputed, and are reported separately. A candidate below 95% complete-exit coverage fails feasibility and does not advance to confirmatory inference.

## Explicit non-claims
A Tradetron report, repository README, video, or earlier backtest does not establish a durable edge.