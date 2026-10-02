# Phase 21 — Pre-Expiry Adverse-Move Risk Control Conclusion

## Research question

Can a very large adverse NIFTY move before expiry be used to either close the three-leg position early or add one OTM-(n+3) tail hedge, while reducing losses without sacrificing profitable trades?

## Frozen comparator

Phase-20 final strategy:
1. 90% of selected-X target;
2. from 13:30 IST expiry day, exit when combined MTM < 0 and running MFE < 0.50× target;
3. otherwise expiry fallback at the latest complete observation at or before 15:29;
4. no payoff-boundary stop.

Baseline for this phase:
- 190 trades
- net P&L ₹149,129.53
- maximum drawdown ₹27,336.11

## Pre-registered test

Direction-aware NIFTY adverse moves:
- 200/300/400/500/600 points
- 1/5/15 consecutive-minute confirmation
- spot-only, negative-MTM, and negative-MTM-plus-MFE<0.50×target signals.

Two action families:
- early exit of all three original legs;
- buy one OTM-(n+3) option on the adverse side, with target-or-baseline or recover-to-zero-or-baseline exit.

All candidates used the corrected minute-level engine, exact strike mapping, one adverse ₹0.05 option tick, historical NIFTY lot sizes, ₹10/order brokerage and the audited statutory/transaction cost model.

## Training safety result

**No candidate passed the pre-registered training safety screen.**

The screen required zero baseline-positive trades to be affected before their frozen Phase-20 comparator exit.

The smallest number of affected profitable training trades among the candidate grid was **1**, reached by the 600-point threshold family. Therefore no rule was eligible for walk-forward promotion under the pre-registered protocol.

## Closest training candidate — early exit

**600 NIFTY points / 1-minute confirmation / spot-only**

Training:
- uplift: **+₹1,885.47**
- profitable trades affected: **1**
- loss reduction: **₹13,590.83**

2024–2025 validation:
- uplift: **−₹33,923.36**
- profitable trades affected: **2**

2026 holdout:
- uplift: **−₹44,039.53**
- profitable trades affected: **2**

Full sample:
- uplift: **−₹76,077.42**
- candidate net P&L: **₹73,052.11**
- maximum drawdown: **₹52,740.01**, versus **₹27,336.11** for the frozen comparator
- drawdown deterioration: **₹25,403.90**

Thus even the closest candidate that looked positive in training failed both later periods and materially worsened drawdown.

## Tail-hedge result

The closest training tail-hedge analogue was:

**buy one OTM-(n+3) option after a 600-point / 1-minute spot trigger**

Training uplift was only **+₹1,078.84**, with one profitable training trade affected.

Validation uplift was **−₹32,168.32** and 2026 holdout uplift was **−₹44,400.51**.

Full-sample uplift was **−₹75,490.31**, with maximum drawdown **₹52,924.61**.

The hedge therefore did not produce a robust tail-loss repair after its additional execution costs.

## Decision

**Phase 21 does not produce a promotable pre-expiry stop or adjustment.**

The frozen Phase-20 strategy remains unchanged.

In particular, the research does **not** support:
- exiting simply because NIFTY is 200–600 points adverse from entry;
- adding a single farther-OTM n+3 hedge on those same thresholds;
- using these signals as a deterministic pre-expiry repair rule.

The evidence indicates that the large adverse NIFTY moves are not sufficiently persistent or one-directional to make a simple spot-distance trigger reliable. The same signal can occur in trades that subsequently recover and reach the original target, which is exactly what the strict training-winner constraint exposed.

## What this means operationally

For the historically tested rule set, the defensible risk-control architecture remains:

**10:00 entry → target exit when reached → 13:30 expiry-day MTM/MFE stop → 15:29 expiry fallback.**

There is no validated pre-expiry hard stop or one-step tail hedge.

This does not mean large adverse moves are harmless. It means that, within the tested 200–600 point trigger families and the specified execution model, forcing an intervention before expiry damaged the strategy more than it helped.

## Strengths

- Uses the corrected 190-trade dynamic-n ledger.
- Tests both exit and repair mechanisms.
- Uses direction-aware spot movement.
- Preserves exact minute observations and execution costs.
- Uses training-only screening and a separate 2024–2025 validation plus 2026 holdout.
- Explicitly records the effect on historically profitable trades.

## Limitations

- Only the pre-registered 200–600 point threshold family was tested.
- The hedge tested only one farther-OTM option and did not optimize hedge quantity, dynamic delta or multi-step rebalancing.
- Historical minute data do not reproduce live bid/ask depth, latency, partial fills or liquidity shocks.
- The 190-trade sample is still modest for tail-event inference.

## Future research

A materially different risk-control mechanism should be treated as a separately registered phase, not added retrospectively to this grid. Candidates worth considering scientifically are dynamic delta-based hedging, volatility-regime filters, event-gap controls and multi-step repair rules that depend on option sensitivity rather than a fixed NIFTY-point threshold.

