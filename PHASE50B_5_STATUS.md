# Phase 50B-5 Status — Chronological Validation

## State
**ACTIVE — waiting for/entering GitHub Actions execution**

Branch: `phase-50b-chronological-validation`

## Frozen scope
- TT-03 source-faithful baseline
- TT-03 OTM350, the single frozen far-OTM mutation selected in 50B-4
- TT-04 source-faithful baseline
- TT-05 source-faithful baseline
- TT-06 and TT-07 excluded because terminal feasibility failures prohibit downstream P&L use

## Chronology
- Development: 2021–2023
- Validation: 2024–2025
- Protected holdout: 2026

## Required outputs
- net, net50, net20, net20_50
- profit/trade and median trade
- win rate, worst/best trade
- chronological cumulative equity
- maximum drawdown in rupees
- peak-to-trough equity drawdown percentage
- explicit cross-checks against accepted totals

Capital-normalized return percentage is **not claimed** unless a consistent accepted capital/margin denominator is available.

## Scientific gates
1. All accepted baseline candidates must retain >=95% coverage and zero data errors.
2. OTM350 must be reconstructed with the frozen geometry and independently re-pass the same feasibility gate.
3. No additional parameter tuning is permitted.
4. 2026 HOLD cannot influence selection or inference.
5. After this finite phase, advance once to 50B-6 statistical inference.

## Current risks
The OTM350 artifact was computed in the prior 50B-4 Actions run but was not persisted because of a repository publication race. Phase 50B-5 therefore reconstructs it from the identical frozen engine as an artifact-recovery step, not a new optimization.


## Launch checkpoint — 2026-10-08
Trigger commit: `8202482c18393c07a03b5ec817d8dfad0f0e8306`.
Workflow: `.github/workflows/phase50b-5-chronological-validation.yml`.
The phase has been triggered; no numerical result is accepted until reconstruction, audit and chronology cross-checks pass.
