# Phase 53 — Free-Source Option Data Coverage and Execution-Quality Audit

**Branch:** phase-53-free-option-data-coverage-remediation  
**Parent:** Phase 52 factor-conditioned strategy discovery  
**Status:** ACTIVE — source-access and coverage audit, no strategy ranking  
**Created:** 2026-10-10  
**Research mode:** data engineering and source validation only; no new P&L optimization, no holdout access.

## 1. Why this phase exists

Phase 52's frozen 40-configuration × 24-event baseline pilot reconciled to 480 rows: 379 rows fail the preregistered 2% OHLC high-low/open proxy; 100 rows fail prior-minute open-interest (OI) eligibility with observed OI = 0; one row executed. One negative modeled trade is not a profitability sample. The frozen filter will not be relaxed. The immediate question is whether other lawful, accessible data sources can establish contract-level coverage and, separately, genuine quote quality.

This phase is a source and data-readiness gate, not a strategy test. The existing Phase 52 cohort and exclusions are a fixed audit cohort only. It cannot consume or tune on the 2026 holdout.

## 2. Research questions

RQ53.1 Can the pinned market-data revision reproduce all selected expiry partitions, exact timestamps and required contract keys with deterministic hashes?

RQ53.2 Are the 100 missing/zero prior-OI failures caused by genuinely absent/zero OI in the pinned source, ingestion/normalization errors, or a contract/date mismatch?

RQ53.3 What share of each event/configuration row has a valid exact entry bar, an exact prior completed-minute OI bar, and the exact 15:15 exit bar after duplicate/conflict screening—without nearest-strike selection, interpolation, forward fill, or timestamp substitution?

RQ53.4 Do any freely accessible exchange sources provide intraday contract bars or bid/ask/depth observations for the same historical contract, strike, and timestamp? Which free sources offer only daily aggregates and therefore cannot repair intraday option liquidity?

RQ53.5 Can an independent free dataset be validated as genuinely independent (source revision, lineage, matching-file/sample hashes, schema, licensing), rather than a mirror of the existing source?

RQ53.6 If true quote data are not available freely, can the Phase 52 OHLC proxy still be used only as an explicitly labeled conservative research filter while recognizing that it is not a quoted spread or executable fill?

## 3. Aims and objectives

**Aim:** establish a reproducible, legally acceptable and sufficiently complete data foundation for a later factor-conditioned options-strategy replay.

Objectives:
1. Inventory sources, fields, sampling interval, licensing/access requirements, data provenance and supported uses.
2. Verify the pinned Hugging Face dataset revision and all selected expiry partitions, record file hashes/metadata, distinguish missing files from inaccessible APIs.
3. Reconcile the source row counts before and after exact whole-row duplicate normalization; retain all conflicting rows and fail closed on ambiguous exact contract bars.
4. Measure exact contract-time coverage for index entry, option entry, strictly prior one-minute OI, exact 15:15 exit, and where available bid/ask prices/quantities and market depth.
5. Audit official NSE and BSE free reports for daily contract prices/OI, participant-level positioning and FII/FPI summaries, without treating daily data as intraday OI.
6. Audit public GitHub sources carefully: differentiate sample files and MIT-like code from the actual full licensed dataset; flag any API that requires an exchange/brokerage account and credentials.
7. Preserve the old 2% OHLC proxy as an immutable reference result. If actual quote data become available, register a separate execution-quality rule and compare in a later phase.
8. Publish a source matrix, deterministic JSON result, row-level CSV audit, error records and a go/no-go decision; no strategy selection here.

## 4. Hypotheses

- H0-A (coverage): the current free pinned source does not supply enough eligible selected contract rows to support defensible 40×24 performance inference under the frozen gates.
- H1-A (coverage remediation): one or more independent, legally usable public sources materially increase exact-key prior-OI and entry/exit coverage without imputation.
- H0-B (execution-quality): publicly accessible sources do not provide timestamp-aligned historical bid/ask/depth observations at adequate coverage for these selected option rows.
- H1-B (execution-quality): a public source can provide those quote/depth fields and be verified independently against official reports.

