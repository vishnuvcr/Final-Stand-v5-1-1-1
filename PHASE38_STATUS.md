# Phase 38 Status — Corrected Model Robustness vs Stateful Control

**COMPLETE — ALL FIVE MODEL SELECTORS REJECTED FOR PROMOTION**

## Final decision

Phase 38 tested the five Phase-37 polarity-corrected model selectors against the frozen canonical Phase-32 stateful control.

**No selector is promoted.** The canonical stateful direction rule remains the accepted control.

## Final control

Frozen canonical Phase-32 artifact:
- 206 trades
- 102 expiry blocks
- net P&L: **₹63,672.58**
- gross P&L: **₹84,054.00**
- costs: **₹20,381.42**
- win rate: **65.53%**
- profit factor: **1.203**
- maximum drawdown: **₹61,960.87**
- artifact SHA-256: **f98fc6e38e84bdfab09aeeffc2df333da1a3060d3756b1ab12b7e8cb5f32435f**

## Primary paired result

All selectors were compared against the frozen control on 93 common expiry blocks.

| Selector | Mean Δ/expiry | 95% bootstrap CI | P(selector > control) | Expiry blocks won | Full-sample net |
|---|---:|---:|---:|---:|---:|
| CATBOOST | **-₹200.98** | -₹1,485 to +₹1,050 | 37.63% | 40.86% | ₹57,874.80 |
| MARKOV_REGIME_TREE | **-₹252.75** | -₹1,559 to +₹995 | 34.37% | 37.63% | ₹53,060.31 |
| WAVELET_TREE | **-₹486.79** | -₹1,792 to +₹772 | 23.19% | 39.78% | ₹31,294.89 |
| OOF_STACK | **-₹557.00** | -₹1,876 to +₹731 | 20.18% | 33.33% | ₹24,765.71 |
| DART | **-₹614.99** | -₹1,918 to +₹699 | 18.11% | 35.48% | ₹19,372.11 |

All 10,000-resample bootstrap intervals cross zero, and every point estimate favors the control.

## Holdout and stress

All five selectors were positive in the 2026 holdout:
- CATBOOST +₹49,054.33
- MARKOV_REGIME_TREE +₹41,969.35
- WAVELET_TREE +₹50,776.68
- OOF_STACK +₹48,345.59
- DART +₹39,053.96

At +50% transaction costs, all five remained positive. At +100% costs, DART became slightly negative (−₹522.77).

## Direction asymmetry

Every selector produced positive CALL-side net P&L and negative PUT-side net P&L. OOF_STACK was especially asymmetric: 80.8% of trades were PUT-side and its PUT-side net P&L was −₹18,294.25.

This asymmetry is an additional reason not to promote any selector.

## Reproducibility audit

A fresh Phase-32 reconstruction produced 205 trades / 103 expiries / +₹65,945.47 instead of the frozen 206 / 102 / +₹63,672.58 control. This was logged as **F38-001**.

The primary treatment comparison therefore uses the frozen canonical control artifact; the regenerated control is retained only as an audit record in control_validation.json.

## Workflow evidence

- Successful corrected run: **37433424224**
- Earlier mismatched-control run: **37432966945** — rejected as primary evidence.
- Pull request: **#12**

## Phase 38 outcome

**REJECT ALL FIVE CORRECTED MODEL SELECTORS. DO NOT CHANGE THE CANONICAL STATEFUL DIRECTION RULE.**

Next research priority: Phase 39 robustness of the canonical strategy, with broker-realistic bid/ask, latency/fill and cost/slippage validation.


## Secondary risk-adjusted diagnostic

A cumulative **net-P&L / maximum-drawdown** ratio was calculated as a Calmar-style diagnostic:

| Strategy | Net/DD |
|---|---:|
| MARKOV_REGIME_TREE | **1.309** |
| CATBOOST | **1.173** |
| STATEFUL_CONTROL | **1.028** |
| WAVELET_TREE | **0.579** |
| OOF_STACK | **0.399** |
| DART | **0.368** |

Markov has the strongest cumulative return-to-drawdown efficiency and CatBoost ranks second. This does **not** alter the Phase-38 rejection because neither model beats the frozen control in the preregistered paired expiry comparison.
