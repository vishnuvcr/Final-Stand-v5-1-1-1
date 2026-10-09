# Phase 51-1J Error Log

Every runtime or extraction failure must be recorded with run ID, cause, correction, and evidence impact.

## T51-1J-001 — Text crawler cannot operate cascading date selectors — OPEN / AUTOMATION ADDED

- **Date:** 2026-10-09
- **Observation:** Public page text reveals Year/Month/Expiry/Date/Strike Range controls, but the text view does not expose dynamically populated option values or download responses.
- **Impact:** Target dates cannot be classified as raw-data-present from page descriptions alone.
- **Correction:** Added a GitHub Actions Playwright audit to use ordinary browser interaction, enumerate options, and inspect same-origin XHR/fetch responses and visible downloads.
- **Evidence status:** No target-session option data accepted; no P&L.
