# Phase 46 YouTube / Video Source Ledger

**Discovery date:** 2026-10-07  
**Purpose:** strategy-hypothesis discovery for VIX-conditioned NIFTY research.  
**Evidence status:** discovery only; no video claim is treated as validated trading evidence.

| ID | Source | Main idea extracted | Candidate implication | Scope |
|---|---|---|---|---|
| YT-001 | Trading with Groww — “What Is the Best Options Strategy for High VIX Markets?” | Compares Long Straddle vs Short Straddle across low/medium/high India-VIX regimes using 5+ years of backtest framing | Directly test Long Straddle/Short Straddle by VIX regime; short straddle requires defined-risk variant for promotion | India VIX / NIFTY |
| YT-002 | IBBM Academy — “High VIX Option Strategy | Best Volatility Trading Strategy | Calendar Trap Options Strategy” | Presents a Calendar Trap as a high-VIX setup based on option-premium/volatility behavior | Test Calendar Trap / calendar-differential structures in HIGH/RISING/SPIKE VIX | India VIX / NIFTY |
| YT-003 | Neu Markets — “High VIX strategy | fully hedged iron condor...” | Uses a fully hedged Iron Condor in volatile markets, with price-action/context overlays | Test hedged Iron Condor specifically after high-VIX spikes or with falling-after-spike confirmation | NIFTY / BankNIFTY |
| YT-004 | AlphaHedge — “IV Is Very High - Learn This Options Strategy Before IV Crash” | High IV can fall sharply after a small recovery; discusses limited-risk negative-vega structures | Test defined-risk negative-vega structures conditional on HIGH VIX + VIX reversal | Generic options / transferable |
| YT-005 | Strategy Desk — “Put Ratio Backspread for NIFTY | Complete Strategy + Adjustment Guide” | Put ratio backspread for sharp downside moves with NIFTY examples | High-priority convex downside candidate for RISING/HIGH VIX | NIFTY |
| YT-006 | Volatility Trading Strategies — “3 Options Trades for the coming VIX Spike!” | Explicit VIX-spike trade framework; includes a live calendar option trade and discussion of fading VIX spikes | Candidate family: calendar + long-volatility responses to VIX spikes; test fade-vs-follow timing | Global volatility / transferable |
| YT-007 | CA Rachana Ranade — “India VIX above 25! | What does it mean...” | India-VIX elevated regime, VIX/NIFTY relationship, mean reversion and volatility-based options strategies | Use high-VIX/mean-reversion state as a router variable; do not copy discretionary trade calls | India VIX |
| YT-008 | Quantsapp — “Volatility Skew Simplified” | NIFTY volatility skew shape and shifts may encode directional expectations | Test skew slope/shift as secondary router for asymmetric spreads/backspreads | NIFTY |
| YT-009 | Kotak Stockshaala — “Understanding Volatility, VIX, IV & Vega...” | VIX, IV, put/call IV differences, vega and IV crush | Supports explicit IV/VIX divergence and vega exposure as candidate features | India options |
| YT-010 | projectoption — “VIX Term Structure Explained” | Contango/backwardation in VIX futures can distinguish bullish/bearish volatility environments | Search for an India-compatible term-structure proxy before numerical testing | Global volatility |

## Additional searchable video lead

A public YouTube-derived source linked from Cashparency describes an India-VIX short-strangle strategy. Because short strangles are undefined-risk and already belong to the project's diagnostic-only universe, this is logged as a source lead but **not** as a priority promotion candidate.

## Preliminary ranking for numerical follow-up

1. **Put Ratio Backspread / Put Backspread + RISING/HIGH VIX** — strongest direct fit to the empty bearish high-volatility regime.
2. **Calendar Trap / Calendar Spread + HIGH/RISING VIX** — distinct family not represented as a high-VIX trigger in the previous sweep.
3. **Long Straddle / Long Strangle + HIGH/RISING/SPIKE VIX** — direct regime comparison hypothesis.
4. **Reverse Iron Condor / Long Iron Butterfly + VIX expansion** — defined-risk long-volatility convexity.
5. **High-VIX + VIX-reversal → hedged Iron Condor/Iron Butterfly** — explicitly tests whether the profitable side is the *post-spike fade*, not the spike itself.
6. **Skew-shift router** for choosing put backspread vs call backspread vs asymmetric butterfly.
7. **IV/VIX divergence router** where the option surface disagrees with the headline India VIX.
8. **Term-structure proxy router** if a point-in-time India equivalent can be constructed without look-ahead.

## Important methodological warning

