# Phase 27 Supplement — Delta-Based Exit Research

## Research question

Can portfolio delta be used as a state-dependent exit signal for the corrected NIFTY dynamic-n three-leg ratio strategy?

Specifically:
1. Does profit booking become more effective when MTM has reached a high fraction of the original target and portfolio absolute delta is close to zero?
2. Does a large direction-aware adverse portfolio delta identify losing trades early enough to justify a stop?

## Scientific rationale

NSE describes NIFTY 50 index options as European-style CE/PE contracts. urlNSE NIFTY 50 contract specificationshttps://www.nseindia.com/static/products-services/equity-derivatives-nifty50

The practitioner Black-Scholes delta is a standard implied-volatility-based hedge sensitivity, but the academic literature shows that it is model-dependent and need not equal a minimum-variance hedge ratio. Hull and White document this distinction; Alexander et al. discuss smile- and regime-adjusted deltas; more recent index-option work similarly shows that the useful volatility input can vary by moneyness and regime. Therefore this study treats reconstructed delta as an empirical state variable rather than an assumed exact hedge ratio.

## Method

For every complete minute in which NIFTY spot and all three selected option legs were simultaneously observed:

1. Infer each option's implied volatility from its observed price using European Black-Scholes.
2. Use r=0 and q=0 as the baseline reconstruction assumptions.
3. Calculate each leg's Black-Scholes delta.
4. Aggregate actual position signs:
   Δ_portfolio = Δ_long − Δ_short1 − Δ_short2.
5. Define absolute delta as |Δ_portfolio|.
6. Define direction-aware adverse delta as:
   - portfolio delta for the call-side structure;
   - negative portfolio delta for the put-side structure.

The final delta coverage was 99.21%.

## Pre-registered tests

### Profit booking
MTM fractions: 0.50, 0.60, 0.70, 0.80, 0.90 of the original target.

Absolute-delta thresholds: 0.05, 0.10, 0.15, 0.20, 0.25, 0.30.

### Adverse stop
Adverse-delta thresholds: 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50.

Confirmation: 1 or 3 exact consecutive minutes.

### Walk-forward
- Training: through 2023-12-31.
- Validation: 2024-01-01 through 2025-12-31.
- Holdout: 2026-01-01 through 2026-09-30.

The locked Phase-20 strategy is the comparator. Its target and 13:30 expiry-day MFE stop remain active. Delta exits may occur before that control stop, but the control is never altered.

## Results

The training-selected delta profit rule was:

> MTM >= 0.90×target AND |portfolio delta| <= 0.05.

No adverse-delta stop survived the training selection screen.

| Period | Control net P&L | Delta candidate | Difference |
|---|---:|---:|---:|
| Training | ₹62,905.98 | ₹57,140.07 | −₹5,765.91 |
| Validation | ₹75,809.78 | ₹73,475.74 | −₹2,334.04 |
| 2026 holdout | ₹10,413.76 | ₹9,305.72 | −₹1,108.04 |
| Full sample | ₹149,129.53 | ₹139,921.53 | −₹9,208.00 |

The candidate affected 54 profitable control trades in validation and 6 in the 2026 holdout. Maximum drawdown was not improved in either period.

Bootstrap 95% confidence intervals for mean paired uplift were:
- validation: −₹30.31 to +₹86.97;
- 2026 holdout: −₹141.92 to −₹13.82;
- full sample: −₹78.99 to +₹5.25.

The combined promotion screen therefore failed.

## Discussion

The user's proposed intuition—“book profit when delta becomes small, stop when adverse delta becomes large”—is financially plausible, but the backtest shows that the simple version is not useful here.

The important distinction is between **risk state** and **exit value**. A portfolio delta near zero does not imply that the remaining expected P&L is inferior to the value already captured. The ratio structure also has nonlinear gamma and volatility exposure. Consequently, a delta threshold can cause premature exits while the existing target/expiry-stop framework allows the trade to continue through favorable theta/volatility evolution.

Similarly, a large adverse delta is not automatically a good stop signal. In this structure it can arise during temporary spot/volatility moves that subsequently mean-revert. The adverse-delta grid did not produce a training candidate worth carrying forward.

This is consistent with the broader literature's warning that Black-Scholes delta is not a universal minimum-variance hedge ratio and that implied-volatility surface and regime effects matter. Hull & White show that practitioner implied-BS delta can differ from minimum-variance delta. Alexander et al. find evidence for smile/regime adjustments in index-option hedging. High-frequency index-option research also documents rapid, non-Gaussian changes in the implied-volatility surface, particularly for short-maturity OTM puts. urlHull & White — Optimal Delta Hedging for Optionshttps://papers.ssrn.com/sol3/papers.cfm?abstract_id=2658343 urlAlexander et al. — Regime-Dependent Smile-Adjusted Delta Hedginghttps://papers.ssrn.com/sol3/papers.cfm?abstract_id=1678460 urlAndersen et al. — The Fine Structure of Equity-Index Option Dynamicshttps://papers.ssrn.com/sol3/papers.cfm?abstract_id=2350997

## Strengths

- Exact observed one-minute option prices.
- Actual three-leg portfolio delta rather than a single option Greek.
- Same transaction-cost and slippage assumptions as the locked strategy.
- Strict train/validation/holdout separation.
- Paired trade-level bootstrap inference.
- No promoted rule was selected from holdout performance.
- Numerical failures and comparator errors were logged before accepting evidence.

## Limitations

1. Historical exchange/broker Greeks were not available in the primary cached dataset, so delta was reconstructed.
2. The baseline uses r=0 and q=0; this is a pragmatic reconstruction assumption rather than a claim that the true NIFTY forward curve has zero carry.
3. The dataset uses observed close/LTP-like prices rather than full bid/ask/order-book history.
4. The holdout has only 16 trades, so it is useful as a temporal stress test but not a large independent sample.
5. The study tests simple threshold rules, not full smile-adjusted or model-free delta surfaces.

## Conclusion

**No delta-based exit is promoted.**

The Phase-20 canonical strategy remains the research control and final historical specification.

## Future research

A future delta phase should not simply repeat more threshold values. A meaningful next study would test:
- smile-adjusted delta using the local IV surface;
- delta acceleration or delta shock rather than level;
- gamma-adjusted directional exposure;
- delta conditioned on VIX/India VIX and cross-market state;
- separate call-side and put-side delta dynamics;
- model-free or forward-based delta;
- interactions between delta and option OI/volume/volatility regimes.

These should be preregistered as a new phase and compared against the same locked Phase-20 control.
