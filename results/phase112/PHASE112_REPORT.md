# Phase 112 — Greek Stop-Loss Combination Report

Generated UTC: 2026-10-24T07:03:44.109685+00:00  
Workflow: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40072066860  
Status: **EMPIRICAL SCREEN COMPLETE — NO PROMOTION**.

## Coverage and data provenance

- Dataset: \`thetrademarkk/india-index-options-1m\`, resolved revision SHA \`0f4800e43e6f96cec0794369d78eb4d3c4211ef5\`.
- Observed weekly expiry files: 267, from 2021-05-27 through 2026-08-04.
- Scheduled / eligible / excluded campaigns: **259 / 139 / 124**.
- Eligible split counts: development **93**, validation **45**, holdout **1**. The 2026 holdout has only one eligible event and cannot establish reliability.
- Exclusions: 50 incomplete selected-option paths, 22 no confirmed signal, 22 no valid 0.10-Delta contract, 17 missing/invalid/duplicate entry bars, 4 no next session, 3 invalid monitoring IV, 2 incomplete preceding-expiry daily candles, 2 unsupported historical lot-size dates, 1 incomplete spot path and 1 invalid session grid. Full row-level reasons are in \`campaign_exclusions.csv\`.
- The inherited selector requires a valid selected contract with pre-entry OI of at least 100 at the exact 09:59 bar. This common eligibility rule is recorded in the research log.

## Fixed entry and stop protocol

The entry rule did not change: last confirmed daily HL/LL sells one PE; HH/LH sells one CE; select the valid option closest to absolute model Delta 0.10 from the exact 09:59 completed bar; enter the exact 10:00 open next observed session after previous expiry. Scheduled exit is 10:00 on target weekly expiry.

The 72 candidates are: no-stop reference, 19 individual-Greek threshold variants and 52 multi-Greek combinations. Multi-Greek subsets use fixed normalized thresholds and either:
- **ANY:** stop if any included Greek breaches its threshold.
- **ALL:** stop only when all included Greeks breach on the same completed minute.

A stop is evaluated on a completed minute and filled at the next exact observed minute open. Missing/invalid minutes are not interpolated.

### Greek feature definitions

| Greek | Trigger feature | Normalization / interpretation |
|---|---|---|
| Delta | \`abs(Delta)\` | Absolute option Delta |
| Gamma | \(0.5 |\Gamma| (0.005S)^2 / C_0\) | Convexity risk for a 0.5% spot shock divided by entry premium |
| Vega | \(|\text{Vega}\times5|/C_0\) | Premium fraction for a 5-vol-point change |
| Theta | Current short Theta / entry short Theta | Breach when ratio is at or below threshold |
| Rho | \(|\text{Rho}|/C_0\) | Premium fraction for a 100-basis-point rate change |

Greeks are European Black–Scholes estimates with a fixed 6% rate and zero dividend, not exchange-published Greeks.

## Primary cost results

Primary cost ID: **B20_S0.25_F1.0** (₹20 brokerage/order, ₹0.25 adverse slippage per option unit per side, 1.0× modeled fees). All figures use one historical lot and modeled date-effective STT, exchange/IPFT, SEBI, stamp duty and GST.

| Split | Candidate | Trades / scheduled | Net P&L ₹ | Win % | Max drawdown ₹ | Stop hit % | Net uplift vs no-stop ₹ |
|---|---|---:|---:|---:|---:|---:|---:|
| Development | No stop | 93 / 133 | 24,244.61 | 86.0 | 7,192.71 | 0.0 | — |
| Development | Delta 0.50 | 93 / 133 | 7,116.47 | 81.7 | 13,666.73 | 12.9 | -17,128.13 |
| Development | Gamma 0.30 | 93 / 133 | 17,210.24 | 50.5 | 4,596.78 | 55.9 | -7,034.37 |
| Development | Theta 0.50 | 93 / 133 | 23,691.76 | 86.0 | 7,192.71 | 6.5 | -552.84 |
| Validation | No stop | 45 / 103 | 10,854.87 | 86.7 | 3,663.00 | 0.0 | — |
| Validation | Delta 0.50 | 45 / 103 | 7,066.39 | 86.7 | 5,133.91 | 11.1 | -3,788.48 |
| Validation | Gamma 0.30 | 45 / 103 | 7,567.34 | 60.0 | 3,154.76 | 42.2 | -3,287.53 |
| Validation | Theta 0.50 | 45 / 103 | 10,367.11 | 86.7 | 3,663.00 | 28.9 | -487.76 |
| Validation | Delta 0.50 + Gamma 0.20 (ANY) | 45 / 103 | 2,669.21 | 33.3 | 1,963.18 | 73.3 | -8,185.66 |
| Holdout | No stop | 1 / 23 | 2,051.41 | 100.0 | 0.00 | 0.0 | — |
| Holdout | Delta 0.50 | 1 / 23 | 2,051.41 | 100.0 | 0.00 | 0.0 | 0.00 |
| Holdout | Gamma 0.30 | 1 / 23 | 2,051.41 | 100.0 | 0.00 | 0.0 | 0.00 |
| Holdout | Theta 0.50 | 1 / 23 | 1,469.40 | 100.0 | 0.00 | 100.0 | -582.01 |

### What the Greek combinations showed

**No multi-Greek combination improved net P&L over no-stop in validation.** Across each of the 24 cost cases, the 52 combinations split into 37 with negative paired uplift and 15 with exactly zero uplift; none had positive paired uplift. The 15 zero-uplift rules simply never fired and therefore reproduced the no-stop result rather than improving it.

The most relevant trade-off was Gamma 0.30: in validation it produced **₹7,567.34**, beating the Delta 0.50 stop by about **₹500.95**, and had lower max drawdown (**₹3,154.76** versus **₹5,133.91**). But it still underperformed no-stop by **₹3,287.53**. Delta 0.50 + Gamma 0.20 with ANY logic cut validation drawdown to **₹1,963.18**, but net P&L fell to **₹2,669.21**, an **₹8,185.66** loss of uplift versus no-stop. These are risk/return trade-offs, not evidence the stops improve overall returns.

**Theta 0.50** was the least disruptive active single-Greek stop: validation net P&L was ₹10,367.11 versus ₹10,854.87 without a stop, with the same reported max drawdown and an uplift of -₹487.76. Theta thresholds 0 and 0.25 never triggered, so their apparent equality with no-stop is not a benefit.

**Vega and Rho thresholds triggered on 100% of validation campaigns** at the registered scales; both produced **-₹3,186.70** net and **-₹14,041.57** paired uplift versus no-stop. Gamma 0.05 and 0.10 stopped 97.8% and 95.6% of validation campaigns and also lost money. These results indicate the registered feature thresholds are too aggressive for this normalization; they must not be tuned after seeing these outcomes in the same sample.

### Cost robustness and statistical caution

- Across the 24 cost cases, all 19 individual-Greek variants had **zero cases with positive validation uplift versus no-stop**: 17 were negative in every cost case and two (Theta 0 and 0.25) were exactly equal to no-stop in every case.
- All 52 Greek combinations likewise had zero positive-uplift cases in validation across the full cost grid.
- The 95% bootstrap intervals are campaign-based and descriptive; grid size creates multiple-comparison risk, and the one-trade holdout cannot support inferential claims.
- The cost model is approximate, not a verified Paytm Money contract note. OHLC next-open fills do not model queue position, bid/ask spread or market impact.

## Decision

**No stop-loss candidate is promoted.** On this dataset, no tested Greek or combination improved after-cost net P&L over the matched no-stop reference in validation. Gamma 0.30 and Delta+Gamma ANY reduce drawdown somewhat but sacrifice substantial net return. Vega/Rho trigger scales and tighter Gamma thresholds are clearly too aggressive in this registered setup. The holdout has only one eligible campaign.

The supplied Pine imports \`DevLucem/ZigLib/1\`, but the library body was not included. The causal Python ZigZag signal is still a proxy, so the study is not a definitive reproduction of the exact TradingView indicator.

## Reproducibility artifacts

- \`summary.json\`, \`coverage.json\`, \`candidate_registry.json\`
- \`source_manifest.csv\`, \`scheduled_campaigns.csv\`, \`campaign_exclusions.csv\`
- \`candidate_cost_grid.csv\` (72 candidates × 24 cost cases × 3 splits)
- \`campaign_ledger_primary.csv\` and the three primary-cost figures under \`figures/\`
- [GitHub Actions run 40072066860](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/40072066860)
