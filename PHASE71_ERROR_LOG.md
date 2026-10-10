# Phase 71 Error / Blocker Log
Date: 2026-10-10

## B71-001 — Initial authenticated-access blocker
- Status: RESOLVED FOR CONNECTIVITY TEST ONLY
- Original cause: Repository secret `DHAN_ACCESS_TOKEN` was not configured at first.
- Resolution evidence: [Run 38041733380](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38041733380) ran authenticated requests successfully. Secret value was masked in logs and not committed.
- Scope limit: This does not resolve provider data quality, permitted retention/publication rights, or contract semantics.

## B71-002 — ATM-relative coverage is not full-chain
- Status: KNOWN LIMITATION
- Cause: The endpoint uses rolling ATM-relative strikes; official documentation limits the available relative strikes by instrument/context.
- Impact: Cannot infer far-OTM/wide-wing coverage or claim full-chain historical data.
- Resolution: Validate every candidate strategy's required strikes against returned offsets; source additional authorized data only if genuinely necessary.

## B71-003 — No historical executable quote data in endpoint
- Status: KNOWN LIMITATION
- Cause: This endpoint documents OHLC/IV/OI/volume/spot, not historical bid/ask or depth.
- Impact: Execution-quality claims remain unsupported.
- Resolution: Use conservative spread/slippage and Paytm Money cost sensitivity, while labeling the fills as modeled rather than observed. Do not claim execution-grade evidence without quotes.

## B71-004 — Aggregate count anomaly and unresolved timestamp bounds
- Status: OPEN; PHASE 72 REQUIRED
- Evidence: 2026-07-28 probes returned 750 timestamps overall, 375 timestamp rows on target date; 2026-08-04 probes returned 770 overall, 385 timestamp rows on target date. This occurred consistently across WEEK/MONTH and CALL/PUT probes.
- Risk: Counts may include rows outside regular session, duplicated timestamps, unusual timestamp bounds, or provider behavior not captured by the original aggregate-only probe.
- Resolution: Re-query only the same bounded dates and produce non-sensitive audit metrics: unique/duplicate counts, target-date and regular-session counts, first/last IST timestamp, out-of-session rows, gaps, required-field array lengths and valid-price ratios. Do not retain raw market rows in public GitHub.
