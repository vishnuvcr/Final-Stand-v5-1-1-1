# Phase 62 research plan — OptionsData sample and target-date validation

## Research question
Can a newly documented historical NIFTY options source supply a legally usable, schema-valid and exact-session-complete dataset for the frozen Phase 51 OOS gap, and can it validate the data ingestion pipeline without changing the frozen replay?

## Aim
Validate the vendor's freely downloadable sample and its documented licence/schema, then determine whether the exact missing sessions (2026-07-28 and 2026-08-04) can be obtained under the same permitted-use terms. This is a source/data engineering phase, not a profitability backtest.

## New lead and public evidence
- Free sample: https://optionsdata.shop/sample
- Live coverage catalog: https://optionsdata.shop/coverage
- Terms: https://optionsdata.shop/terms
- FAQ/schema: https://optionsdata.shop/faq
- Vendor describes contract-level 1-minute OHLC, volume and OI, but no bid/ask or depth. It says research/backtesting and internal use are permitted, while raw data redistribution/public-repository publication is prohibited. It disclaims completeness and says the live catalog is not a warranty that every bar exists.
- The public sample covers 2026-09-15 through 2026-09-17, not the two missing OOS sessions. The catalog's broad date span alone is not exact-session proof.

## Frozen constraints
- Missing OOS sessions: 2026-07-28 and 2026-08-04.
- Do not alter Phase 51's OOS window (2026-04-21 through 2026-08-04), strategy definitions, selection, cost model or holdout.
- Do not infer quotes/spreads from OHLC ranges. No bid/ask/depth is published in this source.
- Do not buy any pack, send personal details, or contact the vendor on the user's behalf.
- Never commit raw data, signed download URLs, tokens, or private/licensed files. Do not upload raw files as Actions artifacts. Store only hashes, schemas, row/date counts and aggregate diagnostics if permitted.
- The source is independent and not exchange-authorized; do not describe it as official NSE data.
- A code license does not grant rights to underlying market data.

## Phases and methods
1. **Terms/schema gate:** record current public terms and required schema; confirm that private/internal research and derived analysis are permitted and redistribution is prohibited.
2. **Free sample smoke test:** download the publicly offered sample in an ephemeral Actions runner; inspect archive contents and Parquet schemas; check timestamp timezone, contract keys, OI semantics, duplicates/conflicts, minute coverage, and expected sample dates. Never persist the raw archive or attach it to artifacts.
3. **Exact target-session gate:** separately verify that the vendor will provide an authorized sample or licensed files for both 2026-07-28 and 2026-08-04 and all required target contracts. The public sample is not a substitute. A broad coverage span is not sufficient.
4. **Canonical normalization test:** test both documented schema layouts, map fields to canonical timestamp/underlying/expiry/strike/CE-PE/OHLCV/OI fields, preserve missing versus true zero, and reject ambiguous duplicate contract-minute keys.
5. **Decision:** accept only if terms are compatible with intended private research and derived-result publication, both target sessions and exact contracts exist, and required fields pass validation. Since bid/ask/depth are absent, any resulting backtest must explicitly remain OHLC-based and cannot claim executable quote fidelity.
6. **Replay gate:** only after exact-session acceptance, run the existing frozen Phase 51 acquisition/coverage checks. Then recalculate Paytm Money brokerage, statutory charges, slippage and stress scenarios. No strategy promotion from source validation alone.

## Statistical analysis
None in this phase. No P&L, strategy ranking, hypothesis testing or holdout access. Report schema and data-quality counts only.

## Acceptance criteria
- Public sample download/schema smoke test runs automatically on push and is manually dispatchable.
- No raw market data is committed or uploaded.
- Report states sample date range, schema, key validation counts, and exact-target status separately.
- Target sessions are marked blocked until exact files/contracts are independently verified.
- README, status, research log, chat log and error log are updated.
- Workflow failure is recorded and corrected without concealing earlier errors.

## Finite stopping rule
One free-sample pipeline validation and one exact target-date availability decision. If the vendor cannot provide exact files/contract coverage and permitted-use confirmation without purchase, stop and report the concrete missing prerequisite; do not begin another repetitive source search. A paid pack requires explicit user authorization and must not be purchased automatically.

## Status at plan freeze
Plan frozen before workflow execution. No purchase made; no raw data downloaded by this phase yet; no P&L or strategy promotion.
