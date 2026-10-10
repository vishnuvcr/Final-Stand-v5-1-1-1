# Phase 98 Literature and Evidence Review

**Version:** 1.0  
**Reviewed:** 2026-10-10  
**Scope:** Opening-range breakout (ORB), intraday continuation, India VIX as a risk-state measure, transaction costs, inference and backtest overfitting.  
**Relationship to preregistration:** This is contextual literature; it does not alter the frozen Phase 98 hypotheses, dates, strategy rules, cost scenarios or stopping rule. The Phase 98 evaluation is a NIFTY options replay, while much of the cited ORB evidence concerns U.S. futures or other index futures. It must not be treated as a direct estimate of NIFTY-options profitability.

## Executive synthesis

The evidence is mixed rather than uniformly supportive of opening-range breakouts. Older peer-reviewed studies find intraday trend/ORB effects in some futures samples, but the same research reports that apparent full-sample profitability can weaken substantially across subperiods. A newer September 2026 SSRN preprint reports that none of 225 preregistered ORB configurations in nine U.S. futures markets met its prespecified positive criteria after costs. That preprint is not peer-reviewed and concerns different instruments, but it strengthens the case for a fixed, falsifiable test rather than a broad search over many range lengths, exits and filters.

The source for India VIX describes it as an option-order-book-derived estimate of expected volatility over the next 30 calendar days. It is not itself a directional forecast. Phase 98 therefore uses VIX only as a preregistered high-volatility exclusion, lagged to the prior session; it does not claim that high VIX predicts the sign of NIFTY returns.

Multiple-testing and backtest-overfitting research warns that evaluating many candidate strategies and selecting a winner inflates apparent significance. Phase 98 addresses this risk by testing one frozen breakout specification, one frozen prior-only VIX treatment, fixed development/validation dates, two declared primary tests with Holm adjustment and a protected 2026 holdout that remains sealed. This is necessary discipline, not a guarantee against all sources of bias.

The data are minute OHLC(+volume/open-interest where supplied), not a complete historical bid/ask/depth record. Fixed adverse slippage at bar-open prices is a sensitivity model, not a fill reconstruction. A profitable OHLC replay, if observed, would still require independent confirmation using verified contract metadata and more realistic executable-quote data before any paper/live consideration.

## Thematic review

### 1. Opening-range breakout evidence

**Holmberg, Lönnbark and Lundström (2013).** Their peer-reviewed article, “Assessing the profitability of intraday opening range breakout strategies,” proposes a way to examine ORB-like filters and reports evidence of intraday trending in U.S. crude-oil futures. The authors also report that results from the full sample were not robust to time splits and were largely explained by the most recent, more volatile subperiod. This is an important warning: an apparent full-sample effect may be regime- or period-dependent. The asset, market microstructure, holding horizon and price data differ from the NIFTY option vertical tested here, so the paper motivates robustness checks but does not validate this particular strategy.

Source: Holmberg, U., Lönnbark, C., & Lundström, C. (2013). *Assessing the profitability of intraday opening range breakout strategies*. Finance Research Letters, 10(1), 27–33. https://doi.org/10.1016/j.frl.2012.09.001

**Tsai et al. (2019).** “Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets” uses one-minute data for DJIA, S&P 500, NASDAQ, Hang Seng and TAIEX futures over 2003–2013. The published abstract reports statistically significant results in the examined setups and notes that the effective probing time differs by market. The finding supports treating opening-window definition as market-specific; it does not establish that a 15-minute NIFTY range or option debit spread is profitable. The study concerns index futures rather than options and predates newer market structure and fee conditions.

Source: Tsai, Y.-C., Wu, M.-E., Syu, J.-H., Lei, C.-L., Wu, C.-S., Ho, J.-M., & Wang, C.-J. (2019). *Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets*. IEEE Access, 7, 32061–32071. https://doi.org/10.1109/ACCESS.2019.2899177

