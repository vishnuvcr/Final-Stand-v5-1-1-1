# Phase 106 Error and Limitation Log

## Registered limitations

- The later calendar window does not guarantee statistical independence.
- Daily OHLC bars do not contain historical bid/ask, depth, queue, latency, partial-fill or market-impact evidence.
- Slippage values are scenarios, not observed spread estimates.
- Account-specific Paytm Money brokerage and contract notes remain unverified.
- Source/schema/accounting gate failures block strategy interpretation; dates must not be substituted and records must not be interpolated.

## Runtime and gate log

Automated results are recorded in `results/phase106/` and the GitHub Actions run linked from the repository.