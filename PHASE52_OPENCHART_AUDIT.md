# Phase 52 — OpenChart Source Feasibility Audit

**Question:** Can marketcalls/openchart supply *all* historical options data required by the Phase 52 and Phase 51 replay pipeline?

**Decision before live probe:** **Not as the sole or presumed-complete source.** It is a plausible *auxiliary* source for querying individual NSE/NFO instruments' historical OHLCV bars. Complete coverage of every strike/expiry/session, old-contract discovery, stable historical depth, OI, bid/ask, Greeks, and storage/redistribution permissions have not been established. A bounded runtime probe is preregistered separately and cannot upgrade the source to primary status by itself.

## Source facts inspected

- Repository: https://github.com/marketcalls/openchart
- Pinned upstream commit: a207108890c96a9830b35a8d15442c896ea0a9d6 (project code updated to API v1 on 2026-01-16).
- The project README describes a Python client for NSE charting endpoints, dynamic symbol search in IDX/EQ/FO, historical OHLCV, and intervals including 1m. The documented response columns are timestamp plus Open/High/Low/Close/Volume.
- Implementation submits separate requests to https://charting.nseindia.com/v1/exchanges/symbolsDynamic and /v1/charts/symbolHistoricalData. historical() performs a symbol search then retrieves history for one selected instrument; historical_direct() needs a known token, symbol and type.
- The client does not expose historical option-chain snapshots, open interest, implied volatility, exchange Greeks, bid/ask, order-book depth, trade-by-trade prints, or a bulk historical chain endpoint in the inspected public API.
- Its symbol search returns a query result set. No source-side mechanism for reconstructing a complete historical symbol master/contract universe, expiry calendar, all strikes at all timestamps or pagination of every expired contract is documented in the inspected implementation.
- The implementation converts response epoch milliseconds to UTC datetimes then removes timezone metadata. It also serializes start/end via datetime.timestamp(). Consequently, timezone-naive values must not be assumed to be IST or UTC correctly without comparison to independently verified market-session anchors; date-aware timestamps are a hard acceptance gate.
- The repository is MIT-licensed as software. That does not grant a licence to the underlying NSE market data.

## Capability matrix

| Requirement | Evidence from inspected code/docs | Phase 52 disposition |
|---|---|---|
| Individual contract OHLCV candles | Explicitly supported by historical_direct() and schema | Probe as auxiliary candidate |
| 1-minute bars | Interval implemented as (1, 'I') | Verify with live/known anchors |
| NIFTY option symbol search | FO segment plus dynamic search | Probe limited queries only |
| Complete expired-contract universe | No demonstrated historical symbol master or all-chain endpoint | **Not proven; block source-completeness claims** |
| OHLCV for all strikes and expiries across full dates | Requires hundreds/thousands of exact symbol-time queries; no completeness guarantee or historical coverage bound | **Not acceptable as sole source yet** |
| OI / change in OI / PCR | Not present in documented bar response schema | Must come from a separately audited source |
| Greeks, IV surface, skew/term structure | Not present | Must derive point-in-time from valid option+underlying inputs; do not claim exchange Greeks |
| Bid/ask, quote depth, trade prints | Not present | Cannot establish executable fills or true spread |
| Source stability / rate limits | Public GitHub issues include reports of failed requests, data access problems and rate limiting; oldest backfill question is unresolved in the reviewed issue list | Bounded retries/backoff only; no aggressive crawl |
| Timestamp/session correctness | Upstream strips timezone metadata from converted timestamps | Independent timestamp reconciliation required |
| Legal/storage status | MIT applies to client code; NSE's own Data Sharing & Usage Policy separately governs data usage, storage, sharing and redistribution | Keep raw source responses out of the public repository until terms are cleared |

## Preregistered bounded probe

Workflow: .github/workflows/phase-52-openchart-source-probe.yml  
Probe code: research/phase52/openchart_source_probe.py  
Pinned client revision: a207108890c96a9830b35a8d15442c896ea0a9d6.

