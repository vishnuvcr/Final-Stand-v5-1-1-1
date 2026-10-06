# Phase 45 Pre-Registration

## Hypothesis
Ready-made option structures have materially different performance conditional on India-VIX state, and the differences can be measured without tuning on the 2026 holdout.

## Evidence reuse
Phase 43 is authoritative for its 22 already-tested families. Phase 45 must not recompute or overwrite those accepted rows.

## VIX timing
VIX information is point-in-time: the current entry date is classified only from observations strictly before the entry session. The expanding 25th/75th level and 10th/90th directional conventions match Phase 43.

## Costs
Historical lot sizes, ₹10/order Paytm Money brokerage, date-aware Indian statutory charges, GST, and one adverse ₹0.05 option tick per leg at both entry and exit.

## Selection
Select only from validation. Rank within each VIX state and risk class by positive validation net P&L and robustness to +50% costs, subject to at least 20 active validation expiries. Holdout is opened only after this freeze.

## Multiple testing
The full preregistered strategy × VIX matrix is treated as a single hypothesis family for Holm adjustment.

## Failure rules
Any look-ahead, wrong expiry linkage, missing quote substituted by forward-fill, wrong strike offset, wrong lot size, omitted fee, persistence failure, or holdout contamination makes the affected run non-evidence until corrected and rerun.