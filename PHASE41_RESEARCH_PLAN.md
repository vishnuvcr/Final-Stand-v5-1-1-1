# Phase 41 Research Plan — Regime-Conditional Counterfactual Policy Learning

## Scientific motivation

Phase 39 showed that direct economic-margin learning was more promising than ordinary direction classification, but its positive out-of-sample contribution came from only seven overrides and was preceded by negative development performance. Phase 40 independently showed that India VIX regime conditioning produced the strongest validation cluster, while the pre-selected high-VIX CATBOOST policy remained statistically inconclusive on the untouched 2026 holdout.

Phase 41 therefore tests a narrower hypothesis rather than another classifier sweep:

> Can a small, pre-registered regime-conditional economic-margin policy identify a sufficiently broad and stable set of profitable control overrides, and can matched-state/ranking diagnostics show that the apparent uplift is not merely a sparse selection artifact?

The canonical Phase-32 stateful strategy remains the default and benchmark.

## Primary research questions

1. Does adding explicitly modeled India-VIX regime state to economic-margin prediction improve control-relative policy value?
2. Does the model rank the opportunities with the largest counterfactual CALL-versus-PUT advantage before they occur?
3. Does the apparent value of overrides persist when the selected opportunities are compared against matched non-override states?
4. Does the improvement survive exact sequential replay, realistic costs/slippage and the untouched 2026 holdout?
5. Is India VIX more useful as a regime/routing variable than as a direct directional predictor?

## Aims

### Primary aim
Identify, from a tightly bounded candidate family, a regime-conditional override policy that improves the canonical stateful strategy without materially increasing drawdown.

### Secondary aims
- quantify the incremental value of India VIX level and change;
- test model ranking quality independent of a hard trading threshold;
- perform propensity-matched scoring as a diagnostic of selection overlap, not as proof of causality;
- test stability across development, validation and the frozen 2026 holdout;
- retain a reproducible rejection result if no candidate passes the promotion gate.

## Registered candidate universe

Two economic-margin learners are mandatory:
1. VIX-interaction Sparse-GAM/Ridge: spline-transformed, low-dimensional point-in-time features plus explicit India-VIX regime interactions.
2. VIX-aware ExtraTrees margin learner: shallow, regularized ExtraTrees regressor on the same fixed feature layer.

Each learner is combined with:
- uncertainty penalty: fixed at 1.0 times recent residual MAD scale;
- override margins: ₹0, ₹250, ₹500, ₹1,000;
- routing gates: ALL, HIGH-VIX, HIGH-VIX+RISING.

Declared policy variants: 24.

No learned ensemble weights, no post-hoc architecture changes and no new threshold families are permitted after seeing results.

## Frozen point-in-time feature layer

The existing Phase-39 point-in-time feature matrix is the base source. Phase 41 may use only the following pre-specified categories:

- NIFTY short-horizon returns/ranges/realized volatility;
- NIFTY medium-term returns/realized volatility/drawdown;
- ATM and near-ATM option premium/OI/volume/IV/skew/PCR;
- candidate spread credit geometry;
- global equity returns and global volatility;
- USD/INR, gold and crude returns;
- FII/DII and derivatives-flow summaries already present in the cached matrix;
- timestamped sentiment summaries already present in the cached matrix;
- point-in-time India VIX level, one-session change, high-regime and rising-regime state from the cached Phase-40 VIX file.

No feature may use information after the entry timestamp.

## Data units

The accepted Phase-39 fixed-opportunity panel is reused without changing its outcome definitions:
- 477 opportunities;
- 271 development opportunities / 135 expiries;
- 172 validation opportunities / 82 expiries;
- 34 untouched 2026 holdout opportunities / 20 expiries.

For every opportunity:
- CALL net P&L;
- PUT net P&L;
- DeltaP&L = CALL net − PUT net;
- canonical control action.

Both counterfactual outcomes are already available for every accepted row.

## Chronological model fitting

All model predictions are expanding-window and use only rows strictly earlier than the prediction timestamp.

- Warm-up: first 100 chronological opportunities use canonical control only.
- No random cross-validation.
- No holdout tuning.
- Model residual scale is based only on predictions/outcomes already observed by the current timestamp.
- Development/validation selection occurs before any 2026 policy result is examined.