YouTube descriptions are strategy-discovery sources, not peer-reviewed evidence. No claimed win rate, “best strategy” label, or anecdotal success is accepted without the project's independent development/validation/holdout process.


## Direct video links

- YT-001: https://www.youtube.com/watch?v=tUXls22PGBk
- YT-002: https://www.youtube.com/watch?v=b4FGNAIPCS8
- YT-003: https://www.youtube.com/watch?v=AUDWzocTGvY
- YT-004: https://www.youtube.com/watch?v=492ZfUBRNw0
- YT-005: https://www.youtube.com/watch?v=85d7J4URbMA
- YT-006: https://www.youtube.com/watch?v=cPzFxHZHaNM
- YT-007: https://www.youtube.com/watch?v=DHuaakCWfpM
- YT-008: https://www.youtube.com/watch?v=CAQRNWR2JCY
- YT-009: https://www.youtube.com/watch?v=P3EbwULnRXg
- YT-010: https://www.youtube.com/watch?v=U2DLXKIFNaY

## Search limitation

The web search layer exposes indexed YouTube results rather than an authoritative complete YouTube corpus. Therefore “all available” cannot be guaranteed literally. The scan is reproducible at the keyword-family level and records the relevant indexed sources found in this run. Future discovery runs should add new query families rather than assume this ledger is exhaustive.


## User-designated channel: Profit Breakout

The channel `@profitbreakout` is now a dedicated source stream for this project. The indexed search located the following directly relevant videos:

| PB-ID | Video | Research use |
|---|---|---|
| PB-001 | India VIX & Options Strategies: When to Use Calendar, Iron Fly, Condor, Straddle, Strangle | Explicit low/high VIX comparison; maps VIX states to calendar, iron fly, iron condor, straddle and strangle families |
| PB-002 | Batman Strategy in Options Trading — Double Ratio Spread with Smart Adjustments | Batman/double-ratio structure plus an explicit VIX-based entry filter |
| PB-003 | IRON FLY vs IRON CONDOR — Same Margin, Different Mindset | High-vs-low volatility comparison and regime-dependent structure choice |
| PB-004 | Iron Fly to Iron Condor: When and Why This Shift Works Better | Adaptive transition from iron fly to iron condor using premium imbalance, market structure and changing volatility |
| PB-005 | This Credit Spread Strategy Adapts to Every Market Move | Weekly call credit spread + monthly put credit spread, with explicit adjustment logic and market-condition discussion |
| PB-006 | Covered Call 2.0: Double Premium Strategy with Adjustments | Current-week + next-week call selling, protective put and delta rebalancing; useful as a longer-horizon low/normal-vol candidate |
| PB-007 | This 1-Year NIFTY Strategy Generates Regular Options Income | Long-duration NIFTY structure combined with weekly/monthly call selling and defined-risk management |
| PB-008 | Monthly Option Strategy for Working People — How VIX Changes the Trade | Explicit India-VIX adaptation, strike selection by VIX and changes for low vs high VIX |
| PB-009 | Weekly Option Strategy Done The Right Way — Discipline Over Prediction | Hedged weekly structure and risk-control framework; candidate for cross-regime baseline testing |

### Direct links

- PB-001: https://www.youtube.com/watch?v=vVkAw2G93as
- PB-002: https://www.youtube.com/watch?v=Lt3FX1ce-FA
- PB-003: https://www.youtube.com/watch?v=TE4p9tOz6XE
- PB-004: https://www.youtube.com/watch?v=gfot9-Iumn8
- PB-005: https://www.youtube.com/watch?v=XEMWdenneZ4
- PB-006: https://www.youtube.com/watch?v=DiCY_w93O3M
- PB-007: https://www.youtube.com/watch?v=s_3Z8YKHGc4
- PB-008: https://www.youtube.com/watch?v=n3FK3eaUqpU
- PB-009: https://www.youtube.com/watch?v=pqWJwPArmek

### Why PB-008 is especially important

PB-008 explicitly asks how a monthly options strategy changes when India VIX is low versus high. It is therefore a direct source for the project's central question rather than merely a generic options-strategy video. However, source claims remain hypotheses until independently reconstructed and tested.

### Expanded cross-regime rule

Profit Breakout strategies are **not** being tagged as HIGH-VIX-only. The source material explicitly spans low/high VIX and changing-volatility conditions. Every mechanically reconstructable candidate from this channel must therefore enter the subsequent test matrix across **ALL, LOW, NORMAL, FALLING, RISING, HIGH, SPIKE and HIGH_RISING**, with regime-specific routing tested only after the baseline cross-regime matrix exists.
