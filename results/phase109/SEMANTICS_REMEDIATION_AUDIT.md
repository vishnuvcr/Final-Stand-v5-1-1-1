# Phase 109 semantic implementation audit

**Initial status:** Source defects confirmed; corrected Actions run pending.  
**v1 engine:** `phase109-eod-engine-v1`  
**v2 engine:** `phase109-eod-engine-v2-semantics`  
**Promotion:** None.

| Risk | v1 behavior | v2 correction |
|---|---|---|
| Strategy core identity | Name fragments could map another architecture to ROC/EMA/reversion methods | Exact allowlist only |
| EMA slope | Alias of ordinary price-return momentum | Normalized change in EMA from the previous signal observation |
| EMA crossover | Current EMA spread sign only | Requires a previous/current sign crossing and threshold |
| Cross-asset confirmation | Reused the opposite domestic index as generic cross-asset evidence | Unsupported confirmation families are blocked |
| Realised-volatility low/high | Computed a state but did not select a target state | Blocked until target state is explicitly preregistered |
| Risk-profile execution | Escaped stop/target regex could fail to parse registered premium barriers | Shared `parse_risk_profile()` helper and regression coverage |
| Resume reproducibility | Existing cursor could be reused by modified logic | Engine version bump resets cursor; v2 results separate from v1 |

## Rule coverage
The v2 allowlist consists of ROC momentum, EMA crossover, normalized EMA slope, return z-score fade, RSI rebound, Bollinger reversion, EMA-deviation fade, and relative strength. This describes coded rules, not profitable strategies. Other registered architectures remain visible as blocked pending actual inputs, rule cores and tests.

## Required costs and validation
Each evaluated eligible configuration must be costed at all 24 registered combinations: ₹10/₹15/₹20 brokerage per order, ₹0/₹0.05/₹0.25/₹0.50 per-option-unit-per-side adverse slippage, and 1.0×/1.5× modeled fees. The canonical date-effective charge model is retained. Development/validation only for selection; the 2026-04 onward holdout is reserved. Multiple-testing/session-cluster inference and execution validation are mandatory. Positive-volume EOD OHLC is not verified executable price evidence. No strategy is promoted.

## Additional source-validity finding — 2026-10-12

The official index/VIX context audit returned only 218 unique dates per series across the requested multi-year range, while 743 options archive dates were available. The source audit previously checked schema/duplicate/OHLC quality and nonempty data but did not check date density, so its PASS was not sufficient for VIX/regime research. The prior context and any v2 results using it are diagnostic only.

Current correction: source queries are now limited to 60-calendar-day windows and each of India VIX, NIFTY 50 and NIFTY BANK must cover at least 90% of weekdays in the requested window. The dispatch gate also validates archive/index date overlap; the evaluator has an independent v3 runtime coverage guard and refuses the old v2 cursor. Latest test evidence: [run 38225233888](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225233888), 32/32 passed. Updated source run [38225253211](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225253211) remains queued behind the earlier acquisition run [38224816723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224816723). No corrected v3 empirical checkpoint is yet verified.

## Cost-schedule source check — 2026-10-12

### Verified public schedule inputs

- Paytm Money's official F&O FAQ states brokerage of **₹10 for every unique order that gets executed** ([official Paytm Money F&O FAQ](https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web)). The model's ₹10/order case is the public baseline; ₹15 and ₹20 per order remain explicit higher-cost stress cases. The trade-specific contract note and account-level add-ons have not been inspected, so these remain indicative.
- NSE's official STT page lists option-sale STT at **0.15% from 1 April 2026**, versus 0.10% through 31 March 2026, and exercised-option STT at 0.15% from that date ([NSE STT schedule](https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax)).
- NSE's 27 February 2026 circular revises equity-options exchange charges effective **1 March 2026**. The schedule records ₹3,552 per crore premium value in exchange transaction charges plus ₹0.01 per crore IPFT contribution ([NSE Circular FA73061](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf)). These are separate fields in the canonical model.
- NSE's levy guide lists equity-options stamp duty at 0.003% on the buyer and SEBI turnover fee at ₹10 per crore ([NSE levies guide](https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies)).
- Regression coverage now checks date-effective exchange-fee rates, April 2026 STT, and the ₹10 round-trip brokerage total for two executed orders. Model calculations were not changed; reported numeric rate fields now preserve 12 decimal places so the displayed exchange/IPFT rates are not rounded into a misleading value.

### Limitations

The canonical model uses a configurable brokerage-per-order parameter and applies the 1.5× stress multiplier to modeled round-trip fees; per-option-unit adverse slippage remains a separate scenario. The model estimates statutory/service fees but cannot prove spread, depth, latency, impact, partial-fill or achieved-execution costs. Exact contract-note treatment of IPFT/GST and any client-specific paid services remains to be reconciled before live-use claims. No strategy is promoted.

## Special-session coverage and evaluator v4 — 2026-10-12

- The repaired NSE Indices context audit contains 748 observations for India VIX, NIFTY 50 and NIFTY BANK from 2023-10-03 through 2026-10-08, with zero context-fetch failures, clearing the 90% weekday data-density threshold.
- Calendar reconciliation still reports five NIFTY 50-observed sessions without a valid option archive: 2023-11-12, 2024-01-20, 2024-05-18, 2025-02-01 and 2026-02-01. The weekday-only options downloader had not tried those dates.
- Added requested_dates() to union weekdays with observed official NIFTY 50 sessions outside weekdays, plus regression coverage. Latest full regression workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed 38 tests.
- Evaluator v4 (phase109-eod-engine-v4-session-coverage) resets progress independently from v3, writes unique result filenames, requires the 90% context gate and checks that remaining session/archive gaps were explicitly probed. The latest source workflow [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) is queued after the prior source workflow [38225253211](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225253211) finishes.
- The old v3 evaluation [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004) may complete but is diagnostic only because its engine did not require special-session reconciliation. No v4 empirical shard or strategy promotion is yet verified.
