# Phase 52 Research Plan — Factor-Conditioned Options Strategy Discovery

**Branch:** phase-52-factor-conditioned-strategy-discovery  
**Status at initialization:** OPEN — ongoing source discovery, legacy selector pilot, and exhaustive finite-grid replay queue  
**Protocol type:** Open-ended recurring research; every individual Actions run is bounded and auditable  
**Primary instrument:** NIFTY index options, with verified NIFTY spot and futures reference series; cross-index replication is secondary  
**Broker cost model:** Paytm Money, date-aware statutory charges, conservative slippage and fill-stress scenarios

## 1. Research question

Do India VIX and its dynamics, option Greeks and volatility surface, open-interest/volume/PCR features, NIFTY spot/futures basis, synthetic futures, liquidity, market regime/sentiment, global cross-market relationships, flows, event/news context and corporate-action/calendar effects provide incremental, reproducible net profitability when selecting an options strategy and its configuration, compared with an unconditional strategy baseline?

The decision is broader than “which fixed strategy is best.” The experiment will compare:
1. which structure to choose;
2. which finite parameter configuration to use within that structure;
3. when to enter, adjust, hedge, exit or abstain;
4. whether a factor adds useful information beyond simpler controls; and
5. whether the resulting rule holds across the preregistered entry-condition and market-regime matrix.

## 2. Aim and objectives

### Aim

Build a reproducible, data-audited discovery and validation system that searches at least 312 distinct structure × selector hypotheses, then exhaustively evaluates the registered finite configuration space in deterministic shards. The search should continue on a schedule until a candidate passes all registered gates or a serious data, access, licensing, software or safety issue requires intervention.

### Objectives

1. Audit all 40 repositories visible in the connected GitHub account inventory, prioritising user-created option/market-strategy code, registries, parameter sweeps, and previously accepted/rejected research.
2. Search indexed YouTube videos, public strategy education, source code, papers, NSE/BSE documentation, Hugging Face, Kaggle and other accessible public repositories. Store source URLs, retrieval date, claims, reconstructed rules, licensing/access constraints and evidence grade.
3. Create at least 300 distinct candidate hypotheses across strategy structure and selector logic. Deduplicate aliases without erasing valid differences in legs, ratios, expiry pairing, entry logic or risk management.
4. Build a point-in-time data-availability map for each factor and historical interval before any P&L is calculated.
5. Enumerate and test all configurations in the documented finite search domain, with stable configuration IDs and resumable shards. Never claim exhaustive search over continuous/unbounded parameter values.
6. Compare VIX, Greeks/IV/skew, OI/volume/PCR, spot, futures, synthetic futures, skew/term structure, liquidity, trend/range, global markets, FII/DII and event-context factors through preregistered ablations and incremental-value tests.
7. Account for Paytm Money brokerage, date-aware NSE transaction charges, taxes, exchange charges, slippage, bid/ask, latency/fill stress and available historical lot sizes.
8. Preserve chronological training/validation/OOS boundaries, multiplicity correction, failed attempts, source hashes, coverage gaps and reproducible numerical artifacts.
9. Retain both positive and negative results, and publish a final manuscript with methods, charts, tables, appendices, source ledger, configuration space and machine-readable supplements.
10. Keep status, errors, research-step logs and a concise conversation/decision log in the repository. Record decisions and actions—not hidden private chain-of-thought.

## 3. Hypotheses

- H1 — VIX: level, percentile, term structure, change, acceleration and spike/fade state modify the relative performance of long-volatility, short-volatility and directional structures.
- H2 — Greeks/surface: delta, gamma, theta, vega, IV-versus-realised volatility, skew and term structure can improve structure/strike/expiry selection after costs.
- H3 — OI/flow: point-in-time OI change, strike concentration, PCR, volume/OI and buildup/unwind proxies add information beyond spot-only features.
- H4 — underlying/basis: synchronized spot, traded futures and synthetic futures reveal basis/lead-lag conditions that change expected execution value or directional/volatility risk.
- H5 — interaction: combinations of factors may provide incremental utility even where single-factor filters fail; each interaction must be compared against simpler controls to limit overfit.
- H6 — selective action: a calibrated selector with an abstain/no-trade action can improve net outcomes and tail risk versus unconditional strategies and random/hindsight controls.
- H7 — robustness: any apparent uplift should survive chronological walk-forward evaluation, realistic costs, adverse execution stress, regime/entry-condition splits and multiplicity adjustment.

