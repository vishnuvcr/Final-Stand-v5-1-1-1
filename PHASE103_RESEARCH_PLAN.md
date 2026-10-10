# Phase 103 Research Plan — Novel Intraday NIFTY Options Strategies

**Branch:** `phase-103-novel-intraday-strategy-discovery`  
**Parent:** `phase-102-final-strategy-ranking`  
**Test period:** development calendar year 2024; chronological validation calendar year 2025  
**Option source:** `thetrademarkk/india-index-options-1m`, pinned revision `3eacf762d401efd9a08e804592fa7882b354c4a2`, CC-BY-NC-4.0  
**Data rule:** no 2026 options are downloaded or evaluated; 2021–2023 underlying observations are used only for rolling warm-up where needed.  
**Decision rule:** this finite discovery phase may identify a candidate for *new independent validation*, but cannot approve live use.

## 1. Research questions

1. Can new entry/exit rules based on opening-range continuation, failed-breakout reversal, or low-range/low-VIX compression produce positive NIFTY weekly-options results after realistic execution-cost assumptions?
2. Does confirmation by previous-session cross-market breadth improve an opening-range breakout's trade quality?
3. Does explicitly stopping on range failure or short-strike breach preserve risk better than a fixed end-of-day close?
4. Does any rule maintain positive net P&L under doubled adverse tick slippage, ₹20/order brokerage and +50% charge stress?
5. Are observed results large and stable enough to justify one new independent confirmatory test?

## 2. Three preregistered strategy hypotheses

All strategies make at most one intraday position per session, use observed listed contracts, one historical lot per leg, and hard-close intraday. They use only information available before the entry fill and never forward-fill prices.

### S103-A — Cross-market-confirmed opening-range breakout debit spread (XAC-ORB)

- Opening range: NIFTY high/low from observed 09:15–09:29 bars.
- Search for the first close after 09:29 beyond that range, no later than 14:30.
- Cross-market filter: prior-session returns for SP500, NASDAQ, DOW and NIKKEI must have at least three observed values; at least three must share the breakout sign. If breadth does not confirm, abstain.
- Bullish: buy one nearest-ATM CE and sell one CE 100 NIFTY points higher. Bearish: buy one nearest-ATM PE and sell one PE 100 points lower.
- Entry uses the first complete observed next-minute option OPEN snapshot within five minutes of the signal. Exit at the next observed OPEN after a close re-entering the opening range, or the 15:14 decision bar followed by a fill no later than 15:20.
- This is a bounded-risk debit spread, not an uncapped long option.

### S103-B — Failed-breakout reclaim reversal debit spread (FBR)

- Use the same observed 09:15–09:29 opening range.
- Wait for the first close outside the range. If a subsequent close re-enters the range within the next five observed one-minute bars, enter the opposite direction; no same-candle high/low sequencing is assumed.
- Failed high breakout: buy a nearest-ATM PE debit spread (long PE at ATM, short PE 100 points lower). Failed low breakout: buy a nearest-ATM CE debit spread (long CE at ATM, short CE 100 points higher).
- Stop if a subsequent spot close crosses the frozen breakout extreme; target the opposite opening-range boundary; otherwise hard-close via the 15:14 decision bar and next complete option OPEN snapshot.
- If the first breakout does not reclaim inside five bars, no trade is taken that session.

### S103-C — Prior-range-compression / low-India-VIX iron condor (RC-VIX-IC)

- Compute the first 45-minute NIFTY high-low range from 09:15–09:59.
- Entry is eligible only when that range is below the median range of the preceding 20 observed sessions (strictly lagged) **and** the prior-session India VIX close is at or below its trailing 60-observation 75th percentile.
- At the 10:00 decision time, sell one CE at ATM+100 and buy one CE at ATM+200; sell one PE at ATM−100 and buy one PE at ATM−200. Exact listed strikes are required.
- Stop/exit on the next complete option OPEN after a spot close crosses either short strike; otherwise hard-close at 15:14 / next complete option OPEN.
- The wings define the expiry risk. A stop fill can still suffer gaps/slippage and is not represented as guaranteed max-risk.

Parameters are fixed before running outcomes. No strike-width, time-window, VIX threshold, signal duration, or exit tuning is allowed during Phase 103.

## 3. Data, sourcing and feature gates