These hypotheses are evaluated using source inventory and coverage counts, not profitability or p-values. No inference on H0/H1 is allowed until coverage is demonstrably paired and independently verified.

## 5. Source search and triage

Priority order:
1. **Pinned HF source** (thetrademarkk/india-index-options-1m, revision 0f4800e43e6f96cec0794369d78eb4d3c4211ef5): primary exploratory intraday one-minute OHLCV+OI source, declared CC BY-NC 4.0. Full-data use is limited by license; no commercial/live inference. Compare any updated or mirrored copy at the file level.
2. **NSE official free reports**: F&O UDiFF common bhavcopy, NCL/combined OI, participant-wise OI/trading volumes, and FII derivatives statistics. These are valuable daily controls/aggregate positioning sources, but must not be described as 1-minute option quotes. Use EOD records only at known publication time for EOD-conditioned factors.
3. **BSE official historical derivatives pages/files**: historical contract price/OI fields, FII/FPI summaries and file-format documentation. Establish whether access is genuinely free and whether it offers daily trade/settlement data versus quote/depth streams. BSE's market-data product/contract feeds may be paid; exclude paid feeds from a free-source path.
4. **OptionVault public GitHub repository** (QuantDev-stack/OptionVault): public code and sample files only. The repository README says the full 300+ GB data are for licensed users; do not mislabel the samples or code as free full historical data.
5. **Breeze options pipeline** (mukhilj/breeze_options_pipeline): public downloader code, but it requires an ICICI Direct account, API key, and fresh session. Treat as credentialed broker API—not an anonymous free public dataset. Do not use or request credentials in this phase.
6. Search further public GitHub, Kaggle and Hugging Face repositories only if exact downloadable files, licensing, schema and provenance can be verified. Do not infer data access from project descriptions, notebooks, generated/synthetic bars or repository stars.

## 6. Scientific methodology

### 6.1 Freeze the cohort and keys
Use the 480 event/configuration rows from the matching v0.2 artifact/manifest and the same 40 configuration IDs, 24 event IDs, development/validation partition, entry times and expiry mapping. Preserve run-version identifiers. Holdout remains untouched. The v0.1 result is not overwritten as if it were v0.2.

### 6.2 Source and revision inventory
For every source record its exact URL/repository, revision or report date, licensing terms, access requirements, expected granularity, required fields, observed schema, file count/size, SHA-256/LFS object hash where available, and whether evidence is direct or merely documentation. Timeouts, 403s and undocumented access are UNKNOWN/INACCESSIBLE, not MISSING_DATA.

### 6.3 Contract-time integrity
Use strict exact timestamps in Asia/Kolkata and full contract identity (underlying, expiry, option type, strike). Separately count:
- source file absent or unreadable;
- index entry not exact;
- option entry absent, invalid, conflicting or duplicate exact rows;
- prior completed-minute OI absent, null, zero, below 100, conflicting, or valid;
- range proxy fail with exact high, low, open and ratio;
- exit bar absent, invalid, conflict, or valid;
- bid/ask/depth absent or aligned and valid, where truly sourced.

Only fully identical rows may be removed after documented canonical normalization. Never average conflicting values. Never fill OI by previous-day/EOD data, nearest strike, forward fill, interpolation or later observations.

### 6.4 OHLC and quote semantics
Calculate (high-low)/open*100 only as the pre-registered OHLC range proxy and keep the threshold at 2% in Phase 52. This proxy is not bid-ask spread. Quote spread is (ask-bid)/mid*100 only with timestamp-aligned positive bid/ask and a defined mid; retain bid/ask sizes and stale-quote flags where provided. Execution scenarios in later phases must include both marketable and conservative fills if such data exist.

### 6.5 Factor alignment
Daily NSE/BSE OI, FII/FPI participation, daily volatility, global-market inputs, gold and cross-asset variables may be considered in future factor features only with explicit information availability timestamps. They must not be forward-filled into earlier intraday decisions before the data could be known. Option Greeks must be exchange-sourced or reproducibly derived using contemporaneous IV/rates/dividends and documented assumptions; vendor labels are not ground truth.

