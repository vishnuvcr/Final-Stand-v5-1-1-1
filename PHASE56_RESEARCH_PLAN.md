# Phase 56 research plan — OHLC price-reference P&L sensitivity

**Branch:** `phase-56-ohlc-pnl-sensitivity`  
**Status:** COMPLETE — preregistered diagnostic analysis accepted; no strategy promotion  
**Parent evidence:** Phase 55 all-leg audit ledger; Phase 54 fixed 11-threshold coverage sensitivity  
**Dataset revision:** `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`  
**Sample:** frozen 40 configurations × 24 event identities = 480 configuration-event rows  
**Protocol version:** phase56-ohlc-reference-pnl-v1.0

## 1. Research question

Within the frozen Phase 52 development/validation pilot, how do descriptive net P&L results change across the 11 already-preregistered OHLC-range thresholds when entries and exits reference the recorded same-day option-bar opens, while applying date-aware statutory costs, Paytm Money brokerage scenarios and adverse slippage stresses?

This is an **OHLC price-reference sensitivity**, not an executable backtest: the dataset does not contain historical bid/ask quotes or market depth, and OHLC opens do not guarantee available fills.

## 2. Aim and objectives

**Aim:** quantify whether the very low 2% proxy-gate coverage is the only reason the frozen pilot has too little price-reference evidence to describe net P&L, without relabelling candle range as spread or relaxing any rule silently.

Objectives:
1. Verify and pin the exact 480-row Phase 55 leg-audit ledger and source revision.
2. Recompute row eligibility at the 11 thresholds already preregistered in Phase 54: 2, 3, 4, 5, 6, 8, 10, 12, 15, 20 and 1000 percent. The 1000% value remains a diagnostic near-removal of the range proxy, not a recommended production setting.
3. Keep the exact prior-minute OI minimum (100), exact entry bar, exact 15:15 exit bar and selected legs unchanged. Any row with an observed required-leg OI failure remains rejected at every threshold.
4. Apply the same adverse premium fill arithmetic as the accepted Phase 52 kernel to the stored exact entry-open and exit-open references. Never invent missing OHLC fields or synthesize bids/asks.
5. Apply the existing date-aware statutory-fee helper plus two brokerage scenarios and a broader, preregistered slippage ladder.
6. Report every threshold/cost scenario, including negative outcomes and low sample sizes; provide row-, configuration- and family-level descriptive summaries without selecting or promoting a winner.
7. Stop after the fixed matrix, invariant checks and report persistence. Holdout access and any live-trading recommendation are prohibited.

## 3. Falsifiable hypotheses

- **H1 — Coverage reproduction:** eligible-row counts reproduce the accepted Phase 54 counts exactly: 1, 1, 8, 24, 55, 91, 150, 227, 298, 345 and 380, in threshold order.
- **H2 — Cost sensitivity:** net P&L does not improve when brokerage rises from ₹10 to ₹20 per executed order for an otherwise identical trade and slippage assumption.
- **H3 — Slippage sensitivity:** gross P&L does not improve as the fixed adverse slippage per fill increases.
- **H4 — Eligibility is not profitability:** more rows admitted by a wider OHLC threshold do not, by themselves, demonstrate better liquidity, better fills or higher expected profitability.
- **H5 — Robustness is demanding:** any apparent positive configuration-level result may be concentrated in a few event dates or fragile to the adverse-cost ladder; these metrics are diagnostic only and are not an OOS result.

No hypothesis is assumed to be true before the run.

## 4. Frozen universe and eligibility rules

Input: `results/phase52/historical_pilot/event_replay.csv` from Phase 55.

The ledger must contain exactly 480 rows with status counts:
- `EXCLUDED_OHLC_RANGE_PROXY`: 379;
- `BLOCKED_LEG_ELIGIBILITY`: 100;
- `REPLAY_PASS`: 1.

The complete selected-leg counts are fixed by family:
- `BUY_CALL`, `BUY_PUT`: 1 leg;
- `BULL_CALL_SPREAD`, `BEAR_CALL_SPREAD`, `LONG_STRADDLE`, `LONG_STRANGLE`: 2 legs;
- `SHORT_IRON_CONDOR`: 4 legs.