- Load the point-in-time NIFTY minute OHLC bars and matching listed option expiry files from the pinned Hugging Face revision. Use only expiry files dated on or before 2025-12-31.
- Use committed previous-session global-market features under `results/phase39_feature_source/global_daily.parquet` and committed India VIX daily data `data/phase40_vix/india_vix.csv`; use strict backward joins only.
- Audit FII/DII and news-sentiment coverage from the repository's prior-publication source tables. They are not inserted into the primary rules unless the source is sufficiently complete and explicitly point-in-time; a missing value will never be filled. The currently committed Phase 39 feature manifest shows FII/DII absent throughout its 2024–2025 validation features, so the primary rules do not depend on these inputs.
- Synthetic futures, Greeks, live option depth and contemporaneous bid/ask are not present in the pinned OHLC source and will not be fabricated. These are logged as future execution-data requirements.
- Source license CC-BY-NC-4.0 is acceptable only for this bounded non-commercial research use; it is not evidence of commercial redistribution/use rights for a deployed system.

## 4. Execution and cost models

Primary run:
- observed option OHLC OPEN used for entry/exit, only at next available timestamp after signal;
- one adverse ₹0.05 tick on each leg fill;
- ₹10 brokerage per order;
- date-effective brokerage/turnover/STT/stamp/IPFT/SEBI/GST schedule encoded from the existing repository execution helper;
- historical NIFTY lot size for the chosen expiry;
- no price interpolation or forward fill.

Stress models:
1. **Registered friction stress:** two adverse ₹0.05 ticks per fill, ₹20/order brokerage, and +50% statutory/turnover charge stress.
2. **Severe impact stress:** baseline one-tick slippage plus additional 0.25% adverse price impact per fill, ₹20/order, +50% charges and an additional ₹50 per round trip.

These are simulations from OHLC bars, not verified Paytm Money contract-note costs or proof of executable fills. Costs are calculated per leg/order, not as a single flat percentage of P&L.

## 5. Sample, inference and promotion gates

- Development: eligible sessions in 2024. Descriptive only.
- Validation: eligible sessions in 2025. This is the main selection/validation screen; 2026 remains out of scope.
- Each strategy is scored on the full set of eligible sessions with zero P&L on days without a signal, so the primary statistic is mean net P&L per calendar trading session rather than a selective per-trade mean.
- Use a deterministic five-session circular moving-block bootstrap (5,000 resamples) for the 2025 mean daily net P&L interval and one-sided null test. Apply Holm correction across the three preregistered strategies.
- Also report trades, signal coverage, failed entries/exits, win rate, profit factor, cumulative net, and trade-order/cumulative daily drawdown. No trades or no complete fills are not treated as zero-profit evidence for per-trade expectancy.
- Promotion eligibility (never automatic approval): ≥30 completed 2025 trades, ≥95% complete execution coverage among signals, positive base/stress/severe-stress net P&L, 95% block-bootstrap CI lower bound above zero for mean daily net, Holm-adjusted p<0.05, no accounting/data error, and cumulative daily drawdown ≤₹60,000 against a fixed ₹3,00,000 one-lot research account reference. Because 2026 option data are excluded and the source has non-commercial licensing, passing this screen could only nominate an independent validation candidate.

## 6. Planned steps and finite stopping rule

- **103-A — preflight:** test data schemas, pinned revision access, expiry-date universe, cost helper and rule-specific signal functions.
- **103-B — deterministic replay:** evaluate all three frozen rules over 2024–2025. Log every signalled but unfilled trade and every exit coverage gap.
- **103-C — inference and robustness:** calculate baseline and two stress ledgers, session-block bootstrap and Holm-adjusted validation results.
- **103-D — audit/publication:** run unit tests; reconcile ledger counts/net P&L; publish CSV/JSON/graph/report; update status, research log, error log and root README links.
- **Finite stop:** Phase 103 ends after one complete replay/audit cycle. If inputs or coverage fail, record the blocker and stop; do not tune the rules until they “work.” Any promising candidate needs a separately preregistered follow-up with fresh authorized sample, quote/depth and independent holdout.

## 7. Required outputs

- `results/phase103/trades.csv`, `daily_pnl.csv`, `coverage_audit.csv`, `summary.csv`, `feature_coverage.json`, `validation.json`, `PHASE103_REPORT.md`, and an SVG comparison chart.
- `research/phase103/novel_intraday_strategies.py` and deterministic unit tests.
- `PHASE103_STATUS.md`, `PHASE103_RESEARCH_LOG.md`, `PHASE103_ERROR_LOG.md`, and `PHASE103_CHAT_LOG.md`.
