# Phase 111 — Non-Repainting ZigZag Weekly Option Test

**Branch:** `phase-111-zigzag-weekly-expiry-options`  
**Registered:** 2026-10-24 (Asia/Kolkata)  
**Parent:** `main`; prior research branches are read-only  
**Instrument:** NIFTY 50 weekly index options, inferred from the Final Stand project and the supplied NIFTY chart  
**Signal chart timeframe:** Daily  
**Rule status:** Frozen before replay  
**Tester review:** Explicitly waived by the user for this test; no developer/tester branches will be created  
**Promotion status at registration:** None

## Research questions

1. Does selling the option indicated by the last confirmed daily ZigZag++ label, using the exact non-repainting/no-look-ahead rule below, produce positive after-cost results?
2. How often does the intended 0.10-delta option selection succeed with exact contract identity and an observed 09:59 selection bar plus 10:00 entry bar?
3. How often does the sold option's model-estimated absolute delta reach 0.50 before the scheduled expiry-day exit?
4. How do outcomes change across date-effective transaction costs, brokerage, adverse slippage and a 1.5× fee stress?
5. Are results directionally consistent across chronological development (through 2023), validation (2024–2025) and the available 2026 holdout?
6. What is the difference between the specified stop-loss strategy and the same entry/contract with the stop disabled, on the same eligible campaigns?

## Aim and objectives

**Aim:** Test the supplied ZigZag++ low/high signal rule for NIFTY weekly option selling without repainting or future information.

Objectives:
- Lock the source signal/settings and record the unresolved library-parity limitation.
- Build daily NIFTY candles only from observed one-minute OHLC rows and evaluate the indicator state using data available no later than the prior listed expiry's close.
- Select one put after a last confirmed low (HL/LL), or one call after a last confirmed high (HH/LH), targeting absolute option delta 0.10.
- Enter at exactly 10:00 IST on the first observed NIFTY session after the previous observed weekly expiry.
- Monitor the sold option using completed one-minute bars; exit at the next exact minute open after absolute model delta first reaches 0.50, or at exactly 10:00 IST on the target weekly expiry date if no stop is triggered.
- Enforce exact observed timestamps and immutable expiry/strike/option-side matching. Never forward-fill, interpolate, or invent fills.
- Report the full source cutoff, eligibility funnel, exclusions, one-lot results, 24 cost scenarios, fixed-stop/no-stop comparison, chronological splits, uncertainty and limitations.
- Publish status, errors, logs, report, manuscript, machine-readable results and figures in this branch; sync a link and current status to the main README.

## Frozen interpretation of the supplied rule

### Indicator and repaint policy

The screenshot shows NIFTY 50 on a **1D** chart. Default source inputs shown/provided: Depth 12, Deviation 5, Backstep 2. Use the non-repainting path represented by `repaint=false`; do not act on a provisional last ZigZag leg. At the cutoff (the prior listed expiry session close), identify the latest **confirmed** pivot/label available from past data only:

- **HL or LL (a low):** sell one NIFTY put targeting absolute delta 0.10.
- **HH or LH (a high):** sell one NIFTY call targeting absolute delta 0.10.

The label is classified against the previous confirmed pivot of the same side: a higher high is HH; otherwise LH; a lower low is LL; otherwise HL. No future bars after the cutoff may enter the signal calculation.

**Important implementation limitation:** The user's Pine source calls the external TradingView library `DevLucem/ZigLib/1`; the library body itself is not included in the supplied code. This phase implements a deterministic, causal MT4-style ZigZag port based on the stated Depth/Deviation/Backstep and the author's comment that ZigZag++ is based on MT4. This is explicitly a **non-repainting implementation proxy**, not a claimed byte-for-byte TradingView-library reproduction. A strategy result is therefore labelled provisional with a source-parity caveat unless a reproducible chart-label parity sample is available. Do not tune the signal implementation to profitability.

### Trade timing and option selection

For each current target expiry in the observed options-file sequence, pair it only with the immediately preceding observed expiry if the expiry spacing is 4–10 calendar days (to avoid bridging a missing weekly file). The prior expiry must be an observed, complete NIFTY daily session. Signal state is frozen after that session's final available minute close.

- Entry date: first observed NIFTY trading session strictly after the prior expiry.
- Select from the target expiry's exact-contract file using the 09:59 IST option close and NIFTY close to estimate European Black–Scholes delta with a fixed 6.0% continuous risk-free rate and 0% dividend yield. Choose the valid option on the indicated side minimizing `abs(abs(delta) - 0.10)`; deterministic ties use strike distance from NIFTY spot then strike.
- Entry: selected option's exact 10:00 IST open. This respects signal/contract-selection causality; the selection is not recomputed from the 10:00 opening print.
- Scheduled exit: exact 10:00 IST open on the target expiry session. This is one fixed point within the requested 09:30–10:30 window.
- Stop: after each completed bar from entry until just before the scheduled exit, estimate delta from the observed option close and same-minute NIFTY close. When absolute delta is at least 0.50, buy back at the exact next market minute's observed option open. A stop signal may not fill on its own signal bar.
- Model Greeks are estimates, not exchange-published Greeks. The sold put's signed delta is negative; the stop uses absolute delta so the rule applies symmetrically to calls and puts.

### Data and eligibility

