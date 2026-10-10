# Phase 84 Decision Report — Cross-phase evidence reconciliation

Date: 2026-10-10
Status: Synthesis in progress; source-backed matrix initialized.

## Executive decision

**No strategy is newly approved for promotion by Phase 84.** The repository contains several distinct classes of evidence which must not be collapsed into a single “best strategy” ranking:

1. The Phase 83 static-structure experiment is terminal and found no defined-risk candidate passing its registered gate.
2. The Phase 38 canonical stateful control remains the accepted historical comparator; its alternative model overlays were rejected because paired differences favored the control and confidence intervals crossed zero.
3. TT-04 and TT-05 had positive descriptive results in Phase 51-3, but only over a partial window with two unresolved sessions. That does not satisfy the full registered OOS requirement or authorize live use.
4. Phase 52 factor-conditioned pilot coverage and Phase 66 CCI reconstruction did not yield adequate completed-trade samples for profitability inference.

## Evidence matrix

See [evidence_matrix.csv](evidence_matrix.csv). Figures retain their original source assumptions and units; raw P&L across these studies is not a valid cross-study ranking because the strategy definitions, periods, sample sizes, and execution assumptions differ.

## Reconciliation findings

### 1. Phase 83 is a terminal no-go for its registered universe

The Phase 83 manuscript and status report 11,163 matched comparisons across 238 expiry clusters. No primary test survived Holm correction and no defined-risk variant/horizon passed the candidate gate. The 2026 holdout remains sealed. This result does not prove every options strategy is unprofitable and does not invalidate unrelated canonical strategy findings.

### 2. Canonical control findings remain separate

Phase 38 retained the frozen stateful control (206 trades, 102 expiry blocks, net ₹63,672.58, maximum drawdown ₹61,960.87). Five corrected model selectors had negative mean paired differences on 93 common expiry blocks and all bootstrap intervals crossed zero. None was promoted. The control's historical total cannot be compared directly with Phase 51 or Phase 83 totals without harmonized periods, capital, and execution models.

### 3. Positive partial-OOS totals are not promotion evidence

Phase 51-3 reports TT-04 at +₹13,271.51 and TT-05 at +₹17,098.15 at the ₹10/order scenario; both stayed positive in its four registered cost/friction scenarios. However, this sample only extends through 2026-07-21, while 2026-07-28 and 2026-08-04 remain missing from the full registered window. It is descriptive evidence, not a completed confirmatory OOS result. No promotion is justified.

### 4. Do not repeat source probes or manufacture a profitability result

The existing README records a Phase 59–61 source-sufficiency no-go and later bounded probes (Phases 71–76) into missing-date data and contract identity. This phase does not repeat those probes. Reopen historical replay only if a genuinely new source has documented automated-use/storage/publication rights and exact target-date, expiry, strike, side and timestamp identity. Execution-quality claims additionally require historical bid/ask and size/depth, not OHLC or LTP alone.

## Recommended next research step

The next *numerical* experiment should be conditional, not automatic:

- **Gate A — source rights:** documented permission for automated research, retention/caching, and the intended publication of derived results.
- **Gate B — exact identity:** independently validated target-session coverage and fixed expiry/strike/side mapping for every required event.
- **Gate C — execution quality:** if claiming executable performance, quote/depth data and a frozen fill model with Paytm Money brokerage, statutory charges, adverse slippage and latency sensitivity.
- **Gate D — preregistration:** only after A–C pass, create a finite new branch with frozen questions, sample window, outcomes, statistical family, cost scenarios, and stop rules.

If any gate fails, stop and record the blocker; do not tune around missing data, treat missing observations as losses, or open the sealed Phase 83 holdout. This is a conditional research plan, not a strategy recommendation.

## Scope and limitations

This phase is a synthesis of repository artifacts, not a new backtest, literature search, or independent reproduction of raw numerical results. The reported numbers are source-derived and were not recalculated from trade-level data here. A single cross-study winner is intentionally not named. Phase 84 completes only after all links and source figures are validated and the README/status/error log are synchronized.
