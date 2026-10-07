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


## Source-lock update — 2026-10-07
The raw Tradetron export resolves the state transition graph, but it leaves one runtime-scope question unresolved: the variable ic_entered is initialized to 0 and set to 1 by the initial IC entry, with no reset anywhere in the export. The replay therefore must not assume repeated initial-IC entries after a terminal state or monthly universal exit.

Exact transitions recovered:
- state 0 -> state 1 on CE short abs(delta) <= 0.10; state 0 -> state 2 on PE short abs(delta) <= 0.10.
- state 1 -> state 3 on short abs(delta) <= 0.10; state 1 -> state 2 on short abs(delta) >= 0.65.
- state 2 -> state 4 on short abs(delta) <= 0.10; state 2 -> state 1 on short abs(delta) >= 0.65.
- state 3 -> state 5 on short abs(delta) <= 0.10; state 3 -> state 2 on short abs(delta) >= 0.65.
- state 4 -> state 6 on short abs(delta) <= 0.10; state 4 -> state 1 on short abs(delta) >= 0.65.
- state 5 -> state 3 on short abs(delta) <= 0.10; no >=0.65 transition is present in the export.
- state 6 -> state 4 on short abs(delta) <= 0.10; no >=0.65 transition is present in the export.

**Runtime-variable lifecycle resolution — 2026-10-07**

Official Tradetron documentation was checked before numerical implementation. Runtime Variables are strategy-level memory and persist through the current cycle until a Universal Exit; the current cycle/counter is the unit associated with live runtime values. Therefore the raw export's `ic_entered=0 -> 1` is interpreted as:

- initialize `ic_entered=0`, `state=0` at the start of each new strategy counter;
- set `ic_entered=1` at the first initial-IC entry;
- do not reset `ic_entered` during any intra-cycle transition;
- monthly Universal Exit at current-month expiry >=15:15 ends the counter, allowing the next counter to initialize again;
- do not invent any additional reset.

Sources: [Tradetron Runtime Variables](https://help.tradetron.tech/en/article/runtime-variables-in-tradetron-capture-once-use-anywhere-83nahv/) and [Tradetron keyword documentation](https://files.tradetron.tech/TT_Keywords.pdf).

**Frozen transition implementation rule**

A state transition is executed only when the source trigger is satisfied and complete contemporaneous quotes exist for every leg of both the exiting state and the target state. When the target state lacks a complete quote set, the current state is retained and the trigger is re-evaluated at the next observed timestamp; no partial or synthetic transition is created. This is a deterministic data-feasibility rule, not a parameter choice. Such missed transition observations are reported in a dedicated diagnostic table.

**Execution gate:** TT-07 is now unblocked and may enter numerical replay after the registered TT-06 evidence dependency passes. No numerical result exists yet.