# Phase 103 — Novel Intraday Strategy Discovery Results

Audit status: PASS
Promotion decision: NO STRATEGY PROMOTED
Source revision: 3eacf762d401efd9a08e804592fa7882b354c4a2 (CC-BY-NC-4.0)
Sample: 2024 development / 2025 validation; 2026 options excluded.

## 2025 validation results

        strategy  completed_trades  execution_coverage_pct  net_completed_trades_rupees  stress_net_completed_trades_rupees  severe_stress_net_completed_trades_rupees  mean_daily_net_ci95_low  mean_daily_net_ci95_high  holm_adjusted_p_validation  max_drawdown_daily_pnl_rupees  candidate_eligible_for_independent_followup
  S103-A_XAC_ORB               126                   100.0                -10466.802233                       -25662.157474                              -37872.659878               -97.458565                 20.845419                         1.0                   10590.903496                                        False
      S103-B_FBR               114                   100.0                 -6676.294345                       -20515.676592                              -32070.677770               -82.442531                 33.699328                         1.0                    8704.077599                                        False
S103-C_RC_VIX_IC                89                   100.0                 -7422.302659                       -27962.092493                              -35613.217215               -92.848067                 28.540251                         1.0                   12509.528437                                        False

All results are fixed-one-lot rupee P&L sums, not compounded account returns. The decision statistic is mean net rupees per eligible session, including zero outcomes on sessions with no signal. A missing exit leaves that session non-estimable and disables inference rather than fabricating a price.

## Development results

        strategy       split  eligible_sessions  signal_opportunities  completed_trades  entry_or_strike_gaps  exit_gaps  execution_coverage_pct  net_completed_trades_rupees  stress_net_completed_trades_rupees  severe_stress_net_completed_trades_rupees  mean_net_per_completed_trade  median_net_per_completed_trade  win_rate  profit_factor  max_drawdown_daily_pnl_rupees                  bootstrap_status  mean_daily_net_rupees  mean_daily_net_ci95_low  mean_daily_net_ci95_high  p_one_sided  holm_adjusted_p_validation  candidate_eligible_for_independent_followup promotion_decision
  S103-A_XAC_ORB development                246                   126               126                     0          0                   100.0                -12186.185782                       -25605.909555                              -34974.566679                    -96.715760                     -112.779951  0.111111       0.375773                   12474.968753 COMPUTED_CIRCULAR_BLOCK_BOOTSTRAP             -49.537341               -75.332150                -20.683469     1.000000                         NaN                                        False       NOT_PROMOTED
      S103-B_FBR development                246                   138               138                     0          0                   100.0                -11333.391867                       -26171.896337                              -36890.938923                    -82.126028                     -139.177645  0.282609       0.486685                   11333.391867 COMPUTED_CIRCULAR_BLOCK_BOOTSTRAP             -46.070699               -74.557369                -18.366374     0.999000                         NaN                                        False       NOT_PROMOTED
S103-C_RC_VIX_IC development                246                    82                82                     0          0                   100.0                 -5132.594791                       -22086.496754                              -27673.880662                    -62.592619                      -67.793878  0.390244       0.564434                    7872.259153 COMPUTED_CIRCULAR_BLOCK_BOOTSTRAP             -20.864206               -44.801389                  3.205053     0.958008                         NaN                                        False       NOT_PROMOTED

## Coverage and execution audit

- Signals: 675; completed trades: 675; blocked exits: 0.
- Option file load failures: 0; eligible sessions: 493.
- Entries use first complete observed option OPEN after signal within five minutes. Exits use first complete observed option OPEN after exit decision within the deadline. No interpolation or forward fill.
- Each signal has a corresponding coverage-audit row; unfilled opportunities remain explicit.

## Feature/source availability audit


