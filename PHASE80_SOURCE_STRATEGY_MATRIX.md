# Phase 80 — Source and strategy matrix
Audit date: 2026-10-10

## Strategy axis coverage

| Axis | Existing evidence in project | Under-coverage | Next action |
|---|---|---|---|
| Structure family | Phase 43/45 tested broad fixed structures; Phase 50B tracks named Tradetron and external strategy lineages | No claim of all structures; different underlying/expiry/time can change economics | Freeze six representative families for Phase 81 |
| VIX regime | Phase 40–50/50B feature/strategy-regime matrices; Holm gate failed promotion | Several regime cells sparse; phase 49 had zero Holm survivors | Reuse lagged VIX as secondary descriptive stratifier only |
| Strike/width | A broad set of geometries and ratio variants have already been tested | Existing 4-DTE expiry-focused protocol is not identical to session-based testing | Use fixed ATM/±100/±300 offsets; only registered iron-fly wings vary 100/200/300 |
| Entry/exit timing | Existing principal strategy tests generally enter four sessions before expiry and exit expiry day | Paired same-day versus overnight holding window not systematically compared across the same fixed template basket | Phase 81 |
| Costs/fills | Current frozen model contains date-aware fees, ₹10/order and one ₹0.05 adverse tick per leg assumptions | OHLC open is not a bid/ask quote; depth absent | Add conservative stress and explicit caveat; do not claim fillability |
| Directional covariates | Premium direction, OI filters, feature/symbolic/ensemble selectors exist | Point-in-time global crossings/futures/synthetic futures/Greeks data may not all be aligned for this specific short window | Do not indiscriminately combine unavailable features; record future data gate |
| Holding risk | Stops, MFE, target exits, expiry fallback have been explored | Static overnight exposure is a distinct question; not equivalent to delta-hedged option returns | Test as paired horizon only |
| Statistical multiplicity | Phase49/50B use Holm; Phase77 bootstrap; Phase78 temporal stability | Number of historical search variants is large and must be disclosed | Record phase81 declared tests; Phase82 Holm/cluster inference; manuscript notes historic search degrees of freedom |

## Sources

| Source | Technical coverage | Rights/status | Decision |
|---|---|---|---|
| Bhat et al. (2024), Journal of Futures Markets, DOI 10.1002/fut.22512 | Delta-hedged overnight vs intraday short option returns | Peer-reviewed article; dataset link available | Research motivator, not direct strategy proof |
| Zenodo 10899828 | 1-minute spot/futures/options 2017–2020 | Record has no clear license visible in metadata | Do not download/cache into repo until rights clarified |
| artist-23/nifty-options-data | OHLC, IV, OI, volume, spot; 2020–2025 | No clear dataset license in card; exact expiry identity not established from preview | Do not cache or use as primary execution sample until validated |
| rissin/nse-options-intraday | OHLC, explicit expiry/strike/side; Upstox 1m 2024–2026 and NSE EOD 2001 onward | license other; source card says honor Upstox terms; intraday OI absent | Metadata lead only; needs rights confirmation |
| thetrademarkk/india-index-options-1m | Existing primary 1-minute chain OHLCV(+OI), 2021-2026 | CC-BY-NC-4.0 | Existing research source within lawful terms; cannot establish spreads/depth |
| QuantDev-stack/OptionVault | Repo sample includes options, Greeks, futures and market-depth/tick files | Full coverage requires separate license per README; sample sizes small | Tool/schema inspiration, not complete free data |
| sahilempire/nifty-options-research-lab | Public strategy catalog, costs, slippage, research methodologies; no included market data | MIT repo; third-party empirical claims not independently verified | Use ideas/checklists, not results as proof |

## Selected new axis
**Same structure, two holding windows, matched date:** 09:20–15:20 intraday and 15:20–next valid session 09:20 overnight, using exact same contract IDs and fixed strikes. That separates structure effect from exposure-clock effect far better than testing unrelated strategies on different dates.
