# Phase 49 Literature Review — Parameter Optimization and Backtest Overfitting

## Data-snooping correction

Sullivan, Timmermann and White describe White's Reality Check bootstrap as a way to evaluate a trading-rule universe while explicitly accounting for data-snooping bias: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=160330

Hsu and Kuan examine trading strategies using White's Reality Check and Hansen's Superior Predictive Ability framework, illustrating why significance must be evaluated across the searched strategy universe rather than only the winning rule: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=821759

## Backtest overfitting

Bailey, Borwein, López de Prado and Zhu show that investment backtests can become overfit as the number of tested configurations increases, motivating the strict separation of tuning, validation and holdout in this phase: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253

The same authors demonstrate that high simulated performance can be produced by testing relatively many alternative configurations, reinforcing the need to favor broad parameter plateaus over isolated maxima: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659

## Phase-49 implication

Phase 49 therefore does not select the parameter combination with the largest single historical P&L. It requires forward-fold development consistency, stress profitability, trade-count support and neighborhood robustness before a single frozen parameter set is allowed into validation.