All are falsifiable hypotheses. None is assumed true, and a high in-sample profit or high win rate alone is not evidence of an edge.

## 4. Scope and candidate universe

The initial registry contains 312 candidate hypotheses: 52 base structures × 6 selector modes. The legacy factor-selector pilot is a first sequential test on frozen Phase45 outcomes and Phase39 as-of features; it does not substitute for replaying all 312 registered hypotheses and their variable configurations. The six selector modes are:
1. unconditional/base control;
2. India VIX level/trend/percentile/term-state router;
3. Greeks/IV/skew/gamma/theta router;
4. OI/volume/PCR/strike-concentration router;
5. spot/futures/synthetic-futures/basis router;
6. multivariate regime/sentiment/cross-market/flow/event router.

The registered base structure universe includes every distinct named preset visible in the supplied strategy-builder images—Buy Call/Put; Sell Call/Put; bull call/put spreads; bear call/put spreads; long/short straddles and strangles; long/short iron butterflies and iron condors; bull/bear condors and butterflies; call/put ratio spreads and ratio backspreads; calendars; synthetic futures; risk reversals/range forward; Strip/Strap; Batman; Double Plateau; Jade Lizard/Reverse Jade Lizard—and additional families: broken-wing butterflies, double calendar, call/put diagonals, calendar trap, iron-condor-to-ratio transition, ratio calendar, parity conversion/reversal, futures-basis spread and delta-neutral long-gamma scalping.

Naked, unlimited-loss or execution-fragile structures may be analysed as labelled diagnostics; they are not eligible for live-risk promotion. Undefined-risk structures must be reported separately from defined-risk structures.

## 5. Parameter space and exhaustive-search interpretation

Parameter domains are finite and versioned in research/phase52/configuration_space.json. The current accepted pre-test grid is phase52-grid-v1.3. The validator computes 9,379,584 applicable configurations; this is a queue size, not a count of tested configurations. The registered dimensions include:
- entry time and entry condition;
- days to expiry and weekly/monthly expiry pairing;
- strike selection by ATM offset or target delta;
- strike distance, wing width, ratio and leg quantity;
- entry credit/debit and liquidity/quote quality constraints;
- exit, take-profit, stop, trailing, time and underlying/Greek/VIX-trigger modes;
- hedge instrument, hedge cadence and delta bands;
- VIX level/change/percentile/spike-reversal thresholds;
- Greek, IV/RV, skew and term-structure thresholds;
- OI/PCR/volume/buildup thresholds;
- spot momentum, gap, range, realised volatility and basis/synthetic-basis thresholds;
- available event, cross-market, flow and sentiment context;
- cost/slippage/fill stress level.

For each family, only structurally applicable dimensions are expanded; inapplicable dimensions are explicitly marked rather than silently assigned. The project must enumerate the complete Cartesian product of the frozen applicable finite grid for each candidate over resumable shards. A versioned expansion/refinement can be added only as a separate registered grid version; the original run is preserved.

Continuous real-number spaces cannot be literally exhausted. Therefore the claim is “exhaustive over the published finite grid,” not exhaustive over every mathematically possible parameter value. Coarse-to-fine grids may only be expanded under a logged version change. Candidates/configurations are not silently dropped because interim P&L is poor; if compute limits require a staged queue, every configuration remains queued and the scheduler resumes it.

## 6. Scientific methodology

### Phase A — Governance and lineage

Read parent README, current Phase 51 status/plan/error/chat logs and relevant previous phase plans before any new numerical job. Pin the base commit, source hashes and rule revisions. Create a deduplicated repository/source ledger. User repositories are evidence of candidate specifications, not proof of profitability.

