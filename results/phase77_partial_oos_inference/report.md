# Phase 77 — Partial-OOS expiry-cluster inference audit

Decision: **AUDIT_PASS_DESCRIPTIVE_ONLY**

## Coverage and exclusions

Validated interval: 2026-04-21 through 2026-07-21. Missing expiry dates 2026-07-28 and 2026-08-04 are explicitly excluded; no synthetic data are used.

## Results

| Strategy | Trades | Expiry clusters | Net ₹10/order | Net +50% friction | Net ₹20/order | Net ₹20/order +50% | Bootstrap fraction total > 0, base | Bootstrap fraction total > 0, max friction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TT02 | 13 | 13 | ₹-1341.12 | ₹-2936.31 | ₹-3701.12 | ₹-6476.31 | 0.466 | 0.391 |
| TT04 | 62 | 13 | ₹13271.51 | ₹10287.26 | ₹10345.11 | ₹5897.66 | 0.722 | 0.605 |
| TT05 | 62 | 14 | ₹17098.15 | ₹14239.72 | ₹14171.75 | ₹9850.12 | 0.916 | 0.788 |

## Uncertainty

For each cost scenario, 10,000 expiry-cluster bootstrap replicates resample expiry clusters rather than individual trades. Percentile intervals are reported for total net P&L and mean net per trade in `summary.json`. With only 14 expiry clusters, these intervals are unstable and descriptive only.

## Audit and interpretation

Ledger reconciliation errors: 0.
No strategy is promoted. Positive bootstrap fractions do not mean the strategy has that probability of being profitable in the future. The data interval is short and excludes the two later missing expiries. All published net values retain the frozen Paytm Money cost/friction model; no new costs or execution assumptions were added.

## Errors

- None detected in count/net reconciliation.
