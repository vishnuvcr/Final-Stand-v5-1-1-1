# Phase 98 — NIFTY Opening-Range Breakout with Defined-Risk Debit Spreads

**Branch:** phase-98-nifty-opening-range-debit-spread  
**Registered:** 2026-10-10 (Asia/Kolkata)  
**Parent:** phase-97-risk-adjusted-regime-selection  
**Status:** PREREGISTERED — runtime feasibility and strategy test pending  
**Primary objective:** test a new causal entry/exit hypothesis, not another ranker on the old strategy-summary table.

## 1. Research question

Does a NIFTY 15-minute opening-range breakout, expressed through a near-the-money defined-risk debit vertical, produce positive session-level expectancy after historically applicable Paytm Money brokerage, exchange/statutory levies, GST, one-tick adverse entry/exit slippage, and a more severe cost/price stress? Does a fixed, prior-close India VIX extreme-risk filter improve that outcome without validation tuning?

## 2. Why this is a new hypothesis

Phases 95–97 tested selection methods on the already explored Phase 45 summary table. They did not conduct new trade-level market replays and all selected validation endpoints were negative. Phase 90 showed a small 2024 incremental IV magnitude-prediction gain that did not independently replicate in Phase 91; Phase 92's combined synthetic-forward proxy/OI block worsened its target prediction. Those results do not justify another feature/ranking sweep.

Phase 98 tests a different mechanism: a breakout in observed underlying price, entry after the signal bar completes, a defined-risk directional option structure, and deterministic target/stop/time exits. It makes no claim that a breakout or a VIX filter is already profitable.

## 3. Data, time boundaries and governance

- Primary source: Hugging Face dataset thetrademarkk/india-index-options-1m, repository revision frozen to 0f4800e43e6f96cec0794369d78eb4d3c4211ef5 when available.
- Source files: index/NIFTY.parquet and options/NIFTY/{EXPIRY}.parquet.
- Time zone: Asia/Kolkata. Minute bars are treated as timestamped at the start of the minute.
- Development: 2021-05-27 through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Do not load any option expiry after 2025-12-31, any timestamp in 2026, HOLD rows, or the protected Phase 83 2026 holdout. Sessions that would require a 2026 expiry chain are excluded and counted.
- Raw option files remain in ephemeral/cache storage and are not published as workflow artifacts. Only aggregate data-quality reports and derived P&L ledgers are persisted.
- If the pinned revision is unavailable, required columns are absent, or exact-contract coverage is inadequate, record the specific feasibility failure and do not silently substitute a source, timestamp, fill, or parameter.

## 4. Frozen strategy arms

### Arm A — opening-range breakout debit spread

1. Require all 15 underlying bars from 09:15 through 09:29 IST. The opening range is the maximum high and minimum low from these bars.
2. Scan completed underlying bars timestamped 09:30 through 14:45 IST in time order. The signal is the first close strictly above the opening-range high (bullish) or strictly below its low (bearish). At most one signal/trade per session.
3. The signal bar completes one minute after its timestamp. The first possible entry is the next minute's exact observed option-bar open. No signal-close fills, proxy prices, interpolation, or forward-fill.
4. Choose the nearest listed expiry on or after the session. The common strike is the nearest strike to the signal-time underlying close that exists for both CALL and PUT in the exact expiry chain. Define one strike step by the modal adjacent strike spacing at the signal timestamp.
5. Bullish: buy one-lot ATM CALL and sell one-lot CALL two strike steps above ATM. Bearish: buy one-lot ATM PUT and sell one-lot PUT two strike steps below ATM. Both legs must have exact, positive, observed entry opens. If per-minute volume/OI fields are available, log them at signal/entry time; never treat absent OI as an observed zero. Volume/OI do not create additional post-hoc filters in the primary strategy.
6. Apply one adverse ₹0.05 tick to every leg-side fill in the base case. The initial debit is long-leg entry fill minus short-leg entry fill and must be strictly between zero and the vertical width.
7. Evaluate paired observed closing marks beginning at the entry minute. Target: spread mark >= initial debit + 50% of (vertical width − initial debit). Stop: spread mark <= 50% of initial debit. If either threshold is met on a completed bar, exit both legs at the next minute's exact observed open. If neither is met, time-exit at the exact 15:15 IST open.
8. Never infer a fill on a missing bar. Require at least 95% paired-minute close coverage through the recorded trigger/time-exit point; report gaps separately. If an exit-minute open for either leg is unavailable, the campaign is incomplete and excluded from P&L. Do not continue searching later prices.

### Arm B — same entry/exit with a frozen high-volatility exclusion

Arm B follows all of Arm A's rules, but skips the trade when the prior trading session's India VIX close is above the 75th percentile of the preceding 252 available VIX closes. All quantiles use prior sessions only. This is a fixed risk filter, not a parameter grid. If its prior-only history is too short or unavailable, the Arm B session is unavailable and is counted rather than inferred. Arm A remains the unfiltered comparator.

## 5. Execution and costs

