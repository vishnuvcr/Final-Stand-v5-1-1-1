# Phase 29 Delta-Change Exit Research — Conclusion

No target-percentage criterion was used. Candidate target and stop exits were driven entirely by short-leg absolute-delta change over fixed lookback windows. No Phase-20 target or 13:30 conditional stop was used by the candidate; only expiry fallback remains.

Delta coverage: 99.21%
Training-selected target: MEAN_target_lb5_d0.20_c3
Training-selected stop: S1_stop_lb1_d0.05_c3

Training: {'trades': 97, 'base_net': np.float64(60942.315013499996), 'candidate_net': np.float64(81157.47119775001), 'net_uplift': np.float64(20215.15618425), 'winner_affected': 2, 'stops': 3, 'base_dd': 21763.229811150002, 'candidate_dd': 6825.297276500001, 'win_rate': 0.9896907216494846}
Validation: {'trades': 77, 'base_net': np.float64(73886.18577038005), 'candidate_net': np.float64(74717.64182745505), 'net_uplift': np.float64(831.4560570750015), 'winner_affected': 1, 'stops': 2, 'base_dd': 27321.078748147494, 'candidate_dd': 27321.078748147494, 'win_rate': 0.935064935064935}
2026 holdout: {'trades': 16, 'base_net': np.float64(4108.616860530492), 'candidate_net': np.float64(3533.9246939494915), 'net_uplift': np.float64(-574.6921665810005), 'winner_affected': 1, 'stops': 1, 'base_dd': 17890.35296654, 'candidate_dd': 17890.35296654, 'win_rate': 0.75}
Full: {'trades': 190, 'base_net': np.float64(138937.11764441052), 'candidate_net': np.float64(159409.0377191545), 'net_uplift': np.float64(20471.920074744), 'winner_affected': 4, 'stops': 6, 'base_dd': 27321.078748147498, 'candidate_dd': 27321.078748147498, 'win_rate': 0.9473684210526315}

Promotion: False
