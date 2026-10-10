# Phase 103 Research Log

## 2026-10-11 — Initialization

- User requested a separate branch to research successful options strategies in NIFTY 50 stocks, with five stocks selected initially.
- Checked the main README and current repository research/error logs, and verified Phase 102's completion. Phase 102's accepted conclusion remains that no strategy is approved for live trading.
- Created branch `phase-103-nifty50-stock-options` from `main`, keeping earlier research branches and artifacts unmodified.
- Read Phase 102 plan/status and its conversation/error logs before registering the new phase.
- Preregistered a bounded plan covering stock universe freeze, source/rights/data feasibility, contract integrity and transaction costs, baseline/candidate definition, chronological validation, independent test, sealed holdout, inference, final manuscript and stop rules.
- Chosen initial basket: HDFCBANK, ICICIBANK, RELIANCE, SBIN, INFY. Rationale combines a published official NIFTY 50 constituent-weight snapshot with visible exchange/market pages showing stock-option contract discovery/activity. This is **not** asserted to be a comparable top-five ranking by average option volume. Phase 103.1 must calculate liquidity metrics over a common observation window, before viewing strategy P&L.
- Evidence leads: official NIFTY 50 snapshot (as of 2026-02-27), NSE index/derivatives pages, and stock-specific stock-option pages. The public pages differ in their last data timestamp and do not, alone, demonstrate an adequate licensed historical sample.
- No raw market data downloaded, no holdout opened, no strategy code run and no profitability claim made.
- Next step: add registration manifest/validator/unit tests and a manual/branch-push Actions workflow; then run it to validate the registry.


## 2026-10-11 — Dhan Data API integration

- User explicitly requested use of the Dhan Data API access token for this new stock-options study.
- Verified official Dhan documentation for historical rolling expired stock-options, the five-year lookback description, 30-day per-call limit, supported option fields, relative-strike limitations, and official instrument-master CSV.
- Added secure GitHub Actions secret lookup via common secret-name aliases. Only the secret reference is in code; token values are not printed, committed or uploaded.
- Added a bounded 10-probe sample: five stock underlyings x ATM monthly CALL/PUT over a common 30-day historical window. Instrument IDs are resolved from a fresh Dhan master download, not hardcoded.
- Added derived-only audit outputs and automatic status/error logging on the research branch. Raw payloads remain ephemeral until applicable retention and republication rights are verified.
- Local validation of the Python code and four focused unit tests passed before committing; Dhan network response is pending the GitHub Actions run.
- No strategy rules, P&L, stock ranking by outcome or holdout use is part of this step.


<!-- DHAN_API_RUN_38088253613 -->
## Dhan API audit did not produce output — run 38088253613
The workflow failed before a machine-readable result was written. No source/data success is claimed.


<!-- DHAN_API_RUN_38088262635 -->
## Dhan API audit did not produce output — run 38088262635
The workflow failed before a machine-readable result was written. No source/data success is claimed.

 
## 2026-10-11 — Dhan workflow preflight correction

- Reviewed job logs for runs 38088253613 and 38088262635. The repository secret was present but masked; the Python test step failed before the Dhan HTTP request, so no authentication or historical-coverage result was produced.
- Root cause: source-rights registration test had false-negative string matching. Corrected to substring-match the registered metrics and added tests for empty side blocks and output-summary safety.
- Preserved both failed runs and the fallback-logging defect in E103-006/E103-007; fixed bridge printf handling in commit 52565b4. Next evidence must come from a new run that reaches the Dhan request step.

<!-- DHAN_API_RUN_38088386046 -->
## Dhan Data API audit — run 38088386046 — 2026-10-10T21:38:40.601895+00:00

- **Result:** NO_DATA_RETURNED_OR_SCHEMA_MISMATCH.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38088499642_ATTEMPT_1 -->
## Dhan Data API audit — run 38088499642, attempt 1 — 2026-10-10T21:40:38.031865+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38088524054_ATTEMPT_1 -->
## Dhan Data API audit — run 38088524054, attempt 1 — 2026-10-10T21:41:06.132469+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## 2026-10-11 — Dhan request parameter diagnosis