### Phase B — Literature/source discovery

Search:
- peer-reviewed research on option volume, demand pressure, volatility risk premia, option Greeks and implied-volatility surfaces;
- NSE/BSE official market-data, contract and India VIX methodology documents;
- YouTube strategy walkthroughs and transcripts where available;
- public GitHub repositories, Kaggle and Hugging Face catalogs/datasets;
- user's own GitHub strategies and prior Final Stand research;
- StockMock, StockMojo and comparable platforms as strategy-definition/backtest cross-checks, not substitutes for audited quote-level data unless they provide verifiable exports.

Record both positive and negative source findings. Search coverage is broad and reproducible but cannot honestly be described as every video ever published because public indexing is incomplete.

### Phase C — Data inventory and admissibility

Build an as-of timestamped coverage map for options OHLC/volume/OI, spot, futures, VIX, Greeks/IV, global-market data, FII/DII flow, news/events and charges. Use HF_TOKEN from GitHub Actions secrets only for authorised acquisition, never log it, and cache immutable files with path, repository revision, byte size and SHA-256. Follow dataset licensing and do not publish raw licensed/private data without permission.

Reject stale, incomplete, duplicated, timestamp-incompatible or contract-mismatched files. Never forward-fill missing option premiums, interpolate tradable quotes, fabricate Greeks/OI, or use future information. When only LTP exists, model adverse fills and explicitly mark bid/ask uncertainty.

### Phase D — Strategy reconstruction and registry

For each source: freeze leg directions, quantities, strike mapping, expiry pairing, entry timing, rebalance/repair logic, exits and capital/margin assumptions. Record ambiguities and alternatives as distinct variants. A source's advertised return is a hypothesis, not evidence. Validate that 312 candidate IDs are unique and every candidate maps to a documented structural rule and a source lineage.

### Phase E — Replay and configuration enumeration

Use point-in-time quotes and exchange-valid contract metadata. Generate every applicable configuration deterministically. Queue items carry candidate ID, configuration ID, data fingerprint, engine revision and seed. Jobs process bounded shards, write durable completion markers and resume from the next unprocessed configuration. Replay results must include executed opportunities, exclusions, missing-price reasons, costs, slippage and source lineages.

### Phase F — Factor attribution and interaction tests

Compare each factor-conditioned candidate against the same structure and configuration without that factor, with paired observation windows and identical cost assumptions. Use nested time-ordered validation to select the strategy, parameters and factors. Quantify marginal information through feature ablation, conditional uplift and interactions. Never select a factor based only on contemporaneous or outcome-derived VIX/OI states. Include random/shifted-label placebo controls and a simple baseline.

### Phase G — Validation, costs and robustness

- Development/training: earliest admissible period.
- Rolling/expanding walk-forward validation: only for model/parameter selection.
- Frozen confirmation/OOS: untouched until the selector/configuration is frozen.
- Later prospective paper validation: record actual quote snapshots, intended orders, delayed fills, rejection/latency and realised costs if authorised feeds exist.

Cost scenarios: Paytm Money ₹10/order baseline proxy and ₹20/order sensitivity; date-aware statutory charges under the applicable schedule; at least baseline, +50% and +100% adverse slippage/friction; bid/ask-aware replay when available; fill/latency stress; explicit margin and buying-power usage. If the brokerage schedule changes, version the cost model rather than rewriting past results.

### Phase H — Statistical analysis

Report net P&L, profit/trade, P&L percentage on declared capital and margin, trades, expectancy, win rate, profit factor, mark-to-market maximum drawdown, Sharpe/Sortino/Calmar where valid, volatility, worst trade/day/week, tail loss, expected shortfall/CVaR, capital/margin utilisation, turnover and robustness across regimes.

