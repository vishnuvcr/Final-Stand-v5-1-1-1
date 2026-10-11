# Phase 106 Error and Limitation Log

## Registered limitations
- Later calendar window does not guarantee statistical independence.
- Daily OHLC bars do not contain historical bid/ask, depth, queue, latency, partial-fill or market-impact evidence.
- Slippage values are scenarios, not observed spread estimates.
- Account-specific Paytm Money brokerage and contract notes remain unverified.
- The sample covers 21 sessions and 19 post-warm-up outcome sessions; statistical uncertainty remains substantial.

## E106-001 — No candidate robustly positive after costs
The primary case (₹20/order, ₹0.25/unit/side slippage, 1.0× modeled fees) was negative for all three candidates. Strict stress made all three more negative. This is a strategy-result blocker, not a runtime error. No tuning or promotion is permitted in this phase.

## Runtime status
The verified Phase 106 workflow passed source and accounting gates and produced 72 scenario rows. No raw market rows or trade-by-trade price records are published.