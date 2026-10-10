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


## F64-001 — Future contract availability could influence strike selection — PATCHED BEFORE ACCEPTED NUMERICAL OUTPUT
- Date: 2026-10-10
- Run: 38026911131 (numerical step cancelled before completing).
- Observation: the first implementation chose the nearest ITM strike among contracts appearing anywhere in an expiry file. This used information later than the breakout trigger to decide which strike would be selected.
- Impact: any output produced by that code would be non-evidence for the strategy test. No completed report/summary was accepted.
- Correction: extracted select_itm_strike; it only considers call/put contracts with a valid observed close on the exact trigger minute. Entry still requires an observed option close at the next exact minute. Added a regression test for a strike present only in the future.
- Status: PATCHED; awaiting the corrected run. This is an implementation correction before accepting results, not a post-result strategy-rule change.
