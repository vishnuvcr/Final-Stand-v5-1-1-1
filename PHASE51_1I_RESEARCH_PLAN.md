# Phase 51-1I — Authorized Access Recovery

## Objective
Determine whether an authorized broker/API credential already configured in the repository permits recovery of the two missing Phase-51 NIFTY option blocks.

## Routes
Priority remains:
1. Upstox expired instruments + 1-minute candles.
2. ICICI Breeze.
3. Dhan.
4. Authorized commercial archive.

This branch first performs a non-secret credential-presence inventory. If UPSTOX_ACCESS_TOKEN is present, the existing preregistered Upstox acquisition gate runs automatically.

## Safety
Secrets are never printed. Only boolean presence and acquisition status are recorded.

No strategy P&L is inspected during acquisition. Raw data must pass integrity, common-source equivalence and >=95% replay coverage gates before entering the OOS engine.

## Stop rule
If no authorized route is configured, Phase 51 remains DATA-BLOCKED and the branch closes without changing the OOS window.

## External context
Upstox's current official documentation confirms an expired-option contract endpoint and 1-minute expired historical candles, with the latter restricted to the Plus plan. This makes an already-authorized Upstox credential the highest-priority reproducible route.
