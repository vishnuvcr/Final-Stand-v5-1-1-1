# Phase 42 Manuscript — Confidence Calibration and Selective Counterfactual Routing

## Abstract
Phase 42 tested whether the Phase-41 uncertainty layer was too conservative. Seventy-two preregistered variants were screened chronologically; the holdout was untouched until the top three validation candidates were frozen. Exact sequential replay and paired-expiry inference were then completed.

## Results
See the complete 72-variant grid in results/phase42_confidence_calibration/fixed_grid_validation.csv.

|Rank|Model|Calibration|Margin|Gate|Validation uplift|Holdout uplift|Holdout overrides|
|---:|---|---|---:|---|---:|---:|---:|
|1|SPLINE_RIDGE_VIX|RAW|500.0|ALL|26542.28|20607.09|8|
|2|EXTRATREES_VIX|RAW|250.0|ALL|-23919.81|42514.83|10|

## Statistical inference
Paired-expiry bootstrap and sign-flip results are persisted in sequential_summary.csv.

## Discussion
A ranking signal is not sufficient for promotion unless it converts into robust sequential control-relative P&L after costs. Conformal-style calibration is treated as a selective decision layer; no formal exchangeability-based guarantee is claimed for financial time series.

## Strengths
- bounded preregistration;
- strict chronology;
- untouched holdout;
- exact execution-cost model.

## Limitations
- small independent holdout;
- financial dependence weakens formal conformal guarantees;
- historical fills do not reproduce live latency/queue effects.

## Conclusion
NO PROMOTION — CANONICAL STRATEGY UNCHANGED

## Future research
Require materially new information or prospective broker-quality validation rather than endless threshold tuning.
