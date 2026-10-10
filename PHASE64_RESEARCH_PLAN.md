# Phase 64 Research Plan — Paper-Derived CCI NIFTY Options Strategies

## Research question
Does the published CCI-based NIFTY long-option breakout rule produce a robust, net-profitable result in the available intraday option dataset under the project's frozen chronological split and realistic transaction-cost assumptions, and does a separately pre-registered EMA trend filter improve its out-of-sample results?

## Aim
Translate a directly specified published strategy into a deterministic test, inspect the user's fourteen supplied research PDFs, and run two fixed candidates without selecting parameters from validation or using the 2026 holdout.

## Research question and scope
This phase tests the *rule mechanism* described by Pinkal Shaha (2019), not the paper's reported performance. The supplied PDF claims 68 trades across Oct 2008–Sep 2018, ₹145,362 net, 63.25% win rate, and a 100% target / 50% stop. Its results table inconsistently reports 80 total trades while the surrounding text and 43 wins + 25 losses equal 68. The original period is not covered by the selected dataset, so this is an independent reproduction of the rule on a shorter modern sample, not a direct replication.

## Data and fixed date split
- Dataset: Hugging Face dataset `thetrademarkk/india-index-options-1m`, pinned to commit `3eacf762d401efd9a08e804592fa7882b354c4a2`.
- Source: `index/NIFTY.parquet` for underlying intraday OHLC and `options/NIFTY/YYYY-MM-DD.parquet` for option-contract OHLC; contract files are discovered from repository metadata.
- Trading window: only the data needed to construct development and validation is loaded into the backtest. No 2026 option files are downloaded. Any 2026 rows in the index file are removed before feature construction.
- Development: 2021-05-27 through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Protected holdout: all 2026 data; not accessed by the test script and not used for features, selection, hypothesis tests, or plots.
- First eligible CCI signals require adequate 20-day rolling history. EMA variant requires 200 prior daily observations. The script must fail or exclude early rows where those features are unavailable.

