# Phase 112 Error / Limitation Log

Append all errors and scientific limitations. Record fix commits and re-run results; do not erase earlier failures. Never store tokens or raw credential-bearing responses.

## E112-001 — Signal library parity
- Issue: supplied Pine imports DevLucem/ZigLib/1, but the function body is not embedded.
- Impact: all inherited entry results remain a causal Python proxy, not a verified byte-for-byte indicator strategy.
- Mitigation: fixed rule inherited from Phase 111 and no parameter tuning; keep limitation prominent in all conclusions.
- State: OPEN.

## E112-002 — Historical source sample is incomplete
- Phase 111's first full replay found 259 scheduled, 142 eligible, 121 excluded and only one eligible 2026 holdout campaign.
- Impact: potential selection bias and low holdout power.
- Mitigation: keep exact exclusion ledger; present split-specific coverage and uncertainty; no promotion on a sparse holdout.
- State: OPEN.


## E112-003 — Stop threshold scale was too aggressive for some normalized metrics (observed result, not patched)
- Finding: on the validation split, all registered standalone Vega and Rho threshold variants triggered in 100% of campaigns; their primary-case net P&L was -₹3,186.70 and paired uplift vs no-stop was -₹14,041.57. Gamma thresholds 0.05 and 0.10 also triggered in over 95% of validation campaigns.
- Impact: these registered stop rules frequently cut positions early and were harmful in this sample.
- Disposition: no thresholds were altered after seeing outcomes. The same validation dataset must not be reused for threshold fishing; any alternative scale would require a separately preregistered future phase and independent untouched evaluation sample.
- State: Logged; no same-sample correction permitted.

## Final run disposition — workflow 40072066860
- Compile/tests/replay all passed; 259 scheduled / 139 eligible / 124 excluded; 72 candidates × 24 costs × 3 splits = 5,184 rows.
- No Greek stop candidate is promoted. Main scientific limitations remain E112-001 (ZigLib parity) and E112-002 (partial source/low holdout coverage).