- Completed API attempt [38088524054](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088524054) passed unit tests, resolved 5/5 underlying IDs from the Dhan instrument master (master hash `2d962ddbd2681df30f08032f8b355aae50595b7a5a289d7e280c7eb558ca1173`), and completed all ten calls. All ten requests received HTTP 400, error code `DH-905`, safe error message `expiryCode is required`, and 0 rows.
- Diagnosis: request used numeric 0; the provider treated it as missing. Docs show 0 as Current/Near Expiry in the annexure but provide a request sample with 1 (Next Expiry). Registered a bounded test using `expiryCode: 1`, changed the code/manifest together, and added a test to freeze that parameter.
- First API attempt remains a failed request-schema run, not evidence of absent historical options data. No raw option payloads were committed and no strategy P&L calculated.

<!-- DHAN_API_RUN_38088597286_ATTEMPT_1 -->
## Dhan Data API audit — run 38088597286, attempt 1 — 2026-10-10T21:42:20.727955+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38088846052_ATTEMPT_1 -->
## Dhan Data API audit — run 38088846052, attempt 1 — 2026-10-10T21:45:46.027177+00:00

- **Result:** REQUEST_SCHEMA_OR_PARAMETER_ERROR.
- Window: 2026-08-02 inclusive to 2026-09-01 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 0/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.



## 2026-10-11 — Bound API latency diagnosis to one probe

- Run [38088625181](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088625181), which used `expiryCode: 1` on a 30-day window and up to ten stock/side probes, remained in the API request step and was cancelled when a smaller bounded workflow was committed. It did not persist a report and contributes no data evidence.
- Updated the client to support a strict `--max-probes` cap. The new default smoke-test request is one HDFCBANK CALL probe for 2026-08-03 only, with a 60-second per-request timeout, while keeping the upper bound of 30 days per API call. The workflow records the probe limit.
- This is a scope adjustment for debuggability/finite execution; it does not alter the chosen stock basket or any strategy rules.

<!-- DHAN_API_RUN_38088975571_ATTEMPT_1 -->
## Dhan Data API audit — run 38088975571, attempt 1 — 2026-10-10T21:47:54.152267+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089043087_ATTEMPT_1 -->
## Dhan Data API audit — run 38089043087, attempt 1 — 2026-10-10T21:48:48.952462+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089057160_ATTEMPT_1 -->
## Dhan Data API audit — run 38089057160, attempt 1 — 2026-10-10T21:49:02.855491+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089084020_ATTEMPT_1 -->
## Dhan Data API audit — run 38089084020, attempt 1 — 2026-10-10T21:49:47.179010+00:00

- **Result:** DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.

<!-- DHAN_API_RUN_38089152325_ATTEMPT_1 -->
## Dhan Data API audit — run 38089152325, attempt 1 — 2026-10-10T21:50:42.137495+00:00

- **Result:** DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## 2026-10-11 — Dhan date-boundary and stale-artifact diagnosis

- Run [38088975571](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088975571) verified a successful 1-probe API request after the workflow environment was fixed. It initially counted 770 rows.
- After adding IST-date counts, runs [38089084020](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089084020) and [38089152325](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089152325) independently showed 385 rows on 2026-08-03 and 385 on 2026-08-04 from a request whose toDate was 2026-08-04. Since the official docs say toDate is non-inclusive, the sample is flagged for date-window mismatch.
- Corrected the audit script to produce aligned columns and count out-of-window rows. The resulting status is `DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS`, not a clean pass.
- Earlier run [38088846052](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088846052) had passed tests but failed before an API request due to an absent `PHASE103_MAX_PROBES` env variable; its status logger repeated stale prior JSON, which is logged as E103-010. Future acceptance requires JSON `run_id` to match Actions run ID.
- Next action is a single HDFCBANK CALL query using equal start/end date values to test endpoint boundary behaviour, then re-run an ordinary half-open request with strict post-fetch range filtering. No further stock probes/backtests until this date-boundary gate is understood.

