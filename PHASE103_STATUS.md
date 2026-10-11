# Phase 103 Status — NIFTY 50 Constituent Stock Options

**Updated:** 2026-10-11  
**Branch:** `phase-103-nifty50-stock-options`  
**State:** PHASE 103.1B IN PROGRESS; MULTI-SESSION AUDIT LIMITED TO FOUR PREVIOUSLY PASSING STOCK/SIDE PANELS; NO STRATEGY P&L YET  
**Strategy promotion:** NONE  
**Previous research:** frozen; no previous-phase data or conclusions changed.

## Phase checklist

- [x] Read the current Phase 102 final status, plan, README checkpoint and repository logs.
- [x] Create isolated Phase 103 branch from `main`.
- [x] Register bounded research question, aims, objectives, gates, metrics and stop rule.
- [x] Select and source five initial stocks: HDFCBANK, ICICIBANK, RELIANCE, SBIN, INFY.
- [x] Record that this is an initial research basket, not a proven top-five option-volume ranking.
- [ ] Run registration workflow and verify its automated checks.
- [x] Phase 103.1A: first-session Dhan screen completed; 68/70 offset probes returned rows, with four of ten stock/side alignment gates passing.
- [ ] Phase 103.1B: multi-session audit of ICICIBANK CALL, RELIANCE CALL/PUT, SBIN CALL from 2026-08-03 inclusive to 2026-08-10 exclusive (28 probes maximum).
- [ ] Phase 103.2: canonical contract/data and execution-cost audit.
- [ ] Phase 103.3: preregister candidate rules and baselines.
- [ ] Phase 103.4: chronological development and validation.
- [ ] Phase 103.5: frozen independent test with date-effective costs.
- [ ] Phase 103.6: sealed stock-options holdout and evidence gate.
- [ ] Phase 103.7: final manuscript and bounded closeout.

## Selected stocks

1. HDFCBANK — HDFC Bank
2. ICICIBANK — ICICI Bank
3. RELIANCE — Reliance Industries
4. SBIN — State Bank of India
5. INFY — Infosys

The exact reason, weight snapshot and public contract discovery links are in `research/phase103_stock_options/stock_universe.json` and `results/phase103/STOCK_UNIVERSE_SELECTION.md`.

## Current finding

The first-session historical data screen is complete. Four stock/side panels passed relative-surface alignment on 2026-08-03: ICICIBANK CALL, RELIANCE CALL, RELIANCE PUT and SBIN CALL. The next bounded experiment extends only those panels across multiple sessions. HDFCBANK CALL/PUT, ICICIBANK PUT, SBIN PUT and both INFY sides are excluded from this run because their first-session alignment/coverage gate failed. No stock-options strategy has been backtested, ranked or promoted yet.

## Next action and stopping rule

Run the bounded multi-session audit on the four eligible stock/side panels. Strategy P&L remains blocked until exact fixed-contract/expiry identity, source rights, and realistic Paytm Money brokerage/tax/spread/slippage inputs are documented. If those gates cannot be passed, produce a source-specific NO-GO rather than fabricate fills.


## Dhan API integration — 2026-10-11

- [x] DhanHQ expired-stock-options API chosen as the primary Phase 103.1 historical option source.
- [x] Secure secret-based integration implemented in the isolated branch; the token is never emitted to logs or result artifacts.
- [x] Bounded smoke-test workflow added with automatic branch-push and manual dispatch triggers.
- [x] Workflow tests added for the 30-day request limit, fresh instrument ID mapping, array integrity and authentication error handling.
- [ ] Confirm live GitHub Actions result and whether the configured repository secret is accepted by Dhan.
- [ ] If endpoint succeeds, assess comparable sample coverage and strike/expiry reconstruction. No strategy P&L test until data and execution gates pass.

API probe default window: 2026-08-02 inclusive to 2026-09-01 exclusive. This is a source feasibility window only, not a protected performance holdout. Dhan's endpoint returns rolling strike OHLC/IV/volume/OI/spot, not documented historical bid/ask/depth. No raw rows are committed or uploaded until data storage/redistribution permissions are verified.


<!-- DHAN_API_RUN_38088253613 -->
### Dhan audit did not produce output
Run 38088253613 failed before a machine-readable result was written; inspect its Actions log. No API success or strategy result is claimed.


<!-- DHAN_API_RUN_38088262635 -->
### Dhan audit did not produce output
Run 38088262635 failed before a machine-readable result was written; inspect its Actions log. No API success or strategy result is claimed.

 
## Failed preflight runs — resolved code defect, Dhan still untested
Runs [38088253613](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088253613) and [38088262635](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088262635) stopped at the unit-test step because a source-rights validator assertion was too literal. The validator is corrected and additional response-summary tests were committed to trigger a clean retry. **Neither run queried Dhan; no data access conclusion can be drawn from them.**

<!-- DHAN_API_RUN_38088386046 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38088386046 — 2026-10-10T21:38:40.601895+00:00

