# Phase 50B — TT-07 Source Audit

## Strategy
Dynamic IC to Ratio.

## Initial state
- Runtime variables: `ic_entered=0`, `state=0`.
- Initial entry: Friday (`Week Day == 5`) at/after 09:20 while flat.

## Initial iron condor
- Sell monthly CE at +0.30 delta.
- Sell monthly PE at -0.30 delta.
- Buy monthly CE at +0.10 delta.
- Buy monthly PE at -0.10 delta.
- The initial IC exits when either short leg reaches absolute delta <=0.10.

## Directional transition state machine
- Falling-market call ratio: buy +0.50 CE, sell two +0.40 CE, buy +0.10 CE.
- Rising-market put ratio: buy -0.50 PE, sell two -0.40 PE, buy -0.10 PE.
- Continuation states use +0.40/+0.30/+0.08 CE or the symmetric -0.40/-0.30/-0.08 PE geometry.
- A ratio state exits when its defining short leg reaches absolute delta <=0.10 or >=0.65.
- Universal exit: current-month expiry day at/after 15:15.

## Evidence handling
Native Tradetron P&L is provenance only. Common replay must use exact option quotes, point-in-time delta reconstruction, historical lot size and Paytm Money/NSE cost assumptions.

## Priority
High-priority source control because it overlaps the independently specified Iron-condor-to-ratio GitHub lineage and is directly relevant to VIX/tail-state transitions. Native High-VIX diagnostic had only 3 High result days, so it cannot establish a regime edge.

## Raw-export state-machine reconciliation — 2026-10-07

The original ASB export was independently inspected rather than inferred from the summary audit.

### Exact state map recovered from the export
- state=0: Initial monthly iron condor. If CE short absolute delta <=0.10, exit IC and enter state=1. If PE short absolute delta <=0.10, exit IC and enter state=2.
- state=1: Initial call ratio (+0.50 / -2×+0.40 / +0.10 CE). If defining short absolute delta <=0.10, exit and enter state=3. If defining short absolute delta >=0.65, exit and enter state=2.
- state=2: Initial put ratio (-0.50 / +? two short -0.40 / -0.10 PE; all PE quantities are signed by option position). If defining short absolute delta <=0.10, exit and enter state=4. If defining short absolute delta >=0.65, exit and enter state=1.
- state=3: Continuation call ratio (+0.40 / -2×+0.30 / +0.08 CE). If defining short absolute delta <=0.10, exit and enter state=5. If defining short absolute delta >=0.65, exit and enter state=2.
- state=4: Continuation put ratio (-0.40 / -2×-0.30 / -0.08 PE). If defining short absolute delta <=0.10, exit and enter state=6. If defining short absolute delta >=0.65, exit and enter state=1.
- state=5: Second call continuation (+0.40 / -2×+0.30 / +0.08 CE). If defining short absolute delta <=0.10, exit and enter state=3. The export contains no >=0.65 entry transition for this state.
- state=6: Second put continuation (-0.40 / -2×-0.30 / -0.08 PE). If defining short absolute delta <=0.10, exit and enter state=4. The export contains no >=0.65 entry transition for this state.

The monthly universal exit is a separate terminal exit on the current-month expiry day at/after 15:15.

### Important source ambiguity — ic_entered lifecycle
The export initializes ic_entered=0 and the initial IC entry condition sets it to 1. No later condition in the raw export resets ic_entered to 0. Therefore it is not scientifically defensible to assume that a new initial IC is allowed after a state-5/state-6 terminal transition or after monthly universal exit.

Decision: TT-07 numerical replay is blocked until this runtime-scope semantics is resolved from actual Tradetron execution behavior or an authoritative account/backtest trace. No substitute interpretation will be silently coded.