Primary source: Hugging Face dataset `thetrademarkk/india-index-options-1m`, files `index/NIFTY.parquet` and `options/NIFTY/YYYY-MM-DD.parquet`. Resolve the dataset revision to a commit SHA and hash every source file used. Use the existing Hugging Face token if present; source access remains optional-token for publicly accessible data. Use Actions caching and do not commit raw market data. The dataset card declares CC BY-NC 4.0 and warns that strike coverage is partial; research results are non-commercial only.

A campaign is excluded (and its reason retained) if any required source, signal, contract identity, selected option, exact timestamp, valid OHLC, model IV/Greeks, stop-monitoring minute, or next-minute exit open is unavailable/invalid. A missing option minute makes stop detection incomplete and is not silently ignored. Expiry pairs longer than 10 or shorter than 4 days are not treated as weekly campaigns. The latest available source date—not today's date—defines the research cutoff.

## Costs and benchmark

One historical NIFTY lot per campaign, using the date-effective lot schedule already registered in the project. Block unsupported lot-size transition dates.

Run all 24 combinations:
- Brokerage: ₹10 / ₹15 / ₹20 per order.
- Adverse slippage: ₹0 / ₹0.05 / ₹0.25 / ₹0.50 per option unit per side.
- Modelled fee multiplier: 1.0× / 1.5×.

Charge two brokerage orders per completed round trip. Entry slippage worsens the short-sale fill and exit slippage worsens the buyback fill. Itemize date-effective STT, exchange/IPFT, SEBI fee, stamp duty and GST. The primary comparison is ₹20/order, ₹0.25 adverse slippage per option unit per side, 1.0× fees. This model is not a verified Paytm Money contract note; present cost stresses rather than claim account-specific exactness.

The no-stop benchmark uses the same signal, same contract and same entry, but exits at 10:00 on target expiry. Compare strategy vs benchmark by matched campaign and cost scenario.

## Statistical analysis

- Report scheduled, excluded and eligible campaign counts and coverage by development (expiry through 2023-12-31), validation (2024-01-01 through 2025-12-31), and holdout (2026-01-01 onward, limited by observed source files).
- For both the stopped strategy and no-stop reference report gross/net P&L, net P&L per trade, return on entry premium, win rate, profit factor, max drawdown, stop-hit rate, holding time, exclusions and exact coverage.
- For each of the 24 cost cases report net P&L, return on entry premium, win rate and paired incremental P&L versus no-stop.
- Compute campaign-level 95% bootstrap intervals for mean net P&L and paired uplift where sample size permits, with a fixed random seed. Calculate one-sided t-test p-values only as descriptive inference; distinguish small samples, serial dependence and selection bias. No grid search of signal settings is permitted.
- Keep the holdout chronological and do not use it to alter rules. Low sample size, missing source coverage or no library-parity verification blocks promotion.
- All numerical outputs must reconcile to event and cost denominators. Empty-sample zero totals are placeholders and must never be described as observed zero-return results.

## Scientific workflow / finite stopping gates

| Gate | Work | Pass condition | Failure handling |
|---|---|---|---|
| 111.0 | Register plan/source/code and freeze exact rule | Plan, source script and status committed | Do not change plan without logged protocol amendment |
| 111.1 | Resolve source revision and inspect daily/option schemas, dates, duplicates and coverage | Auditable source manifest and observed cutoff | Log source blocker; no fabricated prices |
| 111.2 | Validate no-look-ahead signal, exact timestamps, IV/delta signs, fees and stop timing | Regression tests pass; prefix-invariance test passes | Log each error and correct without changing strategy |
| 111.3 | Run fixed-rule campaign replay | Eligible/excluded funnel and per-event outcome ledger reconcile | Exclude gaps; do not interpolate |
| 111.4 | Run 24 cost cases and paired no-stop comparison | Costs and P&L arithmetic reconcile for every completed event | Correct formula then rerun bounded phase |
| 111.5 | Statistics, figures, interpretation and manuscript | Results, caveats and split-specific uncertainty published | If sample insufficient, conclusion is inconclusive/no-go |
| 111.6 | Publish and stop | Repository README/status/logs/report/artifacts updated | No recursive parameter expansion; no promotion without evidence |

The test ends at Gate 111.6. No parameter expansion, repeated search loop or developer/tester gate is registered; the user explicitly waived tester review.

## Strengths and limitations to retain in the manuscript

**Strengths:** causal cutoff, no provisional-pivot entry, exact timestamp joins, exact expiry/strike/side, explicit exclusion accounting, fixed single signal rule, deterministic option selection, date-effective fees and slippage sensitivity, matched no-stop benchmark, frozen chronological splits and reproducible code/tests.

**Limitations:** the external ZigLib source code is not embedded in the supplied script; the Python indicator is a documented proxy pending TradingView label parity. Index/options source is partial and declared CC BY-NC 4.0. Delta/IV are model-estimated with a constant rate. OHLC open fills and slippage are simulations, not bid/ask/depth executions. Paytm Money account-specific charges are unverified. Missing data and strict path completeness may create selection bias. The holdout is bounded by the dataset's actual last expiry and may be too small for inferential claims.

## Research and extension references

- User-provided Pine source and indicator dependency: https://www.tradingview.com/script/NC3cgEcT-ZigLib/
- Source dataset/schema/license: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- Dataset's open monthly/daily market-data disclaimer should be retained in all public-facing results.
- Classic MT4 ZigZag description/source basis: https://www.mql5.com/en/code/7796
- Prior project protocol for exact-minute option selection, date-aware fees and historical lot sizes: Phase 110 plan/source in this repository's history.