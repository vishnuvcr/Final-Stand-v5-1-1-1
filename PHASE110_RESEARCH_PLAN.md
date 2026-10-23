# Phase 110 — Greek-Conditioned Stop-Loss Research Plan

**Branch:** phase-110-greek-stoploss-short-strangle  
**Parent:** main (read-only lineage; prior research branches are not modified)  
**Registered:** 2026-10-23 (Asia/Kolkata)  
**Instrument assumption:** NIFTY weekly index options, inferred from the Final Stand repository's index-options datasets and prior work.  
**Research state at registration:** plan frozen; empirical execution pending; no strategy promoted.

## Research questions

1. For a short NIFTY weekly strangle entered at 10:00 IST on the first trading session after the previous listed weekly expiry, does a stop based on the short position's net delta improve after-cost outcomes compared with the fixed 14:00 IST expiry-day exit?
2. Does the result change when “combined delta” is defined as (a) the absolute signed net portfolio delta or (b) the sum of absolute call/put deltas?
3. Do gamma, vega, and theta conditions add out-of-sample risk control value independently or in combinations?
4. How do OR exits (any active Greek condition breaches at the same observation) compare with AND exits (all active conditions breach simultaneously)?
5. Which rules, if any, are robust across chronological development and validation splits, execution-cost stresses, and a reserved holdout?
6. What fraction of scheduled weekly campaigns is actually testable with exact minute bars, valid pre-entry delta estimates, and uninterrupted timestamped observations?

## Frozen base strategy

For consecutive, observed weekly expiry files E(previous) and E(current):

- Find the first observed NIFTY trading session strictly after E(previous). Enter at exactly 10:00 IST that session.
- From the current-week expiry option file, use only the exact 09:59 IST completed bar and the exact 09:59 index bar close for strike selection.
- Estimate European option implied volatility by inverting the 09:59 observed close under Black–Scholes, assuming a continuously compounded 6.0% rate, 0% dividend yield, and expiry at 15:30 IST. Greeks are model estimates, not exchange-published Greeks.
- Select one call and one put whose absolute model delta is closest to 0.15; use the pre-decision OI gate of at least 100 contracts and valid OHLC. Resolve ties deterministically by distance from spot then strike.
- Enter short one lot of each leg at the exact 10:00 bar open, subject to exact contract identity and valid OHLC. No nearest-timestamp match, forward-fill, interpolated premium, or current-bar close for entry selection.
- The no-stop control covers both legs at the exact 14:00 IST bar open on the current expiry day.
- Use observed expiry files rather than hard-coding a weekday. This is important because NSE weekly expiry conventions have changed historically and holiday adjustments apply.
- Treat all OHLC fills as an intraday simulation proxy, not executable bid/ask fills. The preferred Hugging Face dataset is declared CC BY-NC 4.0, so this is non-commercial research only and not evidence for commercial deployment.

An event is a weekly pair only if consecutive listed option-file expiries are 4–10 calendar days apart. Longer gaps, missing predecessor expiries, missing 09:59 selection inputs, missing exact 10:00 entries, missing exact 14:00 exit bars, invalid OHLC, duplicate contract-minute keys, invalid model Greeks, or missing any minute in the monitoring path are explicit exclusions. No observation is synthesized.

## Definition of each Greek stop

All Greek values are recalculated at every completed minute from the observed leg close, exact underlying close, remaining time to 15:30 expiry, and model IV. A trigger is evaluated on the completed bar at time t and the exit fill uses the next minute's exact open, preventing same-bar look-ahead. The fixed 14:00 exit remains the fallback if no trigger fires.

- **Net-delta rule (primary first test):** short-strangle position delta is -(call delta + put delta); stop when its absolute value reaches a threshold. Test 0.20, 0.30, 0.40, 0.50, 0.60 and 0.80. The user-requested 0.40 is an explicitly reported primary configuration.
- **Gross combined-delta alternative:** abs(call delta) + abs(put delta), which does not cancel the opposite signs of the two long-option deltas. Test 0.40, 0.50, 0.60, 0.80 and 1.00. This avoids silently conflating two different definitions of “combined delta.”
- **Gamma-risk rule:** normalized second-order adverse spot-move proxy = max(0, -short-position gamma) × 0.5 × (0.5% of spot)^2 / initial credit. Stop levels: 10%, 20%, 30%, 40%, 50% of initial credit.
- **Vega-risk rule:** normalized premium impact of an adverse +1 absolute implied-volatility percentage point = max(0, -short-position vega per 1-vol-point) / initial credit. Stop levels: 10%, 20%, 30%, 40%, 50% of initial credit.
- **Theta guard:** short-position theta per calendar day divided by its entry value. Stop if the ratio falls to/below 0.00, 0.25, 0.50, or 0.75. The metric is explicitly a decay-edge guard and is not described as a direct loss estimate. Events with non-positive or unavailable entry theta are not eligible for theta-conditioned tests.

