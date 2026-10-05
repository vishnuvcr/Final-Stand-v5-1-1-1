# Phase 32 Strategy Specification — Continuous Delta 6x6 Vertical Spread

## Trading state
target_dir is a runtime state variable.
- +1 = CALL spread.
- -1 = PUT spread.
Initial state: +1.

## CALL spread
Entry requires:
1. target_dir == +1
2. open NIFTY 50 position count = 0
3. time >= 09:20 IST
4. today != current weekly expiry day

Legs:
- SELL 6 lots current-week CE at the strike whose delta is +0.25.
- BUY 6 lots current-week CE at that strike + 50 points.

Exit:
- first observation where short CE delta >= +0.50 OR short CE delta <= +0.04.
- close the complete spread.

## PUT spread
Entry requires:
1. target_dir == -1
2. open NIFTY 50 position count = 0
3. time >= 09:20 IST
4. today != current weekly expiry day

Legs:
- SELL 6 lots current-week PE at the strike whose delta is -0.25.
- BUY 6 lots current-week PE at that strike - 50 points.

Exit:
- first observation where short PE delta <= -0.50 OR short PE delta >= -0.04.
- close the complete spread.

## Post-trade direction
Let net_trade_pnl be the complete two-leg net P&L after modeled costs.
- net_trade_pnl > 0 -> keep target_dir.
- net_trade_pnl < 0 -> target_dir = -target_dir.
- net_trade_pnl == 0 -> keep target_dir.

## Continuous operation
After exit, the engine may take another trade on the same trading day when all entry conditions are met. There is no daily trade-count cap in the frozen specification.

No new entry is permitted on weekly expiry day.
No 15:25 universal exit is used.
No discretionary rollover is used.

## Contract expiry
Open positions that survive until contract expiry are terminated at the contract boundary according to the audited historical settlement/executable-price convention. This does not count as a delta-triggered exit and is reported separately.

## Important implementation note
The real-time Tradetron description says execution is continuous/every tick. The repository's reproducible public primary data are 1-minute. The Phase-32 historical result therefore represents a 1-minute-bar backtest of a tick-driven strategy, not literal tick replay. This distinction must remain visible in every result and conclusion.