**Fetna (2026 preprint).** “Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data” is a recent SSRN preprint (posted September 2026) that tests a large prespecified grid across nine U.S. futures markets. Its abstract reports that zero of its 225 cells met its positive decision rule and that aggregate confirmation-window gross profits became losses under its $25 round-trip-cost scenario. It argues that very small gross edges can be consumed by trading friction. This work is not peer-reviewed as of this review date and studies U.S. futures, so its numbers should not be imported into the NIFTY options analysis; its design and cost-aware falsification emphasis are relevant methodological context.

Source: Fetna, M. (2026). *Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data*. SSRN preprint, posted 14 September 2026. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428398

**Synthesis.** ORB evidence depends on market, sampling period, session alignment, exit conventions and costs. The available literature does not justify assuming that the ORB effect transfers to NIFTY options. Phase 98 therefore tests a single predeclared instrument expression and does not tune opening lengths or thresholds after observing validation outcomes.

### 2. India VIX: what it measures and what it does not

The National Stock Exchange describes India VIX as a near-term expected-volatility measure derived from best bid/ask prices in NIFTY options and calibrated to indicate expected volatility over the next 30 calendar days. A high value signals greater expected magnitude of market fluctuation, not a reliable up/down direction.

Official source: NSE India, *India VIX Index*. https://www.nseindia.com/static/products-services/indices-indiavix-index  
Methodology background: NSE, *India VIX white paper*. https://nsearchives.nseindia.com/s3fs-public/inline-files/white_paper_IndiaVIX.pdf

Phase 98's filter is deliberately narrow: compare the prior trading session's VIX close with a 75th percentile calculated from the preceding 252 available closes. It uses the prior close only and fails closed when sufficient VIX history is unavailable. This tests a specified risk-state exclusion, not whether VIX is generally predictive, and not a family of quantile or window choices.

### 3. Multiple testing and backtest overfitting

**Harvey, Liu and Zhu (2016).** Their Review of Financial Studies paper addresses the proliferation of claimed factors and argues that ordinary significance thresholds are too permissive after many tests; their framework proposes materially higher hurdles for newly mined findings. While focused on the cross-section of returns rather than ORB specifically, the lesson applies to iterative strategy research: the number of tried configurations is part of the evidence, and a nominal p-value from a selected winner can be misleading.

Source: Harvey, C. R., Liu, Y., & Zhu, H. (2016). *… and the Cross-Section of Expected Returns*. Review of Financial Studies, 29(1), 5–68. https://doi.org/10.1093/rfs/hhv059  
Public working paper: https://www.nber.org/papers/w20592

**Bailey et al. (2017).** “The Probability of Backtest Overfitting” proposes combinatorially symmetric cross-validation to estimate the risk that a selected backtest winner is overfit. The paper emphasizes that a single holdout can be unreliable when many alternatives have been compared and selected. Phase 98 does not implement the full PBO framework because it is not evaluating a large candidate matrix in this phase; instead, it reduces researcher degrees of freedom by freezing one rule and using a separate time validation sample. This is a mitigation, not proof that PBO is zero.

Source: Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2017). *The Probability of Backtest Overfitting*. Journal of Computational Finance. https://doi.org/10.21314/JCF.2016.322  
Open repository copy: https://escholarship.org/uc/item/4w1110bb

### 4. Transaction costs, quote quality and executable fills

For an option vertical, gross spread P&L can be small relative to the friction on four leg-side fills (long and short at entry and exit), particularly with option bid–ask spread, market impact and fast price movement. Brokerage and statutory levies are only part of execution friction; an OHLC dataset cannot reconstruct the exact spread, queue position, available depth, latency or whether both legs could execute at the modeled prices.

Phase 98 therefore uses one and two adverse ticks on each leg-side fill, explicit brokerage assumptions, date-aware charges and a severe statutory-fee multiplier. These costs are a transparent stress test, not a claim that they encompass every execution cost. For exact practical inference, the account's applicable broker tariff and complete historical bid/ask or trade/quote data are necessary. The account category is not specified here, so the registered ₹10/order base case must be interpreted as the frozen legacy-tariff assumption; the ₹20/order stress case is not guaranteed to represent the maximum possible friction.

