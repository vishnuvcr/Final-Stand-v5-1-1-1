# Literature and Evidence Review

## Scope
This review supports the restarted NIFTY weekly-options ratio strategy. It is a background evidence review, not a claim that prior literature validates this exact rule.

## Indian NIFTY option-market efficiency

- Jain (2019), *Indian equity options: Smile, risk premiums, and efficiency*, studies Indian equity options and reports that a parsimonious smile-adjusted Black model fits option prices well and that implied volatility contains incremental information about future volatility. This supports treating the cross-strike premium structure as potentially informative about the market's volatility surface, while not establishing profitability of the present ratio rule.
- Mutum and Das (2019), *Lower Boundary Conditions and Pricing Efficiency Testing of Indian Index Options Market*, reports that apparent lower-boundary mispricing was concentrated in thinly traded and near-expiry options and argues that most signals were not exploitable after liquidity considerations.
- Vipul (2009), *Box-spread arbitrage efficiency of Nifty index options*, uses time-stamped transactions data to study model-free box-spread mispricing and arbitrage opportunities.
- Aggarwal and Gupta (2009) examine Nifty call/put spreads, box spreads and butterfly relationships as internal efficiency tests.
- Priyan and Mohanti (2015) similarly examine box-spread violations and report that many apparent violations were associated with low liquidity.
- Dixit, Yadav and Jain (2011) test lower-boundary conditions using Nifty futures prices rather than spot, emphasizing the importance of the correct underlying/forward reference in option pricing tests.
- A 2025 SSRN study by Kumar, Sarva and Gupta evaluates Nifty pricing discrepancies and explicitly incorporates transaction costs; its abstract reports that many theoretical pricing discrepancies become much less exploitable after costs.

## Volatility smile, skew and tail risk

- Jain (2019) provides evidence that the implied-volatility smile contains information about future volatility.
- A 2021 *Economics Letters* study on COVID-19 and Nifty options documents sharp changes in implied volatility smiles, skewness, convexity and risk-neutral densities during the pandemic, showing that option-surface shape changes materially across regimes.
- Potharla and Sen (2026, SSRN) study conditional dynamics of Nifty volatility-smile asymmetry from 2008–2024 and report relationships between smile curvature, liquidity, trading activity, maturity and volatility regimes.

These findings motivate Phase 4 regime and execution sensitivity checks: a rule based on OTM premium differences can be regime-dependent and can be distorted in illiquid far-OTM contracts.

## Ratio-spread literature

Ratio spreads are established multi-leg option structures in practitioner literature. Lowell's treatment describes ratio spreads as structures that can express directional bias and notes their dependence on implied-volatility skew and the risk of large adverse moves. This is conceptual background only; it is not evidence that the present NIFTY implementation has positive expectancy.

## Data and market-structure sources

The primary executable dataset is the public Hugging Face 1-minute NIFTY index-options dataset used in this project. Its documentation describes 1-minute OHLCV(+OI), strike, option type and expiry fields and warns that far/illiquid strikes can be sparse. The project therefore excludes incomplete observations rather than imputing missing far-OTM prices.

NSE's current contract-information pages document NIFTY option contract structure, strike schemes, price steps and lot-size files. Historical NSE circulars are used for date-aware lot sizes. In particular, NSE circular FAOP47854 states that NIFTY weekly expiries from August 2021 onward used the revised 50-unit lot; FAOP64625 raised the NIFTY lot from 25 to 75 for new contracts introduced from November 20, 2024; and NSE circular FAOP70616 later revised 75 to 65 for the 2026 cycle.

## Research gap

The reviewed literature addresses option-market efficiency, volatility-surface information and arbitrage relationships, but does not directly test the exact two-stage rule used here:
1. compare OTM6/7/8 call and put X values to choose the directional label;
2. within the selected side, prefer the highest n retaining at least 95% of maximum X;
3. enter a 1:-1:-1 three-leg OTM ratio at 4 trading sessions before expiry;
4. target 90% of initial X times lot size;
5. otherwise hold to expiry.

The present research therefore contributes a reproducible, cost-aware historical test of that specific rule, subject to the dataset and execution-model limitations documented elsewhere in the repository.

## Key sources

- Jain, S. (2019). *Indian equity options: Smile, risk premiums, and efficiency*. Journal of Futures Markets, 39(2), 150–163. DOI 10.1002/fut.21971.
- Mutum, K., & Das, A. K. (2019). *Lower Boundary Conditions and Pricing Efficiency Testing of Indian Index Options Market: Empirical Evidence from Nifty 50 Index*. Indian Journal of Finance. DOI 10.17010/ijf/2019/v13i3/142266.
- Vipul (2009). *Box-spread arbitrage efficiency of Nifty index options: The Indian evidence*. Journal of Futures Markets, 29(6), 544–562. DOI 10.1002/fut.20376.
- Aggarwal, N., & Gupta, M. (2009). *Empirical Evidence on the Efficiency of Index Options Market in India*. DOI 10.1177/097324700900500311.
- Priyan, P. K., & Mohanti, D. (2015). *An Investigation of Box-Spread Strategy and Arbitrage Efficiency on Indian Index Options Market*. DOI 10.1177/0972622520150106.
- Dixit, A., Yadav, S. S., & Jain, P. K. (2011). *Testing Lower Boundary Conditions for Index Options Using Futures Prices: Evidences from the Indian Options Market*. DOI 10.1177/0256090920110102.
- *The impact of COVID-19 on tail risk: Evidence from Nifty index options* (2021). Economics Letters, 204, 109878. DOI 10.1016/j.econlet.2021.109878.
- Potharla, S., & Sen, G. (2026). *Conditional Dynamics of Volatility Smile Asymmetry: Evidence from Nifty-50 Index Options*. SSRN 6857939.
- Kumar, A., Sarva, M., & Gupta, N. (2025). *Testing Market Efficiency in Indian Index Options Using the Black-Scholes Model: Empirical Analysis and Dynamic Hedging Approach*. SSRN 5289505.
- NSE historical circulars: FAOP47854, FAOP64625, FAOP70616.
