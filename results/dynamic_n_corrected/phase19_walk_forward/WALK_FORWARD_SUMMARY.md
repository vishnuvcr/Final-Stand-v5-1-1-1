# Phase 19 Walk-Forward Stop Confirmation

Selected only on train data (through 2023-12-31): **mfe_cut_1330_mfe1_c1**

## Train
{'trades': 97, 'base_net': 60942.3150135, 'candidate_net': 66635.15598775, 'net_uplift': 5692.840974249992, 'winner_affected': 0, 'loss_reduction': 5692.840974249992, 'losses_eliminated': 0, 'base_dd': 21763.22981115, 'candidate_dd': 18958.6678896, 'stops': 2}

## Validation (2024-2025)
{'trades': 77, 'base_net': 73886.18577038003, 'candidate_net': 77085.76786037255, 'net_uplift': 3199.582089992509, 'winner_affected': 0, 'loss_reduction': 3819.2265506475014, 'losses_eliminated': 0, 'base_dd': 27321.078748147498, 'candidate_dd': 27336.11356767749, 'stops': 5}

## Holdout (2026-01-01 onward)
{'trades': 16, 'base_net': 4108.616860530492, 'candidate_net': 7191.077531638491, 'net_uplift': 3082.4606711079978, 'winner_affected': 0, 'loss_reduction': 17867.6878174405, 'losses_eliminated': 0, 'base_dd': 17890.35296654, 'candidate_dd': 22756.003463442, 'stops': 4}

## Full
{'trades': 190, 'base_net': 138937.11764441052, 'candidate_net': 150912.001379761, 'net_uplift': 11974.8837353505, 'winner_affected': 0, 'loss_reduction': 27379.755342337994, 'losses_eliminated': 0, 'base_dd': 27321.078748147498, 'candidate_dd': 27336.113567677487, 'stops': 11}

Promotion condition:
- zero baseline-positive trades affected in validation and holdout;
- positive net-P&L uplift in validation and holdout;
- no materially worse maximum drawdown;
- exact minute-level fees retained.