Paytm Money's published notice describes brokerage changes for new users from 25 August 2023 and continuation of the old rate for existing-user cohorts. That means one flat account-agnostic fee cannot be asserted as the actual rate for every account. This does not change the preregistered computation; the limitation is carried into interpretation.

Source: Paytm Money, *Brokerage charges increase from 25th Aug ’23; existing users will continue on old brokerage charges*. https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/

#### 6. Practitioner video and independent online backtest material (low evidential weight)

The targeted search also found practitioner explainers and self-published NIFTY/Bank NIFTY analyses. These are useful for documenting what retail traders mean by a “15-minute ORB” and for discovering alternate hypotheses, but they are not peer-reviewed evidence. Their strategy definitions, fee assumptions, dataset quality, survivorship/selection risks, source data, and complete trade ledgers are not uniformly independently reproducible. They should not be assigned the same weight as a peer-reviewed paper or an audited replay.

- **Stock Menthol (YouTube, 13 September 2026):** a video description titled around the 15-minute opening-range breakout discusses marking the first 15-minute range and adds a Fair Value Gap filter. The listing references a funded-trader service and a backtesting feature; the search listing alone does not establish independent net profitability. It is a description of a popular retail rule, not validation. https://www.youtube.com/watch?v=_PQHVKKGeB4
- **Trader Swami (YouTube, 8 February 2023):** a “15 minute ORB” tutorial describes an intraday breakout and scanner for Bank Nifty, Nifty and stocks. Its description is educational and makes broad promotional claims; no verified source-faithful option-level results are established by the listing. https://www.youtube.com/watch?v=cLLEKlvplVQ
- **Finance With Sai (19 March 2025):** a self-published Bank Nifty ORB backtest page explicitly says it compares results before and after slippage/charges. It is closer to the execution-cost question than a pure chart tutorial, but trades the index/spot signal and discusses implementation in F&O; its assumptions and sample still differ from this Phase 98 long/short option vertical. https://financewithsai.com/orb-backtest-on-banknifty/
- **Intraday Lab (1 April 2026):** a self-published article reports an analysis of NIFTY's first 15-minute candle over 2017–2026. It states that popular breakout interpretations can fail, but the article is not peer reviewed and Phase 98 does not import its reported figures as ground truth. https://intradaylab.com/blog/nifty-first-15-minute-candle-analysis
- **Intraday Lab (7 May 2026):** a separate practitioner article says it compared NIFTY breakout rules on about 12 months of data, including false-breakout observations. Because the search result does not provide a reproducible full data/ledger package, use it only as practitioner context. https://intradaylab.com/blog/breakout-trading-nifty-what-actually-works

Across practitioner sources, the repeated warning is that an appealing chart rule is not equivalent to a tested, post-cost option strategy. Their claims are not aggregated or meta-analyzed here because the designs and evidence quality are not sufficiently comparable.

### 7. Indian-market microstructure, option efficiency and intraday volatility evidence

**Aggarwal and Gupta (2009).** Using daily NIFTY 50 index-option closing data from January 2006 to March 2009, this paper examines call/put spreads, box spreads and butterfly convexity relationships while incorporating bid–ask, brokerage and taxes. It reports frequent and large box-spread relationship violations, but fewer violations in call/put spreads and convexity, and emphasizes that market frictions materially affected arbitrageurs' ability to capture violations. This is Indian options-market evidence, but it studies no-arbitrage relationships using older daily closes—not an intraday directional ORB strategy or modern weekly expiry verticals.

Source: Aggarwal, N., & Gupta, M. (2009). *Empirical Evidence on the Efficiency of Index Options Market in India*. Asia-Pacific Journal of Management Research and Innovation, 5(3). https://doi.org/10.1177/097324700900500311

