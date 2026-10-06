# Phase 48 Manuscript — Independent Multi-Expiry VIX Strategy Bridge

## Abstract

Phase 48 independently evaluated three mechanically reconstructed strategies motivated by Phase-46 public-video/Profit Breakout discovery: Double Calendar Straddle, Monthly Wide-Range Hedge, and Covered Call 2.0 as an option-only synthetic-future proxy. The purpose was to overcome the multi-expiry quote limitation found in Phase 47 while retaining the complete VIX panel: ALL, LOW, NORMAL, FALLING, RISING, HIGH, SPIKE and HIGH_RISING. An independent NIFTY intraday options source covering October 2024 through July 2026 was bridged to the project's canonical NIFTY spot series for point-in-time strike selection. After timestamp, schema, spot-field and historical lot-size audits, 124 trade observations were accepted. One validation working candidate emerged: Covered Call 2.0 proxy in LOW VIX (30 validation trades, +₹10,327 net; +₹6,786 under +50% monetary fee/charge stress). The 2026 protected confirmation remained positive (+₹2,754; +₹2,114 stressed, 6 trades). However, the validation active-vs-rest effect had a bootstrap 95% CI crossing zero, permutation p=0.2718, and Holm-adjusted p=1.0. No strategy survived the full promotion gate. Phase 48 therefore produces a promising diagnostic signal but no validated trading strategy and does not alter the canonical Phase-20/42 strategy.

## Research question

Can an independent historical NIFTY intraday source with multiple expiries visible on the same trade date provide reliable evidence for VIX-conditioned multi-expiry strategies discovered from public sources, while maintaining realistic costs, point-in-time information, validation-only selection and a protected 2026 holdout?

## Aims and objectives

1. Test three preregistered source-derived multi-expiry baselines.
2. Preserve LOW/NORMAL/FALLING regimes as active research states while also testing RISING/HIGH/SPIKE/HIGH_RISING.
3. Apply realistic Paytm Money-style brokerage and Indian statutory charges plus adverse option-tick slippage.
4. Audit timestamp, data schema, spot selection, historical lot size, duplicates and split integrity before accepting evidence.
5. Apply validation-only candidate freezing, protected 2026 confirmation and Holm multiple-testing correction.

## Data and methodology

### Independent option data

The bridge used the public Hugging Face NIFTY intraday options dataset for 2024, 2025 and 2026. The source contains timestamp, date, expiry, strike, option type, close, OI and volume fields. Its raw timestamps were UTC-naive representations of an Indian market session; they were normalized by +05:30 before the registered 10:00 IST entry and <=15:29 IST expiry exit rules.

### Spot series

The independent option source has no NIFTY spot-price field. Point-in-time NIFTY spot was therefore obtained from the project's canonical 1-minute NIFTY index series at the exact entry timestamp. No option prices, strikes or expiries were substituted from this series.

### Registered strategies

**B1 Double Calendar Straddle:** sell current-month ATM CE and PE and buy next-month ATM-equivalent CE and PE at four trading sessions before current monthly expiry; exit at the latest complete <=15:29 IST observation on expiry.

**B2 Monthly Wide-Range Hedge:** after the prior monthly expiry, sell current-month call and put nearest 0.30 absolute Black-Scholes delta using prior-only India VIX as sigma proxy; buy next-month call and put at the strike minimizing call-put premium gap near spot; exit on current-month expiry.

**B3 Covered Call 2.0 static proxy:** use an option-only synthetic long-future representation, plus a 0.30-delta protective put and current/next-week call sales near 0.30 delta. This is explicitly a proxy because the source strategy contains a true futures leg and active adjustments.

### Execution costs

Each leg uses historical NIFTY lot size, ₹10 F&O brokerage per order, date-aware STT/exchange/SEBI/IPFT/stamp/GST treatment and adverse ₹0.05 option-price slippage at entry and exit. The +50% stress multiplies monetary brokerage/statutory charge components; the adverse tick remains fixed.

### Historical lot-size audit

The superseded Phase-48 run incorrectly used a 50-lot value for late-2024 contracts. NSE's 2024 circulars specify the revised NIFTY 25-lot schedule and the later 75-lot transition, with the last old-lot weekly expiry on 19-Dec-2024, first revised weekly expiry on 02-Jan-2025, last old-lot monthly expiry on 30-Jan-2025, and first revised monthly expiry on 27-Feb-2025. The engine was corrected and the prior numerical result was rejected before the final evidence set.

## Results

