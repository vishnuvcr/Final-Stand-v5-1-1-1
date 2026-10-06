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


## 2026-10-06 — Phase 37 registration

### Error F36-006 — Model direction polarity mismatch discovered after Phase-36 acceptance
**Affected Phase-36 treatments:** CATBOOST, DART, WAVELET_TREE, OOF_STACK, MARKOV_REGIME_TREE.

**Finding:** Phase 35 defines the target as the sign of `log(expiry_close / reference_spot)`, so the cached probabilities represent an up/bullish expiry move probability. Phase 36 mapped `p >= 0.50` to CALL and `p < 0.50` to PUT, which is opposite to the intended Continuous Delta 6x6 economic mapping.

**Correct mapping registered for Phase 37:** bullish/up -> PUT spread; bearish/down -> CALL spread.

**Evidence status:** Phase-36 numerical artifacts are retained for audit, but its model-selector P&L is not valid evidence for the intended polarity hypothesis.

**Prevention:** All future model-to-strategy overlays must explicitly document the prediction target, probability semantics and economic position mapping in the pre-registration before numerical execution.


## 2026-10-06 — Phase 38 run 37432966945

### Error F38-001 — Regenerated control did not match the frozen canonical Phase-32 result
**Symptom:** The first Phase-38 robustness run reconstructed 205 control trades with net **+₹65,945.47**, while the previously accepted canonical Phase-32 result has 206 trades with net **+₹63,672.58**.

**Cause:** The current Phase-32 engine/data reconstruction did not reproduce the frozen historical control artifact exactly. The reconstructed output also began with 04-Jan-2024 trades, whereas the frozen canonical control begins at 11-Jan-2024.

**Evidence status:** The selector-versus-control results from run 37432966945 and its rerun are **rejected as primary evidence** because the control was not frozen-identical.

**Correction:** The accepted Phase-32 control was frozen by its SHA-256 artifact fingerprint and expiry-level P&L cache under `results/phase38_corrected_model_robustness/frozen_control_*`. Phase 38 paired tests now use this frozen control. The workflow still reconstructs the control for audit, but the reconstruction is explicitly validated and cannot silently replace the frozen comparator.

**Prevention:** Future control-relative phases must compare a regenerated benchmark against a frozen canonical artifact before any treatment-versus-control result is accepted.

**Research impact:** No model promotion decision is based on the mismatched-control run.


## 2026-10-06 — Phase 38 manuscript packaging

### Error F38-002 — Unescaped manuscript delimiter in tool write
**Symptom:** The first attempt to create PHASE38_MANUSCRIPT.md failed in the tool layer with a JavaScript template-string parse error.

**Cause:** Markdown inline code delimiters were embedded directly inside a JavaScript template literal.

**Evidence status:** No repository file was changed and no numerical analysis was affected.

**Correction:** The manuscript was rewritten without the conflicting delimiter syntax and committed successfully.

**Research impact:** None.


## 2026-10-06 — Phase 39 workflow packaging

### Error F39-001 — JavaScript interpolation of GitHub Actions shell variable
**Symptom:** The first two attempts to create the Phase 39 workflow failed in the tool layer with ReferenceError: GITHUB_REF_NAME is not defined.

**Cause:** The workflow text was constructed as a JavaScript template literal, so the GitHub Actions shell expression ${GITHUB_REF_NAME} was interpreted by the tool runtime instead of emitted literally.

**Evidence status:** No numerical evidence or repository file was changed by the failed attempts.

**Correction:** The workflow was rebuilt using string concatenation so the GitHub Actions shell variable is emitted literally.

**Research impact:** None.


## 2026-10-06 — Phase 39 tool/automation audit

### Error F39-002 — Branch search argument mismatch
The first branch lookup supplied `repository_full_name` to a connector operation that requires separate `owner` and `repo_name` fields.

**Evidence status:** tooling-only; no repository or numerical evidence changed.

**Correction:** Re-ran the lookup with `owner=vishnuvcr` and `repo_name=Final-Stand-v5-1-1-1` and confirmed branch `phase-39-advanced-direction-models`.

### Error F39-003 — Workflow-artifact lookup argument mismatch
The first workflow-artifact lookup supplied `repository_full_name` instead of the required `repo_full_name` field.

**Evidence status:** tooling-only; no numerical evidence changed.

**Correction:** Re-ran with the correct field and recovered the Phase-32 final artifact ID `11380124540`.

### Error F39-004 — Unsupported JavaScript filesystem import attempt
A tool-orchestration attempt tried to import `child_process` inside the restricted JavaScript runtime.

**Evidence status:** tooling-only; no repository or numerical evidence changed.

**Correction:** Used the container-backed runtime for local artifact inspection instead.

### Error F39-005 — Tool-orchestration syntax error during research-log update
A multi-file repository update script failed with a JavaScript syntax error before any GitHub write occurred.

**Evidence status:** tooling-only; no repository or numerical evidence changed.

**Correction:** The updates are being applied as separate deterministic file operations.


## 2026-10-06 — Phase 39 data-split correction before model training

### Error F39-006 — Workflow job-log lookup unavailable while job was running
Symptom: The Actions job-log endpoint returned a 404/blob-not-found response while the numerical job was still executing.

Evidence status: tooling-only; no numerical evidence changed.

Correction: Job status and step state were read from the workflow-run/job APIs instead; no inference was made from the missing log.

### Error F39-007 — Local wait command exceeded the container timeout
Symptom: A long blocking wait was requested from the container runtime and timed out.

Evidence status: tooling-only; no repository or numerical evidence changed.

Correction: Progress was checked through the GitHub Actions run-state API instead of blocking the runtime.

### Error F39-008 — Frozen-control-only dataset did not satisfy the preregistered development split
Finding: The first fixed-opportunity ledger contained only the 206 frozen Phase-38 opportunities beginning in 2024, but the Phase-39 preregistration specifies development through 2023, validation 2024–2025, and untouched 2026 holdout.

Evidence status: The first 206-row counterfactual result is superseded and is not used for model-training evidence.

Correction: The accepted Phase-32 workflow artifact is now used to construct a separate 2021–2023 development ledger (271 trades / 135 expiries), while the exact frozen 2024-01-11 through 2026-06-30 comparator remains authoritative for validation/holdout. The single 2024-01-04 trade is intentionally excluded so the Phase-38 comparator remains exact.

Prevention: Every future Phase-39 model run must assert the registered 271/172/34 development-validation-holdout row counts before training.

### Error F39-009 — Deterministic duplicate-quote handling required an explicit audit correction
Finding: Earlier repository phases recorded duplicate option quote rows at identical timestamp/type/strike combinations. The initial Phase-39 engine relied on implicit row ordering for entry quotes and therefore required an explicit deterministic rule.

Evidence status: The prior Step-1 result is superseded and is not used for model-training evidence.

Correction: Option snapshots are now sorted stably and deduplicated by timestamp/option type/strike, retaining the last observed row, matching the historical engine last-observation aggregation convention.

Prevention: The workflow now reruns the complete counterfactual engine after this correction and blocks progression unless the control arm still reconstructs within the registered tolerance.
