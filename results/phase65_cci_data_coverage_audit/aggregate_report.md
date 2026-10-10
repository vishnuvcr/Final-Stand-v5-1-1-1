# Phase 65 — CCI timestamp and contract-coverage audit

**Decision: diagnostic complete; no strategy promotion.**

- Pinned dataset revision: `3eacf762d401efd9a08e804592fa7882b354c4a2`
- Breakout event rows audited: **30**
- 2026 option data was not queried or downloaded; all event timestamps are bounded through 2025-12-31.
- No P&L was computed. Nearest timestamps are diagnostic only and are not treated as fills.

## Aggregate exact coverage

| variant        | split   |   events |   trigger_index_exact |   entry_index_exact |   option_file_found |   side_trigger_any |   side_entry_any |   events_with_strict_itm_trigger_contract |   median_nearest_side_offset_seconds |
|:---------------|:--------|---------:|----------------------:|--------------------:|--------------------:|-------------------:|-----------------:|------------------------------------------:|-------------------------------------:|
| CCI_BASE       | DEV     |       12 |                    12 |                   6 |                  12 |                  1 |                0 |                                         1 |                               864240 |
| CCI_BASE       | VAL     |       13 |                    13 |                  10 |                  13 |                  5 |                5 |                                         1 |                                  480 |
| CCI_EMA_FILTER | DEV     |        4 |                     4 |                   2 |                   4 |                  1 |                0 |                                         1 |                               643200 |
| CCI_EMA_FILTER | VAL     |        1 |                     1 |                   0 |                   1 |                  0 |                0 |                                         0 |                                  480 |

## Event status counts

- `no_strictly_itm_strike_observed_on_trigger_minute`: 15
- `entry_next_minute_missing_or_outside_window`: 12
- `missing_exact_next_minute_entry_option_bar`: 3

## Interpretation

This phase isolates timestamp and observed-contract coverage. If the exact next-minute bar is absent, it remains a missing observation; no interpolation, forward-fill, or proxy fill is allowed. Results do not establish whether the CCI strategy is profitable or unprofitable.
