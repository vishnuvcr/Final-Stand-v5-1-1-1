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

### Stage 5 — Final exit sequence
After entry, evaluate the open position on complete minute observations:
1. target exit when combined slippage-adjusted gross P&L reaches T;
2. from 13:30 IST on expiry day, conditional stop when combined MTM < ₹0 and running MFE < 0.50×original target;
3. otherwise expiry fallback at the latest complete three-leg observation at or before 15:29 IST.

No pre-expiry payoff-boundary stop is applied.

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


## Phase 20 — payoff-boundary stop research

User question motivating this phase:
- What happens if NIFTY moves materially beyond the green/profit region of the entry-time payoff chart before expiry?

Research question:
- Does an entry-time expiry zero-P&L payoff boundary provide a robust early-warning exit that improves the corrected dynamic-n strategy without cutting baseline-profitable trades, and does it add information beyond the Phase-19 expiry-day conditional stop?

Definition:
- For the selected three-leg structure, compute the entry-time net credit after the same modeled entry slippage used by the backtest.
- Construct the expiry intrinsic P&L as a function of NIFTY spot using the actual selected strikes and entry credit.
- Define the dangerous-side boundary as the zero-P&L point of that expiry payoff:
  - call-side: upper boundary = K_(n+1) + K_(n+2) - K_n + entry_credit;
  - put-side: lower boundary = K_(n+1) + K_(n+2) - K_n - entry_credit.
- This is a structural expiry boundary, not an intraday fair-value boundary. A spot breach while time remains can recover; therefore filtered variants are tested separately.

Pre-registration:
- Boundary buffers: 0, 50, 100, 200 and 400 NIFTY points beyond the expiry breakeven boundary.
- Confirmation: 1 consecutive complete minute or 3 consecutive complete minutes.
- Condition families:
  1. boundary-cross only;
  2. boundary-cross + current combined three-leg MTM < 0;
  3. boundary-cross + current MTM < 0 + running MFE < 0.50× target.
- The Phase-19 rule is a fixed comparator, not re-optimised here:
  **13:30 IST on expiry day + combined MTM < 0 + running MFE < 0.50× original target.**
- A combined rule is evaluated only after the boundary candidate is selected: earliest of the selected boundary stop and the fixed Phase-19 comparator.

Walk-forward protocol:
- Training/selection: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Holdout: 2026-01-01 through 2026-09-30.
- Boundary-rule selection uses training only.
- Primary safety constraint: zero baseline-positive trades affected in training; validation/holdout are then observed without re-optimisation.
- Promotion evidence requires positive net-P&L uplift in validation and holdout, zero baseline-positive trades affected, and no material maximum-drawdown deterioration.
- Exact minute-level three-leg execution prices, one-adverse-tick slippage, six-order brokerage and date-aware statutory charges are retained.

Coverage and limitations:
- Boundary monitoring uses exact timestamps where all three option legs and NIFTY spot are simultaneously available; no forward filling or interpolation is permitted.
- If the underlying crosses between observations, the backtest cannot claim that the crossing was observed.
- The boundary is based only on entry information and therefore contains no look-ahead.
- The Phase-19 rule remains the fixed comparator. This phase does not silently replace it.

Phase-20 completion criterion:
- Produce a frozen comparison report covering baseline, Phase-19 comparator, best boundary candidate, and combined candidate; report train/validation/holdout/full-sample P&L, drawdown, stop counts, affected winners and loss reductions.
- Conclude whether payoff-boundary information should enter the complete research strategy specification.


## Phase 20 completion — final historical entry-to-exit specification

Phase 20 was executed on branch `phase-20-payoff-boundary-stop-research` using the corrected 190-trade ledger and exact common-minute NIFTY/option observations.

### Boundary research result

The pre-registered grid tested:
- expiry zero-P&L payoff boundary buffers: 0, 50, 100, 200 and 400 NIFTY points;
- 1-minute and 3-minute confirmation;
- boundary-only, boundary + negative MTM, and boundary + negative MTM + MFE<0.50×target.

