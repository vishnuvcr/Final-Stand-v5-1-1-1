# Phase 52 Configuration Replay Protocol v1.0

**State:** PRE-REGISTERED BEFORE ANY `phase52-grid-v1.3` configuration P&L run.  
**Grid:** `phase52-grid-v1.3` — 9,379,584 finite parameter configurations. This protocol does not change any grid domain, candidate ID or configuration ID.  
**Parent:** `PHASE52_RESEARCH_PLAN.md`, amendment PA-007.  
**Pinned quote source for research-only screening:** `thetrademarkk/india-index-options-1m` at revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5` (declared CC BY-NC 4.0).  
**No live deployment:** This data source is non-commercial and minute OHLCV/OI is not tick-level bid/ask/order-book data.

## 1. Event universe, dates and splits

The immutable option file list at the dataset revision defines target expiry dates. For each listed target expiry (E), the finite grid's `entry_dte_calendar_days` is applied literally:

- `0`: entry date is (E).
- `7`: entry date is calendar date (E-7) days.

The entry timestamp is exactly `09:45` or `13:00` IST as registered by the configuration. No rolling a holiday/weekend to another date, no nearest-time lookup, and no forward fill. If the exact date, exact index timestamp, exact option leg entry price, exit timestamp/leg price, or required selector input is unavailable, that event is excluded with a reason code. It is not assigned a zero return and it is not interpolated.

Use the existing Phase45 chronological boundaries based on **target expiry date**: development through 2023-12-31, validation 2024-01-01 through 2025-12-31, and holdout from 2026-01-01 onward. Missing late-2026 index timestamps mean the corresponding configurations may have partial event support. Report per-config and per-split expected, eligible and executed events, not only the P&L of successful rows.

For calendar/diagonal families, the target expiry is the near expiry. `WEEKLY_WEEKLY` selects the next later-listed expiry after (E). `WEEKLY_MONTHLY` selects the last listed expiry in the next calendar month with an available option file; if no valid matching contract and exact synchronized leg quote exists, skip the event.

## 2. One-minute OHLC fill semantics

Dataset timestamps are one-minute candle timestamps, not exchange tick/order-book quote timestamps. This protocol therefore treats results as an **OHLC intraday simulation**, never as tick-accurate fills.

- Entry decision uses only completed bars strictly before entry time and prior-session EOD factor data. Strike selection at time (T) may use the underlying index bar `open` at exactly (T), and every option leg must have the corresponding `open` bar at the same timestamp.
- Entry is filled at the option bar `open` at the exact configured entry timestamp, adjusted adversely for slippage. The index `open` is used for strike selection. The same bar's `close` must never determine the entry signal.
- For exit rule `15:15_IST`, all legs must have exact `open` values at 15:15 on the **entry date**.
- For `EXPIRY_OR_LAST_VALID_QUOTE`, close all legs together at the latest exact common option-bar timestamp on or before 15:29 IST on the target near-expiry date.
- For `TAKE_PROFIT_50_PERCENT_MAX_PROFIT`, first compute a terminal payoff grid from the frozen leg geometry to estimate the finite theoretical max profit. Trigger only from a completed-bar close after entry; execute at the next minute's exact `open`. If no finite max profit is defined, or no next-minute common open exists, record an explicit inapplicable/missing-exit status.
- A one-minute OHLC candle does not prove a 15-second quote-age gate. That criterion is not claimed as passed from this source. No field in this dataset is to be described as a true bid/ask spread.

## 3. Liquidity, OI and freshness controls

All traded option legs must pass the frozen minimum open-interest gate of 100 contracts at entry; required fields must be non-null and the strike/expiry/type must match exactly. The parameter `liquidity_max_spread_pct` is applied only to the **intrabar high-low range proxy** `100 × (high-low)/open` at entry because bid/ask quotes are not present. In result labels and the manuscript it must be named an OHLC-range liquidity proxy, never an observed bid/ask spread. Report this source limitation beside every result.

## 4. Anchor strikes, wings, ratios and lots

- `ATM_OFFSET`: `atm_offset_steps` chooses a pivot (K) relative to the modal strike spacing at the exact entry snapshot. For directional one-sided structures, calls anchor above spot and puts anchor below spot by the selected offset. For a structure whose legs share one pivot (e.g. straddle, strip, strap, short iron butterfly, synthetic call/put pair), all same-pivot legs use the same anchor strike at ATM plus the configured offset. For iron condors, call and put wings anchor independently on their respective OTM sides.
- `ABS_DELTA`: estimate each available contract's delta at entry using a Black–Scholes implied-volatility solve from the observed option premium, exact same-time index spot, target expiry time and the frozen 6% rate assumption. Select the strike whose absolute delta is nearest to the registered `absolute_delta`; apply wing offsets only after the base strike is selected. For multi-leg same-pivot CE/PE structures, choose the pivot from the call-side target delta and use the exact same strike for both types; independent OTM CE/PE anchors are used only for structures whose template has separate call and put anchors. Failed/invalid IV solve means unavailable, not an imputed delta.
- `wing_width_steps` selects the registered width for verticals, condors and butterflies. For a broken-wing butterfly the short-to-first-long distance is fixed at one modal step and the far wing uses the registered width; width=1 is intentionally the symmetric boundary case.
- `leg_ratio` applies its first value to the template's first leg and second value to its second leg; any remaining template leg ratios remain fixed. `reference_lots_per_leg` scales every template quantity equally. Lot size by expiry reuses the date-aware Phase43 lot-size function and is fingerprinted in the manifest; verify against official historical contract information before any deployment claim.

## 5. Selector-mode semantics: gates, not hidden strategy switching

Each `candidate_id` fixes its strategy family. Selector modes gate whether that family is entered or the system abstains; they do not silently substitute another strategy. Different families are compared only after same-event replay and multiplicity correction.

- **BASELINE:** no factor gate beyond market-data, contract, liquidity and risk eligibility.
- **VIX_ROUTER:** both gates must pass. `vix_percentile_threshold=25` means prior-only rolling VIX percentile ≤25; 75 means ≥75. `vix_change_pct_threshold=-10` means prior-session VIX percentage change ≤−10%; +10 means ≥+10%.
- **GREEKS_SURFACE_ROUTER:** implied-volatility minus prior-only realized volatility must be ≤−2 or ≥+2 volatility points according to the sign of the threshold; absolute net delta and absolute net gamma must be at least their configured triggers; and `abs(net daily theta)/opening credit` must not exceed `theta_to_credit_daily_limit`. If opening credit is non-positive or any Greek cannot be computed, abstain.
- **OI_FLOW_ROUTER:** absolute aggregate near-ATM OI change is at least its threshold; PCR must be ≤0.85 or ≥1.15 as implied by the configured threshold; cumulative entry-session volume/OI ratio must be at least its threshold. All conditions are required; missing inputs mean abstain.
- **SPOT_FUTURE_SYNTHETIC_ROUTER:** 15-minute spot return must cross the configured signed ±0.4% threshold; lagged previous-session EOD futures basis must cross the signed ±15 bps threshold; and exact-time synthetic-future parity basis from same-strike, same-expiry CE/PE bars must cross its signed ±15 bps threshold. The futures basis remains an EOD proxy; no intraday traded-future fill is inferred from it.
- **MULTI_FACTOR_ROUTER:** three preregistered directional-proxy votes are used because the v1.3 grid exposes only three corresponding threshold parameters. (1) The prior-only India VIX percentile vote is +1 when its rolling percentile is at or below `vix_percentile_threshold` (25 or 75), otherwise −1; this is a risk-regime proxy, not a return forecast. (2) The OI imbalance vote is +1 when near-ATM put OI percent change minus call OI percent change is at least `oi_change_pct_threshold` (15% or 35%), −1 when the difference is at most its negative, otherwise 0/neutral. (3) The spot vote is +1 when prior 15-minute NIFTY return is at least `spot_return_15m_pct`, −1 when at most its negative, otherwise 0/neutral. Compute directional agreement as the largest positive/negative vote count divided by the number of non-neutral votes. Enter only when this agreement meets `multifactor_min_agreement` (0.67 or 0.90) and disagreement uncertainty is no greater than an `abstain_if_uncertainty_quantile` (75th/90th percentile) cutoff fitted on development data only. Zero usable votes, missing required input for a configured vote, or tied top vote means abstain. The quantile and vote rules freeze before outcomes; no PCR threshold or VIX-change threshold is assumed for this selector, because those dimensions are not in the registered MULTI_FACTOR_ROUTER domain.

The already-audited point-in-time global-index/sentiment features (S&P 500, Nasdaq, global VIX, Nikkei, gold, crude, USD/INR and sentiment proxy) may be reported as **non-optimizable auxiliary controls** when source timing and split coverage pass. DII/FII positioning, timestamped news, corporate actions and market breadth are not assumed present: audit and include them only if a reproducible point-in-time source exists; otherwise mark unavailable. They are not fabricated into this grid.

## 6. Families not safely replayable

The 15 families marked `PHASE45_TEMPLATE_REQUIRES_RECONCILIATION` or `SPECIFICATION_BLOCKED` in `research/phase52/strategy_specifications.csv` must be output as `BLOCKED_SPECIFICATION` with the exact family and reason for every associated config. No family geometry may be reconstructed from a name or screenshot alone.

The five diagnostic-only families (naked call, naked put, short straddle, short strangle and covered-call-future/short-gamma variant) may be measured only as diagnostics and can never pass promotion. Any config requiring an actual intraday traded future, futures hedge, delta-band rebalancing or futures-basis arbitrage is `BLOCKED_MISSING_INTRADAY_FUTURES_DATA` unless a synchronized point-in-time futures quote source is added and separately audited. Daily EOD futures basis and synthetic option parity are not traded futures quotes.

`TAKE_PROFIT_50_PERCENT_MAX_PROFIT` is inapplicable to unlimited-max-profit and path-dependent calendar/diagonal structures unless a finite, independently validated maximum-profit definition exists; those individual configs receive `BLOCKED_EXIT_SEMANTICS`, not a guessed outcome.

## 7. Costs and result fields

For each configuration, evaluate all grid stress outputs in the same replay. Paytm Money primary conservative brokerage is ₹20 per executed order (official pricing update effective 15 January 2025); ₹10/order is a legacy-plan sensitivity because Paytm Money's F&O FAQ still lists it for some account plans. Confirm the user's actual tariff before deployment. Statutory/transaction charges use the existing date-aware Phase43 schedule (STT, exchange transaction charge, SEBI charge, IPFT, stamp duty and GST) and the full number of leg entry/exit/rebalance orders. Slippage is separate from charges: base adverse slippage is ₹0.05 per leg per fill; stress 0/50/100 means ₹0.05/₹0.075/₹0.10 respectively. Do not multiply statutory charges by the slippage stress. Both ₹20 primary and ₹10 legacy-sensitivity results are preserved; all results are labelled by brokerage scenario.

Each configuration output includes config/candidate/grid/protocol IDs, source and script hashes, family specification status, split, expected events, exact-quote eligible events, executed events, abstentions, exclusion reasons, gross P&L, fee/brokerage, slippage, net P&L for each cost scenario, mean net/trade, win rate, profit factor, cumulative-P&L drawdown, return on the reference ₹6,00,000 capital denominator, max risk proxy, and source-coverage fields. The capital-return denominator is a normalization, not a broker margin calculation.

## 8. Promotion gates

A grid result is not promotable solely because P&L is positive. At minimum require: zero unresolved implementation errors; explicit valid family specification; ≥95% exact entry/exit coverage for the tested testable event universe; at least 30 distinct validation expiry events and 20 untouched holdout expiry events; positive validation and holdout net after ₹10-order and ₹20-order scenarios and the 0/50/100% slippage stress; no unbounded risk for a promoted live candidate; drawdown and risk proxy within preregistered bounds; paired block-bootstrap uplift confidence interval above zero vs the fixed baseline; Holm-adjusted familywise p<0.05 across the frozen candidate family; and an independent rights-cleared source reproduction. Missing quote support, a smaller holdout or the CC BY-NC data license blocks promotion even where exploratory P&L is positive.

**Important:** Current Phase52 fixed-geometry and EOD-selector studies are separate exploratory screens. They do not constitute a run of any of the 9,379,584 configuration rows.


### Brokerage source audit

Paytm Money's official pricing update dated 18 December 2024 states that flat ₹20 brokerage across segments starts 15 January 2025: https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/. A separate current F&O FAQ still states ₹10 per executed order: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web. Because published help sources are inconsistent and individual plans may differ, the configuration grid uses ₹20/order as the primary conservative scenario and ₹10/order only as sensitivity; the actual account tariff must be verified before any live-readiness decision.
