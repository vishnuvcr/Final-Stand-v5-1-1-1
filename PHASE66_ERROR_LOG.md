# Phase 66 Error and Limitation Log

## E66-001 — OHLC is not execution-grade quote data
- Status: OPEN limitation, not a software error.
- Impact: simulated prices cannot establish actual bid/ask, spread, depth, queue priority or market impact.
- Mitigation: label outputs OHLC-reference results; include adverse tick and slippage/fee stress scenarios; no claims of exact execution replication.

## E66-002 — Historical period mismatch
- Status: OPEN limitation.
- Impact: selected dataset does not span the paper's complete October 2008–September 2018 sample.
- Mitigation: report actual source coverage; do not compare non-matching totals as if directly comparable.

## E66-003 — Zero completed trades
- Status: CONFIRMED DATA/PROTOCOL BLOCKER, not evidence of unprofitability.
- Impact: expectancy, win rate, profit factor, drawdown and P&L inference are not estimable when trade count is zero.
- Mitigation: report coverage first and do not fabricate fills. Treat printed ₹0.00 aggregate sums as empty-ledger placeholders.

## E66-004 — First workflow failed due missing branch-local cost helper
- Status: RESOLVED.
- First failing run: [38028015865](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38028015865).
- Cause: runner imported `phase43_vix_strategy_sweep` which was not in the new phase branch.
- Fix: added `research/phase66_cost_helpers.py` with the accepted helper implementation and changed the Phase 66 runner import. The next run passed syntax, test, numerical, report, output-validation, and publication steps.

## E66-005 — Stale phase number in decision metadata
- Status: RESOLVED.
- Cause: the copied script emitted `"phase": 64` in decision.json.
- Fix: corrected the generator and committed decision output to phase 66.

## E66-006 — Empty-sample P&L chart/table ambiguity
- Status: RESOLVED IN REPORT TEXT / SOURCE BUILDER.
- Cause: aggregate sum fields return ₹0.00 on an empty trade ledger, which can be misread as a realized zero return.
- Fix: report and report-builder explicitly state there are zero completed trades, money sums are placeholders, and performance metrics are not estimable. Do not interpret zero bars as evidence of zero strategy returns.

## Automated run history
- Failed attempt: run [38028015865](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38028015865), commit `9eabb1c8d321db08ad624cdc5617fff61b749434`.
- Successful numerical run: [38028140800](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38028140800), commit `99695fd038052d9c6826e05f3ba67280f12e3311`.
- Successful run completion marker confirms 2026 holdout option files downloaded = 0.

- Final verification rerun: [38028425558](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38028425558) passed after the metadata/reporting corrections; numerical outcome remained unchanged.
