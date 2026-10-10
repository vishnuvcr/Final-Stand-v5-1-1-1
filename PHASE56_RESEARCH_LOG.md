# Phase 56 research log

## 2026-10-10 — Phase initiated and preregistered

- Created dedicated branch `phase-56-ohlc-pnl-sensitivity` from the Phase 55 evidence-repair branch.
- Preregistered a bounded 480-row diagnostic P&L sensitivity using the 11 Phase 54 thresholds, date-aware statutory costs, ₹10/₹20 brokerage cases and six slippage assumptions.
- Frozen market-data revision: `0f4800e43e6f96cec0794369d78eb4d3c4211ef5`. No raw market data will be downloaded.
- No strategy outcome has been computed or selected yet. All 132 threshold × brokerage × slippage scenario combinations are required, including negative or empty outcomes.
- Explicit guardrail: open-based simulated fills are not executable quote evidence; candle range is not bid/ask spread; no holdout or promotion.

## Run checkpoint 37995733702

- Run: [37995733702](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37995733702); workflow status=failure; report accepted=False; observed report status=REPORT_MISSING_OR_INVALID.
- No Phase56 result accepted until scenario counts, frozen thresholds and invariants pass.

## Run checkpoint 38019102367

- Run: [38019102367](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019102367); workflow status=failure; report accepted=False; observed report status=REPORT_MISSING_OR_INVALID.
- No Phase56 result accepted until scenario counts, frozen thresholds and invariants pass.

## Run checkpoint 38019146547

- Run: [38019146547](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38019146547); workflow=success; report=accepted; status=OHLC_PRICE_REFERENCE_PNL_SENSITIVITY_COMPLETE_NON_EXECUTABLE.
- Input rows=480; SHA-256=8b0a1167573fdbd7ee32c77bcf493b79db23f8eeeb67aa92700a15c4e8c3683f; pinned revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- Parent statuses={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}; complete leg payloads=480.
- Eligible rows by threshold={"10": 150, "1000": 380, "12": 227, "15": 298, "2": 1, "20": 345, "3": 1, "4": 8, "5": 24, "6": 55, "8": 91}.
- Output matrix: 132 threshold/cost summaries; 5,280 configuration summaries; 924 family summaries; 18,960 non-executable price-reference trade scenarios; 440 severe-cost configuration-threshold screens.
- Configurations passing the severe-cost screen at any threshold=5; passing configuration-threshold pairs=5.
- All costs/slippage are modeled assumptions; candle range is not bid/ask spread; no holdout used and no strategy is promoted.

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