Use paired bootstrap clustered by expiry/session and where appropriate moving/block bootstrap for serial dependence; confidence intervals; paired permutation/sign-flip tests for incremental uplift; multiple-testing correction (Holm or stronger familywise method); and selection-bias-aware diagnostics such as Deflated Sharpe / probability of backtest overfitting where assumptions permit. Report sample sizes and uncertainty. Zero/low sample regimes remain non-informative, not success or failure.

### Phase I — Promotion gate

A candidate is a research survivor only if it:
1. has source-complete reproducible replay, zero unresolved data errors and registered coverage;
2. is net-positive under the primary cost model and remains acceptable under adverse friction stress;
3. beats its matched unconditional/control policy by a preregistered economically meaningful amount, with an uncertainty interval that excludes zero or an explicitly preregistered equivalent evidence threshold;
4. survives the registered multiple-testing adjustment;
5. exhibits acceptable drawdown/tail risk, adequate trade count and no single-day/expiry concentration;
6. remains credible across the required entry-condition matrix and predefined regimes (or is explicitly scoped to the subset that passed);
7. passes untouched OOS confirmation and all execution/margin audits.

A strategy is never declared successful in all possible market conditions. The final decision must state the exact tested condition matrix and where it did or did not work. No research result automatically authorises live orders.

### Phase J — Manuscript and repeat cycle

Write a structured manuscript with abstract, research question, related literature, data sources and provenance, aims/objectives, strategy registry, methods, statistical plan, results, figures, tables, inferences, discussion, strengths, limitations, conclusion, future work, references and appendices/supplements. Keep machine-readable CSV/JSON, figures and run manifests. Daily/recurring iterations append their checkpoint and continue queued configurations; passed candidates move to robustness/paper confirmation but do not terminate the broader discovery process.

## 7. Entry-condition matrix

At minimum report independent results for:
- time-of-day buckets;
- opening gap and gap direction;
- trend / range / breakout / reversal / high-noise states;
- India VIX LOW/NORMAL/HIGH, rising/falling, spike and post-spike reversal;
- expiry proximity and weekly/monthly tenor;
- high/low IV-RV spread and skew;
- directional, delta-neutral and volatility-expansion conditions;
- OI/PCR/liquidity feature availability buckets;
- spot-futures basis and synthetic-future divergence;
- event versus non-event sessions when time-stamped data support it;
- cross-market aligned/divergent conditions when source quality supports it.

Do not interpret missing-factor rows as neutral-factor rows. Report selection coverage and abstention rate.

## 8. Source and data priorities

1. NSE official contract/specification, bhavcopy, F&O and India VIX material; BSE sources where instruments/underlyings are relevant.
2. Already validated and hash-pinned datasets in earlier project phases; primary RISSIN NIFTY options data and existing validated spot reference where eligible.
3. Hugging Face/Kaggle/open-source market archives, inspected for exact dates, contract coverage, freshness and licence.
4. Official broker APIs/data exports where authorised secrets exist; credentials are checked by presence only and never printed.
5. StockMock/StockMojo and other backtest platforms for reconstructing rule semantics and independent platform comparisons.
6. YouTube and public code for hypothesis generation, followed by independent rule reconstruction.

The known Phase 51 full-window gaps (2026-07-28 and 2026-08-04) remain explicit. Phase 52 may test other verified complete intervals; it must not imply those missing sessions have been solved.

## 9. Automation and governance

- Dedicated branch: phase-52-factor-conditioned-strategy-discovery.
- Main-branch Actions orchestrator: manual dispatch plus scheduled recurring runs; it checks out this research branch and writes durable logs/results to this branch.
- Each run has a bounded wall-time and configuration-shard budget. Continuation is automatic on the next schedule; no single action is an unbounded process.
- Cache immutable input data and package downloads; use repository manifests and Action cache keys. Never commit raw datasets or credentials.
- Append one status checkpoint and log every test outcome and every error/fix. Failed tests are retained as non-evidence, not erased.
- Branch-local manual workflow remains available for focused execution.
- Do not store hidden private reasoning. Store concise decision summaries, commands/results, evidence references and user-visible conversation summaries.
- Do not merge experimental strategy changes to the canonical live/paper strategy until the promotion gates pass.

