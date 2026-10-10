# Research Log — main branch

## 2026-10-03 — Phase 20 isolated runner trigger
- Added a temporary main-branch execution bridge that checks out only `phase-20-payoff-boundary-stop-research`, executes the pre-registered boundary-stop research, and persists outputs back to that phase branch.
- The strategy code and research artifacts remain isolated on the Phase-20 branch.
- Phase history and detailed step logs continue on the phase branch.
[RUN_PHASE20_BRIDGE]

## 2026-10-03 — Phase 20 optimized execution trigger
- Optimized Phase 20 to reuse the locked 190-trade ledger and NIFTY spot file, loading option files only for expiry dates capable of breaching the entry payoff boundary.
- Corrected strike-column access in the option-path reconstruction before triggering the run.
[RUN_PHASE20_BRIDGE_OPTIMIZED]


## 2026-10-03 — Main-branch Phase 20 final status
- Phase 20 payoff-boundary research completed on isolated branch `phase-20-payoff-boundary-stop-research`.
- Boundary-stop family rejected after negative validation and 2026 holdout results.
- Final historical exit rule: target → 13:30 expiry-day negative-MTM/MFE<0.50×target stop → 15:29 expiry fallback.
- Final historical result: ₹149,129.53 net P&L across 190 trades; 179/190 positive net trades; 5 conditional stops; 0 baseline-positive trades stopped.
- Canonical final rules: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/FINAL_STRATEGY_RULES.md
- Detailed Phase 20 log, errors and artifacts remain on the isolated research branch.


## Final research closeout — 2026-10-03
- Phase 23 complete; no OOS strategy adjustment promoted.
- Phase 24 complete; no reversal trigger promoted.
- Final strategy remains the Phase-20 canonical dynamic-n specification.
- Final manuscript and evidence package are retained on branch phase-24-targeted-reversal-trigger.


## 2026-10-04 — Phase 27 final status
- Phase 27 delta-based exit research completed on isolated branch `phase-27-delta-exit-research`.
- Training-selected delta profit rule: MTM ≥ 0.90×target and |portfolio delta| ≤ 0.05.
- Validation uplift: −₹2,334.04. 2026 holdout uplift: −₹1,108.04.
- Holdout bootstrap 95% CI for mean trade-level uplift: −₹141.92 to −₹13.82.
- No adverse-delta stop selected.
- **No Phase-27 rule promoted; Phase-20 remains canonical.**


## Phase 28 — individual-leg delta research — COMPLETE — 2026-10-04

Phase 28 tested S1=short OTM-(n+1) and S2=short OTM-(n+2) deltas independently. Coverage was 99.21%. The least-bad training rule was S1 |delta|≤0.05 after 90% target, but it lost ₹2,998.16 training, ₹2,487.05 validation and ₹35.91 in the 2026 holdout. No adverse short-leg delta stop passed. **No promotion; Phase-20 remains canonical.**


## 2026-10-05 — Phase 29 complete: short-leg delta-change exits
- Tested target and stop entirely from individual/combined short-leg delta change; removed target-percentage criteria.
- Delta coverage 99.21%; 480 preregistered rules.
- Training-selected target: MEAN, 5-minute, 0.20 threshold, 3-minute confirmation.
- Training-selected stop: S1, 1-minute, 0.05 threshold, 3-minute confirmation; zero uplift.
- Versus canonical Phase 20: +₹18,251.49 training, −₹1,092.14 validation, −₹6,879.84 2026 holdout, +₹10,279.51 full.
- **Decision: no promotion; Phase 20 remains canonical.**
- Artifacts persisted on the Phase-29 branch.


## 2026-10-06 — Phase 41 active interim status
- Isolated branch phase-41-regime-conditional-policy-learning created from Phase 40.
- The registered fixed-opportunity screen completed successfully: 24 variants evaluated; zero passed the validation safety screen.
- The top three diagnostic policies produced zero overrides across development, validation and the frozen 2026 fixed panel.
- Exact sequential identity validation remains the registered closing step.