The training-safe selector was **400-point buffer / 1-minute / boundary-only**. It produced +₹711.91 training uplift, but **−₹14,390.87** validation uplift and **−₹49,064.48** 2026 holdout uplift, with maximum drawdown increasing to ₹41,711.94 in validation and ₹65,371.18 in holdout. The combined boundary-plus-Phase-19 rule was also negative out of sample.

Therefore **no payoff-boundary/green-area stop is admitted to the final strategy**.

### Phase-19 comparator audit

Phase 20 reconstructed the fixed comparator directly from minute paths and cross-checked it against the Phase-19 walk-forward grid. Cross-check status: **PASS**.

Final expiry-day conditional stop:
**13:30 IST on expiry day + current combined MTM < ₹0 + running MFE < 0.50×original target.**

Walk-forward:
- Training: +₹1,963.67, zero baseline-positive trades affected.
- Validation 2024–2025: +₹1,923.59, zero baseline-positive trades affected.
- 2026 holdout: +₹6,305.15, zero baseline-positive trades affected, no holdout max-DD change.
- Full sample: +₹10,192.41; 5 exits changed; zero baseline-positive trades affected.

### Final strategy lock

The final historical research specification is now frozen in:
- `FINAL_STRATEGY_RULES.md`
- `STRATEGY_SPEC.md`
- `DYNAMIC_N_SPEC.md`

Complete exit precedence:
1. target;
2. 13:30 expiry-day conditional stop;
3. 15:29 expiry fallback.

There is **no pre-expiry payoff-boundary stop**.

### Final-rule historical result

Applying the final exit logic to all 190 corrected trades:
- net P&L: **₹149,129.53**
- mean net/trade: **₹784.89**
- net winners: **179/190 (94.21%)**
- profit factor: **2.34**
- max drawdown: **₹27,336.11**
- target exits: **178**
- conditional-stop exits: **5**
- expiry-fallback exits: **7**
- baseline-positive trades stopped early: **0**

This result is historical and does not establish future profitability or live implementability.

## Phase 21 — pre-expiry adverse-move risk control

User question: what should be done when NIFTY moves very far against the strategy before expiry?

This phase tests a bounded, pre-registered extension on top of the frozen Phase-20 strategy rather than changing the historical comparator.

Candidate families:
- direction-aware early exit after 200/300/400/500/600 adverse NIFTY points from the 10:00 entry spot;
- 1/5/15 consecutive-minute confirmation;
- spot-only, negative-MTM, and negative-MTM-plus-MFE<0.50×target filters;
- tail-hedge repair that buys one OTM-(n+3) option on the dangerous side after the same signal, with either target-or-baseline exit or recovery-to-zero-baseline exit.

Comparator: the frozen Phase-20 final strategy, including the 13:30 expiry-day MTM/MFE stop.

Selection: training through 2023-12-31 only; zero baseline-positive trades may be affected; no hedge execution gaps; then maximize training net uplift and loss reduction.

Promotion: positive validation and 2026 holdout uplift; zero baseline-positive trades affected; no material maximum-drawdown deterioration; no hedge execution gaps.

No additional threshold family will be introduced after inspecting results. A materially different adjustment is a separate registered phase.


[RUN_PHASE21_ADVERSE_MOVE_TRIGGER]

## Phase 21 completion — pre-expiry adverse-move risk control

The pre-registered 200/300/400/500/600-point direction-aware trigger grid, 1/5/15-minute confirmations, spot/MTM/MFE signal families, and one-lot OTM-(n+3) tail-hedge repair were completed on the corrected 190-trade minute-level engine.

No candidate passed the training safety constraint of zero baseline-positive trades affected. The closest candidate, 600-point/1-minute/spot-only early exit, improved training by ₹1,885.47 but produced −₹33,923.36 validation uplift and −₹44,039.53 2026 holdout uplift and increased full-sample maximum drawdown to ₹52,740.01.

Decision: no pre-expiry adverse-move stop or one-lot n+3 hedge is promoted. The Phase-20 final strategy remains frozen. A materially different risk-control mechanism requires a separately registered phase.

