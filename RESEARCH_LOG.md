# Research Log

## 2026-10-02 — Research restart
- Restarted because the prior implementation did not exactly match the latest strategy definition.
- Created phase-1-restart-strategy-v2.
- Prior global n=6..15 x Call/Put results are superseded.

## 2026-10-02 — Direction selector locked
- Stage 1 uses OTM6/7/8 only.
- X_call6 > X_put6 selects the user-defined BEARISH call structure.
- X_call6 < X_put6 selects the user-defined BULLISH put structure.
- Exact equality is NO_TRADE_TIE.

## 2026-10-02 — High-n selector locked
- Stage 2 evaluates n=6..15 only on the Stage-1-selected side.
- Primary rule: X(n) >= 95% of selected-side X_max, then choose highest n.
- 90% and 97.5% are reserved for robustness analysis.

## 2026-10-02 — DTE correction
- Four trading sessions before expiry, with expiry=0 DTE.
- Ordinary Thursday expiry therefore uses preceding Friday 10:00.

## 2026-10-02 — Phase 2 execution
- GitHub Actions completed successfully using the cached Hugging Face dataset.
- 196 eligible trades were generated.
- Summary: net win rate 37.24%; mean net -₹303.48; median net -₹448.21; total net -₹59,481.78; total gross -₹42,880.50; costs ₹16,601.28; target-exit rate 37.24%.
- Direction: BEARISH 19 trades, mean net -₹632.24; BULLISH 177 trades, mean net -₹268.19.
- Selected n distribution: n=6 (188), n=7 (6), n=8 (1), n=15 (1).
- Missing/excluded cases: 7 expiries, recorded in results/restarted_v2/missing.csv.

## 2026-10-02 — Phase transition
- Created phase-2-restart-v2 from the completed Phase 1 execution state.
- Restored the workflow to manual-only after autonomous execution.
- Phase 3 statistical analysis is now the next planned phase.
