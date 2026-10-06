# Phase 45 Manuscript — Exhaustive Ready-Made NIFTY Option Strategies by India-VIX State

## Abstract
Phase 45 was initiated to answer a practical gap identified after Phase 44: the strongest VIX result could not be called the best possible VIX-conditioned option strategy because many strategy-builder presets had not yet been compared under a common execution model. The phase therefore evaluated the 20 ready-made structures visible in the supplied screenshots that had not been covered by the accepted Phase-43 matrix, while reusing the 20 Phase-43 families that correspond to the common ready-made universe. This produced a unified 40-family comparison without overwriting prior accepted evidence.

The new sweep generated 5,102 trade rows. Combined with the accepted Phase-43 matrix, the unified analysis contained 9,699 trade rows. India VIX states were classified point-in-time from observations strictly before entry. Costs included historical NIFTY lot sizes, ₹10 Paytm Money F&O brokerage per order, date-aware statutory charges/GST, and one adverse ₹0.05 option tick per leg at entry and exit.

The preregistered empirical screen required at least 20 validation trades, positive validation net P&L and positive P&L under +50% cost stress for a defined-risk strategy/state to enter the working-strategy freeze. Seven validation strategy/state rows passed these economic conditions. All seven were previously tested Phase-43 families; none of the 20 newly added families produced a positive defined-risk validation state meeting the same screen. Six candidates were frozen for 2026 confirmation: three in LOW VIX and three in NORMAL VIX.

The best validation result was a bear call spread in LOW VIX, with ₹24,743 validation net P&L and ₹23,082 under +50% cost stress. Five of the six frozen candidates remained profitable in the untouched 2026 confirmation; the NORMAL-VIX call backspread failed badly in holdout. However, no validation strategy/state survived the preregistered multiple-testing inference gate. The phase therefore does not promote any new VIX-conditioned ready-made strategy to the canonical strategy.

## Research question
Which ready-made NIFTY option structures work best in each India-VIX state after realistic costs, and do any regime-specific results remain statistically defensible and out-of-sample?

## Aims
1. Cover the remaining ready-made structures from the user's strategy-builder screenshots.
2. Reuse accepted Phase-43 evidence rather than recomputing identical strategy families.
3. Compare LOW, NORMAL, HIGH, SPIKE, FALLING, RISING and HIGH_RISING VIX states using point-in-time information.
4. Include realistic Paytm Money brokerage, statutory charges and adverse option-tick slippage.
5. Separate defined-risk candidates from unlimited/diagnostic structures.
6. Freeze candidates only from validation and use 2026 only as confirmation.
7. Produce a final VIX-by-strategy map without changing the canonical Phase-20/42 strategy.

## Strategy coverage
### Newly tested in Phase 45
Buy Call; Sell Put; Bull Condor; Bull Butterfly; Range Forward; Buy Put; Sell Call; Bear Condor; Bear Butterfly; Risk Reversal; Batman; Jade Lizard; Reverse Jade Lizard; Long Iron Condor; Long Iron Butterfly; Double Plateau; Strip; Strap; Long Synthetic Future; Short Synthetic Future.

### Reused from accepted Phase 43
Long/Short Straddle; Long/Short Strangle; Bull Call Spread; Bear Put Spread; Bull Put Spread; Bear Call Spread; Long Call Butterfly; Long Put Butterfly; Short Iron Butterfly; Short Iron Condor; Call Broken-Wing Butterfly; Put Broken-Wing Butterfly; Call Ratio Spread; Put Ratio Spread; Call Backspread; Put Backspread; Long Call Calendar; Long Put Calendar; plus accepted Phase-43 provenance for the remaining calendar variants.

The 20-family Phase-45 subset is the part of the ready-made universe that required new numerical execution. Two additional Phase-43 calendar variants are retained as repository research families but are not part of the screenshot-derived ready-made subset.

