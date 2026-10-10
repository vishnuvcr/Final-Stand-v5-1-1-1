# Phase 78 Error Log
Date: 2026-10-10

## B78-001 — Cross-window temporal disagreement
- Status: CLOSED as a research finding; the underlying instability remains.
- TT-04 historical HOLD: -₹6,456.29 at base costs and -₹11,148.57 under +50% friction; those are the historical HOLD scenarios published by the source. The ₹20/order HOLD cases are not present in the historical TT-04 summary and are reported as NA, not inferred.
- TT-05 historical HOLD: -₹40,244.68 base; -₹44,082.90 under +50% friction; -₹43,926.28 at ₹20/order; -₹49,605.30 at ₹20/order plus 50% friction.
- The newer partial interval is positive for both candidates in all four registered scenarios. This sign disagreement is temporal instability, not grounds to tune or promote.

## B78-002 — Non-independent windows
- Status: OPEN limitation.
- Phase 51-3 covers 2026-04-21 to 2026-07-21, only a short interval; it does not establish independent long-horizon confirmation. Missing 2026-07-28 and 2026-08-04 expiries remain excluded.

## B78-003 — Initial workflow dependency step
- Status: CLOSED.
- First run 38043179854 failed because `pip install` was invoked without package arguments. No analysis ran and no evidence was accepted. The unnecessary step was removed. Corrected run 38043185158 passed, and the later corrected-format run 38043221791 is the final evidence run.

## B78-004 — Unavailable values incorrectly formatted as NaN
- Status: CLOSED.
- The first report rendered missing historical TT-04 ₹20/order split values as NaN. The source did not provide those split fields; report code now renders them as NA and does not infer values.
