# Phase 43 Pre-registration

## Frozen timing
- Entry: 4 trading sessions before expiry, 10:00 IST.
- Exit: latest complete observation at or before 15:29 IST on expiry day.
- No forward filling, interpolation or same-day look-ahead.

## Frozen VIX states
ALL, LOW, NORMAL, HIGH, SPIKE, FALLING, RISING, HIGH_RISING.
Thresholds are expanding-history thresholds from prior observations only.

## Frozen strike mapping
ATM = nearest listed strike to entry spot; OTM1/2/3 are 1/2/3 listed strike steps away; ITM1 is one step in-the-money.
The engine verifies strike spacing per expiry.

## Execution costs
Every leg gets one adverse 0.05 option tick at entry and exit.
Paytm Money brokerage assumption: ₹10 per F&O order.
Apply date-aware STT, exchange transaction charges, SEBI fees, IPFT, stamp duty and GST.
Orders are counted leg-by-leg.

## Position sizing
Primary results are one historical NIFTY lot. Secondary results normalize finite-risk structures by maximum defined loss.

## Data hierarchy
1. Repository cache.
2. Phase-40 India VIX cache.
3. Existing accepted NIFTY/option cache.
4. Hugging Face dataset thetrademarkk/india-index-options-1m using HF_TOKEN only for missing data.
5. No repeated full downloads when a valid cache exists.

## Statistical controls
Development is for design/router selection; validation is for confirmation; 2026 is untouched holdout.
Bootstrap: 10,000 resamples. Primary unit: expiry.
Raw and Holm-adjusted inference are both reported.

## Evidence rejection
Reject any run with look-ahead, silent missing-data replacement, wrong lot size, wrong expiry, sign errors, omitted fees, corrupted VIX cache, holdout selection or failed artifact persistence.

Only the final accepted GitHub Actions run is evidence.