A row can be price-reference eligible at a threshold only when **every** expected leg has all of:
- a unique expected leg ID, valid side, quantity and lot size;
- `entry_status=PASS`, positive finite `entry_open`;
- `prior_oi_status=PASS` and prior OI ≥ 100;
- finite `entry_range_proxy_pct` not greater than the tested threshold;
- `exit_status=PASS`, positive finite `exit_open`.

A row explicitly blocked for a required-leg prior-OI failure stays rejected at all thresholds. A missing/malformed field or incomplete leg set fails closed; no interpolation, nearest-bar substitution or threshold-based imputation is allowed. Eligibility may differ by threshold, but the underlying row sample never changes.

## 5. Preregistered pricing and transaction-cost scenarios

### Price references and fill rule

Use the stored exact entry `open` and exact 15:15 exit `open` per leg. An OHLC open is only a price reference; it is not a historical bid, ask, executable queue fill, or market-impact estimate. Require the recorded exact-bar status to be PASS. Do not fabricate full OHLC bars merely to call the Phase 52 `evaluate_leg_fill` function; calculate the same adverse open-reference cashflows from the documented helper arithmetic and feed the actual orders to the shared `cost_breakdown` function.

Adverse slippage per fill (INR), in fixed order:
- ₹0.00 — zero-slippage lower-bound diagnostic only;
- ₹0.05 — Phase 52 base adverse-slippage assumption;
- ₹0.075 — 50% stress over base;
- ₹0.10 — 100% stress over base;
- ₹0.25 — severe uncalibrated stress;
- ₹0.50 — very severe uncalibrated stress.

The ₹0.25 and ₹0.50 cases are explicit stress assumptions, not measured spreads. All price adjustments must use the kernel's nonnegative adverse-fill convention and record their exact value.

### Brokerage and statutory costs

Run both ₹10 and ₹20 per executed order for every eligible row and threshold. The current Paytm Money F&O FAQ states ₹10 brokerage per unique order executed (retrieved 2026-10-10): https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web . The ₹20 case is retained as a conservative/alternate tariff comparator; actual client pricing must be verified against the account's tariff before any real trade. Paytm Money's pricing disclaimer states tariff is subject to change: https://www.paytmmoney.com/stocks/pricing .

Use the accepted Phase 52 kernel's date-aware exchange, SEBI, IPFT, GST, STT and stamp-duty calculations. Charge brokerage and statutory fees on every entry and exit order, including every leg; do not scale statutory charges down with the slippage stress. Do not add or omit a cost item between scenarios. This does not certify that current fees are a perfect reconstruction of every historical broker-specific tariff.

Total combinations: 11 range thresholds × 2 brokerage values × 6 slippage values = **132 scenario combinations** for the top-level grid summary, with trade/configuration details retained beneath it.

## 6. P&L calculation protocol

For each eligible row, threshold and cost scenario:
1. Parse all legs from `resolved_legs_json`; use only recorded leg sides, quantity, lot size, expiry, entry-open and exit-open values.
2. For each leg, derive signed units as quantity lots × historical lot size. Buy entries are adversely raised and buy exits adversely reduced; sell entries are adversely reduced and sell exits adversely raised, with the zero floor respected.
3. Compute gross P&L from those adjusted price references. Build the two actual order records per leg and pass the orders to the existing date-aware `kernel.cost_breakdown`.
4. Net P&L = gross P&L − total transaction costs. Record gross, every statutory/brokerage component, total cost, net, reference-capital return, lot/order counts, and cost assumptions.
5. Reuse the same market rows across all threshold/cost variants; only the fixed eligibility threshold or preregistered cost parameter changes.
6. Retain ineligible rows with explicit reason codes, but do not assign simulated P&L to them.
7. Keep repeated configurations/event dates distinct. Never sum the full parameter grid and call the result a single investable portfolio.

The shared Phase 52 fee helper is used so this is directly comparable to the accepted one-row cost output. The price model remains an approximation because actual historical quotes, queue position, order type, latency, partial fills and market impact are unavailable.

## 7. Statistical analysis

Descriptive summaries only:
- eligibility counts and shares by threshold;
- gross and net P&L, total fees, mean/median per admitted configuration-event row, positive/negative row counts and win-rate by threshold/brokerage/slippage;
- per-configuration and per-family breakdowns, plus the count of configurations remaining positive under each cost assumption;
- event-level contribution concentration and leave-one-event-out net total for configurations with adequate event counts;
- scenario invariants described above.

