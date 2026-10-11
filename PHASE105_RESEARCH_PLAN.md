# Phase 105 Research Plan — EOD OHLC Strategy Pilot

**Branch:** `phase-105-eod-ohlc-strategy-pilot`  
**Parent:** `phase-104-eod-stock-options` (frozen source audit and fee model)  
**Registered:** 2026-10-11  
**Status:** REGISTERED — bounded exploratory proxy pilot; runtime results pending  
**Promotion rule:** no strategy may be promoted from this pilot.

## 1. Research question

Within the already-audited 2026-08-03 inclusive to 2026-09-02 exclusive five-stock NSE EOD sample, do a small number of prespecified one-session long-option rules show positive after-cost results under explicitly adverse OHLC execution-proxy assumptions, and are any results robust enough to justify collecting an independent, longer sample?

This is a new study, not a revision of Phase 104. Phase 104 remains a data-quality audit only: it passed contract identity/OHLC completeness but did not test strategy profitability.

## 2. Frozen scope and source

- Universe: HDFCBANK, ICICIBANK, INFY, RELIANCE and SBIN.
- Data: official NSE UDiFF daily F&O archives only; use the same bounded window as Phase 104.
- Permitted fields: trade date, symbol, exact expiry, strike, CE/PE, daily OHLC, volume, open interest, reported underlying value and contract lot size.
- Raw rows and downloaded archive bodies stay in memory only. Persist archive hashes, row/coverage counts and aggregate strategy outputs only; no raw-price or trade-by-trade files.
- This window is an already-inspected feasibility sample, not an independent holdout and not a representation of all market regimes.
- No OpenChart, Dhan rolling-strike, index-options, synthetic, interpolated, or missing-session proxy records are mixed into this study.

## 3. Prespecified strategies (no parameter grid)

All positions are long options only, at most one lot per stock per signal, selected using information available at the prior session close. The chosen contract must have 7–35 calendar days to expiry on the signal date, positive prior-session traded volume and OI, positive lot size, and complete/valid prior-session OHLC. Select the earliest eligible expiry; within that expiry choose the strike nearest the prior-session reported underlying value. Break ties by higher prior OI, then higher prior volume, then lower strike. No contract may be selected from the entry session's prices or OI.

1. **MOMENTUM_ATM:** use the sign of the underlying value's prior-session close-to-close change; rising selects CE, falling selects PE.
2. **REVERSAL_ATM:** invert the same prespecified direction signal.
3. **MOMENTUM_OI_CONFIRM:** use the momentum direction only when the sum of OI for that side, same selected expiry and strikes within ±3% of the signal-date underlying value increased versus the previous session. OI is not intrinsically directional; this is an exploratory confirmation filter, not a market-microstructure claim.

Signal timestamp: after session t−1 closes, using underlying values and option volume/OI known through t−1. Entry proxy: selected contract's session-t open. Exit proxy: same session-t close. There is no overnight holding, no short/naked option, no expiry holding, no stop-loss tuning, no portfolio compounding and no rule optimization. Use the prior session's lot-size field; exclude a contract if the entry-day lot size contradicts it.

A signal is not a fill. Missing contracts, invalid OHLC, zero-volume target-session bars and non-positive entry values are recorded as coverage exclusions, never filled by interpolation. This target-session exclusion is retrospective data-quality handling and cannot establish that a real order would or would not have filled.

## 4. Cost and execution sensitivity

- Apply Phase 104's date-effective cost engine for the August 2026 sample: exchange transaction charges, separately itemized IPFT, STT, stamp duty, SEBI fee, GST, and two executed orders per completed round trip.
- Brokerage sensitivity: ₹10, ₹15 and ₹20 per executed order. User-specific Paytm Money account tier/contract notes remain unverified.
- Adverse slippage per option unit, on each side: ₹0.00 (idealized reference only), ₹0.05, ₹0.25 and ₹0.50. Add to the proxy entry and subtract from the proxy exit, floored at zero.
- Fee/levy sensitivity: 1.0× and 1.5× modelled fees. This adds up to 24 prespecified cost scenarios per strategy.
- A zero-slippage outcome is not the preferred estimate. Even adverse slippage values are assumptions, not observed spreads, queue costs, latency or market impact. OHLC marks never become verified executable fills.

## 5. Analysis and statistical safeguards

