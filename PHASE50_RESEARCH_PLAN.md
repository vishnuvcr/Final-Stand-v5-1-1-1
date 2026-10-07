# Phase 50 Research Plan — VIX × Far-OTM Tail Geometry

## Research question

Do genuinely out-of-the-money strike distances materially improve VIX-conditioned NIFTY defined-risk option strategies, particularly in HIGH/RISING/SPIKE VIX regimes, relative to the near-ATM geometries already tested in Phases 43–49?

## Why this phase exists

Phase 43–45 established that LOW/NORMAL VIX bearish defined-risk spreads were the strongest empirical cluster, while HIGH/SPIKE/RISING/HIGH_RISING did not yield a statistically defensible promoted strategy. However, those phases did not exhaust far-OTM geometry. Phase 49 searched only a near-ATM geometry band: Bear Call short offsets 1–4, Bear Put long offsets 0–2 with widths 1–4, and Put BWB body 0–1 with wings 1–4.

Phase 50 therefore tests the missing tail-distance dimension explicitly rather than concluding that high-VIX regimes have no exploitable strategy.

## Literature hypothesis

Research on option-implied tail risk and volatility skew motivates testing deep OTM options directly. Deep OTM option-implied tail measures have been found to contain information about future underlying returns, while volatility-skew work documents economically meaningful information in short-maturity OTM options. Recent NIFTY-50 research also reports that smile asymmetry/convexity becomes more pronounced in high-volatility regimes and that downside tail pricing is regime- and liquidity-sensitive.

These findings motivate, but do not establish, a tradable NIFTY strategy. All conclusions remain empirical and out-of-sample.

## Primary strategy families

Stage 1 uses only existing, defined-risk or explicitly bounded-tail families already present in the accepted Phase-43/45 universe:

1. Bear Call Credit Spread
2. Bear Put Debit Spread
3. Bull Call Debit Spread
4. Bull Put Credit Spread
5. Iron Condor
6. Iron Butterfly
7. Put Broken-Wing Butterfly
8. Call Broken-Wing Butterfly
9. Call Backspread
10. Put Backspread

Short straddles/strangles, ratio spreads, calendars and synthetic futures are not primary candidates because of their materially different tail-risk/data requirements. They remain diagnostic only.

## VIX regimes

Primary mutually exclusive level states:
- LOW
- NORMAL
- HIGH

Secondary transition tags:
- RISING
- FALLING
- SPIKE
- HIGH_RISING

A trade may carry one level state and one or more transition tags. Stage 1 prioritises HIGH plus all secondary high-volatility transition tags. LOW/NORMAL are retained as controls so that any improvement can be measured against the regimes where the project already has evidence.

## Strike-distance universe

The key novel variable is distance from point-in-time ATM measured in actual listed strike steps.

Tail-distance candidates:
- 2
- 3
- 4
- 5
- 6
- 8
- 10
- 12 strike steps from ATM

Stage 1 is deliberately wide enough to reach genuinely far OTM strikes. The engine must not substitute a missing farther strike with a nearer strike.

A descriptive entry-delta estimate will be recorded where option data permit a stable implied-volatility inversion. Delta is descriptive in Stage 1, not a selection variable, preventing a second large search family from being introduced immediately.

## Stage 1 — coarse tail-distance screen

Fixed controls:
- entry time: 10:00 IST
- entry horizon: 4 trading sessions before expiry
- family-specific registered baseline width
- tail distance: eight values above

Each family×VIX-state×distance cell is evaluated chronologically using:
- 2021–2023 development
- 2024–2025 validation
- untouched 2026 holdout only after validation freeze

The screen records trade count, net P&L, +50% cost stress, win rate, profit factor, maximum drawdown, quote coverage and active-vs-complement regime advantage.

Eligibility requires, at minimum:
- >=15 development trades in the cell
- positive stressed development mean/trade
- positive validation net and stressed net
- >=15 validation trades
- no catastrophic validation drawdown

No candidate is promoted from Stage 1 alone.

## Stage 2 — focused geometry refinement

The best tail-distance cells from Stage 1 are frozen by family×regime and then refined only within their local neighbourhood:
- width: 1, 2, 3, 4, 6, 8 steps as structurally appropriate
- entry time: 09:30, 10:00, 10:30, 11:00
- DTE: 3, 4, 5, 6

Stage 2 remains chronological and uses 2021–2023 for tuning only. Validation is frozen after selection.

## Stage 3 — statistical confirmation

For the final frozen candidates:
- active-VIX versus complement-VIX comparison
- 10,000 bootstrap resamples
- 10,000 one-sided permutation tests
- Holm correction across the final frozen family×regime candidates
- paired comparison against the registered near-ATM baseline where common expiries exist

A candidate must pass BOTH:
1. economic gate; and
2. statistical gate.

## Stage 4 — protected holdout

Only candidates surviving validation inference are evaluated on 2026.

Holdout cannot alter:
- strike distance
- width
- entry time
- DTE
- VIX definition
- execution model
- cost model

A positive holdout point estimate without statistical validation is classified as encouraging but non-confirmatory.

## Execution model

Reuse accepted Phase-43 cost and execution primitives:
- historical NIFTY lot sizes
- ₹10 brokerage per order
- date-aware STT/exchange/SEBI/IPFT/stamp/GST
- one adverse ₹0.05 option tick per leg at entry and exit
- +50% monetary fee/charge stress
- no forward fill
- no interpolation
- no nearest-strike substitution
- exact observed quotes only

## Required diagnostics

Phase 50 must explicitly publish:
- VIX state opportunity counts
- quote availability by tail distance
- missing/deep-OTM quote rates
- realized entry delta where available
- annual and split-level P&L
- maximum drawdown
- profit factor
- active-vs-complement inference
- baseline paired uplift
- candidate surface/plateau plots

A missing quote is never converted to a zero price or a synthetic quote.

## Self-audit gates

1. Tail-distance construction audit.
2. No nearer-strike substitution.
3. VIX point-in-time audit.
4. Historical lot-size audit.
5. Entry/expiry calendar audit.
6. Duplicate quote audit.
7. Development/validation separation.
8. Multiple-testing accounting.
9. Holdout contamination audit.
10. Empty-ledger/file-format audit.
11. Parameter-surface reproducibility audit.

Every failure must be appended to ERROR_LOG.md and the affected run classified NON-EVIDENCE until corrected.

## Stop condition

Phase 50 closes after:
- Stage 1 tail-distance sweep is complete,
- Stage 2 local refinements are complete where eligible,
- final frozen candidates receive validation inference,
- qualifying candidates receive protected 2026 confirmation,
- all artifacts/manuscript/figures are published,
- and a final decision is recorded.

Phase 50 must not reopen Phase 49's parameter search.