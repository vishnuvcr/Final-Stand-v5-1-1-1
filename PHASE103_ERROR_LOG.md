# Phase 103 Error, Defect and Limitation Log

## 2026-10-11 — Initial source screen

### E103-001 — Public stock-option snapshots are not synchronized
**Type:** evidence limitation, not a program defect.  
**Finding:** public pages surfaced for HDFCBANK, ICICIBANK, RELIANCE, SBIN and INFY carry different crawl/market timestamps and different presentation/turnover semantics. They cannot support a truthful cross-stock quantitative liquidity rank as-is.  
**Resolution:** select an explicitly provisional initial universe from the official constituent-weight snapshot plus visible contract discovery evidence; require a common-window quantitative liquidity and data-quality audit in Phase 103.1 before any strategy P&L is evaluated.

### E103-002 — Current constituent snapshot is dated 2026-02-27
**Type:** time/provenance limitation.  
**Finding:** official NIFTY 50 whitepaper gives the cited weights as at 2026-02-27, not a synchronized 2026-10-11 live rank.  
**Resolution:** preserve the snapshot date beside every weight and refresh official membership/weights at Phase 103.1. Do not describe them as today's weights.

### E103-003 — Historical options data rights and fill quality unknown
**Type:** pending research gate.  
**Finding:** public quote/option-chain pages prove discovery only; they do not grant programmatic scraping, retention or publication rights and do not establish bid/ask/depth coverage for the backtest horizon.  
**Resolution:** source audit records rights and exact sample coverage before acquisition or modeling. Stop NO-GO if no authorized sample suffices.

No runtime execution error is recorded at initialization. Any failed workflow/run must be appended here with run URL, symptom, cause, correction and final verification. Resolved errors must never be removed.


### E103-004 — Dhan rolling-option data is not an exact fixed-contract tape
**Type:** source/model limitation.  
**Evidence:** Dhan's official endpoint describes data by relative strike (ATM and offsets) and documents OHLC, IV, volume, OI, strike and spot, not historical bid/ask/depth.  
**Risk:** an ATM-offset series can change actual strike over time. Treating its entire path as one persistent contract would misstate contract P&L; using OHLC as an executable quote would overstate fill certainty.  
**Resolution:** store the actual strike timestamp series, reconstruct exact contract identity only when it can be proven, exclude unresolved paths from P&L, and require an authorized source or clearly labelled conservative cost/fill proxy for spread/slippage. Never call this endpoint alone proof of an executable historical fill.

### E103-005 — Raw Dhan data retention/republication terms not yet confirmed
**Type:** data-governance limitation.  
**Risk:** committing or publicly artifacting raw API rows may exceed the subscription or market-data licence permitted use.  
**Resolution:** API audit emits aggregate counts and timestamp ranges only. Raw values remain ephemeral until permitted storage/retention rights are confirmed. The research still needs reusable data storage for later phases; use an approved private store if applicable rather than publishing raw market data to this public repository.


<!-- DHAN_API_RUN_38088253613 -->
### E103-DHAN-38088253613 — No audit output produced
A workflow step failed before a valid audit JSON was written. No data-success claim is made. Inspect the earliest failed step before retrying.
Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088253613


<!-- GITHUB_RUN_ID -->
### E103-DHAN-38088253613 — No audit output produced
A workflow step failed before a valid audit JSON was written. No data-success claim is made. Inspect the earliest failed step before retrying.
Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088253613


<!-- GITHUB_REPOSITORY -->
### E103-DHAN-38088253613 — No audit output produced
A workflow step failed before a valid audit JSON was written. No data-success claim is made. Inspect the earliest failed step before retrying.
Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088253613


<!-- GITHUB_RUN_ID -->
### E103-DHAN-38088253613 — No audit output produced
A workflow step failed before a valid audit JSON was written. No data-success claim is made. Inspect the earliest failed step before retrying.
Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088253613


<!-- DHAN_API_RUN_38088262635 -->
### E103-DHAN-38088262635 — No audit output produced
A workflow step failed before a valid audit JSON was written. No data-success claim is made. Inspect the earliest failed step before retrying.
Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088262635

 
### E103-006 — Registration test prevented the first Dhan API call
**Affected runs:** [38088253613](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088253613), [38088262635](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088262635).  
**Symptom:** Dhan audit job stopped at unit tests; network/API step was skipped.  
**Cause:** registration validator used exact list membership for a rights-audit phrase that is included as a clause within a longer metric entry.  
**Correction:** validator now checks whether any registered metric contains the phrase. Additional response tests were added and a new push-triggered run has been requested by committing tests.  
**Accepted evidence:** none from either run. The environment shows a masked Dhan secret was injected, but no API request was made. Do not treat this as confirmed Dhan access.
 
