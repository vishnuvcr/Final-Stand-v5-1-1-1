# Phase 97 Error / Limitation Log

## Known source-data blockers
- Phase 85 previously recorded a no-go for a new execution-quality replay using then-verified free sources.
- Phase 89 established rolling ATM-relative option-field coverage on its sample; it did not establish broad exact-contract identity, historical bid/ask/depth, or credible fills.
- Without authorized point-in-time exact-contract features and labels, training RF/XGBoost/LSTM would not reproduce the paper and could create false confidence. Such training is prohibited.
- Historical Paytm Money fees and spread/slippage must be sourced or stress-tested; they must not be invented.

## Runtime errors
- None recorded at phase start. Append all CI/data-gate errors and their resolution here.

- 2026-10-10: Gate run 38072759556 completed successfully and wrote a bounded DATA_BLOCKED result. This is expected gate behaviour, not a runtime error. Model fitting remains blocked until eligible source data become available.