No p-values, confidence intervals, Sharpe claims, optimizer ranking, model selection or generalization claims are permitted. Each configuration uses overlapping market dates and structures, and the thresholds share the same events; the 480 planned rows are not 480 independent samples. Family-pooled totals and all-grid totals are descriptive grid diagnostics, not a capital-weighted account equity curve.

A configuration may be marked `ROBUSTNESS_SCREEN_PASS_FOR_FURTHER_RESEARCH_ONLY` only if it has at least 10 eligible event identities and net P&L remains positive at both ₹20/order and ₹0.50 adverse slippage per fill; this label is **not** promotion eligibility and does not replace independent quote validation or untouched holdout testing. All configurations must be reported, whether they pass or fail.

## 8. Acceptance criteria and invariant tests

- Input SHA-256, pinned source revision and parent row/status counts recorded.
- Every one of the 11 thresholds reproduces Phase 54 eligibility counts and all categories reconcile to 480.
- Each eligible row has complete selected-leg records; no P&L is assigned to the 100 prior-OI-blocked rows.
- Each trade scenario has exactly two orders per leg; fee calculations cover all fills.
- ₹20 brokerage net P&L is no greater than ₹10 brokerage net P&L for the same trade/slippage.
- Gross P&L is non-increasing as slippage rises for each same trade.
- All scenario outputs are finite; threshold/cost scenario totals reconcile to the event-level rows.
- Regression tests and GitHub Actions self-test pass; outputs, status, research log, error log and chat log persist.
- The report states prominently that price-reference fills are not executable quotes; candle range is not spread; no strategy is promoted.

## 9. Known strengths and limitations

**Strengths:** fixed event/configuration universe; verified full-leg payload; exact entry/prior-OI/exit timestamps from the pinned source; transparent fees and adverse-fill stresses; zero holdout contamination; all scenario outcomes preserved; reproducible input fingerprint.

**Limitations:** small fixed cohort (24 event identities); only 40 of the 9,379,584 enumerated configurations; the pilot is BASELINE selector only and does not test factor-selector efficacy; non-commercial data license; missing historical bid/ask/depth; open-based fills do not model available size, queue position, latency or partial fills; flat rupee slippage is a stress assumption rather than empirical calibration; scenario overlap creates multiplicity and dependence.

## 10. Stop rule, inference and future direction

Stop after this fixed 132-combination cost/threshold matrix, coverage/P&L validation and repository persistence. Do not add more thresholds, re-optimize parameter values, or access holdout within Phase 56.

- If no configuration passes the preregistered severe-cost robustness screen, record `NO_ROBUST_CONFIGURATION_UNDER_OHLC_PRICE_REFERENCE_STRESS`.
- If one or more configurations pass, record only that they merit **future quote-validated research**; do not call them profitable or executable.
- Regardless of outcome, no strategy promotion is authorized because true historical bid/ask/depth is unavailable and the source declares CC BY-NC 4.0.
- Future work, if still within the approved project phases: obtain licensed/authorized independent quote data or a newly verified lawful source; validate fills against quote/depth and re-run on a preregistered development/validation sample; keep holdout untouched until a candidate survives all prior gates.

## 11. Research record and phase changes

Only operational decisions, actions, results and errors belong in the repository; do not record private chain-of-thought. Update this plan only if the proposed scientific design changes. Every software or validation failure must append to the error log, and every bounded run must update status/research/chat records and the README.

**Phase status at plan creation:** OPEN; code/tests/workflow and output verification pending.


## Final status update — 2026-10-10

The frozen matrix completed in [run 38019146547](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019146547). All acceptance criteria passed: 480-row reconciliation, complete leg payloads, Phase 54 threshold counts, 132 threshold/cost summaries, 5,280 configuration summaries, 924 family summaries, 18,960 trade-scenario rows, 440 severe-cost screens, monotonic slippage/brokerage invariants and untouched holdout. The five severe-cost screen passes occur only at the 1000% diagnostic threshold; none is a production candidate. Phase 56 is closed per its stop rule.
