# Phase 50B Research Plan — User-Supplied + Prior-Repository Strategies

## Purpose

Phase 50B extends the VIX × far-OTM research without altering Phase 50A's frozen numerical results. The scope change is explicit: incorporate the seven user-supplied Tradetron strategies and relevant prior strategy specifications/results from the user's other GitHub repositories.

Phase 50A remains a separate branch and evidence stream. Phase 50B is a new bounded phase because this scope materially changes the candidate universe.

## Primary research question

Do the user's previously created / supplied NIFTY option strategies contain VIX-conditioned and/or far-OTM variants that outperform their frozen source-faithful definitions after realistic Paytm Money/NSE costs, slippage, and chronological out-of-sample validation?

## Source hierarchy

1. User-uploaded Tradetron JSON exports are the executable source of truth for the seven supplied strategies.
2. The seven Tradetron URLs are retained as provenance references. The web crawler could not retrieve those dynamic pages, so no rule is inferred from page HTML where the uploaded export already supplies the rule.
3. Prior GitHub repository strategy specifications are secondary source material and must be revalidated under the current project's cost/data protocol before any claim is accepted.
4. Prior backtest results are historical evidence only and never automatically promoted.

## User-supplied strategies

The seven uploaded exports are:
1. Dynamic Ratio Reversals
2. 0.20/0.10 Delta Calendar Hedge Spread v4
3. Corrected Dynamic-n NIFTY Weekly Options Strategy
4. Profit Breakout Premium Match Straddle
5. Simple Intraday Short Straddle
6. Intraday Asym Premium
7. Dynamic IC to Ratio

The supplied Tradetron URLs, in the order provided by the user, are retained in the registry.

## Prior repository strategy families to include

### A. Iron-condor-to-ratio
Repositories:
- vishnuvcr/Iron-condor-to-ratio-v1
- vishnuvcr/Iron-condor-to-ratio-v2

Source rule: monthly 0.30-delta short IC with 0.10-delta wings; transition when a short leg reaches about 0.10 delta; then directional ratio spread and continuation/reset logic.

### B. Intraday Asymmetric Premium
Repository:
- vishnuvcr/Option-intraday-v1

This duplicates one supplied source strategy but is important because it contains a closed, independently gated historical evaluation. Its negative validated result remains a frozen negative control, not a reason to exclude new VIX/far-OTM variants.

### C. NoDip / four-leg NIFTY calendar
Repository:
- vishnuvcr/NoDip-Stage-1

Frozen source rule: first trading day after prior weekly expiry, 09:15; near-ATM PE buy, near-ATM CE sell, far-expiry same-strike CE buy and PE sell; far expiry three weekly intervals out; exit near-expiry close; one lot per leg; no adjustment.

Historical gross results remain provenance only; Phase 50B will re-evaluate using the current cost and OOS gates.

### D. NIFTY BATMAN / MC strategy
Repositories:
- vishnuvcr/MC-OPTIONS-INDEPENDENT-BACKTEST-MC1
- vishnuvcr/MC-OPTIONS-MARGIN-REDUCTION-MC2
- vishnuvcr/MC-OPTIONS-VERIFICATION-MC3

Frozen MC-RQ6-v1 control: D3, 09:30, 756-session bootstrap, 5,000 paths, P20/P35/P65/P80 mapping, +1/-2/+1/-2 four-leg structure, expiry exit, 2 option-point adverse slippage per leg plus brokerage/STT/lot-size model.

### E. Final Stand v4 option research
Repository:
- vishnuvcr/Final-stand-v4

Includes dynamic OTM8 re-centering, Phase 11 premium-direction ratios, and Phase 12 full-chain option-surface/OI direction research. These are diagnostic candidate sources; no unfinished branch is treated as a validated strategy.

### F. Daily-Options strategy families
Repository:
- vishnuvcr/Daily-Options

Relevant historical families include regime-filtered defined-risk credit spreads, breakout/OI-confirmation families, and IV-skew/tail-credit research. Closed negative results are retained as null/control families. Active/incomplete phases remain source specifications only until independently reproduced.

### G. Naked-option direction
Repository:
- vishnuvcr/Naked-option-v1

