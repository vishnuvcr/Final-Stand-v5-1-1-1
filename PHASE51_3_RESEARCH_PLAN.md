# Phase 51-3 Research Plan — Available-Data Strategy Sweep

## Research question
Among the frozen Phase-50B strategies that have eligible opportunities in the complete Phase-51 data endpoint (2026-04-21 through 2026-07-21), which strategies can produce auditable, source-faithful partial-OOS evidence without changing strategy rules?

## Aim
Use the available complete 2026 option interval for a strictly chronological, source-faithful diagnostic sweep while preserving the unresolved 2026-07-28 and 2026-08-04 boundary as missing data.

## Objectives
1. Reuse frozen Phase-50B replay engines without changing trading rules.
2. Restrict replay to 2026-04-21 through 2026-07-21.
3. Evaluate candidates independently; a no-opportunity candidate is non-informative, not a failure.
4. Require zero data errors and >=95% trade coverage before treating a candidate's P&L as auditable evidence.
5. Apply Paytm Money ₹10/order and ₹20/order scenarios plus +50% friction stress.
6. Preserve all raw artifacts and exclusions.
7. Do not promote a strategy from this partial window alone.
8. Record the missing 2026-07-28 and 2026-08-04 expiries explicitly.

## Frozen candidates
TT-02, TT-03, TT-04, TT-05, TT-06, TT-07 as registered in Phase 50B. Candidates whose engine requires unavailable data or has already reached terminal feasibility failure remain diagnostic only.

## Method
- Use the frozen source gate: rissin/nse-options-intraday / upstox_intraday/NIFTY/NIFTY_2026.parquet.
- Use cached Hugging Face data in Actions.
- Reuse the exact Phase-50B engines for eligible candidates; wrapper only changes the evaluation date bounds and output directory.
- No synthetic prices, interpolation, forward-fill, calendar reinterpretation, parameter tuning, or candidate re-selection.
- Preserve observed-LTP execution/slippage and registered cost functions.
- Coverage = completed candidate executions / candidate opportunities; target >=95%.
- Data-error count must equal zero for an evidence-grade result.

## Statistical analysis
This phase is descriptive/diagnostic. No confirmatory promotion test is permitted. For evidence-grade candidates report trade count, coverage, net P&L under four cost/stress scenarios, mean/median trade P&L, win rate, maximum drawdown where reconstructable, and chronological trade/equity tables.

## Decision rules
PASS_AVAILABLE_OOS: >=95% coverage, zero data errors, auditable artifacts.
NO_ELIGIBLE_CAMPAIGNS: zero opportunities.
FAIL_COVERAGE: <95% coverage.
DATA_ERROR: any unreconciled data errors.
No candidate is promoted from this phase.

## Stop rule
After the finite candidate set is evaluated, close the phase. Full Phase-51 remains pending until 2026-07-28 and 2026-08-04 are recovered through an authorized or otherwise accepted raw-data route.
