# Phase 41 Literature Review

## 1. Policy learning and heterogeneous treatment effects

Athey and Wager (2021), Policy Learning With Observational Data, Econometrica 89(1), 133–161, develops policy-learning methods using doubly robust treatment-effect estimation and explicitly frames the target as selecting actions under constraints rather than merely predicting outcomes. This supports the Phase-41 decision framing, while also highlighting that policy evaluation assumptions matter. DOI: https://doi.org/10.3982/ECTA15732

Nie and Wager (2021), Quasi-Oracle Estimation of Heterogeneous Treatment Effects, Biometrika 108(2), 299–319, develops a two-step approach that isolates treatment-effect signal from nuisance components before learning heterogeneity. It motivates using a separate economic-margin target and careful nuisance-control rather than optimizing raw outcomes. DOI: https://doi.org/10.1093/biomet/asaa076

Athey, Tibshirani and Wager (2019), Generalized Random Forests, Annals of Statistics 47(2), provides a framework for estimating heterogeneous effects through adaptive neighborhoods. This is relevant as a methodological benchmark, but the small number of independent expiry observations makes unrestricted causal forests a secondary diagnostic rather than the primary model. DOI: https://doi.org/10.1214/18-AOS1709

Zhang, Li and Liu (2020), A unified survey of treatment effect heterogeneity modeling and uplift modeling, surveys uplift/treatment-effect methods and their common potential-outcome framing. https://arxiv.org/abs/2007.12769

## 2. Ranking and treatment prioritization

Yadlowsky et al. (2024/2025), Evaluating Treatment Prioritization Rules via Rank-Weighted Average Treatment Effects, Journal of the American Statistical Association 120(549), proposes RATE metrics for judging whether a prioritization score concentrates positive treatment effects near its top ranks. This is directly analogous to asking whether the Phase-41 predicted override score concentrates positive CALL-vs-PUT counterfactual margins. DOI: https://doi.org/10.1080/01621459.2024.2393466

Phase 41 adapts the idea only as a diagnostic because both hypothetical arms are already observed in the backtest; it does not make a causal claim from the ranking metric.

## 3. Off-policy evaluation

Off-policy evaluation literature motivates caution when learned policies differ from the historical behavior policy. DICE-family work such as Yang et al. (2020) discusses distribution-correction approaches for off-policy evaluation. Phase 41 avoids relying on off-policy estimators for its primary historical claim because the repository can directly calculate both counterfactual arms for each fixed opportunity. The exact sequential replay remains authoritative for trading-policy performance. https://arxiv.org/abs/2007.03438

## 4. India VIX and NIFTY regime relevance

NSE defines India VIX as an option-order-book-derived measure of expected near-term NIFTY volatility and provides historical India VIX data. This makes India VIX a natural regime-state variable but not, by definition, a direction signal. https://www.nseindia.com/static/products-services/indices-indiavix-index

A June 2026 SSRN preprint by Shaunak Sajjan, Variance Risk Premium in Nifty 50 Weekly Expiry Cycles: VIX Calibration Bias and Regime Dependence, reports regime-dependent behavior in 380 weekly NIFTY expiry cycles and specifically finds the high-VIX regime has distinct realized-volatility behavior and an upward directional bias in that sample. Because this is a recent preprint rather than peer-reviewed evidence and may overlap conceptually with the repository's own sample period, Phase 41 treats it as external hypothesis support, not confirmation. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6918100

A 2021 ScienceDirect study on Indian market fear also uses India VIX and historical volatility as explanatory variables and reports predictability of volatility rather than a simple stable directional edge. https://www.sciencedirect.com/science/article/pii/S266709682100032X

A February 2026 SSRN preprint on NIFTY intraday volatility regimes reports persistent volatility states and improved short-horizon volatility forecasts under regime-conditioned models, while return differences across regimes were much weaker. This is consistent with the Phase-40 interpretation that regime information may be more useful for routing than for direct direction prediction. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6316139

## 5. Market-context variables

Phase 41 retains pre-existing point-in-time variables covering:
- global equity markets and global volatility;
- USD/INR;
- gold and crude;
- option IV/skew/OI/volume;
- FII/DII flows;
- timestamped sentiment.

These variables are not introduced as a free-form search space. Their role is constrained to the pre-registered low-dimensional feature list.

## 6. Methodological synthesis

The combined literature suggests three principles that govern Phase 41:

1. The decision target should be the economic value of the available action, not a generic directional label.
2. Heterogeneous treatment/policy value should be assessed with ranking and robustness diagnostics, not only a single mean uplift.
3. Regime variables such as volatility are better treated as contextual state variables unless independent evidence establishes direct directional predictability.

These principles are consistent with the empirical sequence of Phases 38–40 and define Phase 41 without opening another unrestricted model search.
