# Phase 31 Status

**Status: COMPLETE — REJECTED**

Phase 31 tests asymmetric entry-referenced combined short-leg delta target/stop rules, including the requested 0.25 target / 1.50 stop specification.

Workflow: `.github/workflows/phase-31-asymmetric-delta-exit.yml`.


## Result
GitHub Actions run 37229448057 completed successfully. Delta coverage was 99.21%. The training-selected asymmetric rule was target 0.50 / stop 2.50 / confirmation 1, but it remained strongly inferior to the frozen canonical strategy in validation and holdout.

The specifically requested **target 0.25 / stop 1.50** rule was tested. With one-minute confirmation its full-sample P&L was ₹47,165.60 versus ₹138,937.12 for the no-stop comparator, a −₹91,771.52 difference. Three-minute confirmation produced ₹50,129.82, still −₹88,807.30.

**Decision: reject Phase 31; Phase 20 remains canonical.**
