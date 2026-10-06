# Phase 35 Pre-registration — Advanced Tree and Adaptive NIFTY Prediction

Primary reference: exact 10:00 IST, six calendar days before weekly NIFTY expiry.

Primary model set:
- LightGBM
- CatBoost
- DART boosting
- NGBoost
- BART
- Quantile-boosting tree model

Secondary model/pathway set:
- Wavelet/EMD/VMD + tree features
- adaptive rolling tree training
- chronological OOF stacking of tree models
- dynamic model selection
- regime-conditioned tree gating
- conformal uncertainty layer

Control set:
- Phase-34 XGBoost
- Phase-34 ExtraTrees
- Phase-34 HistGradientBoosting
- Phase-34 Tree-3 ensemble
- Phase-34 Equal-8 ensemble

No holdout tuning. No random k-fold. No post-hoc threshold search. All stacking/calibration uses chronological OOF predictions only.

A model may enter trading-overlay consideration only after it passes validation, holdout, uncertainty, stability and full-cost overlay gates.
