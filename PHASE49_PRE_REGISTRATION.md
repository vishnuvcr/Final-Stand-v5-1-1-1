# Phase 49 Pre-Registration

## Frozen before numerical execution

- Primary families: Bear Call, Bear Put, Put BWB.
- Primary regimes: LOW and NORMAL.
- Search grid: 192 Bear Call + 144 Bear Put + 384 Put BWB configurations per regime = 1,440 total candidates.
- Development forward folds: 2022 and 2023.
- Validation: 2024-2025.
- Holdout: 2026.
- Costs: historical NIFTY lot sizes, ₹10/order brokerage, date-aware statutory charges/GST, adverse ₹0.05 tick per leg, +50% monetary fee/charge stress.
- No parameter change after validation freeze.

## Selection rule

Development candidate ranking is based on average forward-fold stressed mean/trade with consistency and drawdown constraints. One candidate per family×regime is frozen.

## Failure conditions

Look-ahead, wrong expiry linkage, quote substitution, incorrect lot size, incorrect strike construction, validation tuning, holdout access before freeze, or incorrect cost accounting makes the affected result non-evidence.