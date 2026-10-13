# Phase 109 Research Log

## 2026-10-12 — Requirement clarified
- User corrected the interpretation: minimum 1,000 distinct strategy families, not only 1,000 configurations.
- Plan revised to require ≥1,000 meaningful rule architectures with unique IDs/fingerprints and feasibility gates; ≥1,000 unique configurations per family; all cost cases per configuration.
- Target minimum: 1,000,000 family-configuration pairs and up to 24,000,000 cost-adjusted rows. These are targets, not completed counts.
- Implementation, source feasibility audit, data split, and runtime execution remain pending. Never claim completion without reconciled manifest/shard counts.
- Phase 108 run 38167282757 passed its ten-family/240-cost-row exploratory OHLC proxy screen; all ten were negative in primary and strict stress cases. No promotion.

## 2026-10-12 — Family registry and grid compiler
- Deterministic registry build completed at 2026-10-12 06:48 UTC. Registered 1,025 architecture combinations; exact duplicate fingerprints=0; fingerprints=1,025.
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
- Family input feasibility: 1,025 families; 689 blocked on unavailable inputs, 36 with proxy/execution gates, 300 with fields present but final gates pending. This is not a backtest.
- No strategy is promoted. All empirical evaluation remains pending historical source/point-in-time/license and OOS gates.

## 2026-10-12 07:14 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v1 attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 2,000, remaining 592,000.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 — Official NSE index-options backfill
- Window 2023-10-01 to 2026-10-09 (exclusive): 789 weekdays plus 5 observed special-session dates probed; 748 official archives parsed/cache-hit; 46 requested-date no-archive/fetch/schema statuses (not automatically called missing trading sessions).
- Selected index-option rows 3,345,150; identity-complete 3,345,150; price-complete 3,345,150; positive-volume 1,361,445; zero-volume 1,983,705; invalid positive-volume OHLC 0; duplicate contract keys 0.
- Legacy/UDiFF archives: 188/560. Raw ZIP data are in the private Actions cache and excluded from public repository artifacts.
- The three schema transition probes remain PASS: 2024-07-05 legacy, 2024-07-08 UDiFF, 2026-10-08 UDiFF. This expands source coverage but does not establish complete exchange-session coverage or execute any strategy.
- Official NSE Indices context status=PASS; VIX/NIFTY50/NIFTY BANK unique date counts: 748, 748, 748. Session reconciliation shows 0 observed NIFTY 50 dates without an option archive. See [VIX/index audit](results/phase109/NIFTYINDICES_CONTEXT_AUDIT.md) and [calendar reconciliation](results/phase109/NSE_CALENDAR_RECONCILIATION.md).
- Dhan rolling ATM supplement PASS: 75,177 5-minute rows; successful window-sides 50/50; failed/empty window-sides 0; these rows are feature-only because the contract may roll across strikes. See [Dhan audit](results/phase109/DHAN_ROLLING_OPTIONS_AUDIT.md).
- Official index futures extracted from 748 cached archives: futures dates 748; rows 8,976; missing lot-size 2,256; invalid positive-volume OHLC 4. Raw rows remain in private cache; EOD basis is not an intraday fill claim.
- Exact-contract model-derived IV/Greeks: 772,355 valid rows across 501 UDiFF archive dates. Exclusions: below-model lower bound 59,187; above-model upper bound 0; solver failures 37,032. Constant r=6.5%, q=0% must be sensitivity-tested; these are not exchange-reported Greeks.
- Backfill report: [NSE index-options coverage](results/phase109/NSE_INDEX_OPTIONS_BACKFILL_REPORT.md). Strategy evaluation, contract-size audit, out-of-sample split and multiple-testing correction remain pending.

