# Greek-Conditioned Stop-Loss Rules for a NIFTY Weekly Short Strangle

## Abstract

This preregistered historical screen tests 4294 Greek-based stop configurations for a short NIFTY weekly strangle: sell a roughly 0.15-absolute-delta call and put at 10:00 IST on the first observed trading session after the previous listed weekly expiry, and cover at 14:00 IST on the target expiry day unless a Greek stop triggers. Source SHA: 0f4800e43e6f96cec0794369d78eb4d3c4211ef5. Scheduled campaigns: 259; strict exact-minute campaigns passing all gates: 0. Results are one-minute OHLC simulations with model-derived Greeks and not executable fills. No strategy is promoted.

## Research questions

The primary question is whether abs(signed net short-position delta) crossing 0.40 improves after-cost outcomes versus fixed 14:00 exit. Secondary questions compare gross absolute leg delta, gamma, vega and theta rules, all nonempty active-criterion combinations and contemporaneous ANY versus ALL triggers.

## Methods

### Sample and entry construction

Source: thetrademarkk/india-index-options-1m at resolved revision 0f4800e43e6f96cec0794369d78eb4d3c4211ef5, declared CC BY-NC 4.0. Observed option-expiry files define the calendar; only consecutive listed expiries separated by 4–10 days enter the weekly event universe. Entry is the first index session after the previous expiry. Strike selection uses the exact completed 09:59 close, valid Black–Scholes IV, model delta closest to absolute 0.15 and prior OI at least 100. Entry fills use both exact 10:00 option-bar opens; fixed exit uses both exact 14:00 opens on the target expiry day.

### Greek calculations and causal exit

European Black–Scholes model: 6% continuously compounded rate, zero dividend yield, expiry 15:30 IST, 365.25 days/year. Net short portfolio Greeks equal negative call-plus-put long Greek sums. Net delta may cancel; gross delta is the sum of absolute leg deltas. Gamma risk is max(0,−net short gamma) × 0.5 × (0.5% × spot)^2 divided by initial credit. Vega risk is max(0,−short vega per one IV percentage point) divided by credit. Theta ratio is current short theta/day divided by positive entry theta. Signals use completed closes; exits execute at the following exact minute open.

### Rule and cost grid

The finite sweep registered 4294 distinct rules including the no-stop reference. Threshold domains: net delta 0.20–0.80, gross delta 0.40–1.00, gamma and vega normalized 10%–50% of credit, theta ratio 0.00/0.25/0.50/0.75. Test all nonempty subsets, active thresholds, and ANY/ALL simultaneous-trigger modes. Each development/validation rule is evaluated across 24 costs: ₹10/₹15/₹20 brokerage/order × ₹0/₹0.05/₹0.25/₹0.50 adverse per-unit slippage × 1.0×/1.5× modeled statutory charges. The 1.5× value is a stress scenario, not a claim about actual statutory charges.

### Statistical design

Development is target expiries through 2023-12-31; validation is 2024-01-01 through 2025-12-31; holdout starts 2026-01-01 and ends at the source cutoff. One-sided one-sample tests on event-paired net uplift versus the same campaigns' no-stop result are Holm-adjusted over the full rule sweep. Bootstrap 95% confidence intervals are calculated for mean paired uplift for the frozen validation shortlist only. The holdout shortlist is frozen from validation before holdout results are summarized. Holdout metrics do not rank or modify candidates.

## Results

The first run checkpoint reports 259 scheduled and 0 eligible campaigns; 263 are excluded for the reasons enumerated in exclusions.csv. Positive-net validation rules: 0; positive paired-uplift rules: 0; Holm-adjusted paired-uplift p<0.05 rules: 0. Use PHASE110_REPORT.md and the CSV/JSON files for the complete grid, cost sensitivity and campaign-level results.

## Discussion

A stop can limit exposure to directional/volatility moves but may also realize losses earlier, cut profitable positions and increase costs. Signed net delta and gross leg delta answer different risk questions. Gamma is a local second-order spot-move proxy; vega assumes a one-volatility-point move; theta is a decay-edge guard. These are distinct measures and their normalized thresholds are hypotheses rather than interchangeable loss limits. A one-minute model can miss sub-minute triggers.

## Strengths

Pre-registered finite grid, exact point-in-time entry, prior OI guard, exact bar joins, no interpolation, signed short Greeks, next-open stop execution, date-effective lots/fees, all cost cases, validation multiple-testing correction, and frozen holdout shortlist.

## Limitations

Model-dependent Greeks, no historical exchange Greeks or bid/ask, OHLC fill proxy, exact-path exclusions, partial source history, potential sample attrition, fixed model rate/dividend assumptions, and a non-commercial data license. Any resulting rank is exploratory.

## Conclusion

No threshold is declared optimal solely from this sweep. A candidate requires positive after-cost validation and frozen holdout evidence, cost robustness, non-excessive drawdown, adequate coverage, appropriate source rights and independent tester approval before promotion.

## Future directions

If this finite phase ends with a coverage limitation, register a separate bounded phase to validate the free 2017–2020 Zenodo source or acquire/reconcile Dhan historical expired-option data for the missing recent period, then test against higher-frequency quotes if legitimately available. Do not tune new thresholds on this holdout.

## References

1. https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
2. https://dhanhq.co/docs/v2/expired-options-data/
3. https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web
4. https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
5. https://nsearchives.nseindia.com/content/circulars/FA73061.pdf

## Supplementary material

CSV/JSON files, figures, exclusion reasons, source file hashes and the frozen candidate manifest are stored under results/phase110.