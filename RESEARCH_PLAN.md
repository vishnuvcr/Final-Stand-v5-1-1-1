# Research Plan — OTM6/OTM7/OTM8 Ratio Strategy

## Phase 1 — Strategy definition and data validation
- Define OTM6/7/8 as the 6th/7th/8th OTM strike from the nearest ATM strike at the 10:00 IST entry snapshot.
- Working underlying: NIFTY 50 weekly index options, because the request did not specify an underlying.
- Entry: 4-DTE market-session convention: enter on the fourth trading session counting the expiry session as session 1, at 10:00 IST.
- Strategy 1: +1 OTM6 PE, -1 OTM7 PE, -1 OTM8 PE.
- Strategy 2: +1 OTM6 CE, -1 OTM7 CE, -1 OTM8 CE.
- Selection: P = premium(OTM7)+premium(OTM8)-premium(OTM6); trade the side with higher P.
- Exit target: derive the expiry payoff flatline profit from actual strikes and entry premium, then test it net of costs.
- Fallback exit: expiry-day 15:29 IST mark unless stop-loss/profit target occurs first.
- Stop-loss research: compare fixed loss, premium-relative loss, and structural breach rules without choosing one before out-of-sample validation.
- Costs: Paytm Money brokerage plus statutory charges and configurable slippage; STT must be date-aware.

## Phase 2 — Backtest
- Use 1-minute historical option OHLC plus NIFTY spot/index OHLC; primary clean sample is 2024-01-01 through 2025-12-31 because the selected public dataset is incomplete in parts of 2026.
- Download only required weekly expiry files; cache raw downloads in GitHub Actions and persist compact filtered observations/results in the repository.
- Use close-based execution for the base test, then stress adverse one-tick-per-leg and percentage slippage.
- Record every trade's strikes, premiums, strategy, entry/exit, gross/net P&L, costs, MAE, MFE, and exit reason.
- No look-ahead: strikes are selected only from the 10:00 entry snapshot.

## Phase 3 — Stop-loss selection
- Train candidates only on an early chronological sample.
- Candidate SLs: 0.25x/0.50x/0.75x/1.00x entry flatline; 1.0x/1.5x/2.0x initial premium magnitude; structural breach/breakeven rules.
- Compare expectancy, median trade, worst trade, max drawdown, profit factor, hit rate, tail loss, and slippage sensitivity.
- Validate the selected candidate on a later holdout.

## Phase 4 — Robustness
- Year and volatility-regime analysis.
- Slippage/fee sensitivity.
- Entry-time sensitivity around 09:45–10:15.
- DTE sensitivity around 3–5 calendar days.
- Strike-distance sensitivity around OTM5–OTM9.
- Missing/illiquid quote sensitivity.

## Phase 5 — Research manuscript
- Produce methods, results, statistical analysis, charts, tables, appendices, limitations, conclusion, and future research.

### Stop condition
Stop after Phase 5. Live-trading automation is outside this research unless separately requested.
