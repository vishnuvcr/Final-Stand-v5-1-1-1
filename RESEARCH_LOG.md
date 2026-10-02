# Research Log

## 2026-10-02 — Phase 1 specification review
- Inspected the existing Phase 1 branch and prior research artifacts.
- Confirmed the intended selector is the maximum X across all 20 candidates: n=6..15 × Call/Put.
- Corrected the specification to remove an earlier, unintended stop-loss research phase.
- Locked the primary exit rules to: 90% of initial credit, otherwise 0 DTE/expiry.
- Locked the credit calculation to X × actual lot quantity.
- Preserved a separate gross-vs-net accounting layer for costs and slippage.
- n=15 requires OTM17 data.

## 2026-10-02 — Phase 1 status
- Strategy definition: COMPLETE after correction.
- Data validation: IN PROGRESS.
- Phase 2 implementation: NOT STARTED on its dedicated branch.
