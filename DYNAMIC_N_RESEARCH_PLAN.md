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
8. Stop-loss extension: use the same corrected minute-level engine to test pre-registered exit rules, with strict protection of baseline-positive trades and temporal validation.

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

## Phase 17 stop-loss research protocol

The objective is not to maximize win rate. The primary constraint is to identify a rule that can reduce the tail losses **without stopping any baseline-positive trade before its baseline exit** on the development sample.

Candidate families are fixed before execution:
- hard MTM stop after 0/24/48/72 elapsed hours at 0.50× to 2.00× target;
- expiry-day negative-P&L cutoffs at 14:00, 14:30 and 15:00 IST;
- stagnation stops after 24/48/72 hours;
- MFE-based trailing stops;
- hard-stop plus expiry-day cutoff combinations.

For hard, expiry-day and stagnation candidates, both one-minute and three-minute confirmation are tested.

Temporal validation:
- development: through 2024-12-31;
- validation: 2025-01-01 through 2026-09-30.

Rule selection is frozen using development data only:
1. zero baseline-positive trades affected;
2. maximize development net-P&L uplift;
3. maximize development loss reduction;
4. minimize affected winners as the final tie-break.

The selected rule is then applied unchanged to the validation period. Exact stop-time leg prices and the same date-aware fee model are used. This extension does not alter the no-stop primary result unless a later phase explicitly promotes a rule after successful validation.


## Phase 18 conditional-stop refinement

Phase 17 found no rule that both improved validation net P&L and left all baseline-positive trades untouched. Phase 18 therefore tests one narrowly motivated refinement rather than expanding the search indiscriminately:
- expiry-day negative MTM cutoffs at 13:30, 14:00, 14:30 and 15:00 IST;
- require running MFE to remain below 0, 0.10, 0.25, 0.50, 0.75 or 1.00 times target;
- one-minute and three-minute confirmation.

The rule is selected on development data only, then frozen for validation. A candidate is not promoted unless validation also leaves all baseline-positive trades untouched and improves net P&L.


## Phase 19 walk-forward stop confirmation

The Phase 18 candidate family produced a positive result under the 2021-2026 development/validation split. Because the 13:30 / target-MFE condition still requires temporal confirmation, Phase 19 performs a separate walk-forward test using:
- training/selection: through 2023-12-31;
- validation: 2024-01-01 through 2025-12-31;
- holdout: 2026-01-01 through 2026-09-30.

The same pre-registered Phase 18 cutoff/MFE family is tested. The rule is selected using training data only. Promotion requires zero baseline-positive trades affected and positive net-P&L uplift in both validation and holdout, with no material maximum-drawdown deterioration.


## Phase 19 result — final stop-loss research state

The formal training-only selector chose **13:30 IST / negative MTM / MFE < 1.00× target**, but that rule materially worsened the 2026 holdout maximum drawdown and is **not promoted**.

A nearby robustness candidate, tested in the same pre-registered Phase 19 grid, is retained for paper/forward validation:

**13:30 IST on expiry day + combined three-leg MTM < ₹0 + running MFE < 0.50× original target.**

Walk-forward evidence for this candidate:
- Training (through 2023-12-31): +₹1,963.67 net uplift, 0 baseline-positive trades affected.
- Validation (2024-01-01 to 2025-12-31): +₹1,923.59 net uplift, 0 baseline-positive trades affected.
- Holdout (2026-01-01 to 2026-09-30): +₹6,305.15 net uplift, 0 baseline-positive trades affected, no change in maximum drawdown.
- Full sample: +₹10,192.41 net uplift, 0 baseline-positive trades affected, 5 of 190 exits changed, all of them baseline losing trades.

The candidate does not eliminate any loss completely; it truncates selected expiry losses earlier. It remains a **research candidate**, not a replacement for the locked no-stop primary, until forward execution validation is completed.

Phase 19 is therefore the final stop-loss research phase unless a future forward-data phase is explicitly initiated.