## 2026-10-06 — Phase 41 final closeout
- Phase 41 completed with 24 pre-registered regime-conditional economic-margin variants.
- No variant passed the validation safety gate; the top three frozen diagnostics all had zero overrides across the full development/validation/2026 counterfactual panel.
- Exact sequential replay was completed by the registered identity/no-op audit and matched the canonical control exactly: zero validation and holdout uplift, zero overrides, p=1.0000.
- **Decision: no promotion. Canonical stateful strategy remains unchanged.**


## 2026-10-06 — Phase 42 closeout published to main
- Accepted numerical workflow: 37470344620.
- 72 preregistered variants screened; 2 passed development/validation selection.
- Primary sequential policy: SPLINE_RIDGE_VIX + RAW + ₹500 + ALL; +₹26,542.28 validation uplift and +₹20,607.09 2026 holdout uplift.
- Holdout paired-expiry 95% CI for mean uplift crossed zero (−₹2,020.42 to +₹4,297.35); one-sided sign-flip p=0.3054.
- Final decision: no promotion; canonical stateful strategy unchanged.


## 2026-10-06 — Phase 43 registered
- Created isolated branch `phase-43-vix-all-options-strategies` from the Phase-42 research head.
- Registered the finite VIX-conditioned NIFTY strategy universe, point-in-time VIX regimes, Paytm Money cost model, development/validation/untouched-2026 holdout design, router selection and 10,000-resample inference.
- Canonical Phase-20/42 strategy remains unchanged pending a separately accepted Phase-43 result.
- Initial implementation-writing incident F43-001 was logged on the Phase-43 branch; no numerical evidence was affected.


## 2026-10-06 — Phase 43 final closeout published
- Phase 43 completed on isolated branch `phase-43-vix-all-options-strategies`.
- 22 strategy families / 4,597 observations / 262 expiry opportunities evaluated under point-in-time India VIX and realistic execution costs.
- Corrected regime inference found no Holm-adjusted significant VIX advantage.
- Corrected promotion universe restricted to defined-risk strategies; zero strategy×VIX candidates and zero routers passed the full gate.
- Stage 5 active-exit optimization skipped.
- **Final decision: NO PROMOTION; canonical Phase-20/42 strategy unchanged.**
- Final manuscript: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-43-vix-all-options-strategies/PHASE43_MANUSCRIPT.md


## 2026-10-06 — Phase 44 VIX candidate tuning initialized
- Created isolated branch `phase-44-vix-candidate-tuning` from completed Phase 43.
- Registered finite tuning of six defined-risk Phase-43 candidates using strike geometry, entry time and prior-only VIX percentile profiles.
- The 2026 holdout remains protected until validation/inference freezing.
- Automated branch workflow and main execution bridge registered.
- Initial implementation audit F44-001 was logged and quarantined before evidence acceptance.


## 2026-10-06 — Phase 44 corrected numerical execution
- F44-002 and F44-003 were corrected before accepting any numerical evidence.
- The active Phase-44 run now uses the optimized corrected engine with development-only candidate freeze, validation-only confirmation and 2026 holdout protection.


## 2026-10-06 — Phase 44 active corrected run
- Current numerical run: **37488148310** after F44-005 bounded-memory correction.
- No Phase-44 numerical result has been accepted yet; holdout protection remains active until validation/inference freeze.


## 2026-10-06 — Phase 44 active run update
- Current corrected Stage-1 execution is run **37491292566**.
- No Phase-44 result is accepted yet; 2026 holdout protection remains in force.


## 2026-10-06 — Phase 44 staged execution
- Phase 44 was converted from a monolithic numerical run to development → validation → holdout execution.
- Current corrected development run: **37496337984** after F44-013.
- Premature validation/holdout attempts were classified as failures/non-evidence and logged.
- 2026 holdout remains protected.


## 2026-10-06 — Phase 44 final closeout
- Completed corrected VIX candidate tuning and validation under the registered chronological and cost model.
- No candidate survived the validation inference gate.
- Final decision: **NO PROMOTION**.


## 2026-10-07 18:15 IST — Phase 50B continuation
- Resumed from the accepted TT-03 V5 PASS.
- Live TT-04 run 37621965843 was rechecked; preflight passed and numerical replay remained in progress.
- Re-read TT-04 source audit/workflow/engine at the active run head. No new evidence-impacting defect was identified.
- No TT-04 numerical result is accepted until the artifact audit passes.


