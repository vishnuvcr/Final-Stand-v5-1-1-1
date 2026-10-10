# Phase 96 Research Log

- 2026-10-10: Reviewed Phase 94 finite execution plan and Phase 95 preregistration. Created Phase 96 branch from Phase 95.
- 2026-10-10: Registered moving-average/seasonality scope, fixed test-period policy, next-session execution rule, cost gate, and explicit no-2026-holdout rule before implementation.
- Status: empirical outcomes pending; no claims of replication or profitability.

- 2026-10-10: First Phase 96 CI attempt exposed a Python SyntaxError from literal escaped newlines and a failure-log staging defect when no output directory existed. Recorded both; fixed source and workflow. The fixed replay is not accepted until a fresh run passes tests and publishes outputs.

- 2026-10-10: Phase 96 run [38072623419](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38072623419) passed unit tests and generated six SMA/EMA variant results across 1,486 sessions (2020–2025). Provisional gross/net-proxy total returns ranged 52.5%–100.9%, versus 114.7% for buy-and-hold; Sharpe proxy was higher for SMA(10,50) and EMA(10,50), while their total returns were lower. These are non-inferential, spot-index proxy results—not paper-exact, not investable spot returns, and not options P&L.
- Audit correction: max drawdown was calculated from the full history's equity curve rather than an equity curve reset at the OOS start. Fixed in commit `36ae451dae9b0752f8282b870682ebc129531234`; the earlier report is provisional until the corrected run passes.
