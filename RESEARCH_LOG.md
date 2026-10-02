# Research Log

## 2026-10-02 — Phase 1 specification review
- Inspected the existing Phase 1 branch and prior research artifacts.
- Confirmed the intended selector is the maximum X across all 20 candidates: n=6..15 × Call/Put.
- Corrected the specification to remove an earlier, unintended stop-loss research phase.
- Locked the primary exit rules to: 90% of initial credit, otherwise 0 DTE/expiry.
- Locked the credit calculation to X × actual lot quantity.
- Preserved a separate gross-vs-net accounting layer for costs and slippage.
- n=15 requires OTM17 data.

## 2026-10-02 — Phase 1 status
- Strategy definition: COMPLETE after correction.
- Data validation: IN PROGRESS.
- Phase 2 implementation: NOT STARTED on its dedicated branch.

## 2026-10-02 — stop-loss experiment initialized
- Candidate stop losses: 0.25x, 0.50x, 0.75x, 1.00x, 1.50x, and 2.00x of the positive entry flatline premium.
- Each candidate exits on the first minute where either the 90%-flatline target or the candidate loss threshold is reached; otherwise expiry close.
- Paytm brokerage parameter changed to ₹20 per executed order for the primary run, consistent with Paytm Money's published new-user rate; older-account rates can be tested through the environment parameter.

## 2026-10-02 — initial stop-loss result
- Primary sample: 122 trades from 2024-01-01 through 2025-12-31.
- Baseline with 90%-flatline target and modeled costs: overall mean approximately -11.23 option points/trade; win rate approximately 42.6%.
- Call selections: 23 trades, mean -14.57 points. Put selections: 99 trades, mean -10.45 points.
- Stop-loss grid results: 0.25x mean -9.15; 0.50x -12.47; 0.75x -12.29; 1.00x -11.86; 1.50x -12.21; 2.00x -11.22 option points/trade.
- The 0.25x candidate has the smallest average loss in this in-sample grid, but its stop-out rate is about 82%; it is not considered validated.
- Next research phase: chronological holdout validation, bid/ask/liquidity stress, DTE/entry/strike sensitivity, and regime analysis.
