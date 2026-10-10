# Phase 66 Error and Limitation Log

## E66-001 — OHLC is not execution-grade quote data
- Status: OPEN limitation, not a software error.
- Impact: simulated prices cannot establish actual bid/ask, spread, depth, queue priority or market impact.
- Mitigation: label outputs OHLC-reference results; include adverse tick and slippage/fee stress scenarios; no claims of exact execution replication.

## E66-002 — Historical period mismatch
- Status: OPEN limitation.
- Impact: selected dataset does not span the paper's complete October 2008–September 2018 sample.
- Mitigation: report actual source coverage; do not compare non-matching totals as if directly comparable.

## E66-003 — Zero completed trades in Phase 64
- Status: follow-up in Phase 65 found coverage blockers; Phase 66 must confirm from its outputs.
- Impact: expectancy, win rate, profit factor, drawdown and P&L inference are not estimable when trade count is zero.
- Mitigation: report coverage first and do not fabricate fills.
