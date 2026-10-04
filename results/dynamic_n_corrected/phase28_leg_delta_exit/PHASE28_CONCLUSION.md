# Phase 28 Individual-Leg Delta Research — Conclusion

NSE documents NIFTY index options as European-style CE/PE contracts. Individual-leg deltas were reconstructed minute-by-minute from observed option prices using European Black-Scholes implied volatility (r=0, q=0 baseline). Coverage: 99.21%.

Primary hypothesis: the two short legs, especially the nearer OTM-(n+1) short leg, may provide more useful exit information than net portfolio delta.

Training-selected profit rule: S1_profit_f0.90_d0.05
Training-selected adverse stop: NONE

Combined walk-forward:
- Training: {'trades': 97, 'base_net': np.float64(62905.98265855), 'candidate_net': np.float64(59907.81766712501), 'net_uplift': np.float64(-2998.164991425), 'winner_affected': 62, 'stops': 62, 'base_dd': 19799.562166100004, 'candidate_dd': 19942.724859250004, 'win_rate': 0.979381443298969}
- Validation: {'trades': 77, 'base_net': np.float64(75809.77917437506), 'candidate_net': np.float64(73322.7324562875), 'net_uplift': np.float64(-2487.046718087501), 'winner_affected': 30, 'stops': 30, 'base_dd': 27336.11356767749, 'candidate_dd': 27336.11356767749, 'win_rate': 0.935064935064935}
- Holdout: {'trades': 16, 'base_net': np.float64(10413.76472349899), 'candidate_net': np.float64(10377.85269277949), 'net_uplift': np.float64(-35.91203071950201), 'winner_affected': 1, 'stops': 1, 'base_dd': 17890.35296654, 'candidate_dd': 17890.35296654, 'win_rate': 0.75}
- Full: {'trades': 190, 'base_net': np.float64(149129.526556424), 'candidate_net': np.float64(143608.402816192), 'net_uplift': np.float64(-5521.123740232004), 'winner_affected': 93, 'stops': 93, 'base_dd': 27336.113567677487, 'candidate_dd': 27336.113567677487, 'win_rate': 0.9421052631578948}

Promotion screen: **False**

The Phase-20 strategy remains the control. No rule is promoted unless it passes validation and 2026 holdout with the preregistered drawdown gate.
