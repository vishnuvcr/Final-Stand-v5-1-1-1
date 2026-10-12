# Phase 109 Research Log

## 2026-10-12 — Requirement clarified
- User corrected the interpretation: minimum 1,000 distinct strategy families, not only 1,000 configurations.
- Plan revised to require ≥1,000 meaningful rule architectures with unique IDs/fingerprints and feasibility gates; ≥1,000 unique configurations per family; all cost cases per configuration.
- Target minimum: 1,000,000 family-configuration pairs and up to 24,000,000 cost-adjusted rows. These are targets, not completed counts.
- Implementation, source feasibility audit, data split, and runtime execution remain pending. Never claim completion without reconciled manifest/shard counts.
- Phase 108 run 38167282757 passed its ten-family/240-cost-row exploratory OHLC proxy screen; all ten were negative in primary and strict stress cases. No promotion.

## 2026-10-12 — Family registry and grid compiler
- Deterministic registry build completed at 2026-10-12 06:36 UTC. Registered 1,025 architecture combinations; exact duplicate fingerprints=0; fingerprints=1,025.
- Minimum/maximum configurations per family: 1,080/19,440; complete applicable Cartesian universe=3,719,520 configuration tuples and 89,268,480 cost rows across 45 deterministic shards.
- Registry and manifest hashes: registry `7554ceceb9df6a403f409b9877b6ff0b57c9b0bca724e4ee2c8c25799dbdf60d`; configuration `3253d8df32e73d5b66208373d7ca2d9e30fc20f656dbed52776b71fb31f9941a`; cost grid `0dc9f1792ba6b8eeec903577d3cfd83d122aaa36785248313982e7843a00e33f`; full manifest `f5c0439bc9d9b994a4b5b5ca2bc2260e5b26b8346b91335b4eed894ff5cae6cc`.
- Self-test: PASS. This verifies count, distinct architecture fingerprints, valid per-family Cartesian counts, 24 cost scenarios and contiguous shard ranges only; it does not run the strategies.
- Source-access findings:
- DhanHQ rolling expired-options API : **AUTH_AND_SCHEMA_PROBE_OK**; candidates=; bars=231.
- Hugging Face dataset discovery DII FII India: **NO_RESULTS**; candidates=0; bars=.
- Hugging Face dataset discovery India VIX: **METADATA_DISCOVERED**; candidates=1; bars=.
- Hugging Face dataset discovery India stock market minute: **NO_RESULTS**; candidates=0; bars=.
- Hugging Face dataset discovery NIFTY: **METADATA_DISCOVERED**; candidates=20; bars=.
- Hugging Face dataset discovery NSE bhavcopy: **METADATA_DISCOVERED**; candidates=1; bars=.
- Hugging Face dataset discovery india-index-options-1m: **METADATA_DISCOVERED**; candidates=2; bars=.
- Hugging Face dataset discovery indian markets: **METADATA_DISCOVERED**; candidates=4; bars=.
- Hugging Face dataset discovery nse-options-intraday: **METADATA_DISCOVERED**; candidates=1; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_DECLARED_BUT_UNVERIFIED**; candidates=; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_DECLARED_BUT_UNVERIFIED**; candidates=; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_MISSING**; candidates=; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_DECLARED_BUT_UNVERIFIED**; candidates=; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_DECLARED_BUT_UNVERIFIED**; candidates=; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_DECLARED_BUT_UNVERIFIED**; candidates=; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_DECLARED_BUT_UNVERIFIED**; candidates=; bars=.
- Hugging Face dataset card inspection : **METADATA_DISCOVERED_LICENSE_DECLARED_BUT_UNVERIFIED**; candidates=; bars=.
- Official NSE legacy/UDiFF boundary + recent session probes: 3/3 passed; overall=PASS.
- Source feasibility inventory: 14 registered source classes; see matrix/report for source gates and blocked datasets.
- Family input feasibility: 1,025 families; 923 blocked on unavailable inputs, 54 with proxy/execution gates, 48 with fields present but final gates pending. This is not a backtest.
- No strategy is promoted. All empirical evaluation remains pending historical source/point-in-time/license and OOS gates.

## 2026-10-12 — Restart fixes before first valid shard
- Fixed the merged-index audit's field mismatch after acquisition run 38207969439 failed; chunk-level date-parse metrics are now used for that gate.
- Corrected UDiFF normalization in the evaluator (IDO→OPTIDX, IDF→FUTIDX) and model-Greeks extractor (IDO). Added a synthetic UDiFF evaluator regression test. This addresses code paths that could otherwise silently produce zero option/factor rows.
- Compiler run 38211795297 passed its compile/source-inventory steps and invoked its dispatch step; the evaluation job's actual execution/result must be verified separately.
- Next: confirm latest acquisition and regression-test outcomes, inspect evaluation shard counts/coverage, and only then report empirical strategy performance. No promotion yet.

## 2026-10-12 — Official NSE index-options backfill
- Window 2023-10-01 to 2026-10-09 (exclusive): 789 weekdays probed, 743 official archives parsed/cache-hit, 46 no-archive/fetch/schema statuses (not automatically called missing trading sessions).
- Selected index-option rows 3,321,984; identity-complete 3,321,984; price-complete 3,321,984; positive-volume 1,353,090; zero-volume 1,968,894; invalid positive-volume OHLC 0; duplicate contract keys 0.
- Legacy/UDiFF archives: 185/558. Raw ZIP data are in the private Actions cache and excluded from public repository artifacts.
- The three schema transition probes remain PASS: 2024-07-05 legacy, 2024-07-08 UDiFF, 2026-10-08 UDiFF. This expands source coverage but does not establish complete exchange-session coverage or execute any strategy.
- Official NSE Indices context status=PASS; VIX/NIFTY50/NIFTY BANK unique date counts: 218, 218, 218. Session reconciliation shows 1 observed NIFTY 50 dates without an option archive. See [VIX/index audit](results/phase109/NIFTYINDICES_CONTEXT_AUDIT.md) and [calendar reconciliation](results/phase109/NSE_CALENDAR_RECONCILIATION.md).
- Dhan rolling ATM supplement PASS: 75,177 5-minute rows; successful window-sides 50/50; failed/empty window-sides 0; these rows are feature-only because the contract may roll across strikes. See [Dhan audit](results/phase109/DHAN_ROLLING_OPTIONS_AUDIT.md).
- Official index futures extracted from 743 cached archives: futures dates 743; rows 8,916; missing lot-size 2,220; invalid positive-volume OHLC 4. Raw rows remain in private cache; EOD basis is not an intraday fill claim.
- Exact-contract model-derived IV/Greeks: 769,213 valid rows across 499 UDiFF archive dates. Exclusions: below-model lower bound 58,888; above-model upper bound 0; solver failures 37,032. Constant r=6.5%, q=0% must be sensitivity-tested; these are not exchange-reported Greeks.
- Backfill report: [NSE index-options coverage](results/phase109/NSE_INDEX_OPTIONS_BACKFILL_REPORT.md). Strategy evaluation, contract-size audit, out-of-sample split and multiple-testing correction remain pending.

