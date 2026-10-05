# Phase 32 Status

## Current state
**PHASE 32 INITIALIZED — numerical backtest not yet executed**

### Step 1 — repository/phase audit
- Confirmed repository: vishnuvcr/Final-Stand-v5-1-1-1
- Confirmed prior phases through Phase 31 exist as separate branches.
- Confirmed Phase 31 is complete/rejected and Phase 20 remains canonical.
- Confirmed Phase 31 used the corrected dynamic-n research dependencies and successful GitHub Actions execution.
- Confirmed this strategy is materially different from the prior delta-exit research and is therefore isolated as a new phase.

### Step 2 — branch creation
- Created branch: phase-32-continuous-delta-6x6-backtest
- Base: Phase 31 successful head.
- No prior research result has been modified.

### Step 3 — frozen specification
- Added PHASE32_RESEARCH_PLAN.md.
- Added PHASE32_PRE_REGISTRATION.md.
- Added PHASE32_STRATEGY_SPEC.md.

### Numerical execution
**CI setup is corrected; the second numerical attempt exposed implied-delta vectorization at the Black–Scholes helper level. Correction committed and retrying.**

### Errors
- The first local file-write wrapper attempt failed due to JavaScript quoting syntax; it was corrected before repository evidence was accepted.
- The error is recorded in `ERROR_LOG.md`.

- CI run 37380393437 failed before numerical execution: NumPy was absent from the runner.
- The push-triggered workflow also exposed empty optional input environment variables; the script now uses defaults when inputs are empty.
- CI run 37380443812 failed in implied-delta vectorization; correction is committed.

### Next registered phase step
Implement and audit the continuous trade state machine, then run the Phase-32 GitHub Actions workflow. Do not change the frozen strategy after observing numerical results.

### Step 4 — specification audit correction
- During execution audit, the first Phase-32 engine was found to exclude the last expiry of each month.
- This was inconsistent with the frozen rule current weekly expiry because the monthly expiry is also the current weekly contract for that week.
- No result from the affected runs is accepted.
- Corrected in commit d1b44be28b87b2d6a264cc6ddcd72d3a551a9a2f; corrected run 37383091606 is now the active numerical attempt.


### Step 5 — execution-convention audit correction
- The live specification includes a final-action window ending 120 seconds before the 15:30 market close.
- The 1-minute historical engine initially allowed fresh entries in the 15:28 and 15:29 bars.
- No result from runs using that behavior is accepted.
- Corrected the entry filter to reject timestamps at or after 15:28 IST; corrected engine commit 1513a1c00df8693ea630f6dae52d67a28164c1c7.


### Step 6 — chronological state-machine correction
- Audit identified a serious state-machine/lookahead bug: after selecting a future exit path, the previous loop could continue scanning entry timestamps that occurred before that exit.
- Corrected the engine to a single chronological cursor. After each trade, the next candidate entry begins strictly after the realized exit timestamp.
- A trade now occupies the timeline from its entry until its actual exit or contract termination; overlapping/impossible re-entry is prevented.
- Corrected commit: df8f9c0ca6e3fd3f84bcd6bd9c432f0b03ea171e.
- All earlier Phase-32 numerical runs remain invalid and will not be used.


### Step 7 — state-machine regression correction
- Corrected run 37384048259 failed immediately after the chronological rewrite because `run_expiry()` no longer assigned the option dataframe's `expiry_ts` field required by the delta-selection helper.
- No numerical evidence was produced.
- Restored `df["expiry_ts"] = expiry_ts` in commit 81b83fb4af8f075a9fec2bab42304a7c8964b45a.


### Step 8 — historical lot-size audit correction
- Audited the NIFTY contract-size schedule against NSE circulars.
- The previous engine treated the 2024-2025 transition too coarsely. The corrected schedule now reflects: 50-lot through the last pre-May-2024 weekly contract; 25-lot after the first revised weekly expiry on 02-May-2024; 25 through the last old weekly/monthly expiries in December 2024, with the first revised weekly expiry on 02-Jan-2025; the 30-Jan-2025 monthly expiry remains 25 while the first revised monthly expiry is 27-Feb-2025; 75 thereafter until the first 65-lot weekly expiry on 06-Jan-2026, with first revised monthly expiry 27-Jan-2026.
- Primary references: NSE circulars and their expiry-specific annexures; these are recorded in the phase research log.
- Corrected commit: a29a17470b751c947ba1aa0f8c7ed6d3abfc6e13.
- All numerical runs before this correction are non-evidence.


### Step 8 — zero-net direction-state correction
- Audit found that the implementation used `net>0` versus otherwise, which would flip direction after an exactly zero-net trade.
- The frozen state machine requires zero net P&L to preserve the current direction.
- Corrected commit: 559f520ba7feb795e2b09fd6ab17bfc083fd7ba0.
- The running candidate before this correction is not accepted as evidence.


### Step 9 — historical NIFTY lot-size correction
- NSE's 2024 contract-size revision requires weekly NIFTY contracts to use 75 from the 02-Jan-2025 revised weekly expiry, while the existing 30-Jan-2025 monthly contract remains at 25.
- The prior date-only lot-size function incorrectly assigned 75 to 30-Jan-2025.
- Corrected by adding the 30-Jan-2025 monthly exception.
- Corrected commit: 29458cacb40eab39cdd96c1b57881a70b1829b74.
- All runs before this correction remain non-evidence.
