# Phase 50B — Source / Baseline Audit

## A. User-supplied Tradetron strategies

These numbers are the finished Tradetron account backtest reports, included as provenance and exploratory controls, not as accepted Final Stand evidence.

| ID | Strategy | Native report net P&L | Trades | PF | Max net DD | High-VIX outcome-day gross diagnostic |
|---|---|---:|---:|---:|---:|---|
| TT-01 | Dynamic Ratio Reversals | ₹91,975.51 | 1,877 | 1.030 | ₹53,385.20 | −₹8,979.75 / 22 days |
| TT-02 | 0.20/0.10 Delta Calendar Hedge Spread v4 | ₹61,776.91 | 1,948 | 1.025 | ₹80,587.45 | +₹72,543.25 / 51 days |
| TT-03 | Corrected Dynamic-n Weekly Options | ₹104,274.20 | 558 | 1.185 | ₹26,812.48 | −₹12,044.50 / 16 days |
| TT-04 | Profit Breakout Premium Match Straddle | ₹59,500.13 | 1,218 | 1.050 | ₹36,284.59 | −₹11,102.00 / 33 days |
| TT-05 | Simple Intraday Short Straddle | ₹159,447.32 | 2,448 | 1.059 | ₹64,325.38 | −₹32,256.25 / 57 days |
| TT-06 | Intraday Asym Premium | ₹237,265.75 | 3,722 | 1.068 | ₹64,645.33 | −₹30,894.50 / 57 days |
| TT-07 | Dynamic IC to Ratio | ₹44,416.37 | 820 | 1.031 | ₹43,972.07 | −₹6,149.00 / 11 days |

## Important caveats

1. The Tradetron reports have a high-severity COVERAGE_PARTIAL caveat. These totals cannot be treated as complete-window evidence.
2. TT-01 and TT-07 have additional set-attribution caveats.
3. TT-02 has 1,364 unresolved entry opportunities in its report metadata.
4. TT-03 has a high-severity expiry-set attribution caveat.
5. Tradetron reports use a brokerage profile of ₹0/order in these runs, so they are not yet comparable to the project's Paytm Money cost model.
6. The high-VIX column is a diagnostic outcome-day classification: each result day is classified using the parent Phase-43 point-in-time VIX regime from the prior VIX close. It is not entry-regime performance and is not a promotion test.

## B. Research interpretation

TT-02 — 0.20/0.10 Delta Calendar Hedge Spread v4 has strongly positive gross P&L on HIGH-VIX outcome days (+₹72,543 across 51 result days), unlike the other six supplied strategies.

This is not a conclusion. It is the strongest new VIX hypothesis because it is structurally different from the Phase-49 near-ATM bearish-spread winners, explicitly delta-defined, cross-expiry, and heavily hedged.

## C. Prior repository lineages

### Option-intraday-v1
The independent repository research is already closed after P9. It tested the same basic Intraday Asymmetric Premium rule and concluded 296 primary completed trades, a validated primary window of 2024-10-01 through 2025-12-31, and −₹54,536.79 net P&L under 1-point adverse slippage. Therefore TT-06's positive native report cannot be imported as confirmation.

### NoDip-Stage-1
Locked four-leg calendar study: 84 strict frozen cycles; ₹83,030 gross P&L; 61.90% win rate; PF 2.942; max DD ₹8,022.50; 62.7% strict coverage. It is a calendar-family historical control, not confirmed VIX evidence.

### MC-OPTIONS-INDEPENDENT-BACKTEST-MC1
Locked NIFTY BATMAN: D3 before expiry, 09:30, 756-session × 5,000-path MC, P20/P35/P65/P80 strike mapping, +1/-2/+1/-2 position, and 2 option-points/leg primary slippage. Phase-8 methodological revalidation reported calibration sensitivity and block-bootstrap intervals including zero. It is a tail-geometry control, not a promoted strategy.

### Iron-condor-to-ratio-v1/v2
The source strategy is precisely specified but not yet performance-validated in the source repository. v1 remains in Phase-1 production historical-Greek/IV acquisition with Phase 2 blocked. It enters Phase 50B as a prospective candidate.

### Final-stand-v4
Phase-11 premium-direction research remains a research lead, not an authorized strategy. Phase-12 full-chain/OI direction research is implementation-stage. These belong in the selector-overlay lineage, not as direct strategy P&L evidence.

## D. Phase-50B priority before new numerical replay

1. TT-02 / Delta Calendar Hedge Spread v4 — highest new VIX hypothesis.
2. TT-07 / Dynamic IC to Ratio — structurally closest to the proven source IC→ratio lineage.
3. TT-01 / Dynamic Ratio Reversals — delta-driven dynamic tail strategy.
4. TT-03 / Corrected Dynamic-n — explicit far-OTM fixed-point geometry.
5. NoDip calendar — independent calendar-family control.
6. BATMAN — independent tail-geometry control.
7. TT-04/05/06 — controls rather than leading high-VIX candidates; TT-06 needs reconciliation against the independently closed negative Option-intraday study.

## E. Next numerical action

Do not tune Phase-50B using these native report numbers. Replay the top source-faithful candidates under the Final Stand common cost/quote model with entry-date VIX state, source-semantic delta/strike conversion, semantically valid far-OTM mutations, 2021–2023 development, frozen 2024–2025 validation, protected 2026 holdout, Paytm Money brokerage + statutory charges + adverse slippage, and multiple-testing correction.

Only after that do we decide whether TT-02's high-VIX signal survives.