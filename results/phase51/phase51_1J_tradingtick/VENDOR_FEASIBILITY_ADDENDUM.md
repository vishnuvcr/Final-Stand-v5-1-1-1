# Phase 51-1J Addendum — Authorized Vendor Feasibility

**Assessment date:** 2026-10-09  
**Decision:** Technically promising source; purchase/ingestion not authorized or performed.

## Candidate: Options Data / optionsdata.shop
Public catalog: https://optionsdata.shop/data/nifty-options-historical-data  
Packs/prices: https://optionsdata.shop/packs  
Free sample: https://optionsdata.shop/sample  
FAQ/licensing: https://optionsdata.shop/faq

The vendor currently advertises NIFTY option-chain data at 1-minute resolution, all traded strikes and nearest expiries, OHLCV and open interest, Parquet format, coverage through October 2026. Its 2026 calendar-year NIFTY options pack is listed at ₹2,999; the three-year options pack at ₹7,249; NIFTY options+futures+spot three-year pack at ₹7,999. Catalog claims are vendor claims and still require byte-level validation after acquisition.

The public free sample provides three trading days (2026-09-15 through 2026-09-17), so it is useful for schema/parser smoke tests but **does not establish that the missing target dates are present**. The dataset states that no bid/ask or Greeks are included. This matters for execution modeling: OHLC bars alone cannot establish actual bid/ask spread or fill probability, so the existing conservative slippage/friction framework remains necessary.

The vendor states it is independent and not affiliated with NSE/BSE/MCX; licensing is for internal research/backtesting and prohibits redistribution. The site describes manual UPI payment verification. No purchase was made and no credential/payment information was supplied.

## Required pre-purchase checks
1. Ask vendor to confirm exact file presence for trade dates 2026-07-28 and 2026-08-04, and all required expiry/strike/CE/PE contracts for the frozen strategies.
2. Confirm the actual option pack contains these dates, minute timestamps, timezone, zero/absent-bar conventions, contract metadata, and that files are downloadable for local reproducibility.
3. Confirm permitted internal research use and storage in a private/public GitHub repository. Do not publish licensed raw data to a public repo or GitHub Pages; store only manifests, hashes, schema, derived summaries and reports unless licence explicitly permits more.
4. If confirmation is satisfactory and purchase is authorized, obtain the smallest suitable pack or date-specific custom quote, ingest into a private cache, validate checksums/schema/coverage/duplicates/missing minutes, then rerun the frozen Phase-51 full OOS.
5. Do not treat the vendor's catalog claims as data evidence until the actual files pass these checks.

## Stop condition
This feasibility substep stops here because buying data incurs a financial cost and needs explicit authorization. Phase 51 full-window OOS remains DATA-BLOCKED. No strategy promotion or P&L calculation from this vendor has occurred.
