## Phase 52 resumed — next gates (2026-10-10)

OpenChart investigation is closed at the user's request; its source audit remains in the branch history and no further requests are planned. Research resumes on the frozen Phase 52 pilot: repair checkpoint persistence, then decompose the 480 status rows (379 OHLC-range exclusions, 100 leg-eligibility blocks, one execution) and trace dominant exclusions to exact source rows/contracts/timestamps. Do not treat exclusions as losses or relax filters to increase trade count. No strategy is promoted and holdout remains untouched.

- [Phase 52 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_RESEARCH_PLAN.md)
- [Phase 52 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_STATUS.md)
- [Phase 52 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md)

# Latest research checkpoint — 2026-10-10

## Phase 52 bounded historical pilot v0.2 — replay complete, insufficient coverage

[Workflow 37980455805](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805) completed replay and status reconciliation for 40 configurations × 24 development/validation events = 480 planned configuration-event rows: 379 failed the frozen OHLC-range proxy, 100 were blocked by leg eligibility, and one executed. Thirteen source files had zero read errors; six cost-scenario rows were emitted for the one executed row. The final checkpoint-persistence step failed due conflicts in shared status/research/chat logs. **This is not a usable profitability sample; no strategy is ranked or promoted; holdout remains untouched.**

- [Pilot run summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/historical_pilot/v0.2-run-37980455805-summary.json)
- [Pilot audit note](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/historical_pilot/v0.2-run-37980455805-audit.md)
- [Phase 52 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md)

## OpenChart source feasibility — runtime probe NOT ACCEPTED (2026-10-10)

[Final bounded Actions run 37982673873](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37982673873) completed successfully as a workflow. Its six symbol-query variants all returned the same 20 Index rows; none yielded an option or future, and no historical option-bar request could be issued. The NSE homepage request returned HTTP 403 while the charting symbol search returned HTTP 200. The current wrapper is therefore **not accepted for acquiring all options data**; direct-token historical retrieval remains untested.

- [Phase 52 OpenChart audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_OPENCHART_AUDIT.md)
- [Aggregate-only runtime report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/openchart_probe/runs/37982673873/probe_report.json)
- [Phase 52 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_STATUS.md) · [error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md)

---

## Phase 51-1J — Free-source recovery audit

