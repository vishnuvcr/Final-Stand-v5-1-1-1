# Phase 108 Research Plan — Volatility-Regime Candidates

Branch: `phase-108-volatility-and-market-regime-rules`

## Question
Do simple low/high realized-range regimes change the after-cost outcomes of long-option momentum and reversal rules?

## Registered additions
Keep all six Phase 107 rules. Add LOW_VOL_MOMENTUM, HIGH_VOL_MOMENTUM, LOW_VOL_REVERSAL and HIGH_VOL_REVERSAL. The volatility proxy is based on the range of valid option OHLC bars relative to underlying close, and the regime threshold is a median of preceding estimates only. It is not India VIX or implied volatility. Rules are exploratory and no winner will be promoted.

## Fixed data and costs
- Official NSE daily UDiFF F&O archives; same five stocks and Phase 107 window, 2026-09-02 inclusive to 2026-10-02 exclusive.
- Same contract selection, OHLC validity and next-session open-to-close proxy.
- Brokerage ₹10/₹15/₹20 per order × slippage ₹0/₹0.05/₹0.25/₹0.50 per option unit per side × modeled fees 1.0×/1.5×.
- Ten strategies × 24 cost scenarios = 240 rows.

## Phases
108.0 freeze; 108.1 tests; 108.2 source gate; 108.3 replay/accounting; 108.4 publish report, summaries, logs and README. Stop after this bounded screen.

## Inference limits
This reuses the already-inspected Phase 106/107 sample, so all findings are exploratory and multiple-comparison biased. Bootstrap intervals are descriptive. OHLC and assumed slippage do not establish executable fills, spreads, depth, latency, partial fills or impact. Paytm Money account-specific costs are unverified. No strategy promotion.
