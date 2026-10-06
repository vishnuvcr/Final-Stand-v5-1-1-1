# Phase 43 Literature Review — India VIX and Option-Strategy Selection

## India VIX
NSE defines India VIX as a near-term volatility expectation derived from NIFTY option order-book prices, with a 30-calendar-day constant-maturity interpretation. Higher India VIX indicates higher expected volatility. This supports treating VIX as an ex-ante state variable, not as a standalone directional forecast.

Sources:
- NSE India VIX: https://www.nseindia.com/static/products-services/indices-indiavix-index
- NSE India VIX white paper: https://nsearchives.nseindia.com/s3fs-public/inline-files/white_paper_IndiaVIX.pdf
- NSE computation methodology: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/India_VIX_comp_meth.pdf

## Indian options evidence
Thomas (2015), "Hedging Market Risk and Volatility: Evidence from Indian Options Market", studies Indian option hedging strategies over 2001–2015 and reports that filters including VIX, P/E and put-call ratio can affect profitability and hedging.

Pillai (2026), "Trading the Volatility Risk Premium on Nifty 50: Strategy Backtest with Realistic Frictions", tests multiple NIFTY short-volatility strategies with explicit transaction costs and reports negative net performance for the tested strategies, with tail risk a major driver. This is a strong reason to include realistic costs and tail-loss analysis.

Sajjan (2026), "Variance Risk Premium in Nifty 50 Weekly Expiry Cycles: VIX Calibration Bias and Regime Dependence", studies weekly NIFTY expiry cycles and reports regime dependence while finding that VIX does not perfectly forecast realized weekly moves. This motivates conditional testing instead of assuming high-VIX=short-volatility.

Sources:
- https://ssrn.com/abstract=2587017
- https://ssrn.com/abstract=6876580
- https://ssrn.com/abstract=6918100

## Volatility timing and regime literature
Kita, Ronchetti and Zhang (2023), "Option-Based Volatility Timing", reports that option-implied information can improve volatility timing and is particularly informative in stressed uncertainty states.

Božović (2024), "VIX-managed portfolios", finds that VIX-based risk scaling can improve risk-adjusted outcomes and argues that implied volatility embeds tail-risk information.

Yang (2024, revised 2026), "Volatility-Managed Volatility Selling", reports that reducing short-volatility exposure after high-volatility states can improve risk and return even after transaction costs.

Papanicolaou and Sircar (2014), "A Regime-Switching Heston Model for VIX and S&P 500 Implied Volatilities", provides formal evidence that volatility regimes change implied-volatility dynamics.

Sources:
- https://ssrn.com/abstract=4391540
- https://ssrn.com/abstract=4507634
- https://ssrn.com/abstract=4761614
- https://ssrn.com/abstract=2164500

## Strategy-family evidence
De Saint-Cyr (2023), "A Simple Historical Analysis of the Performance of Iron Condors on the SPX", explicitly tests iron-condor performance by VIX and market condition and reports material regime dependence.

Lu (2026), "Navigating IV: Options Trading Strategy in Earnings Season", compares straddles, strangles, iron butterflies and iron condors and documents meaningful differences under implied-volatility conditions.

Perz (2026), "Profitability of Selected 0DTE index options strategies", reports historical profitability for tested SPX iron-condor variants. This is hypothesis-generating only because the market, maturity and sample differ from NIFTY.

Sources:
- https://ssrn.com/abstract=4643378
- https://ssrn.com/abstract=6710818
- https://ssrn.com/abstract=7162898

## Research gap
The literature mostly examines one strategy, U.S. index options, or portfolio-level volatility timing. Phase 43 creates one directly comparable NIFTY weekly panel spanning major defined-risk strategy families under one timestamp, one cost model and one point-in-time VIX regime definition.

## Working hypotheses
H1: Strategy performance differs by India-VIX regime.
H2: At least one defined-risk strategy has a statistically and economically different regime profile from the unconditional result.
H3: A preregistered VIX router can outperform an unconditional benchmark without holdout tuning.
H4: Any apparent short-volatility edge will weaken materially under realistic costs and tail-loss analysis.

The hypotheses are falsifiable; no direction of the effect is assumed.