| Registered baseline / state | Validation trades | Validation net | +50% charge stress | Win rate | Profit factor | Max DD | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| Covered Call 2.0 proxy / LOW | 30 | ₹10,327 | ₹6,786 | 53.3% | 1.03 | ₹137,156 | Working diagnostic only |
| Covered Call 2.0 proxy / NORMAL | 19 | −₹79,971 | −₹82,396 | 57.9% | 0.64 | ₹136,813 | Reject |
| Double Calendar / LOW | 5 | −₹159,296 | −₹159,810 | 0.0% | 0.00 | ₹129,406 | Reject |
| Double Calendar / NORMAL | 5 | −₹176,636 | −₹177,294 | 0.0% | 0.00 | ₹161,892 | Reject |
| Monthly Wide-Range / LOW | 7 | −₹115,302 | −₹116,162 | 14.3% | 0.03 | ₹97,617 | Reject |
| Monthly Wide-Range / NORMAL | 3 | −₹108,867 | −₹109,268 | 33.3% | 0.04 | ₹113,730 | Reject |

### Validation inference for the only working candidate

The LOW-VIX Covered Call 2.0 proxy had 30 active trades versus 21 complementary trades. Mean active-vs-rest difference was +₹5,325. The bootstrap 95% CI was −₹10,857 to +₹5,325 and the one-sided permutation p-value was 0.2718. The Holm-adjusted p-value across the complete tested strategy×VIX family was 1.0.

### Protected 2026 confirmation

The validation-frozen LOW-VIX Covered Call 2.0 proxy remained positive on six 2026 observations: +₹2,754 net and +₹2,114 at +50% charge stress. Win rate was only 33.3%, with PF 1.05 and maximum drawdown ₹13,053. This is confirmation of the point estimate, not statistical validation.

## Discussion

Phase 48 successfully fixed the data-availability problem identified in Phase 47: the independent source exposes multiple expiries on the same Indian trading dates. The self-audits were material. Without timestamp normalization, every 10:00 entry was missed. Without an independent spot bridge, ATM and delta selection would have been impossible. Without the lot-size audit, late-2024 development P&L would have been overstated. The corrected run changes the numerical development results substantially while leaving the validation/holdout conclusion essentially unchanged.

The LOW-VIX Covered Call 2.0 proxy is the only source-derived baseline with a positive validation result and a positive 2026 confirmation. However, the result is economically weak relative to its very large drawdown and is not statistically distinguishable from the complement. The source implementation is also not reproduced exactly because the available bridge lacks the true futures leg and active adjustment system. This prevents interpreting the result as evidence that the original strategy itself is profitable.

The Phase-48 results therefore support a narrower inference: **there is a low-VIX hypothesis worth further investigation, not a validated trading edge.**

## Strengths

- Independent data source used to challenge the earlier expiry-centric source limitation.
- Full eight-state VIX panel preserved rather than restricting analysis to high VIX.
- Point-in-time timestamp and spot selection with no forward filling of option quotes.
- Realistic brokerage, statutory charges and adverse slippage included.
- Validation-only freezing and protected 2026 confirmation maintained.
- Multiple-testing correction applied across the complete strategy×VIX inference family.
- Numerical runs that contained implementation defects were explicitly rejected before final evidence acceptance.

## Limitations

- Development begins only in October 2024, so the out-of-sample history is short.
- The independent option dataset has no direct NIFTY spot column; the point-in-time spot is bridged from another project dataset.
- Covered Call 2.0 is an option-only synthetic-future proxy and omits the source's exact futures mark and dynamic adjustments.
- High/RISING/SPIKE/HIGH_RISING validation coverage is sparse for these baselines; absence of significance is partly a sample-size limitation.
- The public-video mechanism is hypothesis-generating and not independent performance evidence.

## Conclusion

Phase 48 is **closed with NO PROMOTION**. The only working validation candidate was the LOW-VIX Covered Call 2.0 option-only proxy, with positive validation and 2026 point estimates, but it failed statistical significance, Holm correction and economic robustness criteria. The canonical Phase-20/42 strategy remains unchanged.

## Future research

The next scientifically justified study is a separate preregistered Phase 49 focused narrowly on the LOW-VIX Covered Call 2.0 mechanism: exact historical NIFTY futures plus options, the documented active adjustment rules, a longer independent development history, and a fresh untouched holdout. No live deployment should be based on Phase 48 alone.

## Appendix A — self-audit chronology

F48-001 schema normalization; F48-002 broader multi-expiry feasibility audit; F48-003 zero-trade diagnostic; F48-004 raw timestamp probe; F48-005 UTC-to-IST timestamp correction; F48-006 DuckDB interval syntax correction; F48-007 missing spot-field bridge; F48-008 historical lot-size correction. Only the post-F48-008 numerical run is treated as final Phase-48 evidence.

## Appendix B — machine-readable outputs

- `results/phase48_multiexpiry/final_decision.json`
- `results/phase48_multiexpiry/trade_matrix.csv`
- `results/phase48_multiexpiry/strategy_vix_summary.csv`
- `results/phase48_multiexpiry/validation_inference.csv`
- `results/phase48_multiexpiry/validation_working_candidates.csv`
- `results/phase48_multiexpiry/validation_freeze.csv`
- `results/phase48_multiexpiry/holdout_confirmation.csv`
- `results/phase48_multiexpiry/data_audit.json`