## 2026-10-09 — Phase 51-1 source-gate closeout
Phase 51-1 stopped fail-closed on data availability before any fresh OOS strategy P&L. Frozen OOS: 2026-04-21 to 2026-08-04. Validated spot source: technovusin/nifty50-historical-data. Primary option source reaches only 2026-07-21. Tested thetrademarkk supplemental option source failed endpoint and common-expiry coverage. Upstox authenticated recovery workflow 37839447686 was blocked because UPSTOX_ACCESS_TOKEN is not configured. No strategy promotion or OOS inference was made.


## 2026-10-09 — Phase 51-2 partial-data calendar audit closeout
- Separate branch `phase-51-2-available-data-partial-oos` was used so the incomplete full-window data gate was not silently relaxed.
- Final accepted Actions run: **37847094909**.
- Frozen available option interval: 2026-04-21 through 2026-07-21; 14 observed expiries.
- Both frozen TT-03 BASE (300/350/400) and OTM350 (350/400/450) had 0 eligible campaigns because the frozen entry rule is exactly three calendar days before expiry and every observed expiry in this interval is Tuesday, making the scheduled entry date Saturday.
- Result: no P&L, no inference, no ranking, no promotion. Phase 51 remains blocked on 2026-07-28 and 2026-08-04 option coverage.


## 2026-10-11 — Phase 102 checkpoint
- Published and audited [Phase 102 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-102-final-strategy-ranking); final workflow [38082303704](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38082303704) passed 14/14 evidence invariants and 2/2 unit tests.
- TT-03 dynamic-N V5 is the only high-priority revalidation candidate, not a live recommendation: the hold split has three trades. TT-04/05 fail temporal-stability evidence; U02/U05 results do not support their tested implementations; no candidate was promoted.
- The full plan, scorecard, report, validation JSON and phase logs are linked in the main README. No new market data were downloaded or holdout tuned.


## 2026-10-11 — Phase 103 Dhan stock-options research registered

- User requested a separate five-stock NIFTY constituent options study while keeping prior research/data frozen. Created isolated branch `phase-103-nifty50-stock-options` from `main`; prior result artifacts are not modified.
- Initial stock basket: HDFCBANK, ICICIBANK, RELIANCE, SBIN, INFY. Selection is based on an official constituent-weight snapshot dated 2026-02-27 and option-contract discovery, not a claimed synchronized top-five average-option-volume rank.
- User requested the Dhan data API access token as the data source. Added secret-based Dhan expired-options API client and a 30-day smoke test (ATM monthly CE/PE for all five names), instrument-master ID resolution, focused unit tests, aggregate-only results, and status/error-log automation. No credential or raw API rows are published.
- The Dhan API workflow is bridged from the default branch to permit manual dispatch, and the Phase 103 branch remains the checkout/commit target. [Launch bridge](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/main/.github/workflows/phase103-dhan-data-api-bridge.yml) · [Phase 103 plan/status/logs](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-103-nifty50-stock-options).
- The live API result has not been confirmed in the available tool results at this checkpoint. Do not claim Dhan data was successfully acquired until a run artifact exists. Dhan's endpoint returns rolling-strike OHLC/IV/volume/OI/spot but not documented historical bid/ask/depth, so contract continuity and executable fills remain explicit gates.



## 2026-10-11 — Dhan API live probe and parameter correction

- The first executed Dhan API smoke test, [run 38088524054](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088524054), passed the unit tests, downloaded the 26,116,616-byte instrument master (SHA-256 `2d962ddbd2681df30f08032f8b355aae50595b7a5a289d7e280c7eb558ca1173`), and resolved HDFCBANK, ICICIBANK, RELIANCE, SBIN and INFY. The ten expired-options requests returned HTTP 400 with `DH-905: expiryCode is required`; no option rows were returned.
- The request incorrectly appeared to be missing `expiryCode: 0` to the provider. Its annexure lists zero as current/near expiry, but the request example uses `1` (next expiry). Code and registry were updated to test `expiryCode: 1`, with an additional unit test. Retry [run 38088625181](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088625181) was initiated with safe allow-listed error diagnostics.
- The result is pending until the retry report is persisted. No strategy P&L or success conclusion is drawn. All raw option rows remain unpublished pending retention/republication-rights verification.
