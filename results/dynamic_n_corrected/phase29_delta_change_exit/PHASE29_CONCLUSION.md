# Phase 29 Delta-Change Exit Research — Conclusion

No target-percentage criterion was used. Candidate target and stop exits were driven entirely by short-leg absolute-delta change over fixed lookback windows. No Phase-20 target or 13:30 conditional stop was used by the candidate; only expiry fallback remains.

Delta coverage: 99.21%
Training-selected target: MEAN_target_lb5_d0.20_c3
Training-selected stop: S1_stop_lb1_d0.05_c3

Training: {'trades': 97, 'base_net': np.float64(60942.315013499996), 'candidate_net': np.float64(15341.431265749996), 'net_uplift': np.float64(-45600.883747750006), 'winner_affected': 25, 'stops': 27, 'base_dd': 21763.229811150002, 'candidate_dd': 12933.832836000005, 'win_rate': 0.7938144329896907}
Validation: {'trades': 77, 'base_net': np.float64(73886.18577038005), 'candidate_net': np.float64(63181.56073901753), 'net_uplift': np.float64(-10704.625031362502), 'winner_affected': 25, 'stops': 30, 'base_dd': 27321.078748147494, 'candidate_dd': 6415.238019809998, 'win_rate': 0.7662337662337663}
2026 holdout: {'trades': 16, 'base_net': np.float64(4108.616860530492), 'candidate_net': np.float64(-4569.16067957001), 'net_uplift': np.float64(-8677.777540100506), 'winner_affected': 7, 'stops': 11, 'base_dd': 17890.35296654, 'candidate_dd': 24862.685747598014, 'win_rate': 0.5}
Full: {'trades': 190, 'base_net': np.float64(138937.11764441052), 'candidate_net': np.float64(73953.8313251975), 'net_uplift': np.float64(-64983.28631921302), 'winner_affected': 57, 'stops': 68, 'base_dd': 27321.078748147498, 'candidate_dd': 24862.685747598, 'win_rate': 0.7578947368421053}

Promotion: False
