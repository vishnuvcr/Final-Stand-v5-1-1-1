# Phase 27 Delta Exit Research — Conclusion

Delta was reconstructed minute-by-minute from observed option prices using European Black-Scholes implied volatility (r=0, q=0 baseline), then aggregated using the actual three-leg position signs.

Delta coverage: 99.21%

Training-selected profit rule: profit_f0.90_d0.05
Training-selected adverse stop: NONE

Combined walk-forward:
- Training: {'trades': 97, 'base_net': np.float64(60942.315013499996), 'candidate_net': np.float64(57140.07204440001), 'net_uplift': np.float64(-3802.2429691000025), 'winner_affected': 83, 'stops': 84, 'base_dd': 21763.229811150002, 'candidate_dd': 20276.396015600003, 'win_rate': 0.979381443298969}
- Validation: {'trades': 77, 'base_net': np.float64(73886.18577038005), 'candidate_net': np.float64(73475.73942781001), 'net_uplift': np.float64(-410.4463425700005), 'winner_affected': 54, 'stops': 57, 'base_dd': 27321.078748147494, 'candidate_dd': 27336.11356767749, 'win_rate': 0.948051948051948}
- Holdout: {'trades': 16, 'base_net': np.float64(4108.616860530492), 'candidate_net': np.float64(9305.71989985349), 'net_uplift': np.float64(5197.103039322996), 'winner_affected': 6, 'stops': 8, 'base_dd': 17890.35296654, 'candidate_dd': 17890.35296654, 'win_rate': 0.75}
- Full: {'trades': 190, 'base_net': np.float64(138937.11764441052), 'candidate_net': np.float64(139921.5313720635), 'net_uplift': np.float64(984.4137276529941), 'winner_affected': 143, 'stops': 149, 'base_dd': 27321.078748147498, 'candidate_dd': 27336.113567677487, 'win_rate': 0.9473684210526315}

Promotion screen: **False**

The locked Phase-20 strategy remains the control. A delta rule is not promoted unless it passes the registered validation/holdout and drawdown gates.
