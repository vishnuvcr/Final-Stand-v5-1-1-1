# Phase 56 status — OHLC price-reference P&L sensitivity

**Overall:** OPEN — preregistered diagnostic P&L sensitivity; no strategy promotion.  
**Branch:** `phase-56-ohlc-pnl-sensitivity`  
**Parent:** Phase 55 leg-audit payload repair; Phase 54 coverage sensitivity.  
**Input:** `results/phase52/historical_pilot/event_replay.csv`; 480 frozen configuration-event rows.  
**Pinned market-data revision:** `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`.  
**Design:** 11 previously registered OHLC-range thresholds × 2 brokerage cases × 6 adverse-slippage levels.  
**Forbidden:** quote/spread claims, true execution claims, holdout access, strategy promotion.

## Starting evidence
The parent ledger is expected to reconcile to 379 `EXCLUDED_OHLC_RANGE_PROXY`, 100 `BLOCKED_LEG_ELIGIBILITY`, and one `REPLAY_PASS`. The all-leg payload has been independently parsed on Phase 55's current output. The dedicated newest Phase 55 workflow run [37993968572](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37993968572) is verifying the expanded audit gate; Phase 56 will accept outputs only after its own row/leg checks and Phase 54 eligibility counts match.

## Gates
- [x] Freeze research question, event universe, threshold grid and cost assumptions in [plan](PHASE56_RESEARCH_PLAN.md).
- [ ] Verify input fingerprint, 480 rows and full selected-leg status.
- [ ] Match eligibility counts at every threshold to Phase 54.
- [ ] Compute every preregistered brokerage/slippage combination from exact stored open references.
- [ ] Validate cost arithmetic, invariants, output completeness and regression tests.
- [ ] Persist machine-readable CSV/JSON/Markdown outputs, append logs and update README.
- [ ] Close after the finite matrix; no further optimization in this phase.

**Scientific prior:** this is a price-reference sensitivity, not an executable backtest. An OHLC range proxy is not a quoted bid/ask spread; no result is promotable.
