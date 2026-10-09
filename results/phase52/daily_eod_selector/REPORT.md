# Phase 52 — Daily EOD Factor Selector (Exploratory)

**Status:** EOD_FACTOR_SELECTOR_VALIDATION_ONLY_NO_PROMOTION. No promotion.
- Events: 256; base matrix rows: 9699; matched base/EOD events: 256.
- Baseline strategy selected on development only: buy_call.
- Pinned option revision: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5; EOD archive commit: 0ef4988629d52ca4ca83853b5def1d157f5453d4.
- Feature thresholds and strategy mappings are fit only on development; the later development block tunes feature choices; 2024–25 is validation; 2026 is an untouched holdout only if each factor meets the coverage and 20-event gates.

## Validation and holdout results

| Mode | Split | Events | Feature coverage | Net ₹ | Net 1.5× all-cost stress ₹ | Net 2× extrapolated stress ₹ | Mean uplift vs fixed ₹/event | 95% paired CI | Holm p | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| EOD_CALL_OI_CHANGE | validation | 101 | 99.0% | -108,267 | -112,097 | -115,926 | -406 | [-3058, 1916] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_CALL_OI_CHANGE | holdout | 21 | 100.0% | -148,276 | -149,151 | -150,026 | -1,321 | [-7464, 4523] | nan | EXPLORATORY_NO_PROMOTION |
| EOD_FUTURES_BASIS | validation | 101 | 100.0% | 24,056 | 20,274 | 16,493 | 905 | [-1752, 3596] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_FUTURES_BASIS | holdout | 21 | 100.0% | -56,003 | -57,060 | -58,117 | 3,064 | [-6133, 11235] | nan | EXPLORATORY_NO_PROMOTION |
| EOD_FUTURES_OI_CHANGE | validation | 101 | 100.0% | -26,140 | -29,508 | -32,877 | 412 | [-2892, 3109] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_FUTURES_OI_CHANGE | holdout | 21 | 100.0% | -46,034 | -47,026 | -48,018 | 3,542 | [-3441, 10148] | nan | EXPLORATORY_NO_PROMOTION |
| EOD_OI_PCR | validation | 101 | 100.0% | -264,283 | -266,409 | -268,534 | -1,934 | [-5474, 1310] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_OI_PCR | holdout | 21 | 100.0% | 1,657 | 1,003 | 350 | 5,829 | [-3851, 16387] | nan | EXPLORATORY_NO_PROMOTION |
| EOD_OI_X_BASIS | validation | 101 | 100.0% | -103,095 | -106,493 | -109,891 | -350 | [-3543, 3252] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_OI_X_BASIS | holdout | 21 | 100.0% | -67,761 | -68,435 | -69,109 | 2,522 | [-4273, 11705] | nan | EXPLORATORY_NO_PROMOTION |
| EOD_PUT_OI_CHANGE | validation | 101 | 99.0% | 16,945 | 12,409 | 7,873 | 827 | [-3175, 4874] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_PUT_OI_CHANGE | holdout | 21 | 100.0% | -2,802 | -4,135 | -5,468 | 5,584 | [-7021, 18193] | nan | EXPLORATORY_NO_PROMOTION |
| EOD_VOLUME_PCR | validation | 101 | 100.0% | 25,968 | 22,090 | 18,211 | 923 | [-1454, 3436] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_VOLUME_PCR | holdout | 21 | 100.0% | -167,978 | -168,917 | -169,856 | -2,262 | [-10937, 4137] | nan | EXPLORATORY_NO_PROMOTION |
| EOD_VOLUME_X_BASIS | validation | 101 | 100.0% | 13,422 | 9,619 | 5,817 | 799 | [-2186, 4032] | 1.0000 | EXPLORATORY_NO_PROMOTION |
| EOD_VOLUME_X_BASIS | holdout | 21 | 100.0% | -181,947 | -182,872 | -183,798 | -2,927 | [-11216, 4446] | nan | EXPLORATORY_NO_PROMOTION |

## Factor availability

| Factor | Events | Non-null | Overall coverage | Development | Validation | Holdout |
|---|---:|---:|---:|---:|---:|---:|
| front_future_basis_bps | 256 | 256 | 100.0% | 100.0% | 100.0% | 100.0% |
| front_future_open_interest_change_pct_1d | 256 | 255 | 99.6% | 99.2% | 100.0% | 100.0% |
| option_call_oi_near_atm_change_pct_1d | 256 | 251 | 98.0% | 97.0% | 99.0% | 100.0% |
| option_oi_pcr_near_atm_5steps | 256 | 252 | 98.4% | 97.0% | 100.0% | 100.0% |
| option_put_oi_near_atm_change_pct_1d | 256 | 251 | 98.0% | 97.0% | 99.0% | 100.0% |
| option_volume_pcr_near_atm_5steps | 256 | 252 | 98.4% | 97.0% | 100.0% | 100.0% |

## Limitations

- Daily EOD features are strictly prior-session inputs and are not a substitute for synchronized intraday futures/option quotes.
- NSE data rights review remains mandatory; the legacy options data is CC BY-NC 4.0.
- No selector is promoted from this exploratory screen. It does not test all 9,379,584 registered configurations.
