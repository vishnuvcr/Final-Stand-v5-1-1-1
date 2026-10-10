# Phase 58 research plan — historical quote/depth source feasibility

## Research question
Is there a free, legally cleared, automatable source of historical NIFTY option bid/ask/depth data at the exact entry/exit timestamps required by the existing replay protocol, and if not, which licensed source is the next best candidate?

## Aim
Reassess public documentation and sample schemas for NSE, StockMojo, NiftyTrader, TickBytes, OptionVault, and the existing Hugging Face source. Separate (a) data that exists in public samples, (b) full historical coverage, (c) exact timestamp alignment, (d) automation permission, and (e) license/access conditions.

## Frozen constraints
- Required entry times: 09:45 IST and 13:00 IST; exit: exact 15:15 IST.
- Required instruments: exact NIFTY option contracts and all legs in each selected strategy.
- Need source timestamps, expiry, strike, option side, bid/ask prices and quantities or depth; OHLC/LTP alone is not executable quote evidence.
- No automated extraction from StockMojo because its published terms prohibit scraping/programmatic access.
- Public sample files do not prove target historical date/contract coverage.
- No paid purchase, subscription, account creation, or license acceptance without explicit user authorization.
- Do not upload raw market data to the public repository.

## Method
1. Record each source's published fields, sample file headers/date ranges, advertised full-history coverage, access path, license/terms and limitations.
2. Classify sources separately for factor-feature research and executable quote/depth validation.
3. Verify whether documented free timestamps align with the frozen entry/exit timestamps.
4. Validate the structured source registry and emit a machine-readable decision report.
5. Stop after this bounded audit. Do not weaken timestamp requirements or treat OHLC as spread.

## Acceptance
- Every candidate has source URL, evidence basis, quote/depth fields, temporal coverage, automation permission, licensing/access status and decision.
- Public sample-only data is not promoted to full-history availability.
- The report distinguishes free manual sources from free automatable sources and licensed datasets.
- No purchase is made; the next gate is a user-authorized licensed sample or a newly verified free source.
- Plan, status, error, research, chat and README are updated.

## Status
Plan frozen before audit validation. No strategy evaluation or P&L is performed in Phase 58.