Gamma/vega/theta are normalized by initial combined premium credit so units are interpretable and their thresholds are comparable. Their limits are hypotheses to test, not assumed optimal levels.

## Full combination grid

Enumerate all non-empty subsets of delta, gamma, vega, and theta criteria, every threshold level applicable to each active criterion, both delta definitions when delta is active, and both simultaneous-trigger aggregation modes (ANY/OR and ALL/AND). Single-criterion rules are emitted only once because ANY and ALL are identical for one active condition. Include a no-stop reference. The compiler in the execution script creates stable configuration IDs and records the exact tested denominator; configuration registration alone must never be described as an evaluated test.

Pre-registered threshold grid:
- net-delta: 6 levels;
- gross-delta: 5 levels;
- gamma: 5 levels;
- vega: 5 levels;
- theta ratio: 4 levels;
- aggregation: ANY and ALL for multi-criterion rules.

The finite sweep is bounded to this grid and will not expand recursively. No unregistered threshold search is allowed in the reserved holdout.

## Greek calculation and time rules

European Black–Scholes model; continuous rate 6.0%; dividend yield 0%; fixed expiry time 15:30 IST; one year = 365.25 days. Infer IV from the current completed bar close and exact index close solely to calculate Greeks at that completed observation. For fills, use only exact observed option-bar opens. Use the source's timestamp convention consistently: the bar labeled t is treated as opening at t and its close becomes known at t+1 minute; gamma/vega/theta calculations from that close use time-to-expiry at t+1 minute.

Portfolio Greeks use a signed short position: portfolio Greek = -1 × (long call Greek + long put Greek). Net delta is therefore signed and can cancel, whereas gross combined delta is the sum of absolute leg deltas. Delta and gamma are expressed per underlying point and point-squared respectively; vega is per one IV percentage point; theta is per calendar day. Unit tests must check call/put Greek signs and verify Black–Scholes price/IV round trips.

## Historical-data and source gates

Primary source: Hugging Face dataset thetrademarkk/india-index-options-1m, files index/NIFTY.parquet and options/NIFTY/YYYY-MM-DD.parquet. Resolve the branch name to a full dataset commit SHA before downloading and store the SHA and source-file hashes in results. Reuse GitHub Actions' Hugging Face cache; do not re-download every file on every run. Only aggregate diagnostics and result tables are committed; no bulk raw dataset is added to Git.

Try all usable expiry files visible at the resolved revision, including the latest available sample. The current repository research inventory has found that dataset coverage is partial and its current file list does not extend through the current 2026-10-23 date. Record the true maximum expiry/date from the resolved source and do not extrapolate beyond it. The dataset is licensed CC BY-NC 4.0 and cannot support commercial deployment on its own.

If coverage is inadequate, do not quietly substitute another series. Log a bounded follow-up data task: cross-check the free/open Zenodo 2017–2020 dataset and investigate Dhan expired options for the newer missing period. Dhan's documented relative-strike endpoint may cover only a limited strike band, so every selected strike must be reconciled against exact contract identity before it can be combined. No additional paid source may be assumed necessary until feasible free sources are audited.

## Transaction costs

Report all 24 scenarios:
- Brokerage: ₹10 / ₹15 / ₹20 per executed order.
- Adverse slippage: ₹0 / ₹0.05 / ₹0.25 / ₹0.50 per option unit per side.
- Modelled fee multiplier: 1.0× / 1.5×.

A short-strangle campaign has two entry orders plus two close orders, so brokerage is charged on four executed orders (round-trip ₹40/₹60/₹80 at the listed cases). At entry, adverse slippage reduces each short-sale fill; on closing, it increases each buy-to-close fill. Apply historical lot size by expiry date and record a regression-tested schedule: lot size 75 before 2021-08-01; 50 from 2021-08-01 through 2024-12-19; 75 for weekly expiries 2025-01-02 through 2025-12-23; 65 from 2026-01-06 onward. Unsupported dates are blocked, not silently assigned a lot.

Date-aware statutory modelling must separately itemize: STT on premium received for opening short sales (0.10% through 2026-03-31; 0.15% from 2026-04-01), exchange/IPFT charges (modelled 0.03553% of premium turnover), SEBI turnover fee (₹10/crore), stamp duty on buy-side premium (modelled 0.003%), and 18% GST on brokerage plus exchange/SEBI fees. The 1.5× scenario is a disclosed fee stress, not a statement that statutory rates are legally multiplied. The report must state model assumptions and link official fee references; account-specific contract notes remain unverified.

