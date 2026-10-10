# Phase 80 — Expanded strategy universe and literature audit
Date: 2026-10-10
Status: FROZEN PLAN — discovery is open again; promotion remains gated.

## Research question
Has the project exhausted the meaningful combinations of option structures, holding horizons, point-in-time volatility/market-state information, and exits? Which genuinely under-tested families and public sources deserve bounded follow-up?

## Explicit answer to the completeness question
No finite project can test literally every possible combination. Existing work is broad, but not exhaustive. The repository records a Phase-45 sweep of 20 new ready-made structures plus 22 previously studied families and earlier VIX, feature, symbolic, ensemble, regime, selector, ratio, and stop-rule research. The Phase-45 execution protocol primarily enters four sessions before expiry at 10:00 and holds toward expiry-day close; it therefore does not cover all daily time-of-day/overnight exposure choices. A new finite experiment is justified, not a claim that every permutation will be tested.

## Research aims and objectives
1. Inventory tested, partially tested, and not-yet-tested axes.
2. Discover new published results and public data leads without treating marketing/video claims as proof.
3. Register a limited, interpretable holding-horizon experiment that is orthogonal to the existing D-4-to-expiry sweep.
4. Maintain exact contract/strike/side checks, point-in-time feature timestamps, source rights, Paytm Money costs, adverse slippage, and no forward filling.
5. Use temporal splits and family-wise inference; no promotion from exploratory selection alone.
6. Set a finite end condition and preserve manuscript inputs.

## Existing tested universe (inventory is not a claim of exhaustive combinations)
- Option structures: long/short straddles and strangles; bull/bear vertical spreads; iron fly/condor; long iron fly/condor; call/put butterflies and broken-wing butterflies; ratios/backspreads; calendars; synthetic futures; risk reversals; Batman/double ratios; Jade Lizard variants; condor/butterfly/range-forward families; dynamic ratio/dynamic-n.
- Selectors and covariates: India VIX level/change/regime; premium-direction selectors; OHLC range proxies; historical OI eligibility; feature matrix, symbolic rules, ensemble and rank-to-action policy.
- Exits: target/expiry fallback; pre-expiry and expiry-day loss controls; MFE/conditional stops; entry filters; varying target/entry/DTE/wing/delta parameters in registered prior phases.
- Missing or materially under-covered axis: paired same-session intraday vs overnight holding window under identical contract/structure rules, with realized point-in-time volatility-state stratification and explicit liquidity masking. Some prior research discusses overnight option returns, but the Phase-45 strategy sweep is not a direct test of this axis.

## New-source audit (discovery only; rights status is separate from technical usefulness)
- Bhat, Pandey & Rao (2024), Journal of Futures Markets, “The asymmetry in day and night option returns: Evidence from an emerging market,” DOI 10.1002/fut.22512. Published result concerns delta-hedged short NIFTY option returns, with positive/significant overnight returns versus negative intraday returns; do not equate it to profitability of a static option spread.
- Zenodo 10899828, “Nifty spot, futures and options one-minute data from 2017 to 2020,” https://zenodo.org/records/10899828. Technically promising because it contains spot, futures and option OHLCV; explicit license/rights is blank or not clear in the record; do not cache/redistribute before rights review.
- Hugging Face dataset artist-23/nifty-options-data, https://huggingface.co/datasets/artist-23/nifty-options-data. 34M rows spanning 2020-12-29 to 2025-12-26, fields include OHLC, IV, OI, volume, spot, strike/side and relative strike labels. Dataset card does not clearly identify a reuse license; expiry identity appears represented in part by expiry type rather than necessarily exact expiry date. Lead only; not approved for data-sensitive replay.
- Hugging Face dataset rissin/nse-options-intraday, https://huggingface.co/datasets/rissin/nse-options-intraday. 259M rows, includes explicit expiry/strike/CE-PE and OHLC; intraday track is described as Upstox API 1-minute candles from Oct 2024 onward; OI is NaN in those intraday rows; license is “other” and card says redistribution must align with Upstox terms. Do not adopt raw files until automated-use/retention/redistribution terms are established.
- Hugging Face thetrademarkk/india-index-options-1m, https://huggingface.co/datasets/thetrademarkk/india-index-options-1m. Existing primary source with CC-BY-NC-4.0 tag, partial option coverage and OHLCV(+OI); usable only within applicable noncommercial terms and not as execution quote/depth.
- QuantDev-stack/OptionVault, https://github.com/QuantDev-stack/OptionVault. Repository advertises option OHLC, Greeks, depth and 1-sec/1-min sample files; README says full data requires a separate licensed package. Sample repo is not proof of licensed complete history.
- sahilempire/nifty-options-research-lab, https://github.com/sahilempire/nifty-options-research-lab. New public code/research corpus with strategy/cost/slippage modules and long option-structure and data-source literature files. Its empirical claims are third-party self-reported and must not be treated as our own validated result; code and ideas can inform an independent spec audit.