## 10. Stopping and continuation rules

The research has no arbitrary end date. It continues through scheduled, bounded jobs until at least one candidate survives the full preregistered confirmation matrix, or until the user stops the research, the available data universe is exhausted, or a serious access/licensing/safety/engineering issue blocks further valid research. “Keep searching until successful” is not a guarantee that such a strategy exists; failure to find one is a valid conclusion.

When a survivor appears, continue the overall search while running a separate strict robustness and forward-paper track. Do not relax thresholds after seeing results. Revisions require a new plan version, preserved prior results and a reason logged in the research log/error log.

## 11. Initial deliverables

- PHASE52_RESEARCH_PLAN.md — this protocol.
- PHASE52_STATUS.md — phase and gate status.
- PHASE52_ERROR_LOG.md — operational/scientific error ledger.
- PHASE52_RESEARCH_LOG.md — append-only step outcomes.
- PHASE52_CHAT_LOG.md — visible conversation/decision summaries.
- PHASE52_LITERATURE_REVIEW.md — initial bibliography and evidence hierarchy.
- research/phase52/strategy_registry.csv — 300 hypothesis records.
- research/phase52/configuration_space.json — finite configuration domains.
- research/phase52/repository_audit.csv — inventory of all connected-account repositories and source-audit state.
- research/phase52/validate_registry.py — local validation of the registry and grid.
- research/phase52/factor_attribution.py — point-in-time legacy outcome factor-selector pilot, with development tuning, 2024–25 validation and 2026 holdout.
- research/phase52/results/ — manifests, audit output, shard results, tables and figures.
- .github/workflows/phase-52-factor-conditioned-strategy-discovery.yml — bounded scheduled/manual runner, surfaced on the default branch and in this phase branch.

## Plan changes

This initial plan is the frozen version 1.0. A change to scope, finite grids, hypotheses, cost model or decision gates requires a documented amendment before the amended analysis starts.


## Version history and pre-test amendment

### PA-001 — 2026-10-09 — Registered-universe count and finite-grid clarification

Before any numerical replay, the generated registry was reconciled against this plan. It contains **52 distinct structure families × 6 selector modes = 312 hypotheses**, not 50 × 6 = 300. All 52 families are retained because the extras include additional futures/synthetic-futures, protection and ratio/calendar families. The minimum target remains exceeded; no candidate was dropped based on P&L.

The finite parameter grid was also frozen at `phase52-grid-v1.3` before results: a finite coarse grid is exhaustively enumerated in deterministic resumable shards; costs are evaluated side-by-side for each configuration rather than optimized as a parameter. The amendment does not relax statistical or cost gates and does not change any prior phase result. Any further expansion requires a new version before the expanded grid is evaluated.


## PA-002 — Grid v1.3 audit record — 2026-10-09

The successful first complete bootstrap run shows the committed finite grid identifier is `phase52-grid-v1.3`, with **9,379,584 applicable configurations** across the 312 registered hypotheses. The scheduled/manual runner emits 10,000 deterministic configuration records per default run and checkpoints the next offset. This is queue enumeration only, not 9.38 million backtests. Every cost scenario is evaluated side-by-side for each configuration. Any future domain/grid expansion must be versioned before it is evaluated.


## Plan version history and pre-test amendments

### PA-001 — 2026-10-09 — Candidate universe count correction
The registry contains 52 distinct structure families × six selector modes = 312 hypotheses. All 52 families were retained; no candidate was dropped based on P&L. The versioned finite-grid requirement remains.

### PA-002 — 2026-10-09 — Finite-grid computation feasibility (before numerical results)
Pre-test validator sizing found the original finite-grid draft was too large for a useful recurring queue: grid v1.1 had approximately 197,842,176 configurations; v1.2 had 36,008,064. Before any Phase52 numerical results existed, grid v1.3 reduced the finite domains and froze stale-quote/minimum-OI rules as execution/data gates rather than tunable alpha parameters. Grid v1.3 contains 9,379,584 applicable configurations. At the default 25,000 enumerated configurations per daily run, this represents about 376 runs to *enumerate* the queue alone. Enumeration does not equal backtesting; the runner must separately record actual evaluated configurations. All combinations remaining inside grid v1.3 remain in scope. Subsequent changes require an amendment before the amended grid is tested.

