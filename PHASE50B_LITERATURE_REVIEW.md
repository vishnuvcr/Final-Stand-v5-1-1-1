# Phase 50B Literature Review — VIX, Tail Geometry and NIFTY Options

## Purpose

This review motivates testable hypotheses only. It does not establish profitability for any specific Tradetron or NIFTY strategy.

## 1. Indian option volatility risk premium

Garg & Vipul (2015), *Journal of Futures Markets*, document a volatility risk premium in Indian options. They report that option-strategy returns exploiting the premium are substantially reduced once normal transaction costs are included, and conclude that transaction-cost efficiency is central to the economic usefulness of the premium. DOI: 10.1002/fut.21680. citeturn657172search0

**Phase-50B implication:** native strategy P&L must be treated as provenance only; Final Stand must replay with brokerage, statutory charges and adverse execution.

## 2. Indian option smile / implied-volatility information

Jain, Varma & Agarwalla (2019), *Journal of Futures Markets*, find that a smile-adjusted Black model fits Indian equity-option prices well and that implied volatility has incremental predictive power for future volatility. DOI: 10.1002/fut.21971. citeturn657172search1

**Phase-50B implication:** delta-defined strikes and VIX-conditioned strike geometry are economically meaningful candidate dimensions, but they must be evaluated out of sample.

## 3. NIFTY-50 smile asymmetry and volatility states

Potharla & Sen (2026) study NIFTY-50 implied-volatility smile asymmetry across volatility and liquidity regimes. Their SSRN preprint reports stronger smile convexity during high-volatility regimes and regime-dependent maturity effects, with liquidity/trading-activity effects on tail pricing. SSRN 6857939. citeturn657172search4

**Phase-50B implication:** high-VIX strategy performance can plausibly depend on option-surface geometry, not simply on a scalar VIX level.

## 4. Recent NIFTY volatility-risk-premium evidence with explicit frictions

Pillai (2026), *Trading the Volatility Risk Premium on Nifty 50: Strategy Backtest with Realistic Frictions*, tests four systematic short-volatility strategies over 119 NIFTY monthly expiry cycles using explicit STT, brokerage and slippage assumptions. SSRN version posted 24 June 2026. The paper frames transaction costs and wide spreads as key constraints on implementable short-volatility performance. citeturn657172search2turn657172search3

**Phase-50B implication:** positive gross/native short-volatility results are not sufficient; cost-adjusted replay is essential.

## 5. NIFTY VRP is regime-dependent

Agarwal (2026), *The Variance Risk Premium in Nifty 50: A Structural Anatomy Across Nine Empirical Filters*, uses more than 43 million one-minute option bars from August 2022 to March 2026 and reports positive VRP on 74.9% of days, but also substantial persistence and asymmetric downside behavior. SSRN. citeturn657172search6

Sajjan (2026), *Variance Risk Premium in Nifty 50 Weekly Expiry Cycles: VIX Calibration Bias and Regime Dependence*, reports that High-VIX weeks have statistically distinct realized-volatility distributions and a positive directional bias in the study sample. SSRN 6918100. This is a hypothesis-generating result only; it is not evidence for any particular Phase-50B trade rule. citeturn657172search10

**Phase-50B implication:** later VIX-conditioned analysis should examine both volatility outcomes and directional asymmetry rather than assuming that HIGH VIX automatically means persistent downside.

## 6. Intraday regime research

Preethi S. R. (2026) uses 5-minute NIFTY data with unsupervised regime clustering and reports persistent baseline volatility states punctuated by shorter-lived elevated states. The paper finds regime-conditioned short-horizon volatility forecasts improve relative to an unconditional benchmark, while return differences between regimes are not consistently significant. SSRN 6316139. citeturn657172search13

**Phase-50B implication:** a VIX overlay should not be interpreted as a guaranteed direction signal; it is more defensibly a state variable controlling strike selection, hedge demand and risk.

## 7. Tail-risk / closing-period execution context

Mansuri (2026) reports elevated volatility into the NSE close, especially around 15:00–15:15 IST, in an SSRN study of intraday liquidity cascades and gamma effects. This is current preprint evidence and has not been independently validated here. citeturn657172search12

**Phase-50B implication:** expiry-day exits around 15:15 must be treated as an execution-sensitive part of the source rule, not merely as a bookkeeping timestamp.

## Research gap

The most useful unresolved question for this phase is not whether a volatility risk premium exists in aggregate. It is whether a **specific source-derived strategy geometry changes economically with VIX state and whether that relationship survives exact option-quote replay, historical lot sizes, brokerage/statutory costs, adverse slippage and chronological out-of-sample validation**.

## Reference list

- Garg, S., & Vipul. (2015). *Volatility Risk Premium in Indian Options Prices*. Journal of Futures Markets, 35, 795–812. DOI: 10.1002/fut.21680.
- Jain, S., Varma, J. R., & Agarwalla, S. K. (2019). *Indian equity options: Smile, risk premiums, and efficiency*. Journal of Futures Markets, 39, 150–163. DOI: 10.1002/fut.21971.
- Potharla, S., & Sen, G. (2026). *Conditional Dynamics of Volatility Smile Asymmetry: Evidence from Nifty-50 Index Options*. SSRN 6857939.
- Pillai, S. (2026). *Trading the Volatility Risk Premium on Nifty 50: Strategy Backtest with Realistic Frictions*. SSRN 6876580.
- Agarwal, Y. (2026). *The Variance Risk Premium in Nifty 50: A Structural Anatomy Across Nine Empirical Filters*. SSRN 6530119.
- Sajjan, S. (2026). *Variance Risk Premium in Nifty 50 Weekly Expiry Cycles: VIX Calibration Bias and Regime Dependence*. SSRN 6918100.
- Preethi S. R. (2026). *Intraday Volatility Regimes via Unsupervised Machine Learning: Evidence from the NIFTY Index*. SSRN 6316139.
- Mansuri, M. A. (2026). *Intraday Liquidity Cascades, Order Book Imbalance, and Gamma Explosions: A Quantitative Analysis of the 3:00 PM Regime Shift in NSE Index Derivatives*. SSRN.

