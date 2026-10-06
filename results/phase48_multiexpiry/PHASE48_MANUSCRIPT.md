# Phase 48 Manuscript — Independent Multi-Expiry Data Bridge

## Summary

{
  "trade_rows": 124,
  "strategies": [
    "covered_call_2_static_proxy",
    "double_calendar_straddle",
    "monthly_wide_range_static"
  ],
  "data_errors": 0,
  "validation_working_states": 0,
  "frozen_rows": 0,
  "holdout_confirmation_rows": 0,
  "holm_survivors": 0
}

## Validation working states

| trades   | net   | net50   | mean_net   | win_rate   | max_dd   | profit_factor   | strategy   | split   | state   |
|----------|-------|---------|------------|------------|----------|-----------------|------------|---------|---------|

## Validation inference

| strategy                    | state       |   n_active |   n_rest |   diff_mean |     ci_lo |        p |   p_holm |
|:----------------------------|:------------|-----------:|---------:|------------:|----------:|---------:|---------:|
| monthly_wide_range_static   | LOW         |          7 |        3 |    8464.39  |  -7310.24 |   0.2078 |        1 |
| covered_call_2_static_proxy | LOW         |         30 |       21 |    5430.27  | -11449.6  |   0.2656 |        1 |
| covered_call_2_static_proxy | FALLING     |          3 |       48 |   11128.3   | -30909.4  |   0.2738 |        1 |
| double_calendar_straddle    | LOW         |          5 |        5 |    3417.84  |  -7496.1  |   0.3135 |        1 |
| covered_call_2_static_proxy | NORMAL      |         19 |       32 |    -443.963 | -17046.6  |   0.5139 |        1 |
| double_calendar_straddle    | NORMAL      |          5 |        5 |   -3417.84  | -10801.2  |   0.7008 |        1 |
| monthly_wide_range_static   | FALLING     |          3 |        7 |   -7133.17  | -23761.8  |   0.7662 |        1 |
| monthly_wide_range_static   | NORMAL      |          3 |        7 |   -8464.39  | -24757.3  |   0.8013 |        1 |
| covered_call_2_static_proxy | HIGH        |          2 |       49 |  -32154.5   | -42239.9  |   0.9359 |        1 |
| covered_call_2_static_proxy | SPIKE       |          1 |       50 |     nan     |    nan    | nan      |      nan |
| covered_call_2_static_proxy | RISING      |          1 |       50 |     nan     |    nan    | nan      |      nan |
| covered_call_2_static_proxy | HIGH_RISING |          1 |       50 |     nan     |    nan    | nan      |      nan |
| double_calendar_straddle    | HIGH        |          0 |       10 |     nan     |    nan    | nan      |      nan |
| double_calendar_straddle    | SPIKE       |          0 |       10 |     nan     |    nan    | nan      |      nan |
| double_calendar_straddle    | FALLING     |          0 |       10 |     nan     |    nan    | nan      |      nan |
| double_calendar_straddle    | RISING      |          0 |       10 |     nan     |    nan    | nan      |      nan |
| double_calendar_straddle    | HIGH_RISING |          0 |       10 |     nan     |    nan    | nan      |      nan |
| monthly_wide_range_static   | HIGH        |          0 |       10 |     nan     |    nan    | nan      |      nan |
| monthly_wide_range_static   | SPIKE       |          0 |       10 |     nan     |    nan    | nan      |      nan |
| monthly_wide_range_static   | RISING      |          0 |       10 |     nan     |    nan    | nan      |      nan |
| monthly_wide_range_static   | HIGH_RISING |          0 |       10 |     nan     |    nan    | nan      |      nan |

## Holdout confirmation

No frozen confirmations.

## Important limitation

This phase uses an independent dataset beginning in late 2024; it is supplementary and cannot overwrite the canonical 2021-2025 evidence.