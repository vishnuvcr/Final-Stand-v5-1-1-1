# Research Log

## 2026-10-02 — Phase 1 specification review
- Inspected existing repository artifacts.
- Confirmed the intended selector is the maximum X across all 20 candidates: n=6..15 × Call/Put.
- Removed an unintended stop-loss research phase.
- Locked exits to 90% of initial credit or 0 DTE/expiry.
- Locked initial credit to X × actual lot quantity.

## 2026-10-02 — Phase 2 start
- Created dedicated branch: phase-2-primary-backtest.
- Replaced the prior OTM6/7/8-only implementation with a full n=6..15 implementation.
- Added global maximum-X selection across calls and puts.
- Added candidate-level output so all 20 X candidates can be audited per expiry.
- Added date-aware NIFTY weekly lot sizes for the 2024–2025 primary sample.
- Added a manual GitHub Actions workflow and Hugging Face cache.
- Primary data source provenance and limitations are documented in the README and research plan.
- Backtest execution is pending workflow completion.
