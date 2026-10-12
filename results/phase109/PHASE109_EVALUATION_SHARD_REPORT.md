# Phase 109 evaluation shard report

Status: **PARTIAL_SHARD_COMPLETE**

- Config cursor range: [0, 2,000); registry eligible-config denominator: 594,000.
- Configs attempted in this shard: 2,000; cost-adjusted rows generated: 48,000; expected cost cases/config: 24.
- Completed shard ranges currently recorded: 1; cumulative attempted configs: 2,000; cumulative cost rows: 48,000; remaining eligible configs: 592,000.
- Archive dates loaded: 743; source files loaded: 743; archive parse/duplicate warnings: 0.
- Cost model: `round_trip_cost`; P&L trade entries before 2024-10-01 are blocked.
- Sample: selection. Selection mode uses development/validation only; holdout mode must load the frozen validation shortlist and scores only 2026-04-01 through 2026-10-08.
- All net results remain diagnostic, use EOD OHLC execution proxies, and are exposed to selection/multiple-testing bias. No strategy is promoted.
- Public outputs contain per-configuration/per-cost summary metrics only; raw options rows and trade tapes remain private.
- Cost-row summary: `evaluation_shards/phase109_eval_000000000-000002000.csv.gz`; machine-readable shard summary: `evaluation_shard_summary.json`; resumable ledger: `evaluation_progress.json`.
