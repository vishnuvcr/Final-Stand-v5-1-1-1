# Phase 50B Strategy Registry

## User-supplied Tradetron lineage

| # | Source export | Tradetron URL | Source-faithful characterization | VIX/tail treatment |
|---|---|---|---|---|
| 1 | Dynamic_Ratio_Reversals.json | https://tradetron.tech/bt/view/d164b781832c2202116c72af0d6dc76d | Monthly NIFTY delta-driven ratio/reversal state machine; ratio legs use delta-defined strikes and transition/exit logic. | Delta ladder + VIX conditioning |
| 2 | 020010_Delta_Calendar_Hedge_Spread_v4.json | https://tradetron.tech/bt/view/57d2b9ddc507843ad486a5323316622a | Current-week ±0.20-delta short premium plus next-week ±0.10-delta hedge, with adjustment states. | Calendar/tail-distance + VIX |
| 3 | Corrected_Dynamic-n_NIFTY_Weekly_Options_Strategy.json | https://tradetron.tech/bt/view/79b5f5977342301347e82a8175e9ddf8 | 3-days-to-weekly-expiry 10:00 entry; call-ratio / put-ratio variants using fixed ATM offsets and expiry-day variant. | Offset + delta variants + VIX |
| 4 | Profit_Breakout_Premium_Match_Straddle.json | https://tradetron.tech/bt/view/b83f1f24a8b677c67f472d5189902130 | 10:00 non-expiry-day ATM short straddle; premium mismatch trigger creates matching-premium repair leg. | OTM repair distance + VIX |
| 5 | Simple_Intraday_Short_Straddle.json | https://tradetron.tech/bt/view/667be6a22e2caa8866b7476065a68120 | 09:30 ATM weekly short straddle, max one trade/day, 15:15 exit or fixed P&L stop. | OTM strangle/wing variants + VIX |
| 6 | Intraday_Asym_Premium.json | https://tradetron.tech/bt/view/bc0e67d112845360381bd736f9f98e2d | 09:30 current-week ATM CE short + next-week ATM PE short; 50%-premium imbalance triggers matching-premium repair. | Tail-premium distance + VIX |
| 7 | Dynamic_IC_to_Ratio.json | https://tradetron.tech/bt/view/ade954a4a6aed2bb03b57462d71dd406 | Friday 09:20 monthly 30Δ/10Δ iron condor; short-leg delta trigger transitions to directional ratio; later ratio re-centering. | Delta ladder + VIX conditioning |

## Prior GitHub repositories / lineages

### Iron-condor-to-ratio-v1 / v2
Source-faithful reproduction project for the same IC→ratio strategy. v1 remains data-validation gated; v2 foundation is initialized. No performance conclusion is accepted from either repository.

### Option-intraday-v1
Closed research implementation of Intraday Asym Premium. Primary validated window: 2024-10-01 to 2025-12-31; 296 completed trades; net P&L **-₹54,536.79** at 1-point adverse slippage. This is a frozen negative control, not a deletion from the candidate universe.

### NoDip-Stage-1
Frozen four-leg NIFTY calendar: first trading day after prior weekly expiry, 09:15; near-ATM PE buy, near-ATM CE sell, far-expiry same-strike CE buy and PE sell; far expiry three weekly intervals out; exit near-expiry close. Historical primary study had 84 strict cycles and positive gross P&L, but it was descriptive and not a current-project promotion.

### MC-OPTIONS-INDEPENDENT-BACKTEST-MC1 / MC2 / MC3
NIFTY BATMAN lineage. Locked MC-RQ6-v1: D3/09:30, 756 historical-session bootstrap, 5,000 paths, P20/P35/P65/P80 mapping, +1/-2/+1/-2 legs, expiry exit. The lineage has not established a statistically robust production edge; MC3 verified the historical Monte Carlo method.

### Final-stand-v4
Includes dynamic OTM8 re-centering, premium-direction predictor work and full-chain option-surface/OI research. These are diagnostic research lineages; unfinished branches are not promoted as source-faithful trading results.

### Daily-Options
Contains a large finite tournament of NIFTY option strategy families, including regime-filtered credit spreads, breakout/OI confirmation and IV-skew/tail-credit work. Closed negative families remain useful null controls; unfinished families are not treated as accepted results.

### Naked-option-v1
Long-only NIFTY call/put direction research. Phase 0 is governance/bootstrap; no numerical result is imported as evidence.

## Deduplicated lineages

1. Dynamic IC→Ratio
2. Intraday Asym Premium
3. NoDip / Calendar
4. BATMAN
5. Dynamic Ratio / Ratio Reversal
6. Dynamic-n weekly ratios
7. Premium-match straddle
8. Simple short straddle
9. Final Stand option-surface/direction controls
10. Daily-Options defined-risk / skew controls
11. Long-only naked option control

