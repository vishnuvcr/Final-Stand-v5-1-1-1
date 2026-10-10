# Phase 79 — Final evidence sufficiency decision

**Decision: NO_GO_INSUFFICIENT_EVIDENCE**

## Evidence matrix

| Requirement | Status | Evidence / implication |
|---|---|---|
| Exact fixed-contract identity for every leg/time | **FAIL** | Phase 75: rolling Dhan response lacks per-bar exact expiry date; expiryCode/expiryFlag cannot establish contract expiry identity. Affected legs cannot be replayed as exact contracts. |
| Complete target-date fixed-contract observations | **FAIL** | Phase 76 pinned HF dataset files for 2026-07-28 and 2026-08-04 contain trades only through 2026-07-02; expiry sessions absent. Those expiry dates remain excluded; no imputation. |
| Automated-use and retention rights verified for complete sample | **UNVERIFIED** | Prior source gates did not accept a source satisfying all sample, rights and target-coverage requirements. HF dataset card indicates CC-BY-NC-4.0, which is not accepted here as a general commercial-use clearance. No bulk raw-data caching/publication without documented terms. |
| Cost-aware reproducible accounting | **PARTIAL** | Phase 51-3/50B frozen engine outputs include Paytm Money cost scenarios and friction stresses; Phase 77 ledger reconciliation passed. OHLC-based outcomes are not quote/depth-executable fills. Model accounting is reproducible but fill realism remains limited. |
| Temporal/out-of-sample stability | **FAIL** | Phase 78: TT-04 historical HOLD base -₹6,456.29 and +50% friction -₹11,148.57; TT-05 HOLD base -₹40,244.68 and ₹20/order +50% friction -₹49,605.30, despite positive short partial-window outcomes. No strategy promotion. |
| Reproducible audit trail | **PASS** | Phase 71–78 branches record plans/status/error logs and completed workflow evidence; Phase 77 ledger reconciliation had no count/net errors. Sufficient to document the research no-go, not to claim profitability. |

## Strategy disposition

- **TT-02:** not supported; negative in all four registered cost/friction cases in the available partial sample.
- **TT-04:** not promoted. Positive partial-window results conflict with a negative historical HOLD split; cluster-bootstrap intervals include zero.
- **TT-05:** not promoted. Positive partial-window results conflict with a strongly negative historical HOLD split; cluster-bootstrap intervals include zero.

## Data exclusions

Expiries 2026-07-28 and 2026-08-04 remain explicitly excluded. The HF target-named files do not contain the expiry-session bars. Rolling Dhan history is not accepted as fixed-expiry identity. No missing prices were synthesized.

## Conclusion

The evidence is insufficient to recommend a strategy. This is a **research no-go**, not a claim that every conceivable strategy is unprofitable. The finite empirical promotion path stops here until a genuinely new, authorized and contract-identifiable sample is available. Broad source-search loops and outcome-driven parameter changes are not justified.

## Conditions to reopen

- A concrete source provides exact expiry/strike/side identity and complete target-date bars.
- Documented license/API terms permit intended automated analysis and retention.
- Quote/spread or defensible conservative execution assumptions and Paytm Money charges can be applied.
- A pre-registered temporal test can be run without reusing the same holdout for tuning.

## Limitations and next research

The existing outputs are based on minute OHLC, not historical bid/ask/depth; conservative friction stress does not establish real fillability. Any future study must retain Paytm Money brokerage and all applicable statutory charges, date-aware lot sizes, adverse slippage and spread costs. If reopened, begin with rights/sample validation, then a frozen rule-faithful replay, temporal stability, independent holdout, and manuscript generation. No strategy is approved for live trading.
