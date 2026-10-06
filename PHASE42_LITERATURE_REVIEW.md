# Phase 42 Literature Review — Confidence Calibration and Selective Prediction

## Conformal prediction

Romano, Patterson and Candès, *Conformalized Quantile Regression*, develops adaptive prediction intervals that account for heteroscedasticity and can be substantially tighter than constant-width conformal intervals. citeturn1academia0

Xu and Xie, *Conformal prediction for time series*, develops time-series conformal methodology and EnbPI specifically for sequential data where exchangeability is not directly appropriate. This supports the decision to use rolling past-only calibration and to avoid claiming iid-style finite-sample guarantees in Phase 42. citeturn1academia3

Angelopoulos et al., *Conformal Risk Control*, extends conformal methods to expected monotone loss/risk control and motivates treating uncertainty as a decision constraint rather than merely a prediction interval. citeturn1academia2

Kato, *Conformal Predictive Portfolio Selection*, applies conformal prediction directly to portfolio-return forecasting and selection, reporting that prediction intervals can be used in portfolio decisions. It is relevant finance-specific evidence, but the present study remains a NIFTY options counterfactual policy problem rather than a portfolio-allocation problem. citeturn2academia0

Schmitt, *Taming Tail Risk in Financial Markets: Conformal Risk Control for Nonstationary Portfolio VaR*, proposes regime-weighted conformal calibration for nonstationary financial risk forecasts and explicitly addresses regime dependence. It is a recent preprint, so it is treated as hypothesis support rather than established evidence. citeturn2academia1

## Calibration and selective prediction

The calibration literature emphasizes that a useful uncertainty estimate must be assessed for decision quality, not merely a numerical confidence score. Recent work on calibrated point predictions combines calibration with conformal confidence intervals and notes that exact conditional calibration is difficult in finite samples. citeturn3academia0turn3academia1

These findings motivate Phase 42's explicit separation of:
- point-prediction ranking;
- uncertainty width;
- selective action/abstention;
- realized economic benefit.

## Relevance to Phase 41

Phase 41 supplied the empirical trigger: zero overrides under a fixed robust-MAD uncertainty penalty, but positive observed DeltaP&L concentration in the top predicted-score groups. This makes confidence calibration a scientifically targeted next question rather than an unrestricted model search.

## Methodological caution

Conformal methods are not magic leakage protection. In financial time series, distribution shift and dependence can invalidate simple exchangeability assumptions. Therefore the phase uses past-only rolling calibration, reports empirical coverage/width, and makes no formal finite-sample coverage claim.
