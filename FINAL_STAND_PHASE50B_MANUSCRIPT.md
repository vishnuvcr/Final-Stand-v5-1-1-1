# Final Stand v5 — Phase 50B Final Research Manuscript

## Abstract
Phase 50B expanded the NIFTY weekly-options research universe with seven supplied Tradetron strategies and prior GitHub lineages. After source-semantic replay and a preregistered 95% quote-coverage gate, four candidates remained: TT-03 Corrected Dynamic-n, TT-03 OTM350, TT-04 Profit Breakout Premium Match Straddle, and TT-05 Simple Intraday Short Straddle. Chronological development was 2021–2023, validation 2024–2025, and 2026 was a protected holdout. Four fixed execution-cost models were tested. Statistical inference used 16 fixed strategy-by-cost hypotheses, 10,000 sign-randomization permutations, 10,000 expiry-day block-bootstrap replicates, and Holm correction. No strategy passed the all-cost robustness rule. TT-03 and OTM350 were positive at the first three cost models but failed the strict ₹20/order plus 50% friction criterion after multiplicity correction. TT-04 and TT-05 failed the primary inferential gate. Final decision: NO PROMOTION.

## 1. Research question
Do the previously studied NIFTY option strategies and the seven supplied Tradetron strategies contain a VIX-conditioned or far-OTM variant that survives chronological validation, realistic execution costs, multiplicity-controlled inference, and a protected 2026 holdout?

## 2. Aims and objectives
1. Reproduce source-faithful strategy behavior under common execution costs.
2. Reject candidates with inadequate mandatory-exit quote coverage.
3. Test only semantically valid VIX and far-OTM mutations.
4. Preserve chronological development, validation and holdout separation.
5. Quantify P&L, profit/trade, win rate and drawdown.
6. Apply multiplicity-controlled statistical inference without using the holdout.
7. Produce a finite reproducible decision rather than open-ended optimization.

## 3. Candidate provenance
The supplied Tradetron universe comprised Dynamic Ratio Reversals; 0.20/0.10 Delta Calendar Hedge Spread v4; Corrected Dynamic-n NIFTY Weekly Options Strategy; Profit Breakout Premium Match Straddle; Simple Intraday Short Straddle; Intraday Asym Premium; and Dynamic IC to Ratio. Prior GitHub lineages included Iron-condor-to-ratio, Option-intraday, NoDip, MC-OPTIONS, Daily-Options and Final-stand families.

TT-06 and TT-07 failed the preregistered feasibility gate and their P&L was excluded from confirmatory inference.

## 4. Scientific methodology
Historical option quotes were replayed without forward filling or silent imputation. Mandatory exit coverage required at least 95%. Historical lot sizes, no-look-ahead rules and the registered Paytm Money execution-cost proxy were retained. Doubled-friction stress was mandatory.

Phase 50B-3 tested 28 preregistered VIX hypotheses using DEV+VAL only; no Holm-adjusted robust-positive VIX effect was found. Phase 50B-4 admitted only TT-03 to semantically valid strike-distance mutation. Frozen geometries were BASE ±300/350/400, OTM350 ±350/400/450 and OTM400 ±400/450/500. OTM350 was selected on development data before validation.

Phase 50B-5 compared TT-03, TT-03 OTM350, TT-04 and TT-05 chronologically. The authoritative publication run was 37828322922.

Phase 50B-6 used DEV+VAL 2021–2025 only. The 2026 holdout was protected. For each of 16 strategy-by-cost hypotheses, the null was expected trade-level net P&L <= 0. The primary test used 10,000 fixed-magnitude sign-randomization permutations. Dependence robustness used 10,000 expiry-day block-bootstrap replicates. A one-sided binomial sign test was secondary. Holm correction covered all 16 primary hypotheses. A primary-positive result required positive mean, positive bootstrap lower 95% bound, and Holm-adjusted p < 0.05. A robust strategy required this at all four cost models.

## 5. Chronological results
| Strategy | Trades | Net ₹ | ₹/trade | Win rate | Max DD ₹ | Net50 ₹ | Net20 ₹ | Net20+50% ₹ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TT-03 | 200 | 89,669 | 448.35 | 74.5% | -13,610 | 82,074 | 75,509 | 60,834 |
| TT-03 OTM350 | 200 | 69,552 | 347.76 | 74.0% | -9,953 | 62,094 | 55,392 | 40,854 |
| TT-04 | 1,214 | 55,583 | 45.78 | 64.2% | -52,597 | 11,430 | -1,718 | -74,521 |
| TT-05 | 1,184 | 52,338 | 44.20 | 61.2% | -60,512 | 9,429 | -3,547 | -74,398 |

The drawdowns are chronological trade-equity drawdowns in rupees, not capital-normalized portfolio drawdowns. No common accepted capital or margin denominator exists in the trade-only evidence.

