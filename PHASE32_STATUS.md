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


### Step 9 — current-week expiry-window correction
- Audit found that the prior engine supplied each expiry with a 14-day spot window. This allowed a later-week option contract to be entered before that contract became the current weekly expiry.
- Corrected the engine to process each expiry only in the chronological window strictly after the previous expiry's contract termination and through the current expiry.
- The first available expiry is not used for entries because its preceding current-week window is outside the available dataset.
- Corrected commit: 1675f86b8a71add7a73c03479731e3a5623716b.
- All numerical runs before this correction are non-evidence.


### Step 10 — computational optimization without methodological change
- The exit delta inversion was vectorized across each complete future minute path.
- The mathematical inputs, first-hit rule, chronological state machine, execution model and cost model are unchanged.
- This optimization is required because the scalar minute-by-minute inversion risks exceeding the GitHub Actions timeout on the full historical sample.
- Corrected commit: c0ec4b90fd33eee75ed0515343e28d431aee924a.


### Step 11 — contiguous data-coverage correction
- The successful run #31 is rejected as numerical evidence because the public dataset contains incomplete expiry files and missing weekly contracts; later-week contracts were therefore not guaranteed to be the actual current weekly expiry.
- Added an NSE-consistent expected weekly expiry calendar: Thursday expiries through 28-Aug-2025 and Tuesday expiries for contracts expiring on/after 01-Sep-2025; holiday expiries use the previous observed NIFTY trading day.
- The primary engine now stops at the first missing expected expiry file or incomplete option/spot path and writes coverage.json.
- Corrected commit: a529ed4bd2519f2a47607ad53dd09ff522068c3b.
- Run #31 artifacts are retained for audit only, not accepted as primary performance evidence.


### Step 10 — July 2021 historical lot-size correction
- NSE Circular 28/2021 revised the July-2021 far-month NIFTY expiry to 50 lots while July weekly contracts otherwise retained the old lot until August weekly expiries.
- The engine's broad pre-August-2021 rule incorrectly assigned 75 to the 29-Jul-2021 monthly expiry.
- Corrected with an explicit 29-Jul-2021 exception at 50 lots.
- Corrected commit: d13af44516adec61ea0015eca2ab361fad5c9c2c.
- All earlier runs remain non-evidence.


### Step 12 — final historical expiry-calendar correction
- Corrected the expected NIFTY weekly expiry schedule for the 2025 transition: Thursday through 03-Apr-2025, Monday for contracts from 04-Apr-2025 through 28-Aug-2025, Tuesday from 01-Sep-2025 onward, with holiday adjustment to the prior trading day.
- This change cannot affect the accepted 2021 primary sample, but a final reproduction run will be used so the evidence and final engine revision are identical.
- Corrected commit: d9299e5b343a0bfdfe289b5e4065570b2ed86d99.


### Step 11 — expiry-coverage policy correction
- The successful run exposed an overly restrictive coverage rule: the engine stopped at the first missing expiry file (04-Nov-2021) even though later expiry files are present in the Hugging Face dataset.
- Corrected the engine to process all available expected weekly expiries, log each missing/incomplete expiry, and continue.
- Corrected the first-expiry window so the first weekly contract can use the valid seven-day pre-expiry trading window.
- Corrected commit: 977913fa176bc5c826bb00bcb5684e61bc6c912f.
- The previous successful numerical run is non-evidence for the final result because it truncated the sample at the first gap.


### Step 13 — calendar-boundary correction after gap continuation
- Run #39 demonstrated that continuing past missing expiry files is valid only if the next contract's historical window is anchored to the immediately preceding **expected calendar expiry**, not the last processed file.
- Corrected the engine so missing or incomplete option files do not enlarge the following contract's entry window.
- Corrected commit: cb0001f0e12376d27fa40b113ca47715a15c12cc.
- Run #39 is diagnostic only and is not accepted as final evidence.


### Step 14 — final numerical evidence and phase decision
- Final accepted engine revision: f89e1e5574aa26b69288ae93b9cf180bf9882242.
- Final accepted workflow: GitHub Actions run 37388261915 (run #41), completed successfully with artifact upload.
- Final artifact ID: 11380124540; SHA-256 c97657e5ec4acd4023e133e82cb586b242f030f7ef76985638fcdbcf0b84943.
- Final sample: 478 trades; net P&L ₹83,820.48; win rate 63.60%; profit factor 1.112; maximum drawdown ₹94,492.83.
- Coverage: 264 expected expiries, 239 available, 25 missing, one incomplete; 238 processed; last complete trade-producing expiry 19-May-2026.
- Statistical result: mean-trade bootstrap 95% CI approximately -₹156 to +₹494; t-test p≈0.293.
- Slippage sensitivity: 1 tick ₹83,820; 2 ticks ₹54,378; 3 ticks ₹24,936; 4 ticks -₹4,506.
- Decision under the preregistered promotion standard: **PROMISING BUT INSUFFICIENTLY ROBUST**.
- No Phase-32 strategy modification is promoted. Phase-20 remains canonical.
- Final manuscript: manuscript/PHASE32_CONTINUOUS_DELTA_MANUSCRIPT.md
- Final conclusion: results/dynamic_strategy_phase32/PHASE32_CONCLUSION.md
- Statistical summary: results/dynamic_strategy_phase32/PHASE32_STATISTICAL_SUMMARY.csv
