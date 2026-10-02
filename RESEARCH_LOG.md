# Research Log

## 2026-10-02 — Research restart
- Restarted because the prior implementation did not exactly match the latest strategy definition.
- Created phase-1-restart-strategy-v2.
- Prior global n=6..15 x Call/Put results are superseded.

## 2026-10-02 — Phase 2 execution
- Created phase-2-restart-v2.
- Successful primary run: 196 eligible trades.
- Net win rate 37.24%; mean net -₹303.48; total net -₹59,481.78.
- Direction: BEARISH 19 trades, BULLISH 177 trades.
- n distribution: 6=188, 7=6, 8=1, 15=1.

## 2026-10-02 — Phase 3 statistical analysis
- Created phase-3-restart-statistics.
- First statistical workflow failed during grouped aggregation; implementation was corrected to explicit group loops and rerun successfully.
- Overall profit factor: 0.719.
- Max drawdown on cumulative trade-order net P&L: -₹80,224.28.
- Bootstrap 95% CI for mean net P&L: -₹702.98 to ₹86.52.
- Bootstrap 95% CI for win rate: 30.61% to 44.39%.
- Yearly net P&L: 2021 -₹7,813.05; 2022 -₹1,314.54; 2023 -₹9,536.07; 2024 -₹4,283.23; 2025 -₹47,088.19; 2026 +₹10,553.30 through Sep-2026.
- Target exits: 73, all profitable in the sample; expiry exits: 123, all losses in the sample.
- Selected n was 6 on 188/196 trades.

## 2026-10-02 — Phase 3 completion
- Statistical artifacts persisted under results/restarted_v2/phase3/.
- Workflow restored to manual-only after autonomous execution.
- Next phase: robustness and sensitivity.

## 2026-10-02 — Phase 4 retry trigger
- Corrected a literal newline syntax error in the parameterized backtest before rerunning robustness scenarios.
