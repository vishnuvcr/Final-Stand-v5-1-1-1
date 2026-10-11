# Phase 105 Error and Limitation Log

## Known limitations at registration

- The sample covers one already-inspected 30-calendar-day window, not a fresh independent test and not all market regimes.
- Daily OHLC are bar marks, not bid/ask quotes, book depth or verified fills. Registered adverse-slippage values are scenarios, not empirically observed spreads.
- Paytm Money account-specific brokerage and contract notes are unverified; ₹10/₹15/₹20 per-order rates are sensitivities.
- Fees use Phase 104's date-effective fee engine. Exact contract-note treatment of IPFT/GST and any user-specific charges remain unverified.
- A daily total-volume figure does not prove executable quantity at the open/close. Zero-volume/invalid target-session bars are excluded, not treated as fills.
- Five stocks over one month and only 20 post-warm-up outcome sessions do not support a general profitability claim.

## E105-001 — Reversal candidate not robust to registered stress

**Type:** inference limitation / strategy-promotion blocker; not a runtime error.  
**Evidence:** workflow [38131616138](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38131616138) and `results/phase105/summary.csv` passed source and accounting gates. REVERSAL_ATM netted +₹15,018.02 at ₹20/order, ₹0.25 assumed adverse slippage per side and 1.0× model fees, but its 95% session-cluster bootstrap interval for mean daily P&L crossed zero (-₹2,682.37 to +₹3,957.35) and its median trade was -₹798.60. Under the registered ₹0.50 per-unit slippage and 1.5× fee stress, net P&L was -₹11,709.36.
**Handling:** no strategy promoted; no tuning to rescue it. Need a longer independent sample and a defensible execution model in a separately registered phase.

## E105-002 — EOD bar prices do not identify execution quality

**Type:** structural data limitation.  
**Evidence:** the NSE daily archive supplies OHLC, volume, OI and daily underlying values, not historical bid/ask, depth, queue position, order-arrival latency or partial-fill state.
**Handling:** report every result as an OHLC-price proxy. Slippage values are explicit assumptions, not a claim about actual spreads. Do not infer executable net returns, recommendations or live trading readiness.

## E105-003 — Brokerage/account terms not reconciled

**Type:** cost-model limitation.  
**Evidence:** ₹10/₹15/₹20 per executed order are sensitivity assumptions and the user's Paytm Money account cohort/contract note was not inspected.
**Handling:** keep fee sensitivity and the 1.5× fee stress. Before any later execution-feasibility conclusion, reconcile actual account pricing and contract note with date-effective levies.

## Runtime error status

The verified Actions run passed its automated unit tests, data gate, strategy runner and accounting invariants. No runtime exception was accepted as a research result. Phase 105 closes with evidence/interpretation limitations rather than a code failure.
 

## D105-004 — Documentation formatting correction

**Type:** publication-formatting defect, not a data or numerical error.  
**Evidence:** final documentation QA caught unwanted escape characters before inline-code delimiters in three phase records.  
**Handling:** corrected those Markdown records and re-fetched the branch versions to confirm the files were updated. Numerical outputs, frozen strategy rules, workflow run results and decision are unchanged.