This is a current bootstrap research program for long-only NIFTY calls/puts. No historical result is assumed. It may enter the Phase 50B registry as a diagnostic direction-control family only after its finite method registry is frozen.

## Deduplication

The same strategy may appear in both a user upload and a repository. Examples:
- Intraday Asym Premium ↔ Option-intraday-v1
- Dynamic IC to Ratio ↔ Iron-condor-to-ratio-v1/v2

These are treated as one strategy lineage with multiple source references, not as independent hypotheses.

## Source-faithful first, VIX/far-OTM second

Every lineage has two layers:

### Layer 1 — Source-faithful reproduction
Reconstruct the supplied rule exactly:
- entry timing;
- expiry selection;
- strikes/deltas;
- leg ratios;
- adjustment logic;
- exits;
- no hidden parameter changes.

### Layer 2 — Bounded VIX / tail-distance variants
Only after Layer 1 is reproducibly implemented:
- VIX states: LOW, NORMAL, HIGH plus RISING/FALLING/SPIKE/HIGH_RISING where data permit;
- far-OTM distances using actual listed strikes;
- delta-based equivalents where the source strategy already uses delta;
- widths / hedge distances where structurally meaningful.

No source rule is silently replaced by a tuned variant.

## Feasibility classes

### Class A — directly replayable on current intraday option data
Examples:
- Simple Intraday Short Straddle
- Intraday Asym Premium
- Profit Breakout Premium Match Straddle
- corrected Dynamic-n weekly variants

### Class B — replayable with richer monthly/weekly delta history
Examples:
- Dynamic Ratio Reversals
- Dynamic IC to Ratio / Iron-condor-to-ratio
- BATMAN

### Class C — calendar / cross-expiry structures requiring two synchronized expiries
Examples:
- Delta Calendar Hedge Spread
- NoDip

Class C receives a strict data-availability gate. Missing one leg/expiry fails the observation; there is no synthetic substitution.

### Class D — unfinished predictor / model sources
Examples:
- Final Stand v4 Phase 12
- Naked-option-v1 bootstrap
- unfinished Daily-Options phases

These are not allowed to contaminate the source-faithful strategy tournament. They remain diagnostic selectors until separately frozen.

## Statistical design

Development: 2021–2023 where data coverage supports it.
Validation: 2024–2025.
Protected holdout: 2026.

For each source lineage:
1. freeze source-faithful version;
2. calculate development metrics;
3. register only bounded local VIX/tail variants;
4. select on development;
5. freeze exact candidate;
6. test validation;
7. Holm-adjust across the final candidate family;
8. only qualifying candidates reach 2026 holdout.

Primary inference:
- active VIX state versus complement;
- paired comparison against source-faithful control;
- bootstrap confidence interval;
- one-sided permutation test;
- Holm correction.

## Economics

Use the project-standard Paytm Money/NSE cost model:
- brokerage;
- STT;
- exchange transaction charges;
- SEBI fee;
- GST;
- stamp duty where applicable;
- adverse execution/slippage;
- historical NIFTY lot sizes;
- +50% cost stress.

Market-price backtests from Tradetron are never accepted as equivalent evidence to historical quote replay.

## Reproducibility and audit

Every strategy receives:
- immutable source hash;
- source repository/URL;
- normalized strategy specification;
- source-faithful baseline ID;
- VIX variant registry;
- far-OTM/delta variant registry;
- data coverage report;
- cost assumptions;
- error log;
- validation/holdout decision.

## Promotion gate

A new variant is promotable only if:
- positive validation net;
- positive +50% cost-stress net;
- adequate trade count;
- positive active-vs-complement effect;
- Holm-adjusted p < 0.05;
- protected 2026 confirmation.

No source strategy receives grandfathered promotion because of historical Tradetron/GitHub backtest numbers.

## Stop condition

Phase 50B closes when:
- all seven supplied strategies have source-faithful feasibility classification;
- all directly replayable families are reproduced;
- bounded VIX/far-OTM variants have been screened;
- validation/holdout gates are applied;
- final manuscript and registry are complete.

The phase does not search an unlimited parameter space.
