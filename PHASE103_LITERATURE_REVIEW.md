# Phase 103 Literature Review — Novel Intraday NIFTY Options Rules

**Review date:** 2026-10-11  
**Role:** context and limitations only; this review was completed after the Phase 103 rules were frozen and did not change any parameters.  
**Novelty boundary:** the combinations were designed for this repository; we do not claim that opening-range, failed-breakout, or iron-condor primitives are unprecedented worldwide.

## Research question

What do existing empirical studies suggest about the reliability of opening-range continuation, failed-breakout reversal, and short-volatility/iron-condor ideas after trading costs?

## Findings

| Source | Source-reported evidence | Implication and limitation |
|---|---|---|
| Tsai et al. (2019), IEEE Access, “Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets” | Uses one-minute futures data for DJIA, S&P 500, NASDAQ, HSI and TAIEX from 2003–2013 and reports positive results in that sample. [DOI](https://doi.org/10.1109/ACCESS.2019.2899177) | Supports testing opening-range hypotheses; older, non-Indian futures evidence does not validate NIFTY listed-options fills. |
| Fetna (2026), SSRN preprint, “Opening-Range Breakout Does Not Survive Trading Costs” | Describes a preregistered 225-cell grid across nine U.S. futures markets and reports that none met the combined cost/stability hurdle. [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428398) | Strong caution against choosing a gross winner; it is a preprint and not an India-specific replication. |
| Perz, “Profitability of Selected 0DTE Index Options Strategies” | Reports two SPX 0DTE iron-condor variants profitable over an approximately 12-month sample. [DOI](https://doi.org/10.5171/2024.4452224) | Contrasts with the NIFTY results and motivates continued study, but market, sample and execution assumptions differ. |
| Pillai (2026), SSRN preprint, “Trading the Volatility Risk Premium on Nifty 50: Strategy Backtest with Realistic Frictions” | Tests four short-volatility strategies over 119 monthly expiry cycles (2015–April 2025) and reports negative net annualized returns after costs, with tail risk cited as a major driver. [SSRN PDF](https://papers.ssrn.com/sol3/Delivery.cfm/6876580.pdf?abstractid=6876580&mirid=1&type=2) | Relevant caution for a VIX-filtered iron condor: low VIX and compressed range do not eliminate gap/tail risk. The preprint is not independently reproduced here. |
| Indian index-option efficiency and box-spread studies | Publisher records report that transaction costs reduce the share of apparent option mispricings that can be exploited. [SAGE](https://doi.org/10.1177/0971890714558709) · [Wiley](https://doi.org/10.1002/fut.20376) | Supports strict post-cost evidence requirements; these papers do not test the three rules here. |
| Paytm Money F&O FAQ and NSE STT schedule | Paytm's public F&O FAQ states ₹10 per executed unique order; its published blog documents account-cohort differences. NSE states option-sale premium STT at 0.10% through 31 March 2026 and 0.15% starting 1 April 2026. [Paytm FAQ](https://www.paytmmoney.com/stocks/customer/fno-faq/trading/order-placement/what-is-overnight-order-type) · [pricing note](https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/) · [NSE STT](https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax) | The replay uses ₹10/order baseline, ₹20/order stress and date-effective levy assumptions; the user's plan and historical contract notes were not verified. |

## Synthesis and design controls

1. Range breakout signals must follow completion of the opening range, and fills use later observed option bars rather than same-bar assumptions.
2. A failed breakout requires a subsequent closing-price reclaim; no sequencing is inferred from candle high/low alone.
3. A low-VIX / compressed-range filter does not rule out tail gaps in a short-volatility structure.
4. All candidates are evaluated net of per-leg brokerage, statutory/exchange charges, GST, adverse ticks and impact stress.
5. Literature claims are context only. They do not substitute for the NIFTY options replay and no strategy is promoted.

## What this review does not establish

- It does not verify actual bid/ask/depth, queue position, latency, actual Paytm Money fills or the user's contract notes.
- It does not establish that any Phase 103 rule combination is unprecedented in the worldwide literature.
- It does not justify changing thresholds after inspecting the validation results.
