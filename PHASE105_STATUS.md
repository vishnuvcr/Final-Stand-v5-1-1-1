# Phase 105 Status — EOD OHLC Strategy Pilot

**Updated:** 2026-10-11  
**Branch:** `phase-105-eod-ohlc-strategy-pilot`  
**State:** REGISTERED — implementation and runtime result pending  
**Promotion:** NONE  
**Parent evidence:** Phase 104 EOD identity/OHLC audit passed; no Phase 104 P&L was calculated.

## Frozen scope

- Universe: HDFCBANK, ICICIBANK, INFY, RELIANCE, SBIN.
- Sample: 2026-08-03 inclusive to 2026-09-02 exclusive.
- Three candidates only: MOMENTUM_ATM, REVERSAL_ATM, MOMENTUM_OI_CONFIRM.
- Entry proxy is next session open; exit proxy is that session's close; contract selection uses only prior-session data.
- Costs: Paytm Money brokerage sensitivity ₹10/₹15/₹20 per order; Phase 104's date-effective fee engine; slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side; fee multiplier 1.0×/1.5×.
- Raw NSE rows/prices/trade-by-trade records must remain ephemeral; only aggregates and hashes may be published.

## Step status

- [x] 105.0 Registration and scope freeze.
- [ ] 105.1 Reacquire source and pass data/identity/OHLC integrity gate.
- [ ] 105.2 Unit tests and chronology/leakage checks.
- [ ] 105.3 Frozen replay, costs/slippage, aggregate outputs.
- [ ] 105.4 Accounting review, manuscript, logs and README closeout.

## Current decision

No empirical outcome has been accepted yet. This month-long previously inspected data sample is exploratory and is not an independent holdout. Positive proxy returns cannot establish real-world executability or live profitability.
