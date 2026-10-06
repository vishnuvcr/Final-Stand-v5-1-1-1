# Phase 36 Results Index — Independent Per-Trade Direction Selector Overlay

**Final decision: REJECTED — NO LIVE-TRADING PROMOTION**

## Final accepted evidence
- GitHub Actions run: 37428502722 (#4)
- corrected code revision: c8963bcded49ae15cf5b059394f3471ec1c3f2a4
- all seven selector jobs: success
- publication job: success
- final artifact commit: produced by the publication job on the Phase-36 branch

## Primary window
2024-01-01 through 2026-06-30.
128 expected expiries; 104 expiry files available; one later file incomplete; 103 processed expiry files in the final treatments.

## State-dependent control
206 trades; net ₹63,672.58; gross ₹84,054.00; costs ₹20,381.42; win rate 65.53%; PF 1.203; max drawdown ₹61,960.87.

## Independent selectors
OTM789_FRESH -₹39,122.38; OTM678_FRESH -₹62,665.27; DART -₹54,475.24; OOF_STACK -₹59,868.85; WAVELET_TREE -₹66,398.02; MARKOV_REGIME_TREE -₹88,163.44; CATBOOST -₹92,977.93.

## 2026 holdout
All seven selectors lost money; the stateful control was approximately flat at -₹275.65.

## Statistical comparison
Per-expiry bootstrap mean differences versus the control were negative for every selector; every 95% interval was entirely below zero.

## Artifacts
Each selector folder contains trades.csv, skips.csv, summary.csv, yearly_statistics.csv, direction_statistics.csv, selector_usage.csv, coverage.json and run.log.