### PA-003 — 2026-10-09 — Add an initial legacy factor-selector pilot
Before full grid replay, add a first-stage test on the existing frozen Phase45 per-expiry trade-outcome matrix joined to the Phase39 point-in-time feature panel. The pilot trains selectors chronologically inside development, chooses one feature per factor group using only the later development-tuning segment, and then reports validation and holdout separately. It uses only a predeclared risk-limited legacy-strategy subset and blocks data if the Phase39 leakage audit or as-of feature join fails. This is evidence from a legacy fixed-entry/expiry-exit matrix only. It does not claim the 312 Phase52 hypotheses or variable configurations have all been backtested. Futures basis and exact-time synthetic-future divergence remain unavailable in this seed panel and are explicitly NOT TESTED.

The plan is now **version 1.3**. No strategy-performance thresholds were relaxed and no grid change was informed by P&L.


### PA-004 — 2026-10-09 — Matched-sample factor pilot coverage gate

The initial join audit found 68.2% of all legacy strategy-outcome rows had a valid same-expiry, point-in-time Phase39 feature observation no later than the entry timestamp and no more than 24 hours earlier. The blanket 90% gate was too coarse because the legacy outcome matrix includes expiry sessions for which the factor panel has no same-expiry observation. Before accepting any factor P&L result, the pilot is amended to: (a) never impute missing features or change the entry/outcome, (b) require at least 50% feature match overall and in each development/validation/holdout split, (c) require at least 20 matched expiry sessions in validation and holdout, (d) publish matched/unmatched rows and expiry coverage by split, and (e) compare every selector only to the baseline on the same matched expiry keys. If any gate fails, the script writes a coverage-only report, records no factor performance, and continues other workflow steps. This permits only exploratory inference on the observable matched sample; it does not remove or backfill missing intervals and cannot satisfy a wider full-data claim.

This amendment uses input coverage information only. No selector P&L or factor uplift had been calculated when PA-004 was added.


### PA-005 — 2026-10-09 — Preserve validation inference when 2026 holdout coverage is insufficient

The source Phase39 feature panel ends on 2026-04-24, while Phase45 outcomes extend further through 2026. Under the matched-sample protocol, the 2026 holdout may therefore fail its coverage gate. Before factor-outcome calculations, the pilot is amended so that (1) development and validation each require at least 50% matched rows, (2) validation requires at least 20 matched expiries, and (3) the 2026 holdout is only evaluated when its own match rate is at least 50% and it includes at least 20 matched expiries. If the holdout does not qualify, development/validation analysis may still be reported as a **validation-only exploratory screen**, and the holdout row is emitted as `HOLDOUT_NOT_EVALUATED_LOW_FEATURE_COVERAGE_OR_SAMPLE`. No holdout-performance claim or promotion can follow. This amendment relies on feature-panel date coverage, not P&L.


### PA-006 — Daily official-format NSE F&O bhavcopy factor supplement (2026-10-09)

**Rationale:** A public GitHub archive has a history of daily NSE F&O bhavcopy ZIPs spanning legacy and post-2024 UDiFF formats, including NIFTY options, futures, daily volume, and open interest. It may add daily point-in-time features where the intraday seed feature panel is incomplete.

**Scope is deliberately narrow:** For each replay event, select the last available index session strictly before the 10:00 IST entry date. Use that session's end-of-day NIFTY option OI/volume for the strategy's target expiry and the nearest non-expired NIFTY futures contract's end-of-day close/OI/volume. If a prior session's archive, target expiry, or needed field is missing, keep the factor missing and log the exact gap; never forward fill or substitute another expiry/session silently.