## 2026-10-12 09:39 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 2,000, remaining 170,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 10:35 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 4,000, remaining 168,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 11:57 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 6,000, remaining 166,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 13:13 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 8,000, remaining 164,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 13:22 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 10,000, remaining 162,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 13:36 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 12,000, remaining 160,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 13:51 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 14,000, remaining 158,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 14:04 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 16,000, remaining 156,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 14:22 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 18,000, remaining 154,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 14:36 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 20,000, remaining 152,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 14:45 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 22,000, remaining 150,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 14:49 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 24,000, remaining 148,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 14:53 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 26,000, remaining 146,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 14:57 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 28,000, remaining 144,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:00 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 30,000, remaining 142,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:04 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 32,000, remaining 140,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:09 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 34,000, remaining 138,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:14 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 36,000, remaining 136,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:18 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 38,000, remaining 134,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:22 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 40,000, remaining 132,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:25 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 42,000, remaining 130,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:33 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 44,000, remaining 128,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:46 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 46,000, remaining 126,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:50 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 48,000, remaining 124,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 15:59 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 50,000, remaining 122,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:05 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 52,000, remaining 120,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:16 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 54,000, remaining 118,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:21 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 56,000, remaining 116,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:28 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 58,000, remaining 114,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:33 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 60,000, remaining 112,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:39 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 62,000, remaining 110,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:46 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 64,000, remaining 108,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 16:54 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 66,000, remaining 106,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 17:05 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 68,000, remaining 104,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 17:20 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 70,000, remaining 102,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 17:30 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 72,000, remaining 100,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 17:45 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 74,000, remaining 98,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 17:50 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 76,000, remaining 96,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 18:01 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 78,000, remaining 94,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 18:15 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 80,000, remaining 92,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 18:31 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 82,000, remaining 90,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 18:39 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 84,000, remaining 88,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 18:52 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 86,000, remaining 86,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 19:08 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 88,000, remaining 84,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 19:14 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 90,000, remaining 82,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 19:26 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 92,000, remaining 80,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 19:37 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 94,000, remaining 78,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 19:52 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 96,000, remaining 76,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 20:12 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 98,000, remaining 74,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 20:26 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 100,000, remaining 72,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 20:32 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 102,000, remaining 70,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 20:38 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 104,000, remaining 68,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 20:48 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 106,000, remaining 66,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 20:54 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 108,000, remaining 64,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 21:09 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 110,000, remaining 62,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 21:22 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 112,000, remaining 60,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 21:31 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 114,000, remaining 58,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 21:38 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 116,000, remaining 56,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 21:46 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 118,000, remaining 54,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 21:55 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 120,000, remaining 52,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 22:02 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 122,000, remaining 50,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 22:11 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 124,000, remaining 48,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 22:24 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 126,000, remaining 46,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 22:34 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 128,000, remaining 44,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 22:47 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 130,000, remaining 42,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 22:57 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 132,000, remaining 40,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 23:08 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 134,000, remaining 38,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 23:15 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 136,000, remaining 36,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 23:25 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 138,000, remaining 34,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 23:28 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 140,000, remaining 32,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 23:39 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 142,000, remaining 30,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-12 23:50 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 144,000, remaining 28,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 00:03 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 146,000, remaining 26,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 00:10 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 148,000, remaining 24,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 00:22 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 150,000, remaining 22,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 00:31 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 152,000, remaining 20,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 00:40 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 154,000, remaining 18,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 00:46 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 156,000, remaining 16,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 00:52 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 158,000, remaining 14,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 01:03 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 160,000, remaining 12,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 01:07 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 162,000, remaining 10,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 01:15 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 164,000, remaining 8,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 01:25 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 166,000, remaining 6,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.

## 2026-10-13 01:39 UTC — Grid evaluation shard
- Engine phase109-eod-engine-v4-session-coverage attempted 2,000 configs and produced 48,000 rows across 24 cost cases/config; cumulative attempts 168,000, remaining 4,800.
- Selection used development/validation only; the 2026-04+ holdout was not evaluated. EOD fills are proxies and no strategy was promoted.
