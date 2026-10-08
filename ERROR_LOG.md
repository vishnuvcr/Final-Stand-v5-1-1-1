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


### Error F39-037 — Step-7 workflow omitted required scikit-learn dependency
Run: 37448200891 (Step-7 run #1).

Symptom: The symbolic runner failed immediately with `ModuleNotFoundError: No module named 'sklearn'`.

Evidence status: Non-evidence dependency failure.

Correction: Step-7 workflow now installs `scikit-learn`, matching the script's SimpleImputer and StandardScaler imports.

Prevention: Each workflow dependency list will be checked against the runner imports before execution.


### Error F39-038 — Step-7 symbolic grammar misclassified binary expressions
Run: 37448412461 (Step-7 run #2).

Symptom: The symbolic evaluator raised `ValueError: too many values to unpack` when processing a binary expression.

Cause: Unary and binary expressions are both stored as one-element lists, so `len(expr)==1` was not sufficient to identify the unary grammar form.

Evidence status: Non-evidence implementation failure.

Correction: The evaluator now detects unary expressions by the inner tuple length (2 fields versus 5 for binary expressions).

Prevention: Grammar nodes will use explicit expression-type tags in later structural-search code.


### Error F39-039 — Sequential symbolic replay contained a literal newline escape
Run: 37449008339 (Step-7 sequential-symbolic run #1).

Symptom: Python raised `SyntaxError: unexpected character after line continuation character` on the combined feature-path assignment.

Cause: A repository text transformation inserted the characters `\\n` literally instead of creating a new source line.

Evidence status: Non-evidence syntax failure.

Correction: The two assignments will be emitted as separate Python lines.

Prevention: Newly generated Python files will be syntax-checked structurally before workflow execution.


### Error F39-040 — Sequential symbolic replay used the wrong training-ledger path
Finding: After fixing the source-line syntax, the symbolic replay would still have attempted to fit its coefficient from the canonical control CSV, which does not contain `delta_pnl_call_minus_put`.

Evidence status: No sequential evidence was produced from this version.

Correction: The replay now fits the symbolic coefficient and residual uncertainty from the point-in-time feature matrix joined to the accepted Phase-39 fixed-opportunity counterfactual ledger.

Prevention: Counterfactual-target models must train exclusively from the fixed-opportunity ledger, never the one-arm control trade CSV.


### Error F39-041 — Sequential symbolic workflow omitted copied-script scikit-learn dependency
Run: 37449411300 (Step-7 sequential-symbolic run #2).

Symptom: The replay failed at import time with `ModuleNotFoundError: No module named 'sklearn'`.

Cause: The sequential symbolic script inherits non-used sklearn imports from the audited base replay engine.

Evidence status: Non-evidence dependency failure.

Correction: Step-7 sequential-symbolic workflow now installs scikit-learn as part of the inherited engine dependency set.

Prevention: Copied/derived replay engines will be dependency-audited against all imports before execution.


### Error F39-042 — Sequential symbolic training duplicated the economic target during ledger cross-check
Run: 37449790870 (Step-7 sequential-symbolic run #3).

Symptom: Training failed with missing `delta_pnl_call_minus_put` after the feature/ledger merge because the target had been suffixed.

Cause: The accepted point-in-time feature matrix already carries the economic target for audit, while the fixed ledger contains the same target.

Evidence status: Non-evidence runtime failure.

Correction: The replay now retains the target from the feature matrix and imports the ledger target under an explicit suffix only for a numerical equality audit; a hard <1e-8 rupee target-match assertion is applied.

Prevention: Any dual-source target cross-check will use explicit suffixes and an equality invariant rather than relying on pandas's default column retention.


### Error F39-043 — Sequential/fixed propensity-treatment count mismatch
Run: 37451770011 (propensity run #1).

Symptom: The propensity runner asserted seven mapped overrides, but the sequential replay contains 479 trades versus 477 fixed opportunities; not every sequential entry is necessarily represented in the fixed panel.

Evidence status: Non-evidence data-mapping failure.

Correction: Propensity matching now explicitly distinguishes total sequential overrides from overrides mapped to the fixed-opportunity panel and reports any unmapped overrides. No treatment is inferred for an unmatched timestamp.

Prevention: All causal/observational analyses will audit exact row-level mapping before statistical estimation.


### Error F39-044 — Development-only propensity fitting impossible because Sparse-GAM treatment is absent early
Runs: 37451770011 and 37451980628.

Finding: The Sparse-GAM sequential override set is 3 development, 3 validation and 1 holdout. The initial development-only propensity design therefore had an insufficient treatment class.

Correction: The observational propensity model is now fit across the complete fixed-opportunity panel using pre-entry covariates only, while matching is performed separately within development, validation and holdout periods.

Interpretation: This is a descriptive matched-scoring/robustness analysis, not a causal identification result, because positivity is weak and treatment is generated by a deterministic policy.


### Error F39-045 — Propensity treatment labels pointed to the superseding symbolic replay
Run: 37452211468 (propensity run #3).

Symptom: The propensity analysis saw zero treated opportunities because it read the later symbolic sequential replay instead of the audited Sparse-GAM override file.

Evidence status: Non-evidence source-selection failure.

Correction: Treatment labels now come from results/phase39_sequential_policy_audit/override_audit.csv, the authoritative seven-override Sparse-GAM audit.

Prevention: Candidate-specific analyses must use candidate-specific immutable result artifacts rather than generic sequential filenames.


### Error F39-046 — Stale development-only propensity assignment remained after design change
Run: 37452359631 (propensity run #4).

Symptom: Runtime NameError for ps_dev after the model had been changed to a full-panel propensity fit.

Evidence status: Non-evidence implementation cleanup failure.

Correction: Removed the obsolete ps_dev/ps_val/ps_hold assignment.


### Error F39-047 — Propensity summary retained obsolete sequential-source variable
Run: 37452505360 (propensity run #5).

Symptom: NameError for variable s after switching treatment labels to the audited Sparse-GAM override file.

Evidence status: Non-evidence summary-stage failure; matching calculations had already executed.

Correction: Final summary now reports the audited override count and mapped fixed-opportunity count directly.


### Error F39-048 — Propensity result rows lacked period field
Run: 37452652520 (propensity run #6).

Symptom: Final summary lookup raised KeyError for period after matching had completed.

Evidence status: Non-evidence reporting failure.

Correction: Each propensity result row now stores its period explicitly.


### Error F39-049 — CI still expected seven mapped fixed-opportunity overrides
Run: 37452805894 (propensity run #7).

Finding: The audited Sparse-GAM policy has seven sequential overrides but only five exact timestamp matches in the 477-row fixed-opportunity panel. The other two cannot be used in fixed-opportunity propensity matching.

Evidence status: Statistical calculation completed; only the CI schema gate failed.

Correction: Verification will distinguish seven audited sequential overrides from five mapped fixed-opportunity treated observations.


### Error F39-050 — Propensity verifier row count was stale after caliper expansion
Run: 37452962833 (propensity run #9).

The statistical analysis completed successfully, but CI expected 12 rows after the caliper grid was expanded to seven values, producing 21 rows.

Evidence status: valid propensity results; verification-only failure.

Correction: verifier updated to expect 21 rows.


## 2026-10-06 — Phase 40 initialization

### Error F40-001 — Initial ensemble engine required deterministic-grid corrections before execution
The first draft of the Phase-40 engine contained a validation-grid accumulation bug and mixed global-VIX thresholds with India-VIX values. It was not executed as evidence.

**Evidence status:** non-evidence implementation issue.

**Correction:** The engine was rewritten so all 1,764 candidates are retained, India-VIX development thresholds are used for India-VIX routing, neutral VIX votes are treated as abstentions in majority voting, and the top-10 freeze occurs only after the complete validation grid is written.

**Prevention:** CI asserts exactly 1,764 grid rows and exactly 10 frozen holdout candidates before any result is accepted.


### Error F40-002 — GitHub Actions heredoc indentation failure
**Run:** 37454503074.

The India-VIX cache step failed before numerical execution because the YAML block scalar preserved indentation before the shell heredoc terminator, so Bash did not recognize the closing `PY` marker.

**Evidence status:** non-evidence CI failure; no model calculations ran.

**Correction:** Replaced the inline heredoc with a deterministic `python -c` acquisition command and retained the cache-write/push step.

**Prevention:** Avoid shell heredoc terminators inside indented YAML run blocks unless indentation is explicitly validated.


### Error F40-003 — India-VIX cache push race
**Run:** 37454627680.

The India-VIX download itself succeeded and produced 1,590 cached rows locally, but the workflow attempted to push that cache from a stale checkout. Connector-side documentation commits had advanced the remote branch, so GitHub rejected the cache push as non-fast-forward.

**Evidence status:** non-evidence CI persistence failure; the numerical screen did not start.

**Correction:** The workflow no longer pushes from the acquisition step. The cache is kept in the working tree and is committed together with research results only after a fresh `git pull --rebase` in the final persistence step.

**Prevention:** All workflow-generated artifacts are now persisted in one race-safe final commit.


### Error F40-004 — Phase-32 replay return-arity mismatch
**Run:** 37454752168.

The ensemble engine called `base.run_expiry()` expecting two return values, but the canonical function returns three: trades, skips and updated direction state.

**Evidence status:** non-evidence runtime failure; no ensemble candidate was evaluated.

**Correction:** The Phase-40 arm-cache replay now explicitly unpacks all three values.

**Prevention:** Reused research engines must be checked against their current function signature before integration.


### Error F40-005 — Candidate arm replay reached an unavailable scheduled expiry
**Run:** 37454846921.

The canonical weekly calendar includes 07-Apr-2025, but the Hugging Face option dataset does not contain that file. The run stopped while rebuilding the arm cache.

**Evidence status:** non-evidence; no ensemble grid result was written.

**Correction:** Phase 40 now defines its study-expiry universe from the already accepted Phase-39 fixed-opportunity ledger, which excludes unavailable option files. The authoritative control comparison is read from the frozen Phase-38 expiry-level control rather than reconstructed during the ensemble screen.

**Prevention:** Future derived phases must inherit the accepted study-expiry ledger before requesting raw option files.


### Error F40-006 — Frozen-control variable removed during comparator refactor
**Run:** 37455126781.

The exhaustive 1,764-candidate calculation itself completed, but final scoring failed with `NameError: frozen_control is not defined` because a prior refactor removed the comparator initialization while changing from reconstructed control to the frozen Phase-38 control.

**Evidence status:** non-evidence; no grid result from this run is accepted.

**Correction:** Initialize and audit the frozen expiry-level control before grid scoring, and compare each candidate only on the exact common study expiries covered by the model-probability cache.

**Prevention:** Comparator initialization now occurs before candidate scoring and the workflow asserts zero missing control expiries.


### Error F40-007 — Final artifact persistence attempted rebase before staging generated files
**Run:** 37455920220.

The 1,764-candidate numerical screen and verification both succeeded. Persistence failed because the workflow ran `git pull --rebase` while the India-VIX cache and result files were unstaged.

**Evidence status:** numerical evidence was calculated successfully but was not persisted by this run; it is not treated as repository-accepted evidence until the corrected persistence run succeeds.

**Correction:** The workflow now stages and commits generated artifacts first, then rebases that local commit onto the latest branch and pushes.

**Prevention:** Generated workflow artifacts must be committed before rebasing a concurrently modified research branch.


### Error F40-008 — VIX-gated candidates were initially implemented as no-trade rather than canonical fallback
**Finding:** The first accepted grid implementation encoded an inactive VIX gate as signal 0, and the candidate scorer skipped that expiry. The Phase-40 pre-registration specifies that an inactive VIX gate must fall back to the canonical stateful direction, not suppress trading.

**Evidence status:** The resulting 1,764-grid numerical artifacts are **superseded** and must not be used for the Phase-40 conclusion.

**Correction:** The engine now reconstructs the point-in-time canonical direction from the accepted Phase-39 control ledger and uses that direction whenever the VIX gate is inactive.

**Prevention:** Every series/gating architecture now has an explicit fallback-state invariant checked before screening.


### Error F40-009 — Duplicate ensemble aliases could consume multiple holdout slots
The validation grid contained many parameterizations (different aggregators/subsets) with exactly the same expiry-level direction sequence. Treating those aliases as independent holdout candidates would exaggerate effective model diversity.

**Evidence status:** The just-completed VIX-gated grid is retained as validation screening evidence, but its raw top-10 holdout list is superseded.

**Correction:** Phase 40 now hashes the validation expiry-level direction sequence and selects the top 10 **unique policies** for holdout evaluation. All 1,764 raw combinations remain reported.

**Prevention:** Future ensemble phases will distinguish specification count from unique decision-policy count.


### Error F40-010 — Paired-inference control index timezone handling
**Run:** 37456994909.

The ensemble grid and unique top-10 selection completed, but inference failed when attempting to localize an already timezone-aware frozen-control expiry index.

**Evidence status:** non-evidence inference failure; no statistical conclusion was written.

**Correction:** The inference engine now checks whether the control index is timezone-naive before localizing; aware timestamps are converted to the canonical timezone.

**Prevention:** All inference joins now use the same explicit timezone-normalization helper.


### Error F40-011 — Exact sequential replay accidentally included 9 prediction-missing expiries
**Run:** 37457649157.

The exact replay reused the broader Phase-39 control study-expiry list but failed to apply the Phase-40 model-prediction-date filter used by the exhaustive grid. Nine expiries therefore entered through the default fallback direction.

**Evidence status:** the sequential replay completed technically, but its statistics are **superseded and not accepted**.

**Correction:** The replay now filters the study universe to the exact 93 expiry dates covered by the cached Phase-36 expert predictions and asserts the count.

**Prevention:** Every downstream replay must inherit both the canonical study-expiry list and the exact model-coverage mask used by the selection stage.


## 2026-10-06 — Phase 41 initialization
- No numerical evidence has been accepted yet.
- The phase begins only after auditing the completed Phase-40 closeout and the Phase-39 counterfactual/feature artifacts.
- An implementation correction was made before execution: propensity-score fitting will use only pre-evaluation history (development for validation diagnostics; development+validation for holdout diagnostics), matching the pre-registration's chronology.
- This correction changes no research parameter, outcome definition or candidate universe.


## 2026-10-06 — Phase 41 Run 37463493504

### Error F41-001 — Sequential replay missing sparse live feature columns

**Symptom:** Step 1 completed, but Step 2 failed when the live point-in-time feature row lacked the three flow/sentiment columns `flow_fii_net_z20`, `flow_dii_net_z20` and `flow_flow_sentiment`. The model matrix constructor indexed those columns directly and raised a KeyError.

**Evidence status:** The Step-2 run produced no accepted sequential evidence. Step-1 fixed-opportunity artifacts are valid and persisted, but the phase remains open.

**Cause:** The fixed feature matrix contains the registered columns, while live source reconstruction can legitimately yield an entirely unavailable auxiliary source for a particular timestamp. The replay constructor did not preserve the full fixed feature schema before imputation.

**Correction:** `Xify()` now uses explicit reindexing to the frozen feature schema and fills unavailable columns with NaN so the pre-registered imputer handles them. No candidate, feature definition, threshold, split or trading rule changed.

**Prevention:** All future sequential feature builders must preserve the exact registered matrix schema at the engine boundary before model prediction.



## 2026-10-06 — Phase 41 Run 37463984884 runtime optimization

### Error F41-002 — Sequential replay unnecessarily refit a policy proven to be an exact no-op

**Finding:** The fixed-opportunity screen showed zero overrides for all three frozen candidates across development, validation and holdout. The first corrected sequential runner still refit the model at every historical entry before discovering that no action change could occur.

**Evidence status:** The run produced no accepted sequential evidence and is superseded.

**Correction:** Sequential replay now checks the frozen full-panel override counts first. When all three splits have zero overrides, the candidate is represented by the exact canonical stateful ledger because action, exit path, future availability and state are unchanged. This is an identity proof, not a parameter relaxation. Workflow concurrency was changed to cancel a superseded expensive run when the corrected runner is pushed.

**Prevention:** Future phases must use a pre-replay identity invariant to avoid recomputing a policy already proven to be exactly identical to the control.


## 2026-10-06 — Phase 41 implementation correction before numerical execution
- Propensity-score fitting in the first draft was incorrectly fit inside each evaluation split. The code was corrected before any accepted numerical run: validation matching now fits propensity on development history only; holdout matching fits on development+validation history only.
- This was a methodology-chronology correction only; no research parameter, outcome definition or trading rule changed.

## 2026-10-06 — Phase 41 accepted execution status
- Numerical evidence is accepted only from the GitHub Actions run that completes preflight, the frozen 24-variant screen, exact sequential replay and closeout without protocol changes.


## 2026-10-06 — Phase 41 implementation correction before numerical execution
- Propensity-score fitting in the first draft was incorrectly fit inside each evaluation split. The code was corrected before any accepted numerical run: validation matching now fits propensity on development history only; holdout matching fits on development+validation history only.
- This was a methodology-chronology correction only; no research parameter, outcome definition or trading rule changed.

## 2026-10-06 — Phase 41 accepted execution status
- Numerical evidence is accepted only from the GitHub Actions run that completes preflight, the frozen 24-variant screen, exact sequential replay and closeout without protocol changes.


## 2026-10-06 — Phase 42 Run 37467480459

### Error F42-001 — Cost-stress guard syntax error

**Symptom:** The syntax audit failed before any Phase-42 numerical screen. The cost-stress column check used an invalid boolean expression combining `not` and bitwise OR.

**Evidence status:** No numerical evidence was produced; the run is rejected and superseded.

**Correction:** Replaced the expression with explicit parenthesized boolean `or` logic. Research parameters, candidate universe, data and decision gates are unchanged.

**Prevention:** Keep preflight syntax compilation mandatory before any expensive phase execution.


## 2026-10-06 — Phase 42 Run 37467624298

### Error F42-002 — Propensity diagnostic state schema omitted India VIX return

**Symptom:** Step 1 numerical screen reached the diagnostic stage but failed because the preregistered propensity state vector requested `india_vix_ret1`, while the policy frame written by the screen omitted that column.

**Evidence status:** No Phase-42 numerical evidence is accepted from this run because the registered workflow did not complete.

**Correction:** Added `india_vix_ret1` to the policy output frame. This preserves the preregistered state vector and does not change the candidate universe, model, thresholds, split, outcome or trading rule.

**Prevention:** Add an explicit schema assertion for all propensity state features before executing propensity diagnostics.


## 2026-10-06 — Phase 42 closeout
- Accepted evidence is limited to the successful Phase-42 workflow after preflight, syntax audit, fixed-opportunity selection, sequential replay and closeout.


## F43-001 — 2026-10-06 — Registration payload syntax incident
- **Symptom:** Initial Phase-43 registration write failed with a JavaScript `SyntaxError` caused by an unescaped content delimiter in the orchestration payload.
- **Evidence status:** No repository file was changed by the failed call; no numerical run occurred.
- **Correction:** Reissued the write with safe string construction. Phase43 plan, pre-registration, status and literature review were successfully committed.
- **Prevention:** Use payload-safe string generation for repository writes and validate syntax before issuing GitHub mutations.


## F43-002 — 2026-10-06 — Workflow expression escaping incident
- **Symptom:** The first workflow/bridge registration used a raw JavaScript template string, so GitHub Actions expressions were persisted with a literal backslash before `${{ ... }}`.
- **Evidence status:** No numerical execution was accepted; no strategy result was produced.
- **Correction:** The workflow files were rewritten with the intended GitHub expression syntax and a new bridge trigger will be issued.
- **Prevention:** Treat GitHub workflow expression syntax as a separate validation target from JavaScript string escaping and inspect the committed YAML before triggering.

## F43-RUN-37474661050 — numerical execution failure
- Exit code: 1. Failed output is non-evidence.


## F43-003 — 2026-10-06 — Finalizer payload delimiter incident
- Initial attempt to persist the Phase-43 post-run manuscript finalizer failed before repository write because a JavaScript template string contained Markdown backtick delimiters from the Python manuscript template.
- No numerical workflow or research artifact was affected.
- Correction: remove embedded Markdown backticks from the generator payload and persist the finalizer separately.


## F43-004 — 2026-10-06 — Invalid regime inference implementation
- The first Phase-43 inference table compared a VIX-regime subset against the same rows from the ALL sample, making every paired difference identically zero.
- **Classification:** statistical implementation defect; the raw strategy trade matrix and gross/net P&L calculations are retained as valid raw evidence, but the first inference table is invalid and must not support conclusions.
- **Correction:** a new postprocessor compares each VIX regime against the complementary non-regime expiry observations within the same strategy and recomputes 10,000-resample confidence intervals, permutation p-values and Holm-adjusted values.
- The corrected postprocess also reapplies the preregistered validation/cost/drawdown gates before any router or holdout promotion.


## F43-005 — 2026-10-06 — Unbounded benchmark entered corrected postprocess
- **Finding:** The first corrected postprocessor excluded calendars but did not exclude the four preregistered unbounded structures from the promotion benchmark universe. This caused `put_ratio_1x2` to become the unconditional benchmark even though unbounded structures are diagnostic-only under the Phase-43 plan.
- **Evidence status:** The corrected inference matrix remains valid as regime-versus-complement diagnostics; the router/benchmark outputs from that postprocess are invalid for promotion and are superseded.
- **Correction:** Promotion/router candidates are now explicitly restricted to the registered defined-risk universe, with calendars also excluded where development coverage is below the 20-trade minimum.
- **Prevention:** The postprocessor now applies the same promotion-universe invariant as the strategy engine before benchmark or router selection.


## F43-006 — 2026-10-06 — Corrected postprocess publication race
- **Symptom:** The corrected defined-risk postprocess completed successfully, but its Git push was rejected as non-fast-forward because another Phase-43 automation updated the branch concurrently.
- **Evidence status:** Numerical output was computed successfully but the failed publication run is not the accepted persistence checkpoint.
- **Correction:** Added fetch/rebase-before-push to the corrected postprocess workflow, matching the project’s established race-safe publication pattern.
- **Prevention:** All Phase-43 publishing workflows now rebase onto the current branch head before pushing generated evidence.


## Phase 44 — initialization audit
No numerical error has occurred at registration. Any failed workflow or implementation defect will be logged before evidence acceptance.


## F44-001 — initial Phase-44 implementation quarantined
- The first tuning implementation was not accepted as evidence because its candidate-selection design was audited before acceptance and the workflow snapshot could select using validation outcomes; its threshold implementation also did not fully reflect the registered directional/spike grid.
- Any run based on that snapshot is **NON-EVIDENCE**.
- Corrected implementation now performs development-only shortlist selection, preserves validation strictly for confirmation, writes the workflow-expected `stage1_candidates.csv`, applies the registered VIX profile families, enforces validation concentration, and opens holdout only after validation/inference freezing.


## F44-002 — redundant VIX profile expansion quarantined
- The running Stage-1 attempt used a profile mapping that redundantly evaluated LOW/NORMAL/HIGH under the combined HIGH+RISING threshold profile. This is an implementation design defect because the rising quantile is irrelevant to those level states and would create duplicate hypothesis labels.
- That run is classified **NON-EVIDENCE** and is being cancelled/replaced by the corrected profile mapping.


## F44-003 — performance optimization before evidence acceptance
- The corrected engine was still unnecessarily slow because it repeatedly scanned the full expiry option dataframe for each family/geometry/time combination.
- No output from the slow implementation is accepted as evidence.
- The registered logic is unchanged. The engine now loads each expiry once, caches expiry-day option series and exact entry prices, and performs the same strategy calculations from those cached objects.


## F44-004 — Phase-43 expiry cache reuse
- The active numerical run spent excessive time in HF repository file enumeration before loading the option sample.
- The accepted Phase-43 expiry-level trade matrix is now used as the primary cached expiry list, preserving the exact audited opportunity sample and eliminating repeated HF repository metadata enumeration. The fallback HF enumeration remains only for cache absence.


## F44-005 — bounded-memory expiry processing
- The active optimized engine retained every loaded expiry dataframe in memory, risking RAM pressure on the GitHub-hosted runner.
- No result from that run is accepted.
- The corrected engine now processes one expiry at a time and relies on the Hugging Face cache for persistence, preserving numerical definitions while bounding memory usage.


## F44-006 — filtered parquet I/O optimization
- The bounded-memory engine still read each complete expiry parquet before discarding most timestamps.
- No numerical output from that implementation is accepted.
- The corrected engine now uses pyarrow predicate filtering and reads only the registered entry-day windows plus expiry-day window for each expiry, with a complete-file fallback only when timestamp filtering is unsupported.


## F44-007 — bridge artifact-audit failure (run 37484989565)
- Numerical execution completed successfully with 25,522 structure/time observations, but the bridge artifact audit failed because the workflow expected `frozen_stage1_holdout.csv` while the script produced `frozen_holdout_confirmation.csv`.
- The run is NON-EVIDENCE because artifact persistence did not pass.
- Correction: the script now writes both canonical audit filenames; the workflow also requires the complete development diagnostic file.

## F44-008 — workflow/script summary-schema mismatch
- The finalization workflow expected `stage1_rows`, `candidate_rows`, `frozen_candidates` and `holm_survivors`, while the script summary initially exposed only lower-level names.
- Correction: the script now emits the workflow fields plus detailed aliases.


## F44-009 — monolithic Stage-1 runtime too long
- The single-script Phase-44 run remained in the numerical step for an excessive duration even after I/O optimization because it processed development, validation and holdout option files in one execution before any candidate freeze.
- No result from the long monolithic run is accepted.
- Correction: Phase 44 is now operationally split into registered development, validation and holdout executions. Development reads only the 2021–2023 development expiries and freezes candidates before validation files are touched; validation and holdout then load only their respective date ranges.


## F44-010 — strike-filtered two-pass parquet reader
- The staged development run was still spending substantial time because expiry-day parquet reads included all strikes.
- No output from that run is accepted.
- The staged reader is now two-pass: one narrow entry-window read determines ATM/step for the four registered entry times; the expiry-day read then filters to the exact strike union required by the preregistered geometries.


## F44-011 — premature validation trigger
- Validation run 37495700050 started before a valid development freeze was persisted and failed because `frozen_stage1.csv` was absent.
- It is non-evidence.
- Root cause: validation workflow listened to the shared runner-script path in addition to its explicit trigger file. Future validation execution is now trigger-file-only.

## F44-012 — premature holdout trigger
- Holdout run 37495700026 started without a completed validation artifact and failed because `validation_confirmation.csv` was absent.
- It is non-evidence.
- Root cause: holdout workflow also listened to the shared runner-script path. The holdout workflow has been changed to trigger-file-only, and holdout remains prohibited until validation inference freeze.


## F44-013 — predicate-filter timestamp incompatibility
- The first strike-filtered staged development run produced zero development rows because the parquet timestamp physical type did not return rows through the predicate-filter path.
- No evidence was accepted.
- Correction: the stage runner now detects empty predicate reads and falls back to the known-good Phase-43 full-parquet reader for that expiry. Two expiry workers are used to shorten elapsed time while keeping memory bounded.


## F44-014 — development persistence filename mismatch
- Numerical development run 37496337984 completed successfully with 13,292 structure/time rows, 3,500 development-profile rows, zero eligible candidate rows, and a passed artifact audit.
- Persistence then failed because the workflow looked for development_summary.json; the runner emits stage1_summary.json.
- The numerical output remains non-evidence until a clean persistence run succeeds.


## F44-014 — development persistence filename mismatch
- Run 37496337984 completed the numerical development stage with 13,292 structure/time rows and 3,500 profile rows.
- Artifact audit passed, but persistence failed because the workflow referenced the wrong summary filename.
- Correct file: stage1_summary.json.


## F44-015 — persistence race after successful numerical execution
- Run 37500626261 completed the registered development calculation and artifact audit successfully, but the persistence step failed because the runner attempted `git pull --rebase` while generated files were already staged as local changes; the local commit was then rejected as non-fast-forward.
- No numerical result is accepted because the artifacts were not persisted to the branch.
- Correction: the development workflow now fetches the branch, resets the worktree to the current remote branch, then stages the generated results/status/log files and pushes a new commit. This preserves the generated numerical artifacts while making publication race-safe.

## F44-validation-RUN-37506989938 — numerical execution failure
- Exit code: 1. Failed output is non-evidence.

## F44-016 — incorrect development uplift definition in first persisted screen
- The original development profile screen computed candidate uplift by subtracting the same strategy P&L from itself on the active-expiry subset, making every uplift exactly zero by construction.
- That implementation is non-evidence.
- Correct definition: candidate portfolio P&L is the selected strategy P&L on active expiries and zero on inactive expiries; unconditional comparator P&L is the same tuned structure on every eligible expiry. Uplift is the expiry-by-expiry difference across the full development opportunity set.
- The persisted structural P&L matrix is reused unchanged; only the profile selection/inference layer is corrected.

## F44-017 — validation must not fail when development freeze is empty
- A validation run started before the uplift-definition defect was discovered and failed because the old development freeze was empty.
- This is non-evidence.
- The registered stop condition permits early Phase-44 closure when no candidates survive development. Validation must therefore close cleanly with NO_STAGE1_CANDIDATES rather than treating the absence of a development candidate as a numerical failure.


## F44-018 — corrected selection runtime optimization
- Profile activation was cached by exact entry timestamp for the corrected development selection layer.
- No numerical definition changed.

## F44-019 — corrected validation uplift and holdout gating
- Validation now evaluates filtered candidate P&L with zero P&L on inactive expiries against the unconditional tuned structure across the complete validation opportunity set.
- Automatic holdout triggering was removed. 2026 remains protected until validation and any registered active-exit stage both pass.


## F45-001 — ready-made definition audit before evidence acceptance
- The first Phase-45 engine snapshot used a Double Plateau construction as two four-leg condors and therefore did not match the registered six-leg two-butterfly definition used by the strategy references.
- The same snapshot classified all Phase-43 strategy names as defined-risk when computing the validation freeze, which would have admitted Phase-43 unbounded diagnostic structures into the promotion-ranking flag.
- Evidence status: the currently running Phase-45 run is superseded/non-evidence because its head predates these corrections.
- Correction: Double Plateau is fixed as two three-leg butterflies; the defined-risk classification explicitly excludes short straddles, short strangles and ratio spreads.
- Prevention: strategy definitions and promotion-risk classes are now validated against a frozen explicit allowlist before execution.


## F45-002 — workflow log endpoint unavailable while numerical job is running
- Run 37512787150 remains in the numerical step, but the temporary GitHub Actions job-log blob returns 404/BlobNotFound while the job is still executing.
- Evidence status: tooling-only; no numerical conclusion is inferred from missing live logs.
- Correction: monitor authoritative workflow/job status and inspect full logs only after completion, matching the established project convention.

## F45-003 — manuscript newline serialization defect
- The first persisted Phase-45 manuscript used the literal two-character sequence \\n instead of actual newline characters because the generator escaped the join delimiter twice.
- Evidence status: numerical CSV/JSON evidence is unaffected; the manuscript presentation artifact is invalid until regenerated.
- Correction: regenerate the manuscript with real newline delimiters and rerun the artifact-format audit before closeout.

## F46-001 — Search coverage is not literally exhaustive
- The web interface exposes indexed/search-ranked YouTube results rather than a complete authoritative corpus.
- Evidence status: no numerical impact; this is a source-coverage limitation, not a strategy-test error.
- Correction/prevention: Phase 46 labels the scan as a broad reproducible indexed search, records the query families and direct sources, and avoids claiming that every YouTube video was retrieved.


## F46-002 — Initial discovery framing was too high-VIX focused
- The first Phase-46 framing prioritized RISING/HIGH/SPIKE/HIGH_RISING because those regimes were empty, but could have unintentionally excluded LOW/NORMAL candidates from the newly discovered source material.
- Evidence status: no numerical test was run under the restricted framing, so no backtest evidence is contaminated.
- Correction: the registered Phase-46 plan now requires all discovered candidates, including Profit Breakout-derived strategies, to be evaluated across the complete eight-state VIX panel. LOW/NORMAL remain active comparator and opportunity regimes.

## F47-001 — timezone-aware Timestamp construction
- Initial Phase-47 engine snapshot mixed timezone-aware timestamps with pd.Timestamp(..., tz=TZ), which can raise on already-aware values.
- Evidence status: pre-numerical only; no accepted numerical output was produced from the affected snapshot.
- Correction: added a single as_tz() normalization helper and applied it to expiry/date conversion paths.
- Prevention: workflow compiles the engine before any data access and the preflight stage must pass before numerical execution.

## F47-002 — multi-window option-file cache key
- Initial load_expiry() cache used only the contract expiry date, even though the same contract file can be needed for different entry/exit windows when it is a next-month hedge in one trade and the current-month contract in another.
- Evidence status: pre-numerical only.
- Correction: cache key now includes contract date plus entry and extra-day windows.
- Prevention: windowed cache keys are part of the numerical engine audit.

## F47-003 — variant accounting dropped S1/S3 rows
- Initial summary/inference grouping used delta_target as a grouping dimension, and NaN values would be dropped for strategies without a delta parameter.
- Evidence status: pre-numerical only.
- Correction: S1 is assigned variant 0.0 and S3 variant 0.30; only S2 varies across 0.25/0.30/0.35.
- Prevention: artifact audit verifies total summary rows against the trade matrix and deterministic inference grouping.

## F47-004 — nondeterministic inference seed
- Initial inference seed used Python's built-in hash(), which can vary between interpreter processes.
- Evidence status: pre-numerical only.
- Correction: deterministic character-sum seed derived from strategy, variant and VIX state.
- Prevention: inference seeds are fixed by source strings and are recorded by the workflow outputs.

## F47-AUTO — Phase 47 workflow failure
- The numerical workflow failed or an artifact self-audit failed.
- Evidence status: affected run is non-evidence until the failure is diagnosed and corrected.
- The workflow requires compile, preflight, numerical, artifact and holdout audits before publication.


## F47-005 — First numerical run blocked by artifact self-audit
- Accepted numerical execution did complete, but it produced only 14 trade rows, all for covered_call_2_proxy; Double Calendar Straddle and Monthly Wide-Range Hedge produced no accepted rows.
- The required all-state artifact audit therefore failed and no numerical result was published as evidence.
- Evidence status: **NON-EVIDENCE**.
- Correction: added a focused monthly diagnostic stage and more robust common-strike selection for the double calendar before rerunning. The next run must show successful diagnostic checkpoints for both S1 and S2 before the numerical stage can proceed.


## F47-006 — Diagnostic workflow column expectation
- After revising the monthly diagnostic to allow separate current/next-expiry ATM strikes, the workflow still printed the removed `common_strikes` column.
- Evidence status: tooling-only; the diagnostic result itself was not numerically accepted.
- Correction: workflow now prints `cur_strikes` and `next_strikes`, matching the revised diagnostic artifact.

## F47-AUTO — Phase 47 workflow failure
- The numerical workflow failed or an artifact self-audit failed.
- Evidence status: affected run is non-evidence until the failure is diagnosed and corrected.
- The workflow requires compile, preflight, numerical, artifact and holdout audits before publication.


## F47-007 — Second numerical run rejected because state-coverage audit was too strict for sparse candidate evidence
- Run 37521447694 produced only 20 rows and did not observe all eight VIX states.
- The self-audit correctly stopped publication, but the audit criterion "all states must be present in the realized candidate trade matrix" is stronger than necessary for a data-sparse exploratory candidate.
- Evidence status remains NON-EVIDENCE.
- The underlying data-feasibility limitation is documented in Phase-47 status. Future phases will distinguish "state has zero feasible observations" from "state was not evaluated."


## F48-001 — Independent dataset schema differed from published summary
- Initial Phase-48 preflight assumed every yearly parquet file had date, timestamp, expiry, strike, option_type, close, spot_price, volume and oi with exactly those names.
- Run 37522707039 failed preflight on the 2024 file before numerical execution.
- Evidence status: NON-EVIDENCE; no numerical run started.
- Correction: added schema discovery and normalization with supported aliases; spot/volume/OI are now optional, while timestamp/expiry/strike/option type/close remain required.
- Prevention: future independent data phases must record actual schema mappings before any strategy query runs.


## F48-002 — Monthly-entry multi-expiry feasibility check too narrow
- Run 37523089497 passed schema compilation but found zero monthly current+next-expiry entry checks under the first feasibility criterion.
- That criterion could not distinguish "this particular monthly entry pattern is absent" from "the entire dataset lacks multi-expiry observations."
- Evidence status: NON-EVIDENCE; numerical stage did not start.
- Correction: preflight now separately audits generic trade dates with more than one distinct expiry and records those dates in multi_expiry_days.csv.
- Prevention: data-source feasibility is now tested at both the exact strategy-entry level and the generic multi-expiry-day level.

## F48-AUTO - Phase 48 workflow or audit failure
- The affected run is non-evidence until diagnosed and corrected.


## F48-003 — Independent dataset contains multi-expiry dates but registered strategy constructors produced zero trades
- Run 37523360435 passed the generic multi-expiry preflight but the numerical engine produced no trade rows.
- Evidence status: NON-EVIDENCE; no validation result was published.
- Cause was not yet assumed. A strategy-level feasibility diagnostic was added to distinguish entry snapshot availability, spot availability, strike selection and common exit availability for B1/B2 before rerunning the full numerical phase.
- Raw artifacts are now uploaded even when later numerical validation fails, improving post-mortem visibility.


## F48-004 — Exact 10:00 entry window was zero across monthly diagnostics
- Phase 48 diagnostic showed current and next expiry rows were both zero when filtering normalized timestamps to 10:00, despite 75 generic multi-expiry trade dates.
- This strongly suggests a timestamp timezone/encoding mismatch or granularity mismatch rather than absence of the underlying contracts.
- Evidence status: NON-EVIDENCE.
- Correction: added a raw timestamp/schema probe to inspect the dataset's actual timestamp type and intraday clock before changing the entry-time filter.

## F48-005 — Confirmed raw timestamp timezone mismatch
- The timestamp probe showed intraday timestamps of 03:45 through 09:59 on dates whose Indian market session should be 09:15 through 15:29 IST.
- This establishes that the source timestamps are UTC-naive representations while the separate date field is the Indian trade date.
- The registered 10:00 IST entry filter therefore had been incorrectly matching 10:00 UTC, yielding zero entry rows.
- Evidence status: all prior Phase-48 numerical attempts remain NON-EVIDENCE.
- Correction: normalized raw timestamps by adding +05:30 before any entry/exit timestamp selection.
- Prevention: the data bridge now records and tests timestamp interpretation explicitly before numerical evidence.

## F48-006 — DuckDB interval syntax error during timestamp correction
- The UTC-to-IST correction initially used SQL syntax `INTERVAL 5 HOURS 30 MINUTES`, which DuckDB rejected.
- The run failed in preflight before any numerical work.
- Evidence status: NON-EVIDENCE.
- Correction: changed to DuckDB-compatible `INTERVAL '5 hours 30 minutes'`.

## F48-007 — Independent option source has no NIFTY spot-price field
- After timestamp correction, multi-expiry option rows were present at 10:00 IST, but the independent dataset's canonical schema has no spot_price or underlying index-price column.
- Evidence status: all affected numerical attempts remain NON-EVIDENCE.
- Correction: the engine now uses the project's canonical NIFTY 1-minute index series only for the point-in-time spot required for ATM/Black-Scholes strike selection; option prices, expiries and legs remain sourced from the independent multi-expiry dataset.
- This source-fusion rule is registered and will be documented in the final manuscript as a limitation rather than hidden.

## F48-008 — Repeated timestamps created Series values at expiry exit
- Phase-48 diagnostic reached the exit stage after timezone and spot corrections, then failed because some option-leg timestamps were duplicated; selecting .loc[timestamp] returned a Series rather than a scalar.
- Evidence status: NON-EVIDENCE.
- Correction: exit prices are now deduplicated by timestamp using the last observed quote, and entry quote selection uses the last duplicate row consistently.
- Prevention: the artifact audit must include duplicate timestamp handling before numerical evidence is accepted.


## F48-008 — Historical NIFTY lot-size schedule audit found a 2024 development-period error
- The first accepted Phase-48 numerical run used lot size 50 for expiries before 2024-12-26.
- NSE Circular 37/2024 revised NIFTY from 50 to 25 effective for new contracts from April 26, 2024. NSE Circular 64672 identifies December 19, 2024 as the last weekly expiry with the existing lot size, January 2, 2025 as the first weekly expiry with the revised lot size, and January 30, 2025 as the last monthly expiry with the old lot size.
- Therefore the October-December 2024 development-period results in the first Phase-48 numerical run used an incorrect lot size.
- Evidence status: prior Phase-48 results are REJECTED AS NON-FINAL and will not be used in the phase conclusion.
- Correction: historical lot-size mapping was corrected for the 2024-2026 sample.
- Prevention: lot-size mapping is now explicitly documented in code and must be cross-checked against NSE circulars before future numerical runs.


## 2026-10-07 — Phase 49 tooling audit
### F49-TOOL-001 — Initial engine file-generation attempts rejected by tool parser/safety layer
- Two early attempts to write the full Phase-49 engine failed before any repository write.
- Evidence status: tooling-only; no numerical analysis or repository evidence was affected.
- Correction: the engine was reduced to a compact implementation that reuses the accepted Phase-43 execution/cost primitives instead of duplicating them.
- Prevention: future phase engines should reuse accepted audited primitives whenever possible and keep new code narrowly scoped to the novel research question.


## F49-001 — Parameter-grid cardinality audit
- Initial engine preflight asserted 1,440 raw geometries, but the registered geometry universe is 720: Bear Call 192 + Bear Put 144 + Put BWB 384.
- The 1,440 figure is the total strategy×VIX-regime candidate family after crossing 720 geometries with LOW and NORMAL.
- Evidence status: pre-numerical only.
- Correction: engine preflight now asserts 720 raw parameter configurations and the phase plan retains 1,440 parameter×regime candidates.
- Prevention: cardinality is now separately recorded for geometry candidates and regime-expanded candidates.


## F49-002 — GitHub Actions import-path defect
- First Phase-49 workflow run 37532278551 passed compilation but failed preflight because `research` is not a Python package in the Actions runtime.
- Evidence status: non-evidence; preflight stopped before any data access or numerical calculation.
- Correction: the tuning engine now adds its own `research/` directory to `sys.path` and imports the accepted Phase-43 module directly.
- Prevention: future isolated Python phase scripts must not assume the repository directory is an importable package unless an `__init__.py` is present.


## F49-003 — Numerical performance self-audit
- The first corrected run reached preflight but the numerical step remained in progress without a refreshed step log, indicating the original candidate evaluator was too expensive for the 720-configuration × multi-entry search.
- Evidence status: non-final; no numerical result is accepted from the long-running process.
- Correction: candidate evaluation now caches entry quotes and expiry-day quote series per expiry/entry snapshot and performs dictionary/index operations instead of repeated full-DataFrame scans for each candidate.
- Prevention: performance gates are now treated as part of scientific reproducibility; a search must complete deterministically within the registered CI timeout rather than relying on an opaque long-running job.


## F49-004 — Second performance audit found cache construction still repeated per candidate
- Self-audit of the optimized engine showed the quote-map cache was being built inside `one()`, so it was reconstructed for every parameter configuration sharing the same expiry and entry time.
- Evidence status: no result from the affected run is accepted.
- Correction: cache is now keyed by expiry-entry timestamp and reused across the complete 720-configuration family for that snapshot.
- Prevention: performance reviews now explicitly check cache lifetime and reuse at the candidate-family level.

## 2026-10-07 — Phase 49 scientific implementation audit

### F49-005 — Undefined family registry in frozen-selection path
- Affected run: 37535442553.
- Symptom: the numerical script referenced FAMILIES while the constant was not defined.
- Evidence status: NON-EVIDENCE. No Phase-49 numerical result from that implementation may be used.
- Correction: add the explicit primary family registry bear_call, bear_put, put_bwb.
- Prevention: preflight and artifact audits validate the expected family×regime space.

### F49-006 — Validation comparator did not implement the registered VIX complement test
- Finding: the previous code evaluated the frozen candidate only when realized VIX matched its target state, then compared those rows against a pooled set of rows belonging to other candidates. This is not the preregistered active-VIX versus complement-VIX comparison.
- Evidence status: NON-EVIDENCE.
- Correction: evaluate each frozen parameter across the full validation opportunity set. Inference uses its active-VIX rows versus the same parameter's complement-VIX rows. The 2026 holdout uses the same frozen definition.
- Prevention: validation artifacts require explicit complement_trades and active_vs_complement_mean fields.

### F49-007 — Development selector did not match the preregistered forward-fold rule
- Finding: the selector required positive net and stressed mean/trade in all of 2021, 2022 and 2023. The registered forward-fold scoring rule is based on 2022 and 2023, with 2021 serving as the earliest development history.
- Evidence status: NON-EVIDENCE for outputs produced by that selector.
- Correction: eligibility and ranking now use 2022 and 2023 forward-fold performance, with a minimum of 10 trades and positive net/stressed mean per trade in each fold.
- Prevention: persist fold-specific 2022/2023 metrics.
### F49-008 — Superseded numerical run became a stale Actions process
- Run 37535442553 remained in-progress without a status update while the corrected run was queued.
- Evidence status: NON-EVIDENCE. The run head predates the corrected Phase-49 engine.
- Operational correction: the Phase-49 workflow concurrency group is being advanced so the corrected execution is not blocked by the stale superseded run. The stale process remains excluded from all research evidence.
### F49-009 — Residual performance bottleneck in candidate metadata lookup
- Audit finding: the corrected engine still recomputed the full NIFTY index trading-day list, point-in-time spot lookup and India-VIX historical quantiles inside the per-candidate path.
- Evidence status: runs 37538452940 and 37538570390 remain NON-EVIDENCE until a complete run passes all audits; no result is accepted from a performance-limited process.
- Correction: cache normalized index trading days, exact timestamp-to-spot mapping and VIX state calculations across all candidates. This changes execution only, not numerical definitions.
- Prevention: future Phase-49 performance audits must examine every candidate-level metadata lookup for repeated whole-dataset scans.
### F49-010 — Residual validation import-path defect and empty-freeze robustness gap
- Finding: the development stage used the corrected direct import path, but the later validation stage still attempted `research.phase43_vix_strategy_sweep`, which can fail because `research` is not a Python package in Actions.
- Evidence status: the active optimized run #9 is now classified NON-EVIDENCE pending rerun with the corrected path. No Phase-49 conclusion is accepted from it.
- Correction: validation now reuses the direct `phase43_vix_strategy_sweep` import path that passed preflight. The engine also has a registered clean early-stop path when no development candidate survives, so an empty freeze is a scientific outcome rather than a runtime error.
- Prevention: all phase engines must use one validated import convention throughout the full execution path; zero-candidate branches must be explicitly tested.
### F49-011 — Artifact self-audit rejected a zero-byte empty development error ledger
- Affected run: 37540089501 (#11). Numerical computation completed successfully and uploaded a complete raw artifact, but the artifact self-audit failed because data_errors.csv was zero bytes when no development errors occurred.
- Scientific evidence status: numerical values remain locked/non-final until a corrected full workflow passes the artifact and publication gates.
- Correction: the engine now writes data_errors.csv with explicit expiry/error headers even when empty. A reproducible reconciliation script was also added for audit/provenance checks.
- Prevention: all empty error ledgers must be valid zero-row CSVs with headers, not zero-byte files.
### F49-012 — Numerical and artifact audits passed, publication commit conflicted
- Affected run: 37542636969 (#12). Numerical computation completed successfully and the artifact self-audit passed.
- Publication failure: the workflow created a results commit, then rebased onto newer repository commits that had updated PHASE49_STATUS.md and RESEARCH_LOG.md, producing merge conflicts.
- Evidence status: NUMERICAL EVIDENCE VALID; publication was operationally incomplete. The raw artifact is preserved and independently reconcilable.
- Correction: the publication step now resets to the latest remote branch before staging the results directory, and does not rebase generated status/log files over concurrent research-audit commits. A separate branch-triggered closeout workflow reconciles the latest raw artifact and publishes the structured manuscript.
- Prevention: publication jobs must never rebase long-lived research logs after generating large artifacts. Results publication and research-log mutation are separated into a conflict-safe closeout path.
### F49-013 — Closeout manuscript generator depended on optional tabulate package
- Affected closeout attempt: 37544857648.
- The raw Phase-49 artifact downloaded successfully and the source-run selection was correct. Reconciliation failed only when pandas.to_markdown required the optional `tabulate` package that the first closeout dependency list did not install.
- Evidence status: numerical evidence remains valid; closeout packaging was incomplete.
- Correction: the manuscript generator now uses an internal Markdown-table renderer with no optional tabulate dependency. The workflow also includes tabulate for redundancy.
- Prevention: closeout workflows must avoid undocumented optional dependencies or install them explicitly and validate imports before processing evidence.
### F49-014 — Closeout reset ordering discarded generated status/log updates
- Affected closeout run: 37544951498.
- Numerical artifact generation and reconciliation succeeded and the full result package was published, but the commit stage reset the branch to origin after generating PHASE49_STATUS.md, RESEARCH_LOG.md and README.md. Those tracked generated updates were therefore discarded before commit, while untracked result files survived.
- Evidence status: numerical evidence and reconciled result package remain valid; publication of the status/log narrative was incomplete.
- Correction: closeout workflow now synchronizes the branch before artifact generation and commits the generated status/log/README changes afterward.
- Prevention: no workflow may reset/rebase the working tree after generating tracked research-status artifacts.
### F49-013 — README phase-status lag at final closeout
- Finding: PHASE49_STATUS.md and the final decision artifacts were CLOSED/NO PROMOTION while the README Phase-49 header still said INITIALIZED.
- Evidence status: documentation-only; no numerical evidence affected.
- Correction: the README Phase-49 section has been replaced with the reconciled final closeout status and links to the final artifacts.
- Prevention: every phase closeout must update the README headline/status in the same closeout pass.

## 2026-10-07 — Phase 50 initialization audit

### F50-001 — Initial Stage-2 candidate identity design was too weak
- The first Phase-50 engine draft did not persist exact Stage-2 entry time/DTE identity in the trade matrix and therefore could not safely reconstruct the frozen candidate from development aggregates.
- Evidence status: PRE-NUMERICAL. No numerical result from the affected engine snapshot was accepted.
- Correction: Stage-2 trade rows now persist family, distance, width, entry hour/minute and DTE; freezing groups on the exact registered candidate identity before validation.
- Prevention: every hierarchical search stage must persist all parameters required to reproduce the exact selected candidate.

### F50-002 — Initial family registry included iron-fly variants without a clean far-OTM distance interpretation
- Evidence status: PRE-NUMERICAL. No numerical output affected.
- Correction: Phase 50 primary grid retains only strategy families for which the tail-distance variable has an unambiguous structural meaning. Iron Butterfly is excluded from the primary far-OTM distance screen and remains covered by earlier phases.


### F50-003 — Phase 50 #1 artifact audit failure on sparse early-stop packaging
- Affected run: **37565293395 (#1)**.
- Numerical calculation completed successfully. The development far-OTM sweep produced **no confirmatory Stage-1 candidate** because the preregistered fold gate required 15 observations in both 2022 and 2023, while the HIGH-VIX state had only 6 development opportunities under the fixed Stage-1 control.
- The artifact audit failed because the early-stop branch did not create all empty error-ledger/result files required by the workflow.
- Evidence status: raw numerical output is useful exploratory diagnostic evidence but was not publication-accepted by the workflow.
- Correction: create valid empty ledgers and an explicit sparse-HIGH exploratory validation branch. The exploratory branch is non-promotable and does not relax the confirmatory gate.
- Prevention: all early-stop paths must emit the full canonical artifact set with headers before publication auditing.


## 2026-10-07 — Phase 50B expansion

### Error F50B-001 — Strategy-universe scope gap
The parent Phase 50 far-OTM phase used a restricted family universe and therefore did not yet contain the user's seven supplied Tradetron strategies or several older repository strategy lineages.

**Evidence status:** no Phase-50B numerical evidence exists yet.

**Correction:** created the dedicated phase-50b-expanded-strategy-universe branch, froze a prospective strategy registry and preregistration, and preserved the parent Phase 50 run unchanged.

**Prevention:** future scope additions must be frozen in a dedicated phase before candidate-selection statistics are run.


### Error F50B-002 — Native-report evidence is not directly comparable to Final Stand costs
Tradetron's finished runs use brokerage_per_order=₹0 in their cost profile and carry high-severity coverage caveats. Treating their native net P&L as Final Stand evidence would mix execution models.

**Correction:** native reports are explicitly classified as provenance/exploratory controls. The next Phase-50B numerical replay uses the project-standard Paytm Money/NSE/statutory/slippage model and entry-date VIX classification.

**Prevention:** every external-engine result must be tagged with its own cost model, coverage and data caveats before entering the research evidence hierarchy.

### Error F50B-003 — Initial TT-02 replay draft used the wrong entry-time model
- Pre-numerical audit found the draft `research/phase50b_tt02_calendar_replay.py` entered only on the trading day immediately before current-week expiry.
- The actual TT-02 strategy initializes `setup_active=1` in its embedded Python and never turns it off; the Entry condition is therefore eligible whenever flat from 09:20 through 15:00.
- Evidence status: NO NUMERICAL EXECUTION from the affected draft.
- Correction: replace the draft with a stateful session-by-session replay that can enter on any eligible flat day and holds until the current-week expiry-day 15:15 universal exit.
- Prevention: for any Tradetron strategy containing `Get Runtime` gates, inspect and freeze the embedded Python/runtime initialization before implementing the historical state machine.

### Error F50B-004 — Registry validation missed Final-stand-v2
- Affected runs: 37570048355 and 37570258257.
- The validation script correctly required the previously identified Final-stand-v2 lineage, but the frozen registry table accidentally omitted it.
- Evidence status: documentation/CI-only; no numerical research evidence was produced by the failed validation runs.
- Correction: added the missing Final-stand-v2 row to PHASE50B_STRATEGY_UNIVERSE.md. The registry validator definition remains unchanged.
- Prevention: after creating or editing a registry, run the same required-term validator against the actual checked-in registry before considering the phase preflight green.


### Error F50B-005 — TT02 replay workflow omitted matplotlib dependency
- Affected run: **37570436149**.
- The corrected TT02 engine imports `phase43_vix_strategy_sweep`, which imports matplotlib at module load even though TT02 itself does not plot figures.
- Evidence status: no numerical replay occurred; failure happened during module import before data acquisition.
- Correction: add matplotlib to the workflow dependency set. No scientific definition changed.
- Prevention: compile/runtime dependency audit must include transitive imports of the shared research engine module.


### Error F50B-006 — TT02 workflow dependency patch missed the numerical job
- Affected run: **37570624002** (and prior standalone attempt 37570436149).
- The first dependency correction changed one install step but left the standalone workflow's numerical job installing the shared Phase-43 module dependencies without matplotlib.
- Evidence status: no numerical replay; failure again occurred at module import before data acquisition.
- Correction: patch every TT02 workflow job dependency line to include matplotlib. A triggering source commit is made only after both workflow definitions are verified.
- Prevention: after workflow edits, inspect every job's dependency commands rather than assuming a single global install step.


### Error F50B-007 — Duplicate TT02 workflow executions consumed runner capacity
- Multiple Phase-50B workflows were independently triggered for the same TT02 replay while the parent expanded workflow also contained the same replay job.
- Evidence status: orchestration-only; no numerical conclusions affected.
- Correction: make the expanded Phase-50B workflow the canonical automatic runner with `concurrency.cancel-in-progress=true`; keep the standalone TT02 workflow manual-only to preserve the manual run button without automatic duplication.
- Prevention: each research phase must have one canonical automatic execution path, with auxiliary workflows manual-only unless a distinct purpose requires otherwise.


### Error F50B-008 — Status/documentation push unintentionally retriggered the full numerical workflow
- A Phase-50B status commit triggered another full TT-02 replay because the canonical workflow's push-path filter included status/research-documentation files.
- Evidence status: orchestration-only; no numerical evidence affected, but runner capacity was duplicated.
- Correction: the canonical automatic workflow is being restricted to the explicit research trigger file and executable engine/pre-registration changes. Status/README/error-log commits no longer start numerical computation. Manual dispatch remains available.
- Prevention: documentation updates must never launch a paid/long numerical study; every automatic research run requires an explicit research-source or trigger-file change.


### Error F50B-009 — Native TT-03 headline trade count is not a complete-trade count
- The Tradetron native result reports 558 “trades”, while its fill ledger contains 1,116 fills (558 buys and 558 sells) and the strategy has three entry legs plus three expiry exits per completed trade.
- Evidence status: provenance accounting only; no Phase-50B inference is affected.
- Correction: Phase-50B will reconstruct complete trades from fills and will not use the native headline trade count as the sample-size denominator.
- Prevention: reconcile headline statistics with fill-level ledgers before using any external-engine trade count in statistical tests.


### Error F50B-010 — Initial TT-03 engine draft omitted the symmetric put set and had an ambiguous entry-price lookup
- Pre-numerical audit found the first draft implemented only the bearish call ratio and used an option-type-only entry-price lookup.
- Evidence status: no TT-03 numerical execution occurred from that draft.
- Correction: the replay now implements both source sets, preserves the listed set order by giving Call Ratio priority when both are executable, falls back to the Put Ratio only if the call set is unavailable, and keys entry prices by option type plus strike.
- Prevention: for multi-set Tradetron templates, reproduce set competition/order and use full instrument identity in P&L ledgers before execution.


### Error F50B-011 — TT-02 exact replay performance bottleneck
- Affected run: 37571121043 was still executing its numerical replay with no artifact output after the source-faithful engine reached the `Run TT02 replay` step.
- Diagnosis: repeated full-DataFrame timestamp scans and unnecessarily expensive implied-vol root solves made the exact 1-minute stateful replay much slower than necessary.
- Scientific status: no result from the slow run is accepted or discarded as evidence; the mathematical replay definition is unchanged.
- Correction: option frames are now timestamp-indexed for O(1)-style timestamp access, and implied volatility uses the same Black-Scholes root with a faster five-step Newton solve plus the same Brent fallback for rare non-convergence.
- Prevention: all long exact replays will be benchmarked for data-access and numerical hot spots before launch, without relaxing quote, timestamp or execution fidelity.


### Error F50B-012 — TT-02 delta-selection hot loop
- After F50B-011, code inspection showed the remaining dominant hot spot: every minute, each nearest-delta call still iterated through every strike in Python and solved IV independently.
- This is a computational implementation issue, not a scientific result.
- Correction: nearest-delta selection is now vectorized across the complete strike set using the same Black-Scholes implied-volatility / European-delta definition; the candidate universe is unchanged and no strike-distance shortcut is introduced.
- The slower run is not used as evidence. The corrected canonical run supersedes it through workflow concurrency.


### Error F50B-013 — TT-04 baseline engine cashflow accounting audit
- Found during static pre-execution audit before any TT-04 numerical run: the initial engine draft represented short-sale cashflows with the wrong sign and used a non-zero-at-entry P&L representation.
- No numerical TT-04 result was produced from the defective draft.
- Correction: TT-04 now tracks executed cash separately and calculates mark-to-market P&L as cash plus the signed market value of all open positions. Opening/closing/replacement cashflows are signed by buy/sell direction.
- Prevention: every new multi-leg replay must satisfy a zero-at-entry MTM identity on a synthetic fixture before numerical execution.


### Error F50B-014 — local TT-04 syntax self-check blocked by environment DNS
- A local pre-execution `py_compile` attempt could not download the current GitHub file because the container had no external DNS/network access.
- No numerical execution was attempted from the local environment and no evidence was produced.
- GitHub Actions compile is the authoritative executable check before TT-04 numerical execution.


### F50B-015 — in-progress Actions job-log retrieval returned 404
- Time: 2026-10-07.
- Attempted to retrieve the live log for Phase-50B job 112635156015 (TT-02 replay) from GitHub Actions.
- GitHub returned HTTP 404 / BlobNotFound while the job remained in progress.
- Evidence status: **NO RESEARCH IMPACT**. The workflow run itself remains the authoritative execution state; no numerical output was inferred from the failed log retrieval.
- Prevention: do not treat a transient live-log retrieval failure as a numerical failure; re-check run/job state through the Actions run API and use the published artifacts only after the self-audit passes.

### F50B-016 — local polling wait timeout
- Time: 2026-10-07.
- A local 30-second sleep used only to poll the active Actions run exceeded the container tool timeout.
- Evidence status: **NO RESEARCH IMPACT**. No workflow was cancelled or modified by this timeout, and the active GitHub run remains the authoritative execution process.
- Prevention: avoid relying on local sleep/poll loops for long-running Actions jobs; use direct run/job state checks when needed.

### F50B-017 — TT04 trigger placement defect in workflow patch
- Time: 2026-10-07.
- Static review of the newly patched Phase-50B workflow found the TT04 trigger step had been inserted into the registry job rather than after the audited TT03 publication, and a stray shell `fi` remained.
- No numerical evidence was affected because the active run 37572837253 was created from the earlier validated commit and was already executing TT-02 before this patch.
- Correction: moved the trigger step to the end of the TT03 job, removed the stray `fi`, corrected the GitHub Actions bot identity, and preserved the TT04 dedicated manual/trigger workflow.
- Prevention: every workflow edit must be followed by a complete structural inspection of job placement and shell block closure before publication.

### F50B-019 — local polling sleep timeout
- Time: 2026-10-07.
- A second local polling wait helper timed out while waiting for the active GitHub Actions runner.
- Evidence status: **NO RESEARCH IMPACT**. The active Actions job was not cancelled or modified.
- Prevention: rely on direct GitHub Actions state checks rather than local sleep-based polling.

### F50B-020 — TT04 expiry-day position-marking series mismatch
- Time: 2026-10-07.
- Static pre-execution audit of the corrected TT-04 replay found that, on a current-week expiry day, the loop selected the **next-week** option frame for the day because next-week is the source-defined expiry-day entry target.
- An existing position opened on a prior non-expiry day remains a **current-week** position and must therefore be marked, repaired and exited from its own current-week option series.
- Evidence status: **NO NUMERICAL IMPACT**. TT-04 numerical execution had not started.
- Correction: the replay now separates the frame used for new entries (z_entry) from the frame used for an existing position (position expiry). Existing positions retain their original expiry series through their exit; expiry-day new entries use next-week as required by the source.
- Prevention: any strategy that changes the entry expiry on an expiry day must carry the position's immutable trade expiry separately from the day's new-entry target expiry and must use the position expiry for all MTM/exit calculations.


### F50B-021 — TT-02 audit rejected exact-15:15 exit requirement
- Time: 2026-10-07.
- Canonical TT-02 run 37572837253 completed its numerical loop and produced 237 candidate trade rows, but the artifact audit correctly rejected the result because five expiry blocks had no option quote exactly at 15:15.
- Evidence status: **NO SCIENTIFIC IMPACT / NOT EVIDENCE**. The summary included net -₹85,250.87 and stressed net -₹111,763.06, but those figures are diagnostic only because the required zero-data-error audit failed.
- Root cause: the replay interpreted the source rule “exit at/after 15:15” as an exact-15:15 quote requirement and recorded missing exact timestamps as data errors.
- Correction: TT-02 v2 and the unexecuted v3 fallback now search from 15:15 onward for the earliest common timestamp at which all open legs have observed closes, then execute the simultaneous exit at that timestamp. No forward-fill or invented price is used.
- Prevention: expiry-day exits must implement temporal inequalities literally; never replace “at/after” with an exact timestamp requirement without an explicit source basis. The artifact audit remains zero-tolerance for unresolved data errors.


### F50B-022 — Phase-50B registry publisher shell closure defect
- Time: 2026-10-07.
- Corrected TT-02 code automatically launched run 37589199743, but the run stopped before numerical execution because the registry publish shell block in the workflow was missing its closing `fi`.
- Registry validation itself passed and the registry artifact uploaded successfully; the failure was workflow-only.
- Correction: restored the missing `fi`, normalized the GitHub Actions bot email identity in the TT-03 publisher, and structurally re-counted shell `if`/`fi` tokens before the next trigger.
- Evidence status: **NO SCIENTIFIC IMPACT**. TT-02 did not execute in run 37589199743.
- Prevention: every workflow patch must pass a complete shell-block balance audit before a numerical trigger is emitted.


### F50B-023 — local polling helper timeout
- Time: 2026-10-07.
- A local 30-second sleep used only to let the active GitHub Actions replay advance exceeded the container execution timeout.
- Evidence status: **NO RESEARCH IMPACT**. No GitHub Actions job was cancelled or modified.
- Prevention: do not use local sleep-based waiting for long-running numerical runs; use direct Actions state and job-step checks.


### F50B-024 — live TT-02 job-log endpoint unavailable
- Time: 2026-10-07.
- Attempted to retrieve the live log for TT-02 job 112687069655 while the numerical replay remains in progress; GitHub returned `BlobNotFound` / HTTP 404.
- Evidence status: **NO RESEARCH IMPACT**. The Actions run/job state remains available through the run and job APIs, and no numerical output was inferred from the missing log.
- Prevention: live log retrieval is secondary monitoring only; acceptance requires published artifacts and the explicit artifact audit, never a transient live-log endpoint.


### F50B-025 — TT-02 mandatory-exit quote gaps reclassified as coverage exclusions
- Time: 2026-10-07.
- Corrected TT-02 replay still found five opened positions without a complete common observed quote at or after 15:15.
- Root cause is the underlying historical option-chain coverage, not an execution-rule defect. The public dataset documentation explicitly notes that option coverage is partial and that illiquid/far strikes can be sparse or absent. citeturn551023search2turn551023search4
- Correction: these cases are now recorded in `coverage_gaps.csv`, excluded from primary P&L, never forward-filled, and no longer counted as `data_errors`.
- The feasibility gate is pre-registered at 95% complete mandatory-exit coverage. The observed replay had 247 complete exits and 5 coverage gaps among 252 opened positions (~98.0%), so it clears this operational gate if the rerun reproduces the same coverage.
- Prevention: every sparse-market-data limitation must be separated from model/code errors and carried into the final sensitivity and limitations analysis.


### F50B-026 — TT-03 entry window implementation correction
- Time: 2026-10-07.
- Pre-execution audit found TT-03 selected only the first timestamp in the 10:00–10:05 window.
- Correction: the engine now evaluates the entire frozen entry window and selects the earliest timestamp at which a complete source-defined ratio set is available, retaining call-set priority and put-set fallback.
- Evidence status: **NO SCIENTIFIC IMPACT**. TT-03 had not executed.
- Prevention: source-defined time windows must be implemented as windows, not silently collapsed to the first bar unless the source explicitly requires that.


### F50B-027 — stale TT-03 downstream execution risk
- Time: 2026-10-07.
- The active Phase-50B run 37593965525 was created before the later TT-03 entry-window correction, so its downstream TT-03 job would otherwise have checked out the older engine revision.
- Correction: the current workflow refreshes the TT-03 job to the latest branch head before compilation, stamps TT-03 artifacts with `50B-TT03-WINDOW-V2`, and downstream TT-04 preflight rejects any TT-03 result lacking that revision.
- Evidence status: **NO SCIENTIFIC IMPACT**. The active TT-02 run remains the only numerical evidence candidate; stale downstream evidence cannot pass the revised gates.
- Prevention: all phase-chain numerical jobs must stamp their engine revision and downstream gates must require the expected revision.


### F50B-028 — workflow-list API false duplicate alert
- Time: 2026-10-07.
- An Actions API query using a `workflow_id` filter returned unrelated Phase-46 workflow runs on the same branch, which briefly appeared to be Phase-50B duplicates.
- Direct inspection of the returned run `path` showed those runs belonged to `phase-46-vix-youtube-strategy-discovery.yml`.
- Evidence status: **NO RESEARCH IMPACT**. No Phase-50B numerical workflow was duplicated or altered.
- Prevention: verify both workflow name/path and run ID before classifying an Actions run as a duplicate.


### F50B-029 — TT-04 silent loss on missing exit quote
- Time: 2026-10-07.
- Pre-execution audit found `finish()` returned `None` for a missing exit-leg quote and the caller silently discarded the trade without recording the coverage limitation.
- Correction: TT-04 now records such cases in `coverage_gaps.csv`; they are excluded from primary P&L, never imputed, and the workflow applies the same 95% coverage feasibility gate.
- Evidence status: **NO SCIENTIFIC IMPACT**. TT-04 had not executed.
- Prevention: a failed exit must always produce either a completed trade or an explicit error/coverage record.


### F50B-030 — TT-02 terminal-position accounting safeguard
- Time: 2026-10-07.
- Pre-rerun audit found that a position still open at the end of the replay loop could otherwise be omitted from both completed trades and coverage gaps.
- Correction: the corrected engines now record any terminal open position as an explicit coverage exclusion, preserving the opened-position denominator.
- Evidence status: **NO IMPACT ON CURRENT RUN**. Run 37593965525 was already executing from an earlier commit; this safeguard will apply to the next canonical rerun.
- Prevention: every numerical replay must reconcile opened positions = completed trades + explicit exclusions + documented model errors.


### F50B-031 — TT-02 engine revision gate
- Time: 2026-10-07.
- Added explicit TT-02 engine revision `50B-TT02-COVERAGE-V3` to prevent artifacts from the pre-coverage/terminal-accounting engines from being promoted.
- The workflow audit now requires that revision before accepting TT-02 evidence.
- Evidence status: **NO IMPACT ON CURRENT RUN**. Run 37593965525 predates this revision stamp and will therefore be diagnostic unless separately superseded by a latest-code audited rerun.


### F50B-032 — Paytm Money brokerage-rate ambiguity resolved by robustness scenario
- Time: 2026-10-07.
- Current Paytm Money public material conflicts: one current F&O FAQ displays ₹10/order while an official 2025 pricing announcement states flat ₹20/order from 15 January 2025. [Paytm Money F&O FAQ](https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web); [Paytm Money pricing update](https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/)
- Correction: retain the preregistered ₹10/order primary model for continuity, while adding a non-selective ₹20/order robustness scenario required for promotion sensitivity.
- Evidence status: **NO IMPACT ON CURRENT RUN**; this applies only to the latest-code rerun.


### F50B-033 — TT-03 silent exclusion of incomplete exits
- Time: 2026-10-07.
- Pre-execution audit found TT-03 returned `None` for missing expiry-day exit observations, which would silently omit an opened trade from the sample.
- Correction: TT-03 now emits explicit `coverage_gaps.csv` exclusions, carries a coverage rate, and its workflow enforces the 95% feasibility threshold plus current-cost robustness fields.
- Evidence status: **NO SCIENTIFIC IMPACT**. TT-03 had not executed under this corrected implementation.
- Prevention: every opened trade must reconcile to completion, explicit coverage exclusion, or documented model error.


### F50B-034 — TT-04 engine revision gate
- Time: 2026-10-07.
- Added TT-04 engine revision `50B-TT04-COVERAGE-V2` and required it in the dedicated TT-04 workflow audit.
- This blocks any pre-coverage-correction TT-04 artifact from being treated as evidence.
- Evidence status: **NO SCIENTIFIC IMPACT**. TT-04 numerical execution has not begun.


### F50B-035 — Phase-50B concurrency hardening
- Time: 2026-10-07.
- Added a serialized concurrency group to the canonical Phase-50B workflow with `cancel-in-progress: false`.
- Purpose: prevent overlapping numerical runs from competing for cached/published artifacts or obscuring the canonical evidence lineage.
- Evidence status: **NO SCIENTIFIC IMPACT**. The active run 37593965525 was already running before this workflow hardening.


### F50B-036 — TT-05 control workflow introduced
- Time: 2026-10-07.
- Added a deterministic TT-05 replay and dependency-gated workflow as the next registered control after TT-04.
- No numerical TT-05 execution occurred in this step, so no evidence impact.


### F50B-037 — TT-02 v2/v3 fallback equivalence audit
- Time: 2026-10-07.
- Audited the prepared v3 fallback against v2 and confirmed the scientific state machine and cost model are unchanged; only traversal/indexing is optimized.
- v3 remains performance-only and is forbidden while v2 is active.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-038 — Phase 50B overlapping stale/corrected runs
- Time: 2026-10-07.
- The intended workflow concurrency group did not prevent run 19 from starting while stale run 18 was still executing.
- Run 18 is on pre-revision commit `0b09aff...` and is therefore diagnostic/non-evidence; run 19 on corrected commit `dcbb00c...` is the sole eligible TT-02 evidence run.
- No third numerical run will be launched while either is active.
- Evidence status: **NO SCIENTIFIC IMPACT**; compute-efficiency/control defect.


### F50B-039 — Statistical gate fail-open cost fallback
- Time: 2026-10-07.
- The execution-only statistical gate previously substituted missing ₹20 brokerage scenario fields with primary-cost fields, which could mask missing robustness evidence. This was corrected before first statistical execution; the gate now fails closed and explicitly registers all seven strategy slots.
- Evidence status: NO SCIENTIFIC IMPACT.


### F50B-040 — TT-04 dependency gate incomplete
- Time: 2026-10-07.
- TT-04 preflight independently checked TT-03 revision, nonzero trades and zero data errors, but did not enforce the 95% coverage or full four-cost-field contract.
- Corrected before TT-04 execution; preflight now requires coverage >=95%, candidate denominator consistency, and net/net50/net20/net20_50/vix_state fields.
- Evidence status: **NO SCIENTIFIC IMPACT**; pre-execution control hardening.


### F50B-041 — TT-02 revision constant undefined at runtime
- Time: 2026-10-07.
- The TT-02 audit required engine revision `50B-TT02-COVERAGE-V3`, but the engine referenced `TT02_ENGINE_REV` without defining it. Python compilation did not detect this because the lookup occurs only when the result summary is constructed.
- Corrected before accepting any numerical evidence; a static AST contract audit was added to the workflow.
- Current run 37596743408 predates this correction and remains non-authoritative even if it eventually completes.
- Evidence status: **NO SCIENTIFIC IMPACT** because no output from the defective revision can pass the new audit.


### F50B-042 — TT-06 workflow creation quoting defect
- Time: 2026-10-07.
- The first local construction of the TT-06 workflow failed before GitHub write because GitHub Actions expression syntax conflicted with JavaScript template interpolation.
- Retried with literal-safe construction; workflow was written successfully and structurally audited.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-043 — TT-07 runtime-variable lifecycle ambiguity
- Time: 2026-10-07.
- Direct inspection of the original Dynamic IC to Ratio ASB export recovered the exact state transition graph but showed that ic_entered is set from 0 to 1 at initial entry and never reset in the export.
- This leaves repeated-initial-IC lifecycle semantics unresolved. Numerical TT-07 replay is blocked until authoritative Tradetron behavior or a trace resolves the scope of that runtime variable.
- No speculative reset policy will be coded.
- Evidence status: **NO SCIENTIFIC IMPACT**; source-faithfulness protection.


### F50B-044 — Stale-run handoff control
- Time: 2026-10-07.
- The pre-fix TT-02 run remained visibly active after the corrected trigger was queued. The workflow now uses cancel-in-progress concurrency so the stale run can be retired without waiting the full timeout.
- This is an execution-control event; no research evidence is taken from the stale run.


### F50B-045 — Superseded TT-02 run retired
- Time: 2026-10-07.
- The corrected concurrency policy successfully cancelled the pre-fix TT-02 replay when the authoritative corrected run was queued.
- No output from the cancelled run is used as evidence.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-046 — Active TT-02 live-log endpoint unavailable
- Time: 2026-10-07.
- Authoritative run 37598918723 remains in progress, but the GitHub workflow-job log endpoint returned HTTP 404 BlobNotFound while the job was active.
- This is an observability/API artifact issue, not evidence of numerical failure. No retry or duplicate replay was started.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-047 — Documentation state lagged authoritative workflow/run state
- Time: 2026-10-07.
- During the continuation audit, README/status text was found to contain older TT-02 run identifiers and an obsolete `cancel-in-progress: false` description, while the authoritative workflow source uses `cancel-in-progress: true` and run 37598918723 is the active corrected execution.
- Evidence status: **NO SCIENTIFIC IMPACT**; documentation-only inconsistency.
- Correction: synchronize Phase-50B status/research/chat/error/README records to the authoritative run and workflow state. Numerical evidence remains governed by the actual workflow/artifact gates, not stale prose.


### F50B-050 — Repository patch orchestration variable error
- Time: 2026-10-07.
- A single batched repository-write script referenced the TT-06 edited-content variable before assigning it, so the write operation aborted before any GitHub file was modified.
- Evidence status: **NO SCIENTIFIC IMPACT**; no repository mutation occurred from the failed batch.
- Correction: rebuild the patch payload with explicit per-file variables and apply writes sequentially with fresh content SHAs.
- Prevention: validate all patch variables before invoking repository writes; use sequential writes for related files.


### F50B-048 — TT04 downstream dependency preflight too weak
- Time: 2026-10-07.
- Static audit found the TT04 dependency preflight used `test -s` for the TT03 error CSV, which would reject a valid zero-error empty file, and its final TT04 artifact audit did not explicitly require all four preregistered cost fields.
- Evidence status: **NO SCIENTIFIC IMPACT**; TT04 had not executed numerical research yet.
- Correction: use existence checks plus explicit zero-row validation, and require `net/net50/net20/net20_50/vix_state` before downstream publication.

### F50B-049 — TT06 exit-timestamp selection used the dataframe index instead of timestamps
- Time: 2026-10-07.
- Static audit found TT06's 15:15+ exit search compared the RangeIndex to a timezone-aware timestamp. The code compiled but would fail at runtime when reaching the common-exit search.
- Evidence status: **NO SCIENTIFIC IMPACT**; TT06 had not executed.
- Correction: select the earliest common observed value from the explicit `timestamp` columns at/after 15:15, then perform the existing complete-leg exit/coverage logic.


### F50B-051 — TT03 timezone-naive split accounting failure
- Time: 2026-10-07.
- Corrected TT03 numerical replay completed its trade generation but failed while constructing DEV/VAL/HOLD summaries because `df.expiry` parsed as timezone-naive under the runner's pandas version while `DEV_END/VAL_END` are timezone-aware.
- This is a code/accounting defect, not a market-data failure; no TT03 numerical result was accepted or published.
- Correction: normalize the expiry series explicitly with `pd.to_datetime(..., utc=True).dt.tz_convert(TZ)` before chronological split comparisons.
- A dedicated TT03 workflow was added so the corrected replay can execute without unnecessarily rerunning the already accepted TT02 stage.
- Evidence status: **NO SCIENTIFIC IMPACT**; TT03 evidence remains pending.


### F50B-052 — TT-07 runtime-variable lifecycle ambiguity resolved from authoritative documentation
- Time: 2026-10-07.
- The raw TT-07 export initialized `ic_entered=0`, set it to 1 on initial entry, and contained no explicit reset. This had blocked source-faithful replay.
- Official Tradetron documentation states that Runtime Variables are strategy-level memory that persist across the current cycle and remain active until a Universal Exit; the current counter is the cycle in which live runtime values are associated.
- Correction: model `ic_entered` and `state` as counter-scoped. Monthly Universal Exit ends the counter; the next counter reinitializes them. No intra-cycle reset is introduced.
- Evidence status: **NO NUMERICAL IMPACT**; blocker was resolved before TT-07 execution.
- Sources: https://help.tradetron.tech/en/article/runtime-variables-in-tradetron-capture-once-use-anywhere-83nahv/ and https://files.tradetron.tech/TT_Keywords.pdf

### F50B-053 — Repository patch orchestration assertion error
- Time: 2026-10-07.
- A TT-07 engine patch attempt used Python-style `assert` inside the JavaScript repository-write environment, causing the patch script to abort before the GitHub write.
- No repository mutation occurred from the failed attempt.
- Correction: replaced the assertion with an explicit JavaScript error check and retried successfully.
- Evidence status: **NO SCIENTIFIC IMPACT**.

### F50B-054 — TT-07 transition trigger initially recalculated target strikes instead of tracking held strikes
- Time: 2026-10-07.
- Self-audit of the newly written TT-07 engine identified that transition conditions were initially evaluated using a newly selected nearest-delta strike instead of the actual strike held by the live state.
- This would have changed the source semantics and could have generated false state transitions.
- Correction: transition evaluation now reads the actual open short-leg strike from the position ledger and reconstructs its contemporaneous delta. The workflow has not yet executed this pre-correction engine.
- Evidence status: **NO SCIENTIFIC IMPACT**; caught and fixed before numerical execution.


### F50B-055 — TT-07 transition execution was not transactional
- Time: 2026-10-07.
- Pre-execution self-audit found that `execute_open_close` could mutate cash for earlier closing legs before discovering a missing quote on a later leg.
- This could corrupt the simulated ledger and is therefore classified as a source-accounting integrity defect.
- Correction: validate all old-state and target-state quotes first, compute a single cash delta, and mutate the position only after every quote is confirmed.
- The defect was caught before any TT-07 numerical run.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-056 — TT-03 trigger remained non-observable at commit-status level
- Time: 2026-10-07.
- The corrected TT-03 trigger commit `f7f01c5265203ad27b33d28d0633a93609a4538d` has remained `pending` in the available commit-status endpoint, while no TT-03 result artifact or downstream TT04 trigger is visible on the branch.
- The available GitHub connector cannot enumerate arbitrary workflow runs by workflow file, so a live run ID could not be independently recovered from the connector.
- Because the dedicated TT03 workflow uses `cancel-in-progress: true`, a controlled trigger refresh will either start the intended run or cancel/restart a stale queued/in-progress attempt without permitting overlapping TT03 numerical evidence.
- This is an operational observability/control event, not a scientific conclusion.


### F50B-056 — Corrected TT03 trigger had no associated Actions status
- Time: 2026-10-07.
- The corrected TT03 trigger commit `f7f01c5265203ad27b33d28d0633a93609a4538d` remained status-pending with zero reported checks and no published TT03 result directory.
- This did not prove a numerical failure; it indicated that the expected workflow association was not observable through the available GitHub status surface.
- Correction: after confirming that no TT03 artifact or downstream TT04 trigger existed, the trigger file was changed and committed again to explicitly retrigger the dedicated TT03 workflow.
- No duplicate numerical evidence was launched while the previous trigger had no observable Actions run.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-057 — Batched documentation write hit a stale SHA conflict
- Time: 2026-10-07.
- A sequential documentation synchronization batch attempted to update multiple repository files using SHAs fetched before the preceding write.
- The first write advanced the branch, causing a later file update to be rejected with HTTP 409 because its SHA was stale.
- No scientific or data artifact was lost; the failed write did not overwrite any file.
- Correction: all subsequent related documentation writes will fetch a fresh SHA immediately before each individual update.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-059 — Repository-write script quoting error during statistical-gate documentation patch
- Time: 2026-10-07.
- A batched JavaScript repository-write script contained an unescaped template-literal backtick in its string content and aborted before any GitHub mutation.
- No scientific or repository evidence was altered by this failed attempt.
- Correction: subsequent content payloads will avoid nested template literals or escape them before execution.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-060 — Statistical gate used stored VIX level labels and could not test preregistered dynamic modes
- Time: 2026-10-07.
- Pre-execution audit found that replay trade tables store only the three-level VIX label (LOW/NORMAL/HIGH), while the preregistered statistical family also includes SPIKE, RISING, FALLING and HIGH_RISING.
- The gate therefore could not validly evaluate the full frozen VIX hypothesis family from the stored label alone.
- Correction: reconstruct full VIX mode membership from each trade's entry timestamp and the cached project VIX series using the same frozen vix_state definition.
- Stored level labels are retained as a consistency check; mismatches are reported rather than silently ignored.

### F50B-061 — Statistical gate could count VIX-unobservable trades in every regime complement
- Time: 2026-10-07.
- During the VIX-mode reconstruction correction, trades with fewer than the required historical VIX observations initially produced an empty mode set and could have been counted as members of every regime complement.
- Correction: inferential testing now restricts to trades with an observable reconstructed VIX mode. Unclassifiable trades are excluded from both the regime and complement for the inferential family.
- Evidence status for F50B-060/F50B-061: **NO SCIENTIFIC IMPACT**; no statistical-gate result from the defective implementation is accepted.


### F50B-062 — TT03 dedicated workflow preflight omitted pandas installation
- Time: 2026-10-07.
- Corrected TT03 run 37610158492 failed in its dependency gate before numerical execution because the preflight job imported pandas without installing the replay dependencies.
- The numerical engine itself was not reached and no TT03 evidence was produced.
- Correction: the dedicated TT03 preflight now installs the same core scientific/data dependencies used by the numerical job before validating TT02 artifacts.
- A controlled TT03 trigger refresh was committed after this workflow correction.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-063 — TT03 hard-close logic could violate the "no later than 15:29" rule
- Time: 2026-10-07.
- Pre-execution self-audit found that the baseline TT03 engine, when no negative P&L exit occurred, searched for an observed timestamp at or after 15:29 and could therefore choose 15:30 or later.
- That contradicts the source-defined hard close of no later than 15:29.
- Correction: the engine now takes the latest simultaneously observed index/option timestamp **at or before 15:29**, without requiring an exact 15:29 quote and without forward-filling.
- The currently running TT03 job uses the pre-correction commit and will be superseded by a controlled retrigger.
- Evidence status: **NO SCIENTIFIC IMPACT**; corrected before accepting any TT03 result.

### F50B-064 — TT03 entry had an unnecessary modal-strike-step feasibility gate
- Time: 2026-10-07.
- The engine computed a modal strike step and refused an otherwise complete source-defined ratio entry when the modal-step calculation was unavailable.
- The source rule specifies point-distance strikes (ATM±300/350/400); modal strike-step availability is not a source condition.
- Correction: removed the modal-step gate. Complete contemporaneous source-defined strikes are now sufficient.
- No numerical result from the pre-correction TT03 engine is accepted.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-065 — TT03 missing-entry campaigns could be silently omitted from coverage denominator
- Time: 2026-10-07.
- Self-audit found that an eligible expiry with a valid three-days-before entry day but no observed entry timestamp, or no complete call/put ratio quote set inside 10:00–10:05, could return None and disappear from the candidate denominator.
- Because the source strategy is scheduled to attempt entry on each eligible campaign day, such data failure must be an explicit coverage exclusion rather than an unobserved absence.
- Correction: these cases now return explicit coverage_gaps.csv rows and contribute to candidate_trades.
- The current TT03 run is being superseded before numerical evidence acceptance.
- Evidence status: NO SCIENTIFIC IMPACT.


### F50B-066 — TT03 corrected baseline failed the preregistered 95% feasibility gate
- Time: 2026-10-07.
- Corrected TT03 engine revision 50B-TT03-WINDOW-V2 generated 187 completed trades from 202 candidate campaigns, with 15 explicit coverage exclusions: coverage = 92.574%.
- Primary net was +₹87,005.53, +50% cost stress +₹79,885.04, ₹20/order +₹73,765.93, and ₹20/order +50% stress +₹60,025.64.
- These P&L figures are diagnostic only because coverage is below the preregistered 95% feasibility threshold. The audit correctly rejected the artifact before publication.
- Decision: classify TT03 as FEASIBILITY FAIL — NO PROMOTION. Do not tune VIX, far-OTM distance, or other parameters for TT03, and do not include TT03 in confirmatory statistical inference.
- A rerun is authorized only to persist the full diagnostic replay and coverage gaps; it is not a scientific re-test.
- Evidence status: SCIENCE-GATING RESULT — TT03 fails feasibility.


### F50B-067 — TT04 premium-match helper violated source exact-match semantics
- Time: 2026-10-07.
- Pre-execution audit found the TT04 engine used nearest-premium selection by absolute LTP error instead of requiring an exact contemporaneous observed premium match.
- This could substitute a different premium and materially change the repair leg.
- Correction: TT04 V3 requires an exact observed LTP match (within deterministic floating-point tolerance) and uses nearest distance-to-spot only as a tie-break among exact matches.
- No TT04 numerical run had produced accepted evidence before this correction.
- Evidence status: NO SCIENTIFIC IMPACT; caught before execution.

### F50B-068 — TT04 exit path required earliest complete 15:15+ timestamp
- Time: 2026-10-07.
- Pre-execution audit found the TT04 baseline attempted exit at the first index timestamp at/after 15:15 and treated missing leg quotes there as a coverage loss, rather than searching later same-day observed timestamps permitted by the source rule.
- Correction: TT04 V3 searches observed timestamps from 15:15 through 15:30 and selects the earliest timestamp with complete quotes for all live legs; only then is a coverage exclusion recorded.
- No TT04 numerical run had produced accepted evidence before this correction.
- Evidence status: NO SCIENTIFIC IMPACT; caught before execution.


### F50B-069 — TT03 diagnostic rerun initially pinned to a pre-hardening workflow commit
- Time: 2026-10-07.
- TT03 run 37612856834 started from head 27328ba before the diagnostic-capture workflow hardening and before the later TT04 V3 changes.
- Because the workflow uses serialized cancel-in-progress concurrency, that run is not trusted to provide the final diagnostic persistence/routing outcome.
- Correction: refreshed the TT03 trigger after all workflow hardening so the next serialized run is evaluated from the latest branch head.
- Evidence status: NO SCIENTIFIC IMPACT; this is execution-orchestration control only.


### F50B-066 — TT03 baseline failed preregistered 95% feasibility gate; raw diagnostic artifact was not retained
- Time: 2026-10-07.
- Corrected TT03 run 37611676386 completed numerical replay successfully but produced 187 completed trades out of 202 candidate campaigns: 92.5743% coverage, below the preregistered 95% feasibility threshold.
- The audit correctly rejected the run, so no TT03 P&L was accepted as evidence and no TT04 trigger was created.
- Because the audit failed before artifact upload, the 15 coverage-gap rows were not retained for root-cause classification.
- Correction: the dedicated TT03 workflow now uploads its full replay directory with `if: always()` so feasibility-failed runs remain available for diagnosis without being promoted or published as evidence. A controlled diagnostic retrigger was launched after the workflow correction.
- Evidence status: **TT03 numerical output remains NON-EVIDENCE pending coverage-gap diagnosis; no downstream phase is permitted yet.**


### F50B-067 — TT03 hard-close coverage search stopped at a partially quoted 15:29 timestamp
- Time: 2026-10-07.
- Self-audit of the V2 engine found that hard-close logic selected the latest timestamp at or before 15:29 that had any option data, then checked all legs only at that timestamp.
- If one live leg was missing at that latest timestamp but a complete quote existed at an earlier timestamp, the engine incorrectly classified the campaign as a coverage gap.
- This can artificially reduce execution coverage and likely contributes to the 92.57% V2 feasibility failure.
- Correction: V3 now searches backward from 15:29 for the latest timestamp at or before the hard close where **all live legs** have observed quotes. No forward fill or imputation is introduced.
- The V2 187/202 result remains non-evidence. The V3 engine is being re-run from scratch behind the same 95% feasibility gate.
- Evidence status: **NO SCIENTIFIC IMPACT**; caught before acceptance of TT03 evidence.


### F50B-068 — TT03 workflow could route TT04 on FAIL_COVERAGE
- Time: 2026-10-07.
- Self-audit of the dedicated TT03 workflow found that its downstream routing script allowed both `PASS` and `FAIL_COVERAGE` feasibility states to create the TT04 trigger.
- This contradicted the preregistered 95% feasibility gate: a strategy failing coverage must stop, not advance to downstream validation.
- Correction: downstream TT04 routing is now fail-closed and occurs only when TT03 feasibility state is exactly `PASS`; `FAIL_COVERAGE` exits without creating a downstream trigger.
- The affected V3 run was superseded via the strategy-specific concurrency group and a controlled retrigger after the correction.
- Evidence status: **NO SCIENTIFIC IMPACT**; caught before any TT04 downstream trigger was accepted.


### F50B-069 — TT03 candidate denominator counted a non-standard-session day as a missing 10:00 entry
- Time: 2026-10-07.
- The V2 diagnostic identified 2022-10-24 as a missing 10:00–10:05 observation for a 2022-10-27 expiry. NSE records show that 24-Oct-2022 had a Diwali Muhurat session beginning at 18:15, so there was no normal 09:15–15:30 session at the strategy's scheduled entry time. citeturn282531search15turn282531search21
- Treating that day as a data-coverage failure would incorrectly penalize the feasibility denominator because no source-defined entry opportunity existed at 10:00.
- Correction: V4 excludes intended entry dates with no normal 09:15–15:30 NIFTY index session as explicit `session_exclusions`, not coverage gaps. A normal-session day with no 10:00–10:05 observations remains a genuine coverage gap (e.g. 2022-03-07 is not an NSE holiday and therefore remains a data-coverage candidate). citeturn250743search0turn250743search13
- Evidence status: **NO SCIENTIFIC IMPACT** from the old denominator; V2 remains non-evidence and V4 is the active source-faithful implementation.


### F50B-070 — TT03 V4 diagnostic persistence referenced undefined session-exclusion dataframe
- Time: 2026-10-07.
- After adding `session_exclusions.csv` to the V4 diagnostic contract, the workflow persistence step referenced `sx` before loading it.
- This would fail after numerical replay and prevent the feasibility artifact from being persisted, even though the engine itself was correct.
- Correction: the persistence step now loads `session_exclusions.csv` before constructing the feasibility JSON.
- The workflow trigger was not allowed to serve as evidence; a further controlled retrigger will execute only the corrected workflow.
- Evidence status: **NO SCIENTIFIC IMPACT**; caught before accepting V4 evidence.


### F50B-071 — TT04 workflow accepted TT03 FAIL_COVERAGE and continued numerical replay
- Time: 2026-10-07.
- A prior TT04 workflow version explicitly allowed TT03 `FAIL_COVERAGE` to continue independently. This was inconsistent with the registered research plan, which requires a strategy to pass the 95% feasibility gate before advancing.
- A TT04 run (37614211996) had already passed that weak gate and was executing when this defect was detected.
- Correction: TT04 preflight is now PASS-only and requires TT03 `engine_revision=50B-TT03-WINDOW-V4`, `feasibility_state=PASS`, zero data errors and coverage >=95%. A controlled TT04 retrigger supersedes the weak-gate run via the workflow's serialized concurrency group.
- Evidence status: **NO TT04 RESULT FROM THE WEAK-GATE RUN WILL BE ACCEPTED OR USED**.


### F50B-072 — TT03 V4 negative-exit path left `exit_snap` uninitialized
- Time: 2026-10-07.
- V4 numerical replay completed, but 14 eligible expiry campaigns raised `UnboundLocalError` because `exit_snap` was initialized only by the hard-close branch. When the source-defined negative-P&L exit triggered first, the exit timestamp was set but its snapshot was not retained.
- This caused `data_errors.csv` to contain 14 engine errors, so the V4 artifact was correctly rejected despite 99.47% nominal coverage.
- Correction: V5 initializes `exit_snap`, stores the contemporaneous snapshot whenever the negative-P&L exit triggers, and validates the snapshot before leg settlement. This removes the accounting/runtime defect without changing source entry/exit semantics.
- The V4 P&L and coverage statistics are **NON-EVIDENCE** because of the 14 engine errors. V5 is the active implementation.


### F50B-066 — TT03 workflow artifact gate lagged corrected engine revision V5
- Time: 2026-10-07.
- The replay engine had been hardened from V2 to V5, but the dedicated workflow still required V2 in its static and artifact audit gates.
- This could reject a scientifically corrected V5 run even if its replay and coverage were valid.
- Correction: workflow revision gates were advanced to 50B-TT03-WINDOW-V5 before the next numerical execution.
- No V5 result was accepted through the stale V2 audit path.
- Evidence status: NO SCIENTIFIC IMPACT.


### F50B-073 — TT03 workflow accumulated duplicate diagnostic/routing blocks during iterative hardening
- Time: 2026-10-07.
- Iterative fixes left multiple TT03 persistence/audit/routing sections in the dedicated workflow, including stale V4/V5 assumptions and duplicated artifact publication paths.
- This increased the risk of contradictory terminal classifications and stale downstream routing.
- Correction: replaced the workflow with one source-of-truth numerical replay, one terminal-classification/persistence block, one diagnostic upload, and one downstream routing block.
- Evidence status: NO SCIENTIFIC IMPACT; no accepted TT03 evidence came through the conflicting workflow state.

### F50B-074 — TT04 gate was coupled to TT03 PASS rather than persisted terminal classification
- Time: 2026-10-07.
- The research plan allows unrelated registered strategies to continue after a candidate reaches a persisted feasibility/validity failure, provided no failed candidate P&L is consumed as evidence.
- The TT04 workflow was still PASS-only despite the repository's terminal-classification architecture.
- Correction: TT04 now accepts TT03 terminal states PASS, FAIL_COVERAGE, or INVALID_ENGINE, but in the latter two cases explicitly forbids using TT03 P&L as evidence.
- Evidence status: NO SCIENTIFIC IMPACT; TT04 execution remains independently source-faithful.


### F50B-075 — TT04 entry coverage could silently omit eligible trading days
- Time: 2026-10-07.
- Pre-execution audit found that TT04 could finish a normal trading day without an entry and without recording a coverage exclusion when no complete ATM CE/PE quote pair was available during 10:00–10:05.
- Missing option-chain loads were also recorded only as data errors, without preserving the scheduled entry day in the candidate denominator.
- Correction: normal-session days are now explicit entry candidates; missing entry quotes are explicit coverage gaps, and non-regular-session days are separate session exclusions.
- Evidence status: NO SCIENTIFIC IMPACT; no TT04 numerical replay from the pre-correction engine is accepted.


### F50B-077 — Repository-log synchronization script quoted a backticked filename inside a JavaScript template literal
- Time: 2026-10-07.
- A multi-file documentation update script failed to parse because the string contained an unescaped backticked filename reference.
- The script failed before execution; no repository file was mutated by this failed attempt.
- Correction: subsequent repository-write payloads use plain quoted strings without nested backticks.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-078 — Actions GITHUB_TOKEN push could not trigger the downstream TT04 push workflow
- Time: 2026-10-07.
- TT03 V5 correctly persisted PASS and wrote the TT04 trigger marker, but no TT04 Actions run appeared after the workflow pushed that marker using the repository GITHUB_TOKEN.
- Current GitHub documentation confirms that events caused by GITHUB_TOKEN do not create new workflow runs for ordinary push events; workflow_dispatch and repository_dispatch are exceptions. [GitHub GITHUB_TOKEN documentation](https://docs.github.com/en/actions/concepts/security/github_token) and [Triggering a workflow](https://docs.github.com/en/enterprise-cloud%40latest/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- Correction for the active research session: ChatGPT created a normal user-authored trigger commit to dispatch TT04. No TT04 numerical run had started from the suppressed GITHUB_TOKEN push.
- Evidence status: **NO SCIENTIFIC IMPACT**; orchestration-only.


### F50B-079 — Web citation tokens accidentally written into repository Markdown
- Time: 2026-10-07.
- The F50B-078 log entry initially used chat citation tokens inside a repository file.
- Correction: replaced them with ordinary Markdown hyperlinks so repository documentation remains portable and renders correctly outside the chat UI.
- Evidence status: **NO SCIENTIFIC IMPACT**.


## 2026-10-07T18:15:00+05:30 — No new scientific error; live-state checkpoint
- Direct inspection of TT04 run 37621965843 found preflight successful and numerical replay still in progress.
- No new implementation error was identified in the active TT04 V3 workflow or downstream statistical-gate audit.
- No numerical output was classified as evidence before completion; no duplicate TT04 run was started.


### F50B-070 — TT04 live-log endpoint returned BlobNotFound while replay remained active
- Time: 2026-10-07.
- Direct job-state inspection shows TT04 run 37621965843 remains in_progress in the numerical replay step.
- Fetching its live job log for job 112794408361 returned GitHub BlobNotFound.
- This is an Actions log-availability/observability issue, not a workflow failure and not numerical evidence.
- Handling: continue using authoritative workflow/job state and artifact publication gates; do not infer replay outcome from missing live logs and do not launch a duplicate run.
- Evidence status: NO SCIENTIFIC IMPACT.


## 2026-10-07 — F50B-071 — TT04 replay still active; no new error
- Direct job-state inspection confirms run 37621965843 remains in_progress at the numerical replay step.
- No new implementation failure is indicated; result artifacts and downstream trigger are simply not yet available.
- Evidence status: **NO SCIENTIFIC IMPACT**.


## 2026-10-07 — F50B-072 — TT04 active-run checkpoint
- Direct job inspection confirms run 37621965843 is still active in the numerical replay.
- No Actions artifact is available yet.
- No scientific inference was made from the incomplete run.
- Evidence status: NO SCIENTIFIC IMPACT.


### F50B-080 — Dormant TT04 fallback construction script hit a JavaScript quoting syntax error
- Time: 2026-10-07.
- A repository-write preparation script intended to construct a performance-only TT04 fallback failed to parse in the tool runtime because of nested quoting in a replacement string.
- The script failed before the GitHub create-file call; **no repository file was mutated by this failed attempt**.
- Correction: rebuild the fallback using safer literal construction and keep it dormant until a genuine TT04 workflow failure/timeout is established.
- Evidence status: **NO SCIENTIFIC IMPACT**.


### F50B-081 — TT04 canonical numerical replay failed before artifact audit
- Time: 2026-10-07.
- Canonical TT04 Actions run 37621965843 completed with the numerical replay step failed. Artifact audit, upload, publication and TT05 routing were skipped, so no scientific output was accepted.
- The job-log endpoint for job 112794408361 remained unavailable with BlobNotFound; therefore the underlying runtime exception is intentionally not guessed.
- Handling: the failure satisfies the registered condition for the dormant performance-only fallback. A separate gated fallback workflow was added and its trigger activated.
- Scientific status: NO TT04 RESULT FROM THE FAILED RUN IS EVIDENCE. The fallback remains subject to the identical coverage/zero-error/cost audit.


### F50B-082 — TT04 fallback workflow could not be programmatically dispatched
- The fallback workflow was correctly installed and its trigger marker was refreshed, but no Actions run was created. The available GitHub connector exposes workflow inspection/rerun operations but no workflow_dispatch operation. API-authored trigger commits also do not create push-triggered workflow runs in this repository configuration. This is an orchestration/tooling limitation, not a scientific result. The fallback remains pending execution; no P&L is accepted.


### F50B-083 — TT04 canonical replay failed on timezone mismatch during split-summary construction
- The completed canonical run 37621965843 ran for about 50 minutes and failed after the replay loop while constructing DEV/VAL/HOLD split masks. Pandas rejected comparison of timezone-naive expiry_dt values with timezone-aware DEV_END/VAL_END. No artifact audit ran, so no P&L from this run is evidence. Correction: both canonical and performance-fallback engines now localize expiry_dt to the project timezone before split classification. Scientific rules and trade logic are unchanged.


### F50B-085 — TT04 live log endpoint unavailable during active replay
- Time: 2026-10-07.
- Direct job-state inspection confirms corrected TT04 run **37629750175** remains active in the numerical replay.
- Fetching the live job log for job **112821170181** returned GitHub `BlobNotFound` while the job is still running.
- This is an Actions log-availability/observability issue, not a workflow failure and not numerical evidence.
- Handling: continue using authoritative workflow/job state and artifact publication gates; do not infer replay outcome from the unavailable live log and do not launch a duplicate run.
- Evidence status: **NO SCIENTIFIC IMPACT**.


## F50B-086 — TT04→TT05 downstream trigger suppressed by GITHUB_TOKEN push (2026-10-07)
- Evidence: TT04 run 37629750175 passed and published its TT04 artifact, but GitHub Actions showed no TT05 run; the screenshot also showed no workflow in progress.
- Root cause: the TT04 handoff created `trigger/phase50b_tt05.start` with a `git push` authenticated by `GITHUB_TOKEN`. Such token-authored pushes do not start a separate ordinary push-triggered workflow.
- Scientific impact: none. TT04 results remain valid and accepted; TT05 had not executed, so no TT05 evidence was lost or contaminated.
- Correction: TT04, TT05 and TT06 downstream handoffs were hardened with `actions: write` and explicit GitHub Actions workflow-dispatch API calls after the audit-passed marker commit. The marker remains as an audit trail.
- Recovery: the TT05 marker was deliberately touched through the repository API, producing a real push event; TT05 run 37654354444 then started and passed preflight.
- Prevention: future phase handoffs use explicit workflow dispatch rather than relying on GITHUB_TOKEN push events.


## F50B-088 — TT05→TT06 workflow-dispatch 404 (2026-10-07)
- TT05 recovery run **37666116836** completed replay, artifact audit, upload and safe publication successfully.
- The final downstream-dispatch step returned HTTP 404 when addressing `phase-50b-tt06-intraday-asym.yml` through workflow-dispatch.
- Root cause: GitHub workflow-dispatch requires the workflow definition to exist on the repository default branch; this phase-specific workflow is maintained on the research branch.
- Scientific impact: **none**. TT05 evidence remains valid and published; only the orchestration step failed.
- Recovery: the TT06 trigger marker was updated through the repository API, launching TT06 run **37675162843**.


## F50B-089 — TT06 split-report timezone mismatch (2026-10-08)
- Run: **37675162843**.
- Preflight, compile, static engine audit and HF setup passed. The numerical replay then failed only during DEV/VAL/HOLD split classification.
- Cause: `pd.to_datetime(df.expiry)` returned timezone-naive expiry timestamps, while `DEV_END`/ `VAL_END` are timezone-aware project-timezone timestamps; Pandas rejected the comparison.
- Scientific impact: **NO NUMERICAL EVIDENCE ACCEPTED** from this run. The failure occurred after trade generation logic and before artifact audit/publication.
- Correction: changed the reporting-layer conversion to `pd.to_datetime(df.expiry).dt.tz_localize(TZ)`. Trading rules, quote selection, repair logic, exit logic, cost model, lot sizes and VIX capture are unchanged.
- Recovery: a fresh TT06 run will be triggered from the existing marker path after the corrected engine is committed.
- Prevention: all Phase-50B replay engines must normalize expiry columns to the canonical project timezone before any chronological split comparison.


## F50B-090 — TT06 feasibility failure at 70.40% coverage (2026-10-08)
- Run: **37722386852**; numerical job **113132915078**.
- The corrected TT06 replay completed successfully and produced 692 trades from 983 candidate trades, with 291 coverage exclusions and 3 session exclusions. Coverage = **70.3967%**, below the frozen **95% mandatory-exit coverage gate**.
- Cost outputs from the completed replay are diagnostic only: net **−₹907,626.93** at ₹10/order; net50 **−₹959,664.39**; net20 **−₹988,008.53**; net20_50 **−₹1,080,236.79**.
- Chronological diagnostic splits were DEV 382 trades/−₹155,259.71, VAL 278/−₹327,254.08, HOLD 32/−₹425,113.13 at the base ₹10/order model. These are not inferential evidence because the feasibility gate failed.
- The Actions failure occurred in the artifact audit solely because `coverage_rate >= 0.95` was false. Replay generation itself completed; no data-error assertion failed.
- Scientific classification: **TT06 FAIL_COVERAGE**. Per the candidate-local stopping rule, TT06 is closed for promotion, VIX conditioning, parameter tuning and confirmatory inference. Its P&L must not be consumed as evidence by downstream candidates.
- No trading rule, strike rule, stop, exit, cost model, lot size or VIX definition was changed to obtain this classification.
- Prevention: persist the terminal classification before advancing to an unrelated registered candidate; downstream workflows must explicitly verify that TT06 P&L is excluded when TT06 is FAIL_COVERAGE.
- Evidence status: **TT06 is not a valid Phase-50B evidence candidate and is not promotable.**


## F50B-091 — TT07 feasibility failure at 1.69% coverage (2026-10-08)
- Run **37746729676**; numerical job **113210030856**.
- TT07 replay completed, but only **1/59** candidate campaigns produced a complete trade, giving **1.6949%** coverage; 58 coverage exclusions, 1 entry exclusion, 2 transition-diagnostic rows and zero data errors.
- The artifact audit failed solely because the frozen **95% mandatory-exit coverage gate** was not met. The replay itself did not crash.
- Diagnostic cost outputs are not evidence: net **+₹611.91** at ₹10/order, +₹304.75 under +50% friction, +₹187.11 at ₹20/order, and **−₹332.45** at ₹20/order +50% stress.
- Scientific classification: **TT07 FAIL_COVERAGE**. Per the candidate-local stopping rule, TT07 is closed for promotion, VIX conditioning, parameter tuning and confirmatory inference. Its P&L must not be consumed downstream.
- The divide-by-zero RuntimeWarnings observed in the implied-volatility Newton update were non-fatal and did not cause the terminal classification; they are recorded as an implementation warning for future engine hardening, not as accepted evidence.
- Terminal classification has been persisted at `results/phase50b/tt07_dynamic_ic_ratio_replay/terminal_classification.json`.
- No strategy rule, strike, stop, exit, cost model, lot size or VIX definition was changed.


## F50B-093 — Live Actions log endpoint unavailable during TT-03 far-OTM run (2026-10-08)
- Run: 37762837711; job: 113263197383.
- Workflow state remained in_progress; the live job-log endpoint returned GitHub 404 BlobNotFound while BASE regression was executing.
- No numerical result was inferred from the unavailable log.
- Scientific impact: none; execution continues from the authoritative run state.
- Action: rely on workflow job/run state and persisted artifacts only; do not retry or alter research code solely for this endpoint error.


## F50B-094 — Far-OTM publication push race (2026-10-08)
- Run **37762837711** completed all three frozen geometry replays and the selection audit successfully, but the final publication push was rejected as non-fast-forward because the research branch received a concurrent repository update while Actions was running.
- Scientific impact: **none**. Numerical replay, BASE regression, coverage gate and preregistered selection completed before publication. No result was altered by the push failure.
- Selection result already printed by the authoritative audit: **OTM350 frozen for validation**. DEV/VAL/HOLD values are recorded in the run log; holdout remains protected.
- Recovery: hardened the publication step to fetch/rebase the current branch before pushing. This is an orchestration-only correction; frozen geometry, selection criteria and cost assumptions are unchanged.
- Prevention: Actions publication must reconcile concurrent branch updates before pushing generated artifacts.
\n\n## 2026-10-08 — Phase 50B-5 chronology run 37821975113\n\n### Error F50B-095 — Accepted-total cross-check used the wrong summary column names\n**Run:** 37821975113.\n\n**Symptom:** The OTM350 reconstruction and artifact audit passed, but the chronological-validation script stopped before producing its outputs with `KeyError: 'net'`.\n\n**Cause:** The summary builder prefixes every metric with its cost-model name, so the aggregate net field is `net_net`, not `net`. The cross-check incorrectly indexed the unprefixed names.\n\n**Evidence status:** Non-evidence CI/reporting failure only. No Phase 50B-5 numerical conclusion was accepted from this run.\n\n**Correction:** The cross-check now explicitly maps accepted totals to `{cost}_net` and records observed values from those fields. No trading rule, dataset, cost assumption, split, or selection criterion changed.\n\n**Prevention:** Cross-checks must validate the generated schema before indexing aggregate metrics; future phase scripts should use explicit schema assertions for every accepted evidence field.\n\n**Research impact:** None on prior accepted TT-03/TT-04/TT-05 evidence. Phase 50B-5 remains incomplete and must rerun from the frozen protocol.\n

## 2026-10-08 — Phase 50B-5 run 37827007176

### Error F50B-096 — Publish rebase lacked Git identity
**Run:** 37827007176.

**Symptom:** All numerical and audit steps passed, but publication failed during `git rebase` with `empty ident name`.

**Cause:** Git identity was configured for the initial commit but not explicitly available when the rebase-created commit was generated.

**Evidence status:** Numerical results are complete and audit-passed, but this run is not the authoritative published checkpoint.

**Correction:** Configure the GitHub Actions bot name/email immediately before rebase. No research parameter, trade rule, split, cost model, or inference criterion changed.

**Prevention:** Publication workflows must set Git identity immediately before commit/rebase operations.

**Research impact:** None on numerical evidence.
\n\n## 2026-10-09 — Phase 50B-5 completion\nNo new error. Run 37828322922 passed all numerical, audit and publication gates after the F50B-096 Git identity correction.\n\n## 2026-10-09 — Phase 50B-6 initialization\nNo numerical error observed at initialization. The inference engine is frozen and awaits GitHub Actions execution.\n
## 2026-10-09 — Phase 50B-6 run 37831453896

### Error F50B-097 — Block-bootstrap input schema bug
**Run:** 37831453896.

**Symptom:** The preregistered inference script failed in the expiry-day block bootstrap because the bootstrap block arrays included both numeric P&L and Timestamp values.

**Cause:** The bootstrap call passed a dataframe containing both expiry_dt and the renamed P&L column and converted the entire grouped dataframe to numpy.

**Evidence status:** No statistical output was accepted. The failure occurred before the audit or publication stages.

**Correction:** The bootstrap now explicitly groups expiry dates but resamples only the numeric P&L vector. The permutation test, hypothesis family, cost models, seed, replicate counts, protected holdout and promotion criteria are unchanged.

**Prevention:** Bootstrap routines must explicitly isolate the numeric statistic column before conversion to numpy and include a numeric-schema assertion.


## 2026-10-09 — Phase 50B-6 corrected run 37832396945
No new error. The corrected inference run passed all numerical, audit and publication gates. F50B-097 was the only Phase 50B-6 implementation defect and was corrected before accepted inference.


## 2026-10-09 — Phase 50B-7 initialization
No new error. Final manuscript phase initialized from the audited 50B-6 evidence.


## 2026-10-09 — Phase 51 initialization
No error. New phase registered from the terminal Phase 50B evidence. No Phase 50B result was modified.


## 2026-10-09 — Phase 51-1 data audit
F51-001: the initially selected NIFTY spot cache ends 2026-07-02 while the frozen OOS window extends to 2026-08-04. No strategy P&L was calculated from this incomplete source. The OOS window remains frozen. A separate spot-source fallback and overlap audit is required before replay.


## 2026-10-09 — Phase 51 tooling audit

### F51-002 — Local repository clone unavailable
The container runtime attempted a read-only clone of the public repository for independent file inspection, but outbound DNS/network access was unavailable (`Could not resolve host: github.com`).

**Evidence status:** tooling-only; no repository or numerical evidence changed.

**Correction:** Repository inspection continued exclusively through the authenticated GitHub connector, including branch, file, commit and Actions APIs.

**Prevention:** Prefer the GitHub connector for repository access; use the container only when the required bytes are already locally available or network access is known to work.

### F51-003 — Fallback audit was initially only a download/print stub
The Phase-51 fallback scripts created in the prior step downloaded the Jitendra12421 spot file and printed its columns/tail but did not yet enforce the registered schema, full OOS coverage, timestamp integrity, or overlap-discrepancy gate.

**Evidence status:** no strategy P&L was calculated; no scientific evidence was produced.

**Correction:** The fallback scripts are being replaced by explicit acquisition, coverage, timestamp-integrity and overlap-comparison gates before replay.

### F51-004 — Repository update batch orchestration syntax error
A multi-file update script failed in the tool runtime with a JavaScript `SyntaxError` before any GitHub write occurred.

**Evidence status:** tooling-only; no repository or numerical evidence changed.

**Correction:** Subsequent Phase-51 writes are being performed as deterministic one-file operations with fresh SHA reads where needed.


## 2026-10-09 — Phase 51-1A fallback gate correction

### F51-005 — Initial session-length gate rejected legitimate shortened-session candidates
Actions run **37835085807** downloaded the fallback successfully but stopped because three OOS dates had fewer than 300 rows: 2026-05-25 (277 rows), 2026-06-25 (30 rows) and 2026-07-08 (30 rows).

**Evidence status:** no fallback gate was accepted; no overlap result or strategy P&L was produced.

**Diagnosis:** A simple row-count threshold cannot distinguish a legitimate shortened trading session from a truncated 30-row source fragment.

**Correction:** The gate now records exact first/last timestamps, session span and maximum internal gap for short days. A short day is accepted only when it still has at least 240 rows, spans at least 240 minutes and has no internal gap greater than five minutes. Tiny 30-row fragments will fail closed.

**Prevention:** Session completeness tests must use temporal continuity and session-span invariants, not row count alone.


## 2026-10-09 — Phase 51-1A source-quality finding

### F51-006 — Independent fallback source contains material intraday gaps
The corrected fallback audit exposed three suspicious OOS dates: 2026-05-25 has 277 rows from 09:15–15:29 with a 99-minute internal gap; 2026-06-25 has only 30 rows from 15:00–15:29; 2026-07-08 has only 30 rows from 15:00–15:29.

**Evidence status:** no strategy P&L was calculated. The source remains rejected as a replay source until the gap is explained or an independent source passes the frozen replacement gate.

**External calendar cross-check:** NSE's 2026 equity-derivatives holiday schedule lists 01-May, 28-May and 26-Jun in this OOS interval, not 25-May, 25-Jun or 08-Jul. NSE regular equity-market trading opens at 09:15. The observed 30-row fragments therefore are not explained by a scheduled market holiday. citeturn302243search0turn302243search12

**Correction:** retain fail-closed behavior and perform source triangulation with an independent public NIFTY 1-minute dataset before any OOS replay.

### F51-007 — Duplicate Phase-51-1A diagnostic runs from overlapping push triggers
The workflow-file update and marker update both matched the workflow's branch/path trigger, producing two data-gate runs (37835369256 and 37835394540). No strategy P&L or promotion evidence was generated.

**Correction:** treat the cleanest completed gate run as the audit reference and avoid additional marker commits unless a workflow-only change is required. The workflow itself remains manually runnable.

### F51-008 — Plan update wrapper interpolation error
A tool-orchestration string containing Markdown backticks failed with a JavaScript SyntaxError before any GitHub write occurred.

**Evidence status:** tooling-only; no repository or numerical evidence changed.

**Correction:** use plain-text generated sections without embedded template-literal delimiters for repository writes.


## 2026-10-09 — Phase 51-1 options-source completeness finding

### F51-009 — Frozen OOS options file stops before the frozen OOS endpoint
The Phase 51-1 data manifest contains NIFTY option rows from 2026-04-21 through 2026-07-21, with 14 weekly expiries. The frozen OOS window ends 2026-08-04, so the 2026-07-28 and 2026-08-04 expiry blocks are absent from the initially selected options source.

**Evidence status:** no strategy P&L was calculated. The OOS window remains frozen; the missing expiry blocks are not silently removed from the research period.

**Correction:** register an independent pre-P&L option-source augmentation gate. Thetrademarkk's NIFTY options directory contains explicit 2026-07-28 and 2026-08-04 1-minute option files. These files will be compared against common expiries from the original rissin source before either is used for replay.

**Prevention:** Phase 51 option coverage must be audited at the expiry-block level, not merely by total row count and maximum observed expiry.


## 2026-10-09 — Phase 51-1A freeze publication correction

### F51-010 — Validated spot-source freeze depended on a non-persisted fallback manifest
Run **37836116045** completed the spot source acquisition, primary overlap and independent triangulation gates successfully, but the final freeze step failed because `results/phase51/spot_fallback_manifest.json` was not present in the runner workspace at publication time.

**Evidence status:** source-quality evidence is valid and already persisted in the Actions artifact; no P&L or inference was affected.

**Correction:** the freeze step will depend only on the persisted overlap/triangulation artifacts that are present after the audit steps, and will record the failed fallback as an explicit F51-006 source-quality rejection rather than requiring the transient acquisition manifest.

**Prevention:** publication steps must consume only artifacts explicitly guaranteed by the immediately preceding workflow contract.


### F51-011 — Spot freeze publication schema mismatch
Run **37836313364** failed only in the freeze publication step because the workflow treated `spot_fallback_gate.json` as if source metadata were top-level; the file stores it under `details`.

**Evidence status:** scientific gates passed; no P&L affected.

**Correction:** use the persisted JSON schema as emitted by the overlap audit (`details.fallback_source` and `details.gate`) in the freeze step.


### F51-012 — Option augmentation run cancelled by concurrent branch publication
Options gate run **37836222630** was cancelled during its audit while the spot-source validation workflow was publishing a new branch commit. No option augmentation result was accepted or used.

**Correction:** rerun the options gate after the spot-source freeze is complete and the branch is stable.


## 2026-10-09 — Phase 51-1B final options-source feasibility finding

### F51-015 — Public supplemental NIFTY 1-minute files do not cover the frozen missing expiries
The independent `thetrademarkk/india-index-options-1m` files named `2026-07-28.parquet` and `2026-08-04.parquet` were audited successfully at schema level, but their actual timestamps end on **2026-07-02 15:30 IST** and **2026-07-02 15:29 IST**, respectively. They therefore cannot supply the frozen OOS sessions for the 2026-07-28 and 2026-08-04 expiries.

The pre-P&L overlap audit also showed that the supplemental source is only a partial subset of the original RISSIN rows for common expiries (34.6%, 15.0%, and 4.6% matched coverage for 7 Jul, 14 Jul and 21 Jul), so it is not a drop-in replacement for the frozen source. Price differences were generally small on matched rows, but 7 Jul also failed the registered p95-relative-error threshold.

**Decision:** do not augment the frozen OOS with this source. No strategy P&L has been calculated for Phase 51 from incomplete option data.

**External-source search:** public evidence confirms Upstox provides expired-contract 1-minute candles, but its expired-instrument APIs require an authenticated Upstox Plus account. Public FNOTrader material advertises a current NIFTY 1-minute archive, but no installed project integration is available to acquire its raw data. Daily historical pages (e.g. MoneyTicks / optionbacktesting.in) are insufficient for minute-level replay.

**Required next acquisition:** authenticated 1-minute expired-option source reaching at least 2026-08-04, or a publicly downloadable dataset with equivalent provenance and full strike/time coverage. Until then Phase 51 remains DATA-BLOCKED and the frozen OOS window is unchanged.


## 2026-10-09 — Phase 51-1C authenticated-source gate
### F51-016 — Missing Upstox access secret
Workflow run 37839447686 could not acquire the missing 2026-07-28 and 2026-08-04 expired NIFTY option contracts because UPSTOX_ACCESS_TOKEN is not configured in repository secrets. No source data or strategy P&L was fabricated.


## 2026-10-09 — Phase 51-1D source audit

### F51-016 — UI/backtest platforms cannot be promoted to raw-data sources without an authorized export/API
StockMock, StockMojo, FNOTrader, QuantFlo and AlgoTest were checked as potential recovery sources. Their public documentation establishes minute-level historical option data/backtesting capability, but this audit did not establish an authorized bulk raw-data export/API for the frozen OOS blocks for this repository. Treating their UI outputs or opaque backtest numbers as if they were the missing raw tape would violate the preregistered source-equivalence requirement.

**Evidence status:** no strategy P&L or inference was calculated.

**Correction:** register these platforms as independent validation/oracle sources only. Prioritize authenticated Upstox raw acquisition and authorized OptionsData.shop raw Parquet. Retain NSE as the official licensed-data route.

**Prevention:** platform existence or minute-level UI visibility is not sufficient evidence of a reproducible raw dataset; require documented authorized export/API access and a pre-P&L equivalence audit.
