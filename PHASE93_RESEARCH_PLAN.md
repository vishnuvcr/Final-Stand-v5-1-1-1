# Phase 93 — Uploaded Literature Evidence Audit and Manuscript Integration

**Registered:** 2026-10-10  
**Branch:** phase-93-uploaded-literature-audit  
**Parent:** phase-92-synthetic-forward-oi-study-2022  
**Type:** bounded evidence synthesis and documentation quality control; no new market-data experiment  
**Strategy promotion:** none

## Research question

Do the 14 user-uploaded papers provide directly applicable, reproducible evidence for NIFTY options-strategy profitability, or do they mainly inform daily index-price prediction, feature engineering, and broad options-strategy hypotheses?

## Aim and objectives

1. Review all 14 uploaded PDFs by extracting searchable text and checking titles, abstracts, methods/results, limitations and conclusions.
2. Record each paper's exact source filename, bibliographic metadata, reported target/frequency/design, author-reported result, relevance, and limits in a literature evidence audit.
3. Distinguish daily index-level price prediction, feature/association studies, conceptual options strategy descriptions, and empirically reported option-strategy results.
4. Integrate the source findings into the existing Phases 89–92 manuscript without altering any registered sample, model, forecast metric or strategy decision.
5. Highlight claim-level reproducibility requirements: exact contract/expiry/strike, point-in-time option quotes/depth, fill assumptions, independent OOS tests and brokerage/statutory/spread/slippage costs.
6. Add an automated audit workflow with both bounded push triggers and a manual workflow_dispatch button.
7. Update status, error/chat logs and README links. Keep the 2026 Phase 83 holdout sealed and do not repeat the closed rolling-ATM predictor sweep.

## Methods

- Inputs: the 14 PDFs attached in the conversation. Filenames are enumerated in results/phase93/UPLOADED_LITERATURE_AUDIT.md.
- Extraction: pdftotext -layout was used for searchable text; no OCR was used. The review considered the opening metadata/abstract, methods/results, limitations/conclusion and any reported trading metrics available in extracted text.
- Synthesis: qualitative narrative synthesis, classified by research target and evidence proximity to the current program. No pooled effect, meta-analysis or cross-paper ranking is computed because targets, horizons, datasets, methods and reported units are heterogeneous.
- Reporting rule: distinguish what a paper reports from what this project independently reproduced. Treat source-reported backtests as claims of that source, not verified strategy results.
- Copyright/data rule: PDFs remain as user uploads and are not copied into this repository. The repo stores bibliographic metadata and a concise critical summary only.

## Preregistered classifications

- **A — direct trading evidence:** a defined strategy and option-contract returns are tested.
- **B — options-market/strategy context:** derivatives, signals or strategy logic are studied, but executable evidence is insufficiently comparable to this project.
- **C — index-level forecasting:** daily NIFTY or equity price forecasts, not option strategy P&L.
- **D — conceptual/limited empirical evidence:** descriptive strategy material or a proposal without a reproducible OOS execution evaluation.

A category does not certify methodological quality. Author-reported metrics are transcribed only where visible in the source and are flagged as unverified by this research program.

## Acceptance tests

- All 14 PDFs have unique audit IDs U01–U14 and exact filename mappings.
- Every paper has a summary, relevance classification, limitations, and statement of how it is used (or not used) in the manuscript.
- The manuscript cites all 14 uploaded sources and clearly separates index-price forecasting from option-trading profitability.
- The new automated validator passes on GitHub Actions.
- The main README links the audit and records the status.
- No raw uploaded PDF, raw market row, API token, hidden reasoning, or Phase 83 holdout material is added to repository logs.

## Scope boundary and stopping rule

This phase is complete after reviewing the fixed set of 14 uploaded papers, integrating them into the manuscript, validating bibliography coverage, and updating repository documentation. Do not expand to arbitrary additional years or model tuning. A separate empirical option-strategy phase requires a materially new hypothesis or verified authorized exact-contract execution-grade data; it must include Paytm Money brokerage and statutory charges, bid/ask spread, adverse slippage, latency, and stressed-cost analysis.

## Related evidence

- [Phase 92 stopping decision](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-92-synthetic-forward-oi-study-2022/results/phase92/CROSS_PHASE_FACTOR_SYNTHESIS.md)
- [Phase 92 manuscript before literature audit](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/blob/phase-92-synthetic-forward-oi-study-2022/results/phase92/MANUSCRIPT_DRAFT.md)
