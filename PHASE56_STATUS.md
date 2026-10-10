# Phase 56 status — OHLC price-reference P&L sensitivity

**Overall:** COMPLETE — preregistered diagnostic P&L sensitivity passed; no strategy promotion.  
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
- [x] Verify input fingerprint, 480 rows and full selected-leg status.
- [x] Match eligibility counts at every threshold to Phase 54.
- [x] Compute every preregistered brokerage/slippage combination from exact stored open references.
- [x] Validate cost arithmetic, invariants, output completeness and regression tests.
- [x] Persist machine-readable CSV/JSON/Markdown outputs, append logs and update README.
- [x] Close after the finite matrix; no further optimization in this phase.

**Scientific prior:** this is a price-reference sensitivity, not an executable backtest. An OHLC range proxy is not a quoted bid/ask spread; no result is promotable.

## Run checkpoint 37995733702

- Run: [37995733702](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37995733702); workflow status=failure; report accepted=False; observed report status=REPORT_MISSING_OR_INVALID.
- No Phase56 result accepted until scenario counts, frozen thresholds and invariants pass.

## Run checkpoint 38019102367

- Run: [38019102367](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019102367); workflow status=failure; report accepted=False; observed report status=REPORT_MISSING_OR_INVALID.
- No Phase56 result accepted until scenario counts, frozen thresholds and invariants pass.

## Run checkpoint 38019146547

- Run: [38019323348](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019323348); workflow=success; report=accepted; status=OHLC_PRICE_REFERENCE_PNL_SENSITIVITY_COMPLETE_NON_EXECUTABLE.
- Input rows=480; SHA-256=8b0a1167573fdbd7ee32c77bcf493b79db23f8eeeb67aa92700a15c4e8c3683f; pinned revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- Parent statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}; complete leg payloads=480.
- Eligible rows by threshold={"10": 150, "1000": 380, "12": 227, "15": 298, "2": 1, "20": 345, "3": 1, "4": 8, "5": 24, "6": 55, "8": 91}.
- Output matrix: 132 threshold/cost summaries; 5,280 configuration summaries; 924 family summaries; 18,960 non-executable price-reference trade scenarios; 440 severe-cost configuration-threshold screens.
- Configurations passing the severe-cost screen at any threshold=5; passing configuration-threshold pairs=5.
- All costs/slippage are modeled assumptions; candle range is not bid/ask spread; no holdout used and no strategy is promoted.
\n## Final decision — Phase 56 closed\n\nAccepted run: [38019146547](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019146547). All 480 input rows and all selected-leg payloads passed validation. The 11 thresholds reproduced Phase 54 eligibility counts exactly; 18,960 modeled cost-scenario rows were computed across 11 thresholds, two brokerage levels and six adverse-slippage assumptions. Five configuration-threshold pairs passed the preregistered severe-cost screen, all at the 1000% diagnostic threshold; these are quote-validation leads only, not strategy winners. No holdout, statistical significance claim, executable-fill claim or promotion. The OHLC range proxy is not a spread.\n

## Run checkpoint 38019323348

- Run: [38019323348](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019323348); workflow=success; report=accepted; status=OHLC_PRICE_REFERENCE_PNL_SENSITIVITY_COMPLETE_NON_EXECUTABLE.
- Input rows=480; SHA-256=fbae8f080a685b2bafcc1248995b9342fea4c598110916e42296bee1af57dd55; pinned revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- Parent statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}; complete leg payloads=480.
- Eligible rows by threshold={"10": 150, "1000": 380, "12": 227, "15": 298, "2": 1, "20": 345, "3": 1, "4": 8, "5": 24, "6": 55, "8": 91}.
- Output matrix: 132 threshold/cost summaries; 5,280 configuration summaries; 924 family summaries; 18,960 non-executable price-reference trade scenarios; 440 severe-cost configuration-threshold screens.
- Configurations passing the severe-cost screen at any threshold=5; passing configuration-threshold pairs=5.
- All costs/slippage are modeled assumptions; candle range is not bid/ask spread; no holdout used and no strategy is promoted.

## Supplemental robustness interpretation — severe-cost screen (2026-10-10)

An independent read of the accepted `robustness_screen.csv` confirms five configuration-threshold pairs pass the **coded** severe-cost screen at the 1000% diagnostic threshold, using ₹20/order and ₹0.50 adverse slippage per fill. The code's screen is defined as at least 10 distinct event identities plus positive aggregate configuration-event net P&L. It reports leave-one-event-out minimum separately; that minimum is **not** part of the current pass condition.

- `2432b3ba491006a1f15a` — LONG_STRADDLE, ATM offset 3 steps, entry 13:00 IST: grid-sum net ₹11,813.17 across 10 event identities; leave-one-event-out minimum +₹3,953.36.
- `60c2d16b969965ff2b15` — BEAR_CALL_SPREAD, ATM offset 1 step, entry 13:00 IST: grid-sum net ₹1,570.09 across 10 event identities; leave-one-event-out minimum +₹1,133.31.
- `f96abfc5c945c889729f` — BEAR_CALL_SPREAD, ATM offset 1 step, wing 3 steps, entry 13:00 IST: grid-sum net ₹3,076.01 across 10 event identities; leave-one-event-out minimum +₹2,384.07.
- `0a2c71c6e12e773afc2d` — LONG_STRADDLE, ATM offset 1 step, entry 13:00 IST: grid-sum net ₹3,002.47 across 10 event identities; leave-one-event-out minimum −₹3,558.39.
- `c31e45a39d28e22b70b2` — BUY_PUT, ATM offset 1 step, entry 13:00 IST: grid-sum net ₹3,495.90 across 10 event identities; leave-one-event-out minimum −₹1,680.54.

**Interpretation:** three of five have a positive leave-one-event-out minimum; two are visibly event-sensitive under this additional descriptive check. This post-run reading does not alter the preregistered screen, select a configuration, or establish a strategy result. Every pair uses the 1000% near-removal diagnostic threshold, OHLC-open price references rather than executable quotes, and overlapping configuration-event samples; sums are not portfolio P&L. The source remains CC BY-NC 4.0 and no promotion/holdout use is permitted. These IDs are merely leads for authorized quote validation if the data-license gate is later resolved.
