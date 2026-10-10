# Phase 60 research plan — evidence sufficiency and decision gate

## Research question
Given the accepted Phase 52–59 evidence, is there enough source-verified, contract-complete, executable-quality historical data to continue factor-conditioned option strategy efficacy testing without relaxing preregistered rules or inventing data?

## Aim
Make a bounded, auditable go/no-go decision for the next empirical phase, consolidating accepted results and explicit data/licensing constraints.

## Scope
- Read only committed reports and status records from Phases 52–59; do not redownload source data or scrape websites.
- Verify the 480-row Phase 52 ledger reconciliation and the Phase 54/56/57 conclusions.
- Preserve source provenance, license restrictions, frozen event universe, OI minimum, 2% OHLC range baseline, fees/slippage assumptions, chronological splits and untouched holdout.
- Keep the Phase 59 conclusion that no free, license-clear automated source has been verified for exact prior-minute OI plus historical bid/ask/depth.
- Decide whether a valid next empirical run is possible with currently accepted evidence.
- Record a finite restart condition; do not initiate paid access, use credentials, accept a license, or alter strategy rules.

## Hypotheses / decision rules
H0 (data-inadequacy): accepted evidence is insufficient for a defensible factor-conditioned profitability comparison.
Reject H0 only if all are true:
1. exact contract identity and timestamps are verified for the frozen events;
2. prior-minute OI is source-recorded and not imputed or coerced from missing to zero;
3. bid, ask, bid quantity and ask quantity are available at required entry/exit timestamps, or a separately preregistered alternative explicitly limits its claims to OHLC reference simulation;
4. license and automated cache/storage rights are documented;
5. coverage supports a meaningful development/validation sample without touching holdout;
6. costs include Paytm Money brokerage, statutory charges, slippage and stress cases;
7. independent reproduction and data-quality tests pass.

## Methodology
1. Validate required Phase 59 registry/report/status files and exact 10-source / zero-accepted-source counts.
2. Embed immutable cross-phase facts with run IDs and links: Phase 52 480-row baseline; Phase 54 11-threshold coverage sensitivity; Phase 56 modeled cost sensitivity; Phase 57 independent reproduction; Phase 58/59 source no-go.
3. Use deterministic assertions; no new P&L, no strategy ranking, no significance testing, no data download.
4. Emit a decision report, evidence matrix, restart checklist and run logs.
5. If the evidence gate fails, stop the empirical strategy-testing path and state precisely what evidence is needed to reopen it.

## Frozen facts carried forward
- Phase 52 baseline: 40 configurations × 24 events = 480 rows; 379 OHLC-range exclusions, 100 prior-OI eligibility blocks, 1 replay pass; only one baseline row executed.
- Phase 54 sensitivity: eligible rows at 2/3/4/5/6/8/10/12/15/20/1000% = 1/1/8/24/55/91/150/227/298/345/380. Coverage counts only, not profitability or spread evidence.
- Phase 56 cost-aware OHLC reference sensitivity produced 18,960 modeled scenario rows; five configuration-threshold pairs passed the severe-cost screen only at the 1000% diagnostic threshold. These are validation leads, not winners.
- Phase 57 independent reproduction matched 2,286 common scenarios to Phase 56 with zero mismatches in gross P&L, statutory fee components, total fees, net P&L and modeled return. This validates reproducibility of the same OHLC reference model, not executability.
- Phase 59 reviewed 10 source candidates and accepted zero free/license-clear exact prior-minute OI sources and zero exact quote/depth sources.
- The pinned options dataset declares CC BY-NC 4.0. It is not commercial/live-trading evidence.
- Holdout remains untouched; no factor selector or strategy is promoted.

## Statistical analysis
None in this gate. It is an evidence sufficiency decision, not an efficacy experiment.

## Acceptance criteria
- All embedded run links and parent source references are present.
- Source report and registry are internally consistent (10 candidates, zero accepted exact OI sources, zero accepted quote/depth sources).
- Report explicitly separates coverage from P&L and OHLC range from bid/ask spread.
- Tests pass and workflow persists report/status/research/error/chat/README records.
- If NO-GO, next empirical phase remains blocked until the restart checklist is satisfied.

## Finite restart checklist
- Obtain explicit authorization and documented license/storage/automation rights for a candidate feed, or identify a new free source with clear rights.
- Verify a small exact target-date sample before any bulk download: contract expiry, strike, CE/PE, timestamps 09:44/09:45/12:59/13:00/15:15 IST, OI provenance, and bid/ask/quantities if claiming execution quality.
- Verify complete coverage of the frozen target keys and independently hash/validate the sample.
- Only then preregister a new data-quality phase. Do not reuse holdout for source selection.
- If no qualifying source is available, stop empirical strategy efficacy work rather than relaxing gates or treating exclusions as losses.

## Status
Plan frozen before the automated decision-gate run. This phase is bounded and does not promote a strategy.
