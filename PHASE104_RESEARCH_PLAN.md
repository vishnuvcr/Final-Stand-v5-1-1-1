# Phase 104 Research Plan — EOD Contract-Identified NIFTY Stock Options

**Branch:** `phase-104-eod-stock-options`  
**Parent:** `main` at phase creation  
**Registered:** 2026-10-11  
**State:** REGISTERED; PHASE 104.1 EOD SOURCE AUDIT PENDING  
**Previous work:** Phase 103 is frozen and terminal NO-GO for intraday stock-options P&L from the current Dhan rolling-option sample. Do not modify Phase 103 evidence or reopen its selector hunt.

## 1. Research question

Can official NSE end-of-day (EOD) futures-and-options bhavcopy records provide sufficiently complete, exact-expiry/strike/side historical stock-option records to support a separate daily-frequency research protocol for the frozen five-stock basket, and can any resulting strategy be evaluated without presenting EOD OHLC as verified executable fills?

## 2. Frozen universe and separation

The initial study basket remains HDFCBANK, ICICIBANK, RELIANCE, SBIN and INFY. It is a fixed research basket, not a claim that these are the top-five stocks by option volume.

- Phase 103 intraday rolling-option observations remain frozen/read-only.
- This branch uses official NSE daily UDiFF F&O bhavcopy records as a distinct EOD data route.
- Do not pool the Dhan rolling-relative-strike series with these EOD rows as if they were a continuous fixed-contract tape.
- Do not scrape the NSE option-chain interface; use the published daily archive route only.
- Do not persist raw NSE/Dhan market rows in the public repository or artifacts. Until applicable caching/retention terms are established, the workflow emits aggregate metadata and keeps raw rows ephemeral.
- This phase may conclude that EOD data are adequate for contract identity but inadequate for strategy execution analysis. Passing one gate does not automatically pass the next.

## 3. Registered hypotheses and aims

**H1 — EOD identity feasibility.** NSE daily UDiFF records include contract identity fields (symbol, expiry, strike, CE/PE) plus daily OHLC, volume, OI and underlying value for the fixed universe across the bounded sample.

**H2 — EOD strategy feasibility.** Even if daily contract identity passes, EOD bars alone may not validate bid/ask spread, intraday fills, queue position, latency or partial fills. A strategy P&L test is permitted only if the research protocol defines defensible execution assumptions and clearly labels bar-price simulation as a proxy.

Aim: establish whether a lower-frequency, contract-identified study can move forward without repeating Phase 103's unresolved data-identity problem.

Objectives:
1. Test the official NSE daily archive format and exact contract key on a fixed 30-calendar-day sample.
2. Measure daily file availability, row/field completeness, unique contracts, duplicate identities, symbol-wise coverage, trading-volume/OI missingness and underlying-value coverage.
3. Separate absent files on non-trading dates from download/schema errors; never interpret missing fields as zero.
4. Verify historical contract multiplier/lot-size fields and identify the additional corporate-action/calendar data needed.
5. Record data use, storage, caching and derived-publication limitations; do not republish raw rows.
6. Review current Paytm Money and statutory charge schedules before any P&L run. Apply date-effective charges, including the official STT change effective 1 April 2026; stress brokerage, statutory levies, adverse slippage and spread assumptions.
7. Define a small, interpretable EOD strategy family only after data quality passes. Do not use the audit window as a final holdout or tune on the independent test.
8. Publish a manuscript and close this phase by the defined stop rule.

## 4. Boundaries and phases

### 104.0 — Registration and source screen
- Freeze the research question, universe, data route, exclusions and stop rule.
- Read Phase 103 terminal result before every next step.
- Record official source references and clearly distinguish API accessibility from legal rights.

