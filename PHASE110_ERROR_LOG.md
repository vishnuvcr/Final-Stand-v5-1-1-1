# Phase 110 Error / Limitation Log

Append-only. Empty empirical-error state at initial registration; expected source limitations are recorded separately and are not mislabeled as run failures.

## 2026-10-23 — Initial source and design limitations

- **L110-01 — Meaning of “combined delta” is ambiguous.** A net signed portfolio delta and a sum of absolute leg deltas are not interchangeable. Mitigation: preregister both; do not quietly select one post hoc.
- **L110-02 — Modelled Greeks, not exchange Greeks.** Available one-minute OHLCV+OI does not provide historical executable quotes or the official exchange Greek tape. Mitigation: calculate Black–Scholes estimates from exact completed bars, freeze rate/dividend/expiry assumptions and label them as estimates.
- **L110-03 — OHLC is not bid/ask.** Minute-bar opens are execution references, not confirmed fills. Mitigation: test adverse slippage grid on every opened/covered leg, no same-bar close fills, disclose the residual uncertainty.
- **L110-04 — Source history is partial.** Current repository inventory shows the preferred dataset may end before the current date and may omit far strikes/expiry files. Mitigation: resolve revision SHA and exact coverage during execution, report exclusions, and do not extrapolate; next data work must test free supplements and Dhan if needed.
- **L110-05 — Non-commercial license.** Primary Hugging Face source is declared CC BY-NC 4.0. Mitigation: exploratory research only; no commercial or live-trading claim based on it.
- **L110-06 — Intraday Greek observations may be missing.** Exact-minute gaps mean a trigger could be missed. Mitigation: do not fill; mark incomplete campaigns as censored/excluded from paired comparison.
- **L110-07 — Multiple testing.** Thousands of thresholds/combinations can create apparent winners. Mitigation: register the finite grid, report the whole denominator, Holm-adjust validation p-values, reserve holdout and prohibit tuning against holdout.

## Actual code/workflow failures

None recorded at registration. New runtime, data, mathematical, test or persistence errors must be appended with the failing workflow run, root cause, corrective commit, retest and whether any prior metric was invalidated.