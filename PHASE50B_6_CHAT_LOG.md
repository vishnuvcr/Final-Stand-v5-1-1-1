# Phase 50B-6 Action Log

## 2026-10-09 — Phase initialized

OTM350 was frozen from Phase 50B-4 as the strongest preregistered far-OTM mutation. BASE remained the fixed comparator.

## 2026-10-09 — Pairing audit correction

The first inference implementation incorrectly required identical exit timestamps. This was rejected as an audit design error because exit timing is a treatment outcome and can legitimately differ between geometries.

The corrected unit is the common expiry/campaign block. The corrected audit found:
- 76 common validation expiry blocks;
- 0 entry timestamp mismatches;
- 18 exit timestamp mismatches;
- 0 direction mismatches.

## 2026-10-09 — Statistical inference

Accepted Actions run 37851668489 completed the preregistered inference and audit.

Primary result:
- mean OTM350 minus BASE = -₹73.88 per validation expiry;
- 95% bootstrap CI = -₹282.26 to +₹149.36;
- one-sided sign-flip p = 0.7386;
- 10/76 expiry blocks favored OTM350;
- 66/76 favored BASE.

All registered cost-stress variants remained unfavorable to OTM350.

## 2026-10-09 — Phase close

Phase 50B-6 is closed with **NO PROMOTION**. OTM350 is rejected as an improvement over BASE.

No additional far-OTM tuning is permitted from this result. The research chain returns to endpoint data recovery/full-window OOS validation and final manuscript integration.