- **Result:** NO_DATA_RETURNED_OR_SCHEMA_MISMATCH.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38088499642_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38088499642, attempt 1 — 2026-10-10T21:40:38.031865+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38088524054_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38088524054, attempt 1 — 2026-10-10T21:41:06.132469+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## Dhan expiry-code parameter correction

The first API request reached Dhan but all 10 probes returned HTTP 400 `DH-905: expiryCode is required` because the provider apparently rejected the value 0 as missing. The script and machine-readable manifest now use `expiryCode: 1` (Next Expiry, matching the official sample request) for a bounded retry. Awaiting the retry result. This change affects data acquisition only; there is still no accepted data sample or strategy test.

<!-- DHAN_API_RUN_38088597286_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38088597286, attempt 1 — 2026-10-10T21:42:20.727955+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38088846052_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38088846052, attempt 1 — 2026-10-10T21:45:46.027177+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.



## Current bounded retry — run 38088846052
The earlier 30-day/10-probe request was cancelled before it produced a derived report; it is not accepted as a failed market-data observation. The active launch [run 38088846052](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088846052) reduces the initial diagnostic to one session and one HDFCBANK CALL request using `expiryCode: 1`. The next gate is a safe aggregate response; no strategy backtest is running.

<!-- DHAN_API_RUN_38088975571_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38088975571, attempt 1 — 2026-10-10T21:47:54.152267+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089043087_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089043087, attempt 1 — 2026-10-10T21:48:48.952462+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089057160_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089057160, attempt 1 — 2026-10-10T21:49:02.855491+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089084020_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089084020, attempt 1 — 2026-10-10T21:49:47.179010+00:00

- **Result:** DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089152325_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089152325, attempt 1 — 2026-10-10T21:50:42.137495+00:00

- **Result:** DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## Date-boundary gate — latest result

The latest accepted API smoke result currently remains a **data-boundary NO-GO**, not a source-access NO-GO: authentication worked and the API returned data, but 385 of 770 timestamps were on the non-requested end date. The equal-date diagnostic is now registered with default probe limit 1. Do not advance to all five stocks or strategy P&L until the query-boundary behavior is documented and deterministic timestamp filtering is tested.

<!-- DHAN_API_RUN_38089220578_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089220578, attempt 1 — 2026-10-10T21:51:44.041591+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-03 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## Date-boundary resolution and next data gate — 2026-10-11

- The same-date endpoint diagnostic [run 38089220578](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089220578) returned 385 HDFCBANK CALL rows only on 2026-08-03.
- Combined with the earlier [out-of-window result 38089152325](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089152325), the evidence indicates the Dhan endpoint treats its `toDate` as inclusive despite the current documentation describing it as non-inclusive.
- Acquisition now translates the fixed research target `[start,end)` into provider `fromDate=start`, `toDate=end-1 day`, and checks timestamps against the original half-open window. No extra-date rows may be accepted.
- Next run: all five frozen stock symbols × CALL/PUT, one common IST session (2026-08-03), using ten bounded API requests. This validates one-day cross-stock/side coverage only; it does not establish full-history coverage or strategy profitability.

<!-- DHAN_API_RUN_38089336359_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089336359, attempt 1 — 2026-10-10T21:53:28.424115+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-03 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## Corrective workflow gate — 2026-10-11

Run [38089336359](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089336359) is rejected: unit tests failed before any Dhan request; no data inference from it. The current workflow now clears stale output files before tests and validates that any JSON written belongs to the active Actions run. The date-adapter import is corrected. Await the next all-ten-probe run before accepting cross-stock sample availability.

<!-- DHAN_API_RUN_38089393338_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089393338, attempt 1 — 2026-10-10T21:55:03.773246+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 10/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


<!-- DHAN_NO_RESULT_RUN_38089656281 -->
### No fresh Dhan audit result
Run 38089656281 produced no current-run JSON; prior run output was not accepted.


## Latest accepted gate — 2026-10-11

**PASS: Dhan API retrieval for all five stocks and both option sides on one common IST session.** Run [38089393338](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089393338) passed 13 tests and all 10 data requests for 2026-08-03. Each probe returned 385 rows, array lengths were consistent, all timestamps fell inside the target day, and zero rows were outside the request window. Raw minute rows were not persisted or uploaded.

This is a one-day source-access/coverage PASS only. No fixed-contract strategy P&L test has begun. Next: seven-offset relative-strike surface audit across all five stocks and CALL/PUT, then assess fixed-contract continuity and common-window coverage.


## Strike-surface retry — preflight correction
Runs [38089656281](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089656281) and [38089669894](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089669894) failed at unit tests because the new summarizer signature was not reflected in older test calls. No Dhan API calls were made. Updated tests and workflow input schema; next run will use seven relative strikes and 70 probes only after all tests pass.

<!-- DHAN_API_RUN_38089913649_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38089913649, attempt 1 — 2026-10-10T22:03:09.668123+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 7/7.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## Latest run — seven-offset HDFCBANK CALL surface

