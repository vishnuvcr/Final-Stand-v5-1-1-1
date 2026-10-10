# Phase 103 Status — NIFTY 50 Constituent Stock Options

**Updated:** 2026-10-11  
**Branch:** `phase-103-nifty50-stock-options`  
**State:** PHASE REGISTERED; STOCK UNIVERSE SELECTED; DATA/ACTION RESEARCH NOT YET RUN  
**Strategy promotion:** NONE  
**Previous research:** frozen; no previous-phase data or conclusions changed.

## Phase checklist

- [x] Read the current Phase 102 final status, plan, README checkpoint and repository logs.
- [x] Create isolated Phase 103 branch from `main`.
- [x] Register bounded research question, aims, objectives, gates, metrics and stop rule.
- [x] Select and source five initial stocks: HDFCBANK, ICICIBANK, RELIANCE, SBIN, INFY.
- [x] Record that this is an initial research basket, not a proven top-five option-volume ranking.
- [ ] Run registration workflow and verify its automated checks.
- [ ] Phase 103.1: common-window options data access/licence/coverage/liquidity audit.
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

Only the universe-registration stage is complete. No historical stock-options data have yet been downloaded or evaluated; no options strategies have been backtested, ranked or promoted. The next critical gate is a rights-aware, comparable data/liquidity audit. Current public contract pages are exploratory leads, not proof of historical data adequacy.

## Next action and stopping rule

Run the registration validator and GitHub Actions workflow. Then begin Phase 103.1 only with exact source rights and common-window coverage evidence. If no eligible source can support the required historical sample, stop the empirical path with a NO-GO report rather than repeatedly searching unchanged sources, loosening gates, or fabricating fills.


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
