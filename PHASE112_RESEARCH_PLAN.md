# Phase 112 — Greek Stop-Loss Combinations for ZigZag Weekly Options

**Branch:** `phase-112-zigzag-greek-stop-combinations`  
**Parent:** Phase 111 ZigZag weekly option rule  
**Registered:** 2026-10-24 IST  
**User instruction:** Check Greek combinations as stop-loss rules; tester review waived  
**Signal changes:** NONE. Keep the confirmed-only daily ZigZag proxy and entry/exit contract logic fixed.  
**Promotion:** None until there is adequate evidence; the TradingView ZigLib parity caveat remains in force.

## Research question, aim and objectives

**Question:** Do Gamma, Vega, Theta or Rho stop conditions improve after-cost results and drawdown relative to Delta-only and no-stop exits for the same ZigZag entries and selected 0.10-absolute-delta option?

**Objectives**
1. Reuse Phase 111's exact signal/contract/timestamp eligibility gate and its frozen source revision when available.
2. Estimate Delta, Gamma, Vega, Theta and Rho at each completed minute from observed option close, spot close, time to expiry, IV and the fixed European Black–Scholes assumptions (6% continuous rate, 0% dividend).
3. Test each Greek as a stand-alone stop, Delta-only sensitivity, all pairwise and higher-order metric combinations, with OR/AND aggregation.
4. Compare every stop rule to both Delta-only thresholds and a matched no-stop hold-to-expiry-day-10:00 benchmark on the same campaign at each cost scenario.
5. Report all planned, eligible and excluded campaigns, stop rate, exact fill convention, split-specific P&L, costs, drawdowns, coverage and uncertainty.
6. Publish a finite report and manuscript. Do not recursively expand the grid or promote on development/validation fit.

## Frozen entry/exit rule inherited from Phase 111

- Daily chart proxy with Depth=12, Deviation=5 ticks, Backstep=2; only a last confirmed pivot known by the preceding observed expiry's session close is used.
- HL/LL => sell one NIFTY PE; HH/LH => sell one NIFTY CE.
- Contract/side selected from exact 09:59 completed bar to minimize distance from absolute model Delta 0.10; tie breaks by spot distance then strike. Entry at exact 10:00 IST open on the first observed session after prior expiry.
- Scheduled exit is exact 10:00 IST open on target weekly expiry day.
- At each completed one-minute close, calculate Greek metrics; a stop first hit at close timestamp t is filled at the next exact observed minute open t+1 minute. Never fill at the stop-trigger close or retrospectively within the same bar.
- Any missing contract minute, spot minute, invalid OHLC, invalid IV/Greek, or unavailable next-minute exit open invalidates the campaign for all candidates. Do not forward-fill or invent a fill.
- The current source data was revision SHA `0f4800e43e6f96cec0794369d78eb4d3c4211ef5` with expiry coverage ending 2026-08-04 in the previous Phase 111 run. Phase 112 resolves and records its own revision and does not assume coverage beyond the observed files.

## Greek definitions and frozen normalization

Use per-option-unit Greek values. Let S=spot, K=strike, sigma=IV, tau=years remaining, and C0=entry premium. Use model-estimated European Greeks; these are not exchange-published Greeks.

| Metric | Minute-level value used for trigger | Individual threshold sweep | Meaning |
|---|---|---|---|
| Delta | `abs(option_delta)` | 0.30, 0.40, 0.50, 0.60 | Absolute Delta; Delta-only 0.50 is the direct reference |
| Gamma | `0.5 × abs(Gamma) × (0.005 × S)^2 / C0` | 0.05, 0.10, 0.20, 0.30 | Convexity-only estimate for a 0.5% spot move, as a fraction of entry premium |
| Vega | `abs(Vega × 5 IV-points) / C0` | 0.05, 0.10, 0.20, 0.30 | Estimated premium fraction exposed to a 5-vol-point implied-volatility move |
| Theta | `current short theta / entry short theta` | 0.00, 0.25, 0.50 | Stop if the short option's daily theta cushion falls to or below threshold × entry cushion. Theta configs are invalid only if entry short theta is nonpositive/unavailable; such campaigns are explicitly excluded for every candidate to preserve paired comparison. |
| Rho | `abs(rho per 1 percentage-point rate move) / C0` | 0.0001, 0.0005, 0.0010, 0.0025 | Premium fraction represented by a hypothetical 100 bp interest-rate change. Rho stops may rarely/never trigger over weekly maturities; report actual hit counts, don't relax thresholds after looking at results. |

