# Phase 100 Error / Limitation Log

## Known limitations at synthesis start
- Phase 95's source-claim reconciliation had failed due to a malformed manifest suffix; a parser correction is under a fresh workflow run. The failed reconciliation output is not accepted.
- Phase 96 is an operationalized SMA/EMA index signal screen; paper-specific seasonality and timing/stop rules are not yet fully replicated.
- Phase 97 is data-blocked for exact-contract ML options training.
- Phase 98 is data-blocked for original-period CCI execution reconstruction.
- Phase 99 verifies payoff algebra with illustrative premiums; it is not a historical market P&L backtest.
- Historical Paytm Money charges, bid/ask/depth, slippage and latency remain mandatory for options profitability claims.

## Runtime errors
- None recorded at phase start. All synthesis/workflow failures must be logged with corrective actions and rerun outcome.
