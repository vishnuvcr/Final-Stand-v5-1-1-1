# Phase 50B-6 Preregistration — Frozen OTM350 vs BASE

**Status: FROZEN before numerical inference.**

## Locked treatment

OTM350:
- CE: +350/+400/+450
- PE: -350/-400/-450

## Locked comparator

BASE:
- CE: +300/+350/+400
- PE: -300/-350/-400

## Protected sample roles

- DEV through 2023-12-31: selection history only; no new geometry selection.
- VAL 2024-01-01 through 2025-12-31: primary confirmatory sample.
- HOLD 2026 onward: protected descriptive sample; no selection and no inferential decision.

## Primary endpoint

Mean paired expiry-level net P&L difference OTM350 minus BASE on VAL under the standard cost model.

## Primary test

A deterministic expiry-block paired bootstrap with at least 10,000 resamples, producing a 95% confidence interval and one-sided p-value for positive uplift.

The inferential unit is the expiry/campaign block to preserve within-expiry dependence among option legs.

## Secondary endpoints

- +50% cost stress;
- ₹20/order brokerage;
- ₹20/order +50% stress;
- median paired expiry difference;
- fraction of validation expiries where OTM350 exceeds BASE;
- profit factor and drawdown diagnostics;
- year-by-year validation diagnostics;
- CALL/PUT directional diagnostics.

Holm correction will be used across the registered secondary economic tests.

## Prohibitions

No:
- new strike distances;
- new DTE rules;
- new entry times;
- new exits/stops;
- VIX threshold tuning;
- holdout-based selection;
- post-hoc subgroup selection;
- synthetic prices;
- forward filling;
- silent coverage removal.

## Decision principle

A positive raw result is not sufficient. The frozen mutation must demonstrate control-relative validation evidence that remains economically meaningful after realistic cost stress. Otherwise no promotion occurs.
