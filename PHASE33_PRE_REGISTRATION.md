# Phase 33 Pre-Registration

## Frozen hypothesis
H1: At the exact 10:00 IST observation six calendar days before expiry, measurable information in recent NIFTY prices/volatility, global markets and point-in-time sentiment contains out-of-sample information about the expiry-day NIFTY close direction or magnitude.

H0: The requested model families do not produce economically or statistically credible out-of-sample predictive improvement versus simple baselines.

## Exact reference and target
Reference = NIFTY 50 spot at E minus 6 calendar days, 10:00 IST.
Target close = latest complete NIFTY observation at or before 15:29 IST on E.

No shifting is allowed when the reference timestamp is unavailable.

## Baselines
B0 constant-probability model estimated only from training data.
B1 sign of recent 5-session return.
B2 always-CALL / always-UP.
B3 always-PUT / always-DOWN.

## Frozen model specifications
M1 LSTM: 30-session sequence, one LSTM layer, fixed hidden width, dropout and training schedule stated in code before numerical execution.
M2 GARCH: GARCH/EGARCH/GJR-GARCH family, horizon equal to the reference-to-expiry trading horizon; volatility scored separately from directional models.
M3 SOFNN-inspired: Gaussian fuzzy memberships initialized by self-organizing clustering; fixed compact rule count; sentiment + regime features; no feature selection after holdout.
M4 Random Forest: fixed estimator count/depth/feature sampling stated in code; class probabilities retained.
M5 Ensemble: arithmetic mean of M1/M3/M4 probabilities; GARCH only gates predicted move confidence.

## Data leakage controls
- Features are timestamp-censored at 10:00 on the reference date.
- Global markets may use only information whose local market was already closed before the Indian 10:00 cutoff.
- Sentiment records dated after the cutoff are excluded.
- Dataset-provided forward-return/target columns are never used as predictors.
- Model fitting and scaling occur only on past data.
- Holdout is untouched until final reporting.

## Primary evidence
Accepted only from a successful GitHub Actions run that persists:
- point-in-time event dataset;
- model predictions for every model;
- metrics by split;
- leakage/data-coverage audit;
- economic overlay ledger if executed;
- reproducibility metadata.

## Pre-registered decision
No model or ensemble is promoted solely because it has high accuracy. A trading overlay must also improve net outcomes after the repository's established execution-cost model. If the model phase does not pass the OOS promotion gate, the result is rejection for trading use even if in-sample performance is strong.
