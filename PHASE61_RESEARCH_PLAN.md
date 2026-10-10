# Phase 61 research plan — new-source restart audit

## Research question
Do newly surfaced public or broker/vendor leads, not already accepted by Phase 59, satisfy the Phase 60 restart requirements for exact contract identity, prior-minute OI, timestamp coverage, source authorization, and (if claiming execution quality) historical bid/ask and quantities?

## Aim
Perform one finite metadata-only delta audit of new leads. Decide whether to reopen empirical strategy testing, authorize a sample-validation phase, or retain the NO-GO. No credentials, purchases, API calls to private endpoints, bulk downloads, or scraping.

## Scope and frozen constraints
- Carry forward Phase 60 NO-GO and all Phase 52–60 evidence unchanged.
- Assess only newly identified leads: MoneyTicks, DhanHQ expired-option API, ICICI Breeze, BarathGB007's collector, and the Zenodo 2017–2020 dataset.
- Required target keys: actual date/time IST, underlying, expiry, strike, CE/PE, OI source value and missing/zero distinction. Exact frozen times are 09:44, 09:45, 12:59, 13:00 and 15:15 IST.
- Execution-quality claims additionally require historical bid, ask, bid quantity and ask quantity.
- Do not interpret repository code licenses as market-data licenses.
- Do not treat public browsing as permission for automated caching, redistribution or derived-result publication.
- Do not alter the 480-row grid, OI minimum 100, 2% OHLC baseline, cost model, chronology or untouched holdout.

## Method
1. Freeze a source registry from public metadata/published documentation only.
2. Classify every source against history, exact contract identity, OI, bid/ask/depth, timestamp match, access, license/storage rights, and target-date coverage.
3. Emit deterministic JSON/Markdown report with a clear accept/reject reason per candidate.
4. Test that no source is accepted unless explicit rights and all required schema/time conditions are documented.
5. Persist the result, logs and README checkpoint in this branch.

## Decision rules
- ACCEPT_FOR_SAMPLE_VALIDATION only if explicit data access and license/storage/automation/derived-result rights are documented, and published evidence supports the required target contract/time fields.
- FOLLOW_UP_ONLY if plausible but rights, access, exact coverage or schema remains unverified.
- REJECT_FOR_FROZEN_REPLAY if historical period, fields, timestamp cadence or contract identity cannot meet the frozen requirements.
- No source in this phase is presumed accepted from vendor marketing claims alone.

## Analysis
No statistical analysis and no P&L. This is a bounded source feasibility audit.

## Acceptance criteria
- Exactly five new leads assessed.
- All decisions are reproducible from the committed registry.
- No candidate is accepted without rights plus exact timestamp/contract evidence.
- Tests and manual GitHub Actions workflow pass.
- README and status/error/research/chat logs are updated.

## Finite stopping rule
Stop after this one metadata audit. If no source qualifies, do not create another repetitive source-search phase. Keep empirical factor/strategy testing blocked until the user or provider supplies documented authorization or a genuinely new source with clear rights and exact target sample. The next step after such evidence is a small sample validation, not bulk acquisition or strategy optimization.

## Status
Plan frozen before automated execution. No source data downloaded and no strategy promoted.