A public Hugging Face dataset, [thetrademarkk/india-index-options-1m](https://huggingface.co/datasets/thetrademarkk/india-index-options-1m), lists both missing NIFTY files: [2026-07-28](https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/commit/dbc0596) and [2026-08-04](https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/commit/51ca58c). The metadata-only audit [run 37916601582](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37916601582) downloaded both files, but both were stale: timestamps ended on 2026-07-02 and each contained zero rows on its named target session. This source is rejected for the missing dates despite its filenames and expiry metadata.
- [Free-source plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/PHASE51_1J_FREE_SOURCE_PLAN.md) · [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/PHASE51_1J_STATUS.md) · [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/PHASE51_1J_ERROR_LOG.md)
- Raw files will not be committed to the public repository. No P&L or strategy promotion until provenance, exact contract coverage and data-integrity gates pass.

---

## Phase 51-1J — TradingTick public-source audit (CLOSED / INSUFFICIENT)

**Terminal audit:** [GitHub Actions run 37915320571](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37915320571) succeeded on 2026-10-09. This is a successful audit workflow but a negative source-eligibility result for intraday replay.

- The public TradingTick pages loaded, and 2026-07-28 was selectable, but the observed payloads did not provide verified intraday timestamps/series.
- 2026-08-04 was not listed in the audited selectors. This does not exclude a separate paid/private archive.
- **No TradingTick P&L was calculated; no strategy was promoted.** Phase 51 full-window OOS remains data-blocked pending authorized, timestamped, contract-complete data for 2026-07-28 and 2026-08-04.
- [Phase 51-1J branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-51-1J-tradingtick-source-audit)
- [Final report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/results/phase51/phase51_1J_tradingtick/REPORT.md)
- [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/PHASE51_1J_STATUS.md) · [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/PHASE51_1J_ERROR_LOG.md) · [Chat log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/PHASE51_1J_CHAT_LOG.md)

---

**Next authorized-data candidate:** [Options Data NIFTY 1-minute options catalog](https://optionsdata.shop/data/nifty-options-historical-data) advertises OHLCV + OI for all traded strikes through October 2026, with a 2026 calendar-year options pack listed at ₹2,999. The free sample is only 15–17 September 2026 and does not prove the two missing sessions exist in the selected pack. This is an independent vendor, not exchange-affiliated; no bid/ask or Greeks are included. [Vendor feasibility addendum](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1J-tradingtick-source-audit/results/phase51/phase51_1J_tradingtick/VENDOR_FEASIBILITY_ADDENDUM.md). **No purchase made**; exact target-date/contract coverage and licence/storage terms must be confirmed before acquisition. Raw licensed files must not be published to the public repo unless explicitly permitted.


# Final Stand v5 1-1-1-1 — Latest Research Checkpoint (2026-10-09)

## Phase 51 full-window OOS — DATA-BLOCKED (freshness re-audit 2026-10-09)

The latest raw-byte re-audit [run 37912433753](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37912433753) reconfirmed that the public Hugging Face option files named for expiries 2026-07-28 and 2026-08-04 still end on 2026-07-02. The files' hashes/sizes were unchanged from the previous audit; neither contains its target trading session. **No full-window OOS P&L was calculated.**

- [Phase 51-1H status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1H-current-hf-byte-validation/PHASE51_1H_STATUS.md)
- [Phase 51-1H error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1H-current-hf-byte-validation/PHASE51_1H_ERROR_LOG.md)
- [Upstox expired option-candle API](https://upstox.com/developer/api-documentation/get-expired-historical-candle-data/) (requires authorized Plus access)
- [Potential vendor archive: NIFTY 1-minute full chain](https://optionsdata.shop/data/nifty-options-historical-data) (paid; not purchased)

The remaining blocker is access to an accepted raw archive or authorized API credentials. No synthetic prices, forward fills, shortened OOS windows or strategy promotion are allowed.

---

## Phase 51-3 — CLOSED: PASS_AVAILABLE_OOS (partial diagnostic only)

Authoritative source-faithful replay completed successfully in [GitHub Actions run 37882057283](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37882057283). The frozen primary options object passed SHA-256/byte-size verification; the validated spot source covered 2026-04-21 09:15 through 2026-07-21 15:29 IST (23,625 observations), and 14 weekly expiries were derived from the primary option records. The eligible candidate set was TT-02, TT-04 and TT-05; all had 100% recorded execution coverage and zero row-level data errors.

| Strategy | Trades | Net ₹10/order | Net +50% friction | Net ₹20/order | Net ₹20/order +50% |
|---|---:|---:|---:|---:|---:|
| TT-02 | 13 | -₹1,341.12 | -₹2,936.31 | -₹3,701.12 | -₹6,476.31 |
| TT-04 | 62 | +₹13,271.51 | +₹10,287.26 | +₹10,345.11 | +₹5,897.66 |
| TT-05 | 62 | +₹17,098.15 | +₹14,239.72 | +₹14,171.75 | +₹9,850.12 |

**Interpretation:** TT-04 and TT-05 were positive under the four registered cost/friction scenarios in this short interval; TT-02 was negative. These are descriptive partial-OOS results only. **No strategy is promoted** and no parameter tuning or confirmatory hypothesis test was run.

The complete preregistered Phase-51 OOS window remains **2026-04-21 through 2026-08-04**. Option blocks for **2026-07-28 and 2026-08-04 remain unresolved**, so this phase does not establish full-window performance or justify live deployment.

- [Phase 51-3 final report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-3-available-data-strategy-sweep/results/phase51/available_oos/PHASE51_3_AVAILABLE_OOS_REPORT.md)
- [Sweep summary JSON](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-3-available-data-strategy-sweep/results/phase51/available_oos/sweep_summary.json)
- [Phase 51-3 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-51-3-available-data-strategy-sweep)
- [Phase 51-3 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-3-available-data-strategy-sweep/PHASE51_3_STATUS.md)
- [Phase 51-3 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-3-available-data-strategy-sweep/PHASE51_3_ERROR_LOG.md)
- [Phase 51-3 chat log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-3-available-data-strategy-sweep/PHASE51_3_CHAT_LOG.md)
- [Phase 51-3 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-3-available-data-strategy-sweep/PHASE51_3_RESEARCH_PLAN.md)

---
## Phase 51-1I — CLOSED / DATA-BLOCKED

The preregistered authorized-access recovery route was executed automatically.

Credential inventory found **no configured authorized API credentials** for:
- Upstox
- Dhan
- ICICI Breeze

No secret values were exposed and no unauthorized access was attempted.

The frozen Phase-51 OOS window remains **2026-04-21 → 2026-08-04**. The missing option blocks remain **2026-07-28 and 2026-08-04**.

**No OOS P&L has been calculated from incomplete data.**

- [Phase 51-1I branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-51-1I-authorized-access-recovery)
- [Phase 51-1I status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1I-authorized-access-recovery/PHASE51_1I_STATUS.md)
- [Phase 51-1I error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1I-authorized-access-recovery/PHASE51_1I_ERROR_LOG.md)
- [Authorized recovery Actions run 37876882587](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37876882587)

### Current blocking condition

An authorized raw-data route is now the only blocking dependency. The existing workflow is ready to execute the frozen Upstox acquisition automatically when `UPSTOX_ACCESS_TOKEN` is configured, followed by the existing source-equivalence and replay-coverage gates.

An authorized OptionsData.shop archive/API export would also be acceptable under the preregistered gate.

**No strategy tuning, source selection by expected P&L, OOS-window shortening, synthetic prices or forward filling is permitted.**

---

# Final Stand v5 1-1-1-1 — Latest Research Checkpoint (2026-10-09)

## Phase 51-1H — CLOSED / DATA-BLOCKED

A final live-byte audit was executed against the current public Hugging Face NIFTY options repository for the unresolved Phase-51 expiries **2026-07-28** and **2026-08-04**.

The files are real Parquet objects and their schema is canonically mappable, but both terminate on **2026-07-02**, so neither contains the required target trading session.

| Target | Size | Rows | Actual end | Decision |
|---|---:|---:|---|---|
| 2026-07-28 | 3,990,663 B | 320,359 | 2026-07-02 15:30 IST | REJECT |
| 2026-08-04 | 58,248 B | 2,646 | 2026-07-02 15:29 IST | REJECT |

No OOS P&L was calculated and the frozen 2026-04-21 → 2026-08-04 window was not shortened.

StockMock and StockMojo were also checked as independent historical-option research/oracle platforms. Their public materials describe minute-level historical replay/backtesting, but no reproducible raw archive suitable for repository ingestion was established, so neither replaces the raw-data gate.

- [Phase 51-1H report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1H-current-hf-byte-validation/results/phase51/PHASE51_1H_CURRENT_HF_REPORT.md)
- [Phase 51-1H manifest](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1H-current-hf-byte-validation/results/phase51/PHASE51_1H_CURRENT_HF_MANIFEST.json)
- [Phase 51-1H status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1H-current-hf-byte-validation/PHASE51_1H_STATUS.md)
- [Phase 51-1H error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1H-current-hf-byte-validation/PHASE51_1H_ERROR_LOG.md)
- [Accepted audit run 37876719483](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37876719483)

**Next:** preregistered authorized-data recovery, beginning with a non-secret credential-presence check for Upstox/Dhan/ICICI routes. No P&L or parameter tuning is permitted until the raw-data gate passes.

---

# Final Stand v5 1-1-1-1 — Latest Research Checkpoint (2026-10-09)

## Phase 50B-6 — CLOSED / NO PROMOTION

Phase 50B-6 performed the preregistered dependence-aware validation inference for frozen OTM350 versus fixed BASE.

**Primary result:** 76 validation expiry blocks; mean OTM350 minus BASE = **−₹73.88** per expiry; 95% paired-bootstrap CI **−₹282.26 to +₹149.36**; one-sided expiry-block sign-flip p = **0.7386**. OTM350 beat BASE on **10/76** expiry blocks; BASE won **66/76**.

All registered cost variants remained unfavorable to OTM350:
- +50% stress: mean difference −₹73.03; p = 0.7375
- ₹20/order: mean difference −₹73.88; p = 0.7409
- ₹20/order +50% stress: mean difference −₹73.03; p = 0.7381
- Holm-adjusted secondary p-values: 1.0000

The 2026 HOLD was protected and unused for selection or inference.

**Decision: OTM350 is rejected as an improvement. BASE remains the canonical TT-03 control within this research chain. No further far-OTM tuning is permitted from this result.**

- [Phase 50B-6 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-6-statistical-inference)
- [Phase 50B-6 preregistration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-6-statistical-inference/PHASE50B_6_PREREGISTRATION.md)
- [Phase 50B-6 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-6-statistical-inference/PHASE50B_6_RESEARCH_PLAN.md)
- [Phase 50B-6 final report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-6-statistical-inference/results/phase50b/PHASE50B_6_FINAL_REPORT.md)
- [Phase 50B-6 statistical endpoints](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-6-statistical-inference/results/phase50b/phase50b6_inference/statistical_endpoints.csv)
- [Phase 50B-6 pairing diagnostics](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-6-statistical-inference/results/phase50b/phase50b6_inference/pairing_identity_diagnostics.csv)
- [Phase 50B-6 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-6-statistical-inference/PHASE50B_6_STATUS.md)
- [Phase 50B-6 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-6-statistical-inference/PHASE50B_6_ERROR_LOG.md)
- [Accepted statistical Actions run 37851668489](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37851668489)

## Phase 50B-4 — CLOSED / FROZEN CANDIDATE

Phase 50B-4 completed the preregistered TT-03 far-OTM geometry comparison. OTM350 and OTM400 both passed 99.50% coverage and zero-data-error feasibility gates. OTM350 won the preregistered within-mutation development gate with DEV +50% stress net ₹32,213.01 versus ₹14,511.75 for OTM400.

**Important:** BASE remained economically stronger. OTM350 was frozen as a candidate for statistical comparison, not promoted over BASE.

- [Phase 50B-4 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-4-far-otm-geometry)
- [Phase 50B-4 final report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-4-far-otm-geometry/results/phase50b/PHASE50B_4_FINAL_REPORT.md)

---


## Phase 50B-4 — Far-OTM Geometry — ACTIVE (2026-10-09)

Phase 50B-3 closed without promoting a VIX regime. The next finite preregistered step is testing only the TT-03 natural strike-distance mutations **OTM350 (350/400/450)** and **OTM400 (400/450/500)** against the accepted **BASE (300/350/400)** control.

Selection is frozen: an OTM mutation must pass >=95% coverage, positive DEV net and positive DEV +50% cost-stress net; if both qualify, the higher DEV +50% DEV-stress net is selected. Validation and protected 2026 HOLD are post-selection.

- [Phase 50B-4 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-4-far-otm-geometry)
- [Phase 50B-4 preregistration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-4-far-otm-geometry/PHASE50B_4_FAR_OTM_PREREGISTRATION.md)
- [Phase 50B-4 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-4-far-otm-geometry/PHASE50B_4_STATUS.md)

## Phase 50B-3 — VIX Conditioning — ACTIVE (2026-10-09)

Phase 51 remains blocked at the full-window data gate because the audited primary option source ends at 2026-07-21 and the 2026-07-28/2026-08-04 endpoint blocks remain unresolved. The non-confirmatory Phase-51-2 partial audit found no eligible TT-03 campaigns under its frozen three-calendar-day entry rule, so no economic inference was made.

The bounded Phase-50B research is therefore continuing on its own preregistered finite chain. TT-02, TT-03, TT-04 and TT-05 passed the 95% feasibility gate; TT-06 and TT-07 are terminal coverage failures and are excluded from downstream VIX analysis.

Phase 50B-3 freezes **28 strategy×VIX hypotheses** (four feasible strategies × LOW/NORMAL/HIGH/SPIKE/FALLING/RISING/HIGH_RISING), using **entry-time VIX only**. 2026 HOLD is descriptive and protected from selection/inference. No VIX threshold or strategy parameter is being tuned.

- [Phase 50B-3 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-3-vix-conditioning)
- [Phase 50B-3 preregistration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-3-vix-conditioning/PHASE50B_3_VIX_PREREGISTRATION.md)
- [Phase 50B-3 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-3-vix-conditioning/PHASE50B_3_RESEARCH_PLAN.md)
- [Phase 50B-3 literature review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-3-vix-conditioning/PHASE50B_3_LITERATURE_REVIEW.md)
- [Phase 50B-3 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-3-vix-conditioning/PHASE50B_3_STATUS.md)

## Phase 51 — CURRENT RESEARCH STATUS: FULL-WINDOW DATA AVAILABILITY STOP

**Latest authoritative status (2026-10-09): full Phase-51 economic OOS validation remains blocked.**

The frozen OOS window remains **2026-04-21 through 2026-08-04**. The primary NIFTY 1-minute options source stops at expiry **2026-07-21**; the tested public augmentation did not satisfy the registered endpoint/common-expiry quality gates for **2026-07-28** and **2026-08-04**; the authenticated Upstox recovery path is blocked by the missing **UPSTOX_ACCESS_TOKEN** secret.

### Phase 51-2 partial-data audit result

A separate, explicitly non-confirmatory Phase-51-2 branch audited the currently complete endpoint **2026-04-21 through 2026-07-21**.

The frozen Phase-51-1 source record contains **14 observed expiries, all Tuesdays**. The frozen TT-03 rule requires entry exactly **three calendar days before expiry**. Every scheduled entry date therefore falls on Saturday, leaving **0 eligible campaigns** for both frozen TT-03 BASE (300/350/400) and TT-03 OTM350 (350/400/450).

Therefore:
- **0 trades**
- **0 candidate campaigns**
- **No P&L evidence**
- **No statistical inference**
- **No promotion decision**

This is a calendar/protocol outcome, **not** evidence that TT-03 is profitable or unprofitable. No strategy rule was changed, and the full Phase-51 window was not shortened.

Authoritative Phase-51 files:
- [Phase 51 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1-cost-data-calibration/PHASE51_RESEARCH_PLAN.md)
- [Phase 51 source-gate report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1-cost-data-calibration/results/phase51/PHASE51_1_SOURCE_GATE_REPORT.md)
- [Phase 51-1 structured decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-1-cost-data-calibration/results/phase51/phase51_1_source_gate_final.json)
- [Phase 51-2 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-51-2-available-data-partial-oos)
- [Phase 51-2 report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-2-available-data-partial-oos/results/phase51/PHASE51_2_PARTIAL_OOS_REPORT.md)
- [Phase 51-2 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-2-available-data-partial-oos/results/phase51/PHASE51_2_PARTIAL_OOS_STATUS.md)
- [Phase 51-2 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-51-2-available-data-partial-oos/results/phase51/PHASE51_2_ERROR_LOG.md)
- [Phase 51-2 final Actions run 37847094909](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37847094909)
- [Authenticated Upstox recovery branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-51-1C-authenticated-options-acquisition)

**Phase 51-3 through 51-6 are not advanced from this partial audit.** A calendar-normalized three-trading-day interpretation, if researched, must be separately pre-registered as a new strategy specification rather than inserted into Phase 51.

---

## Phase 50B — Current research status (2026-10-07)

**TT-03 V5: PASS. TT-04: RUNNING. No strategy promoted.**

Phase 50B is the finite research extension testing the user's supplied Tradetron strategies and prior strategy lineages under common chronological replay, broker-realistic costs, VIX conditioning and protected holdout rules. The isolated research branch is [phase-50b-expanded-strategy-universe](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-expanded-strategy-universe).

- TT-03 V5 run [37620274641](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37620274641): **PASS**, 200/201 complete campaigns (99.50%), 1 coverage exclusion, 1 session exclusion, zero data errors.
- TT-03 accepted baseline cost outputs: **₹89,669.15 / ₹82,074.11 / ₹75,509.15 / ₹60,834.11** for ₹10/order, +50% stress, ₹20/order, and ₹20/order +50% stress respectively. These are not a promotion decision.
- TT-04 V3 run [37621965843](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37621965843) is **running** after successful preflight and dependency validation.
- Current research chain: **TT-04 → TT-05 → TT-06 → TT-07 → statistical inference → finite VIX/far-OTM variants → chronological validation → protected 2026 holdout → final decision/manuscript**.

See the [Phase 50B branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-expanded-strategy-universe), [status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-expanded-strategy-universe/PHASE50B_STATUS.md), [research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-expanded-strategy-universe/PHASE50B_RESEARCH_PLAN.md), [chat log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-expanded-strategy-universe/PHASE50B_CHAT_LOG.md), and [error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-expanded-strategy-universe/ERROR_LOG.md).

## Phase 50B — User + Prior-Repository Strategy Integration — INITIALIZED

Phase 50B adds the seven user-supplied Tradetron strategies and relevant prior strategy lineages discovered in the user's GitHub repositories to the VIX/far-OTM research. It is isolated from Phase 50A so earlier numerical evidence remains frozen.

- [Phase 50B branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-user-and-repo-strategy-integration)
- [Strategy registry](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-user-and-repo-strategy-integration/PHASE50B_STRATEGY_REGISTRY.md)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-user-and-repo-strategy-integration/PHASE50B_RESEARCH_PLAN.md)
- [GitHub repository audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-user-and-repo-strategy-integration/PHASE50B_GITHUB_REPO_AUDIT.md)

# Final Stand v5 1-1-1-1

Systematic options-strategy research repository.

## Phase 41 — Regime-conditional counterfactual policy learning — COMPLETE / NO PROMOTION

Phase 41 completed on isolated branch phase-41-regime-conditional-policy-learning.

| Metric | Result |
|---|---:|
| Declared variants | 24 |
| Validation-eligible variants | 0 |
| Fixed-panel validation uplift of frozen candidates | ₹0 |
| Fixed-panel 2026 holdout uplift of frozen candidates | ₹0 |
| Sequential validation uplift | ₹0 |
| Sequential 2026 holdout uplift | ₹0 |
| Holdout overrides | 0 |
| Paired-expiry p-value | 1.0000 |
| Promotion | **NO — canonical strategy unchanged** |

All three frozen diagnostic candidates were proven to be exact no-op policies: zero overrides across development, validation and holdout. Their sequential replay is therefore identical to the canonical stateful benchmark.

An important secondary finding is that the model score still ranked economically favorable counterfactual states. For the leading rank-1 policy, the top 10% of validation scores had mean observed CALL-minus-PUT advantage of **+₹2,502.61** (95% bootstrap CI **+₹425.31 to +₹4,688.79**). The 2026 holdout top 10% mean was **+₹7,338.85** (95% CI **+₹2,593.35 to +₹9,856.56**). This is a ranking signal, not a tradable result, because the registered uncertainty gate produced zero overrides and the independent expiry-level trading uplift remained exactly zero.

India VIX is therefore retained as a regime/routing research variable, not a promoted direct directional predictor.

- [Phase 41 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-41-regime-conditional-policy-learning)
- [Phase 41 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-41-regime-conditional-policy-learning/PHASE41_MANUSCRIPT.md)
- [Phase 41 pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-41-regime-conditional-policy-learning/PHASE41_PRE_REGISTRATION.md)
- [Phase 41 final decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-41-regime-conditional-policy-learning/results/phase41_regime_policy/final_decision.json)
- [Phase 41 workflow run 37466520042](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37466520042)

## Latest research status

**Dynamic-n corrected primary research is complete. Stop-loss research is complete through Phase 19.**

### Locked dynamic-n primary

- 190 trades
- Net P&L: **₹138,937.12**
- Net win rate: **94.21%**
- 178 target exits
- 12 expiry exits
- 11 losing trades, all expiry exits
- Maximum drawdown: **₹27,321.08**

Controlled n-selection ablation showed that the 95%-band dynamic-n preference did **not** add incremental aggregate P&L versus fixed n=6 on the same trade universe: fixed n=6 returned ₹139,543.97 versus ₹138,937.12 for dynamic n.

### Stop-loss research

Phase 17 tested 108 pre-registered hard, expiry-day, stagnation, trailing and combined stop rules. No rule both preserved all baseline-positive trades and improved validation P&L.

Phase 18 and Phase 19 tested a narrower expiry-day conditional stop. The final **research candidate for paper/forward validation** is:

> **At 13:30 IST on expiry day, exit all three legs when combined strategy MTM is negative and running MFE since entry is below 0.50 × the original target.**

Walk-forward results for this candidate:

| Period | Net uplift | Baseline-positive trades affected | Stops |
|---|---:|---:|---:|
| Training through 2023-12-31 | +₹1,963.67 | 0 | 1 |
| Validation 2024-01-01 to 2025-12-31 | +₹1,923.59 | 0 | 2 |
| Holdout 2026-01-01 to 2026-09-30 | +₹6,305.15 | 0 | 2 |
| Full sample | +₹10,192.41 | 0 | 5 |

The candidate changes five exits, all baseline losing trades, and leaves every historically profitable baseline trade untouched. It does **not** eliminate any loss completely; it truncates selected expiry losses earlier.

The formal train-selected 13:30 / MFE < 1.0× rule was **not promoted** because its 2026 holdout maximum drawdown increased materially. The 0.50× version is retained as the more conservative robustness candidate.

The no-stop dynamic-n strategy remains the locked primary until the stop candidate is tested with forward/paper execution and real broker fills.

## Phase artifacts

- Phase 17 stop-loss research: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-17-stop-loss-research
- Phase 18 conditional-stop refinement: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-18-conditional-stop-refinement
- Phase 19 walk-forward confirmation: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-19-stop-walk-forward-confirmation
- Final stop-loss conclusion: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/STOP_LOSS_CONCLUSION.md
- Stop-loss manuscript supplement: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/manuscript/STOP_LOSS_EXTENSION_SUPPLEMENT.md
- Walk-forward report: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-19-stop-walk-forward-confirmation/results/dynamic_n_corrected/phase19_walk_forward/WALK_FORWARD_SUMMARY.md



## Phase 42 — Confidence Calibration and Selective Counterfactual Routing — COMPLETE

Accepted workflow: **37470344620**.

Phase 42 screened **72 preregistered** combinations of two frozen economic-margin learners, four calibration modes, three economic margins and three India-VIX routing gates.

Only two policies passed the development/validation selection gate. The primary frozen policy was **SPLINE_RIDGE_VIX + RAW score + ₹500 margin + ALL routing**.

| Metric | Validation | 2026 holdout |
|---|---:|---:|
| Sequential uplift vs canonical control | **+₹26,542.28** | **+₹20,607.09** |
| Overrides | 43 | 8 |
| 95% paired-expiry CI for mean uplift | **−₹634.82 to +₹1,335.41** | **−₹2,020.42 to +₹4,297.35** |
| One-sided sign-flip p | **0.2654** | **0.3054** |

The second frozen policy, **EXTRATREES_VIX + RAW + ₹250 + ALL**, produced **−₹23,919.81 validation uplift** and **+₹42,514.83 holdout uplift**, indicating substantial policy instability.

All ROBUST_MAD and CONFORMAL_80/90 variants produced zero overrides. This suggests the uncertainty/calibration layer can suppress a potentially informative ranking signal, but the RAW score remains statistically inconclusive.

**Decision: NO PROMOTION. The canonical stateful strategy remains unchanged.**

The complete Phase-42 branch, manuscript, grid, sequential replay and error log are retained on branch `phase-42-confidence-calibration-abstention`.

## Research governance

All previous superseded dynamic-n numerical results remain marked as obsolete. Execution errors and corrections are logged in `ERROR_LOG.md`; research-phase progress is tracked in `RESEARCH_LOG.md`; the research protocol is maintained in `DYNAMIC_N_RESEARCH_PLAN.md`.

**Phase 19 is the final stop-loss research phase under the current plan.**


## Latest completed phase — Phase 20

Phase 20 compared entry-time payoff-chart/green-area boundary stops against the fixed expiry-day conditional stop.

The boundary family tested 0/50/100/200/400 NIFTY-point buffers, 1/3-minute confirmation, and boundary/MTM/MFE variants. The training-safe selector was 400 points with 1-minute confirmation, but it lost **₹14,390.87** in 2024–2025 validation and **₹49,064.48** in the 2026 holdout, while materially worsening drawdown. Therefore **no payoff-boundary stop is included**.

The fixed Phase-19 comparator was independently reconstructed and cross-checked:
- 13:30 IST on expiry day;
- combined three-leg MTM < ₹0;
- running MFE < 0.50× original target.

Walk-forward uplift: +₹1,963.67 training, +₹1,923.59 validation, +₹6,305.15 holdout, +₹10,192.41 full sample, with zero baseline-positive trades affected.

### Final entry-to-exit rules

The final historical rules are recorded on the Phase-20 branch:
- [Final strategy rules](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/FINAL_STRATEGY_RULES.md)
- [Final strategy specification](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/STRATEGY_SPEC.md)
- [Phase 20 supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/manuscript/PHASE20_PAYOFF_BOUNDARY_SUPPLEMENT.md)
- [Phase 20 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-20-payoff-boundary-stop-research/results/dynamic_n_corrected/phase20_payoff_boundary/BOUNDARY_STOP_CONCLUSION.md)

Final historical result over 190 corrected trades:
- Net P&L: **₹149,129.53**
- Mean net/trade: **₹784.89**
- Net winning trades: **179/190 (94.21%)**
- Profit factor: **2.34**
- Maximum cumulative drawdown: **₹27,336.11**
- Target exits: **178**
- Conditional-stop exits: **5**
- Expiry-fallback exits: **7**

This is historical research evidence, not a guarantee of future or live performance. Forward/paper execution validation remains separate from the historical research.

## Phase 21 status — pre-expiry risk-control research

Phase 21 is being evaluated on isolated branch `phase-21-pre-expiry-adverse-move-risk-control`. It tests bounded early exits and one-lot OTM-(n+3) tail-hedge repairs against the frozen Phase-20 strategy. The canonical strategy remains unchanged unless the pre-registered walk-forward promotion screen is passed.


## Phase 21 final status — pre-expiry adverse-move control

Phase 21 is complete. The pre-registered 200–600 point direction-aware early-exit and one-lot OTM-(n+3) hedge families produced **no candidate that satisfied the training safety constraint of zero profitable baseline trades affected**. The closest candidate (600-point / 1-minute / spot-only early exit) improved training by ₹1,885.47 but lost ₹33,923.36 in 2024–2025 validation and ₹44,039.53 in the 2026 holdout, while full-sample maximum drawdown rose to ₹52,740.01. **No Phase-21 rule is promoted; the Phase-20 final strategy remains the canonical historical specification.**

Phase-21 research files are isolated on branch `phase-21-pre-expiry-adverse-move-risk-control` and draft PR #2.


## Phase 23 final status — entry-filter research

Phase 23 tested BULLISH-only entry filters after Phase 22 found that all 11 historical losses were in the BULLISH/put structure, while all 18 BEARISH/call trades were profitable. The BULLISH subgroup also contained 161 winners, and no pre-registered BULLISH-only filter could remove at least two training losses while retaining 95% of winners and improving training P&L. The top unconstrained diagnostic (BULLISH direction margin ≥ 0.15) removed 12 winners and only 1 loss and was strongly negative out of sample. **No entry filter is promoted; the Phase-20 strategy remains canonical.**

Phase 23 artifacts are isolated on branch `phase-23-conditional-bullish-entry-filter` and draft PR #4.

## Phase 22 final status — entry-filter research

Phase 22 tested pre-entry filters using payoff-buffer geometry, direction confidence, structure quality and pre-entry NIFTY regime. **No candidate passed the pre-registered safety screen.** No tested filter removed even one training loss without also removing a profitable training trade. The Phase-20 canonical strategy therefore remains unchanged.

See the Phase-22 draft PR and branch for the complete grid and manuscript supplement.


## Final research closeout — Phase 24 complete

The preregistered research phases are complete. Phase 23 and Phase 24 did not produce an out-of-sample improvement that passed the registered promotion gates. The **Phase-20 canonical dynamic-n strategy remains the final historical entry-to-exit specification**.

Final historical result: **190 trades, ₹149,129.53 net P&L, 179/190 profitable trades (94.21%), profit factor 2.34, maximum drawdown ₹27,336.11** under the research execution-cost model.

- [Final strategy rules](FINAL_STRATEGY_RULES.md)
- [Final strategy specification](STRATEGY_SPEC.md)
- [Final research manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/manuscript/FINAL_RESEARCH_MANUSCRIPT.md)
- [Phase 23 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/results/dynamic_n_corrected/phase23_entry_state/PHASE23_CONCLUSION.md)
- [Phase 24 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/results/dynamic_n_corrected/phase24_targeted_reversal/PHASE24_CONCLUSION.md)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-24-targeted-reversal-trigger/DYNAMIC_N_RESEARCH_PLAN.md)
- [Error log](ERROR_LOG.md)

## Phase 25 — alternative direction chooser

Phase 25 tested alternative option-price, IV, OI/volume, NIFTY and cross-market direction choosers while holding the rest of the final strategy fixed. **No alternative passed the preregistered training/OOS gates; OTM6/7/8 remains the direction chooser.**

- [Phase 25 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-25-direction-chooser-alternatives/results/dynamic_n_corrected/phase25_direction_chooser/PHASE25_CONCLUSION.md)
- [Phase 25 manuscript supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-25-direction-chooser-alternatives/manuscript/PHASE25_DIRECTION_CHOOSER_SUPPLEMENT.md)

## Phase 27 — Delta-based exit research — COMPLETE

Phase 27 tested portfolio-delta-based profit booking and adverse-delta stops against the locked Phase-20 strategy. Delta coverage was **99.21%**. The training-selected rule (MTM ≥ 0.90×target and |portfolio delta| ≤ 0.05) produced **−₹2,334.04** validation uplift and **−₹1,108.04** 2026 holdout uplift. The holdout bootstrap 95% CI for mean trade-level uplift was **−₹141.92 to −₹13.82**. **No delta exit is promoted; Phase-20 remains canonical.**

- [Phase 27 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-27-delta-exit-research)
- [Phase 27 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-27-delta-exit-research/PHASE27_STATUS.md)
- [Phase 27 supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-27-delta-exit-research/manuscript/PHASE27_DELTA_EXIT_SUPPLEMENT.md)

## Phase 28 — individual-leg delta research — COMPLETE

Phase 28 directly tested **per-leg delta**, especially the short OTM-(n+1) and OTM-(n+2) legs, rather than portfolio delta. The Phase-20 strategy remained frozen as control.

- Delta coverage: **99.21%**.
- Training-selected rule: S1 |delta| ≤ 0.05 after MTM ≥ 90% of target.
- Training uplift: **−₹2,998.16**.
- 2024–2025 validation uplift: **−₹2,487.05**.
- 2026 holdout uplift: **−₹35.91**.
- Full-sample uplift: **−₹5,521.12**.
- No adverse short-leg delta stop was promoted.

**Decision: reject individual-leg absolute-delta exit rules. Phase-20 remains canonical.**

- [Phase 28 pre-registration](PHASE28_PRE_REGISTRATION.md)
- [Phase 28 status](PHASE28_STATUS.md)
- [Phase 28 supplement](manuscript/PHASE28_INDIVIDUAL_LEG_DELTA_SUPPLEMENT.md)
- [Phase 28 results](results/dynamic_n_corrected/phase28_leg_delta_exit/)


## Phase 29 — short-leg delta-change exit research — COMPLETE / REJECTED

Phase 29 tested the requested exit mechanism: target and stop entirely from individual or combined short-leg delta change, with the target-percentage criterion removed. No portfolio-delta or absolute-delta level trigger was used.

- Delta coverage: **99.21%**
- Selected target: **MEAN short-leg delta change, 5-minute lookback, 0.20 threshold, 3-minute confirmation**
- Selected stop: **S1 short-leg delta change, 1-minute lookback, 0.05 threshold, 3-minute confirmation**; zero uplift
- Versus canonical Phase 20: **−₹1,092.14 validation** and **−₹6,879.84 2026 holdout**
- **Decision: NO PROMOTION. Phase 20 remains canonical.**

Artifacts: [Phase 29 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-29-delta-change-exit-research) · [status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-29-delta-change-exit-research/PHASE29_STATUS.md) · [manuscript supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-29-delta-change-exit-research/manuscript/PHASE29_DELTA_CHANGE_SUPPLEMENT.md) · [conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-29-delta-change-exit-research/results/dynamic_n_corrected/phase29_delta_change_exit/PHASE29_CONCLUSION.md)


## Phase 30 — corrected entry-referenced delta-proportion research — OPEN

A new isolated research phase was registered after correcting the intended delta definition. Phase 30 uses the **sum of the two short-option deltas at entry** as the fixed reference and measures later movement as a **proportion of that entry value**. It does not use prior-minute lookbacks, delta differences, or a mean of the short legs.

- [Phase 30 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-30-entry-delta-proportion-exit)
- [Phase 30 pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/PHASE30_PRE_REGISTRATION.md)
- [Phase 30 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/PHASE30_STATUS.md)

The numerical phase remains open pending successful GitHub Actions execution. No result is inferred from workflow-dispatch unavailability.


## Phase 30 — COMPLETE / REJECTED

Phase 30 tested entry-referenced proportional movement in the combined absolute delta of the two short option legs. GitHub Actions execution completed successfully (run 37228084351), with 99.21% delta coverage. The training-selected rule failed both validation and 2026 holdout against the frozen Phase-20 canonical strategy and is rejected.

- [Phase 30 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-30-entry-delta-proportion-exit)
- [Phase 30 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/PHASE30_STATUS.md)
- [Phase 30 conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-30-entry-delta-proportion-exit/results/dynamic_n_corrected/phase30_entry_delta_proportion_exit/PHASE30_CONCLUSION.md)


## Phase 32 — Continuous Delta 6x6 Vertical Spread — COMPLETE / NO PROMOTION

Phase 32 independently tested the frozen Continuous Delta 6x6 Vertical Spread strategy on NIFTY 50.

- [Phase 32 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-32-continuous-delta-6x6-backtest)
- [Final manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-32-continuous-delta-6x6-backtest/manuscript/PHASE32_CONTINUOUS_DELTA_MANUSCRIPT.md)
- [Conclusion](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-32-continuous-delta-6x6-backtest/results/dynamic_strategy_phase32/PHASE32_CONCLUSION.md)
- [Results index](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-32-continuous-delta-6x6-backtest/results/dynamic_strategy_phase32/PHASE32_RESULTS_INDEX.md)
- [Frozen rule card](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-32-continuous-delta-6x6-backtest/results/dynamic_strategy_phase32/PHASE32_STRATEGY_RULES.md)
- [Literature supplement](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-32-continuous-delta-6x6-backtest/results/dynamic_strategy_phase32/PHASE32_LITERATURE_REVIEW.md)
- [Final figures](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-32-continuous-delta-6x6-backtest/results/dynamic_strategy_phase32/figures/PHASE32_FIGURES.svg)
- [Final GitHub Actions run #41](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37388261915)

Headline result: **478 trades, ₹83,820.48 net P&L, 63.60% win rate, 1.112 profit factor, ₹94,492.83 maximum drawdown.** The classification is **PROMISING BUT INSUFFICIENTLY ROBUST**. The result is not promoted because the source has material expiry gaps, mean-trade inference includes zero, performance is regime-dependent, and four ticks of modeled slippage eliminate the edge. **Phase-20 remains canonical.**




## Phase 33 — NIFTY D−6 prediction models — COMPLETE / NO PROMOTION

Phase 33 tested LSTM, GARCH/EGARCH/GJR-GARCH, sentiment-augmented SOFNN-inspired fuzzy learning, Random Forest and a fixed equal-weight ensemble using the exact **10:00 IST / six-calendar-days-before-expiry** reference.

**Final result: no model is promoted to trading.** There were 245 eligible events: 128 development, 95 validation and 22 untouched 2026 holdout. Random Forest was strongest on validation (54.74% accuracy; 0.6851 log loss). The 2026 ensemble reached 59.09% accuracy, but the simple always-down baseline reached 63.64%; all model signed-return bootstrap intervals included zero. GARCH-family volatility correlation with realized absolute return was only 0.066, with QLIKE 66,548.975. **Phase 20 remains canonical.**

- [Phase 33 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-33-nifty-prediction-models)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/PHASE33_RESEARCH_PLAN.md)
- [Pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/PHASE33_PRE_REGISTRATION.md)
- [Final status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/PHASE33_STATUS.md)
- [Data dictionary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/PHASE33_DATA_DICTIONARY.md)
- [Literature review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/results/phase33_nifty_prediction/PHASE33_LITERATURE_REVIEW.md)
- [Final manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/results/phase33_nifty_prediction/PHASE33_NIFTY_PREDICTION_MANUSCRIPT.md)
- [Statistical summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/results/phase33_nifty_prediction/PHASE33_STATISTICAL_SUMMARY.csv)
- [Decision table](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/results/phase33_nifty_prediction/PHASE33_DECISION_TABLE.csv)
- [GARCH summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-33-nifty-prediction-models/results/phase33_nifty_prediction/PHASE33_GARCH_SUMMARY.json)
- [Final figures](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-33-nifty-prediction-models/results/phase33_nifty_prediction/figures)
- [Final postprocess Actions run #4](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37422362350)

The full manuscript records methodology, leakage controls, statistical tests, strengths, limitations and future research. Any future use of RF/ensemble as a direction chooser requires a new registered phase with the established Paytm Money transaction-cost and slippage model.


## Phase 34 — Alternative NIFTY D−6 prediction models — COMPLETE / NO PROMOTION

Phase 34 tested eight additional forecasting families beyond Phase 33: **XGBoost, ExtraTrees, HistGradientBoosting, RBF-SVM, Elastic-Net Logistic Regression, a point-in-time HMM regime model, a compact Transformer and a compact temporal-convolution model**, plus fixed equal-weight ensembles. The reference remained exactly **10:00 IST on six calendar days before NIFTY expiry**, with the same 245-event point-in-time universe used in Phase 33.

**Final decision: no Phase-34 model is promoted to trading. Phase 20 remains canonical.** The strongest raw 2026 holdout accuracy was **68.18%** from ExtraTrees and the equal-weight-8 ensemble, but the holdout contains only 22 events and the uncertainty/promotion gates were not all passed. XGBoost was the strongest new model on validation at **57.89% accuracy**. Tree-equal-3 achieved the strongest new-family holdout log loss at **0.6350**. HistGradientBoosting produced the most notable signed-return diagnostic (**0.00832; 95% bootstrap CI 0.00138–0.01534; sign-flip p=0.0363**) but only tied the always-down baseline on directional accuracy. No candidate passed all preregistered gates.

- [Phase 34 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-34-alternative-nifty-prediction-models)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/PHASE34_RESEARCH_PLAN.md)
- [Pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/PHASE34_PRE_REGISTRATION.md)
- [Final status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/PHASE34_STATUS.md)
- [Literature review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/results/phase34_alternative_prediction/PHASE34_LITERATURE_REVIEW.md)
- [Final manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/results/phase34_alternative_prediction/PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md)
- [Statistical summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/results/phase34_alternative_prediction/PHASE34_STATISTICAL_SUMMARY.csv)
- [Decision table](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/results/phase34_alternative_prediction/PHASE34_DECISION_TABLE.csv)
- [Results index](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/results/phase34_alternative_prediction/PHASE34_RESULTS_INDEX.md)
- [Accuracy figure](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/results/phase34_alternative_prediction/phase34_accuracy_comparison.svg)
- [Signed-return figure](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-34-alternative-nifty-prediction-models/results/phase34_alternative_prediction/phase34_holdout_signed_return_ci.svg)
- [Accepted numerical Actions run #2](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37422865721)
- [Accepted postprocess Actions run #7](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37423631294)

Any future use of HistGradientBoosting, ExtraTrees or an ensemble as a direction chooser requires a new registered overlay phase with complete Paytm Money brokerage/statutory charges, slippage, execution/fill constraints and expiry-gap handling.


## Phase 35 — advanced tree and adaptive prediction search — RESEARCH REGISTRATION

A deeper literature search was completed after Phase 34, with **tree-based models retained as the core family**. The search identified several stronger unexplored directions: **LightGBM, CatBoost, DART, NGBoost, BART, quantile-boosting trees, wavelet/EMD/VMD decomposition followed by trees, adaptive rolling tree models, leakage-safe OOF stacking, dynamic ensemble selection, regime-gated trees, forecast pooling/winsorization, and calibration/conformal uncertainty layers**.

The immediate numerical priority is LightGBM + CatBoost + DART, followed by probabilistic/quantile tree models, decomposition-enhanced trees, adaptive tree retraining, and leakage-safe tree stacking. The recently published NIFTY MS-Beta-t-QVAR work is being treated as a regime/volatility gate rather than a stand-alone directional model. The numerical phase and addenda are completed in the final section below; this section records the original registration rationale.

- [Phase 35 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-35-advanced-tree-and-adaptive-prediction-search)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/PHASE35_RESEARCH_PLAN.md)
- [Pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/PHASE35_PRE_REGISTRATION.md)
- [Literature review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/PHASE35_LITERATURE_REVIEW.md)
- [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/PHASE35_STATUS.md)


## Phase 35 — Advanced NIFTY Prediction Model Search — COMPLETE / NO PROMOTION

Phase 35 exhaustively expanded the D−6 / 10:00 IST NIFTY prediction search while **keeping tree models as the core family**. It tested LightGBM, CatBoost, DART, XGBoost, ExtraTrees, HistGradientBoosting, equal/winsorized tree pooling, RFE-LightGBM, NGBoost, quantile trees, BART, wavelet/EMD/VMD/CEEMDAN tree models, adaptive rolling/weighted trees, dynamic pooling, chronological OOF stacking, probability calibration, conformal uncertainty, and a reproducible Markov-switching volatility-gate proxy.

**Final decision: no model is promoted to live trading.** There were 245 eligible events: 128 development, 95 validation and 22 untouched 2026 holdout. The strongest Phase-34 validation benchmark was 57.89% accuracy; no Phase-35 method exceeded it. Several models reached 68.18% holdout accuracy, and OOF stacking produced the strongest holdout signed-return diagnostic (+0.00951; 95% bootstrap CI +0.00255 to +0.01627; sign-flip p=0.0139), but the holdout contains only 22 observations and the signed-return diagnostic is not executable option P&L.

The correct next phase is a **frozen trading-overlay validation**, not another unrestricted model search.

- [Phase 35 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-35-advanced-tree-and-adaptive-prediction-search)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/PHASE35_RESEARCH_PLAN.md)
- [Pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/PHASE35_PRE_REGISTRATION.md)
- [Final status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/PHASE35_STATUS.md)
- [Final manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/PHASE35_FINAL_MANUSCRIPT.md)
- [Final statistical summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/PHASE35_FINAL_STATISTICAL_SUMMARY.csv)
- [Final decision table](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/PHASE35_FINAL_DECISION_TABLE.csv)
- [Calibration diagnostics](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/calibration_diagnostics.csv)
- [Uncertainty summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/uncertainty_summary.csv)
- [Accuracy figure](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/phase35_holdout_accuracy.svg)
- [Signed-return figure](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-35-advanced-tree-and-adaptive-prediction-search/results/phase35_advanced_tree_prediction/phase35_holdout_signed_return.svg)
- [Accepted principal Actions run #5](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37425240176)
- [Accepted Markov addendum Actions run #8](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37426499636)
- [Accepted CEEMDAN addendum Actions run #1](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37426761476)

**Phase 20 remains canonical until a separate overlay phase demonstrates improvement after full Paytm Money brokerage/statutory charges, slippage, execution/fill constraints and expiry-gap handling.**


## Phase 36 — Independent per-trade direction selector overlay

**Status: COMPLETE — REJECTED — NO LIVE-TRADING PROMOTION.**

This phase tested the requested rule change: **the previous trade's status, P&L, win/loss result and prior direction do not determine the next trade's direction**. Every eligible new trade receives a fresh direction decision. All other Continuous Delta 6x6 entry, exit, spread, slippage, brokerage and statutory-cost rules were frozen.

Final numerical evidence: **GitHub Actions 37428502722 (#4)**. A final reproducibility checkpoint, **37429748933 (#18)**, also completed all seven selector jobs and the rebase-safe artifact publication successfully.

Primary window: **2024-01-01 to 2026-06-30**.

| Treatment | Net P&L |
|---|---:|
| Phase-32 stateful control | **+₹63,672.58** |
| OTM789 fresh | -₹39,122.38 |
| DART | -₹54,475.24 |
| OOF stack | -₹59,868.85 |
| OTM678 fresh | -₹62,665.27 |
| Wavelet-tree | -₹66,398.02 |
| Markov-regime tree | -₹88,163.44 |
| CatBoost | -₹92,977.93 |

All seven independent selectors were also negative in the 2026 holdout, while the stateful control was approximately flat at -₹275.65. Per-expiry bootstrap comparisons favored the stateful control for every selector.

**Conclusion:** the independent-direction overlay is rejected. The Phase-32 stateful direction rule remains the canonical strategy. No Phase-36 selector is promoted to live trading.

### Phase 36 artifacts
- [Phase 36 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-36-independent-direction-selector-overlay)
- [Research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-36-independent-direction-selector-overlay/PHASE36_RESEARCH_PLAN.md)
- [Pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-36-independent-direction-selector-overlay/PHASE36_PRE_REGISTRATION.md)
- [Strategy specification](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-36-independent-direction-selector-overlay/PHASE36_STRATEGY_SPEC.md)
- [Final status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-36-independent-direction-selector-overlay/PHASE36_STATUS.md)
- [Final manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-36-independent-direction-selector-overlay/results/phase36_independent_direction/PHASE36_MANUSCRIPT.md)
- [Results index](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-36-independent-direction-selector-overlay/results/phase36_independent_direction/PHASE36_RESULTS_INDEX.md)
- [Phase 36 workflow](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/workflows/phase-36-independent-direction-selector-overlay.yml)

**Next research priority:** forward/paper validation of the canonical stateful strategy with full bid/ask, latency, fill-probability and Paytm Money-specific transaction-cost modeling.


## Phase 37 — corrected model direction polarity — COMPLETE NUMERICAL CORRECTION

**Status: correction validated; no live-trading promotion yet.**

Phase 37 reran the five predictive model selectors after correcting the Phase-36 polarity mismatch. The frozen mapping is **bullish/up probability >= 0.50 -> PUT spread; bearish/down probability < 0.50 -> CALL spread**.

| Selector | Net P&L | PF | Max DD | 2026 holdout |
|---|---:|---:|---:|---:|
| CatBoost | ₹57,874.80 | 1.186 | ₹49,337.02 | ₹49,054.33 |
| Markov-regime tree | ₹53,060.31 | 1.174 | ₹40,547.67 | ₹41,969.35 |
| Wavelet-tree | ₹31,294.89 | 1.100 | ₹54,085.53 | ₹50,776.68 |
| OOF stack | ₹24,765.71 | 1.081 | ₹62,024.82 | ₹48,345.59 |
| DART | ₹19,372.11 | 1.060 | ₹52,629.57 | ₹39,053.96 |

All five corrected selectors are profitable after costs and positive on the 2026 holdout. The Phase-36 model-selector conclusion is therefore invalid for the intended hypothesis because it used the opposite polarity.

**Not yet promoted:** the preregistered common-expiry paired bootstrap versus the canonical stateful control has not yet been regenerated. Phase 38 is required for control-relative statistical robustness, walk-forward validation, CALL/PUT asymmetry, cost/slippage stress and full execution realism.

- [Phase 37 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-37-model-direction-polarity-correction)
- [Phase 37 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-37-model-direction-polarity-correction/PHASE37_MANUSCRIPT.md)
- [Phase 37 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-37-model-direction-polarity-correction/PHASE37_STATUS.md)
- [Phase 37 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-37-model-direction-polarity-correction/PHASE37_RESEARCH_PLAN.md)
- [Phase 37 pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-37-model-direction-polarity-correction/PHASE37_PRE_REGISTRATION.md)
- [Phase 37 results](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-37-model-direction-polarity-correction/results/phase37_model_direction_polarity_correction)


## Phase 38 — corrected model robustness vs stateful control — COMPLETE / REJECTED

Phase 38 tested the five Phase-37 polarity-corrected model direction selectors against the frozen canonical Phase-32 stateful control. The phase used 10,000 deterministic paired expiry bootstrap resamples, 2024/2025/2026 splits, +25/+50/+100% cost stress, and CALL/PUT asymmetry analysis.

**Final result: none of the five selectors is promoted. The canonical stateful direction rule remains unchanged.**

| Selector | Net P&L | 2026 holdout | Mean Δ vs control / expiry | P(selector > control) |
|---|---:|---:|---:|---:|
| CATBOOST | ₹57,874.80 | ₹49,054.33 | -₹200.98 | 37.63% |
| MARKOV_REGIME_TREE | ₹53,060.31 | ₹41,969.35 | -₹252.75 | 34.37% |
| WAVELET_TREE | ₹31,294.89 | ₹50,776.68 | -₹486.79 | 23.19% |
| OOF_STACK | ₹24,765.71 | ₹48,345.59 | -₹557.00 | 20.18% |
| DART | ₹19,372.11 | ₹39,053.96 | -₹614.99 | 18.11% |

All five selectors were positive in the 2026 holdout and at +50% transaction-cost stress, but every paired point estimate favored the control and every bootstrap interval crossed zero. Every selector also showed positive CALL-side P&L and negative PUT-side P&L.

A control-reproducibility discrepancy was detected and logged as F38-001: a fresh Phase-32 reconstruction produced 205 trades / 103 expiries / ₹65,945.47 rather than the frozen canonical 206 / 102 / ₹63,672.58. The frozen canonical artifact is therefore authoritative for Phase-38 treatment comparisons.

- [Phase 38 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-38-corrected-model-robustness)
- [Phase 38 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/PHASE38_STATUS.md)
- [Phase 38 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/PHASE38_MANUSCRIPT.md)
- [Phase 38 paired bootstrap](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/results/phase38_corrected_model_robustness/paired_bootstrap.csv)
- [Phase 38 cost stress](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/results/phase38_corrected_model_robustness/cost_stress.csv)
- [Phase 38 control audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/results/phase38_corrected_model_robustness/control_validation.json)
- [Phase 38 pull request #12](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/pull/12)

**Next research priority:** Phase 39 robustness of the canonical stateful strategy with broker-realistic bid/ask, latency, fill probability, and expanded cost/slippage stress.

### Phase 38 secondary risk-adjusted diagnostic

The cumulative net-P&L / maximum-drawdown ranking is:

1. **MARKOV_REGIME_TREE: 1.309**
2. **CATBOOST: 1.173**
3. **STATEFUL_CONTROL: 1.028**
4. **WAVELET_TREE: 0.579**
5. **OOF_STACK: 0.399**
6. **DART: 0.368**

Markov has the strongest cumulative return-to-drawdown efficiency, but this is only a secondary diagnostic; it does not overturn the preregistered control-relative rejection of all five model selectors.

- [Risk-adjusted summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-38-corrected-model-robustness/results/phase38_corrected_model_robustness/risk_adjusted_summary.csv)


## Phase 39 — advanced and counterfactual direction prediction — INITIALIZED

The previous prediction search was deeper than the Phase-38 summary alone suggests. Phase 35 already tested XGBoost, LightGBM, CatBoost, ExtraTrees, HistGradientBoosting, DART, NGBoost, BART, quantile trees, wavelet/EMD/VMD/CEEMDAN hybrids, adaptive trees, dynamic pools, OOF stacking, calibration, conformal methods and regime-gated trees. Phase 38 then rejected the corrected model selectors relative to the canonical stateful control.

Phase 39 therefore changes the **problem formulation**, not merely the classifier.

### New primary research idea

Instead of predicting NIFTY expiry direction, predict the **counterfactual economic margin between the actual tradable CALL and PUT spreads** at the same entry opportunity:

**DeltaP&L = CALL net P&L − PUT net P&L**

The main invented method is the **Control-Relative Counterfactual Override Learner (CROL)**. The canonical stateful control remains the default action; the model is allowed to override only when predicted incremental P&L and uncertainty satisfy preregistered conditions.

Additional candidate families include Bayesian dynamic models, Bradley-Terry preference learning, Gaussian processes, sparse GAM/GA2M, weighted analog/kNN/DTW methods, Bayesian online change-point gates, online expert aggregation, constrained symbolic regression and a lower-priority time-series foundation-model track.

- [Phase 39 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-39-advanced-direction-models)
- [Phase 39 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-39-advanced-direction-models/PHASE39_RESEARCH_PLAN.md)
- [Phase 39 preregistration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-39-advanced-direction-models/PHASE39_PRE_REGISTRATION.md)
- [Phase 39 literature review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-39-advanced-direction-models/PHASE39_LITERATURE_REVIEW.md)
- [Phase 39 candidate method registry](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-39-advanced-direction-models/results/phase39_candidate_method_registry.csv)
- [Phase 39 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-39-advanced-direction-models/PHASE39_STATUS.md)

**Current Phase-39 status:** formulation and preregistration complete; numerical counterfactual engine construction is next. Phase-38 canonical strategy remains unchanged.


## Phase 43 — VIX-conditioned NIFTY all-strategy sweep — COMPLETE / NO PROMOTION

Phase 43 completed the broad India-VIX-conditioned NIFTY weekly option sweep with realistic costs, chronological validation, multiple-testing correction and protected 2026 holdout. No VIX router passed the registered promotion gates.

- [Phase 43 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-43-vix-all-options-strategies)
- [Phase 43 status](PHASE43_STATUS.md)
- [Phase 43 manuscript](PHASE43_MANUSCRIPT.md)

**Final Phase 43 decision: NO PROMOTION.**

## Phase 44 — VIX candidate tuning — COMPLETE / NO PROMOTION

Phase 44 tuned six defined-risk VIX-conditioned candidate families across finite strike geometry, four entry times and prior-only India-VIX threshold grids. The corrected study used a 13,292-row development structural matrix, 3,500 profile evaluations, 522 development-eligible configurations and 30 frozen validation candidates.

- [Phase 44 branch](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-44-vix-candidate-tuning)
- [Phase 44 manuscript](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/PHASE44_MANUSCRIPT.md)
- [Phase 44 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/PHASE44_RESEARCH_PLAN.md)
- [Phase 44 pre-registration](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/PHASE44_PRE_REGISTRATION.md)
- [Phase 44 literature review](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/PHASE44_LITERATURE_REVIEW.md)
- [Phase 44 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/PHASE44_STATUS.md)
- [Phase 44 final decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/results/phase44_vix_tuning/final_decision.json)
- [Phase 44 validation matrix](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/results/phase44_vix_tuning/validation_confirmation.csv)
- [Phase 44 gate summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/results/phase44_vix_tuning/phase44_gate_summary.csv)
- [Phase 44 candidate funnel](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-44-vix-candidate-tuning/results/phase44_vix_tuning/figures/candidate_funnel.svg)

**Validation result:** 18/30 frozen candidates had positive net P&L; 16/30 remained positive under +50% cost stress; 9/30 had positive total uplift. Zero candidates had a strictly positive 95% CI lower bound, zero had unadjusted p<0.05, and zero survived Holm correction.

**Phase 44 decision: NO PROMOTION.** Stage 3 active-exit tuning was skipped and the 2026 holdout remained protected. The Phase-20/42 canonical strategy remains unchanged.


## Phase 50B current checkpoint — 2026-10-07 18:15 IST
- TT-03 V5 is accepted: 200/201 campaigns, 99.50% coverage, one session exclusion, zero data errors; source-faithful cost outputs are ₹89,669 / ₹82,074 (+50% stress) / ₹75,509 (₹20/order) / ₹60,834 (₹20/order +50% stress).
- TT-04 dedicated run **37621965843** is executing from the corrected V3 engine after TT-03 terminal PASS gating.
- TT-04 remains unaccepted until its exact premium-match replay passes coverage, zero-data-error, and cost-robustness artifact audits.
- No Phase-50B strategy has been promoted.


## Phase 50B — latest research status — 2026-10-07 18:15 IST

Phase 50B remains active on branch [phase-50b-expanded-strategy-universe](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-50b-expanded-strategy-universe).

- **TT-03 V5:** PASS accepted from Actions run **37620274641** — 200/201 complete campaigns, 99.50% coverage, one coverage exclusion, one session exclusion, zero data errors. Source-faithful net results are ₹89,669.15 (₹10/order), ₹82,074.11 (+50% stress), ₹75,509.15 (₹20/order), and ₹60,834.11 (₹20/order +50% stress).
- **TT-04 V3:** Actions run **37621965843** is currently executing the numerical replay after successful preflight, compilation, TT-03 terminal-gate verification and HF-cache setup.
- **Evidence status:** TT-04 is not yet accepted; no downstream statistical inference, tuning, holdout promotion or strategy promotion is being inferred from the in-progress run.
- **Research chain:** TT-04 → TT-05 → TT-06 → TT-07 → protected statistical inference → finite VIX/far-OTM variants → chronological validation → protected 2026 holdout → final decision/manuscript.

[TT-04 current Actions run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37621965843) · [Phase 50B status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-50b-expanded-strategy-universe/PHASE50B_STATUS.md)


## Phase 50B — latest status — 2026-10-07
The accepted TT-03 V5 baseline is complete (200/201 coverage candidates, 99.50%, zero data errors). TT-04 V3 run **37621965843** is currently executing its numerical replay; no TT-04 result is accepted until the full artifact, coverage, zero-error and cost audit passes. No strategy has been promoted.


## Phase 50B — live execution contingency — 2026-10-07
TT-04 V3 remains the active numerical replay. A separate dormant performance-only fallback was prepared but not executed or wired into the workflow; no fallback result is evidence.


## Phase 51-3 — Initial orchestration checkpoint (SUPERSEDED)

This initial setup checkpoint is superseded by the current Phase 51-3 retry status near the top of this README. The first run did start; it failed in TT-02 and its console P&L figures were not accepted as evidence.

## Phase 52 — Factor-Conditioned Strategy Discovery (opened 2026-10-09)

**Branch:** [phase-52-factor-conditioned-strategy-discovery](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-52-factor-conditioned-strategy-discovery)  
**Current state:** OPEN — source-discovery and configuration-queue bootstrap; no Phase 52 profitability result or strategy promotion.

Phase 52 tests whether VIX, Greeks/IV/skew, OI/volume/PCR, spot/futures/synthetic-futures basis, market regimes, liquidity and available cross-market/event context improve *which* option structure/configuration to select or when to abstain. The preregistered matrix contains **312 hypotheses** (52 structure families × 6 selector modes) and a finite, versioned grid. It will enumerate the grid deterministically and preserve all cost scenarios and negative results.

- [Research plan and version amendments](PHASE52_RESEARCH_PLAN.md) — objectives, hypotheses, finite-grid scope, methodology and promotion gates.
- [Phase status and gates](PHASE52_STATUS.md) — current blockers and evidence boundary.
- [312-hypothesis registry](research/phase52/strategy_registry.csv) — structure × selector matrix.
- [Strategy leg specifications](research/phase52/strategy_specifications.csv) — standardized variants and source-reconciliation blockers.
- [Finite configuration grid](research/phase52/configuration_space.json) — `phase52-grid-v1.3`, deterministic search dimensions and Paytm Money cost/stress scenarios.
- [User-repository audit queue](research/phase52/repository_audit.csv) — inventory of all 40 repositories; inventory is not equivalent to a completed source-code audit.
- [Initial literature and source ledger](PHASE52_LITERATURE_REVIEW.md) — papers, NSE data sources, YouTube and public-code leads.
- [Research log](PHASE52_RESEARCH_LOG.md) · [Error log](PHASE52_ERROR_LOG.md) · [conversation/decision log](PHASE52_CHAT_LOG.md).
- [Main-branch scheduled/manual workflow](.github/workflows/phase-52-factor-conditioned-strategy-discovery.yml) — daily at 03:30 UTC (09:00 IST) and manually runnable; uses a bounded configuration shard and source discovery. A scheduled run does not claim P&L.
- [Deterministic registry/grid validator and shard enumerator](research/phase52/validate_registry.py) · [recurring public source discovery](research/phase52/source_discovery.py).

**Important:** The current runner now includes a legacy factor-selector pilot, but not the full Phase52 parameter replay. The pilot's first execution stopped at its self-test before data analysis; the binning test was patched and is awaiting a rerun. All 312 hypotheses remain `REGISTERED_NOT_TESTED` until their applicable structures/configurations receive source-faithful replay. Grid enumeration is not a tested-configuration count. The Phase 51 missing option sessions (2026-07-28 and 2026-08-04) remain unresolved and are not silently filled or excluded from its original full-window claim. No strategy is promoted to live trading by this branch.



### Phase 52 latest checkpoint — 2026-10-09

The first complete GitHub Actions retry succeeded: [run 37924369419](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37924369419). Registry/specification/grid validation passed; 32 unique Hugging Face/GitHub source leads were added; 10,000 of 9,379,584 finite-grid configurations were deterministically enumerated and checkpointed. This is **not** 10,000 backtests. The numerical replay engine and point-in-time data/coverage audit remain not started; no Phase 52 profitability result or strategy promotion exists. Fresh YouTube API discovery is pending an optional `YOUTUBE_API_KEY` secret.


**Latest research checkpoint (2026-10-09):** the first Actions execution passed the registry/grid audit (312 hypotheses; grid v1.3 = 9,379,584 configurations) but stopped before market-data analysis due to a brittle factor-binning self-test. The test was patched before any P&L calculations; the failure is recorded in [F52-005](PHASE52_ERROR_LOG.md). The grid-size feasibility decision is logged as [F52-006](PHASE52_ERROR_LOG.md). A legacy outcome-matrix selector test is the first numerical stage; NIFTY futures basis and true synthetic-future divergence are not present in that seed feature panel and will not be claimed as tested.


### Phase 52 selector screen — current result (2026-10-09)

The corrected recurring workflow completed successfully in [run 37927040268](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37927040268). The point-in-time join matched 6,617 of 9,699 legacy Phase45 trade rows (68.2%). All six development-selected factor policies had negative 2024–25 validation net P&L. The VIX router was least negative at -₹63,547, but its +₹1,411 per-expiry relative stress uplift had a 95% paired block-bootstrap CI of [-₹915,+₹4,290] and Holm-adjusted p=0.985. This is not statistically significant. The 2026 holdout was not evaluated because only 13 expiry observations matched. No selector or strategy is promoted. The 9,379,584 finite-grid configuration queue is still largely queued/enumerated, not backtested.


### Phase 52 latest selector checkpoint (2026-10-09)

The corrected scheduled workflow completed in [run 37927040268](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37927040268). The point-in-time join matched 6,617/9,699 legacy Phase45 trade rows (68.2%). All six development-selected factor policies had negative 2024–25 validation net P&L. The VIX router was least negative at -₹63,547, but its +₹1,411 per-expiry relative stress uplift had a 95% paired block-bootstrap CI [-₹915,+₹4,290] and Holm-adjusted p=0.985. The 2026 holdout was not evaluated because only 13 expiry observations matched, below the preregistered 20-expiry threshold. No selector was promoted. The 9,379,584 finite-grid configurations remain queued/enumerated, not tested backtests.


### Phase 52 base replay and daily factor-source checkpoint (2026-10-09)

The pinned Phase43/45 base-geometry replay completed in [Actions run 37929888516](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37929888516), writing 9,699 outcome rows across 42 strategy labels and 256 expiries through 2026-05-26. It uses `thetrademarkk/india-index-options-1m` at pinned revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`, declared CC BY-NC 4.0, so this result is research-only. The lagged daily NSE bhavcopy supplement built 256/256 EOD factor rows from 512 source archives, with zero missing archive paths, file errors, or gap rows; this is daily EOD, not intraday futures basis. LOW-VIX Bear Call Spread again led validation (₹24,743 net; ₹23,082 legacy 1.5× all-cost stress), but the inherited Phase45 multiple-testing gate had zero Holm-adjusted survivors. The exact-10:00 coverage audit run [37930010915](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37930010915) failed before emitting a coverage result because its script was only on main; the script has now been copied to the Phase52 branch. Full-window coverage remains unverified, and no candidate is promoted.


### Phase 52 option/OI event-coverage gate (2026-10-09)

The configuration-grid preflight completed successfully in [run 37934719402](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37934719402). Across 267 pinned option-expiry files it audited all 1,068 expiry × calendar-DTE {0,7} × exact-entry-time {09:45,13:00} events, with zero source-file errors. There were 1,012 exact NIFTY index entry timestamps, 1,016 events with any option rows at entry, 1,012 with at least one OI≥100 contract, and 1,040 with both option types at a common target-expiry exit timestamp. The strict broad intersection is 1,004/1,068; only 74/112 holdout events meet that broad gate. This is **not** selected-strike/leg validation and no P&L was calculated. The pinned index bars end 2026-07-02 despite option expiry files extending to 2026-08-04; the 2026-07-28 and 2026-08-04 sessions remain unresolved. Grid checkpoint is 235,000/9,379,584 IDs enumerated—not backtested. No strategy is promoted.

Detailed records: [Phase52 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_STATUS.md), [research log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_RESEARCH_LOG.md), [error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md), [event audit summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/option_quote_coverage/summary.json), [event-level CSV](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/option_quote_coverage/entry_exit_quote_coverage.csv).


### Phase 52 selected-strike preflight (2026-10-09; verification pending)

Because broad event coverage is not proof that the configured strikes can trade, a stricter audit was added to the scheduled/manual workflow. It checks exact entry/exit OHLC and OI≥100 for CE/PE strike ranks -6 through +6 around nearest ATM, with pinned file hashes; it produces coverage diagnostics only and does not calculate P&L. The self-test and first full run are pending. Absolute-delta strike configurations remain blocked until a validated point-in-time delta/IV resolver exists. The configuration grid is still queued/enumerated rather than backtested. See [PA-009 and current status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_STATUS.md), [selected-strike audit code](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/research/phase52/selected_strike_coverage_audit.py), and [error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md).


**Pre-run audit note:** During code review, a timestamp-key format mismatch in the new selected-strike auditor was caught and patched before accepting any output; it is recorded as F52-023 in the [Phase52 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md). Selected-strike coverage is still pending a fresh Actions self-test/full run.


**Workflow self-audit update:** The previously failing status-log persistence step passed in [run 37935663113](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37935663113) after the safe rebase/push fix. A point-in-time strike-ladder issue was caught before accepting selected-strike results and patched; see [F52-026](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md). Two earlier runs are using older code snapshots; [run 37937318538](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37937318538) is queued to validate the corrected script. No selected-strike result or configuration P&L is accepted yet.


**Concurrency safeguard:** Workflow persistence now checks whether the selected-strike auditor changed after a run checked out its source snapshot; stale selected-strike outputs are discarded/restored rather than overwriting newer evidence. Verification is pending. See [F52-027](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md).


**Persistence guard refinement:** The stale-output guard now leaves a valid placeholder path when no accepted selected-strike output exists, avoiding a secondary git-add failure. This is logged as F52-028; workflow verification is still pending.


**Queue checkpoint:** Run [37935663113](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37935663113) advanced deterministic configuration enumeration to offset 260,000 of 9,379,584. This is enumeration only; the full variable-grid backtest remains unstarted.


**Strategy-specification progress (PA-010):** Source review of the Phase45 strategy plan and sweep code reconciled exact leg geometry for 11 named presets (condors, butterflies, Reverse Jade Lizard, Range Forward, Bear Risk Reversal, Batman and Double Plateau). Specification blockers are reduced to four genuinely unresolved families: Calendar Trap, Iron-Condor-to-Ratio transition, conversion/reversal, and futures-basis overlay. Registry revalidation is pending; this is not a backtest result. See [Phase52 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_RESEARCH_PLAN.md) and [strategy specification registry](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/research/phase52/strategy_specifications.csv).


**Registry snapshot protection:** The workflow now also prevents a run using the pre-PA-010 strategy-specification CSV from overwriting the registry audit generated from the reconciled definitions. This is logged as F52-030; the end-to-end guard test is pending.


**Selected-strike audit caution:** The selected-strike step in run 37937164472 completed, but it used the pre-correction strike-ladder source and is explicitly not accepted. The workflow guard should prevent its results from being published as current; a patched-source rerun is queued in run 37938099763.


**Workflow concurrency correction:** Run [37937164472](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37937164472) completed its audit steps but failed at persistence because parallel runs collided on generated artifacts. One shared concurrency group has been restored; the resolver preserves existing remote result files on collisions and merges only append-only logs, while source/code conflicts still fail closed. See [F52-032](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md). Verification pending.


## Phase 52 — selected ATM-offset leg coverage gate (2026-10-09)

The corrected selected-strike audit completed in [workflow run 37942202655](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37942202655). It used pinned dataset revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5` and resolved the ATM-relative strike ladder only from contracts present at the exact entry timestamp, avoiding future-listed strike leakage.

- 267/267 expiry files audited; zero source file errors.
- 1,068/1,068 event rows; 27,768 ATM-offset × option-type leg-event rows across offsets -6..+6.
- 11,222 rows meet entry OI≥100; 15,718 rows have valid expiry-exit OHLC; 11,108 rows pass exact-index + entry OI + expiry-exit OHLC.
- These are leg-level coverage counts only—not complete multi-leg configuration coverage and not P&L. ABS_DELTA remains blocked pending a tested point-in-time IV/delta resolver. The 2026-07-28 and 2026-08-04 exit data gaps remain unresolved; no candidate is promoted.
- Configuration queue checkpoint: 335,000/9,379,584 IDs enumerated, still `ENUMERATED_NOT_BACKTESTED`.

Artifacts: [summary](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/selected_strike_coverage/summary.json), [source file audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/selected_strike_coverage/source_file_audit.csv), [source errors](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/selected_strike_coverage/source_errors.csv), [status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_STATUS.md), [research log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_RESEARCH_LOG.md), [error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md).


### Phase 52 audit-code corrections (2026-10-09)

The prior ATM-offset coverage artifact from [run 37942202655](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37942202655) is superseded: code review found offsets mapped to ordinal strike ranks and the index close used as the ATM anchor. The corrected audit now uses exact-time NIFTY index open and modal strike-step arithmetic. The model-delta audit [run 37944408314](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37944408314) failed at self-test before any market-data analysis; its sigma and negative fixtures have been corrected, and delta selection now uses only exact prior completed one-minute closes with entry-open eligibility checked separately. Regression reruns are pending. These changes do not alter grid v1.3 domains. No configuration-grid P&L exists; no strategy is promoted.


### Phase 52 PA-013: pre-entry OI gate

A final timing audit found the selected-strike coverage script was using entry-bar OI for a trade simulated at that same bar's open. It has been patched to use the exact prior completed minute's OI for the >=100 gate, while checking current entry-bar open/OHLC separately; entry-bar OI is diagnostic only. The current workflow [37954806932](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37954806932) checked out the earlier code, so any selected-strike output from that run is not accepted as final. Fresh rerun required; no Phase52 grid P&L exists.


### Phase 52 corrected strike/delta coverage and replay-kernel test (2026-10-09)

- **ATM-offset coverage:** [run 37956261518](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956261518) passed with corrected exact-time index open/modal strike-step mapping and prior-completed-minute OI gate. 27,768 offset/type rows were audited across 267 files; 10,552 had prior-bar OI≥100, 10,501 had valid exact entry bars and 10,405 had exact-index plus target-expiry exit support. These are not trades or P&L.
- **ABS_DELTA diagnostic:** [run 37956675818](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956675818) audited all 4,272 target-delta/type rows with zero file errors. 232 lacked an exact prior minute, 148 lacked an OI-qualified candidate, 3,892 passed prior-bar OI, and only 2,232 had valid exact entry-bar references. These are model delta estimates, not exchange Greeks or strategy outcomes.
- **Replay kernel:** [run 37957753452](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957753452) passed synthetic exact-bar, common-time, prior-OI, fill/slippage, fee-scenario and exit-rule tests. The first attempt failed after tests passed due to a literal runner-temp manifest path; that was corrected in the succeeding run.
- **Current decision:** no strategy is promoted. The 9,379,584 grid remains enumerated/not backtested, the index dataset stops 2026-07-02 and its CC BY-NC licence precludes commercial use without independent rights-cleared evidence. Next step is template-aware multi-leg integration and golden tests.


### Phase 52 — corrected strike/delta audits and replay-kernel test (2026-10-09)

- **ATM-offset audit:** [run 37956261518](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956261518) passed over 267/267 source files. Of 27,768 offset/type rows, 10,552 had prior-bar OI≥100, 10,501 had valid exact entry bars and 10,405 also had exact-index/target-expiry exit support.
- **ABS_DELTA diagnostic:** [run 37956675818](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37956675818) passed all 4,272 checks with zero file errors: 3,892 prior-OI-qualified and 2,232 exact entry-bar references. Model deltas are not native exchange Greeks and no P&L was calculated.
- **Replay kernel:** [run 37957753452](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37957753452) passed synthetic exact-bar, fill, common timestamp, prior-OI, fee/slippage and exit-trigger tests. The first run failed only at manifest path handling after the kernel tests passed; the corrected rerun succeeded.
- **Current state:** grid v1.3 has 360,000/9,379,584 configurations enumerated and zero Phase52 configuration backtests. The pinned index series ends 2026-07-02 and the options source is CC BY-NC 4.0, so full-window/commercial promotion remains blocked. No strategy is promoted; the next gate is source-aware template parsing and end-to-end leg/exit golden tests.


### Phase 52 whole-position synthetic integration — latest checkpoint

[Run 37960484240](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960484240) passed the source-bound strategy-template resolver, end-to-end synthetic whole-position tests across all 45 supported option-only templates, and the independent canonical replay-kernel/Phase43 fee-parity regression. The integrated test produces 270 synthetic cost-scenario rows across ₹20 primary/₹10 legacy brokerage × 0/50/100% slippage; it verifies exact option legs, prior-minute OI, common 15:15 exits, fee math and fail-closed missing-leg cases. A reference-lot scaling gap found during review was fixed before historical replay. The initial integration run [37960340815](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37960340815) failed because its butterfly test fixture inadvertently overrode the native 1:2:1 ratio; corrected rerun passed. All calculated P&L here is synthetic fixture arithmetic only. The finite grid has 360,000/9,379,584 IDs enumerated and **zero historical Phase52 configuration backtests**. The main next gate is a bounded historical pilot with exact source/leg/exit/cost manifests; no strategy is promoted.

## Phase 52 bounded historical pilot — run 37962192723

- **Run:** [37962192723](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37962192723); job=failure; self-test=success; plan-only=success; replay=failure.
- **Frozen pilot preflight only:** configs=40; events=24; planned config-event rows=480; historical replay report missing.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Branch-local run details: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-52-factor-conditioned-strategy-discovery/results/phase52/historical_pilot
- This is a bounded baseline engineering run, not a factor-router efficacy result.

## Phase 52 bounded historical pilot — run 37962948690

- **Run:** [37962948690](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37962948690); job=success; self-test=success; plan-only=success; replay=success.
- **Pilot result status:** HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS; configs=40; planned config-event rows=480; executed=1; excluded/errors=479; cost rows=6; source file errors=0.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Branch-local run details: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-52-factor-conditioned-strategy-discovery/results/phase52/historical_pilot
- This is a bounded baseline engineering run, not a factor-router efficacy result.


## Phase 52 — pilot integrity and coverage gate (updated 2026-10-10)

The v0.1 report and v0.2 run artifact are distinct versions, not contradictory rows. The verified v0.2 artifact for [run 37980455805](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37980455805) contains 480 rows: 379 OHLC-range-proxy exclusions, 100 prior-OI blocks (all prior OI=0, validation split), and one replay pass. Its one modeled trade is net negative across all six cost cases and is not a strategy-performance conclusion. The checkpoint conflict was fixed and the persistence regression test passed on [run 37983999726](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37983999726). The audit-provenance rerun is active at [run 37984566094](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37984566094). No filter or holdout was changed; no strategy has been promoted. See [Phase 52 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_STATUS.md), [research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_RESEARCH_PLAN.md), and [error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md). Next: improve data coverage through a separate, free-source-only source-validation phase; do not loosen the frozen 2% range proxy to manufacture rows.

## Phase 52 bounded historical pilot — run 37983999726

- **Run:** [37983999726](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37983999726); job=success; self-test=success; plan-only=success; replay=success.
- **Pilot result status:** HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS; configs=40; planned config-event rows=480; executed=1; excluded/errors=479; cost rows=6; source file errors=0.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Branch-local run details: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-52-factor-conditioned-strategy-discovery/results/phase52/historical_pilot
- This is a bounded baseline engineering run, not a factor-router efficacy result.

## Phase 52 bounded historical pilot — run 37984566094

- **Run:** [37984566094](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37984566094); job=success; self-test=success; plan-only=success; replay=success.
- **Pilot result status:** HISTORICAL_BASELINE_PILOT_COMPLETE_WITH_EXPLICIT_EXCLUSIONS; configs=40; planned config-event rows=480; executed=1; excluded/errors=479; cost rows=6; source file errors=0.
- **Interpretation:** bounded BASELINE engineering pilot only; no winner ranking/promotion. Holdout remains untouched. Queue enumeration is not a backtest count.
- Branch-local run details: https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/tree/phase-52-factor-conditioned-strategy-discovery/results/phase52/historical_pilot
- This is a bounded baseline engineering run, not a factor-router efficacy result.


## Phase 53 — Free-source option data coverage remediation (2026-10-10)

Phase 52's checkpoint-persistence defect is resolved and its regression test passed on [run 37983999726](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37983999726). The verified v0.2 pilot still has only one replay pass out of 480 rows, so Phase 53 is a bounded source-quality/data-coverage audit, not another strategy optimization or a promotion attempt. It preserves the 2% OHLC proxy and holdout.

- [Phase 53 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-53-free-option-data-coverage-remediation/PHASE53_RESEARCH_PLAN.md)
- [Data source matrix](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-53-free-option-data-coverage-remediation/PHASE53_DATA_SOURCE_MATRIX.md)
- [Phase 53 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-53-free-option-data-coverage-remediation/PHASE53_STATUS.md)
- [Phase 53 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-53-free-option-data-coverage-remediation/PHASE53_ERROR_LOG.md)
- [Machine-readable source registry](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-53-free-option-data-coverage-remediation/research/phase53/sources.json)
- [Manual/automatic source audit workflow](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-53-free-option-data-coverage-remediation/.github/workflows/phase-53-free-option-data-coverage.yml)

Phase 53 must establish exact source revision/file coverage and distinguish official daily reports from timestamp-aligned intraday quote/depth. Public sample files or credential-dependent APIs are not counted as free full-history sources. No strategy, factor router or holdout is promoted or evaluated in this phase.


## Phase 54 — OHLC-reference sensitivity (non-executable)

Phase 53 closed with a bounded NO-GO for free independent historical bid/ask/depth data. Phase 54 is a separate branch and does not treat candle range as spread, recompute P&L, or promote any strategy. It audits whether the frozen Phase 52 output retains complete per-leg evidence needed to calculate threshold sensitivity. The first valid audit found 373 empty leg payloads and partial payloads among other exclusions, so alternate-threshold counts are blocked rather than imputed.

- [Phase 54 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_RESEARCH_PLAN.md)
- [Phase 54 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_STATUS.md)
- [Phase 54 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_ERROR_LOG.md)
- [Sensitivity code](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/research/phase54/ohlc_reference_sensitivity.py)
- [Manual and push-triggered workflow](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/.github/workflows/phase-54-ohcl-reference-sensitivity.yml)

The workflow reports eligibility counts only. Exit validity, executable fills, transaction-cost profitability and strategy superiority are not tested in this phase; holdout remains untouched.


## Phase 55 — Complete leg-audit payload repair

Phase 54 showed that the stored event replay output was not sufficiently detailed to calculate alternate OHLC thresholds without inventing leg values. Phase 55 repairs the Phase 52 runner to preserve one audit record per selected leg, continue checking remaining legs after the first failure, and fail closed if a leg is omitted.

- [Phase 55 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_RESEARCH_PLAN.md)
- [Phase 55 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_STATUS.md)
- [Phase 55 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_ERROR_LOG.md)
- [Runner regression tests](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/research/phase52/tests/test_historical_pilot_leg_audit.py)
- [Cached manual/automatic pilot workflow](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/.github/workflows/phase-55-leg-audit-payload-repair.yml)

The workflow reruns the same frozen 480-row pilot against the pinned revision, validates expected leg counts and cost rows, and caches the Hugging Face files by revision. Raw market data is not committed; no holdout or strategy promotion is allowed.


## Research continuation — Phase 54 completed; Phase 55 all-leg audit repair active (2026-10-10)

### Phase 52 — repaired bounded historical pilot evidence

Workflow [37990362985](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37990362985) completed the frozen 40-config × 24-event pilot with 480 rows. The accepted row ledger has 379 `EXCLUDED_OHLC_RANGE_PROXY` rows with full selected-leg diagnostics, 100 prior-OI eligibility blockers, and one baseline `REPLAY_PASS`. The 100 blockers each have an observed required-leg prior OI below 100; the other legs were not all audited in this Phase 52 output. The pilot is not a useful profitability sample (one executed row); no strategy is ranked or promoted.

- [Phase 52 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_RESEARCH_PLAN.md) · [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_STATUS.md) · [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/PHASE52_ERROR_LOG.md)
- [Accepted 480-row replay ledger](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-52-factor-conditioned-strategy-discovery/results/phase52/historical_pilot/event_replay.csv)
- [Phase 52 evidence-repair workflow run](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37990362985)

### Phase 54 — OHLC-reference coverage sensitivity CLOSED

The corrected Phase 52 ledger was copied byte-for-byte to the Phase 54 branch and verified by input fingerprint. Run [37992502101](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992502101) passed unit tests, self-test, input reconciliation, all 11 preregistered thresholds, artifact upload, and checkpoint persistence.

| OHLC range proxy threshold | Rows meeting OI + entry + range checks | Share of 480 |
|---:|---:|---:|
| 2% (frozen baseline) | 1 | 0.21% |
| 3% | 1 | 0.21% |
| 4% | 8 | 1.67% |
| 5% | 24 | 5.00% |
| 6% | 55 | 11.46% |
| 8% | 91 | 18.96% |
| 10% | 150 | 31.25% |
| 12% | 227 | 47.29% |
| 15% | 298 | 62.08% |
| 20% | 345 | 71.88% |
| 1000% (diagnostic near-removal) | 380 | 79.17% |

Across every threshold the 100 explicit prior-OI blockers remain rejected, entry-data rejections are zero, and all categories reconcile to 480. The increasing counts show sensitivity to the range-proxy threshold, **not** more profitable or more liquid opportunities. The OHLC high-low/open statistic is not a quoted bid/ask spread; there are no recalculated exits, fills, costs, or P&L, and no holdout use or strategy promotion.

- [Phase 54 plan and preregistered amendment](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_RESEARCH_PLAN.md) · [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_STATUS.md) · [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_ERROR_LOG.md)
- [Sensitivity report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/results/phase54/ohlc_reference_sensitivity/report.md) · [Machine-readable threshold results](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/results/phase54/ohlc_reference_sensitivity/threshold_sensitivity.csv) · [Family coverage](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/results/phase54/ohlc_reference_sensitivity/family_coverage.csv)

### Phase 55 — complete selected-leg audit CLOSED

The bounded audit repair completed successfully in [run 37993968572](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37993968572). Syntax validation, regression tests, deterministic self-test, pinned replay, external audit, artifact upload and checkpoint persistence passed.

- 480 rows reconciled: 379 `EXCLUDED_OHLC_RANGE_PROXY`, 100 `BLOCKED_LEG_ELIGIBILITY`, 1 `REPLAY_PASS`.
- Complete selected-leg payloads verified for **480/480 rows**, with family-appropriate number of unique leg IDs and entry/OI/range/exit statuses; six cost rows for the one replay-pass row.
- Source revision unchanged: `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`.
- [Plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_RESEARCH_PLAN.md) · [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_STATUS.md) · [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_ERROR_LOG.md) · [Machine-readable audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/results/phase52/historical_pilot/phase55_audit.json)

### Phase 56 — OHLC price-reference P&L sensitivity ACTIVE

Phase 56 is a separate, bounded analysis of price-reference economics across the 11 already-preregistered Phase54 thresholds. It applies exact stored entry/exit opens with the existing date-aware statutory charges, ₹10 (current Paytm Money F&O FAQ rate) and ₹20 per-order brokerage cases, and six fixed adverse-slippage assumptions from ₹0.00 to ₹0.50 per fill. The zero-slip scenario is a lower-bound diagnostic; the largest slippage values are deliberately severe and uncalibrated stress tests. This is not a quote-based or executable backtest, and an OHLC range statistic is not bid/ask spread.

The workflow [37995733702](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37995733702) is running the frozen 480-row ledger; it has not yet been accepted. The output gate requires exact Phase54 eligibility counts, all 480 complete leg payloads, 132 threshold/cost summaries, 5,280 configuration summaries, 924 family summaries, 440 severe-cost screens and 18,960 per-row non-executable price-reference cost scenarios.

- [Phase56 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/PHASE56_RESEARCH_PLAN.md) · [Status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/PHASE56_STATUS.md) · [Error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/PHASE56_ERROR_LOG.md) · [Automated workflow](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/.github/workflows/phase-56-ohlc-pnl-sensitivity.yml)

**Research-wide guardrails:** no holdout used; no strategy promoted; source revision remains pinned to `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`; CC BY-NC 4.0 rules prohibit commercial use/promotion of this data; OHLC open fills remain simulated reference prices, not confirmed executions. No profitability conclusion is established.


# Latest continuation checkpoint — 2026-10-10 — Phase 55 and Phase 54 accepted

## Phase 55 — Complete selected-leg audit (CLOSED / PASS)

The bounded repair replay passed in [run 37993968572](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37993968572). The frozen 480-row ledger reconciles to 379 OHLC-range-proxy exclusions, 100 strict prior-minute OI blocks, and one baseline replay pass. The audit verified 480/480 rows have the expected number of selected-leg records with unique leg IDs, on the pinned source revision `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`. This closes serialization/data-integrity repair only; it does not improve eligible sample size or establish strategy efficacy.

- [Phase 55 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_RESEARCH_PLAN.md)
- [Phase 55 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_STATUS.md)
- [Phase 55 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/PHASE55_ERROR_LOG.md)
- [Repaired event replay ledger](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-55-leg-audit-payload-repair/results/phase52/historical_pilot/event_replay.csv)

## Phase 54 — OHLC-reference sensitivity (CLOSED / COVERAGE ONLY)

After syncing the Phase 55 repaired ledger, [run 38018639487](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38018639487) passed regression tests, sensitivity computation, 480-row reconciliation, artifact upload and log persistence. The input fingerprint is `fbae8f080a685b2bafcc1248995b9342fea4c598110916e42296bee1af57dd55`; all 480 rows have complete leg payloads, including explicit hard prior-OI blockers. Across the preregistered range thresholds (2, 3, 4, 5, 6, 8, 10, 12, 15, 20 and 1000%), eligible row counts were 1, 1, 8, 24, 55, 91, 150, 227, 298, 345 and 380 respectively. Every threshold reconciled to 480 rows; the 100 OI blockers remained invariant and entry-data rejects were zero.

These counts are eligibility sensitivity only. OHLC high-low/open is not a quoted bid/ask spread, and relaxing the diagnostic range threshold does not validate fills, exits or profitability. No P&L was recomputed, holdout remained untouched, and no strategy was promoted.

- [Phase 54 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_RESEARCH_PLAN.md)
- [Phase 54 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_STATUS.md)
- [Phase 54 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/PHASE54_ERROR_LOG.md)
- [Sensitivity report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/results/phase54/ohlc_reference_sensitivity/report.md)
- [Threshold table](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-54-ohcl-reference-sensitivity/results/phase54/ohlc_reference_sensitivity/threshold_sensitivity.csv)

## Next research gate

Continue Phase 52's factor-conditioned strategy research only after resolving the upstream data-coverage limitations and the source-license/executable-quote constraints. The 480-row BASELINE pilot is not a factor-selector experiment, has only one baseline replay pass, and cannot support strategy ranking. The finite grid size (9,379,584 configurations) remains queue size, not tested count. Do not promote a strategy or use the 2026 holdout until a predeclared, adequately covered, cost-aware replay and statistical validation pass.


## Phase 56 supporting audit — Exact prior-minute OI source diagnosis (CLOSED / PASS)

[Run 38018825640](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38018825640) passed the regression tests and audited all exact contract-time keys behind the 100 Phase 52 prior-OI-blocked rows. Of 220 blocked leg references, there are 60 unique expiry/timestamp/type/strike keys across the 2025-03-13, 2025-07-31 and 2025-12-30 partitions. All 60 keys have exactly one exact prior-minute source row, and all 60 source rows explicitly report numeric OI=0. No key was missing or duplicated. The partition hashes matched the pinned Phase 52 source audit.

This resolves the immediate data diagnosis: the exclusions are caused by source-recorded zero OI, not absence of the exact prior-minute row. It does not prove that the dataset's zero values perfectly represent exchange reality, but under the frozen OI >= 100 gate they remain correctly ineligible. No filter was relaxed, no P&L was recomputed, holdout remains untouched, and no strategy was promoted.

- [Phase 56 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-prior-oi-coverage-diagnosis/PHASE56_RESEARCH_PLAN.md)
- [Phase 56 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-prior-oi-coverage-diagnosis/PHASE56_STATUS.md)
- [Phase 56 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-prior-oi-coverage-diagnosis/PHASE56_ERROR_LOG.md)
- [Exact contract-time audit CSV](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-prior-oi-coverage-diagnosis/results/phase56/prior_oi_coverage/contract_oi_audit.csv)
- [Machine-readable report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-prior-oi-coverage-diagnosis/results/phase56/prior_oi_coverage/report.json)

## Phase 56 — Cost-aware OHLC price-reference P&L sensitivity (CLOSED / NON-EXECUTABLE)

The previously failing, preregistered Phase 56 analysis was repaired and accepted in [canonical-input run 38019323348](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019323348). The validator defect was that it rejected the canonical underscored OI reason; normalization and regression tests now pass. The bounded matrix reconciled 480 rows, 40 configurations, 24 event identities, all 11 thresholds and all 18,960 cost scenarios (₹10/₹20 brokerage × six adverse-slippage cases). The 100 hard prior-OI blocks remained ineligible at every threshold.

| OHLC range threshold | Eligible configuration-event rows | Grid sum at ₹10/order + ₹0.05 slip | Grid sum at ₹20/order + ₹0.50 slip |
|---:|---:|---:|---:|
| 2% | 1 | -₹166.19 | -₹214.80 |
| 4% | 8 | +₹13,115.04 | +₹12,312.13 |
| 5% | 24 | -₹1,864.05 | -₹4,231.65 |
| 10% | 150 | +₹7,426.04 | -₹10,386.81 |
| 15% | 298 | +₹45,114.40 | +₹7,183.14 |
| 20% | 345 | +₹40,144.70 | -₹3,138.02 |
| 1000% diagnostic | 380 | +₹55,926.12 | +₹7,902.95 |

**Important:** grid sums pool overlapping configurations on the same events; they are not portfolio returns. The apparent positives are highly threshold-sensitive. Only five configuration-threshold pairs passed the preregistered severe-cost screen, all at the 1000% diagnostic threshold; that threshold effectively removes the OHLC range gate and is not a recommended setting. The five are leads for independent quote validation only. No significance, generalization or live-trading claim is made; OHLC range is not spread, and OHLC-open fills are not executable quote evidence.

- [Phase 56 research plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/PHASE56_RESEARCH_PLAN.md)
- [Phase 56 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/PHASE56_STATUS.md)
- [Phase 56 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/PHASE56_ERROR_LOG.md)
- [P&L sensitivity report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/results/phase56/ohlc_pnl_sensitivity/report.md)
- [Threshold/cost summary CSV](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/results/phase56/ohlc_pnl_sensitivity/threshold_summary.csv)
- [Severe-cost robustness screen](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-56-ohlc-pnl-sensitivity/results/phase56/ohlc_pnl_sensitivity/robustness_screen.csv)

## Next gate after Phase 56 price-reference sensitivity

Phase 52 remains open but the current BASELINE pilot has only one replay pass and does not test factor-selector efficacy. The next valid work is to improve source-backed candidate/event coverage or obtain independent, legally usable executable quote data; the Phase 56 result is not a reason to weaken OI eligibility. Any subsequent strategy test must retain Paytm Money brokerage/statutory costs and adverse slippage, chronological splits, multiple-testing controls and an untouched holdout.


**Provenance correction:** the final accepted Phase 56 report is from canonical-input run [38019323348](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019323348), which uses the exact Phase 55 ledger blob `06f9b0d39652923bae052dd82f2c779ada111da3` and SHA-256 `fbae8f080a685b2bafcc1248995b9342fea4c598110916e42296bee1af57dd55`. The earlier accepted run's only ledger differences were the 100 exclusion-reason strings; it is superseded for input provenance, and the computed metrics reproduced exactly.


## Phase 58 — Historical quote/depth source feasibility (CLOSED / NO-GO)

[Run 38019987421](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019987421) passed the source-registry tests. Six candidates were reviewed: NSE, StockMojo, NiftyTrader, TickBytes, OptionVault and the existing Hugging Face 1-minute dataset. **Zero sources are verified for full historical bid/ask/depth at the frozen 09:45/13:00 entries and exact 15:15 exit with permitted automation.**

- **StockMojo:** advertises minute-level historical OI, premium, IV and Greeks, but its published terms prohibit bots, scraping, programmatic access and systematic data collection. It cannot be used by the automated GitHub research workflow.
- **NiftyTrader:** documents bid/ask at close, free single-day CSVs and premium bulk downloads; its listed premium intraday snapshots (09:30, 11:30, 13:30, 15:00) do not match the frozen timestamps.
- **TickBytes and OptionVault:** public samples show quote/depth fields, but the full historical datasets are licensed/private and target-date coverage and reuse/storage terms are unverified. They are the best licensed follow-up candidates, not accepted data sources.
- **NSE:** live bid/ask is not a verified historical intraday quote archive, and the site terms restrict copying/aggregation.
- **Current Hugging Face dataset:** usable for research-only OHLC/OI, but lacks bid/ask/depth and declares CC BY-NC 4.0.

No purchase was made and no terms-violating scraping was performed. The source gate remains closed; the next valid step is explicit authorization for a licensed sample with exact target-date/contract coverage and research/storage rights, or discovery of a newly verified free source.

- [Phase 58 plan](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-58-quote-source-feasibility-audit/PHASE58_RESEARCH_PLAN.md)
- [Phase 58 status](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-58-quote-source-feasibility-audit/PHASE58_STATUS.md)
- [Phase 58 error log](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-58-quote-source-feasibility-audit/PHASE58_ERROR_LOG.md)
- [Source registry](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-58-quote-source-feasibility-audit/research/phase58/sources.json)
- [Machine-readable source report](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-58-quote-source-feasibility-audit/results/phase58/quote_source_feasibility/report.json)