## New research question for Phase 81
For the same frozen option structure and same session, does holding the position intraday (09:20 entry to 15:20 exit) versus overnight (15:20 entry to next trading session 09:20 exit) change net returns and tail risk after Paytm Money charges, adverse slippage, and liquidity filters? Does that difference vary with lagged India VIX state?

### Frozen universe (six structures; no optimization of signals)
1. Short ATM straddle (unbounded; diagnostic only; never a live candidate).
2. Short ATM iron fly, protective wings W ∈ {100, 200, 300} points (three registered width variants).
3. Long ATM iron fly, corresponding widths (long-volatility contrast).
4. Short iron condor: short OTM ±100, buy wings ±300 (defined risk).
5. Bullish put credit spread: short put ATM−100, long put ATM−300.
6. Bearish call credit spread: short call ATM+100, long call ATM+300.
These are fixed templates, not a claim they are optimal. For strategies 2 and 3, wing widths are the only structure variants; count each separately in the multiple-testing ledger.

### Holding-window definitions
- Both windows share one ex-ante strike anchor: derive ATM from the prior 09:19 minute close and use the same exact expiry/strike/side basket for both matched windows.
- Day session: enter on 09:20 candle open and exit on 15:20 candle open on the same valid session.
- Overnight: enter the same strike basket on 15:20 candle open and exit on the next valid trading session's 09:20 candle open. The ATM anchor is intentionally held constant to make the time-window contrast paired and avoid changing the structure as a hidden second variable.
- Use listed expiry strictly later than the entry date; skip expiry dates themselves and sessions where the next trading date is contract expiry, so no contract is silently switched or carried through expiry settlement.
- Require each leg's exact expiry/strike/side and nonzero volume at entry and exit, positive open prices, and exact timestamps. No forward fill, sparse-strike ordinal mapping, or synthetic bars.
- Exclude dates with missing or invalid option bars and log the reason. Report liquidity/coverage counts before interpreting performance.
- Reference prices are candle open (not quotes); apply one adverse ₹0.05 tick per leg per fill, plus frozen date-aware fees, brokerage assumed ₹10 per executed order and all modeled statutory charges. Results remain indicative because OHLC does not supply historical bid/ask/depth.
- Use only lagged VIX (last completed prior trading day). No same-day close/VIX leakage.
- Bhat et al. studied delta-hedged option returns. This experiment uses static structures and therefore is a new adaptation, not a replication of that paper.

## Temporal policy and inference
- Development: entries through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31; candidate shortlist is frozen before holdout is touched.
- Holdout: 2026-01-01 through 2026-09-30, used only in a later confirmation phase after a preregistered selector is committed.
- Phase 81 should rank candidates using DEV and VAL only and keep holdout outputs unopened/unreported.
- Phase 82 should compute paired session differences, session/expiry clustered bootstrap intervals, Holm family-wise adjusted significance across the declared tests, drawdown and tail measures, year/regime breakouts and candidate freeze record. Report test count and every exclusion.
- No winner will be promoted solely because its net total is positive. Require sufficient sample, positive net after stress, credible liquidity coverage, positive validation and frozen holdout confirmation, no material tail-risk/drawdown deterioration, and adjusted inference consistent with a real edge. If nothing passes, conclude no promotion rather than expand the grid post hoc.

## Finite end condition
Phase 80 discovery closes after this source/strategy matrix. Phase 81 performs one registered temporal-axis sweep. Phase 82 performs statistical inference/frozen holdout confirmation only if data sufficiency passes. Phase 83 assembles the manuscript and closes the study; no rolling parameter search. Reopening requires a genuinely new source with usable rights/coverage or a separately justified registered hypothesis.