**Vipul (2009).** “Box-spread arbitrage efficiency of Nifty index options: The Indian evidence” uses time-stamped transactions to identify box-spread mispricing. Its abstract reports that cost-adjusted opportunities could occur frequently but generally did not persist even for two minutes; liquidity/immediacy risk and volatility were related to observed mispricing. This supports strict timestamp-matched trading and skepticism about acting on stale or asynchronous option quotes. It does not directly validate the ORB signal.

Source: Vipul (2009). *Box-spread arbitrage efficiency of Nifty index options: The Indian evidence*. Journal of Futures Markets, 29(6), 544–562. https://doi.org/10.1002/fut.20376

**Patnaik and Thomas (2004).** “Profitability of Trading Strategies on High-Frequency Data, with Trading Costs” tests Indian equity-market momentum and contrarian rules on high-frequency order-book data for 1996–2002, with explicit execution/price-impact costs. The abstract reports short-run momentum profitability in some strategies but declining profits as the formation period lengthened, after controlling for microstructure effects. This is an older single-stock equity sample, not current NIFTY options, but it illustrates why signal horizon and executable prices matter.

Source: Patnaik, T. C., & Thomas, S. (2004). *Profitability of Trading Strategies on High-Frequency Data, with Trading Costs*. SSRN working paper. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=568363

**Chakrabarti and Kumar (2020).** This peer-reviewed study investigates the high-frequency (five-minute) relationship between NIFTY returns and model-free implied volatility. It reports a negative and asymmetric short-term relationship, with negative return innovations particularly associated with sharp rises in India VIX; its authors caution that simple VAR behavior does not fully explain extreme joint movements. The paper supports treating volatility and market direction as distinct quantities; it does not establish that a prior-day VIX percentile identifies profitable ORB sessions.

Source: Chakrabarti, P., & Kumar, K. K. (2020). *High-Frequency Return-Implied Volatility Relationship: Empirical Evidence from Nifty and India VIX*. Journal of the Developing Areas, 54(3), 53–68. https://ideas.repec.org/a/jda/journl/vol.54year2020issue3pp53-68.html

## 5. Research design consequences

These sources support the following fixed safeguards, all consistent with the Phase 98 preregistration:

1. **Avoid validation tuning.** Strategy parameters, split dates, target/stop rules and VIX threshold remain frozen.
2. **Keep the time boundary intact.** Development covers 2021–2023; validation covers 2024–2025; protected 2026 data are not opened.
3. **Use exact observed bars.** No interpolation, forward-filling, signal-close fill or inferred missing exit price.
4. **Separate code success from evidence acceptance.** A workflow can pass while source coverage is invalid; only data, coverage, source-manifest and audit gates allow a performance report to be accepted.
5. **Treat missing signal-session returns as unknown, not zero.** No-breakout sessions are zero-return sessions; sessions with a signal but unavailable data are unknown and block confirmatory inference.
6. **Apply declared cost and statistical rules.** Use the fixed base and stress cost models, adequate trade gates, moving-block confidence intervals, one-sided sign-flip tests and Holm correction for the two primary tests.
7. **Do not promote from this phase.** A positive historical replay remains a research lead because OHLC fills cannot establish executable live fills.

## Applicability map

| Evidence source | Evidence type | Relevant implication | Key transfer limitation |
|---|---|---|---|
| Holmberg et al. (2013) | Peer-reviewed ORB/futures | Subperiod instability can overturn a full-sample result | U.S. crude futures; not NIFTY options |
| Tsai et al. (2019) | Peer-reviewed intraday index-futures study | Opening/probing windows may vary by market | Futures, 2003–2013 sample; no direct option-vertical result |
| Fetna (2026) | SSRN preprint, not peer-reviewed | Costs and preregistration can reverse apparent ORB profitability | U.S. futures and its fee assumptions |
| NSE India VIX page/white paper | Official methodology | VIX is expected volatility, not direction | Does not validate this particular 75th-percentile filter |
| Harvey et al. (2016) | Peer-reviewed multiple-testing methodology | Ordinary p-values are weak after broad searches | Broad asset-pricing factor context, not a direct ORB test |
| Bailey et al. (2017) | Backtest-overfitting methodology | Selection across many variants inflates winner's apparent reliability | Phase 98 fixes one variant and does not estimate full PBO |
| Aggarwal & Gupta (2009) | Indian NIFTY index-option efficiency | Costs affect ability to exploit option pricing relationships | Daily data from 2006–2009; not directional ORB |
| Vipul (2009) | Indian NIFTY option box-spread microstructure | Timestamp precision and short-lived mispricing matter | Arbitrage relation, not ORB strategy |
| Chakrabarti & Kumar (2020) | NIFTY/India VIX five-minute evidence | Return–volatility relation is asymmetric; VIX is not a simple direction forecast | Does not test this specific filter |
| Patnaik & Thomas (2004) | Indian equity intraday strategies with order-book costs | Execution and price impact affect high-frequency strategy returns | Older single-stock sample, not options |
| Paytm Money tariff notice | Official broker communication | Brokerage can vary by account cohort | Account cohort/tariff not individually verified |

