# Phase 36 Error Log — Independent Per-Trade Direction Selector Overlay

## 2026-10-06 — Run 37427528243

### Error F36-001 — Mixed skip-ledger row widths
**Affected jobs:** CATBOOST, WAVELET_TREE, OOF_STACK.

**Symptom:** The numerical loop completed many expiry calculations, then Pandas failed constructing the skip DataFrame with:
\`ValueError: 3 columns passed, passed data had 4 columns\`.

**Cause:** Missing/incomplete expiry skips were stored as three fields, while \`run_expiry()\` returned three fields that were prefixed with expiry, producing four fields.

**Evidence status:** The affected jobs are non-evidence. No conclusion or promotion decision uses them.

**Correction:** Normalize all skip records to the fixed schema \`expiry, timestamp, reason, detail\` before constructing the DataFrame.

**Prevention:** Enforce a single audit-record schema at the engine boundary and validate row widths before serialization.

**Research impact:** None on accepted evidence; failure occurred after the trade calculation loop and before final artifact creation.


## 2026-10-06 — Run 37428195471

### Error F36-002 — Duplicate quote rows in fresh premium selector
**Affected selectors:** OTM678_FRESH, OTM789_FRESH.

**Symptom:** Eight expiry-level loops terminated with:
\`TypeError("float() argument must be a string or a real number, not 'Series'")\`.

**Cause:** At some timestamps the option snapshot contained duplicate rows for the same option type and strike. Pandas \`loc\` returned a Series instead of a scalar close.

**Evidence status:** Fresh-selector results from run #3 are non-final and are not used for phase conclusions.

**Correction:** Group each option type/strike pair in the snapshot and use the last observed close deterministically before evaluating OTM678/OTM789 premium expressions.

**Research impact:** No accepted model-selector results are affected. Fresh-selector results require rerun after correction.


## Error F36-003 — Final artifact-manifest blob mapping
The first final-research packaging commit mapped several prepared content blobs to the wrong filenames. Numerical evidence was unaffected, but the repository manifest was incorrect.

**Evidence status:** packaging-only, non-evidence.

**Correction:** Each affected file was re-read, remapped and verified individually.

## Error F36-004 — Invalid workflow content during artifact-manifest repair
**Runs:** 37429445210, 37429450459, 37429454606, 37429458477, 37429477965, 37429482697, 37429486634.

During the manifest repair, the workflow file temporarily contained the error-log content. Because the workflow still had a broad `PHASE36_**` push filter at that moment, documentation commits triggered invalid workflow runs.

**Evidence status:** CI/packaging-only; no numerical output was accepted.

**Correction:** The executable workflow was restored and push triggers were narrowed to research source/cache/workflow and preregistration files.

## Error F36-005 — Publish non-fast-forward race
**Run:** 37429502607 (#17), publish job only.

All seven numerical jobs succeeded, but artifact publication created a commit from a stale checkout and `git push` was rejected as non-fast-forward after the branch advanced.

**Evidence status:** CI/publish-only; numerical evidence was valid.

**Correction:** The publish step was hardened with `git pull --rebase origin "$GITHUB_REF_NAME"` immediately before pushing.

## Final reproducibility checkpoint
**Run:** 37429748933 (#18).

All seven numerical selector jobs succeeded and the rebase-safe publication job also succeeded. This is the final workflow validation checkpoint.
