# Phase 50B-3 Final Report — VIX Conditioning

## Decision

**CLOSED — DESCRIPTIVE VIX CONDITIONING COMPLETE; NO REGIME PROMOTED.**

Four feasible Phase-50B source-faithful strategies were evaluated across seven frozen entry-time VIX modes: **28 registered strategy×regime hypotheses** and 84 split-level cells.

No VIX threshold, strategy parameter, strike, DTE, stop or exit rule was tuned. The 2026 HOLD period was not used for selection or inference.

## Feasibility

| Strategy | Trades | Coverage | VIX-unobservable |
|---|---:|---:|---:|
| TT-02 | 247 | 98.02% | 0 |
| TT-03 | 200 | 99.50% | 0 |
| TT-04 | 1,214 | 98.54% | 0 |
| TT-05 | 1,184 | 96.65% | 0 |

TT-06 and TT-07 were terminal FAIL_COVERAGE and were excluded from all VIX analysis.

## Descriptive findings

**TT-03:** NORMAL was the strongest large-sample cell: DEV net ₹38,716.41 across 41 trades and VAL net ₹28,708.78 across 43 trades; +50% stress nets were ₹37,148.37 and ₹27,012.55. LOW was positive in DEV but negative in VAL. HIGH was sparse.

**TT-04:** NORMAL produced positive DEV/VAL net of ₹31,636.09 / ₹32,742.21 and +50% stress of ₹23,399.76 / ₹22,971.45. HIGH was negative in DEV/VAL but positive in protected HOLD, illustrating why HOLD cannot select regimes.

**TT-05:** NORMAL produced positive DEV/VAL net of ₹30,191.31 / ₹95,173.07 and +50% stress of ₹21,961.96 / ₹85,453.97. LOW was negative in DEV/VAL and HOLD was negative in NORMAL/HIGH.

**TT-02:** regime behavior was mixed: NORMAL was positive in DEV/VAL but negative in HOLD; HIGH was sparse and negative in DEV/VAL but positive in HOLD.

These are descriptive observations only.

## Statistical analysis

No hypothesis test was run in Phase 50B-3. Phase 50B-6 will apply the preregistered bootstrap/permutation framework to DEV+VAL only, with Holm correction across all 28 hypotheses. HOLD remains excluded from inference.

## Conclusion

VIX conditioning is retained as a **research variable**, not a promoted filter. All 28 hypotheses remain registered for the subsequent finite statistical/chronological gates.

The next bounded phase is Phase 50B-4 far-OTM geometry, limited to the preregistered TT-03 BASE/OTM350/OTM400 family.
