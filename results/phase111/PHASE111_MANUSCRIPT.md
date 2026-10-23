# Phase 111 — Non-Repainting ZigZag Weekly Options Research Manuscript

## Abstract
This fixed-rule exploratory study tests single-leg weekly NIFTY option selling from the last confirmed daily ZigZag-style pivot. Because the submitted Pine script imports an external library whose body was not included, the Python signal is a causal MT4-style proxy rather than verified TradingView parity. No strategy promotion follows from this screen.

## Research question, aim and objectives
Test whether selling the 0.10-absolute-delta option indicated by the last confirmed daily pivot, with buyback at absolute model delta 0.50 or fixed expiry-day 10:00 exit, produces robust after-cost outcomes versus no-stop hold-to-expiry. Objectives are no-look-ahead signals, exact contracts/minutes, explicit exclusions, 24 costs and chronological splits.

## Methodology
One-minute NIFTY OHLC is aggregated into complete 375-minute sessions. Depth 12, Deviation 5 ticks and Backstep 2 are used by a deterministic causal ZigZag proxy. Only opposite-reversal-confirmed pivots known by previous expiry close are eligible. HL/LL selects a put; HH/LH selects a call. The exact 09:59 bar close determines the nearest valid 0.10 absolute-delta option; entry uses exact 10:00 open. A completed minute whose model-estimated absolute delta is at least 0.50 fills at the next exact minute open. No interpolation/forward-fill is allowed. One historical lot and a date-aware fee model are used.

## Statistical analysis
Development is through expiry 2023-12-31; validation is 2024–2025; holdout is 2026 onward to the available source cutoff. The 24-case registered cost grid compares stopped and no-stop outcomes on matched eligible campaigns. Campaign bootstrap confidence intervals and one-sided t-tests are descriptive only; no signal parameters are tuned.

## Results
The Phase 111 report, summary.json, coverage.json, campaign_exclusions.csv, campaign_ledger.csv and cost_grid.csv carry the source revision, coverage funnel, costs and results. A null estimate on an empty split is not a measured zero return.

## Discussion
Exact option coverage may select a nonrepresentative subset. Model IV/delta assumes European Black–Scholes, a fixed 6% rate and 0% yield. OHLC prices are simulated fills, not bid/ask/depth. The source dataset is declared CC BY-NC 4.0 and has a historical coverage cutoff; account-specific Paytm Money contract charges are unverified. Confirmed-label parity against TradingView remains open.

## Strengths and limitations
Strengths: frozen single rule, causal confirmation, exact timestamp joins, matched no-stop comparison, cost stresses and recorded exclusions. Limitations: unverified ZigLib parity, partial options data, sparse holdout, proxy prices/model Greeks and potential selection bias from path-complete campaigns.

## Conclusion and future direction
No strategy is promoted from this screen. A bounded follow-up may compare a supplied TradingView label fixture to this proxy and test the frozen rule with better quote data. No recursive parameter search is authorized.

## Appendices
Source hashes and expiry files are in source_manifest.csv; exact scheduled/excluded denominators are in scheduled_campaigns.csv and campaign_exclusions.csv; cost and split summaries are in cost_grid.csv.
