# Phase 110 — Greek Stop-Loss Screen

Generated: 2026-10-23T11:42:46.342608+00:00
Resolved dataset SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5
Status: **EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION**

## Coverage gate

- Observed expiry files: 267 (2021-05-27 through 2026-08-04).
- Weekly campaigns scheduled: 259; exact-path eligible: 130; excluded: 133.
- Exclusions: {"ENTRY_BAR_MISSING_INVALID_OR_DUPLICATE_CE": 8, "ENTRY_BAR_MISSING_INVALID_OR_DUPLICATE_PE": 7, "ENTRY_OPEN_HAS_NO_VALID_MODEL_IV_PE": 1, "INCOMPLETE_EXACT_SPOT_PATH": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_1": 5, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_16": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_18": 2, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_2": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_24": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_27": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_4": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_5": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_53": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_7": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_8": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_0_PUT_92": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_1085_PUT_626": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_10_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_1169_PUT_915": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_11_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_140_PUT_1333": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_15_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_1_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_1_PUT_1": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_1_PUT_8": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_237_PUT_411": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_245_PUT_168": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_268_PUT_268": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_269_PUT_268": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_27_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_29_PUT_65": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_2_PUT_0": 2, "INCOMPLETE_SELECTED_LEG_PATH_CALL_321_PUT_459": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_333_PUT_633": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_340_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_344_PUT_279": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_3_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_442_PUT_275": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_4_PUT_0": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_515_PUT_249": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_5_PUT_0": 3, "INCOMPLETE_SELECTED_LEG_PATH_CALL_644_PUT_552": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_689_PUT_1348": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_807_PUT_1125": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_89_PUT_251": 1, "INCOMPLETE_SELECTED_LEG_PATH_CALL_9_PUT_0": 1, "INVALID_GREEK_IV_CE_AT_09:15": 4, "INVALID_GREEK_IV_CE_AT_09:45": 1, "INVALID_GREEK_IV_CE_AT_09:47": 1, "INVALID_GREEK_IV_CE_AT_10:59": 1, "INVALID_GREEK_IV_CE_AT_11:38": 1, "INVALID_GREEK_IV_CE_AT_11:53": 1, "INVALID_GREEK_IV_CE_AT_13:06": 1, "INVALID_GREEK_IV_CE_AT_15:08": 1, "INVALID_GREEK_IV_PE_AT_09:15": 1, "INVALID_GREEK_IV_PE_AT_09:16": 1, "INVALID_GREEK_IV_PE_AT_09:37": 1, "INVALID_GREEK_IV_PE_AT_13:25": 1, "INVALID_GREEK_IV_PE_AT_13:33": 1, "INVALID_GREEK_IV_PE_AT_13:43": 1, "INVALID_GREEK_IV_PE_AT_13:57": 1, "INVALID_GREEK_IV_PE_AT_15:17": 1, "INVALID_TRADING_SESSION_SCHEDULE": 2, "MISSING_EXACT_0959_SPOT_OR_OPTION_BAR": 1, "NO_OBSERVED_SESSION_AFTER_PREVIOUS_EXPIRY": 4, "NO_VALID_0_15_DELTA_CE_WITH_PRE_ENTRY_OI": 20, "NO_VALID_0_15_DELTA_PE_WITH_PRE_ENTRY_OI": 18, "UNSUPPORTED_HISTORICAL_LOT_SIZE_DATE": 2}.

## Registered sweep and costs

- Rules registered including no-stop: 4294.
- Each rule is evaluated under 24 cost combinations for development and validation.
- Brokerage per executed order ₹10/₹15/₹20; per-unit adverse slippage ₹0/₹0.05/₹0.25/₹0.50 per leg per side; fee stress 1.0×/1.5×.
- Primary comparison case: ₹20/order, ₹0.25 slippage/unit/side, 1.0× fee model.
- The requested 0.40 threshold is tested both as absolute signed net position delta and as the sum of absolute leg deltas.

## Validation findings

- Rules with positive net validation P&L at primary costs: 3934.
- Rules with positive paired uplift versus no-stop: 170.
- Rules with Holm-adjusted one-sided p < 0.05 for paired uplift: 0.
- Each stop is paired with the same campaign's no-stop result. Validation ranks rules; the frozen shortlist is persisted before holdout summarization.

### Top validation rules by paired uplift (one lot, primary costs)

| Rule | Trades | Net P&L (₹) | Paired uplift (₹) | Max drawdown (₹) | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|
| DELTA=0.30 / GAMMA=0.50 / ALL | 41 | 57,625.55 | 10,928.15 | 3,478.54 | 1 |
| GAMMA=0.50 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / THETA=0.00 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / THETA=0.25 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / VEGA=0.40 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / VEGA=0.40 / THETA=0.00 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / VEGA=0.40 / THETA=0.25 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / VEGA=0.50 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / VEGA=0.50 / THETA=0.00 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |
| GAMMA=0.50 / VEGA=0.50 / THETA=0.25 / ANY | 41 | 57,217.80 | 10,520.40 | 3,478.54 | 1 |

## Frozen holdout (not used for selection)

| Rule | Trades | Net P&L (₹) | Paired uplift (₹) | Max drawdown (₹) |
|---|---:|---:|---:|
| GAMMA=0.50 / VEGA=0.40 / THETA=0.25 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| GAMMA=0.50 / VEGA=0.50 / THETA=0.25 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| GAMMA=0.50 / THETA=0.00 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| DELTA=1.00 / GAMMA=0.50 / VEGA=0.50 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| DELTA=1.00 / GAMMA=0.50 / VEGA=0.40 / THETA=0.00 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| GAMMA=0.50 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| DELTA=0.40 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| DELTA=1.00 / GAMMA=0.50 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| GAMMA=0.50 / THETA=0.25 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |
| DELTA=1.00 / GAMMA=0.50 / VEGA=0.40 / ANY | 1 | 5,987.49 | 0.00 | 0.00 |

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
