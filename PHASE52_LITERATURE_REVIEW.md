# Phase 52 Literature Review and Source Ledger — Seed Version

**Status:** Initial source seed; review is intentionally open for scheduled expansion.  
**Evidence principle:** Literature supports plausible mechanisms, not profitable NIFTY strategies. A GitHub/YouTube claim is a candidate hypothesis until independently reconstructed and backtested.

## 1. Research synthesis

### Volatility index and regime

NSE describes India VIX as derived from the NIFTY options order book and as an indicator of expected near-term volatility over approximately 30 calendar days. VIX is therefore an available regime variable, but it must be computed and aligned point-in-time. Level alone cannot distinguish a continuing volatility expansion from a post-spike reversal; the research will separate level, change, rate of change, percentile, realised-volatility spread, skew and (where data support it) term-structure state.

- NSE, Volatility Index / India VIX computation methodology: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/white_paper_IndiaVIX.pdf
- NSE historical VIX page: https://www.nseindia.com/reports-indices-historical-vix

### Option volume, demand and implied-volatility surface

Bollen and Whaley (2004), Does Net Buying Pressure Affect the Shape of Implied Volatility Functions?, Journal of Finance 59(2), 711–753, DOI 10.1111/j.1540-6261.2004.00647.x. Their paper reports a relationship between demand pressure and the implied-volatility function, motivating IV/skew/flow features and a direct feature-ablation test. The study is not direct evidence that a particular NIFTY strategy earns net returns.
https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2004.00647.x

Pan and Poteshman (2006), The Information in Option Volume for Future Stock Prices, Review of Financial Studies 19(3), 871–908, DOI 10.1093/rfs/hhj024. Their results motivate testing option volume/PCR-like signals with strict timestamp and flow-definition controls. The paper’s dataset and market are not interchangeable with public NIFTY OI snapshots, and OI/PCR must not be labelled informed order flow without buyer-initiated/opening-trade data.
https://doi.org/10.1093/rfs/hhj024

Gârleanu, Pedersen and Poteshman (2009), Demand-Based Option Pricing, Review of Financial Studies 22(10), 4259–4299, DOI 10.1093/rfs/hhp005. The authors model how option demand pressure may affect option prices and skew. This motivates testing supply/demand-related IV/OI features and relative option pricing, not accepting a trading claim without fees, fill and out-of-sample validation.
https://academic.oup.com/rfs/article-abstract/22/10/4259/1590158

## 2. Official exchange / market data sources

- NSE equity derivatives contract information and permitted lot sizes: https://www.nseindia.com/static/products-services/equity-derivatives-contract-information
- NSE historical F&O/order/trade data subscription and samples: https://betanseapi.nseindia.com/static/market-data/eod-historical-data-subscription
- NSE contracts available for trading: https://www.nseindia.com/static/market-data/securities-information-contracts-available-for-trading
- BSE derivatives and market-data documentation: use official BSE endpoints where relevant and record URL, date, schema, fees/licence and coverage before analysis.
- NIFTY historical options source used by Phase 51-3: Hugging Face rissin/nse-options-intraday, object upstox_intraday/NIFTY/NIFTY_2026.parquet; SHA-256 and byte size are recorded in the Phase-51-3 status/report. Its validated observations cover only through 2026-07-21, not the full original Phase-51 interval.
- Hugging Face thetrademarkk/india-index-options-1m: previous Phase-51 audits rejected objects labelled for 2026-07-28/2026-08-04 because the byte contents ended on 2026-07-02 and had no target-session records. Names/metadata alone are insufficient evidence.
- HF_TOKEN may be used by Actions to list/download eligible files, but token values must never be printed or committed. Raw files are cached by immutable hashes and not committed to Git.

## 3. Public code and strategy-discovery leads