## 6. Statistical results
| Strategy | Cost | Mean ₹/trade | Bootstrap lower 95% | Holm q | Primary positive |
|---|---|---:|---:|---:|---|
| TT-03 | ₹10/order | 423.69 | 179.63 | 0.0032 | Yes |
| TT-03 | +50% friction | 385.76 | 136.86 | 0.0032 | Yes |
| TT-03 | ₹20/order | 352.89 | 111.88 | 0.0072 | Yes |
| TT-03 | ₹20 +50% | 279.56 | 36.65 | 0.0810 | No |
| TT-03 OTM350 | ₹10/order | 327.14 | 140.81 | 0.0032 | Yes |
| TT-03 OTM350 | +50% friction | 289.89 | 104.80 | 0.0052 | Yes |
| TT-03 OTM350 | ₹20/order | 256.34 | 69.72 | 0.0176 | Yes |
| TT-03 OTM350 | ₹20 +50% | 183.69 | 2.86 | 0.1593 | No |
| TT-04 | ₹10/order | 55.49 | -63.47 | 1.0000 | No |
| TT-04 | +50% friction | 20.20 | -103.30 | 1.0000 | No |
| TT-04 | ₹20/order | 8.29 | -112.80 | 1.0000 | No |
| TT-04 | ₹20 +50% | -50.60 | -168.76 | 1.0000 | No |
| TT-05 | ₹10/order | 83.71 | -29.12 | 0.7159 | No |
| TT-05 | +50% friction | 48.38 | -67.35 | 1.0000 | No |
| TT-05 | ₹20/order | 36.51 | -79.09 | 1.0000 | No |
| TT-05 | ₹20 +50% | -22.42 | -138.91 | 1.0000 | No |

No strategy passed all four cost models.

## 7. Protected 2026 holdout
The holdout was never used for selection or inference. Descriptive results were: TT-03 +₹6,202; TT-03 OTM350 +₹5,106; TT-04 -₹6,456; TT-05 -₹40,245 at the base cost model. TT-03 and OTM350 had only three completed holdout trades, so these figures cannot independently establish robustness.

## 8. Discussion
TT-03 is the strongest source-faithful candidate. Its evidence remains positive through the four cost models in mean P&L, but the strict doubled-friction hypothesis does not survive Holm correction. OTM350 shows the same pattern with somewhat weaker economics. This is evidence of a promising research signal, not evidence sufficient for production promotion.

TT-04 and TT-05 demonstrate why cost sensitivity and dependence-aware inference matter: aggregate lower-cost P&L is not enough when bootstrap uncertainty crosses zero and multiplicity-adjusted inference fails.

## 9. Strengths
- Prospective finite plan and candidate-local stopping.
- Source-faithful replay with explicit semantic audits.
- 95% quote-coverage feasibility gate.
- Historical lot sizes and realistic cost stress.
- Chronological DEV/VAL/HOLD separation.
- Protected 2026 holdout.
- Multiplicity correction across the complete fixed hypothesis family.
- Expiry-day block bootstrap for dependence robustness.
- Persisted GitHub Actions artifacts and logs.

## 10. Limitations
- Historical quote availability can exclude candidates and may introduce feasibility-related selection effects.
- Strategies are heterogeneous and were not evaluated as a capital-allocated portfolio.
- Trade-level evidence does not establish CAGR, Sharpe, or capital-normalized return.
- TT-03 and OTM350 have very small 2026 holdout samples.
- Sign-randomization relies on sign-exchangeability under the null; bootstrap is a dependence-robust diagnostic, not proof of stationarity.
- Cost models are calibrated proxies, not historical broker fill records.
- No live or paper-trading evidence is included.

## 11. Final decision
### NO PROMOTION
No candidate meets the preregistered all-cost robustness requirement. Descriptively, the ranking is TT-03 first, TT-03 OTM350 second, TT-04 third and TT-05 fourth. This ranking does not override the no-promotion gate.

## 12. Future research
Any continuation must be registered as a new phase. Priority directions are broker-level execution-cost calibration; genuinely out-of-sample paper/live validation after freezing parameters; a registered capital/margin model; fresh regime research; capacity and market-impact analysis; appropriate passive/option benchmarks; and preregistered portfolio combination tests.

## Appendix A — Cost models
net = ₹10/order; net50 = ₹10/order with +50% friction; net20 = ₹20/order; net20_50 = ₹20/order with +50% friction.

## Appendix B — Research phase chain
50B-0 registry → 50B-1 feasibility → 50B-2 replay → 50B-3 VIX gate → 50B-4 far-OTM geometry → 50B-5 chronological validation → 50B-6 statistical inference → 50B-7 final manuscript and decision.

## Appendix C — Repository evidence
Research plan: PHASE50B_RESEARCH_PLAN.md. Status files: PHASE50B_*_STATUS.md. Research log: RESEARCH_LOG.md. Error log: ERROR_LOG.md. Chat/action log: PHASE50B_CHAT_LOG.md. Chronological results: results/phase50b/phase50b5_chronological_validation/. Statistical results: results/phase50b/phase50b6_statistical_inference/. Final figures: results/phase50b/final_manuscript/.