## Review limits and outstanding research gaps

- The cited ORB papers are not direct NIFTY option-vertical replications. Indian instrument-level evidence with transparent option fills and costs remains the key gap this experiment addresses.
- The recent 2026 cost-aware futures result is a preprint, not peer-reviewed; it is included as timely methodological context, not settled consensus.
- This is a targeted, source-quality-stratified review rather than an exhaustive systematic review of every database and video. Searches covered indexed academic/official sources and targeted YouTube/practitioner searches; inaccessible or non-reproducible source claims were not treated as evidence. Additional systematic screening and deduplication would be required before describing it as exhaustive.
- The current dataset does not supply a full historical NBBO/depth tape; exact executable P&L remains unverified.
- Broker charges need to be reconciled with the user's actual account tariff before interpreting net returns as personally realizable.

## References

1. Aggarwal, N., & Gupta, M. (2009). Empirical Evidence on the Efficiency of Index Options Market in India. *Asia-Pacific Journal of Management Research and Innovation, 5*(3). https://doi.org/10.1177/097324700900500311
2. Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2017). The Probability of Backtest Overfitting. *Journal of Computational Finance*. https://doi.org/10.21314/JCF.2016.322
3. Chakrabarti, P., & Kumar, K. K. (2020). High-Frequency Return-Implied Volatility Relationship: Empirical Evidence from Nifty and India VIX. *The Journal of Developing Areas, 54*(3), 53–68. https://ideas.repec.org/a/jda/journl/vol.54year2020issue3pp53-68.html
4. Fetna, M. (2026). Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data. SSRN preprint, posted 14 September 2026. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428398
5. Harvey, C. R., Liu, Y., & Zhu, H. (2016). … and the Cross-Section of Expected Returns. *Review of Financial Studies, 29*(1), 5–68. https://doi.org/10.1093/rfs/hhv059
6. Holmberg, U., Lönnbark, C., & Lundström, C. (2013). Assessing the profitability of intraday opening range breakout strategies. *Finance Research Letters, 10*(1), 27–33. https://doi.org/10.1016/j.frl.2012.09.001
7. National Stock Exchange of India. India VIX Index and white paper. https://www.nseindia.com/static/products-services/indices-indiavix-index
8. Paytm Money. Brokerage rate change notice effective 25 August 2023. https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/
9. Patnaik, T. C., & Thomas, S. (2004). Profitability of Trading Strategies on High-Frequency Data, with Trading Costs. SSRN working paper. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=568363
10. Tsai, Y.-C., Wu, M.-E., Syu, J.-H., Lei, C.-L., Wu, C.-S., Ho, J.-M., & Wang, C.-J. (2019). Assessing the Profitability of Timely Opening Range Breakout on Index Futures Markets. *IEEE Access, 7*, 32061–32071. https://doi.org/10.1109/ACCESS.2019.2899177
11. Vipul (2009). Box-spread arbitrage efficiency of Nifty index options: The Indian evidence. *Journal of Futures Markets, 29*(6), 544–562. https://doi.org/10.1002/fut.20376

**Access date for web sources:** 2026-10-10.