1. Sudheer Bez, nifty-options-algorithmic-backtester: https://github.com/sudheerbez/nifty-options-algorithmic-backtester — public strategy claims around VIX-adjusted iron-condor widths. Claims require reproduction; not accepted results.
2. ManthanN75, NIFTY-OPTIONS-ALGO-PROJECT: https://github.com/ManthanN75/NIFTY-OPTIONS-ALGO-PROJECT — Python/Rust backtesting example and lessons about small samples and backtest bugs.
3. Jay2597, nifty-condor-paper: https://github.com/Jay2597/nifty-condor-paper — VIX-gated monthly iron-condor/strangle paper-trading hypothesis; margin, lot size and slippage claims are to be re-audited from its underlying code and source data.
4. shivam61, nifty-options-backtester: https://github.com/shivam61/nifty-options-backtester — configurable strategy-grid and walk-forward patterns; reported results are not imported as evidence.
5. codewithpom, nifty-straddle-vix-router: https://github.com/codewithpom/nifty-straddle-vix-router — VIX regime, time and stop-grid analysis and useful warnings about naive in-sample optimisation. Treat as a code/research lead only.

## 4. User-owned strategy source lineages

The connected repository inventory shows 40 user repositories. Priority strategy lineages include:
- Final-stand-v1: frozen 504-configuration family and prospective validation rules;
- Final-stand-v2 / Final-stand-v3 / Final-Stand-v4 / this repository: historical weekly/expiry option strategies and selector research;
- Daily-Options: YouTube-derived strategy program and extensive IV/OI/Greek, feature-ablation and cost research;
- Iron_condor: prospective paper-trading pipeline for the NIFTY weekly iron condor with a futures-based underlying reference;
- Iron-condor-to-ratio-v1 / v2: source-based iron-condor-to-ratio transition hypothesis;
- Option-intraday-v1: current-week call plus next-week put asymmetric premium strategy;
- Naked-option-v1: long-only option direction and regime/model research;
- Nifty: Monte Carlo, Batman/adaptive entry and expiry-exit studies;
- Timesfm-trading, Universal-ML-Trade, GBDT-trade-signal, ML-trade, research-ML-trading, market-inefficiency, btst-strategy-lab, Surge-identifier, CPR- and MC-OPTIONS-* : secondary signal, feature, regime and market-inefficiency ideas where options-specific source code applies.

A repository's README or advertised metric is not itself a backtest record. Every candidate needs a frozen rule spec, exact code/source commit, source data and independent replay. Repositories whose root README wasn't accessible through the connected file API remain unaudited until an alternate source path is read.

## 5. Video and platform discovery

- User-designated Profit Breakout YouTube channel: https://www.youtube.com/@profitbreakout. Prior Phase 46 logged nine indexed videos, including India VIX strategy routing, Batman/double-ratio, Iron Fly vs Iron Condor, adaptive structure switching, weekly/monthly hedged spreads and monthly VIX-based strike selection.
- Phase 46 publicly indexed strategy ideas: long straddle/strangle, long/reverse iron structures, put/call ratio backspreads, calendars/diagonals, calendar trap, IV/skew/term-structure routing and defined-risk short-volatility only after a documented spike/fade trigger.
- StockMock and StockMojo are included as candidate-reconstruction and cross-check platforms. Their output must not substitute for raw, synchronized, timestamped contract data unless a reproducible export is available and auditable.

## 6. Key limitations / implications

- Availability and market coverage vary by factor. A factor test is performed only on matched intervals where its input is valid; report retained coverage and whether the matched baseline changes.
- OI records do not automatically identify who opened or closed a position. Any long/short buildup classification is a price/OI proxy, not trader intent.
- Synthetic futures require matched call/put contracts at the same strike, expiry and time. A late or stale premium must not be combined with a different timestamp's spot/future.
- Greek calculations from LTP-derived implied volatility are noisy when bid/ask or rates/dividend inputs are missing. Keep source quality flags and test Greeks as estimated features only.
- Global-market, DII/FII, news and corporate-action information may be daily or have release timestamps. Apply the information only after it would have become observable and test additional coverage/lagging.
- Global literature results are not automatically portable to Indian index options, and paper claims are not evidence of post-cost robustness.


## 7. Additional indexed-source leads added 2026-10-09

