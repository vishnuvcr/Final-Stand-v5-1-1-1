# Phase 59 research plan — public option-data coverage audit

## Research question

Can newly identified public repositories and datasets supply trustworthy, exact-contract prior-minute open interest (OI) or historical bid/ask/depth at the frozen Phase 52 option entry/exit timestamps, under terms that permit automated research and caching?

## Aims and objectives

1. Expand the bounded public-source search beyond the six candidates recorded in Phase 58.
2. Distinguish public metadata/schema claims from independently verified file-level coverage.
3. Audit exact timestamp, expiry, strike, option type, OI and quote/depth requirements for the 100 blocked Phase 52 configuration-event rows.
4. Separate free datasets, public code pipelines, manual-only websites and licensed commercial feeds.
5. Emit a reproducible source registry, rejection rationale and finite next-step recommendation.
6. Stop this phase after the candidate triage; do not scrape against terms, download bulk market data, use credentials, accept licenses, spend money or alter the frozen strategy test.

## Frozen requirements

- Entry timestamps: 09:45 and 13:00 IST; the immediately prior OI timestamps are 09:44 and 12:59 IST.
- Exact common exit reference: 15:15 IST.
- The selected contract must be identified by date/time, underlying, expiry, strike and CE/PE.
- Needed OI must be the source-recorded value at the exact preceding minute, not daily EOD OI, derived/imputed OI, or a missing value rewritten as zero.
- Quote validation requires bid price, ask price, bid quantity and ask quantity at the exact timestamps. OHLC/LTP does not satisfy this requirement.
- Automated access and local cache/storage must be permitted by the data license/terms. A GitHub or Hugging Face repository license for code is not assumed to cover market data.
- No change to the Phase 52 grid, events, 2% threshold, OI minimum, costs, splits or holdout.

## Methodology

1. Freeze the source list in `research/phase59/source_registry.json`, with dated URLs, published schema/coverage claims, license/access notes and explicit evidence limitations.
2. Run a deterministic Python audit that validates each record and checks whether any source meets all hard requirements. This workflow reads only the committed metadata snapshot; it does not crawl websites or download data.
3. Run unit tests for unique source IDs, schema consistency, license and timestamp gates, and the expected conservative no-go decision.
4. Generate JSON/CSV/Markdown reports and append the run outcome to status, research, error and chat logs.
5. Cross-link the source report in the branch README and main README after validation.
6. Stop after this bounded source triage. A licensed candidate may only be tested after explicit authorization and a target-date/contract sample that proves coverage and permissions.

## Statistical analysis

Descriptive inventory counts only. No inferential statistics, P&L, strategy comparison, fill simulation or change to prior research results.

## Acceptance criteria

- Registry has at least eight unique, dated source candidates.
- Every candidate has evidence URLs, known/unknown license status, timestamp/contract capability fields, and an explicit decision.
- No source is marked acceptable unless exact target coverage, required fields and permitted automation are all verified.
- Tests pass; JSON, CSV and Markdown reports agree; workflow supports both manual dispatch and automatic branch-path changes.
- No source data is downloaded or committed, no costs/purchases are incurred, and no holdout or strategy promotion occurs.

## Plan amendment PA-59-001 — metadata-only method

Hugging Face's `rissin/nse-options-intraday` page reports that its Upstox 1-minute rows have NaN OI; its daily bhavcopy rows cannot supply prior-minute OI. The visible schema for `artist-23/nifty-options-data` has OI but no actual expiry field and no dataset card/license grant. These are evidence-screened out without attempting bulk download. Commercial providers remain leads only and require explicit licensing/target coverage permission.

## Status

Plan frozen before automated registry validation. This is a source-feasibility phase, not a strategy efficacy test.