For every candidate and scenario, report intended signals, selected contracts, completed price-proxy trades, exclusions, gross P&L, modelled fees, slippage impact, net P&L, win rate, average and median net P&L per trade, profit factor, maximum peak-to-trough drawdown in rupees, total premium deployed, and net return on premium deployed. Percent portfolio drawdown is not reported because a funded portfolio/position-sizing policy is outside this pilot.

For the registered primary comparison use ₹20/order, ₹0.25 per-unit adverse slippage per side, and 1.0× fees; also show the stricter ₹20/order, ₹0.50 slippage, 1.5× fee stress. Calculate a deterministic percentile bootstrap interval for mean daily portfolio P&L by resampling trading-day clusters, not individual same-day trades. Report the tiny-sample uncertainty and do not use a p-value or rank candidates as proven winners. Any multiple-candidate comparison is exploratory.

No profitability/promotion decision is allowed unless all identity, price-integrity, coverage and accounting invariants pass. Even a positive result is only a candidate for independent replication over multiple regimes/expiries with authorized data.

## 6. Finite research phases and gates

### 105.0 — Registration (this plan)
Freeze research question, symbol set, period, selectors, signal timing, cost scenarios, outputs, limitations and stop rules before strategy P&L is viewed.

### 105.1 — Re-acquire and revalidate the bounded source
Download the daily archive files for the frozen dates; validate source schema, dates, exact contract keys, OHLC plausibility, duplicates, underlying values, OI, volume and lot-size completeness. Log each missing date and safe error category. No raw rows in outputs.
**Gate:** at least 10 parsed archive sessions, ≥99.9% identity completeness, ≥99.0% OHLC completeness, zero duplicate daily contract keys, zero date mismatches and no unresolved source/schema errors.

### 105.2 — Unit tests and chronology audit
Unit-test contract selection, expiry window, direction mapping, zero-volume exclusions, exact-contract next-session matching, lot-size consistency, slippage direction, date-effective fee integration, and bootstrap determinism. Assert that candidate selection cannot use target-session OHLC/OI.

### 105.3 — Frozen strategy replay and cost stress
Run only the three registered rules on the bounded sample. Create aggregate-only CSV/JSON, coverage accounting, report and SVG chart. Record all cost sensitivities; no parameter search or rule adjustment based on outcomes.

### 105.4 — Independent review and closeout
Validate accounting invariants (gross P&L equals stressed exit less entry times lot; net equals gross less slippage and fees; all scenario trade counts reconcile), list data gaps, write conclusions and future-work requirements, update phase status/error/research/chat logs and main README. Stop here.

## 7. Error-handling and stopping rules

- Any source/schema/date/duplicate failure blocks P&L; log the failure and preserve the most recent verified report.
- Any missing price/contract is excluded and counted. Never fabricate a mark or fill.
- Any accounting/test failure blocks strategy conclusions; the workflow exits non-zero and records the phase state.
- No changing parameters, widening dates, substituting symbols, opening 2026 holdout data, or repeating source hunts inside Phase 105.
- No strategy can be called profitable, recommended, or live-trade-ready based on this sample, even when simulated net P&L is positive.
- Stop after the finite phases above. Further data, a longer sample or a new feature hypothesis requires a new isolated registered branch.

## 8. Expected artifacts

- `PHASE105_RESEARCH_PLAN.md`, `PHASE105_STATUS.md`, `PHASE105_RESEARCH_LOG.md`, `PHASE105_ERROR_LOG.md`, `PHASE105_CHAT_LOG.md`
- `research/phase105_eod_ohlc_strategy_pilot.py`
- `tests/phase105/test_phase105_pilot.py`
- `.github/workflows/phase105-eod-ohlc-strategy-pilot.yml`
- Aggregate-only `results/phase105/summary.json`, `summary.csv`, `PHASE105_REPORT.md`, `decision.json` and `figures/net_pnl_by_slippage.svg`

## 9. Source and cost references

- Phase 104 data audit and exact source window: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-104-eod-stock-options
- Official NSE derivatives daily archives: https://www.nseindia.com/all-reports-derivatives
- Official NSE individual-stock option specification: https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities
- Official NSE equity-derivatives levies: https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
- Official NSE STT effective-date page: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- Paytm Money F&O pricing/FAQ: https://www.paytmmoney.com/stocks/pricing

**Interpretation boundary:** this is a one-month, after-cost OHLC proxy pilot. It cannot validate execution quality, generalize across regimes, or replace Phase 102's evidence ranking. No strategy is promoted.
