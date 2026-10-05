# Phase 32 — Frozen Strategy Rule Card

**Status:** Research candidate only. Not promoted to live trading.

1. Underlying: NIFTY 50.
2. Capital reference: ₹6,00,000.
3. Position size: 6 lots per leg.
4. Spread width: 50 points.
5. Expiry: current weekly expiry.
6. Initial direction: CALL.
7. New entries start at 09:20 IST.
8. No new entry on expiry day.
9. No fresh action during the final 120 seconds before the 15:30 close; the 1-minute engine blocks new entries at or after 15:28 IST.
10. CALL entry: sell the available CE whose model delta is nearest +0.25; buy the same-expiry CE at short strike +50.
11. PUT entry: sell the available PE whose model delta is nearest -0.25; buy the same-expiry PE at short strike -50.
12. CALL exit: entire spread exits on the first observation where short CE delta >= +0.50 or <= +0.04.
13. PUT exit: entire spread exits on the first observation where short PE delta <= -0.50 or >= -0.04.
14. Positive **net** trade P&L: retain direction.
15. Negative **net** trade P&L: flip direction.
16. Exact zero net P&L: retain direction.
17. No universal daily square-off.
18. No discretionary rollover.
19. Existing positions may cross sessions until delta exit or reproducible contract termination.
20. Costs must include brokerage, statutory charges and adverse execution slippage.

No entry threshold, exit threshold, spread width, direction rule or size adjustment was optimized after observing the results.
