# Phase 96 Signal-Level Replay

## Interpretation guardrail
These are operationalized SMA/EMA sensitivity variants, not exact reproductions where source parameters are unspecified. The underlying NIFTY spot index is not directly investable. The 0.05% turnover deduction is a sensitivity proxy, not verified Paytm Money costs. No option P&L is inferred.

Input observations: 4487; scored sessions per variant: 1486.

## Results

| strategy             |   sessions |   total_return |   annualized_volatility |   sharpe_rf0 |   max_drawdown |   hit_rate |
|:---------------------|-----------:|---------------:|------------------------:|-------------:|---------------:|-----------:|
| SMA_5_20_net_proxy   |       1486 |       0.525229 |                0.109535 |     0.708611 |      -0.144342 |   0.34253  |
| buy_hold             |       1486 |       1.14732  |                0.180882 |     0.808057 |      -0.384399 |   0.545087 |
| SMA_10_50_net_proxy  |       1486 |       1.0093   |                0.113966 |     1.09558  |      -0.144278 |   0.37214  |
| buy_hold             |       1486 |       1.14732  |                0.180882 |     0.808057 |      -0.384399 |   0.545087 |
| SMA_20_100_net_proxy |       1486 |       0.806464 |                0.117856 |     0.910102 |      -0.211032 |   0.403096 |
| buy_hold             |       1486 |       1.14732  |                0.180882 |     0.808057 |      -0.384399 |   0.545087 |
| EMA_5_20_net_proxy   |       1486 |       0.692929 |                0.110624 |     0.862717 |      -0.140548 |   0.362046 |
| buy_hold             |       1486 |       1.14732  |                0.180882 |     0.808057 |      -0.384399 |   0.545087 |
| EMA_10_50_net_proxy  |       1486 |       0.911547 |                0.114937 |     1.01371  |      -0.144173 |   0.396366 |
| buy_hold             |       1486 |       1.14732  |                0.180882 |     0.808057 |      -0.384399 |   0.545087 |
| EMA_20_100_net_proxy |       1486 |       0.904158 |                0.122271 |     0.954661 |      -0.174228 |   0.434724 |
| buy_hold             |       1486 |       1.14732  |                0.180882 |     0.808057 |      -0.384399 |   0.545087 |

## Limitations
No exact listed-option contract data are used. Month/seasonality and first-Thursday/stop-loss rules are not backtested unless the source register provides fully specified rules. A simple return replay is exploratory and has no significance claim.
