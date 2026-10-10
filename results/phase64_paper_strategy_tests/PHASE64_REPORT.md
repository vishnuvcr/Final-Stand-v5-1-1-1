# Phase 64 — Paper-derived CCI NIFTY options strategy test

**Decision: RESEARCH ONLY / NO PROMOTION.** A successful numerical run does not itself establish a tradable edge.

## Research question
Does the published daily CCI breakout rule on monthly NIFTY in-the-money long options produce net-positive performance in the available modern sample, and does a fixed EMA(50)/EMA(200) trend filter improve it?

## Data and chronology
- Dataset: thetrademarkk/india-index-options-1m, revision 3eacf762d401efd9a08e804592fa7882b354c4a2; published license CC-BY-NC-4.0. Raw option data is not included in this artifact.
- Index data SHA-256: cf084ae28f3fe2d270c8cd0cdf4c1278790d4e9752529149972b9a72a6b52a49; size 8,243,696 bytes.
- Monthly-expiry proxy files loaded: 56; underlying minute rows: 436424.
- Latest underlying timestamp actually used: 2025-12-31 15:59:00+05:30. 2026 option files downloaded: 0.
- Development period: 2021-05-27 to 2023-12-31. Validation period: 2024-01-01 to 2025-12-31. The 2026 holdout is excluded from outcomes, feature calculation, parameter selection, and statistical tests.
- The source paper's original 2008–2018 period is outside the selected dataset. This is an independent modern-sample rule test, not a direct historical replication.

## Frozen candidate definitions
1. **CCI_BASE:** daily CCI(20) crosses above -100 for calls or below +100 for puts. Signal day must be on calendar day 3–15. A later minute close must break the signal day's high/low. Entry is at the next exact observed minute's option close using the nearest strictly ITM strike.
2. **CCI_EMA_FILTER:** identical rules, but calls additionally require signal-day close > EMA50 > EMA200 and puts require close < EMA50 < EMA200. This is a new fixed hypothesis, not a direct reproduction of the moving-average article.
- At most one entry per monthly-expiry proxy; earliest breakout wins; simultaneous call/put triggers are excluded as ambiguous.
- CCI signal becomes known only at signal-day close. No same-day breakout, same-bar fill, interpolation, or forward-fill is allowed.
- Target: option close at least 2× entry; stop: option close at or below 0.5× entry; exit at next exact minute after the target/stop trigger or at a reliable close on the last trading session before expiry.

## Results by split
| Variant | Split | Expiry files | Signal months | Breakout triggers | Completed trades | Trigger coverage | Win rate | Net ₹10/order | Net ₹10 +50% | Net ₹20/order | Net ₹20 +50% | Net 10% price-slip |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CCI_BASE | DEV | 32 | 21 | 12 | 0 | 0.00 | NA | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| CCI_BASE | VAL | 24 | 21 | 13 | 0 | 0.00 | NA | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| CCI_EMA_FILTER | DEV | 32 | 4 | 4 | 0 | 0.00 | NA | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| CCI_EMA_FILTER | VAL | 24 | 3 | 1 | 0 | 0.00 | NA | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

## Descriptive risk and trade statistics
| Variant | Split | Mean net/trade | Median net/trade | Profit factor | Max trade-P&L drawdown | Median holding (minutes) |
|---|---|---:|---:|---:|---:|---:|
| CCI_BASE | DEV | NA | NA | NA | 0.00 | NA |
| CCI_BASE | VAL | NA | NA | NA | 0.00 | NA |
| CCI_EMA_FILTER | DEV | NA | NA | NA | 0.00 | NA |
| CCI_EMA_FILTER | VAL | NA | NA | NA | 0.00 | NA |

## Statistical inference
Only the two frozen variants form the candidate family. For validation, a three-month moving-block bootstrap CI for mean net per trade and a block sign-flip test are attempted only with at least 20 completed trades. Holm correction is applied across computable validation p-values. Underpowered samples report SKIPPED rather than a fabricated p-value.

| Variant | Validation trades | Inference status | Mean net/trade | 95% block CI | Two-sided p | Holm p |
|---|---:|---|---:|---|---:|---:|
| CCI_BASE | 0 | SKIPPED_LT20_TRADES | NA | NA | NA | NA |
| CCI_EMA_FILTER | 0 | SKIPPED_LT20_TRADES | NA | NA | NA | NA |