## Literature-derived variant A — CCI breakout long option
Based on the written rules in Shaha (2019):
1. Calculate daily NIFTY CCI(20) using typical price (high + low + close)/3 and the standard mean-deviation formula.
2. Call setup when CCI crosses from at/below -100 to above -100. Put setup when CCI crosses from at/above +100 to below +100.
3. The signal day must fall between the 3rd and 15th calendar day of a month. Use the monthly expiry proxy defined as the latest expiry-date file within that same month in the pinned dataset; record any month without a file as unavailable, rather than infer a price.
4. Signal is only known after signal-day close. Therefore, breakout evaluation begins on a subsequent trading day. Within the same month and no later than the 15th calendar day, trigger a call when a later one-minute NIFTY close is at/above the signal-day high, or a put when a later close is at/below the signal-day low.
5. Permit at most one completed position per monthly expiry. Select the earliest qualifying breakout chronologically; if call and put triggers are simultaneous on the same minute, mark ambiguous and skip rather than choosing a favorable direction.
6. At the trigger minute's spot close, select the closest *strictly in-the-money* strike present in that expiry's chain (call strike below spot, put strike above spot). Entry occurs at the next exact one-minute timestamp's observed option close; missing next-minute option observation is an entry-coverage failure.
7. Close the long option at the next exact observed one-minute price after the first close-based target/stop event, or at the last reliable observation on the last trading session before the contract expiry (the source paper's “second-last day” interpretation). Target: observed option close >= 2.0× raw entry close. Stop: observed option close <= 0.5× raw entry close. A target/stop event without the exact next-minute fill is excluded and logged; no forward-fill or interpolation.
8. Final-day terminal exits require an observed option close between 15:24 and 15:29 IST on the penultimate trading session. Otherwise, count exit coverage failure and do not manufacture a terminal price.
9. Apply one adverse ₹0.05 option-price tick on entry and exit for primary execution; no spread inference from OHLC.

## Literature-derived variant B — CCI breakout with EMA trend confirmation
Uses identical entry/exit and costs but adds a fixed filter at the signal-day close:
- Call is eligible only when daily close > EMA(50) > EMA(200).
- Put is eligible only when daily close < EMA(50) < EMA(200).
- Both EMAs use only data available through the signal-day close.
This is a new, preregistered filter adaptation informed by the supplied NIFTY moving-average study, not a direct replication of that paper. No EMA length or CCI threshold is tuned.

## Execution costs and stress cases
- Primary execution: observed option close adjusted by one adverse ₹0.05 option tick at both entry (buy) and exit (sell).
- Apply the existing Phase-43 cost implementation and date-aware historical lot-size schedule, with the following explicit scenarios reported separately:
  1. ₹10 per executed order, base statutory charges.
  2. ₹20 per executed order, same statutory charges.
  3. ₹10/order with +50% fee/charge stress.
  4. ₹20/order with +50% fee/charge stress.
  5. Separate paper-comparability stress of ±10% of option price adverse slippage at entry/exit (not substituted for the primary model).
- Preserve historical STT, exchange transaction charge, SEBI fee, IPFT, stamp duty and GST through the accepted charge function. Show the mathematical treatment of the ₹20 and stressed cases in the output.
- This dataset has OHLC, not historical bid/ask/depth. Results are OHLC-close proxy execution, not executable quote-level fills.

## Statistical plan
- Candidate family is frozen at exactly 2 variants; no additional parameter search in this phase.
- Report results separately for development and validation. Candidate definition is not selected or changed based on validation.
- For each split and candidate: expiry opportunities, signal counts, breakout signals, entries, exits, coverage exclusions, trades, win rate, profit factor, mean/median net trade, net P&L under all cost scenarios, maximum drawdown on chronological trade P&L, and exposure/hold duration where available.
- If validation contains fewer than 20 completed trades or coverage is below 95%, label the validation evidence INSUFFICIENT and do not make a confirmatory promotion claim.
- If sample is adequate, calculate a 95% moving-block bootstrap interval (fixed 3-month blocks over the chronologically ordered monthly trade series) for mean net/trade and a two-sided sign-flip permutation test for mean net/trade, then apply Holm adjustment across the two pre-registered candidates. Record seeds and all exclusions. If sample is inadequate, statistical testing is explicitly skipped instead of presenting unstable p-values.
- No significance test or candidate ranking is computed from 2026.
- The paper's own independent-sample t-test for gain vs loss and inconsistent count table are not reused; those tests do not establish a tradable positive expectancy after the project's costs.

## Quality assurance gates
- Pin and record the dataset revision; hash downloaded source files in runner logs/report, but do not publish raw data or raw-data artifacts.
- Validate schema, timestamps/time zone, option-side/strike keys, duplicate keys and conflicts; true missing bars remain missing.
- Enforce no look-ahead: CCI cross only after daily close; entry must be next minute after a spot trigger; target/stop exits are filled only at a subsequent exact observed minute.
- Use frozen chronological DEV/VAL boundaries; explicitly block 2026.
- Audit that every opened position resolves to a fully observed exit and report failures.
- Workflow installs dependencies, caches only the Hugging Face download cache, has branch-push and manual dispatch triggers, and uploads only aggregate report/plots/summary artifacts. No raw files are committed or artifacts.
- Update plan, status, research log, chat/action log, error log, README, and evidence manuscript regardless of outcome.

## Finite stop rule
Run the two frozen variants once on the available development/validation data. Fix only implementation defects proven by a failed QA gate; record and rerun with a new run label if needed. If the pinned source or required fields are unavailable, record the exact blocker and stop. Do not broaden the parameter grid, use holdout, or promote a strategy merely because this phase runs successfully.

## Output deliverables
- This plan and frozen strategy specification.
- Full literature review of all fourteen user-provided PDFs and selected external papers.
- Reproducible Python runner and GitHub Actions workflow.
- Aggregate JSON/CSV and Markdown scientific report with methodology, results, strengths, limitations, conclusion, and future research.
- Error/chat logs and updated main README.