## Methodology
Entry: 4 trading sessions before weekly expiry, 10:00 IST.
ATM: nearest listed strike to NIFTY spot.
Strike offsets: fixed listed-strike steps.
Exit: latest complete observation at or before 15:29 IST on expiry day.
Position size: one historical NIFTY lot per leg.
Execution: every leg receives one adverse ₹0.05 option tick at entry and exit; brokerage ₹10 per order; date-aware STT, exchange charges, SEBI fee, IPFT, stamp duty and GST.
No forward filling, interpolation or synthetic quote substitution was permitted.
India-VIX states were calculated from prior observations only, using the accepted Phase-43 expanding-threshold convention.

## Prespecified working screen
A defined-risk strategy/state entered the validation freeze only when it had at least 20 active validation trades, positive validation net P&L and positive validation P&L under +50% cost stress. Statistical inference was then applied separately; economic positivity was not treated as proof of an exploitable edge.

## Numerical results
| Item | Result |
|---|---:|
| New structures numerically tested | 20 |
| New trade rows | 5,102 |
| Accepted Phase-43 rows reused | 4,597 |
| Unified trade rows | 9,699 |
| Validation working strategy/state rows | 7 |
| Frozen validation candidates | 6 |
| Holdout confirmations | 6 |

### Validation working strategies
| VIX state | Strategy | Trades | Net P&L | +50% cost | Mean/trade | Win rate | Max drawdown | Profit factor |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | Bear Call Spread | 49 | ₹24,743 | ₹23,082 | ₹505 | 63.3% | ₹18,254 | 1.46 |
| LOW | Bear Put Spread | 49 | ₹13,892 | ₹12,109 | ₹284 | 51.0% | ₹7,265 | 1.52 |
| LOW | Put Broken-Wing Butterfly | 49 | ₹13,673 | ₹10,477 | ₹279 | 61.2% | ₹12,390 | 1.46 |
| NORMAL | Bear Call Spread | 49 | ₹12,502 | ₹10,658 | ₹255 | 57.1% | ₹12,258 | 1.24 |
| NORMAL | Bear Put Spread | 50 | ₹4,908 | ₹3,037 | ₹98 | 50.0% | ₹5,970 | 1.17 |
| NORMAL | Call Backspread | 49 | ₹3,158 | ₹772 | ₹64 | 30.6% | ₹102,926 | 1.01 |
| LOW | Short Iron Butterfly | 49 | ₹3,714 | ₹221 | ₹76 | 22.4% | ₹14,916 | 1.12 |

The strongest empirical validation combination was therefore LOW-VIX Bear Call Spread, not the falling-VIX Iron Butterfly from Phase 44.

## Newly added strategies: result
None of the 20 newly tested strategy families produced a positive defined-risk validation strategy/state meeting the minimum-20-trade and +50%-cost screen.

Several newly added unbounded/diagnostic structures showed large apparent validation profits in individual VIX states. Examples include Short Synthetic Future, Sell Call, Risk Reversal and Reverse Jade Lizard. These were intentionally excluded from the promotion universe because their tail risk is not capped by the ready-made structure itself. Their point-estimate P&L must not be interpreted as proof of superior strategy quality.

## Regime comparison and multiple testing
Validation active-vs-complement regime comparisons used 10,000 bootstrap resamples and 10,000 permutation tests. Holm adjustment was applied across the preregistered strategy × regime family.

One notable raw result was Bull Condor in NORMAL VIX with an active-vs-complement mean difference of approximately +₹238 per expiry and an unadjusted one-sided p-value of approximately 0.014. It did not survive the full multiple-testing correction and therefore is not promoted.

No validation strategy/state achieved a positive Holm-adjusted inference threshold.

## 2026 holdout confirmation
The six frozen validation candidates were checked without changing their definitions:

| VIX state | Strategy | Holdout trades | Holdout net | +50% cost |
|---|---|---:|---:|---:|
| LOW | Bear Call Spread | 6 | ₹9,560 | ₹9,374 |
| LOW | Bear Put Spread | 6 | ₹7,484 | ₹7,210 |
| LOW | Put Broken-Wing Butterfly | 6 | ₹3,272 | ₹2,762 |
| NORMAL | Bear Call Spread | 11 | ₹7,445 | ₹6,991 |
| NORMAL | Bear Put Spread | 11 | ₹4,924 | ₹4,297 |
| NORMAL | Call Backspread | 11 | −₹86,271 | −₹86,856 |

