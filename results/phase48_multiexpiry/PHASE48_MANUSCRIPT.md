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
  "validation_working_states": 1,
  "frozen_rows": 1,
  "holdout_confirmation_rows": 1,
  "holm_survivors": 0
}

## Validation working states

|   trades |   net |   net50 |   mean_net |   win_rate |   max_dd |   profit_factor | strategy                    | split      | state   |
|---------:|------:|--------:|-----------:|-----------:|---------:|----------------:|:----------------------------|:-----------|:--------|
|       30 | 10327 |    6786 |    344.233 |   0.533333 |   137156 |          1.0273 | covered_call_2_static_proxy | validation | LOW     |

## Validation inference

| strategy                    | state       |   n_active |   n_rest |   diff_mean |     ci_lo |        p |   p_holm |
|:----------------------------|:------------|-----------:|---------:|------------:|----------:|---------:|---------:|
| monthly_wide_range_static   | LOW         |          7 |        3 |    19817.2  | -19477.5  |   0.1412 |        1 |
| covered_call_2_static_proxy | LOW         |         30 |       21 |     5325.46 | -10856.5  |   0.2718 |        1 |
| double_calendar_straddle    | LOW         |          5 |        5 |     3467.93 |  -7455.12 |   0.302  |        1 |
| monthly_wide_range_static   | FALLING     |          3 |        7 |     7537.86 | -18795.6  |   0.3548 |        1 |
| covered_call_2_static_proxy | NORMAL      |         19 |       32 |    -3761.93 | -19665.1  |   0.6553 |        1 |
| covered_call_2_static_proxy | HIGH        |          2 |       49 |   -10895.8  | -63654.6  |   0.6855 |        1 |
| double_calendar_straddle    | NORMAL      |          5 |        5 |    -3467.93 | -10858.5  |   0.7111 |        1 |
| covered_call_2_static_proxy | FALLING     |          3 |       48 |   -14597.1  | -53644.2  |   0.7931 |        1 |
| monthly_wide_range_static   | NORMAL      |          3 |        7 |   -19817.2  | -53977.6  |   0.8684 |        1 |
| covered_call_2_static_proxy | SPIKE       |          1 |       50 |      nan    |    nan    | nan      |      nan |
| covered_call_2_static_proxy | RISING      |          1 |       50 |      nan    |    nan    | nan      |      nan |
| covered_call_2_static_proxy | HIGH_RISING |          1 |       50 |      nan    |    nan    | nan      |      nan |
| double_calendar_straddle    | HIGH        |          0 |       10 |      nan    |    nan    | nan      |      nan |
| double_calendar_straddle    | SPIKE       |          0 |       10 |      nan    |    nan    | nan      |      nan |
| double_calendar_straddle    | FALLING     |          0 |       10 |      nan    |    nan    | nan      |      nan |
| double_calendar_straddle    | RISING      |          0 |       10 |      nan    |    nan    | nan      |      nan |
| double_calendar_straddle    | HIGH_RISING |          0 |       10 |      nan    |    nan    | nan      |      nan |
| monthly_wide_range_static   | HIGH        |          0 |       10 |      nan    |    nan    | nan      |      nan |
| monthly_wide_range_static   | SPIKE       |          0 |       10 |      nan    |    nan    | nan      |      nan |
| monthly_wide_range_static   | RISING      |          0 |       10 |      nan    |    nan    | nan      |      nan |
| monthly_wide_range_static   | HIGH_RISING |          0 |       10 |      nan    |    nan    | nan      |      nan |

## Holdout confirmation

| strategy                    | state   |   trades |    net |   net50 |   mean_net |   win_rate |   max_dd |   profit_factor |
|:----------------------------|:--------|---------:|-------:|--------:|-----------:|-----------:|---------:|----------------:|
| covered_call_2_static_proxy | LOW     |        6 | 2753.6 | 2113.77 |    458.933 |   0.333333 |  13053.5 |         1.04953 |

## Important limitation

This phase uses an independent dataset beginning in late 2024; it is supplementary and cannot overwrite the canonical 2021-2025 evidence.