### 6.6 Coverage and statistical methods
Primary outputs are denominators, coverage ratios and reason-level counts by source × expiry × event × option type × offset × split, with Wilson 95% confidence intervals for simple coverage rates when the sample definition is fixed. Where two sources support the exact same contract/timestamp, report paired agreement/missingness and discrepancy distributions; use McNemar only for truly paired binary coverage, and Bland–Altman/absolute-error summaries only for numeric values with comparable definitions. Do not use significance tests to turn source checks into profitability evidence. Any later strategy comparisons require a separately registered development/validation design, multiple-testing control, bootstrap confidence intervals, drawdown/risk metrics and net-of-cost P&L.

## 7. Cost, risk and operational controls

No trades are promoted in this phase. Later replay must preserve Paytm Money brokerage cases (₹10 and ₹20 per executed order scenarios until account-specific tariff is independently confirmed), statutory/exchange charges, STT, stamp duty, SEBI/IPFT levies, GST, adverse slippage, spread/impact costs where measured, expiry/settlement treatment, lot size, rejected/unfilled legs and stress scenarios. Cost assumptions must be versioned and frozen before outcome evaluation.

No secret or credential is logged. HF_TOKEN may be used only for the already-configured public/research-source download if required, never printed. Do not store raw licensed market data in Git; persist metadata, hashes, manifests, aggregate coverage and audit artifacts only.

## 8. Acceptance gates and bounded stopping rule

G0 — **Workflow and reproducibility:** unit tests pass; source manifest and report schema validate; report includes UTC timestamp and revision/URL provenance.

G1 — **Pinned dataset coverage:** at least 12 pilot expiry paths are individually checked at pinned revision and file hashes are reported where accessible. Failure is recorded per path, not hidden.

G2 — **Row integrity:** 480 rows reconcile to exactly one first-failure status each; row identity hashes match the frozen cohort. Zero silent drops or imputation. Any ambiguous contract-time row remains blocked.

G3 — **Source independence/legal status:** full data file—not merely a wrapper/sample—must be retrievable at an explicit source and revision with a usable license. Mirrors are considered independent only after provenance and content hashes are compared.

G4 — **Actual execution-quality data:** to claim true spread/depth validation, timestamp-aligned bid/ask and/or depth must exist for the same contract rows. If no free source provides it, record a source no-go and keep the OHLC proxy clearly labeled.

G5 — **Coverage threshold for a later P&L phase:** preregister before replay a target of at least 80% of the 480-row cohort meeting exact entry/prior-OI/exit gates, with at least 70% coverage in each split and no single family/event leakage. The target is a decision rule for data adequacy, not a reason to relax gates. If unmet, stop the historical replay route and propose only legally appropriate data options.

Stop after source inventory, coverage comparison, and a documented go/no-go. Do not continually broaden sources without bound. This phase does not access holdout and does not test or rank strategies.

## 9. Deliverables

- PHASE53_DATA_SOURCE_MATRIX.md and the machine-readable research/phase53/sources.json
- deterministic results/phase53/source_coverage_audit/report.json
- exact path inventory / per-expiry coverage report and immutable source hashes where accessible
- PHASE53_RESEARCH_LOG.md, PHASE53_STATUS.md, PHASE53_ERROR_LOG.md, PHASE53_CHAT_LOG.md
- a main README link, workflow artifact, and Phase 54 recommendation based on a bounded source go/no-go
- at the eventual end of overall research, consolidated structured manuscript with methods, results, tables/figures, limitations, appendices and supplements.

## 10. Starting source references

- NSE all derivatives reports: https://www.nseindia.com/all-reports-derivatives
- NSE EOD historical subscription page: https://www.nse.in/static/market-data/eod-historical-data-subscription
- BSE derivatives file format: https://www.bseindia.com/downloads1/File_Format_Equity_Derivatives.pdf
- BSE historical FII/FPI summary: https://www.bseindia.com/markets/Derivatives/DeriReports/FIISummaryHistorical.aspx
- HF dataset: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- OptionVault: https://github.com/QuantDev-stack/OptionVault
- Breeze API pipeline: https://github.com/mukhilj/breeze_options_pipeline