Thus five of six frozen candidates were positive in the untouched 2026 confirmation, but this does not reverse the failed validation inference gate. The call backspread is an especially clear example of why point-estimate validation performance must not be treated as a live trading guarantee.

## Interpretation
The exhaustive ready-made study changes the interpretation of the earlier Phase-44 finding.

Phase 44 established that a falling-VIX Iron Butterfly was the best empirical result within a narrow six-family tuning universe. Phase 45 shows that, under a broader ready-made comparison, the strongest validation candidates came instead from bearish defined-risk spreads in LOW and NORMAL VIX. The apparent advantage is therefore not specific enough to claim that Iron Butterfly is the best structure for falling VIX.

The broader result is more consistent with regime-sensitive strategy ranking being unstable across strategy families than with one universally optimal VIX strategy.

The most repeatable economic cluster observed in Phase 45 is:

LOW VIX → Bear Call Spread / Bear Put Spread

and, to a lesser degree:

NORMAL VIX → Bear Call Spread / Bear Put Spread.

These are empirical working candidates, not promoted strategies.

## Strengths
- Broad strategy-family coverage.
- Point-in-time VIX classification.
- Realistic lot sizes and Paytm Money cost assumptions.
- Adverse slippage.
- Development/validation/untouched-holdout chronology.
- Explicit separation of defined-risk and unbounded structures.
- Multiple-testing correction.
- Artifact and error logging.

## Limitations
The ready-made study deliberately uses a single fixed preset geometry for each newly added structure rather than optimizing every possible strike geometry. That avoids turning a strategy-family discovery study into a massive post-hoc parameter search.

The validation and holdout samples contain far fewer observations in HIGH, SPIKE, RISING and HIGH_RISING states than in LOW/NORMAL. Those sparse regimes should not be interpreted as evidence of absence of an edge.

Historical close prices do not reproduce every live bid/ask, queue position, latency and fill-quality effect.

## Final decision
NO PROMOTION.

Phase 45 successfully completed the requested exhaustive ready-made strategy comparison. It produced useful empirical regime maps, but no VIX-conditioned ready-made strategy passed the full preregistered statistical promotion standard.

The canonical Phase-20/42 strategy remains unchanged.

## Practical research map
LOW VIX: Bear Call Spread is the strongest validation candidate, followed by Bear Put Spread and Put Broken-Wing Butterfly.

NORMAL VIX: Bear Call Spread is strongest, followed by Bear Put Spread. Call Backspread had a small positive validation result but unacceptable drawdown and failed in the 2026 holdout.

HIGH / SPIKE / RISING / HIGH_RISING: insufficient validation sample size in this design to promote a regime-specific ready-made strategy.

FALLING VIX: the earlier Phase-44 Iron Butterfly observation remains interesting, but Phase 45 does not establish it as the best structure across the broader ready-made universe.

## Future research
The next useful step is not another uncontrolled strategy scan. A focused phase should compare the leading LOW/NORMAL-VIX bearish spreads with continuous VIX change, implied-versus-realized volatility, option open interest, skew, FII/DII flows and cross-market information, with a fixed strategy family and preregistered holdout gates.

## Reproducibility
- PHASE45_RESEARCH_PLAN.md
- PHASE45_PRE_REGISTRATION.md
- PHASE45_LITERATURE_REVIEW.md
- PHASE45_STATUS.md
- PHASE45_CHAT_LOG.md
- research/phase45_ready_made_sweep.py
- results/phase45_ready_made/new_strategy_trade_matrix.csv
- results/phase45_ready_made/full_ready_made_trade_matrix.csv
- results/phase45_ready_made/strategy_vix_summary.csv
- results/phase45_ready_made/validation_regime_inference.csv
- results/phase45_ready_made/validation_freeze_top3.csv
- results/phase45_ready_made/holdout_frozen_top3_confirmation.csv
- ERROR_LOG.md
- RESEARCH_LOG.md