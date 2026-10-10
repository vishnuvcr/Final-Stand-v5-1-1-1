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
