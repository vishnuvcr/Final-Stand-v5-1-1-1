# Exact-contract model-derived IV and Greeks audit

Status: **PASS**
Window: 2024-10-01 through 2026-10-08
Model: European Black-Scholes, flat r=6.5%, q=0%; only the UDiFF sample from 1 October 2024 onward is used for model features.

| Metric | Count |
|---|---:|
| UDiFF archive dates parsed | 501 |
| Positive-volume contract rows considered | 868,574 |
| Valid model IV/Greeks rows | 772,355 |
| Zero/invalid-volume rows excluded | 1,112,251 |
| Missing contract price/spot/expiry rows | 0 |
| Premium below model lower bound | 59,187 |
| Premium above model upper bound | 0 |
| Other solver/Greek failures | 37,032 |
| Near-minimum IV fits | 590 |
| Failed dates | 0 |
| Private model-feature cache bytes | 57,527,497 |

## Important modelling limits

These IV and Greeks are *model-estimated*, not exchange-published. Constant 6.5% interest and zero dividend yield are assumptions; future work must stress the rate, cross-check against Dhan's rolling ATM IV, reject implausible estimates, and assess sensitivity to stale EOD marks. Contracts with zero volume are excluded; positive volume does not prove an executable fill or bid/ask quality. The public report deliberately excludes contract-level premiums/Greeks; detailed records remain in the private Actions cache.