**Source pinning:** Resolve the source repository to an immutable Git commit at run start, download raw ZIPs by that commit SHA, hash each archive, and persist only normalized feature data, per-session hashes and coverage metadata. Raw ZIPs belong in a bounded GitHub Actions cache, not in the source repository. The MIT code license does not grant ownership or redistribution rights to bundled NSE data; source rights/terms remain a non-commercial/reuse review gate.

**Interpretation:** This produces *lagged daily EOD* OI/PCR and futures-basis proxies only. It is not intraday futures basis, does not establish synthetic-future lead/lag, cannot recover missing 1-minute option quotes for Phase 51, and cannot support claims about intraday futures-market inefficiency. It does not change the frozen phase52-grid-v1.3 or permit a parameter-grid change after seeing outcomes.

**Pre-performance tests:** Both legacy and UDiFF parser fixtures must pass; tree completeness must be verified; no archive row is accepted without NIFTY symbol / option or futures type checks; prior-session mapping must be strictly earlier than entry; each raw archive must have a ZIP signature and SHA-256; output must report per-split event coverage and missing reasons before any P&L analysis.


### PA-007 — 2026-10-09 — Freeze configuration-level replay semantics before grid P&L

**Reason:** The fixed-template base replay and the lagged EOD selector are separate exploratory studies, but neither constitutes testing the 9,379,584 finite grid configurations. A code/data-eligibility gate is required before replaying that grid. The domains and values of `phase52-grid-v1.3` are unchanged by this protocol amendment; it fixes their operational meanings before configuration-level P&L is calculated.

**Protocol:** See `PHASE52_REPLAY_PROTOCOL.md` (protocol version `phase52-replay-v1.0`). In brief: event dates come from the pinned dataset's exact option-expiry files; DTE=0/7 is interpreted as exact calendar-day subtraction; entries are only at exact 09:45/13:00 IST timestamps with one-minute OHLC-open fills; there is no rolling to another date, nearest quote, interpolation or forward fill; validation/holdout splits follow the Phase45 expiry-date boundaries; selector modes gate entry/abstain for the registered strategy family rather than silently switch to another family; all Paytm Money charge and slippage cases are evaluated together.

**Data limitation disclosed:** The underlying source is minute OHLCV(+OI), not tick-level bid/ask or market-by-order data. The parameter `liquidity_max_spread_pct` therefore gates an explicitly labelled intrabar high-low range proxy, not an observed bid/ask spread. A 15-second quote-age claim cannot be verified from these minute bars. No result may be presented as tick-level executable evidence. The lagged NSE futures-basis proxy is not an intraday traded-futures quote feed.

**Eligibility:** Families tagged `PHASE45_TEMPLATE_REQUIRES_RECONCILIATION` or `SPECIFICATION_BLOCKED` receive explicit blocked records pending source/leg reconciliation. Diagnostic-only families may be replayed for diagnosis but can never be promoted. Families that require unprovided intraday futures quotes or hedges are blocked for those configurations rather than approximated with index spot or daily EOD basis.

**Cost semantics:** Base adverse option slippage remains ₹0.05 per leg per fill; the registered 0/50/100 stress levels mean ₹0.05/₹0.075/₹0.10 per leg per fill. Brokerage is ₹10/order with ₹20/order sensitivity. Date-aware statutory fees/taxes remain fixed in these slippage stresses; they are not multiplied by the slippage stress. The prior fixed-template `net50` field is a different legacy all-cost multiplier and must not be conflated with this grid's slippage-only stress.

**No post-result grid tuning:** This amendment relies on quote granularity, source schema, and specification/engineering audit only. It adds no parameter value, removes no v1.3 domain, and is frozen before the first configuration-grid P&L run.


### PA-008 — 2026-10-09 — Make Paytm Money brokerage scenario conservative and explicit

**Evidence:** Paytm Money's official 18-Dec-2024 pricing update states a flat ₹20 brokerage charge across segments from 15-Jan-2025: https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/. A separate F&O FAQ still says ₹10 per executed order: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web. The public documentation is not fully consistent, and plan-specific fees may differ.