### 104.1 — Bounded EOD data audit
- Default target window: 2026-08-03 inclusive to 2026-09-02 exclusive, no more than 30 calendar days.
- Query official NSE UDiFF daily archives by trade date and process only the frozen five symbols, stock-options instrument type, and CE/PE records.
- Validate required schema, date range, contract identity, duplicate daily contract keys, per-symbol/date coverage, traded volume, OI, underlying value and lot size.
- No raw-row cache, raw data commit or raw-data artifact. Persist only aggregate summaries, hashes of downloaded archive payloads, safe failure classes and counts.
- Exit gate: at least 10 downloaded trade-date archives; required contract-identity fields complete for at least 99.9% of included stock-option rows; zero duplicate daily contract keys after source-defined de-duplication; schema passes; no unresolved date or instrument-type mismatch. Missing archive dates are listed, not silently dropped.

### 104.2 — Execution-cost and inference feasibility
- Verify Paytm Money's actual F&O brokerage schedule using current official pricing/contract-note evidence where available.
- Build date-effective statutory/exchange fee functions (STT, exchange transaction charges, GST, SEBI fees, stamp duty and any other applicable levy) with unit tests and known worked examples.
- Establish whether EOD-only entry/exit prices can support a defensible strategy question. Use next-session executable quotes or a validated, explicitly conservative proxy if available. EOD OHLC alone is not bid/ask evidence.
- If no defensible execution model is possible, close the empirical P&L route as NOT TESTABLE with current data. Do not invent spreads or claim fills.

### 104.3 — Preregistered strategy test (conditional)
Only enter if 104.1 passes and 104.2 produces a defensible, documented cost/execution model.
- Keep the candidate family small and interpretable; no unregistered grid search.
- Use chronological development, validation, independent test and sealed holdout; avoid overlapping leakage between expiry/date clusters.
- Use defined-risk options only for initial candidates. No naked short options.
- Report gross/net results, costs by type, coverage/exclusions, average/median net trade, drawdown, return on deployed capital, profit factor, tail loss, and uncertainty corrected for multiple trials.
- Never describe a bar-price proxy as exchange-executable backtest evidence.

### 104.4 — Manuscript and closeout
- Publish the methods, source audit, limitations, charts/tables if strategy testing was valid, logs, conclusions and future direction.
- Stop after this closeout. Further data procurement, change of universe, extended history or a different intraday source requires a separately registered plan/branch.

## 5. Decision rules

**Data-feasibility PASS** requires the Phase 104.1 criteria above.  
**Strategy-P&L PASS** additionally requires a verified rights path, date-effective costs, executable quote evidence or a validated conservative fill proxy, independent testing and statistical safeguards.  
If data identity passes but spread/fill evidence does not, the correct conclusion is **EOD contract records are suitable for historical coverage/feature research but not for an executable profitability claim**. Do not force a strategy conclusion from a failed execution gate.

## 6. Prespecified outputs

- `PHASE104_RESEARCH_PLAN.md`, `PHASE104_STATUS.md`, `PHASE104_RESEARCH_LOG.md`, `PHASE104_ERROR_LOG.md`, `PHASE104_CHAT_LOG.md`
- `results/phase104/SOURCE_SCREEN.md`
- `results/phase104/nse_eod_data_audit.json` and `results/phase104/NSE_EOD_DATA_AUDIT.md` (aggregates only)
- `results/phase104/PHASE104_FINAL_MANUSCRIPT.md`
- `research/phase104_eod_stock_options/`, `tests/phase104/` and a manual GitHub Actions workflow.

## 7. External references (retrieved 2026-10-11)

- NSE official derivatives report/archive interface: https://www.nseindia.com/all-reports-derivatives
- NSE official individual-stock options contract specification (expiry, strike, call/put semantics): https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities
- NSE EOD/historical data vending and order/trade product inquiry: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- NSE Data & Analytics product inventory: https://www.nseindia.com/static/nse-data-and-analytics/data-information-vending
- NSE official STT rates effective 1 April 2026: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- Paytm Money official pricing page: https://www.paytmmoney.com/stocks/pricing
- Phase 103 frozen terminal evidence: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-103-nifty50-stock-options

