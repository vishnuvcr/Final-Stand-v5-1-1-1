# Phase 44 Literature Review — VIX/VRP Tuning Context

## Purpose

Phase 44 does not assume that a positive India-VIX regime effect exists. The literature is used to motivate the *types* of tuning that are economically plausible and to define the limitations that the empirical study must explicitly test.

## Key findings from prior research

**Garg & Vipul (2015), Journal of Futures Markets.** Indian option prices contain evidence of a volatility risk premium, but transaction costs materially reduce the economic value of option strategies. This directly motivates explicit brokerage and statutory-cost modelling rather than gross-payoff screening.

**Jain, Varma & Agarwalla (2019), Journal of Futures Markets.** Indian equity-option implied volatility contains information about future volatility and option risk premia, supporting investigation of volatility-conditioned structures while not implying that a simple VIX threshold is sufficient.

**Dynamics of variance risk premium: Evidence from India (2021).** The Indian NIFTY volatility-risk-premium literature reports regime and forecast-dependence questions but also shows that market-neutral option payoffs can be strongly affected by tail behaviour.

**Agarwal (2026 preprint).** A large one-minute NIFTY-option sample finds positive average VRP but substantial time-series persistence and left-tail asymmetry. This supports testing threshold stability rather than assuming a constant premium.

**Pillai (2026 preprint).** A recent NIFTY study that explicitly includes implementation frictions reports that short-volatility strategies can lose money after realistic costs and tail losses. This reinforces the Phase-44 requirement for cost stress and bounded-risk preference.

**John (2026 preprint).** A recent out-of-sample NIFTY VRP study uses pre-registered percentile conditioning and a post-2024 market-structure break. Its design supports the use of percentile-based state variables and strict out-of-sample calibration.

**Sajjan (2026 preprint).** A recent weekly-expiry study reports aggregate VIX information about move magnitude but weaker performance inside low-VIX regimes. This supports testing LOW/HIGH states separately rather than treating VIX as globally linear.

## Research implication

The literature provides a rationale for testing percentile-conditioned volatility states and for treating transaction costs/tail risk as first-class constraints. It does not provide evidence that any Phase-44 candidate should be assumed profitable ex ante.

## External references

- Garg, S. & Vipul (2015), *Volatility Risk Premium in Indian Options Prices*, Journal of Futures Markets 35(9), 795–812. DOI 10.1002/fut.21680. citeturn985549search3
- Jain, S., Varma, J.R. & Agarwalla, S.K. (2019), *Indian equity options: Smile, risk premiums, and efficiency*, Journal of Futures Markets 39, 150–163. citeturn985549search5
- *Dynamics of variance risk premium: Evidence from India* (2021). citeturn985549search9
- Agarwal, Y. (2026), *The Variance Risk Premium in Nifty 50: A Structural Anatomy Across Nine Empirical Filters*. SSRN preprint. citeturn985549search6
- Pillai, S. (2026), *Trading the Volatility Risk Premium on Nifty 50: Strategy Backtest with Realistic Frictions*. SSRN preprint. citeturn985549search2
- John, A.R. (2026), *Harvesting the Volatility Risk Premium in Nifty Index Options: Out-of-Sample Evidence and the Post-2024 Regulatory Regime Break*. Preprint. citeturn985549search1
- Sajjan, S. (2026), *Variance Risk Premium in Nifty 50 Weekly Expiry Cycles: VIX Calibration Bias and Regime Dependence*. SSRN preprint. citeturn985549search10