**Change:** For all future configuration-grid replays, ₹20/order is the primary conservative brokerage scenario and ₹10/order is a legacy-plan sensitivity. Both are computed side by side for the same fills; neither is an optimizable dimension. The grid version remains `phase52-grid-v1.3`; no configurations or threshold domains are added or removed. The existing fixed-template Phase43/45 results using ₹10/order remain historical diagnostics and must not be re-labelled as ₹20/order results.

**Rationale / timing:** This amendment is based only on official published fee documents and occurs before any grid-configuration P&L is calculated. Exact user's account tariff remains to be verified before deployment consideration.


### PA-009 — 2026-10-09 — Selected-strike gate before configuration P&L

**Trigger:** Broad event-level coverage passed, but it does not prove a configuration's selected strike/leg has valid exact entry and exit bars. This distinction was preregistered in replay protocol v1.0 and is now implemented as a dedicated coverage script.

**Implementation:** `research/phase52/selected_strike_coverage_audit.py` audits offsets -6..+6 around the nearest listed ATM strike for CE and PE, exact entry timestamp, OHLC range consistency, OI≥100, exact 15:15 bar and a common target-expiry exit timestamp. This is a coverage-only gate, not a strategy backtest. A self-test and first full workflow execution are pending.

**ABS_DELTA handling:** Absolute-delta selection remains blocked until a validated point-in-time delta/IV resolver is defined and tested. Do not proxy delta from a single minute close or silently substitute ATM-offset strikes.

**Grid impact:** No parameter domains or candidate IDs change; grid stays `phase52-grid-v1.3`. This amendment is procedural and is recorded before any configuration-grid P&L.


### PA-010 — 2026-10-09 — Reconcile named preset leg templates to Phase45 source definitions

**Evidence:** The Phase45 source plan explicitly defines leg signs and strike offsets for the 11 templates previously flagged for reconciliation. Those definitions are in PHASE45_RESEARCH_PLAN.md on branch phase-45-exhaustive-ready-made-strategies, and the Phase45 sweep implementation maps the same named presets. The ambiguity was documentation status, not missing primary leg definitions.

**Resolved named presets and source geometry:**
- **Bull condor:** +1 CE at +1 step; -1 CE at +2; -1 CE at +3; +1 CE at +4.
- **Bear condor:** +1 PE at -1; -1 PE at -2; -1 PE at -3; +1 PE at -4.
- **Bull butterfly:** +1 CE at +1; -2 CE at +2; +1 CE at +3.
- **Bear butterfly:** +1 PE at -1; -2 PE at -2; +1 PE at -3.
- **Long iron condor:** +1 PE at -1; -1 PE at -3; +1 CE at +1; -1 CE at +3 (source-defined long-condor geometry; do not reinterpret from payoff naming).
- **Long iron butterfly:** +1 ATM PE; +1 ATM CE; -1 PE at -2; -1 CE at +2 (source-defined preset, despite the nonstandard name).
- **Reverse Jade Lizard:** -1 CE at ATM; -1 PE at ATM; +1 PE at +2 steps.
- **Range Forward:** +1 CE at +1; -1 PE at -1.
- **Bear risk reversal:** +1 PE at -1; -1 CE at +1.
- **Batman:** +1 CE at +1; -2 CE at +2; +1 PE at -1; -2 PE at -2.
- **Double Plateau:** +1 PE at -1; -2 PE at -2; +1 PE at -3; +1 CE at +1; -2 CE at +2; +1 CE at +3.

**Change:** The 11 rows in research/phase52/strategy_specifications.csv are now marked STANDARD_VARIANT_PREREGISTERED with provenance notes linking them to the Phase45 source definitions. They remain distinct named families; their source-defined template is the baseline and parameterized variants remain separate configurations.

**Grid impact:** No grid domains, candidate IDs or configuration IDs changed. This resolves source specification gates only and does not constitute a backtest. Registry validation must pass on the next workflow run before these rows are considered eligible for replay. ABS_DELTA resolution remains separately blocked under PA-009.