Run [38089913649](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089913649): tests and 7/7 API calls passed. HDFCBANK CALL offsets all returned HTTP 200 for 2026-08-03; 6 offsets returned 385 rows, ATM-3 returned 384. No out-of-window rows or duplicate timestamp/actual-strike keys were found. Six actual strikes covered all 385 timestamps. However, the strict full-offset alignment gate is FAIL because only 384 timestamps were common to all seven offsets. This is a partial fixed-strike coverage finding, not a complete data-integrity PASS and not profitability evidence.

Next: run the same offsets across all five stocks and both CALL/PUT sides, record each fixed-strike's exact coverage, and keep any missing rows missing. No strategy P&L until option contract identity, multi-date coverage and realistic execution assumptions pass.

<!-- DHAN_API_RUN_38090070197_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38090070197, attempt 1 — 2026-10-10T22:05:28.989814+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 7/7.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38090149633_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38090149633, attempt 1 — 2026-10-10T22:08:14.651375+00:00

- **Result:** PROBE_ABORTED_AFTER_FIRST_INVALID_RELATIVE_STRIKE.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 59/60.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## 2026-10-11 — Invalid-strike continuation fix

- [x] Diagnosed the latest expanded run: [38090149633](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38090149633) reached the API and returned 59/60 probes before an empty/invalid INFY CALL ATM+3 side payload caused the whole run to stop.
- [x] Updated the summarizer to distinguish a successful but empty requested-side payload from an HTTP/schema failure.
- [x] Changed the probe loop so empty-side observations are recorded and the frozen universe continues; HTTP failures and malformed non-empty arrays still stop the run.
- [x] Added a unit test for the empty-side status.
- [x] Corrected the workflow's duplicated `--strikes` argument and set the automatic bounded audit default to 70 probes, so the full five-stock × two-side × seven-offset panel is attempted.
- [ ] Verify the new automated run, exact coverage, and all unit tests before accepting the surface audit.
- [ ] No strategy P&L until the expanded surface audit, multiple-session continuity, source rights and execution-cost gates pass.

**Current gate:** remediation committed; the rerun is pending verification. A successful HTTP request with no requested-side rows is a missing-coverage observation, not a pass. Previous failed/partial results remain in the record and are not overwritten.


**Integrity refinement:** the abort condition now exempts only the explicit `SUCCESS_EMPTY_FOR_REQUESTED_SIDE` status. Any other inconsistent arrays, including zero-timestamp/mismatched non-empty arrays, remain an integrity failure. The accepted audit JSON still belongs to run 38090149633; no post-fix run result has yet been verified.


## 2026-10-11 — Regression test entrypoint correction

The empty-side continuation regression class was located after the `unittest.main()` guard, so direct execution of the test file would not discover that class. Moved the guard to the end of the file in commit `f0973d5c66a10bf84dc10a2593849827a45c3dba`. This test-file push should trigger the branch audit workflow. **No post-fix run result is verified yet; the data gate remains pending.**


## 2026-10-11 — Latest continuation checkpoint

The previous audit JSON still belongs to run `38090149633` (59/60 probes; `PROBE_ABORTED_AFTER_FIRST_INVALID_RELATIVE_STRIKE`) and is not accepted as post-fix evidence. The regression test entrypoint was corrected in commit `f0973d5c66a10bf84dc10a2593849827a45c3dba`; the status and error logs now record that correction. The available GitHub integration returned no commit status checks, and no workflow-dispatch action is exposed in this session, so a fresh run could not be directly triggered or verified here. Next step is to inspect the Actions page for the push-triggered run, verify unit tests and the complete probe panel, then proceed only if multi-session contract continuity and execution-cost gates pass. No strategy P&L or promotion.

<!-- DHAN_API_RUN_38113895829_ATTEMPT_2 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38113895829, attempt 2 — 2026-10-11T05:23:53.395084+00:00

- **Result:** PARTIAL_DATA_RETURNED.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 68/70.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

## 2026-10-11 — Multi-session audit scope

- Selected only panels that passed the prior one-session alignment screen: ICICIBANK CALL, RELIANCE CALL, RELIANCE PUT, SBIN CALL.
- Excluded panels with failed first-session coverage/alignment gates from this run; exclusions are not treated as strategy failures or profitability evidence.
- Configured a bounded seven-calendar-day window (2026-08-03 inclusive to 2026-08-10 exclusive), respecting Dhan's documented 30-day limit and covering several sessions.
- Added a safe response-envelope summary of keys, status class, side type, and field shapes; raw market values and credentials remain excluded.
- This remains a data availability/continuity test, not strategy P&L. Exact contract/expiry identity and data rights must be established before performance inference.

<!-- DHAN_API_RUN_38115153795_ATTEMPT_1 -->
### Latest Dhan API data gate

## Dhan Data API audit — run 38115153795, attempt 1 — 2026-10-11T05:35:27.705114+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-10 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 28/28.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.
