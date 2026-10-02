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

## 2026-10-02 — Phase 2 execution environment limitation
- The GitHub connector can create/update the manual workflow but does not expose workflow dispatch/write actions or a repository-wide Actions-run listing in this session.
- Direct container internet access is unavailable, so the Hugging Face dataset cannot be downloaded locally.
- The Phase 2 code is therefore committed and auditable, but no new full-sample performance result is claimed from this session.

## 2026-10-02 — Phase 2 methodology correction
- Corrected NIFTY lot-size mapping using NSE's expiry-specific transition: 25 remained for weekly expiries through 19-Dec-2024; 75 began with the 02-Jan-2025 weekly expiry. cite source recorded in external research notes
- Corrected workflow to manual-only to prevent self-triggering when the workflow commits result files.
- Enabled optional use of the repository HF_TOKEN secret for authenticated/bulk Hugging Face downloads; anonymous access remains valid for public data.