## Splits, metrics, and statistical protocol

Chronological split based on current target expiry:
- Development: expiry through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Reserved holdout: 2026-01-01 onward (bounded by the dataset's actual last covered expiry, expected to be earlier than today's date).

For every rule/cost combination, report completed trade count, valid-event coverage, gross P&L, net P&L, return on entry credit, win rate, expectancy, median trade, profit factor, cumulative-P&L maximum drawdown, and exclusion counts. Use one-lot NIFTY quantities with historical lot size; do not assume portfolio capital without stating it.

Use paired event-level results, one-sided one-sample tests against zero on the primary cost scenario, and Holm family-wise correction over the complete registered Greek-rule sweep. Bootstrap mean-trade-net confidence intervals by campaign for baseline and a validation-frozen shortlist. Rank and select candidate stops using validation only; do not select parameters from holdout performance. After the shortlist is frozen by validation, test baseline plus a maximum of 20 candidates across the holdout and all 24 cost scenarios. Retain the preregistered 0.40-delta rules in the holdout list even if their validation rank is not high. If the sample or inference gates fail, report a screen only and do not promote a strategy.

## Phases, finite stopping point, and gates

1. **110.0 — Registration/source audit:** create branch; read canonical research plan/data/cost rules; freeze the strategy definitions and threshold matrix. Status: complete when plan, logs, code shell and workflow are committed.
2. **110.1 — Data/source gate:** resolve dataset SHA; cache source files; reconcile expiry calendar, previous-expiry/next-session links, point-in-time bars, option types and exact contracts. Publish the manifest, coverage and exclusion reasons.
3. **110.2 — Greek engine and regression tests:** test IV inversion, delta/gamma/vega/theta signs, Greek units, threshold boundaries, timestamp-to-next-open exits, lot-size/date rules, cost accounting and duplicate/gap failure cases.
4. **110.3 — Full combination replay:** evaluate every registered rule across development and validation, all 24 costs; store deterministic grid and run hashes.
5. **110.4 — Validation inference and shortlist freeze:** calculate Holm-corrected validation tests, paired net uplift versus no-stop, bootstrap intervals, robustness to costs and drawdown. Freeze shortlist in a machine-readable file before the holdout evaluation.
6. **110.5 — Reserved holdout audit:** evaluate only the frozen candidates plus no-stop and preregistered 0.40 delta rules; all costs; no threshold changes.
7. **110.6 — Independent tester gate and publication:** separate developer/tester branches only after result acquisition; tester independently checks math, signs, source joins, completeness, fee accounting, split contamination and report-to-CSV reconciliation. Developer must fix/test and resubmit as needed.
8. **110.7 — Final report and stop:** publish manuscript, tables, charts, supplements, status/error/research logs and README link. Stop after the above bounded phases; do not start a new grid without a new user-approved research plan.

**Promotion gate:** positive net after costs; adequate and reported campaign coverage; validation multiple-testing control; candidate passes reserved holdout without re-tuning; stability across plausible slippage/brokerage/fee stresses; drawdown not materially worse than no-stop; independent audit passes; source/license terms permit the intended use. Failing any item means “no promotion,” not a guessed recommendation.

## Auditability and known limitations

- OHLC opens do not establish queue position or executable bid/ask fills; stops are executed at the next available exact minute-bar open, not an intrabar worst tick.
- Black–Scholes Greeks are estimates derived from historical premiums and assumed model inputs; they are not exchange-published Greeks.
- A one-minute model can miss sub-minute spikes. No slippage model perfectly reconstructs live fills.
- Theta is model theta per calendar day; its guard is a decay-edge feature and can be triggered by surface/spot moves as well as time passage.
- Weekly expiry calendar, lot sizes, STT and charges change over time; every date-effective mapping is documented and tested.
- The non-commercial data license prevents a commercial conclusion from this sample alone.

## Primary references to preserve in the final manuscript

- Dataset card: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- Dhan expired-options docs (supplemental source investigation): https://dhanhq.co/docs/v2/expired-options-data/
- Paytm Money F&O brokerage FAQ: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web
- NSE STT and levies: https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
- NSE exchange fee circular FA73061: https://nsearchives.nseindia.com/content/circulars/FA73061.pdf
- NSE contract/expiry information: https://www.nseindia.com/market-data/securities-available-for-trading

No strategy promotion or commercial/live-trading recommendation is authorized by this plan.