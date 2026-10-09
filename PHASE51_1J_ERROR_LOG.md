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
