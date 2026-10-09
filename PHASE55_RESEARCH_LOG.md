# Phase 55 research log

## Step 1 — 2026-10-10 — Audit schema repair
- Created a separate branch from Phase 52.
- Added a helper to create a placeholder audit row for every selected leg before evaluation.
- Reworked leg evaluation to keep processing the remaining legs after the first gate failure, while preserving the first deterministic row-level exclusion reason.
- Added a fail-closed output invariant for expected leg count and unique leg IDs by strategy family.
- Actual pilot rerun and regression verification are pending.

## Run 37988475159

- Run: [37988475159](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37988475159); workflow status=\failure; audit PASS=False.
- Output is not accepted as complete unless the row/leg invariant audit passes.

## Run 37988611330

- Run: [37988611330](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37988611330); workflow status=success; audit PASS.
- Rows=480; status counts={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Leg payload rows audited=380; cost rows=6; source revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- No holdout use, raw data committed, or strategy promotion.

## Run 37993167521

- Run: [37993167521](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/37993167521); workflow status=success; audit PASS.
- Rows=480; status counts={"BLOCKED_LEG_ELIGIBILITY": 100, "EXCLUDED_OHLC_RANGE_PROXY": 379, "REPLAY_PASS": 1}.
- Leg payload rows audited=380; cost rows=6; source revision=0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- No holdout use, raw data committed, or strategy promotion.
