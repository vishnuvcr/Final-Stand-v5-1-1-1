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


### Error F39-010 — Counterfactual summary dictionary syntax regression
Run: 37436818874.

Symptom: The corrected counterfactual engine failed immediately before numerical execution with a Python SyntaxError because the generated summary dictionary lacked its final closing brace.

Evidence status: non-evidence; no numerical calculations were produced by the failed run.

Correction: The summary construction was repaired. The next automatic run must pass syntax, split-count and control-reconstruction assertions before its output is accepted.


### Error F39-011 — Phase 39 CI package-install stall
Runs: 37436916926 and related serialized runs.

Symptom: The numerical job remained in the pip-upgrade step with no progress update, blocking the corrected counterfactual calculation from starting.

Evidence status: CI-only; no numerical evidence changed.

Correction: The workflow no longer upgrades pip; it installs only the required packages with pip's version-check disabled. A single-run concurrency guard is enabled so stale runs cannot race on evidence files.


### Error F39-012 — Corrected Step-1 workflow was not retriggered by a status-only commit
Run: 37437005837 and subsequent branch state.

Symptom: The last known Phase-39 Step-1 Actions run was cancelled during serialized execution, while the later documentation/status commit did not match the workflow's path filter. Therefore the corrected 271/172/34 engine had not yet produced a fresh accepted CI result.

Evidence status: No numerical evidence was produced or accepted from this run state.

Correction: The counterfactual engine is being given explicit invariant checks and a new engine-path commit will be used to trigger a clean serialized Step-1 run from the current branch head.

Prevention: Treat the engine/workflow source commit as the explicit execution trigger for Step-1; do not infer execution from documentation-only commits.