{
  "option_source": {
    "repo_id": "thetrademarkk/india-index-options-1m",
    "revision": "3eacf762d401efd9a08e804592fa7882b354c4a2",
    "license": "CC-BY-NC-4.0"
  },
  "trade_window": "2024-01-01 through 2025-12-31",
  "session_days": 497,
  "prior_session_global_daily": {
    "available": true,
    "rows": 523,
    "covered_days": 523,
    "coverage_pct": 105.23138832997988,
    "columns": [
      "SP500",
      "NASDAQ",
      "DOW",
      "VIX",
      "NIKKEI",
      "SENSEX",
      "USDINR",
      "GOLD",
      "CRUDE",
      "SP500_ret1",
      "NASDAQ_ret1",
      "DOW_ret1",
      "VIX_ret1",
      "NIKKEI_ret1",
      "SENSEX_ret1",
      "USDINR_ret1",
      "GOLD_ret1",
      "CRUDE_ret1"
    ]
  },
  "prior_publication_fii_dii": {
    "available": true,
    "rows": 0,
    "covered_days": 0,
    "coverage_pct": 0.0,
    "columns": [
      "fii_net",
      "dii_net",
      "fii_idx_fut_net",
      "fii_idx_call_net",
      "fii_idx_put_net",
      "flow_pcr",
      "flow_sentiment",
      "fii_net_z20",
      "dii_net_z20",
      "fii_idx_fut_net_z20",
      "fii_idx_call_net_z20",
      "fii_idx_put_net_z20"
    ]
  },
  "prior_publication_news_sentiment": {
    "available": true,
    "rows": 330,
    "covered_days": 330,
    "coverage_pct": 66.39839034205231,
    "columns": [
      "sent_mean",
      "sent_std",
      "sent_count",
      "sent_pos",
      "sent_neg"
    ]
  },
  "india_vix_rows_2024_2025": 491,
  "excluded_modalities": [
    "FII/DII and sentiment were audited but not used in triggers because the existing validation feature manifest shows major FII/DII missingness and point-in-time sentiment timestamps are not independently qualified.",
    "No option Greeks, futures basis, historical bid/ask/depth, or single-stock corporate actions are fabricated."
  ],
  "eligible_option_expiry_file_count": 104,
  "latest_option_expiry_available": "2025-12-30",
  "latest_underlying_timestamp": "2025-12-31 15:59:00+05:30"
}

FII/DII and sentiment were checked but not used as triggers because their point-in-time availability is not sufficiently qualified. Global return and India VIX features are strictly lagged by at least one session.

## Frozen hypotheses

S103-A: opening-range breakout with prior-session cross-market breadth confirmation; one 100-point debit vertical.
S103-B: first opening-range breakout reversed only after a later closing-price reclaim within five bars; one 100-point debit vertical.
S103-C: 09:15–09:59 range compression below its previous-20-session median plus prior-session low-VIX gate; 100-point-wide iron condor with short strikes 100 points from ATM and wings 200 points from ATM.

## Cost, risk and inference

Base: one adverse ₹0.05 tick per leg fill, ₹10/order and date-effective statutory/exchange levies/GST. Stress: two ticks, ₹20/order and +50% charges. Severe stress: one tick plus 0.25% adverse impact per fill, ₹20/order, +50% charges and ₹50 per round trip.
Daily outcomes are bootstrapped in circular five-session blocks with 5,000 resamples. Holm correction covers exactly the three registered candidates. Follow-up eligibility requires ≥30 2025 trades, ≥95% filled signals, no exits missing, positive base and both stresses, 95% CI lower bound above zero, Holm p<0.05 and drawdown ≤₹60,000.

## Limitations

Minute OHLC is not executable bid/ask/depth. Costs follow the repo assumptions rather than independently verified Paytm Money contract notes. The dataset's CC-BY-NC license does not clear commercial use. FII/DII and news sentiment are only source-audited; Greeks, futures basis and depth were not invented. No 2026 options were loaded. Drawdown is cumulative daily P&L, not mark-to-market equity drawdown.

## Artifacts

trades.csv: completed and blocked attempts.
daily_pnl.csv: daily net, stress and severe stress by strategy/session.
coverage_audit.csv: signal statuses.
session_exclusions.csv and source_load_errors.csv: explicit source gaps.
summary.csv, feature_coverage.json, validation.json and comparison.svg: aggregate outcomes.
