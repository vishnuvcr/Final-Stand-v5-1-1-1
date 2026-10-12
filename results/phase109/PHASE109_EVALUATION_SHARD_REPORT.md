# Phase 109 evaluation shard report

Status: **PARTIAL_SHARD_COMPLETE**

- Config cursor range: [14,000, 16,000); registry eligible-config denominator: 172,800.
- Configs attempted in this shard: 2,000; cost-adjusted rows generated: 48,000; expected cost cases/config: 24.
- Completed shard ranges currently recorded: 8; cumulative attempted configs: 16,000; cumulative cost rows: 384,000; remaining eligible configs: 156,800.
- Archive dates loaded: 748; source files loaded: 748; archive parse/duplicate warnings: 0.
- Official context coverage gate: {'INDIA_VIX': 748, 'NIFTY 50': 748, 'NIFTY BANK': 748}; minimum required per series: 710 over 2023-10-03–2026-10-08.
- Official options/index session reconciliation gate: {'official_nifty50_dates_observed': 748, 'observed_nifty50_sessions_without_valid_option_archive': 0, 'no_archive_status_on_observed_nifty50_session': 0, 'maximum_allowed_explicitly_attempted_gaps': 8, 'valid_option_archive_dates_without_nifty50_index_date': 0, 'coverage_pass': True, 'interpretation': 'Any remaining gaps must be explicitly present in the acquisition audit; trades requiring an absent archive remain excluded.'}.
- Cost model: `round_trip_cost`; P&L trade entries before 2024-10-01 are blocked.
- Sample: selection. Selection mode uses development/validation only; holdout mode must load the frozen validation shortlist and scores only 2026-04-01 through 2026-10-08.
- All net results remain diagnostic, use EOD OHLC execution proxies, and are exposed to selection/multiple-testing bias. No strategy is promoted.
- Public outputs contain per-configuration/per-cost summary metrics only; raw options rows and trade tapes remain private.
- Cost-row summary: `evaluation_shards/phase109_eval_v4_session_coverage_000014000-000016000.csv.gz`; machine-readable shard summary: `evaluation_shard_summary.json`; resumable ledger: `evaluation_progress.json`.
