# Phase 94 — Legacy strategy summary-file scan

## Scope and source files
A structural scan of existing canonical summary CSVs on `phase-50b-final-manuscript` found:
- Phase 43 VIX-corrected strategy summary: 58 split rows across 22 strategy labels.
- Phase 45 ready-made strategy/VIX summary: 882 rows across 42 strategy labels, including DEV/VAL/HOLD and VIX subgroups.
- Phase 48 multi-expiry summary: 72 rows across 3 strategy labels.

These files are historical experiment outputs and may share data, rule families, or source lineages; their rows must not be pooled as independent samples. Phase 45 includes a `defined_risk` field and labels `batman` as not defined-risk. Its base net was positive in DEV (+₹59,680), VAL (+₹47,906) and HOLD (+₹88,237), but that is not enough for promotion because the result is not defined-risk and this older VIX table is not the later Phase 50B preregistered all-cost + Holm promotion gate. It must not be described as a validated live strategy.

The Phase 43 split summaries demonstrate strong temporal instability for many structures. Examples include `call_backspread` with +₹32,861 DEV, -₹19,537 VAL, and -₹102,130 HOLD, and `bull_put_credit` with +₹4,592 DEV, -₹34,654 VAL, and -₹28,454 HOLD. Several rows have positive HOLD after negative DEV or VAL; selecting them after looking at the HOLD would create selection bias.

All three Phase 48 multi-expiry candidates in the inspected summary have negative net P&L in DEV, VAL and HOLD:
- `covered_call_2_static_proxy`: -₹16,310 / -₹94,279 / -₹76,397
- `double_calendar_straddle`: -₹89,022 / -₹335,933 / -₹168,062
- `monthly_wide_range_static`: -₹41,142 / -₹224,168 / -₹87,173

## Decision
These older summaries expand the historical inventory but do not change the terminal conclusion: **no strategy is promoted**. Do not rank across phases without verifying the precise run/version, shared source rows, cost model, position sizing, execution assumptions, and whether the split is a protected holdout. The later Phase 50B statistical gate is the more explicit source for its own frozen candidate set and found no robust-positive strategy. The Phase 83 protected 2026 holdout remains sealed.