### Error F39-013 — CI verification used exact equality on floating-point aggregate P&L
Run: 37437767581 (run #9).

Symptom: The corrected counterfactual engine completed successfully and produced 477 rows, but the verification step failed on exact equality between validation-plus-holdout control P&L and the frozen aggregate.

Cause: Binary floating-point addition can differ from the separately accumulated frozen aggregate at the final machine-precision digits even when both values are economically and numerically identical.

Evidence status: Non-evidence CI failure only. The engine output passed the substantive control-reconstruction checks: validation max absolute error ~9.1e-13 rupees and holdout max absolute error ~1.8e-12 rupees.

Correction: Replace exact equality in the workflow with a 1e-6 rupee absolute tolerance, consistent with the authoritative frozen-control benchmark check.

Prevention: Aggregate monetary verification in research CI will use explicit deterministic tolerances rather than raw float equality.


### Error F39-014 — Workflow job-log blob unavailable during long-running numerical step
Runs: 37437767581 and 37438127394.

Symptom: The workflow job remained in progress while the temporary job-log download endpoint returned BlobNotFound.

Evidence status: tooling-only; authoritative job status continued to report the numerical step as in progress. No inference was made from the missing logs.

Correction: Use workflow job state/step state while a job is running; inspect full decoded logs only after the job completes.

Prevention: Do not treat temporary log-unavailability as a numerical failure.


### Error F39-015 — Step 2 feature merge timestamp resolution mismatch
Run: 37439047106.

Symptom: The exact-entry feature builder completed source recovery and option/spot processing, then failed at the backward daily-source merge with Pandas MergeError: incompatible datetime64[us, Asia/Kolkata] and datetime64[ns, Asia/Kolkata].

Evidence status: non-evidence; no feature matrix was accepted.

Cause: PyArrow preserved Parquet timestamp columns at microsecond resolution while the constructed event timestamps were nanosecond resolution.

Correction: Normalize all point-in-time feature join keys to timezone-aware datetime64[ns, Asia/Kolkata] before merge_asof.

Prevention: All future Phase-39 feature joins will explicitly coerce both sides to the same timestamp resolution and timezone before any as-of merge.


### Error F39-015 — Phase-39 feature join timestamp-resolution mismatch
Run: 37439047106 (Step-2 run #1).

Symptom: Feature construction failed at the first cached global-data backward join with Pandas MergeError: `datetime64[us, Asia/Kolkata]` versus `datetime64[ns, Asia/Kolkata]`.

Cause: Cached Phase-35 Parquet files preserved microsecond-resolution timestamps while the newly generated entry keys used nanosecond resolution.

Evidence status: Non-evidence feature-pipeline failure. No model fitting or holdout evaluation occurred.

Correction: Normalize every point-in-time timestamp/join key to timezone-aware Asia/Kolkata nanosecond resolution before any merge_asof operation.

Prevention: Add timestamp-resolution normalization to the shared feature-pipeline boundary and retain the exact source timestamps separately for audit.


### Error F39-016 — Step 2b schema audit compared list and set incorrectly
Run: 37439897984.

Symptom: The schema audit rejected the four known fully-missing columns even though they exactly matched the registered exclusion set.

Cause: The assertion compared a list to a sorted set, causing a type/ordering mismatch.

Evidence status: audit-only failure; no feature evidence changed.

Correction: Compare the two exclusion collections as sets.

Prevention: Schema invariants will use set equality for unordered feature collections.


### Error F39-018 — Step 3 model runner expected target columns inside feature matrix
Run: 37440243604.

Symptom: The economic-model runner failed at the first model because call_net_rupees and put_net_rupees were correctly absent from the point-in-time feature matrix.

Cause: Step 2 explicitly separated labels/controls from predictors, but Step 3 initially assumed the outcome fields were embedded in the feature matrix.

Evidence status: non-evidence model execution failure; no model result accepted.

Correction: Step 3 now joins only the preregistered outcome/control columns from fixed_opportunity_ledger.csv to the point-in-time predictors by entry timestamp.

Prevention: Predictor matrices and economic outcomes remain physically separated; model runners must join them explicitly.


### Error F39-019 — Step 3 ledger join duplicated fields already retained as audit columns
Run: 37440404612.

Symptom: Joining the complete outcome/control schema created pandas suffix columns such as delta_pnl_call_minus_put_x because Step 2 intentionally retained audit copies of those fields.

Evidence status: non-evidence model execution failure; no model result accepted.

Correction: The Step-3 runner now joins only call_net_rupees and put_net_rupees from the fixed-opportunity ledger and uses the already-audited control/target columns from the feature matrix.

Prevention: Outcome/control joins will add only fields physically absent from the predictor file.


### Error F39-016 — Duplicate Step-3 model runner/workflow definitions
Finding: The Phase-39 branch contained two competing Step-3 economic-margin implementations: the established `research/phase39_economic_models.py` + `phase-39-step3-economic-models.yml`, and a later duplicate `phase39_economic_margin_models.py` + `phase-39-step3-economic-margin-models.yml`.

Evidence status: No duplicate-run numerical evidence was accepted. The duplicate path was still at workflow/implementation level and was not used for conclusions.

Correction: The duplicate runner and workflow were removed. The established Step-3 runner remains canonical and has been aligned to the locked Phase-39 model specification.

Prevention: One executable workflow and one executable runner are retained for each Phase-39 research step.

### Error F39-017 — Step-3 ledger join duplicated the economic target column
Run: 37440404612 (Step-3 run #1).

Symptom: The model runner failed with `delta_pnl_call_minus_put_x`/missing target access after joining the feature matrix to a ledger that already contained the target.

Cause: The join reintroduced a column already present in the feature matrix, creating pandas suffixes.

Evidence status: Non-evidence model-pipeline failure. No model result was produced.

Correction: The model runner now joins only the counterfactual outcome columns needed for realized action P&L, while retaining the feature matrix's locked target/control columns.

Prevention: Model-input joins will explicitly list only absent outcome columns and assert one-to-one row identity after merging.


### Error F39-020 — Stale deleted Step-3 workflow referenced a removed duplicate runner
Run: 37440696950.

Symptom: The consolidated Step-3 Actions job invoked `research/phase39_economic_margin_models.py`, which had been removed as the duplicate implementation, and failed with file-not-found before model fitting.

Evidence status: non-evidence CI wiring failure; no model result accepted.

Correction: The canonical `phase-39-step3-economic-models.yml` workflow is now explicitly hardened and triggered; it invokes the retained `research/phase39_economic_models.py` runner.

Prevention: Each phase step will maintain one workflow-to-runner mapping and the workflow verification will assert the expected output contract.


### Error F39-018 — Counterfactual outcome columns leaked into Step-3 predictors
Run: 37440844079 (Step-3 canonical run #6).

Symptom: The persisted locked feature list contained `call_net_rupees` and `put_net_rupees`, which are realized counterfactual outcome variables and therefore prohibited predictors.

Impact: The reported validation uplift from that run is **invalid/non-evidence**. The near-perfect margin fit and very large uplift are explained by direct target leakage and must not be interpreted as predictive performance.

Correction: Explicitly add `call_net_rupees` and `put_net_rupees` to the model LABELS/exclusion set. The Step-3 workflow will also assert that no realized-outcome columns appear in the locked feature manifest.

Prevention: Every future model workflow must perform an explicit predictor blacklist audit against all realized P&L/outcome columns before model fitting is accepted.


### Error F39-021 — CRITICAL: Step-3 first model screen leaked counterfactual outcome columns
Run: 37440844079.

Symptom: The persisted locked feature list contained `call_net_rupees` and `put_net_rupees`, and the seven model results showed an impossible near-oracle validation uplift of ₹406,156.27.

Cause: Step-3 joined the CALL/PUT realized outcomes from the fixed-opportunity ledger before feature selection, but the feature exclusion set did not include those two outcome columns.

Evidence status: **INVALID / NON-EVIDENCE.** All Step-3 model outputs from run 37440844079 are explicitly superseded and must not be cited as model performance.

Correction: Add `call_net_rupees` and `put_net_rupees` to the forbidden outcome/control set and assert that no realized outcome field can enter the locked predictor list.

Prevention: A hard feature-leakage assertion now blocks model training whenever any realized action P&L or control/target column appears among predictors. The result status is invalidated until a clean rerun passes this assertion.


### Error F39-019 — Initial sequential replay loop reused earlier-expiry timestamps
Finding: The first draft of the sequential policy engine built each expiry's timeline from the global sample start rather than from the immediately preceding expiry boundary.

Evidence status: Non-evidence implementation issue caught before sequential execution.

Correction: Each expiry window is now anchored to the immediately preceding expected weekly expiry (or the global research start for the first expiry), matching the audited Phase-32 contract-window convention.

Prevention: Sequential replay uses explicit per-expiry window boundaries and never derives a contract window from the last processed file or global sample start.

### Error F39-020 — Sequential replay option selector required explicit expiry timestamp metadata
Finding: The shared nearest-delta selector expects `expiry_ts` in the option snapshot, while the feature-matrix loader did not add it.

Evidence status: Non-evidence implementation issue caught before sequential execution.

Correction: Every lazily loaded option file now receives deterministic `expiry_ts = expiry + 15:30 IST` metadata.

Prevention: Shared market-data adapters will expose the complete contract timestamp schema required by all downstream selectors.


### Error F39-021 — Sequential replay spot-column schema mismatch
Run: 37441450024 (Step-4 run #1).

Symptom: The sequential replay failed on the first selected arm because the shared `run_arm()` execution routine expects NIFTY spot data in a `spot` column, while the sequential loader exposed only `close`.

Evidence status: Non-evidence runtime failure. No sequential trade result was produced.

Correction: The sequential spot adapter now retains the original `close` field for feature construction and also exposes an identical `spot` field for the shared execution engine.

Prevention: Shared market-data adapters will expose both semantic aliases where downstream engines use different field names.


### Error F39-022 — Sequential replay passed NIFTY close-only frame to canonical run_arm
Run: 37441450024.

Symptom: Step-4 sequential replay failed in the canonical counterfactual arm engine with KeyError: `spot`.

Cause: The sequential replay adapter loaded the NIFTY source with its historical `close` field, while `run_arm()` requires the canonical normalized `spot` field.

Evidence status: non-evidence sequential implementation failure; no policy result accepted.

Correction: The replay adapter now creates deterministic `spot = close` from the NIFTY index source before calling `run_arm()`.

Prevention: Market-data adapters will expose the canonical engine schema (`timestamp`, `spot`) before handing data to shared execution functions.


### Error F39-022 — Sequential replay referenced the wrong locked-feature manifest path
Run: 37441598449 (Step-4 run #2).

Symptom: Replay failed when loading the locked feature list from `results/phase39_features/locked_feature_list.json`.

Cause: The canonical Step-3 model manifest is stored under `results/phase39_models/locked_feature_list.json`, but the sequential script referenced the Step-2 feature directory.

Evidence status: Non-evidence runtime failure. No sequential result was produced.

Correction: Sequential replay now reads the exact locked Step-3 feature manifest, and the Step-4 workflow explicitly depends on that file.

Prevention: Model-dependent workflows will reference the canonical model artifact path directly and verify its existence before execution.


### Error F39-024 — Optional next-expiry quote file absent
Run: 37441878544.

Symptom: Sequential replay failed when constructing point-in-time features because the optional next-expiry file `options/NIFTY/2021-11-04.parquet` does not exist in the Hugging Face dataset.

Evidence status: non-evidence feature-loading failure; no sequential result accepted.

Cause: The replay treated an optional next-contract term-structure input as mandatory.

Correction: Missing next-expiry files now produce an empty optional frame, preserving the current-expiry quote data and leaving the corresponding term-structure features unavailable/NaN. Required current-expiry files remain fatal.

Prevention: Optional cross-contract features will distinguish missing historical coverage from execution-data failure; no synthetic forward fill or imputation is applied at the data-loader boundary.


### Error F39-023 — Sequential replay attempted a missing historical option-expiry file
Run: 37441878544 (Step-4 run #3).

Symptom: Replay failed when the point-in-time feature builder requested `options/NIFTY/2021-11-04.parquet`, which is absent from the public primary dataset.

Cause: The replay's expected calendar included every scheduled weekly expiry, but it did not first filter the calendar against the dataset's actually available expiry files.

Evidence status: Non-evidence runtime failure. No sequential policy result was produced.

Correction: Step 4 now enumerates the available NIFTY option files, processes only available expected expiries, and separately retains the complete expected calendar for contract-window anchoring. A missing option file therefore cannot enlarge a later contract's data window.

Prevention: Sequential replay follows the same available-file/previous-expected-expiry boundary convention already audited in Phase 32.


### Error F39-025 — Sequential replay omitted unavailable optional feature columns instead of materializing NaN
Run: 37442175504.

Symptom: GAM prediction failed because `next_atm_straddle`, `next_atm_iv_skew`, and `iv_term_premium_ratio` were absent from a test-row DataFrame when the next-expiry contract was unavailable.

Cause: The point-in-time feature schema defines those columns as valid optional predictors, but the sequential row builder omitted the columns entirely when no next-expiry source existed.

Evidence status: non-evidence; no policy result accepted.

Correction: Sequential GAM fitting now reindexes both training and test matrices to the locked feature list before imputation, materializing unavailable predictors as NaN for the model's fitted imputer.

Prevention: All sequential replay model inputs will be reindexed to the locked feature manifest before numerical transforms.


### Error F39-024 — Sequential replay omitted optional next-expiry feature columns
Run: 37442175504 (Step-4 run #5).

Symptom: The locked GAM model requested `next_atm_straddle`, `next_atm_iv_skew` and `iv_term_premium_ratio` at an entry where the next contract had no usable quote, causing a missing-column KeyError.

Cause: The point-in-time feature builder correctly treated missing next-contract observations as missing values, but the sequential replay did not materialize the locked feature columns when all next-contract values were unavailable for a row.

Evidence status: Non-evidence runtime failure. No sequential policy result was produced.

Correction: Every sequential feature row now materializes the complete locked feature schema and fills unavailable optional predictors with NaN, allowing the locked training-window imputer to handle them without changing model inputs.

Prevention: Sequential replay will assert the exact locked feature schema before every prediction.


### Error F39-025 — Sequential replay summary treated control file paths as DataFrames
Run: 37442475815 (Step-4 run #7).

Symptom: The full sequential simulation reached the post-replay aggregation stage, then failed with `AttributeError: 'PosixPath' object has no attribute 'assign'`.

Cause: `DEV_CONTROL` and `FROZEN_CONTROL` were defined as pathlib paths and were passed directly to pandas `concat/assign` operations instead of being loaded into DataFrames.

Evidence status: Non-evidence summary-stage runtime failure. The sequential replay result was not accepted because the workflow failed before producing the final verified summary.

Correction: The summary stage now explicitly reads both control CSVs into DataFrames before adding period labels and computing the policy-versus-control comparison.

Prevention: Repository file paths will remain distinct from loaded DataFrames throughout sequential analysis code.


### Error F39-026 — Sequential paired-bootstrap column name mismatch
Run: 37443241411 (Step-4 run #8).

Symptom: The complete sequential replay reached the paired-bootstrap stage, then failed with `AttributeError: DataFrameGroupBy has no attribute net`.

Cause: The policy replay stores realized P&L as `policy_net_rupees`, while the control ledger stores `net_rupees`; the bootstrap helper assumed a shared `net` alias.

Evidence status: Non-evidence statistical-postprocessing failure. The completed replay was not accepted because CI verification/persistence did not run.

Correction: The bootstrap helper now explicitly aggregates `policy_net_rupees` for the policy stream and `net_rupees` for the control stream.

Prevention: Paired statistical helpers will use explicit schema names rather than implicit aliases.


### Error F39-027 — Step-4 period labeling used entry date instead of registered expiry split
Finding: The first completed sequential replay assigned development/validation/holdout using `entry_ts`. This produced an apparent 173/33 validation/holdout control split even though the authoritative Phase-39 fixed-opportunity ledger is 172/34.

Cause: Some late-2025 entries belong to contracts expiring in 2026 and therefore must be holdout observations under the registered expiry-based split.

Evidence status: The underlying sequential trade simulation from run 37443885462 remains valid, but its period-level comparative summary is rejected for conclusions until relabeled.

Correction: Periods are now assigned by expiry year: <=2023 development, 2024-2025 validation, 2026 holdout. The workflow now asserts the authoritative 271/172/34 control counts.

Prevention: All Phase-39 split logic uses the preregistered expiry-period boundary where a trade can span calendar years.


### Error F39-028 — Step-3 development OOF feature selection used future development observations
Finding: The original Step-3 screen selected the feature list from the complete development period before generating chronological development OOF predictions.

Cause: The threshold-selection OOF loop reused a development-wide feature list rather than re-selecting eligible predictors from each expanding training window.

Evidence status: Step-3 threshold/model-selection results from runs before this correction are **superseded**. The validation/holdout feature lock itself did not use holdout data, but the development OOF threshold-selection evidence was not strictly point-in-time.

Correction: Development OOF now recomputes feature eligibility from the current chronological training window before every OOF batch. Validation retains a feature lock selected from the complete development period, which is permitted by the preregistered train/validation design.

Prevention: Any future OOF selection step must derive feature eligibility, imputation, scaling and hyperparameters solely from observations preceding the prediction timestamp.


### Error F39-029 — Initial Step-5 BOCPD gate did not apply threshold consistently
Finding: The initial Step-5 draft stored only a binary gate generated at one fixed 0.35 threshold, while the selection loop nominally evaluated multiple change-point thresholds.

Evidence status: Step-5 run(s) using that draft are non-evidence and must not be used for conclusions.

Correction: The revised runner persists the actual BOCPD posterior change probability and selects the registered threshold from the development OOF stream, then applies the same frozen threshold to validation.

Prevention: Regime-gate hyperparameters must be represented explicitly in the saved prediction artifact and applied identically across development selection and validation replay.


### Error F39-030 — Step-5 fixed-opportunity join duplicated the economic target
Run: 37445670495 (Step-5 run #2).

Symptom: DTW execution failed because `delta_pnl_call_minus_put` had been suffixed to `_x/_y` after the feature/outcome merge.

Cause: The Step-2 feature matrix already retains the fixed-opportunity target for audit, so Step 5 re-imported the same target from the ledger unnecessarily.

Evidence status: Non-evidence runtime failure. No Step-5 model result was produced.

Correction: The Step-5 outcome join now imports only the missing control and realized-action P&L columns and retains the single target column already present in the feature matrix.

Prevention: Advanced-family joins will explicitly import only outcome columns absent from the feature matrix.


### Error F39-031 — Step-5 join duplicated canonical control columns
Run: 37445960376 (Step-5 run #3).

Symptom: The fixed-opportunity screen failed because `control_direction` and `control_net_rupees` were absent after the merge and therefore unavailable to the model-evaluation block.

Cause: Those canonical control columns are already retained in the Step-2 feature matrix; importing them again from the ledger created pandas suffixes and removed the expected unsuffixed names.

Evidence status: Non-evidence runtime failure. No Step-5 result was produced.

Correction: Step 5 now joins only `call_net_rupees` and `put_net_rupees`, while retaining the feature matrix's existing control columns.

Prevention: Step-5 and later joins will import only columns confirmed absent from the base feature layer.


### Error F39-032 — Step-5 NumPy/Pandas array conversion mismatch
Run: 37446241028 (Step-5 run #4).

Symptom: The fixed-opportunity screen failed when `np.where(...)` returned an ndarray and the code attempted to call pandas `to_numpy()` on it.

Evidence status: Non-evidence implementation failure. No Step-5 results were accepted.

Correction: Realized action P&L arrays are now normalized with `np.asarray` before arithmetic and aggregation.

Prevention: Advanced model evaluation will keep explicit NumPy/Pandas type boundaries.


### Error F39-033 — Step-5 automated array patch malformed the evaluator function
Runs: 37446514386 and predecessor Step-5 iterations.

Symptom: The advanced-family evaluator contained unmatched parentheses and incomplete action-assignment expressions after an automated NumPy/Pandas normalization edit.

Evidence status: Non-evidence code-generation failure. No Step-5 result was accepted.

Correction: The complete `evaluate()` function was replaced with a clean explicit implementation covering OOF threshold selection, BOCPD gating, validation replay and summary metrics.

Prevention: For complex evaluator patches, replace the complete affected function rather than applying multiple fragile text substitutions.


### Error F39-034 — Step-5 advanced-family runner required multiple schema and evaluator corrections
Step-5 iterations 2-5 failed before evidence due to duplicate target/control columns, NumPy/Pandas boundary handling, and a malformed evaluator patch. All failed runs are non-evidence.

Correction: The final Step-5 evaluator was replaced wholesale with deterministic OOF/validation logic. Run 37446811261 passed all verification checks and is the only accepted Step-5 result.


### Error F39-035 — Initial Step-6 Hedge implementation was computationally excessive
Run: 37447433376 (Step-6 run #1).

Symptom: The workflow was cancelled while fitting the model one observation at a time across the full development history; no result was produced.

Cause: Repeated spline-model fits multiplied the development computation unnecessarily for an online expert-aggregation screen.

Evidence status: Non-evidence tooling/computation failure.

Correction: Step 6 now fits the economic-margin model once per chronological 20-observation batch and updates Hedge weights after each realized observation. The first 100 warm-up observations remain control-only.

Prevention: Chronological expert-aggregation screens will batch expensive predictive-model fits while preserving per-observation reward updates and causal ordering.


### Error F39-034 — Step-6 expert aggregation array conversion mismatch
Run: 37447505823 (Step-6 run #1).

Symptom: The full-information expert aggregation diagnostic failed when a NumPy `where` result was treated as a pandas Series.

Evidence status: Non-evidence runtime failure. No Step-6 output was accepted.

Correction: Selected expert P&L is now explicitly represented as a NumPy array before aggregation.

Prevention: Keep explicit array types at the expert-aggregation evaluation boundary.


### Error F39-036 — Step-6 verifier incorrectly rejected a valid negative research result
Run: 37447719614 (Step-6 run #2).

Symptom: The Hedge model finished successfully with a validation result of **−₹416.82**, but the workflow verifier failed because it required `validation_uplift >= 0`.

Cause: A research-outcome expectation was encoded as a CI invariant. Negative results are valid evidence and must be recorded, not treated as workflow failures.

Evidence status: The numerical Hedge result is valid research evidence; the run's final verification/persistence step was the only failure.

Correction: Removed the non-negative-uplift assertion. The verifier now checks only schema, completion, parameter-grid and holdout-isolation invariants.

Prevention: CI verification will never encode directional expectations about numerical research outcomes.
