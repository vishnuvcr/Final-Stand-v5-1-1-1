# Phase 82 Error / Limitation Log
Date: 2026-10-10

## E82-001 — Inference uncertainty and clustering
- Status: KNOWN LIMITATION.
- Expiry clustering preserves within-expiry dependence in the bootstrap; it cannot guarantee independence across neighbouring expiries or all calendar-time regimes.

## E82-002 — OHLC-only execution proxy
- Status: KNOWN LIMITATION.
- Inference uses Phase 81 derived outcomes from candle-open prices, modeled fees and adverse ticks. It cannot verify bid/ask, queue, depth, partial fills or market impact.

## E82-003 — Holdout isolation
- Status: CONTROL.
- The workflow must not download, load, score or rank 2026 holdout data. Only derived DEV/VAL CSVs are permitted inputs.

## E82-004 — Multiple testing
- Status: CONTROL.
- Holm correction must cover all 20 one-tick primary hypotheses (10 variants × 2 registered splits). Two-tick analysis is robustness, not another primary hypothesis family.

## E82-005 — Candidate versus significance
- Status: CONTROL.
- A statistically significant overnight/intraday difference is not equivalent to profitability. Candidate gate separately requires positive absolute net P&L in development and validation at one- and two-tick assumptions, for a defined-risk structure and fixed horizon.
