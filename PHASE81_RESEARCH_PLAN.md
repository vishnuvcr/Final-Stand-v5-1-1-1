# Phase 81 — Paired intraday versus overnight structure sweep
Date: 2026-10-10
Status: FROZEN BEFORE NUMERICAL RUN

## Question
Under the same date, expiry, ATM anchor and option-structure template, do intraday and overnight holding windows differ in net returns after brokerage/statutory charges and adverse slippage?

## Registered scope
Ten variants: short ATM straddle (diagnostic only), short iron fly with 100/200/300-point wings, long iron fly with 100/200/300-point wings, short iron condor with short legs ±100 and long wings ±300, bull put credit spread (−100/+300 relative put strikes) and bear call credit spread (+100/+300 relative call strikes). Exact leg definitions are in research/phase81_intraday_overnight_sweep.py and source registry.

Two paired windows:
- Intraday: entry 09:20 bar open, exit 15:20 bar open on same session.
- Overnight: entry 15:20 bar open, exit next valid trading session 09:20 bar open.
Both use the same 09:19 NIFTY spot close as the ATM anchor and the same expiry/strike/side basket. Listed expiry must be later than the following session; expiry-day and prior-session carries into expiry are excluded.

## Source and data policy
- Primary dataset is pinned to revision 0f4800e43e6f96cec0794369d78eb4d3c4211ef5 of thetrademarkk/india-index-options-1m, CC-BY-NC-4.0.
- Use only expiry files with expiry dates through 2025-12-31; do not download or read 2026 option-expiry files in this phase.
- No raw OHLC bars are committed. Derived trade metrics are published as the licensed noncommercial research output.
- Require explicit expiry, exact side/strike/timestamp, valid positive open price and nonzero volume on every leg at both entry and exit. No forward-fill, synthetic bars, or ordinal mapping of sparse strikes.
- All exclusions and file/schema failures are retained.

## Cost assumptions
- Paytm Money brokerage ₹10 per unique executed order, consistent with the broker's current F&O FAQ: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web
- Date-aware statutory levies, exchange/IPFT/SEBI fees, stamp duty and GST from the project's frozen Phase-45 fee schedule. Official NSE rates show option-sale STT at 0.10% through 2026-03-31 and 0.15% from 2026-04-01; the current phase does not inspect post-2025 outcomes. https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- Apply adverse ₹0.05 per leg per fill for primary and ₹0.10 (two ticks) for stress.
- Reference prices are option candle opens, not historical bid/ask or depth; therefore net results are not proven executable results.

## Temporal gates
- Development: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- 2026-01-01 through 2026-09-30 is a sealed holdout for later Phase 82 only. This phase must not download/load, score, or rank those data.
- Lagged India VIX regime is descriptive only, using only prior dates; no same-day look-ahead and no regime parameter tuning.
- Ten registered paired comparisons (overnight minus intraday per structure variant) are the declared comparison family. Phase 81 reports descriptive effects only; Phase 82 must conduct paired/session or expiry-clustered inference, multiple-testing correction, and only then any frozen confirmation.

## Decision criteria
This phase cannot promote a strategy. Report coverage first; show trade counts and exclusions; compare mean/median, totals, win rate, profit factor, drawdown, fees and two-tick stress. A positive aggregate or isolated regime cell is not sufficient. Short ATM straddle is diagnostic only due undefined risk.

## Finite stopping
Phase 81 = one registered sweep. Phase 82 = inference and sealed holdout confirmation only if paired data coverage permits. Phase 83 = final manuscript/figures/tables/appendix and terminal conclusion. Do not add a new structure/parameter because a result looks attractive.