### E103-007 — Failure-fallback logging formatter emitted duplicate malformed entries
**Type:** workflow logging defect.  
**Finding:** the default-branch bridge's first fallback used incorrect `printf` arguments, so two failed preflight runs created extra entries containing literal placeholder labels. The duplicated entries are not separate underlying data errors.  
**Correction:** the bridge formatter was corrected in commit [52565b4](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/commit/52565b4f6f7e2e89af916f768addfc232e02af22); historical entries are preserved for auditability. Subsequent fallback entries should be checked for the one-marker-per-run invariant.

<!-- DHAN_API_RUN_38088386046 -->
### E103-DHAN-38088386046 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** NO_DATA_RETURNED_OR_SCHEMA_MISMATCH; rows returned by 0/10 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088386046

<!-- DHAN_API_RUN_38088499642_ATTEMPT_1 -->
### E103-DHAN-38088499642 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** REQUEST_SCHEMA_OR_PARAMETER_ERROR; rows returned by 0/10 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088499642

<!-- DHAN_API_RUN_38088524054_ATTEMPT_1 -->
### E103-DHAN-38088524054 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** REQUEST_SCHEMA_OR_PARAMETER_ERROR; rows returned by 0/10 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088524054


### E103-008 — Dhan treats expiryCode 0 as missing
**Type:** API request/official-documentation discrepancy.  
**Affected run:** [38088524054](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088524054).  
**Symptom:** all 10 probes returned HTTP 400, `DH-905`, safe error message `expiryCode is required`; zero rows. Instrument master mapping succeeded for all five symbols and Actions secret was injected (masked).  
**Source discrepancy:** official [Expired Options Data](https://dhanhq.co/docs/v2/expired-options-data/) request example uses `expiryCode: 1`; official [annexure](https://dhanhq.co/docs/v2/annexure/) lists 0 as Current/Near Expiry and 1 as Next Expiry.  
**Correction:** changed the bounded probe to `expiryCode: 1` as the documented request example/Next Expiry, updated the machine-readable protocol and added a unit test. The next run will determine whether the request is accepted. This failure is not a data-coverage or profitability finding.

<!-- DHAN_API_RUN_38088597286_ATTEMPT_1 -->
### E103-DHAN-38088597286 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** REQUEST_SCHEMA_OR_PARAMETER_ERROR; rows returned by 0/10 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088597286

<!-- DHAN_API_RUN_38088846052_ATTEMPT_1 -->
### E103-DHAN-38088846052 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** REQUEST_SCHEMA_OR_PARAMETER_ERROR; rows returned by 0/10 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088846052



### E103-009 — Ten-probe/30-day corrected request exceeded the useful bounded runtime window
**Type:** workflow/runtime limitation; no accepted API response.  
**Affected run:** [38088625181](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088625181).  
**Finding:** the request step did not finish before a newer workflow revision cancelled the run; the API did not persist a machine-readable response. The run is not evidence that data are present or absent.  
**Correction:** introduced a strict maximum-probe option and changed the next smoke test to one symbol/side on one trading session. If it succeeds, expand incrementally and log each verified chunk; if it fails or times out, capture its safe error status and stop to diagnose.

<!-- DHAN_API_RUN_38089084020_ATTEMPT_1 -->
### E103-DHAN-38089084020 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS; rows returned by 1/1 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089084020

<!-- DHAN_API_RUN_38089152325_ATTEMPT_1 -->
### E103-DHAN-38089152325 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS; rows returned by 1/1 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089152325


### E103-010 — Automatic Dhan workflow omitted PHASE103_MAX_PROBES
**Type:** workflow configuration defect.  
**Affected run:** [38088846052](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38088846052).  
**Symptom:** 12 unit tests passed, but the API command failed before making a request because `--max-probes` received an empty string. The workflow environment did not define `PHASE103_MAX_PROBES` and still passed the old date defaults. The inherited previous audit JSON was then mistakenly repeated by the status step; it is not evidence from run 38088846052.  
**Correction:** wired `PHASE103_MAX_PROBES` into both workflows, corrected bounded dates, and required each audit conclusion to be tied to the machine JSON's `run_id`. Future status review must check run IDs to avoid stale-artifact confusion.

### E103-011 — Dhan response exceeded documented non-inclusive date window
**Type:** source response/date-boundary issue.  
**Affected runs:** [38089084020](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089084020), [38089152325](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089152325).  
**Finding:** request `fromDate=2026-08-03`, `toDate=2026-08-04` returned 770 HDFCBANK CALL rows, of which 385 have IST date 2026-08-03 and 385 have IST date 2026-08-04. Dhan documentation describes `toDate` as non-inclusive. The audit now marks `DATA_RETURNED_WITH_OUT_OF_WINDOW_ROWS`; no strategy use is allowed until date semantics are explained and extra rows can be deterministically trimmed/reconciled.  
**Next diagnostic:** use equal `fromDate` and `toDate` for one bounded diagnostic request to determine whether the server treats the end date inclusively. This is a diagnostic, not a change to the registered half-open data definition.


### E103-011 resolution addendum — empirically inclusive Dhan end date
Run [38089220578](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089220578) requested `fromDate=toDate=2026-08-03` and returned 385 HDFCBANK CALL rows all dated 2026-08-03. The prior distinct-date query returned 385 rows on the start date and 385 on the end date, indicating practical inclusive-end behavior. The client now maps the registered target half-open range `[start,end)` to provider `fromDate=start`, `toDate=end-1 day`, and retains a strict timestamp gate. The old 770-row result remains rejected; subsequent requests must pass the timestamp gate before acceptance.


### E103-012 — Wrong import in provider-date unit test and stale-output acceptance
**Affected run:** [38089336359](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089336359).  
**Symptom:** unit-test preflight failed with NameError because `provider_to_date` was referenced but not imported. The API call step was skipped. The status logger then reused the previous run's JSON and mistakenly printed its PASS status for the current run.  
**Correction:** add the missing import; delete prior-run output files from the workflow workspace before any tests; make the status writer require the JSON `run_id` to equal the current `GITHUB_RUN_ID`; in fallback, record "no fresh result" rather than treating a stale artifact as current evidence. No data/strategy conclusions are based on this failed run.


<!-- DHAN_NO_RESULT_RUN_38089656281 -->
### E103-RUN-38089656281 — No fresh audit JSON for this run
Tests, network requests or audit generation did not produce a machine result whose run_id matches the current Actions run. Any prior JSON is not valid evidence for this run.
Run: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089656281


### E103-013 — Fixed-contract reconstruction not implied by the ATM API pass
**Type:** remaining validity gate, not an error.  
The 10/10 ATM pass validates access and array shape but does not show that an ATM relative-strike line is a fixed listed contract. Phase 103.1B will audit seven offsets for each stock and option side, aggregate actual-strike/timestamp coverage in memory, and keep raw rows out of outputs. No P&L may be calculated from one rolling-offset series treated as a fixed contract.


### E103-014 — Strike-surface implementation refactor broke test-call signatures
**Affected runs:** [38089656281](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089656281), [38089669894](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089669894).  
**Finding:** the summarizer gained a `requested_relative_strike` positional parameter, but unit tests still passed the HTTP code in that position. The API step was skipped. The initial duplicate-key fixture also failed to create a true same-timestamp duplicate.  
**Correction:** update all test calls with explicit `ATM`, test allowed relative strikes and surface alignment, and use a genuinely overlapping (timestamp,actual strike) fixture. The API must not run until tests pass.


### E103-016 — Relative-strike panel has an incomplete offset row
**Type:** data completeness limitation.
**Run:** [38089913649](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38089913649).
**Finding:** HDFCBANK CALL on 2026-08-03 returned 385 rows for ATM through ATM-2 and 384 rows for ATM-3. The combined offset surface has 384 common timestamps out of a 385-timestamp union, although six actual strikes are observed at every union timestamp and zero duplicate timestamp-strike keys are detected.
**Decision:** strict full-surface gate remains FAIL; do not fill the missing bar. A fixed-strike path may only use timestamps where its actual strike is present. Extend to the other stock/side groups and report exact-strike coverage before strategy testing.

<!-- DHAN_API_RUN_38090149633_ATTEMPT_1 -->
### E103-DHAN-38090149633 — Dhan API access/data gate did not fully pass
**Type:** runtime/access/data-availability gate.
**Status:** PROBE_ABORTED_AFTER_FIRST_INVALID_RELATIVE_STRIKE; rows returned by 59/60 probes.
**Handling:** no raw rows or secret values were logged. Do not start strategy P&L testing until access, entitlement, mapping and coverage issues are resolved.
**Run:** https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38090149633