The fixed thresholds for Greek-combination rules are **Delta 0.50, Gamma 0.20, Vega 0.20, Theta 0.25, Rho 0.0005**. Metric comparison is based on these registered, normalized quantities, not raw Greek magnitudes. Delta/Gamma/Vega/Rho trigger when metric >= threshold; Theta triggers when ratio <= threshold.

## Registered candidate grid

- No-stop benchmark.
- Individual-threshold sweeps for each of Delta, Gamma, Vega, Theta and Rho (19 configs total).
- For each of the 26 multi-Greek subsets of size 2 through 5, test both ANY (first metric to hit) and ALL (all listed metrics must breach on the same completed minute) using fixed thresholds: 52 configs.
- Total registered candidates including no-stop: 72. Do not rank on holdout; do not add or remove a config after inspecting P&L.
- Same-event, same-cost comparisons; report paired incremental P&L vs no-stop, and where relevant vs Delta=0.50.

## Costs and statistics

All 24 registered cost cases:
- Brokerage: ₹10 / ₹15 / ₹20 per order.
- Adverse slippage: ₹0 / ₹0.05 / ₹0.25 / ₹0.50 per option unit on both entry and exit.
- Fee multiplier: 1.0× / 1.5×.
Use date-aware historical lot size and model the date-effective STT, exchange, IPFT, SEBI, stamp duty and GST from the Phase 111 helper. Treat those as approximate; Paytm Money-specific account contract notes are not supplied, and displayed OHLC is not bid/ask execution data.

Chronological splits: development expiry through 2023-12-31; validation 2024-01-01 to 2025-12-31; holdout 2026-01-01 onward limited by source coverage. For each candidate/split/cost report trade count and coverage, gross/net P&L, per-trade mean/median, return on entry premium, win rate, profit factor, max drawdown, stop-hit rate, mean P&L 95% bootstrap interval and matched paired uplift interval. Report p-values descriptively only, accounting for small sample and multiple comparisons; don't present nominal p-values as proof. Test mathematical consistency of P&L = gross minus all costs and candidate-specific fill chronology.

## Gates and finite stopping rule

| Gate | Task | Completion condition |
|---|---|---|
| 112.0 | Register protocol, definitions, and candidate grid | This plan is committed before results |
| 112.1 | Validate current source, Phase 111 lineage, schema and expiry coverage | Dataset revision/hash manifest recorded |
| 112.2 | Greeks, stop timing and cost regressions | Tests pass for Greek signs/units, OR/AND, fills, no look-ahead, and P&L arithmetic |
| 112.3 | Build fixed-rule minute paths and campaign ledger | Every scheduled campaign is eligible or has a specific reason |
| 112.4 | Evaluate all 72 candidates × 24 costs × 3 chronological splits | All completed rows reconcile; no holdout tuning |
| 112.5 | Report, charts, manuscript and conclusion | Key metrics and limitations published; no strategy promotion without adequate sample |
| 112.6 | Update status/log/error log/README; stop | Stop here; no endless loops or parameter fishing |

## Major limitations
- Phase 111's supplied Pine source imports `DevLucem/ZigLib/1` but does not include that library body. The Python engine's confirmed-only ZigZag is a causal proxy and has not been demonstrated byte-for-byte against TradingView labels.
- Minute close-based Black–Scholes IV/Greeks use constant rate/yield; actual volatility surfaces and exchange Greek feeds are unavailable in this replay.
- OHLC opens plus modeled slippage are synthetic fills, not order-book executions.
- Options data have partial strikes and declared CC BY-NC 4.0 license; path-completeness filters can select a nonrepresentative subset.
- Holdout can be too small; a profitable one-trade result is not confirmatory.
- No tester review or developer/tester branches will be created, per explicit instruction.

## Existing source references
- Phase 111 engine/tests/report on branch `phase-111-zigzag-weekly-expiry-options`.
- Dataset: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- TradingView dependency: https://www.tradingview.com/script/NC3cgEcT-ZigLib/
- Phase 110 Greek engine provides prior cost/fee calculation context; Phase 112 is a one-leg study and recomputes the Greek stops for the inherited fixed entries.
