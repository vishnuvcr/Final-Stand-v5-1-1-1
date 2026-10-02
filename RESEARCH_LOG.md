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
- Corrected NIFTY lot-size mapping using NSE circulars FAOP64625/FAOP64672: 25 remained for weekly expiries through 19-Dec-2024; 75 began with the 02-Jan-2025 weekly expiry.
- Corrected workflow to manual-only to prevent self-triggering when the workflow commits result files.
- Enabled optional use of the repository HF_TOKEN secret for authenticated/bulk Hugging Face downloads; anonymous access remains valid for public data.

## 2026-10-02 — Multi-year data acquisition expansion
- Expanded the Phase 2 default sample from 2024–2025 to 2021–2026-09-30.
- Identified a public Zenodo one-minute NIFTY options dataset covering 2017–2020 as a possible pre-2021 extension; it is not yet merged because schema/contract coverage must be validated first.
- Recorded additional paid/claimed sources for possible cross-validation in DATA_ACQUISITION.md.
- Corrected the lot-size model for the expanded period: 75 before the Aug-2021 weekly transition, 50 thereafter until Apr-2024, 25 from May-2024, 75 from Jan-2025, and 65 from Jan-2026.

## 2026-10-02 — Configuration verification
- Re-read the executable and workflow after the multi-year edit.
- Found stale fallback dates in the first edit; corrected them to 2021-01-01 through 2026-09-30.
- Bumped the Hugging Face Actions cache key to v3 so the expanded acquisition is isolated from the earlier 2024–2025 cache generation.

## 2026-10-02 — Weekly-era source audit
- Confirmed NIFTY weekly options began in February 2019; 2017–2018 cannot be included in the exact weekly-options strategy.
- Expanded the intended compatible research window to approximately Feb-2019 through Sep-2026.
- Added a manual Zenodo acquisition/validation workflow for the 2019–2020 supplement.
- Corrected the backtest to rank ATM/OTM strikes only from prices available at the 10:00 entry timestamp, preventing strike-list look-ahead.
- Restricted the expiry set by excluding the final expiry date of each month, which represents the monthly expiry and avoids mixing it into the weekly-only sample.
- Corrected the NIFTY 65-lot transition to the first revised weekly expiry, 06-Jan-2026.

## 2026-10-02 — Repository persistence verification
- The first attempt to persist DATA_ACQUISITION.md and Zenodo documentation was not present in the branch tree during re-audit.
- Restored both files and verified their presence through the branch tree before continuing.

## 2026-10-02 — Final Phase 2 acquisition preparation
- Current target is the compatible weekly-options era: Feb-2019 through Sep-2026.
- The 2019–2020 Zenodo source has a manual cached acquisition/validation workflow; 2017–2018 is excluded from this strategy.
- Primary backtest now uses entry-time strike availability and excludes monthly expiry dates from the weekly sample.
- No performance result is promoted to the research conclusions until the multi-year workflow has actually executed successfully.
