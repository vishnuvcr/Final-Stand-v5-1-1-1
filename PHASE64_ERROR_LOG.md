# Phase 64 Error Log

## Rules
- Log every code, data, workflow and validation failure with root cause, correction, and whether the output is evidence.
- A green workflow is not a scientific pass if source lineage, no-look-ahead rules, trade coverage, candidate universe and statistical gates are not independently audited.
- No raw datasets, credentials, or signed URLs may be committed.
- Preserve failed runs as non-evidence; never overwrite a failed result's conclusion without recording the correction.

## 2026-10-10 — Phase opening
- No numerical execution attempted yet.
- PDF semantic search returned zero hits for two queries, despite the files being mounted. Corrective action: full text was extracted locally via pdftotext -layout, and the rendered title-page contact sheet was inspected.
- Severity: minor tooling limitation. Research evidence not affected; exact paper claims have been reviewed in the extracted text.
- Status: resolved by local document processing; code/data/workflow gates remain pending.
