# Phase 20 — Payoff-Boundary Stop Research

## Question

What happens when NIFTY moves materially beyond the green/profit region of the entry-time payoff chart before expiry?

## Structural boundary

Using the actual selected strikes and the same one-tick entry slippage as the locked backtest, define the entry net credit in points as:

short-leg executed premiums - long-leg executed premium.

The expiry zero-P&L stress boundary is:

- call-side upper boundary = K_(n+1) + K_(n+2) - K_n + credit;
- put-side lower boundary = K_(n+1) + K_(n+2) - K_n - credit.

This boundary is calculated entirely from entry information.

## Pre-registered search

Buffers: 0, 50, 100, 200 and 400 NIFTY points.  
Confirmation: 1 or 3 exact consecutive minutes.  
Conditions: boundary-only; boundary + negative MTM; boundary + negative MTM + MFE < 0.50× target.

Selection used training only, requiring zero baseline-positive trades affected and then maximizing training net uplift.

## Selected boundary rule

**boundary_b400_c1_boundary_only**

Buffer: 400 NIFTY points  
Confirmation: 1 minute(s)  
Condition: boundary_only

## Walk-forward comparison

### Training
                     variant  trades     base_net  candidate_net  net_uplift  winner_affected  loss_reduction  losses_eliminated  stops      base_dd  candidate_dd
         phase19_expiry_stop      97 60942.315013   62905.982659 1963.667645                0     1963.667645                  0      1 21763.229811  19799.562166
      selected_boundary_stop      97 60942.315013   61654.221346  711.906332                0      711.906332                  0      1 21763.229811  21051.323479
combined_boundary_or_phase19      97 60942.315013   62905.982659 1963.667645                0     1963.667645                  0      1 21763.229811  19799.562166

### Validation
                     variant  trades    base_net  candidate_net    net_uplift  winner_affected  loss_reduction  losses_eliminated  stops      base_dd  candidate_dd
         phase19_expiry_stop      77 73886.18577   75809.779174   1923.593404                0     1938.628224                  0      2 27321.078748  27336.113568
      selected_boundary_stop      77 73886.18577   59495.320241 -14390.865530                0        0.000000                  0      1 27321.078748  41711.944278
combined_boundary_or_phase19      77 73886.18577   61433.948464 -12452.237306                0     1938.628224                  0      2 27321.078748  41711.944278

### Holdout
                     variant  trades    base_net  candidate_net    net_uplift  winner_affected  loss_reduction  losses_eliminated  stops      base_dd  candidate_dd
         phase19_expiry_stop      16 4108.616861   10413.764723   6305.147863                0     7379.249732                  0      2 17890.352967  17890.352967
      selected_boundary_stop      16 4108.616861  -44955.862252 -49064.479113                0        0.000000                  0      2 17890.352967  65371.175997
combined_boundary_or_phase19      16 4108.616861  -44955.862252 -49064.479113                0        0.000000                  0      2 17890.352967  65371.175997

### Full sample
                     variant  trades      base_net  candidate_net    net_uplift  winner_affected  loss_reduction  losses_eliminated  stops      base_dd  candidate_dd
            baseline_no_stop     190 138937.117644  138937.117644      0.000000                0        0.000000                  0      0 27321.078748  27321.078748
         phase19_expiry_stop     190 138937.117644  149129.526556  10192.408912                0    11281.545601                  0      5 27321.078748  27336.113568
      selected_boundary_stop     190 138937.117644   76193.679334 -62743.438310                0      711.906332                  0      4 27321.078748  65371.175997
combined_boundary_or_phase19     190 138937.117644   79384.068871 -59553.048774                0     3902.295869                  0      5 27321.078748  65371.175997

## Phase-19 comparator

The fixed comparator remains:

**13:30 IST on expiry day + combined MTM < 0 + running MFE < 0.50× original target.**

## Boundary promotion screen

Boundary candidate passes the pre-registered screen: **False**

Required:
- zero baseline-positive trades affected in validation and holdout;
- positive net uplift in validation and holdout;
- no more than 5% deterioration in maximum drawdown;
- exact minute-level execution costs retained.

## Interpretation guard

The expiry payoff boundary is an expiry-time structural stress level. An intraday breach does not mean the option position is already at its expiry loss; time value can allow recovery. This is why the research explicitly tested negative-MTM and MFE-filtered variants.

Spot/option alignment uses exact common timestamps only. No forward filling, interpolation or unobserved crossing is assumed.
