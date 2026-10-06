# Phase 46 Research Plan — VIX-Regime Strategy Discovery from YouTube and Public Video Sources

## Research question

Can public YouTube/video sources identify additional, mechanically testable option structures or volatility-routing rules that specifically address the currently sparse **RISING, HIGH, SPIKE and HIGH_RISING India-VIX states**, without importing unvalidated claims directly into the trading strategy?

## Motivation

Phases 43–45 found the strongest empirical evidence concentrated in LOW/NORMAL VIX bearish spreads, while no VIX-conditioned strategy passed the full promotion gate for RISING/HIGH/SPIKE/HIGH_RISING states. The purpose of Phase 46 is therefore **strategy discovery only**: search systematically for new hypotheses before numerical testing.

## Scope and search method

The discovery scan uses multiple keyword families covering:
- India VIX + NIFTY + high/rising/spike volatility
- high-IV / negative-vega structures
- long-volatility / volatility-expansion structures
- backspreads and ratio backspreads
- calendar/diagonal structures
- iron condors/iron butterflies in high VIX
- volatility skew, IV/VIX divergence and term structure
- option-chain/OI/volume-profile confirmation

The search includes Indian and global options educators where the underlying strategy is structurally transferable to NIFTY. Global videos are treated as hypothesis sources only; they are not evidence that the same structure works on NIFTY.

This scan is **not claimed to be literally every YouTube video**. Public search indexing is incomplete and ranking is dynamic. The audit goal is a reproducible, broad keyword sweep that records all relevant indexed results found through the selected queries.

## Inclusion criteria

A video is retained when its title/description materially discusses at least one of:
1. VIX/India VIX as a regime variable;
2. a named option structure whose volatility exposure could plausibly address RISING/HIGH VIX;
3. volatility skew/term-structure/IV information that can be translated into a deterministic strategy rule.

## Exclusion criteria

Exclude:
- pure market predictions with no mechanical strategy;
- promotional claims without a reconstructable structure;
- strategies requiring unavailable proprietary signals unless a public proxy can be defined;
- naked/undefined-risk structures from the promoted-strategy universe unless explicitly marked diagnostic;
- claims treated as factual performance evidence without independent backtesting.

## Discovery-only candidate families

The following families are registered for possible later numerical testing:

### A. Long-volatility / convexity
- Long Straddle
- Long Strangle
- Reverse Iron Condor / Long Iron Condor variant
- Long Iron Butterfly
- Long-volatility debit spreads

### B. Downside convexity for rising VIX
- Put Ratio Backspread
- Put Backspread
- Put Broken-Wing / asymmetric downside butterfly variants

### C. Upside convexity for rising VIX
- Call Ratio Backspread
- Call Backspread variants

### D. Term-structure / expiry-differential structures
- Calendar Spread / Double Calendar
- Calendar Trap
- Diagonal Spread

### E. Volatility-surface routing
- India-VIX level + daily VIX change router
- IV-versus-VIX divergence
- Put-call skew slope / skew-shift router
- VIX term-structure state router where a defensible India equivalent is available
- OI/PCR/volume-profile confirmation as a secondary filter rather than a primary standalone signal

### F. High-VIX short-volatility hypotheses to test only after a spike/fade condition
- Fully hedged Iron Condor
- Iron Butterfly after VIX peak/reversal
- Defined-risk credit spreads triggered by falling VIX following a spike

These are hypotheses, not promoted rules.

## Proposed numerical testing protocol for a subsequent phase

No strategy discovered in Phase 46 is numerically accepted yet. A subsequent numerical phase must:
- preregister exact legs, strikes, entry time, expiry, exits and VIX thresholds;
- preserve the 2026 holdout;
- use point-in-time VIX and option-chain information only;
- include historical NIFTY lot sizes;
- include Paytm Money brokerage and all applicable statutory charges;
- include adverse ₹0.05/leg option slippage at entry and exit under the existing project convention;
- prohibit forward-fill/interpolation/synthetic quote substitution;
- separate defined-risk and undefined-risk structures;
- use development → validation freeze → untouched 2026 confirmation;
- apply multiple-testing correction across the complete registered hypothesis family.

## Phase stop condition

Phase 46 closes after the source scan, candidate classification, deduplication, literature/source ledger and a finite candidate registry are persisted. Numerical strategy testing is a subsequent phase and must not be silently added to Phase 46.
