# Phase 42 Literature Review

## Selective prediction and coverage

Gangrade, Kag and Saligrama, Selective Classification via One-Sided Prediction, AISTATS 2021, studies selective classification as an explicit coverage-versus-error trade-off and motivates controlling the fraction of cases on which a model acts. This is directly relevant to Phase 42 because the model is used as a selective override system rather than a mandatory predictor.

https://proceedings.mlr.press/v130/gangrade21a.html

## Financial uncertainty and selective selection

Kaya and Nguyen, Conformal Prediction for Reliable Stock Selections, PMLR 266 (2025), evaluates conformal prediction as a reliability layer for financial stock selection and emphasizes calibrated uncertainty when choosing which signals to act on.

https://proceedings.mlr.press/v266/kaya25a.html

## Policy learning and ranking

Athey and Wager (2021), Policy Learning With Observational Data, frames the target as learning an action policy rather than merely predicting outcomes.

https://doi.org/10.3982/ECTA15732

Yadlowsky et al. (2024/2025), Evaluating Treatment Prioritization Rules via Rank-Weighted Average Treatment Effects, motivates rank-based diagnostics for whether a score concentrates useful treatment effects near its top ranks.

https://doi.org/10.1080/01621459.2024.2393466

Nie and Wager (2021), Quasi-Oracle Estimation of Heterogeneous Treatment Effects, supports separating nuisance prediction from treatment-effect structure.

https://doi.org/10.1093/biomet/asaa076

## India VIX context

NSE describes India VIX as an option-order-book-derived estimate of expected near-term NIFTY volatility over a 30-day horizon. This supports treating VIX as a contextual routing state, not as a direction label.

https://www.nseindia.com/static/products-services/indices-indiavix-index

The recent 2026 SSRN NIFTY volatility-regime literature is treated as hypothesis support only, not evidence for this phase. The repository's Phase 40/41 empirical results remain the primary basis for inference.

## Methodological synthesis

Phase 41 suggests the economic-margin score has ranking information but the uncertainty-penalized action rule was too conservative. The literature supports testing selective coverage explicitly, while preserving strict chronological evaluation and refusing to treat rank diagnostics as causal proof.

Phase 42 therefore tests only one mechanism: controlled score-rank selection using the already validated leading model.
