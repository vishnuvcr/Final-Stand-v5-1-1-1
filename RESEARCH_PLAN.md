# Research Plan — OTMn / OTM(n+1) / OTM(n+2) Selection Strategy

## Research question
Does the specified dynamic 3-leg ratio strategy produce positive risk-adjusted net returns after realistic transaction costs and slippage when tested on historical NIFTY 50 weekly index options?

## Exact strategy specification
At the 10:00 IST entry snapshot, for every n = 6,7,...,15:

- Put X(n) = PE(n+2) + PE(n+1) - PE(n)
- Call X(n) = CE(n+2) + CE(n+1) - CE(n)

Compute all 20 X values. Select the single largest X across both option types and all n.

If the winner is Put, enter:
- Buy 1 × OTMn Put
- Sell 1 × OTM(n+1) Put
- Sell 1 × OTM(n+2) Put

If the winner is Call, enter:
- Buy 1 × OTMn Call
- Sell 1 × OTM(n+1) Call
- Sell 1 × OTM(n+2) Call

The OTM rank is measured from the nearest ATM strike at the 10:00 entry snapshot. For n=15, the data must contain OTM17.

## Entry
- Target entry: 4 DTE at 10:00 IST.
- Base calendar convention: for ordinary Thursday weekly expiries, this is Monday 10:00 IST.
- Holiday/exception handling must be explicit and logged rather than silently inventing a timestamp.
- No look-ahead: only information available at the entry timestamp may determine ATM, strikes, X values, and the selected trade.

## Exit
1. Profit target: 90% of the initial credit X × lot quantity.
2. If the target is not reached, exit the complete position at 0 DTE / expiry according to the defined historical execution convention.
3. There is NO stop-loss in the requested strategy. Do not introduce one into the primary backtest.

## Costs and execution
Report gross and net results separately. Net results must account for:
- Paytm Money brokerage assumptions documented from current/period-appropriate public fee information.
- Exchange transaction charges.
- SEBI charges.
- GST.
- STT.
- Stamp duty.
- Configurable slippage.
- Lot quantity effective on the trade date.

The target is defined from the initial collected credit; costs are deducted from realized P&L rather than changing the 90% target definition.

## Research phases
### Phase 1 — Strategy definition and data validation
Lock formulas, strike ranking, DTE convention, exit rule, cost model, data fields, and missing-data policy.

### Phase 2 — Primary backtest
Run the complete n=6..15 × Call/Put selection across the longest validated minute-level NIFTY sample available. The current primary acquisition target is approximately February 2019 through September 2026. Thetrademarkk/india-index-options-1m covers the later period; the Zenodo 2017–2020 source is being validated for the eligible 2019–2020 weekly-options portion. 2017–2018 is excluded because NIFTY weekly options were not yet available.
Persist raw/filtered data metadata, trade-level results, missing observations, and summary statistics.

### Phase 3 — Statistical analysis
Compute aggregate and stratified performance: trade count, hit rate, mean/median P&L, standard deviation, profit factor, expectancy, cumulative P&L, drawdown, Sharpe/Sortino where appropriate, target-hit rate, holding time, and bootstrap confidence intervals. Analyze selection by n and side without ranking political or other unrelated choices.

### Phase 4 — Robustness and sensitivity
Test slippage/fees, entry timing, DTE convention, data completeness/liquidity filters, volatility regimes, and year-by-year stability. These are sensitivity analyses, not changes to the primary strategy.

### Phase 5 — Research manuscript
Produce a reproducible manuscript with research question, aims/objectives, literature/data review, methodology, results, statistical analysis, discussion, strengths, limitations, conclusion, future research, charts, tables, appendices, and supplements.

## Stop condition
Stop after Phase 5. Do not convert the research into live-trading automation unless separately requested.

## Phase branch policy
Each phase has a dedicated Git branch and manually runnable GitHub Actions workflow. Results and research-status files are updated at every completed step.

## Reproducibility/data policy
Prefer cached repository/Actions artifacts and immutable data manifests. Do not redownload unchanged data unnecessarily. Every data gap, execution error, methodological change, or failed workflow must be recorded in ERROR_LOG.md.
