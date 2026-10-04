# Phase 30
# Execution revision: path-filter trigger only; research parameters unchanged Conclusion — Entry-Referenced Combined Short-Leg Delta Proportion

**Selected rule:** target0.60_stop0.60_c1

The tested variable is the proportional change from entry of the sum of the two short-leg delta magnitudes. There is no prior-minute lookback, no delta-difference measure, and no mean of the two short legs.

Delta coverage: 99.21%

    period  trades      base_net  candidate_net     net_uplift  winner_affected  changed      base_dd  candidate_dd  win_rate
  training      97  60942.315013   11167.218486  -49775.096527               89       91 21763.229811   7114.885327  0.659794
validation      77  73886.185770   19679.676238  -54206.509532               67       72 27321.078748  11114.356182  0.610390
   holdout      16   4108.616861   -6757.928395  -10866.545255               10       14 17890.352967  20767.804212  0.500000
      full     190 138937.117644   24088.966330 -114848.151315              166      177 27321.078748  20767.804212  0.626316

## Canonical Phase-20 comparison
    period  phase20_net  phase30_net     difference
  training     62905.98 11167.218486  -51738.761514
validation     75809.78 19679.676238  -56130.103762
   holdout     10413.76 -6757.928395  -17171.688395
      full    149129.53 24088.966330 -125040.563670

**Promotion decision: REJECT.**
