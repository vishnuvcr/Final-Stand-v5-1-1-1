# Phase 45 Research Plan — Exhaustive Ready-Made NIFTY Option Strategy Study

## Research question
Across the ready-made option strategies shown in the user's strategy builder screenshots, which structures perform best in each India-VIX state after realistic NIFTY execution costs, and do any regime-specific results survive validation and untouched-holdout confirmation?

## Scope
Phase 43 already evaluated 22 core strategy families, including straddles, strangles, directional spreads, butterflies, iron butterfly/condor, broken-wing butterflies, ratio spreads, backspreads and calendars. Phase 45 adds the remaining ready-made structures visible in the screenshots and produces a unified comparison across the full ready-made set.

### Newly tested in Phase 45
- Buy Call
- Sell Put
- Bull Condor
- Bull Butterfly
- Range Forward
- Buy Put
- Sell Call
- Bear Condor
- Bear Butterfly
- Bear Risk Reversal
- Batman
- Jade Lizard
- Reverse Jade Lizard
- Long Iron Condor
- Long Iron Butterfly
- Double Plateau
- Strip
- Strap
- Long Synthetic Future
- Short Synthetic Future

### Reused from accepted Phase-43 evidence
The accepted Phase-43 trade matrix is reused unchanged for the 22 already-tested families so the phase does not duplicate numerical work unnecessarily. Their results remain provenance-linked to Phase 43.

## Fixed trading protocol
- NIFTY weekly expiry.
- Entry exactly 4 trading sessions before expiry at 10:00 IST.
- ATM is the nearest listed strike to the entry spot.
- Offsets are in verified listed-strike steps.
- Primary exit is the latest complete observation at or before 15:29 IST on the relevant expiry day.
- One historical NIFTY lot per leg.
- One adverse ₹0.05 option tick per leg at entry and exit.
- ₹10 Paytm Money F&O brokerage per executed order.
- Date-aware STT, exchange charges, SEBI fee, IPFT, stamp duty and GST.
- No forward filling, interpolation or synthetic quote generation.

## VIX states
ALL, LOW, NORMAL, HIGH, SPIKE, FALLING, RISING and HIGH_RISING using prior-observation expanding thresholds exactly matching the accepted Phase-43 convention.

## Definitions for newly tested structures
- Bull Condor: +1 CE, -1 CE at +2 steps, -1 CE at +3 steps, +1 CE at +4 steps.
- Bull Butterfly: +1 CE, -2 CE at +2 steps, +1 CE at +3 steps.
- Bear Condor: +1 PE at -1 step, -1 PE at -2, -1 PE at -3, +1 PE at -4.
- Bear Butterfly: +1 PE at -1, -2 PE at -2, +1 PE at -3.
- Bullish Range Forward: +1 CE at +1, -1 PE at -1. The screenshot's Range Forward is recorded as a distinct named preset even though its legs coincide with the bullish risk-reversal construction.
- Bear Risk Reversal: +1 PE at -1, -1 CE at +1.
- Batman: +1 CE +1, -2 CE +2, +1 PE -1, -2 PE -2.
- Jade Lizard: -1 PE, -1 CE/+2 CE call spread.
- Reverse Jade Lizard: -1 CE, -1 PE/+2 PE put spread.
- Double Plateau: put condor at -4/-3/-2/-1 plus call condor at +1/+2/+3/+4.
- Long Iron Condor: +1 PE -1/+1 CE +1, sell outer -3 PE/+3 CE.
- Long Iron Butterfly: +1 ATM PE +1 ATM CE, sell -2 PE/+2 CE.
- Strip: +1 CE +2 PE at ATM.
- Strap: +2 CE +1 PE at ATM.
- Long Synthetic Future: +1 ATM CE, -1 ATM PE.
- Short Synthetic Future: -1 ATM CE, +1 ATM PE.
- Buy Call / Buy Put / Sell Call / Sell Put use ATM single-leg presets.

Unbounded structures remain diagnostic-only and are never promoted. Defined-risk and undefined-risk results are reported separately.

## Validation and holdout discipline
Validation (2024-01-01 through 2025-12-31) is the selection period. The 2026 holdout is confirmation only after the validation freeze. No holdout result may alter strategy definitions or ranking rules.

## Statistical analysis
For each strategy × VIX state, report trade count, net P&L, +50% cost-stress net P&L, mean net/trade, win rate, maximum drawdown, profit factor where defined, and active-vs-complement VIX regime difference with 10,000 bootstrap confidence intervals and permutation/sign-flip style p-values. Holm adjustment is applied across the preregistered validation comparison family.

## Working-strategy screen
A candidate state is considered empirically working only when validation has at least 20 active trades, positive net P&L, positive +50% cost-stress P&L, and positive mean active-vs-complement advantage. Statistical significance is reported separately and is required for formal promotion.

## Stage plan
1. Governance and provenance audit.
2. Build the missing ready-made strategy matrix using cached data and HF_TOKEN only for missing option files.
3. Combine with the accepted Phase-43 matrix for the full ready-made universe.
4. Validation ranking by VIX state, separated by defined-risk status.
5. Freeze top validation candidates per regime.
6. Confirm those frozen candidates on 2026 holdout without changing parameters.
7. Produce manuscript, tables, charts, error/status logs and final strategy/regime map.

## Stop condition
Phase 45 closes after the fixed ready-made universe, validation ranking, holdout confirmation and inference are complete. Any new strategy family, new strike geometry beyond this registration, or new adaptive optimization becomes a subsequent phase.