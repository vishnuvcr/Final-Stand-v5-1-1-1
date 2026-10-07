# Phase 50B Research Plan — Expanded Prior-Strategy Universe

## Research question
Do the user's previous NIFTY option strategies, plus the seven supplied Tradetron strategies, contain robust VIX-conditioned or far-OTM variants that survive the same chronological validation and realistic execution-cost gates used in Final Stand v5?

## Scope
This is a prospective scope expansion before confirmatory testing. Existing positive backtests are provenance/control evidence only.

## Candidate sources
Seven supplied Tradetron strategies:
1. Dynamic Ratio Reversals
2. 0.20/0.10 Delta Calendar Hedge Spread v4
3. Corrected Dynamic-n NIFTY Weekly Options Strategy
4. Profit Breakout Premium Match Straddle
5. Simple Intraday Short Straddle
6. Intraday Asym Premium
7. Dynamic IC to Ratio

Prior GitHub strategy lineages:
- Iron-condor-to-ratio-v1 and v2
- Option-intraday-v1
- NoDip-Stage-1
- MC-OPTIONS-INDEPENDENT-BACKTEST-MC1
- MC-OPTIONS-MARGIN-REDUCTION-MC2
- MC-OPTIONS-VERIFICATION-MC3
- Daily-Options
- Final-stand-v4 and v2

## Phase sequence
50B-0 registry and source normalization.
50B-1 feasibility and quote-coverage audit.
50B-2 source-faithful baseline.
50B-3 VIX conditioning.
50B-4 far-OTM geometry where a natural strike-distance variable exists.
50B-5 chronological development/validation and protected 2026 holdout.
50B-6 bootstrap/permutation inference with Holm correction.
50B-7 manuscript, figures, tables, appendices and final decision.

## Scientific rules

## Execution coverage feasibility
The Phase-50B feasibility gate is operationalized at 95% complete mandatory-exit quote coverage for opened positions. Sparse historical option coverage is treated as a data limitation, not silently repaired. Coverage-gap trades are excluded from primary P&L statistics, retained in a separate coverage log, and never imputed. Candidates below 95% coverage fail the feasibility gate; candidates above it must carry the coverage rate and exclusions into the final sensitivity/limitations analysis.

## Scientific rules
Source ambiguities must be resolved before the freeze or represented as finite preregistered variants. No post-result VIX threshold, strike distance, stop, exit, DTE or width changes.

Only semantically valid strike-distance mutations are allowed. Strategies without a natural distance variable remain source-faithful controls unless a new phase registers a distinct structural mutation.

Cost model, no-look-ahead rules, historical lot sizes and doubled-friction stress remain those accepted by the parent research program.

## Deduplication
Exact or near-exact lineages are linked rather than pooled until an explicit rule-diff is completed. Provenance remains separate.

## Stop condition
The phase stops after the finite registered candidate universe has passed its applicable gates. It does not reopen an unbounded strategy search.

## Candidate-local stopping rule — 2026-10-07
A strategy that fails a preregistered feasibility gate is closed for promotion, VIX conditioning, parameter tuning and confirmatory inference. That failure does **not** block unrelated strategies in the finite registered universe from being tested. Downstream workflows may continue only when the failed strategy has a terminal, persisted feasibility classification and the next strategy's workflow explicitly verifies that no failed candidate P&L is being consumed as evidence.
