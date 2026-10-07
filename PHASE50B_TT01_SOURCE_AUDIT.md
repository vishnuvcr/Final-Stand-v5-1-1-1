# Phase 50B — TT-01 Source Audit

## Strategy
Dynamic Ratio Reversals.

## Initial state
- Runtime variables: `state=1`, `entered=1`.
- Put-ratio initial set is therefore immediately active whenever flat.
- The strategy also contains state-machine transitions into opposing ratio structures.

## Source geometry
- Put ratio: buy monthly PE at -0.50 delta; sell two PE at -0.40 delta; buy one PE at -0.10 delta.
- Call ratio: buy monthly CE at +0.50 delta; sell two CE at +0.40 delta; buy one CE at +0.10 delta.
- Continuation A: buy +0.40 CE / sell two +0.30 CE / buy +0.08 CE after the relevant short-leg delta falls to 0.10.
- Symmetric put continuation uses -0.40 / -0.30 / -0.08.
- Reversals are triggered when the relevant 0.10-delta short leg reaches an absolute delta of at least 0.60.

## Exits
Every ratio state has a source exit when the defining short-leg delta reaches <=0.10 or >=0.60, with a universal monthly-expiry 15:15 exit.

## Evidence handling
Native Tradetron performance is provenance only. This source is a state-machine strategy, so Phase-50B replay must preserve runtime state transitions exactly before any VIX/tail mutation is permitted.

## Priority
High-priority source control because it is the closest direct Tradetron analogue to the Iron-condor-to-ratio GitHub lineage, but its native High-VIX diagnostic was negative. It will not be promoted from the native result.