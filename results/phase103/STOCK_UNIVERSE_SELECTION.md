# Phase 103.0 — Initial Five-Stock Selection

**Decision:** register the following as the initial stock-options universe.  
**Data state:** no historical strategy data have been downloaded or backtested.  
**Claim scope:** this is a defensible initial research basket, not proof that the stocks are the five most liquid stock-options underlyings by a comparable statistical measure.

## Selection

| Priority | Symbol | Company | Sector | Official NIFTY 50 weight snapshot | Snapshot rank |
|---:|---|---|---|---:|---:|
| 1 | HDFCBANK | HDFC Bank | Financial Services | 11.83% | 1 |
| 2 | ICICIBANK | ICICI Bank | Financial Services | 8.58% | 2 |
| 3 | RELIANCE | Reliance Industries | Oil, Gas & Consumable Fuels | 8.20% | 3 |
| 4 | SBIN | State Bank of India | Financial Services | 4.34% | 6 |
| 5 | INFY | Infosys | Information Technology | 3.97% | 7 |

Weights and rank are from the official NIFTY 50 whitepaper constituent snapshot as of **27 February 2026**. They are not today's live weights. All five have discoverable listed stock-option contracts in public derivative pages, though the captured public pages do not share one timestamp or a comparable volume calculation.

## Why this basket

- Large index weights provide a transparent starting point and should give adequate underlying-market relevance.
- Public stock-derivatives pages show listed calls and puts for the chosen names.
- Three financial names remain in the five-stock basket because they rank highly on the index snapshot; this creates sector concentration, which must be disclosed in pooled results. Per-stock analysis must be reported separately.
- The list is intentionally fixed before testing P&L. Stocks cannot be chosen or replaced based on backtest performance.

## Important limitation

Current page visibility or a few active strikes do not establish years of accurate, licensed historical quotes or tight executable spreads. The public snapshots have different dates and data presentation. Phase 103.1 must calculate same-window metrics (option volume/turnover, OI, spread/mid, quote depth when available, contract/expiry coverage and missingness) and confirm rights before any strategy test.

## Sources

1. NSE Indices official NIFTY 50 whitepaper (constituent weights dated 27-Feb-2026): https://niftyindices.com/docs/default-source/indices/nifty-50/nifty-50-whitepaper_2026.pdf
2. NSE NIFTY 50 page/constituent download: https://www.nseindia.in/static/products-services/indices-nifty50-index
3. NSE derivatives underlying list: https://www.nseindia.com/static/products-services/equity-derivatives-list-underlyings-information
4. HDFCBANK option listing: https://www.moneycontrol.com/india/fnoquote/hdfcbank/HDF01/2026-10-27/OPTSTK/CE/860.00/true
5. ICICIBANK option listing: https://www.nseindia.com/get-quote/derivatives/ICICIBANK/ICICI-Bank-Limited
6. RELIANCE option listing: https://www.nseindia.com/get-quote/derivatives/RELIANCE/Reliance-Industries-Limited
7. SBIN option listing: https://www.nseindia.com/get-quote/derivatives/SBIN/State-Bank-of-India
8. INFY option listing: https://www.moneycontrol.com/india/fnoquote/infosys/IT/2026-10-27/OPTSTK/CE/1040.00/true
