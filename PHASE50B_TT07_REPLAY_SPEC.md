# Phase 50B — TT-07 Replay Specification

## Status
Source-faithful replay contract frozen before numerical execution. No result exists yet.

## Source strategy
Dynamic IC to Ratio.

## Frozen entry
- Initial entry is on Friday, at or after 09:20 IST, while flat.
- The source's Week Day == 5 condition is interpreted as its stated Friday entry condition; no alternative weekday interpretation is tested in the baseline.
- Use the point-in-time current monthly NIFTY expiry for the initial iron condor.
- Sell monthly CE at +0.30 delta.
- Sell monthly PE at -0.30 delta.
- Buy monthly CE at +0.10 delta.
- Buy monthly PE at -0.10 delta.
- Delta is reconstructed from contemporaneous option quotes using the frozen project Black–Scholes convention; no future quote is permitted.

## Initial iron-condor transition
- The IC exits when either short leg reaches absolute delta <= 0.10.
- The first satisfied condition determines the directional transition.
- If both satisfy at the same observation, process deterministically in CE-then-PE order only to avoid nondeterministic state selection; this is a bookkeeping tie-break, not a tuned parameter.

## Directional ratio states
### Falling-market call ratio
- Buy +0.50 CE.
- Sell two +0.40 CE.
- Buy +0.10 CE.

### Rising-market put ratio
- Buy -0.50 PE.
- Sell two -0.40 PE.
- Buy -0.10 PE.

### Continuation states
- Call continuation: +0.40 / -2 x +0.30 / +0.08 CE geometry using the source leg quantities.
- Put continuation: symmetric -0.40 / -2 x -0.30 / -0.08 PE geometry.

## Ratio-state exits
- Exit/transition when the defining short leg reaches absolute delta <= 0.10 or >= 0.65.
- The next state follows only the source-defined transition logic; no discretionary reset is introduced.

## Final expiry exit
- Exit all remaining legs on the current monthly expiry day at the earliest observed timestamp at or after 15:15 IST for which all live legs have simultaneous quotes.
- Never require an exact 15:15 quote.
- Never forward-fill or impute.

## Execution/cost model
- Historical NIFTY lot size for each actual option expiry.
- Adverse 0.05-point option slippage on every option execution.
- Primary brokerage ₹10/order plus date-aware statutory charges.
- Robustness scenario ₹20/order.
- +50% monetary cost/charge stress.
- No look-ahead.

## Coverage/accounting
Every opened state position must be accounted for as a completed trade or explicit coverage exclusion. No denominator loss is permitted.
- coverage_rate = completed trade units / candidate trade units.
- Minimum feasibility threshold: 95%.
- Coverage gaps are written separately and excluded from primary P&L.
- data_errors.csv must be empty for evidence acceptance.

## Chronology
- DEV: expiry dates through 2023-12-31.
- VAL: 2024-01-01 through 2025-12-31.
- HOLD: 2026-01-01 onward and protected from selection/tuning.

## VIX
VIX is not an input to the source-faithful baseline. It is an external attribution/conditioning variable evaluated only after baseline completion.

## Deterministic delta selection
For a requested target delta, select the listed strike with minimum absolute delta error among valid contemporaneous quotes. Ties resolve to the smaller strike. This tie-break is deterministic bookkeeping, not parameter search.
