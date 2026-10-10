# Phase 103 Error, Defect and Limitation Log

## 2026-10-11 — Initial source screen

### E103-001 — Public stock-option snapshots are not synchronized
**Type:** evidence limitation, not a program defect.  
**Finding:** public pages surfaced for HDFCBANK, ICICIBANK, RELIANCE, SBIN and INFY carry different crawl/market timestamps and different presentation/turnover semantics. They cannot support a truthful cross-stock quantitative liquidity rank as-is.  
**Resolution:** select an explicitly provisional initial universe from the official constituent-weight snapshot plus visible contract discovery evidence; require a common-window quantitative liquidity and data-quality audit in Phase 103.1 before any strategy P&L is evaluated.

### E103-002 — Current constituent snapshot is dated 2026-02-27
**Type:** time/provenance limitation.  
**Finding:** official NIFTY 50 whitepaper gives the cited weights as at 2026-02-27, not a synchronized 2026-10-11 live rank.  
**Resolution:** preserve the snapshot date beside every weight and refresh official membership/weights at Phase 103.1. Do not describe them as today's weights.

### E103-003 — Historical options data rights and fill quality unknown
**Type:** pending research gate.  
**Finding:** public quote/option-chain pages prove discovery only; they do not grant programmatic scraping, retention or publication rights and do not establish bid/ask/depth coverage for the backtest horizon.  
**Resolution:** source audit records rights and exact sample coverage before acquisition or modeling. Stop NO-GO if no authorized sample suffices.

No runtime execution error is recorded at initialization. Any failed workflow/run must be appended here with run URL, symptom, cause, correction and final verification. Resolved errors must never be removed.


### E103-004 — Dhan rolling-option data is not an exact fixed-contract tape
**Type:** source/model limitation.  
**Evidence:** Dhan's official endpoint describes data by relative strike (ATM and offsets) and documents OHLC, IV, volume, OI, strike and spot, not historical bid/ask/depth.  
**Risk:** an ATM-offset series can change actual strike over time. Treating its entire path as one persistent contract would misstate contract P&L; using OHLC as an executable quote would overstate fill certainty.  
**Resolution:** store the actual strike timestamp series, reconstruct exact contract identity only when it can be proven, exclude unresolved paths from P&L, and require an authorized source or clearly labelled conservative cost/fill proxy for spread/slippage. Never call this endpoint alone proof of an executable historical fill.

### E103-005 — Raw Dhan data retention/republication terms not yet confirmed
**Type:** data-governance limitation.  
**Risk:** committing or publicly artifacting raw API rows may exceed the subscription or market-data licence permitted use.  
**Resolution:** API audit emits aggregate counts and timestamp ranges only. Raw values remain ephemeral until permitted storage/retention rights are confirmed. The research still needs reusable data storage for later phases; use an approved private store if applicable rather than publishing raw market data to this public repository.
