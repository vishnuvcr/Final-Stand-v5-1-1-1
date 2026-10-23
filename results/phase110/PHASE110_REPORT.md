# Phase 110 — Greek Stop-Loss Screen

Generated: 2026-10-23T10:46:31.049166+00:00
Resolved dataset SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
Status: **BLOCKED_NO_VALID_CAMPAIGNS**

## Coverage gate

- Observed expiry files: 267 (2021-05-27 through 2026-08-04).
- Weekly campaigns scheduled: 259; exact-path eligible: 0; excluded: 263.
- Exclusions: {"DUPLICATE_SELECTION_CONTRACT_MINUTE": 134, "ENTRY_BAR_MISSING_INVALID_OR_DUPLICATE_CE": 5, "ENTRY_BAR_MISSING_INVALID_OR_DUPLICATE_PE": 4, "MISSING_EXACT_0959_SPOT_OR_OPTION_BAR": 1, "NO_OBSERVED_SESSION_AFTER_PREVIOUS_EXPIRY": 4, "NO_VALID_0_15_DELTA_CE_WITH_PRE_ENTRY_OI": 17, "NO_VALID_0_15_DELTA_PE_WITH_PRE_ENTRY_OI": 22, "UNEXPECTED_ENTRY_TO_EXIT_MINUTE_COUNT": 74, "UNSUPPORTED_HISTORICAL_LOT_SIZE_DATE": 2}.

## Registered sweep and costs

- Rules registered including no-stop: 4294.
- Each rule is evaluated under 24 cost combinations for development and validation.
- Brokerage per executed order ₹10/₹15/₹20; per-unit adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per leg per side; fee stress 1.0×/1.5×.
- Primary comparison case: ₹20/order, ₹0.25 slippage/unit/side, 1.0× fee model.
- The requested 0.40 threshold is tested both as absolute signed net position delta and as the sum of absolute leg deltas.

## Validation findings

- Rules with positive net validation P&L at primary costs: 0.
- Rules with positive paired uplift versus no-stop: 0.",
        f"- Rules with Holm-adjusted one-sided p < 0.05 for paired uplift: 0.
- Each stop is paired with the same campaign's no-stop result. Validation ranks rules; the frozen shortlist is persisted before holdout summarization.

### Top validation rules by paired uplift (one lot, primary costs)

| Rule | Trades | Net P&L (₹) | Paired uplift (₹) | Max drawdown (₹) | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|
| NO_STOP_REFERENCE | 0 | 0.00 | 0.00 | 0.00 | 1 |
| THETA=0.00 / ANY | 0 | 0.00 | 0.00 | 0.00 | 1 |
| THETA=0.25 / ANY | 0 | 0.00 | 0.00 | 0.00 | 1 |
| THETA=0.50 / ANY | 0 | 0.00 | 0.00 | 0.00 | 1 |
| THETA=0.75 / ANY | 0 | 0.00 | 0.00 | 0.00 | 1 |
| VEGA=0.10 / ANY | 0 | 0.00 | 0.00 | 0.00 | 1 |
| VEGA=0.10 / THETA=0.00 / ANY | 0 | 0.00 | 0.00 | 0.00 | 1 |
| VEGA=0.10 / THETA=0.00 / ALL | 0 | 0.00 | 0.00 | 0.00 | 1 |
| VEGA=0.10 / THETA=0.25 / ANY | 0 | 0.00 | 0.00 | 0.00 | 1 |
| VEGA=0.10 / THETA=0.25 / ALL | 0 | 0.00 | 0.00 | 0.00 | 1 |

## Frozen holdout (not used for selection)

| Rule | Trades | Net P&L (₹) | Paired uplift (₹) | Max drawdown (₹) |
|---|---:|---:|---:|
| VEGA=0.10 / THETA=0.25 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| VEGA=0.10 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| THETA=0.75 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| DELTA=0.40 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| VEGA=0.10 / THETA=0.75 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| THETA=0.50 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| VEGA=0.20 / THETA=0.00 / ALL | 0 | 0.00 | 0.00 | 0.00 |
| VEGA=0.20 / THETA=0.25 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| VEGA=0.10 / THETA=0.00 / ANY | 0 | 0.00 | 0.00 | 0.00 |
| VEGA=0.10 / THETA=0.50 / ANY | 0 | 0.00 | 0.00 | 0.00 |

## Decision

**No strategy is promoted from this screen.** Historical Greeks are Black–Scholes estimates, execution is a one-minute OHLC proxy, the dataset is CC BY-NC 4.0, and exact-path coverage can select a non-representative subset. The highest result from a multi-thousand-rule sweep is not sufficient evidence of executable profitability. Independent testing and the registered gates remain mandatory.

## Files

- summary.json: source and run provenance.
- coverage.json / source_files.csv / exclusions.csv: coverage and failure reasons.
- greek_stoploss_grid.csv.gz: complete development/validation rule sweep and 24 cost scenarios.
- validation_candidates.csv: validation rank, Holm correction and bootstrap intervals.
- shortlist_frozen.json: candidate list frozen before holdout output.
- holdout_shortlist.csv: holdout cost grid for the frozen candidates.
- holdout_primary_cost_summary.csv: primary cost comparison.
- trade_ledger_aggregates.csv: campaign-level outcomes without raw minute rows.
- results/phase110/figures/validation_top_rules.svg
- results/phase110/figures/delta040_slippage_sensitivity.svg

## References

- Dataset and license: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- Dhan expired-options docs: https://dhanhq.co/docs/v2/expired-options-data/
- Paytm Money F&O FAQ: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web
- NSE levies: https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
- NSE Circular FA73061: https://nsearchives.nseindia.com/content/circulars/FA73061.pdf