- One lot per leg; no pyramiding or concurrent entries from the same session.
- Base case: one adverse ₹0.05 tick on each leg on entry and exit; ₹10 Paytm Money brokerage per unique executed F&O order; date-aware historical STT, exchange transaction charge, SEBI fee, IPFT, stamp duty and 18% GST on applicable charges.
- Severe stress: two adverse ₹0.05 ticks per leg on every fill, ₹20 per order, and 1.5× statutory/transaction fee rates. Brokerage is ₹20/order (not multiplied again by 1.5).
- Use the date-aware NIFTY lot schedule fixed from the repository's accepted historical engine. Validate the schedule against the source registry before numerical acceptance.
- Report premium-turnover costs by component, base net P&L, stressed net P&L and coverage. Prices remain OHLC proxies, not bid/ask/depth or guaranteed live fills.
- No return percentage or portfolio-capital return is inferred without a validated capital denominator. Maximum theoretical spread loss is used only as a structural risk measure, not as margin.

## 6. Frozen splits and statistical analysis

- Development (2021–2023): descriptive debugging and rule-feasibility only. Do not alter the strategy after viewing its outcomes.
- Validation (2024–2025): primary evaluation. Keep the date universe of all eligible index sessions and record zero P&L for days with no strategy trade; no trade is not a missing return.
- Primary efficacy gate for Arm A: at least 100 complete validation trades, positive mean net P&L per trading session in base cost and severe-stress profitability not negative.
- Primary comparison for Arm B: paired session-level net P&L uplift over Arm A, on the same full session calendar including zero-return/no-trade sessions. Require at least 100 complete validation trades in Arm B to interpret the filter inferentially.
- Use 10,000 resamples of the validation daily series in non-overlapping five-session blocks for 95% confidence intervals. Use 10,000 one-sided paired sign-flip draws at the session level for predeclared positive-mean / uplift tests. Apply Holm correction to the two predeclared primary tests. Publish the exact seed, sample counts and interval endpoints. If sampling gates fail, mark inferential outcomes NOT ESTIMABLE / DESCRIPTIVE, not a pass.
- Report P&L, trade count, mean and median per trade, win rate, profit factor, maximum drawdown, worst trade, 95% expected shortfall, fees by component, slippage stress, monthly/yearly stability, OR signal counts, OI/volume availability when present, coverage and every exclusion reason.
- Trade-level returns are not IID. Include date/month/expiry concentration diagnostics; do not count individual option legs as independent observations.

## 7. Promotion gate and stopping rule

Phase 98 cannot promote a strategy for live trading. Even a positive validation result is only a research lead requiring a new independent, preregistered confirmation phase. No 2026 holdout will be opened to rescue or confirm Phase 98.

Report a research PASS only for complete, audited computation; economic evidence is a separate decision. A candidate may be described as validation-promising only if both primary gates, adequate trade/coverage gates, positive base and stress P&L, sensible drawdown/concentration and Holm-adjusted inference all pass. Otherwise record FAIL, INSUFFICIENT EVIDENCE, or BLOCKED with no parameter changes.

Stop after one frozen strategy test, audit, inference, and manuscript/report publication. Do not run another opening-range/time/strike/target/stop grid under Phase 98.

## 8. Required repository outputs

- research/phase98_opening_range_spread.py
- tests/test_phase98_opening_range_spread.py
- .github/workflows/phase98-opening-range-spread.yml
- results/phase98_opening_range_spread/report.md
- summary.csv, coverage_audit.csv, trade_ledger.csv, inference.json, decision.json, source_manifest.json, validation_report.json
- PHASE98_STATUS.md, PHASE98_ERROR_LOG.md, PHASE98_RESEARCH_LOG.md, PHASE98_CHAT_LOG.md
- Root README and root research/error logs updated on this branch. Raw market data are never copied into the repository.

## 9. Literature / source context

1. Existing Phase 43/45 manuscripts document regime-conditioned NIFTY option studies; Phase 45 itself concluded NO PROMOTION. Their old positive cells are not selection inputs.
2. Phase 90/91 are an annual replication pair for IV's small magnitude-prediction gain; Phase 91 did not establish the gain. Phase 92 found its registered rolling-ATM synthetic-proxy/OI block degraded the studied magnitude predictor. These are context only, not direct breakout evidence.
3. Public NIFTY option OHLCV(+OI) data are incomplete for far strikes/illiquid contracts and lack historical quotes/depth; all OHLC-based fills must be labelled modeled.
4. Relevant general safeguards: Bailey & López de Prado (2014), The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality, Journal of Portfolio Management 40(5), 94–107, DOI 10.3905/jpm.2014.40.5.094. Phase 98 uses a single hypothesis pair and no search grid, with independent confirmation required before promotion.
5. Supplementary, source-quality-stratified literature review: [PHASE98_LITERATURE_REVIEW.md](PHASE98_LITERATURE_REVIEW.md). It covers ORB evidence, Indian options/volatility studies, official India VIX methodology, multiple-testing safeguards, broker tariffs, targeted practitioner/video material, and the pinned dataset's coverage caveats. It is context only and does not change the preregistered test.

## 10. Phase checkpoints

| Step | Gate | Status at registration |
|---|---|---|
| 0 | Check prior README, plans, logs and workflow results | COMPLETE |
| 1 | Freeze question, rules, splits, costs and inference before outcomes | COMPLETE |
| 2 | Implement unit-tested signal/price/cost methods | PENDING |
| 3 | Run pinned-source schema and exact-time/contract coverage audit | PENDING |
| 4 | Run development and validation replay | PENDING |
| 5 | Reconcile output artifacts, exclusion ledgers and inference | PENDING |
| 6 | Publish report/manuscript, update README/research/error/chat logs | PENDING |
| 7 | Close phase and open a separate confirmation phase only if justified | PENDING |

No data results exist at preregistration.
