# Phase 94 Error / Limitation Log

## E94-001 — Literature coverage can be confused with empirical reproduction
- **Detected:** 2026-10-10
- **Severity:** High
- **Issue:** Phase 93 successfully audited and cited 14 PDFs, but did not re-run the papers' models or trading results. The user reasonably expects paper-derived methods to be empirically tested, not only cited.
- **Correction:** This phase registers the methods, makes replication status explicit, and creates bounded downstream phases for model, signal and options-rule testing.
- **Status:** Corrective plan committed; empirical execution remains pending.

## L94-001 — Paper descriptions do not always specify reproducible rules
- **Type:** Limitation
- **Issue:** Some source PDFs describe model families or strategy taxonomies without enough exact hyperparameters, entry/exit conditions, execution assumptions or raw data links to recreate a unique implementation.
- **Handling:** Distinguish exact replication from transparent operationalization and NOT IDENTIFIABLE. Do not invent unreported values.

## L94-002 — Reported accuracy metrics may be scale-dependent or non-comparable
- **Type:** Limitation
- **Issue:** Reported 95%/99% values may be defined on normalized price levels or by a paper-specific formula; they do not automatically mean direction accuracy or tradable profit.
- **Handling:** Recreate source metric only if the formula is identifiable, then report common baseline-relative metrics.

## L94-003 — Options execution data gap
- **Type:** Data blocker
- **Issue:** Prior evidence in Phases 60/61/66/68 did not establish complete authorized exact listed-option contract history with execution-quality quotes for all needed periods. An OHLC proxy with zero eligible trades cannot answer the profitability question.
- **Handling:** No P&L result unless exact-contract mapping, timestamps, entry/exit records and cost schedule are validated. Record blocked rows and excluded events.

## L94-004 — Multimodal historical data availability
- **Type:** Data blocker
- **Issue:** Point-in-time historical news sentiment, option Greeks, PCR, FII/DII, FX and VIX are not guaranteed to be jointly available in all paper source windows.
- **Handling:** Run only source-supported modalities; mark a reduced model as partial and evaluate feature ablations only on common rows.

## E94-005 — Prior result interpretation
- **Detected:** 2026-10-10
- **Severity:** Medium
- **Issue:** Empty trade-summary totals must not be interpreted as observed ₹0 returns, and zero completed trades must not be interpreted as evidence of negative expectancy.
- **Correction:** Preserve Phase 66's NOT ESTIMABLE determination and require valid-trade count/coverage before computing profitability metrics.

## E94-010 — registry CSV alignment validation failed
- Run: [38070702058](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38070702058)
- Failure: validator raised `AttributeError: 'NoneType' object has no attribute 'strip'` on an incomplete CSV row rather than emitting a row-width validation error.
- Root cause: two cross-paper register rows had only 10 columns instead of the required 11.
- Correction: fixed both rows and rewrote the CSV with proper comma/quote escaping; validator now checks row width first and safely reports missing cells.
- Status: correction committed; fresh workflow validation pending.

## E94-011 — status validator expected wording that was not used
- Run: [38070932954](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38070932954)
- Failure: registry validator asserted that the literal phrase `no strategy` appeared in `PHASE94_STATUS.md`; the status file instead expressed the same decision as `Strategy promotion: NONE`.
- Correction: validate the semantic status field (`strategy promotion` and `none`) rather than requiring specific prose wording.
- Status: corrected; awaiting fresh validation.