## Fixed-opportunity screening

For each declared variant, calculate:
- development policy uplift versus canonical control;
- validation policy uplift versus canonical control;
- number and fraction of overrides;
- max drawdown by opportunity order;
- median and mean counterfactual uplift;
- fraction of positive-delta opportunities captured among the highest-scored opportunities.

Selection gate:
1. development uplift >= 0;
2. validation uplift > 0;
3. at least 5 validation overrides;
4. validation max drawdown no worse than 1.25× control;
5. validation override rate <= 25%.

If at least one candidate passes, rank first by validation uplift, then smaller drawdown, then fewer overrides. If none passes, retain the top three validation-ranked variants only as frozen diagnostic candidates.

## Propensity-matched scoring

For the frozen leading candidate, define treatment = policy override and outcome = observed counterfactual improvement DeltaP&L in the fixed-opportunity panel.

Estimate an override propensity using only a pre-specified 10-feature state vector and logistic regression. For validation and holdout separately:
- match override observations to nearest non-overrides within the same VIX regime;
- maximum propensity caliper: 0.05;
- require common-support overlap;
- report treated count, matched pairs, ATT, bootstrap CI and unmatched fraction.

This is explicitly a selection-overlap diagnostic. Because the treatment is policy-generated and both potential outcomes are observed from the backtest, propensity matching cannot establish causal efficacy.

## Ranking diagnostic

For the frozen leading candidate, report actual DeltaP&L in the top 10%, 20% and 30% predicted-override-score groups, with paired bootstrap intervals. This is a direct counterfactual analogue of treatment-prioritization ranking metrics.

## Exact sequential replay

The top three frozen candidates are replayed through the exact chronological strategy engine:
- no overlapping positions;
- same 6x6 NIFTY vertical structure;
- same delta entry/exit rules;
- historical lot-size schedule;
- one-tick adverse slippage;
- brokerage and statutory charges;
- exact option timestamps;
- the canonical stateful direction remains the shadow/default policy;
- an override is allowed only when the model score and preregistered gate permit it.

A different action may change exit time and later opportunities; therefore the sequential replay, not the fixed-opportunity sum, is the only basis for a promotion claim.

## Statistical analysis

Primary:
- paired expiry bootstrap, 10,000 resamples;
- paired sign-flip test;
- 95% CI for mean and total incremental P&L.

Secondary:
- profit factor;
- win rate;
- maximum drawdown;
- override contribution concentration;
- regime/subperiod stability;
- ranking capture;
- matched-state ATT diagnostic;
- +25%, +50% and +100% aggregate cost stress;
- +1/+2/+3 slippage ticks where the engine/data permit.

## Promotion gate

No Phase-41 candidate may replace the canonical strategy unless all are satisfied:
1. positive sequential validation uplift;
2. positive untouched 2026 holdout uplift;
3. no material drawdown deterioration;
4. common-expiry interval does not materially favor the control;
5. positive +50% cost-stress uplift;
6. at least 5 OOS overrides;
7. no single expiry contributes more than 40% of total OOS uplift;
8. stable or improved ranking diagnostics in validation and holdout;
9. no material CALL/PUT asymmetry;
10. no leakage or execution audit defects.

Because the 2026 holdout is small, statistical significance is interpreted with effect size, interval width and multiple-comparison burden rather than p<0.05 alone.

## External-data and literature scope

This phase explicitly retains the broader market context already required by the project:
- India VIX;
- global equity/volatility;
- USD/INR;
- gold;
- crude;
- options IV/skew/OI/volume;
- FII/DII flows;
- point-in-time sentiment.

NSE's official India VIX documentation defines the index as an options-order-book estimate of expected 30-day NIFTY volatility and provides a historical-data access path. The Phase-41 cache remains auditable against NSE before any forward deployment.

## Stop condition

Phase 41 closes after:
1. fixed 24-variant screen;
2. frozen selection and ranking diagnostics;
3. propensity-matched scoring;
4. exact sequential replay of the frozen top three;
5. cost/slippage stress;
6. statistical inference;
7. manuscript/status/readme/error-log update.

No new model class or threshold family is introduced after the results are seen. A materially different mechanism requires Phase 42.
