# Phase 52 — Legacy Factor-Selector Pilot

Status: exploratory selector screen only; no promotion.

- Legacy trade rows: 9,699; matched point-in-time rows: 6,617 (68.2%).
- Recognized risk-limited legacy strategies: 25.
- Development fit ends 2023-02-17; tuning starts 2023-02-24; 2024–25 validation and 2026 holdout were not used to fit the selected feature/mapping.
- Fixed baseline chosen on development: buy_call.

## Results

| Mode | Chosen feature | Split | N expiries | Net ₹ | Net +50% stress ₹ | Net +100% modelled stress ₹ | Mean uplift vs fixed ₹/expiry | 95% block-bootstrap CI | Raw one-sided p | Holm-adjusted p |
|---|---|---|---:|---:|---:|---:|---:|---|---:|
| GLOBAL_SENTIMENT_PROXY | global_NASDAQ_ret1 | development_in_sample | 102 | 186130 | 182021 | 177913 | 1080 | [-1431, 3753] | 0.2232 | nan |
| GLOBAL_SENTIMENT_PROXY | global_NASDAQ_ret1 | validation | 59 | -185057 | -187248 | -189440 | -797 | [-3384, 2064] | 0.6951 | 1.0000 |
| GLOBAL_SENTIMENT_PROXY | global_NASDAQ_ret1 | holdout | 0 | nan | nan | nan | nan | — | nan | nan |
| GREEKS_SURFACE_ROUTER | atm_pe_iv | development_in_sample | 102 | 119771 | 116639 | 113508 | 439 | [-810, 1687] | 0.2442 | nan |
| GREEKS_SURFACE_ROUTER | atm_pe_iv | validation | 59 | -168132 | -169753 | -171374 | -500 | [-2781, 1290] | 0.6229 | 1.0000 |
| GREEKS_SURFACE_ROUTER | atm_pe_iv | holdout | 0 | nan | nan | nan | nan | — | nan | nan |
| MULTI_FACTOR_ROUTER | TREND_X_IV_SKEW | development_in_sample | 102 | 288472 | 285640 | 282808 | 2096 | [-257, 4612] | 0.0258 | nan |
| MULTI_FACTOR_ROUTER | TREND_X_IV_SKEW | validation | 59 | -112260 | -113957 | -115654 | 446 | [-1740, 2637] | 0.3291 | 1.0000 |
| MULTI_FACTOR_ROUTER | TREND_X_IV_SKEW | holdout | 0 | nan | nan | nan | nan | — | nan | nan |
| OI_FLOW_ROUTER | near_atm_oi_pcr | development_in_sample | 102 | 234059 | 231256 | 228454 | 1563 | [-789, 4127] | 0.1382 | nan |
| OI_FLOW_ROUTER | near_atm_oi_pcr | validation | 59 | -173805 | -175142 | -176478 | -591 | [-2178, 814] | 0.7499 | 1.0000 |
| OI_FLOW_ROUTER | near_atm_oi_pcr | holdout | 0 | nan | nan | nan | nan | — | nan | nan |
| SPOT_PROXY_ONLY | nifty_ma_gap_15m | development_in_sample | 102 | 177269 | 174532 | 171794 | 1007 | [-971, 3106] | 0.1830 | nan |
| SPOT_PROXY_ONLY | nifty_ma_gap_15m | validation | 59 | -159796 | -161556 | -163315 | -361 | [-3363, 2520] | 0.5849 | 1.0000 |
| SPOT_PROXY_ONLY | nifty_ma_gap_15m | holdout | 0 | nan | nan | nan | nan | — | nan | nan |
| VIX_ROUTER | India_VIX_state | development_in_sample | 102 | 172758 | 170807 | 168856 | 970 | [-982, 3022] | 0.1630 | nan |
| VIX_ROUTER | India_VIX_state | validation | 59 | -55924 | -56997 | -58070 | 1411 | [-915, 4290] | 0.1642 | 0.9850 |
| VIX_ROUTER | India_VIX_state | holdout | 0 | nan | nan | nan | nan | — | nan | nan |

## Untested factor blocks

The audited legacy feature panel lacks synchronized NIFTY futures basis/OI/volume and exact-timestamp synthetic-future data. Those factors are not tested here. News, corporate actions and breadth are likewise unavailable. A daily sentiment feature is only a proxy and is not equivalent to timestamped news.

This run is a first out-of-sample selection screen over available frozen outcomes. It does not mean all 312 registered hypotheses or all finite parameter combinations have been replayed. No candidate is promoted from this pilot.
