# Phase 51-1J Research Plan — TradingTick historical option data audit

## Research question
Can TradingTick's public historical NIFTY options pages expose the missing 2026-07-28 and 2026-08-04 sessions as reproducible raw intraday contract data suitable for the frozen Phase-51 OOS replay?

## Scope
Audit public, unauthenticated pages and assets on tradingtick.in. Do not bypass authentication, CAPTCHA, paywalls, rate limits, or other access controls. No P&L will be calculated in this phase.

## Objectives
1. Inspect the historical option-chain download page and expired-option chart page with a headless browser.
2. Record selector fields/options, including whether target expiries and session dates can be selected.
3. Capture ordinary same-origin browser request/response metadata to identify public data flows.
4. Determine whether returned/downloaded data contain timestamped intraday OHLC/volume/OI rows for the required contracts, rather than EOD snapshots or individual chart images.
5. Record schema, interval, row/contract coverage, response hashes/byte sizes, and download links without storing cookies, credentials, or private browser state.
6. Preserve only manifests and audit artifacts unless redistribution rights for raw data are clear.
7. If extraction is feasible, prepare a separate acquisition step; do not alter frozen strategies or accept data until licensing, coverage and schema-equivalence gates pass.

## Frozen target dates
- 2026-07-28
- 2026-08-04

The full OOS window remains 2026-04-21 through 2026-08-04. The accepted partial diagnostic through 2026-07-21 is not replaced or extended here.

## Method
- Playwright Chromium loads published pages as an ordinary browser.
- Capture visible form names/options and dynamically populated states after choosing 2026 and relevant months/dates where present.
- Observe ordinary same-origin XHR/fetch responses and public JavaScript references. Store response metadata and schema/shape summaries only.
- Use standard site navigation and visible download actions only. Do not evade site controls.
- Audit any publicly downloadable file's type, headers, timestamps, schema and coverage before research use.

## Acceptance criteria
- PASS_INTRADAY_DATA_CANDIDATE: timestamped intraday rows at the required frequency for both target sessions, required strike/option-side prices and sufficient contract coverage, verifiable provenance and permitted use.
- EOD_CONTEXT_ONLY: daily option-chain snapshots without the intraday sequence required for execution.
- DATE_VISIBLE_DATA_NOT_VERIFIED: date selectable but actual downloadable row coverage not independently inspected.
- DATA_BLOCKED: target absent, download unavailable through ordinary public interaction, or only non-reproducible charts exposed.

## Stop rule
Complete one automated browser/source inspection and a focused retry only if a runtime issue prevents inspection. Close with an evidence-backed classification. Do not loop endlessly or fabricate missing prices.
