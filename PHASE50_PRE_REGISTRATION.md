# Phase 50 Pre-Registration

## Frozen scope

- Primary families: Bear Call, Bear Put, Bull Call, Bull Put, Iron Condor, Iron Butterfly, Put BWB, Call BWB, Call Backspread, Put Backspread.
- Primary VIX level states: LOW, NORMAL, HIGH.
- Secondary tags: RISING, FALLING, SPIKE, HIGH_RISING.
- Stage 1 tail distances: 2, 3, 4, 5, 6, 8, 10, 12 strike steps.
- Stage 1 control entry: 10:00 IST.
- Stage 1 control DTE: 4 trading sessions.
- Development: 2021–2023.
- Validation: 2024–2025.
- Holdout: 2026.
- Costs: accepted Phase-43 model including historical NIFTY lots, ₹10/order brokerage, statutory charges/GST, adverse ₹0.05 tick per leg, +50% monetary cost stress.

## Frozen scientific rules

- ATM is determined point-in-time from the NIFTY spot at entry.
- Strike distance is measured in listed-strike steps.
- Missing farther OTM quotes are not replaced by nearer strikes.
- No future data may determine VIX state or strike selection.
- Parameters may be changed only during registered development stages.
- Validation and holdout are frozen before use.

## Statistical gate

The final candidate set is confirmed using active-VIX versus complement-VIX inference with 10,000 bootstrap resamples, 10,000 one-sided permutation tests and Holm correction.

## Promotion rule

Promotion requires:
- economic validation positivity,
- +50% cost-stress positivity,
- sufficient trade count,
- positive active-vs-complement advantage,
- Holm-adjusted p < 0.05,
- and a protected 2026 confirmation.

Failure at any mandatory gate means NO PROMOTION.

## Explicit non-claims

Phase 50 does not assume high VIX is profitable, does not assume far OTM is superior, and does not treat the literature as evidence of a NIFTY trading edge.

## Sparse-HIGH rule added after feasibility audit
If a primary VIX state has fewer than 15 development observations under the fixed Stage-1 control, its confirmatory candidate gate is not relaxed. Instead, up to five top development far-OTM cells are carried forward as explicitly exploratory diagnostics. Exploratory results cannot be promoted and are excluded from the formal Holm candidate family.