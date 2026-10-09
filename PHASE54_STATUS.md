# Phase 54 status — OHLC-reference eligibility sensitivity

**Overall:** ACTIVE — non-executable coverage sensitivity only.

- Branch: phase-54-ohcl-reference-sensitivity
- Parent: Phase 53 source audit concluded NO-GO for independent, legally cleared free historical bid/ask/depth.
- Input: frozen Phase 52 v0.2.1 event replay CSV; expected 480 configuration-event rows.
- Method: vary only diagnostic OHLC range threshold across 11 preregistered values; preserve exact prior-minute OI >= 100 and existing entry status.
- Forbidden: P&L recalculation, exit/fill assumptions, holdout use, strategy ranking, promotion or live-execution recommendations.
- Next gate: run tests, reconcile row counts, verify artifact/persistence, then close Phase 54.

## Run checkpoint 37989390203

- Run: [37989390203](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37989390203); workflow job status=success.
- Input rows=480; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Complete leg payload rows=102; incomplete=378; empty payloads=0; partial payloads=378.
- Range-excluded rows with complete leg payload=81.
- Sensitivity decision=OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE; alternate thresholds are not computed because parent output lacks complete leg-level evidence.
- No P&L recomputed, no exits validated, no raw data downloaded, no holdout used, no strategy promoted.


## Resume checkpoint — input provenance and leg evidence gate

- Identified and corrected a cross-branch input mismatch: the Phase 54 branch had inherited a Phase 52 v0.2 replay CSV (327,244 bytes; 373 empty leg payloads) while the canonical Phase 52 branch contains v0.2.1 audit-provenance (533,125 bytes; SHA 33c82a92e4546c4be10138dbf518ce0e51a83c03). Phase 54 input file was replaced with the canonical v0.2.1 CSV.
- The earlier successful Phase 54 workflow run 37988153104 is now superseded for data conclusions because it read the stale input. It remains evidence of test/workflow mechanics only.
- The corrected v0.2.1 replay has 480 rows with statuses 379 EXCLUDED_OHLC_RANGE_PROXY, 100 BLOCKED_LEG_ELIGIBILITY and 1 REPLAY_PASS. Payloads contain one leg in 474 rows and two legs in 6 rows, so many multi-leg range exclusions still lack all selected legs' diagnostic evidence.
- No alternate threshold counts are accepted until every selected leg's exact entry/prior-OI evidence is preserved. The Phase 52 runner has been patched to continue through remaining legs after a range-proxy failure and preserve their evidence before returning the canonical exclusion; this patch is not yet verified by a fresh Phase 52 replay.
- Next step: trigger/execute the Phase 52 historical pilot from its dedicated workflow, inspect all 480 payloads and compare hashes; then rerun Phase 54 sensitivity. Do not infer profitability or promote a strategy from this coverage study.

## Run checkpoint 37992224177

- Run: [37992224177](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992224177); workflow job status=failure. Report missing; no conclusion accepted.

## Run checkpoint 37992405659

- Run: [37992405659](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992405659); workflow job status=success.
- Input rows=480; input SHA-256=5052dcf08c20fe0bb921db2172ee7845327112a836145fe2eb91732015901abf; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Complete leg payload rows=82; incomplete=398; explicit hard prior-OI blockers=100; range-excluded rows with complete legs=81.
- Sensitivity decision=OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE; threshold results: NOT COMPUTED; incomplete/non-conclusive per-leg evidence gate remains closed.
- Candle range is not a bid/ask spread. No P&L, fills, exits or commercial/live strategy promotion inferred; holdout untouched.

## Run checkpoint 37992423020

- Run: [37992423020](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37992423020); workflow job status=success.
- Input rows=480; input SHA-256=5052dcf08c20fe0bb921db2172ee7845327112a836145fe2eb91732015901abf; baseline statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Complete leg payload rows=82; incomplete=398; explicit hard prior-OI blockers=100; range-excluded rows with complete legs=81.
- Sensitivity decision=OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE; threshold results: NOT COMPUTED; incomplete/non-conclusive per-leg evidence gate remains closed.
- Candle range is not a bid/ask spread. No P&L, fills, exits or commercial/live strategy promotion inferred; holdout untouched.
