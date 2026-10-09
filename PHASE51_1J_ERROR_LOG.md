# Phase 51-1J Error Log

Every runtime or extraction failure must be recorded with run ID, cause, correction, and evidence impact.

## T51-1J-001 — Text crawler cannot operate cascading date selectors — OPEN / AUTOMATION ADDED

- **Date:** 2026-10-09
- **Observation:** Public page text reveals Year/Month/Expiry/Date/Strike Range controls, but the text view does not expose dynamically populated option values or download responses.
- **Impact:** Target dates cannot be classified as raw-data-present from page descriptions alone.
- **Correction:** Added a GitHub Actions Playwright audit to use ordinary browser interaction, enumerate options, and inspect same-origin XHR/fetch responses and visible downloads.
- **Evidence status:** No target-session option data accepted; no P&L.


## T51-1J-002 — Browser selector inspector syntax error — PATCHED / REPLAY PENDING

- **Run:** [37913468653](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37913468653) completed the browser job and saved an audit manifest, but the per-page selector snapshot failed with a JavaScript syntax error.
- **Impact:** Navigation responses showed HTTP 200, but selector counts were incorrectly recorded as zero because the inspection function errored before enumerating controls. The result classification is **NON-EVIDENCE** for date availability/data coverage.
- **Correction:** Replaced the complex DOM selector script with a simpler JavaScript evaluator and committed the corrected selector inspector. A new Actions run is pending.
- **Status:** PATCHED; wait for corrected browser run before any source classification.


## T51-1J-003 — Target selector state leaked across dates; chart series request was not triggered — PATCHED / REPLAY PENDING

- **Runs:** 37913656447 and 37913684463; audit artifact 11607682395 from run 37913684463 contains selector-level evidence for the usable portion.
- **Findings:** On a clean July-28 selection, TradingTick's historical chain selectors contained expiry/date `2026-07-28`; the same-origin chain endpoint `nifty-whoc-data.php?expiry=2026-07-28&date=2026-07-28` returned 41,899 bytes of JSON with strike-level Close/OI/volume/turnover fields and 15 visible table rows. No timestamp is present in the row schema; treat this as EOD/one-snapshot context, not intraday evidence. The historical chart page's strike filter returned an empty list for this expiry; the separate NIFTY historical-chart page returned a strike list.
- **Bug:** The first loop re-used the same page for both target dates, so the second date was not independently set after the July state. It also did not select a strike, so it never invoked the chart-series data request.
- **Correction:** Reload the target page before each date, capture each target's expiry/date selector independently, select a representative CE strike nearest 24,000 on chart pages if available, capture its ordinary same-origin response, and review returned JSON schema/clock-time fields. Limit response file capture to the TradingTick origin. Workflow triggers only on its marker to avoid duplicate runs; publisher checks out the latest phase branch before replacing result artifacts.
- **Evidence status:** The July 28 chain endpoint is confirmed as a point-in-time option-chain snapshot. Whether the historical chart API returns a full intraday time series and whether 2026-08-04 is available remains unverified until the next run. No P&L is allowed.


## T51-1J-004 — Fresh target-isolated audit finds no intraday payload / August 4 not listed — CLOSED / SOURCE REJECTED

- **Run:** [37915320571](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37915320571), terminal success; artifact publication succeeded.
- **Observed:** All three public pages returned HTTP 200. The 2026-07-28 expiry appeared in controls, but no intraday-like timestamp was found in the observed same-origin payloads. The chain data is snapshot/daily-context, not an evidenced one-minute contract series. The 2026-08-04 date was not present in tested selectors after fresh page reloads.
- **Cause of earlier uncertainty:** Prior scripts leaked cascading selector state between dates and failed to trigger chart-series requests. The corrected run isolated each target and selected a representative strike when available.
- **Correction/outcome:** Fresh-page logic and chart-series triggering are now applied; publication conflict was also fixed by preserving generated artifacts while resetting to the latest phase branch before publication.
- **Evidence impact:** TradingTick public endpoints are rejected for Phase-51 intraday OOS P&L. No prices/P&L accepted. This does not rule out a paid or private archive outside the audited public endpoints.
- **Next:** Assess authorized commercial archive/API access. No purchase or credential assumption without authorization.


## T51-1J-005 — Free HF audit workflow setup failure — PATCHED / RETRY RUNNING

- **Run:** [37916552983](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37916552983).
- **Cause:** setup-python's pip cache option requires a requirements.txt or pyproject.toml, neither exists at repository root. The setup step failed before downloading any source files. Artifact publication also attempted to git-add a nonexistent output directory.
- **Correction:** removed setup-python pip caching (the HF cache remains separately configured) and made metadata publication tolerate a missing output directory. Triggered corrected run [37916601582](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37916601582).
- **Evidence impact:** no source files downloaded and no data conclusions drawn from failed run.


## T51-1J-006 — Free HF files contain no target-date rows — CLOSED / SOURCE REJECTED

- **Run:** [37916601582](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37916601582), all workflow steps passed.
- **Observation:** Both advertised files were downloaded successfully and hashes/schema were recorded, but all timestamps stop on 2026-07-02. The 2026-07-28 file has 320,359 rows and zero rows dated 2026-07-28; the 2026-08-04 file has 2,646 rows and zero rows dated 2026-08-04.
- **Cause:** Stale/incomplete payloads stored under future expiry-date filenames; expiry metadata does not guarantee target-session coverage.
- **Correction:** Automated timestamp-range and target-date row audit added. Workflow setup failure from run 37916552983 is separately logged above and was corrected before this run.
- **Evidence impact:** Reject these files for the missing-session replay. No P&L accepted; raw files were not committed.