<!-- DHAN_API_RUN_38089220578_ATTEMPT_1 -->
## Dhan Data API audit — run 38089220578, attempt 1 — 2026-10-10T21:51:44.041591+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-03 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## 2026-10-11 — Resolve Dhan end-date semantics

- The same-date diagnostic [38089220578](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089220578) succeeded for HDFCBANK CALL and returned 385 rows with timestamps exclusively on 2026-08-03.
- Previous request with `fromDate=2026-08-03`, `toDate=2026-08-04` returned both 2026-08-03 and 2026-08-04. Therefore the provider appears to include its `toDate` even though the published spec says non-inclusive.
- Corrected the client to send provider `toDate = target_end_exclusive - 1 day` while keeping validation against the half-open target dates. Added unit coverage and a corrected table builder.
- Registered the next bounded audit as all five stocks × CALL/PUT for the same 2026-08-03 IST session (10 calls). The resulting report must show per-probe row counts, date bins, outside-window counts and equal-length arrays; strategy P&L remains out of scope.

<!-- DHAN_API_RUN_38089336359_ATTEMPT_1 -->
## Dhan Data API audit — run 38089336359, attempt 1 — 2026-10-10T21:53:28.424115+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-03 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 1/1.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


## 2026-10-11 — Guard against stale Dhan audit artifacts

- Run [38089336359](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089336359) failed before any API call because a test referenced `provider_to_date` without importing it.
- Its status step read the repository's previous audit JSON and repeated its PASS state despite the current run never making an API request. This was an output-isolation bug and has been logged as E103-012.
- Fixes: import the helper, remove checked-in audit outputs from the runner workspace before each run, verify the machine JSON run ID before writing status, and add explicit run-specific no-output entries on failure. The next run will perform ten stock/side probes only after all tests pass.

<!-- DHAN_API_RUN_38089393338_ATTEMPT_1 -->
## Dhan Data API audit — run 38089393338, attempt 1 — 2026-10-10T21:55:03.773246+00:00

- **Result:** PASS_API_DATA_RETURNED_FOR_ALL_REQUESTED_PROBES.
- Window: 2026-08-03 inclusive to 2026-08-04 exclusive.
- Underlying IDs resolved: 5/5.
- API probes returning rows: 10/10.
- Raw rows committed/uploaded: no. Token value printed/logged: no.
- Report: results/phase103/DHAN_DATA_API_AUDIT.md; machine summary: results/phase103/dhan_data_api_audit.json.


<!-- DHAN_NO_RESULT_RUN_38089656281 -->
## Dhan audit no result — run 38089656281
No current-run JSON was produced; previous audit data were not accepted as this run's output.


## 2026-10-11 — All-five-stock Dhan smoke test accepted; register surface audit

- Workflow [38089393338](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089393338) completed SUCCESS; 13 unit tests passed.
- HDFCBANK, ICICIBANK, RELIANCE, SBIN and INFY each returned 385 CALL and 385 PUT minute rows on 2026-08-03 (10/10 probes total).
- All required array lengths were consistent, timestamps were 09:15–15:39 IST, every row mapped to 2026-08-03, and zero rows were outside the half-open target window after the inclusive-toDate adapter.
- Raw payloads were not retained in repository/artifacts; only derived counts/timestamp metadata were published.
- Next bounded gate: seven relative-strike offsets per side and stock over the same one-day target window, to check fixed-strike reconstructability before strategy P&L.


## 2026-10-11 — Strike-surface preflight correction
- The first two automated tests of the new relative-strike code failed before any API calls. Cause: old unit tests passed HTTP status where the new helper expects a relative-strike label. A synthetic duplicate mapping fixture also did not actually overlap a timestamp/strike key.
- Both test issues were corrected; the workflow now accepts the seven documented Dhan offsets and has a 70-probe maximum. No data or strategy conclusion is derived from these failed runs.