## Opportunity and data-quality audit
See opportunity_audit.csv for monthly expiry, signal counts, breakout status, and exact failure reason. Coverage is completed trades divided by monthly expiries with a breakout trigger. No-strike, missing-entry, target/stop-without-next-minute-fill, and missing terminal close cases are not imputed.

Audit counts: CCI_BASE / entry_next_minute_missing_or_outside_window: 9; CCI_BASE / missing_exact_next_minute_entry_option_bar: 2; CCI_BASE / no_qualified_cci_signal: 14; CCI_BASE / no_strictly_itm_strike_observed_on_trigger_minute: 14; CCI_BASE / signal_without_later_breakout: 17; CCI_EMA_FILTER / entry_next_minute_missing_or_outside_window: 3; CCI_EMA_FILTER / missing_exact_next_minute_entry_option_bar: 1; CCI_EMA_FILTER / no_qualified_cci_signal: 49; CCI_EMA_FILTER / no_strictly_itm_strike_observed_on_trigger_minute: 1; CCI_EMA_FILTER / signal_without_later_breakout: 2.

## Execution-cost specification
- Primary execution uses observed option close plus one adverse ₹0.05 tick for entry and minus one tick for exit. Existing Phase-43 historical lot size and date-aware statutory cost helper is reused.
- ₹20/order adds ₹10 per order to the accepted ₹10/order base scenario. In +50% stress, the ₹10 brokerage becomes ₹15 per order and the ₹20 brokerage becomes ₹30 per order; other monetary fees/charges are also stressed 1.5×.
- Separate paper-comparability stress applies 10% adverse option-price slippage: entry price ×1.10 and exit price ×0.90, then recomputes charges. This is a sensitivity and does not replace the one-tick primary model.
- Input is OHLC, not historical bid/ask/depth. These are OHLC-close proxy returns, not guaranteed or quote-faithful fills.

## Interpretation
Shaha (2019) reports ₹145,362 net, a 63.25% win rate and 232.16% average annual ROI for 68 trades. However, the supplied paper's chi-square table labels the total as 80 despite the body and 43 wins + 25 losses implying 68. Its two-sample test of mean winning trade versus mean loss magnitude does not directly test positive strategy expectancy. We do not import those outcomes as expected returns.
The original study's 2008–2018 data are unavailable here. The selected modern source starts in 2021, has incomplete observations in less liquid options, and its CC-BY-NC-4.0 non-commercial license applies. The monthly expiry date is proxied by a late-month option file, not independently proven from exchange calendars.

## Strengths
- Directly specified CCI rule and one separately frozen EMA adaptation; no parameter grid.
- Fixed dataset revision, SHA-256 file manifest, timezone normalization, duplicate/conflict checks, no-look-ahead and exact next-minute fill gates.
- Separate DEV and VAL reporting; 2026 excluded.
- Primary and stressed ₹10/₹20 costs, adverse tick slippage and separate 10% price-slippage stress.

## Limitations
- No direct replication of 2008–2018 data; only the available 2021–2025 interval is tested.
- Monthly expiry file is a proxy and incomplete source coverage can omit a month.
- OHLC does not contain bid/ask/depth, so execution realism remains limited.
- One trade maximum per expiry makes the validation sample potentially small; fewer than 20 trades or <95% trigger coverage means insufficient evidence.
- CCI+EMA is a new hypothesis and has not been supported by a prior options backtest.

## Conclusion
Phase 64 is research-only. Inspect the summary table and machine-readable decisions: positive point-estimate P&L is not confirmation. No live strategy is promoted from this phase. If the validation trade-count, coverage, all-cost and Holm-adjusted statistical gates fail, the correct result is NO-GO / INSUFFICIENT EVIDENCE.

## Future research
1. Acquire authorized older, longer option data if a true replication of the 2008–2018 source paper is necessary.
2. If a frozen variant survives validation, pre-register a separate independent confirmation before opening a new holdout.
3. Only add option Greeks, OI, bid/ask/depth or ML features after the separate Phase-52 data-rights and exact-sample gates are met.

## Reproducibility files
- trade_ledger.csv — completed trade outcomes only.
- opportunity_audit.csv — monthly signals, breakouts and coverage failures.
- summary.csv, decision.json, source_manifest.json — aggregate output and lineage.
- validation_net_pnl.png and validation_equity.png — figures from this run.