### PA-020 — 2026-10-10 — Extended source triage and correct partial-inventory semantics

**New candidates examined (metadata/documentation only; no raw bars downloaded):**

1. rissin/nse-options-intraday includes 1-minute Upstox OHLC for NIFTY/BANKNIFTY/SENSEX from Oct 2024 plus daily EOD data, but its public README explicitly says intraday OI and settlement are NaN and the HF license is “other”. It may only challenge OHLC values on overlapping dates after licensing and lineage clearance; it does not repair Phase52's prior-minute OI requirement.
2. artist-23/nifty-options-data advertises a 34M-row timestamped OHLC/IV/OI dataset. Displayed columns expose only expiry_type/strike_type, not a direct expiry-date field; no explicit license is shown and the viewer shows extreme negative volume and extreme outliers. Hold blocked until license, complete raw schema, expiry join, provenance and numeric validation are solved.
3. codepyx23/india-index-options-1m looks like a mirror/derivative of the pinned TradeMarkk source. It is not independent until identical expiry-file hashes and provenance show otherwise.
4. Zenodo NIFTY 1-minute data covers 2017–2020 and lists OHLC/volume but no OI in its description. It does not cover the Phase52 cohort sampled from 2021 onward.
5. SauMStats/nifty-options-data-engine exposes a code interface, not the external Kaggle raw file archive; its README says market price is close price and bid/ask are unavailable. The Kaggle object URL, license and actual data were not verified, so code is not counted as a source.
6. NSE's visible option-chain page is a current snapshot, not verified historical snapshots; the site places conditions on copying/aggregation. The automated probe is disabled for this endpoint. No scraping or copying.
7. Commercial sources OptionsData.Shop and MoneyTicks are potential procurement leads, not free sources. No purchase is authorized. A minute-bar/OI product would still not satisfy historical bid/ask/depth unless its schema proves it.

**Report correctness fix:** HF direct HEAD requests all returned HTTP 200 for the 13 exact pinned paths, and the exact revision API agrees with SHA 0f4800e43e6f96cec0794369d78eb4d3c4211ef5. The repository tree API uses paginated folder listings. The report now follows Link rel=next metadata pages, records listing_complete, and calls paths absent from a partial tree response “not listed in returned metadata,” never “missing files.” Direct HEAD status takes precedence for path existence. It also skips automated HTTP retrieval of the current NSE option-chain page.

**Phase gate remains unchanged.** No candidate has proven licensed, exact prior-minute OI coverage plus actual bid/ask/depth at adequate overlap. No broad replay begins. Continue the bounded source metadata audit until pagination/tests pass; record a source no-go if the gates cannot be satisfied without paid data or credentials.


### PA-021 — 2026-10-10 — Final Phase53 gate

The final successful source-audit run is 37986608468. It verified the pinned revision, all 13 exact source paths and a complete paginated repository listing (267 option files + 3 index files). A direct metadata ETag comparison found the codepyx23 alternative identical to the pinned dataset on all 13 paths, so it is not independent. The rissin HF alternative documents intraday OI as NaN and shows an “other” license; artist-23 lacks an explicit license in API metadata and exact expiry identity in the viewer schema; Zenodo describes 2017–2020 OHLC/volume rather than OI; public source wrappers and commercial feeds are not free full-history market data. The NSE live option-chain probe stays disabled to respect anti-aggregation terms.

**Phase53 exit condition:** PASS for a reproducible source metadata inventory; NO-GO for independent free intraday prior-OI plus quote/depth input. Phase53 closes without a larger strategy replay. The next bounded phase is Phase54 OHLC-reference sensitivity, a separately preregistered non-executable model that clarifies the OHLC-range proxy is not a spread, preserves exact prior-minute OI and exact exit gates, models all six brokerage/statutory-cost/slippage scenarios, and cannot promote a live strategy. If results remain cost-negative or fail the coverage gate, conclude no evidence supports deployment and issue a manuscript-ready no-go result. Holdout remains untouched.
