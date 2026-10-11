# Phase 106 Research Plan — Forward EOD Replication

**Branch:** `phase-106-forward-eod-replication`  
**Registered:** 2026-10-11  
**Promotion:** prohibited in this phase

## Research question
Do the three fixed Phase 105 EOD long-option proxy rules retain their characteristics in a later non-overlapping calendar window, 2026-09-02 inclusive to 2026-10-02 exclusive, using the same five stocks, contract selection and cost grid? This is a forward-calendar replication, not a verified execution study.

## Frozen scope
- Universe: HDFCBANK, ICICIBANK, INFY, RELIANCE and SBIN.
- Source: official NSE daily UDiFF F&O archives; no substitution or interpolation.
- Dates: 2026-09-02 inclusive through 2026-10-02 exclusive.
- Candidate rules, selector, expiry window, tie-breaks, signal timing and entry-open/exit-close proxy remain unchanged from Phase 105.
- Costs: ₹10/₹15/₹20 per order, adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per unit per side, and 1.0×/1.5× modeled fees.
- Raw market rows and trade-by-trade prices are not published.
- No parameter tuning, winner selection after inspection, or strategy promotion.

## Steps and gates
1. 106.0 Registration: freeze dates, universe, rules and costs.
2. 106.1 Source integrity: at least 10 parsed sessions, ≥99.9% identity completeness, ≥99.0% OHLC completeness, zero duplicate daily keys/date mismatches, no unresolved parse errors and valid OHLC on positive-volume rows.
3. 106.2 Regression and chronology tests; no target-session price/OI may inform signal or contract choice.
4. 106.3 Run only the three fixed rules and all 72 cost scenarios.
5. 106.4 Publish aggregate CSV/JSON, figure, report, status, research log, error log and visible conversation log.

## Statistical analysis
Report gross/net P&L, fees, assumed slippage, return on premium deployed, win rate, average/median trade P&L, profit factor, maximum rupee drawdown, trade coverage and exclusions. Bootstrap daily P&L by session cluster with deterministic 2,000-draw percentile intervals; treat these as descriptive. Do not pool Phase 105 and Phase 106 as if prospectively randomized.

## Stop rule
Stop at 106.4. A source/accounting failure blocks strategy interpretation. Even positive results cannot be promoted because OHLC does not establish executable prices and Paytm Money account-specific contract notes remain unverified. If fewer than 10 valid sessions exist, close as insufficient data without widening the date window.