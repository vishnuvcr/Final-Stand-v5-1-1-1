# Phase 81 Status
Date: 2026-10-10
Status: CORRECTED EXPLORATORY SWEEP COMPLETE — NO STRATEGY PROMOTION.

## Registered sample and integrity
- [x] Corrected run passed and persisted: [GitHub Actions run 38044579698](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38044579698).
- [x] Pinned dataset revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5.
- [x] 238 expiry files loaded; 1,139 candidate sessions assigned; 22,326 paired-window trade rows; 11,163 matched date×variant differences.
- [x] 182 incomplete date/variant cases excluded; 0 file/schema errors.
- [x] 122,310 rows identical on open+volume were collapsed; 0 conflicting duplicate keys; 0 expiry/file-name mismatches; 0 invalid identity fields.
- [x] 2026 holdout option data was not loaded, scored or ranked.
- [x] Paytm Money ₹10/order assumption, date-aware modeled fees, ₹0.05 adverse tick and ₹0.10 two-tick stress are included.
- [x] The first run with coarse duplicate logic is superseded. The first corrected run's data computation succeeded but persistence conflicted; the subsequent corrected run persisted successfully.

## Descriptive result
- All nine defined-risk multi-leg variants have negative aggregate net P&L in both DEV and VAL under the registered one-tick and two-tick cost models.
- The unbounded short ATM straddle has positive aggregate net P&L in the intraday window but negative aggregate P&L in the overnight window. It is diagnostic-only, and these OHLC-open fills are not proof of executable returns.
- Across all ten variants, the average overnight-minus-intraday paired difference is negative in both DEV and VAL. Expiry-cluster inference and Holm adjustment are the next gate; the positive static intraday short-straddle diagnostic is not an eligible strategy candidate.
- No strategy has been promoted. Proceed to Phase 82 using only DEV/VAL; only consider opening the holdout after a preregistered candidate passes gates.
