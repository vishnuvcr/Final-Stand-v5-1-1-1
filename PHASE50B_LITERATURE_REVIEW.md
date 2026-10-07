# Phase 50B Literature Review — VIX, Tail Geometry and NIFTY Options

## Purpose

The literature review is used only to motivate testable hypotheses. It does not count as evidence that any specific Tradetron or NIFTY strategy is profitable.

## Indian option-market evidence

### Garg & Vipul (2015) — Volatility Risk Premium in Indian Options Prices

The study finds a volatility risk premium in Indian option prices and reports that apparent strategy returns decline materially once normal transaction costs are included. This directly supports Phase 50B's requirement that native strategy reports not be accepted without the project's brokerage, statutory charges and slippage model. citeturn542461search2turn542461search4

### Jain, Varma & Agarwalla (2019) — Indian equity options

The authors find that a smile-adjusted Black model fits Indian equity-option prices and that implied volatility contains incremental information about future volatility. This supports treating the volatility smile and delta-defined strike selection as economically meaningful variables rather than assuming fixed strike distance is invariant across regimes. citeturn542461search0turn542461search1

### Potharla & Sen (2026) — NIFTY-50 smile asymmetry

A 2026 SSRN study of NIFTY-50 index options reports that smile convexity becomes more pronounced in high-volatility regimes and that liquidity, trading activity and maturity affect downside-tail pricing. This is directly relevant to the Phase-50 observation that near-ATM VIX sweeps may not exhaust high-VIX far-OTM geometry. citeturn542461search6

### Pillai (2026) — NIFTY volatility-risk-premium strategies with realistic frictions

A 2026 SSRN backtest of four NIFTY short-volatility strategies over 119 monthly cycles reports negative net annualized performance after explicit STT, brokerage and slippage. The paper attributes most of the adverse outcome to tail risk rather than transaction costs alone. This is important negative-context evidence for Phase 50B: a positive native option strategy report must survive both realistic friction and tail-risk tests. citeturn542461search7turn542461search9

## Implications for Phase 50B

1. VIX should be treated as both a regime variable and a potential controller of strike/delta selection.
2. Fixed OTM strike counts and fixed delta targets need not be interchangeable across volatility states.
3. High-VIX far-OTM strategies are plausible hypotheses but are especially vulnerable to sparse data, wide tails and execution costs.
4. Positive native backtests cannot substitute for common-model chronological replay.
5. A strategy that looks attractive only in a tiny high-VIX sample is not statistically promotable.

## Repository cross-check

The Daily-Options literature review already catalogues Indian volatility-risk-premium, smile/skew and condor evidence and explicitly treats video-derived strategy descriptions as hypotheses until cost-aware walk-forward validation.

## Research gap

The most useful open question for this project is not whether options contain volatility premia in aggregate; it is whether **specific source-derived strategy geometries change economically with VIX state and whether that relationship survives exact option-quote replay and realistic frictions**.
