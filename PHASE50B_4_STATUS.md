# Phase 50B-4 Status

**ACTIVE — FAR-OTM GEOMETRY REPLAY**

## Frozen universe
- BASE: 300/350/400 — persisted control
- OTM350: 350/400/450 — numerical candidate
- OTM400: 400/450/500 — numerical candidate

Only the strike-distance tuple changes.

## Promotion/selection gate
OTM350/OTM400 must independently pass >=95% coverage, positive DEV net and positive DEV +50% stress. If both qualify, the higher DEV +50% stress net is selected. If neither qualifies, no far-OTM mutation is selected.

Validation and 2026 HOLD are post-selection and descriptive only.

## Current step
Verify BASE, then replay OTM350 and OTM400 under GitHub Actions. No new distance is permitted.
