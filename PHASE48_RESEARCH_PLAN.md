# Phase 48 Research Plan — Independent Multi-Expiry Data Bridge

## Research question

Can an independent historical NIFTY intraday dataset with multiple expiries visible on the same trade date unlock reproducible testing of the YouTube-derived multi-expiry strategies that were data-infeasible in Phase 47, while retaining all VIX states and protecting a holdout?

## Why Phase 48 exists

Phase 47 established that the project's primary cached option source is structurally insufficient for systematic next-expiry entry-time research. Phase 48 therefore uses the public Hugging Face rissin/nse-options-intraday dataset as a supplemental data bridge. The dataset advertises NIFTY 1-minute intraday coverage from Oct 2024 onward and stores expiry, strike, option type and OHLC in a canonical Parquet schema.

Source documentation: https://huggingface.co/datasets/rissin/nse-options-intraday

## Evidence status

This is a **supplementary exploratory phase**, not a replacement for the 2021–2025 canonical dataset. The available independent dataset begins in late 2024, so development is shorter than the main research split.

Development: 2024-10-01 through 2024-12-31.
Validation: 2025-01-01 through 2025-12-31.
Protected holdout: 2026-01-01 onward.

Because the development period is short, no Phase-48 result can directly replace or overrule earlier canonical conclusions. Any apparently promising result requires a later independent confirmation phase before promotion.

## Full VIX panel

Every candidate is evaluated across:
ALL, LOW, NORMAL, FALLING, RISING, HIGH, SPIKE, HIGH_RISING.

LOW/NORMAL/FALLING are deliberately retained as active research regimes; the purpose is not to hunt only for high-VIX profits.

## Registered candidates

### B1 — Double Calendar Straddle
- Entry: four trading sessions before the selected monthly expiry at 10:00 IST.
- Current monthly expiry: sell ATM-equivalent CE + PE at the current contract's own nearest ATM strikes.
- Next monthly expiry: buy CE + PE at the next contract's own nearest ATM strikes.
- Exit: latest complete observed timestamp <=15:29 IST on current monthly expiry day.
- Static baseline only; no adaptive adjustment.

### B2 — Monthly Wide-Range Hedge, static baseline
- Entry: first trading day after the preceding monthly expiry at 10:00 IST.
- Sell current-month CE + PE nearest 0.30 absolute Black-Scholes delta using prior India VIX as the entry volatility proxy.
- Buy next-month CE + PE at the strike with the smallest call-put premium gap near spot.
- Exit current-month expiry <=15:29 IST.
- The Profit Breakout adjustment rule is **not** included in the first static baseline, so the effect of the initial structure is isolated before any dynamic-management phase.

### B3 — Covered Call 2.0, static proxy
- Entry: first trading day after the preceding weekly expiry at 10:00 IST.
- +ATM CE / -ATM PE current weekly expiry as an option-only long-future proxy.
- Buy current-week ~0.30-delta protective PE.
- Sell current-week ~0.30-delta CE and next-week ~0.30-delta CE near 0.30 delta.
- Exit current-week expiry <=15:29 IST.
- No delta rebalancing in B3. This is a static proxy, not an exact replication of the source's active adjustment system.

## Execution and costs

- Historical NIFTY lot sizes.
- ₹10 Paytm Money F&O brokerage per executed order.
- Date-aware STT, exchange transaction charge, SEBI fee, IPFT, stamp duty and GST.
- Adverse ₹0.05 option tick per leg at entry and exit.
- +50% stress multiplies monetary fee/charge components by 1.5; adverse ₹0.05 tick remains fixed.
- No forward filling, interpolation or synthetic option prices.

## Statistical design

For each strategy × VIX state report trade count, net P&L, fee-stress P&L, mean/trade, win rate, drawdown, profit factor, active-vs-complement difference, bootstrap 95% CI, permutation p-value and Holm-adjusted p-value.

Minimum working-state screen: >=20 trades, positive validation net, positive +50% charge stress and positive active-vs-complement mean advantage.

Formal promotion is prohibited in this supplementary phase unless all gates pass and the result is subsequently independently reconfirmed on a stronger dataset.

## Self-audit stages

1. Dataset file/schema audit.
2. Multi-expiry same-date availability audit.
3. Representative strategy-construction audit across development/validation/holdout.
4. Numerical run.
5. Duplicate/missing-leg/split/state audit.
6. Statistical audit and validation freeze.
7. Protected 2026 confirmation audit.

Any failed audit produces non-evidence, is logged, and triggers correction before rerun.

## Stop condition

Phase 48 closes after the three registered baselines are either numerically testable or proven infeasible on the independent dataset, validation ranking is complete, and 2026 confirmation is protected.