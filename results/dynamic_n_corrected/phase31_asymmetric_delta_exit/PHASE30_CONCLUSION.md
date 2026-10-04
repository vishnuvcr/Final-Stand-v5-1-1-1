# Phase 31
# Execution revision: path-filter trigger only; research parameters unchanged Conclusion — Entry-Referenced Combined Short-Leg Delta Proportion

**Selected rule:** target0.50_stop2.50_c1

The tested variable is the proportional change from entry of the sum of the two short-leg delta magnitudes. There is no prior-minute lookback, no delta-difference measure, and no mean of the two short legs.

Delta coverage: 99.21%

    period  trades      base_net  candidate_net     net_uplift  winner_affected  changed      base_dd  candidate_dd  win_rate
  training      97  60942.315013   28946.726072  -31995.588942               88       90 21763.229811   8966.400195  0.865979
validation      77  73886.185770    3049.723787  -70836.461984               60       65 27321.078748  64438.325556  0.909091
   holdout      16   4108.616861   -2641.143698   -6749.760558               11       14 17890.352967  34504.524069  0.687500
      full     190 138937.117644   29355.306160 -109581.811484              159      169 27321.078748  64438.325556  0.868421

## Canonical Phase-20 comparison
    period  phase20_net  phase30_net     difference
  training     62905.98 28946.726072  -33959.253928
validation     75809.78  3049.723787  -72760.056213
   holdout     10413.76 -2641.143698  -13054.903698
      full    149129.53 29355.306160 -119774.223840

**Promotion decision: REJECT.**
