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
