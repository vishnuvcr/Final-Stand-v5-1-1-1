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