These sources broaden the public review. Each remains a **discovery lead only** until source code/data/methodology are inspected and the strategy is independently reproduced.

### Indian option-market research

- Pathak, Rajesh (2016), *Volatility Informed Trading in the Options Market: Evidence from India*, Business: Theory and Practice 17(1), 13–22. DOI: https://doi.org/10.3846/btp.2016.559. The study examines common implied volatility, option volume and changes in OI using regression/VAR frameworks, also splitting by moneyness and market trend. This supports testing volatility and OI/volume interactions; it does not imply a post-cost NIFTY edge.
- Jithendranathan, Thadavillil (working paper posted 2026-04-29), *Trading Activity, Open Interest, and Volatility: Evidence from the Indian Derivatives Market*: https://papers.ssrn.com/sol3/Delivery.cfm/6675000.pdf?abstractid=6675000&mirid=1. Its stated results associate volatility increases with higher trading activity, particularly puts/index futures, often without corresponding OI increases. This is a recent working paper, not settled consensus; test its claims only with matched timestamped Indian derivatives data.
- Srivastava, Sandeep, *Informational Content of Trading Volume and Open Interest — An Empirical Study of Stock Option Market in India*, NSE Research Initiative Working Paper 29 (2003/2004): https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID606121_code364627.pdf?abstractid=606121. Historically relevant but stock-option sample and period differ from current weekly NIFTY index options.

### YouTube strategy leads

- Profit Breakout, *India VIX & Options Strategies: When to Use Calendar, Iron Fly, Condor, Straddle, Strangle* (2025-09-08): https://www.youtube.com/watch?v=vVkAw2G93as. Directly relevant for VIX/vega structure-routing hypotheses; video claims are not accepted performance evidence.
- Ganesh Sharma, *Secret Option Strategy — VIX + Volume Profile + Option Chain (Nifty Setup)* (2026-04-05): https://www.youtube.com/watch?v=eoMUcUMkciU. Candidate claims combine VIX environment, volume-profile levels and OI/PCR confirmation. Freeze point-in-time volume-profile inputs and prevent contemporaneous/future OI leakage before testing.
- The user-designated Profit Breakout channel remains at https://www.youtube.com/@profitbreakout. Scheduled API-based YouTube discovery requires the optional `YOUTUBE_API_KEY` Actions secret; if absent, workflow logs `NOT_RUN` and uses prior Phase46 video ledger without pretending a fresh crawl occurred.

### Public source-code leads

- Rusty-Thunderbird, *NIFTY50 Options GoldenCross ExtensiveBacktest*: https://github.com/Rusty-Thunderbird/NIFTY50_Options-GoldenCross_ExtensiveBacktest. Its description advertises option-chain/OI/IV/VIX replay, trend/volatility filters, margin awareness and slippage; inspect actual fill assumptions and data provenance before reuse.
- sahilempire, *NIFTY Options Research Lab*: https://github.com/sahilempire/nifty-options-research-lab. The README reports a broad negative strategy sweep and substantial brokerage sensitivity; those claims are not adopted, but its cost-first philosophy and negative controls are useful code-review targets.
- bhawuk-arora, *Backtesting-NSE*: https://github.com/bhawuk-arora/Backtesting-NSE. Description advertises Upstox expired-contract integration, synchronized minute replay and deterministic Parquet reporting. Check license/API eligibility and compare fills/cost conventions.
- Rusty-Thunderbird, *NIFTY50 Options Optimising Strategy*: https://github.com/Rusty-Thunderbird/NIFTY50_Options-Optimising-Strategy. Public-code lead for VIX/trend filters, spot/options synchronization and config parameterization. Claims must be independently reproduced.

## 8. Source-review state

The scheduled `research/phase52/source_discovery.py` stores metadata from Hugging Face and GitHub public search, and uses YouTube Data API search only if `YOUTUBE_API_KEY` is configured. Results carry the evidence grade `DISCOVERY_LEAD_NOT_VALIDATED`; raw third-party performance statements never flow directly into accepted results.
