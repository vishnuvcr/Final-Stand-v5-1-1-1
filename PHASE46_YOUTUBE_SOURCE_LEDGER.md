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
