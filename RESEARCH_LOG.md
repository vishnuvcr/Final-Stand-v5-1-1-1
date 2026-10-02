# Research Log

## 2026-10-02 — Phase 1 start
- Repository inspected: empty at initialization.
- Working underlying assumption: NIFTY 50 weekly index options.
- OTM6/7/8 interpreted as the 6th/7th/8th OTM strikes from ATM.
- Structure identified as an asymmetric 1-long/2-short ratio structure with an uncovered tail; it is not a defined-risk butterfly.
- Candidate data source: thetrademarkk/india-index-options-1m, documenting 1-minute NIFTY spot and option-chain parquet files from 2021–2026.
- NSE historical F&O data and option-chain pages identified for validation.
- Paytm Money documentation confirms ₹10 brokerage per unique executed F&O order; statutory charges are additional and time-varying.
- No numerical performance conclusion yet; workflow execution/data validation is pending.

## 2026-10-02 — methodology correction
- The initial 4-calendar-day implementation produced only 34 trades because Thursday weekly expiries map four calendar days earlier to Sunday.
- Corrected DTE convention to the fourth trading session counting expiry as session 1, which maps ordinary Thursday expiries to Monday and handles holiday weeks using actual spot trading sessions.
- Base profit target set to 90% of the positive entry flatline premium; this fraction remains a parameter for Phase 3 sensitivity testing.
