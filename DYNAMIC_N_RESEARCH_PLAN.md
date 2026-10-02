# Dynamic-n Research Plan — Corrected Restart

## Research question

Does the dynamic-n NIFTY weekly-options directional 3-leg ratio strategy, using the corrected execution/accounting engine and a pre-registered higher-n preference rule, produce positive gross and net returns after realistic execution costs over the validated historical sample?

## Locked strategy

### Entry and data snapshot
- Expiry = 0 DTE.
- Entry occurs exactly 4 trading sessions before expiry.
- Entry snapshot is exactly 10:00 IST.
- Nearest ATM is the strike closest to NIFTY spot at 10:00.
- NIFTY strike interval is ₹50; OTM-n means exactly ATM ± n×₹50.
- No ordinal ranking of sparse quotes and no forward filling.

### Stage 1 — Direction
Calculate:
- X_call_direction = CE(OTM8) + CE(OTM7) - CE(OTM6)
- X_put_direction = PE(OTM8) + PE(OTM7) - PE(OTM6)

Direction:
- X_call_direction > X_put_direction → BEARISH call-side structure.
- X_call_direction < X_put_direction → BULLISH put-side structure.
- Equality → no trade.
- Missing any required OTM6/7/8 price on either side → exclude and log.

### Stage 2 — Dynamic n evaluation
For the selected side, evaluate every n = 6,7,...,15:
- X_n = Premium(OTM(n+2)) + Premium(OTM(n+1)) - Premium(OTM n)

Completeness rule:
- All candidate values n=6..15 must be computable from exact OTM6..17 strikes.
- If any candidate strike/price is missing, exclude the expiry rather than selecting from an incomplete candidate set.

### Weightage / higher-n preference
Primary n-selection rule:
- Compute X_max = max(X_6,...,X_15).
- Eligible n values satisfy X_n >= 0.95 × X_max.
- Higher n values are preferred within this 95%-of-maximum eligibility band.
- Therefore select the largest eligible n.

This is deterministic and fixed before seeing trade outcomes. No post-result optimization is permitted.

### Stage 3 — Position
For selected n:
- buy OTM-n;
- sell OTM-(n+1);
- sell OTM-(n+2).

### Stage 4 — Target
T = 0.90 × X_selected × lot.

Exit on the first complete minute after entry where the slippage-adjusted three-leg gross P&L is at least T.

### Stage 5 — Expiry fallback
If target is not reached:
- exit at the latest complete three-leg observation at or before 15:29 IST on expiry day.

No stop loss.

## Execution and costs

- One adverse ₹0.05 option tick per leg.
- Correct long/short accounting:
  - long OTM-n: exit − entry;
  - short OTM-(n+1)/(n+2): entry − exit.
- Date-aware NIFTY lot size.
- Six executed orders per completed trade.
- Paytm Money brokerage assumption: ₹10 per unique F&O order.
- Date-aware statutory/transaction charges, STT, SEBI/IPFT, stamp duty and GST.
- No forward filling or synthetic prices.
- Incomplete observations are excluded and logged.

## Primary data

Validated executable overlap:
- 2021-05-27 through 2026-09-30.
- Primary source: thetrademarkk/india-index-options-1m.
- Earlier Zenodo 2019–2020 data is not used as primary weekly-contract evidence.

## Analysis phases

1. Dynamic-n specification and implementation audit.
2. Corrected primary backtest.
3. Statistical analysis.
4. Robustness/sensitivity.
5. Direct comparison with corrected fixed-OTM15 under the same sample and execution assumptions.
6. Controlled n-selection ablation: hold the Stage-1 direction selector constant and compare fixed n=6, fixed n=15, and the 95%-band dynamic selector under identical execution assumptions.
7. Final manuscript with tables, figures, appendices and reproducibility details.

## Pre-registered robustness

- target fraction;
- slippage;
- entry time;
- DTE;
- brokerage;
- higher-n threshold around the primary 95% value.

The primary 95% higher-n preference remains fixed unless a sensitivity analysis explicitly changes it.

## Supersession

All previous dynamic-n numerical results are superseded because the prior implementation contained calculation and strike-mapping errors. No previous dynamic-n trade ledger is reused.