The probe will:
1. self-test the quality summarizer without network access;
2. perform a small number of symbol searches for current NIFTY FO instruments and the frozen missing-session prefixes NIFTY26JUL and NIFTY26AUG;
3. request 1-minute bars for at most one currently listed option and, only if discoverable, at most one option from each target-date query;
4. record HTTP status/rate-limit metadata, row counts, first/last timestamps, duplicate timestamps, OHLC validity and whether returned naive clock times resemble the NSE cash-session clock;
5. persist only an aggregate JSON report—never raw OHLCV rows, full symbol dumps or tokens.

This is a discovery smoke test, not an exhaustive source audit. Even if all requests return bars, acceptance still requires a separate frozen contract-universe and date/time coverage audit, source-to-independent-anchor reconciliation, exact-expiry completeness, OI availability strategy, and legal/data-retention review.

## Acceptance gates before using OpenChart in replay

- [ ] API reliability and rate-limit behavior are measurable; empty frames are distinguished from rate-limited/failed requests using captured HTTP metadata.
- [ ] Both 2026-07-28 and 2026-08-04 target windows are verified against exact option symbols and an independent, trusted source.
- [ ] Full target expiry/strike/type universe is enumerable, with per-contract expected-versus-observed coverage.
- [ ] OHLC, volume, duplicates, missing-minute gaps, timestamp convention and session bounds pass source-specific tests.
- [ ] No OI/quote/Greek fields are silently inferred from absent fields; any calculated factors carry point-in-time lineage.
- [ ] NSE data usage and permitted storage/retention are confirmed before storing raw records in the public repository or using them commercially.
- [ ] The resulting pipeline passes existing Phase 52 fee/slippage and replay gates; no strategy outcome is used to decide source eligibility.

## References

1. OpenChart repository and README: https://github.com/marketcalls/openchart
2. OpenChart core request implementation: https://github.com/marketcalls/openchart/blob/master/openchart/core.py
3. OpenChart response transformation: https://github.com/marketcalls/openchart/blob/master/openchart/utils.py
4. OpenChart issues on request failures/rate limiting/backfill depth: https://github.com/marketcalls/openchart/issues
5. NSE Data Sharing & Usage Policy: https://www.nseindia.com/static/market-data/nse-data-policy

## Runtime outcome — 2026-10-10 (final bounded probe)

The workflow [37982673873](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982673873) passed its software/quality checks and persisted an aggregate-only report at [`results/phase52/openchart_probe/runs/37982673873/probe_report.json`](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/openchart_probe/runs/37982673873/probe_report.json).

Six search queries were tested: NIFTY on FO and IDX, current-month prefix NIFTY26OCT on FO, the README's documented option example, and the NIFTY26JUL / NIFTY26AUG prefixes corresponding to unresolved Phase 51 sessions. Each request to `/v1/exchanges/symbolsDynamic` returned HTTP 200 and 20 rows. All 20 rows had type `Index`; the normalized result hash was identical across all six searches. Both NIFTY FO and NIFTY IDX returned the same rows; the other four contract-oriented query strings had zero symbol/description matches. The cookie/homepage GET returned HTTP 403.

**Result:** zero options/futures were identified. The report records two historical date windows planned and zero historical requests. The options-history endpoint was **not exercised**, because the search wrapper did not produce a contract/token. This distinguishes a failed source-discovery step from proof that the separate historical-data endpoint cannot serve an individual known token.

The immediate disposition remains **NOT ACCEPTED for all-options acquisition**. In addition to not exposing OI, Greeks, IV, bid/ask, order depth or trade-by-trade data in its documented OHLCV schema, the current symbol-search wrapper fails the initial option-universe discovery gate. The generic `historical()` method also falls back to the first search result if there is no exact symbol match, so any adapter must explicitly enforce exact symbol/token matching before fetching; otherwise it risks silently selecting the wrong instrument.

A future bounded follow-up may test `historical_direct()` using a separately verified contract/token and then audit expiry/strike/session coverage. It must not treat this current run as a historical data success, fill the Phase 51 gaps, or produce strategy P&L.
