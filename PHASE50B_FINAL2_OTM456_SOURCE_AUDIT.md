# Phase 50B — Final-stand-v2 OTM4/OTM5/OTM6 Source Audit

## Frozen prior specification

The Final-stand-v2 research plan defines:
- signal timestamp: previous weekly expiry-day close;
- baseline Monte Carlo: GBM with leakage-safe 252-session calibration and 50,000 simulations;
- Bull/Bear signal from median simulated terminal price relative to signal spot;
- entry: 10:00 IST on the trading day four trading sessions before the next expiry;
- default strike mapping: 4th/5th/6th listed strikes away from ATM on the signal day;
- position: 1 long OTM4 + 1 short OTM5 + 1 short OTM6 on the predicted side;
- expiry exit;
- explicit brokerage/fees/slippage;
- chronological out-of-sample and statistical robustness controls.

## Role in Phase 50B

This is a high-priority prior strategy candidate because it provides a distinct **direction-selector + bounded option-payoff** lineage rather than another pure volatility-selling structure.

Phase 50B will not reuse previous tuning results as evidence. The frozen source specification becomes the provenance baseline. Any VIX, cross-market, OI, FII/DII or other selector overlay must be registered as a new finite mutation and evaluated chronologically.

## Future mutation dimensions allowed here

Only after source-faithful baseline:
- VIX-conditioned direction overlay;
- cross-market confirmation;
- option-chain/OI confirmation;
- strike mapping sensitivity (signal-day ATM vs entry-day ATM);
- finite OTM-distance sensitivity around 4/5/6 where preregistered.

No post-hoc selector tuning is permitted from protected 2026 results.
