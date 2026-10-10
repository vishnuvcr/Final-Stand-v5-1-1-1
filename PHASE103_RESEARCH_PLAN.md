# Phase 103 Research Plan — NIFTY 50 Constituent Stock Options

**Branch:** `phase-103-nifty50-stock-options`  
**Parent:** `main` at branch creation  
**As-of date:** 2026-10-11  
**State:** PHASE REGISTERED; INITIAL FIVE-STOCK UNIVERSE SELECTED; NO STRATEGY TESTED  
**Legacy-data policy:** frozen/read-only. This phase does not edit, migrate, overwrite, or reinterpret earlier phase data or conclusions.

## 1. Research question

Among a preregistered set of five large and actively traded NIFTY 50 constituent stocks, can any rule-based options strategy deliver repeatable positive net expectancy after realistic execution costs and survive chronological, independent out-of-sample testing?

Secondary questions:
1. Which stock-option contracts have sufficient history, liquidity, quote quality and legal access for a credible test?
2. Do price trend, realised/implied volatility, market regime, option Greeks, open interest, volume, sector/index context, earnings/corporate actions and global risk features improve net strategy outcomes beyond simple baselines?
3. Which strategy, if any, remains economically positive after Paytm Money brokerage, statutory charges, spread, slippage, latency and conservative fill assumptions?
4. Are results robust across stocks, volatility regimes, expiry cycles and independent date/expiry clusters?

## 2. Initial stock universe (fixed for Phase 103.0)

| Symbol | Company | Sector | Published NIFTY 50 weight/rank snapshot | Why included |
|---|---|---|---|---|
| HDFCBANK | HDFC Bank Ltd. | Financial Services | 11.83%; rank 1 | Highest-weight constituent in the 27-Feb-2026 official index snapshot; current stock-option chain and active strikes are publicly discoverable. |
| ICICIBANK | ICICI Bank Ltd. | Financial Services | 8.58%; rank 2 | Second-highest weight in the same official snapshot; NSE stock-options quote shows multiple active calls/puts. |
| RELIANCE | Reliance Industries Ltd. | Oil, Gas & Consumable Fuels | 8.20%; rank 3 | Third-highest weight in the same official snapshot; NSE stock-derivatives page exposes active option strikes and contract information. |
| SBIN | State Bank of India | Financial Services | 4.34%; rank 6 | High index weight and visible October-2026 listed call/put activity in NSE stock-derivatives data. |
| INFY | Infosys Ltd. | Information Technology | 3.97%; rank 7 | Large IT exposure and visible October-2026 listed call/put activity in a public stock-options quote. |

**Selection interpretation:** this is the initial five-stock research basket, selected using a transparent combination of the official index-weight snapshot and observable stock-option listings/activity. It is **not** claimed to be a statistically ranked top five by average option volume or spread: the retrieved public snapshots are not all from a synchronized observation window. Phase 103.1 must calculate comparable liquidity and data-quality statistics over a common window. Do not inspect strategy P&L to choose or replace stocks. If a stock fails a preregistered minimum data/liquidity gate, record the reason and use the next eligible name from the ranked candidate queue before testing returns.

Official index source: https://niftyindices.com/docs/default-source/indices/nifty-50/nifty-50-whitepaper_2026.pdf  
Official NIFTY 50 page and constituent download: https://www.nseindia.in/static/products-services/indices-nifty50-index  
NSE equity-derivatives underlyings reference: https://www.nseindia.com/static/products-services/equity-derivatives-list-underlyings-information  
NSE option-chain interface: https://www.nseindia.com/option-chain  
Stock-options snapshots:
- HDFCBANK: https://www.moneycontrol.com/india/fnoquote/hdfcbank/HDF01/2026-10-27/OPTSTK/CE/860.00/true
- ICICIBANK: https://www.nseindia.com/get-quote/derivatives/ICICIBANK/ICICI-Bank-Limited
- RELIANCE: https://www.nseindia.com/get-quote/derivatives/RELIANCE/Reliance-Industries-Limited
- SBIN: https://www.nseindia.com/get-quote/derivatives/SBIN/State-Bank-of-India
- INFY: https://www.moneycontrol.com/india/fnoquote/infosys/IT/2026-10-27/OPTSTK/CE/1040.00/true

Public page display, index inclusion and current contract activity are discovery evidence only; data licensing, history completeness and tradable execution quality remain to be verified.

## 3. Freeze and isolation rules

- This branch is created from `main`; prior research branches, strategy rules, data blobs, cost ledgers, holdouts and result files are not edited.
- Phase 103 uses only its own namespace: `research/phase103_stock_options/`, `tests/phase103/`, and `results/phase103/`.
- Do not use NIFTY index-option outcomes as evidence of individual-stock-option profitability. Prior work may inform general methodology only; it must not be silently pooled with this phase.
- Keep existing protected 2026 index-options holdout sealed. Define a separate stock-options holdout only after data availability and license checks, before candidate tuning.
- Never infer fills from an OHLC bar when the executable side or path is unknown. No missing contract bars, quotes, Greeks, OI, news, or corporate-action fields may be silently imputed.
- No raw data are committed until licence, retention, caching and derived-publication rights are recorded. Use pinned versions/hashes and cached authorised files rather than repeated downloads.
- Conversation log records visible requests and research decisions, not hidden/private reasoning.
- Every failed run, defect, limitation, and correction stays in the phase error log. Every step updates status and research log.

## 4. Aims and objectives

Aim: discover and test robust stock-specific options strategies for the fixed initial five-stock basket without data leakage or understated costs.

Objectives:
1. Establish point-in-time membership, derivative eligibility, contract specifications, expiries, lot sizes, corporate actions and source rights.
2. Audit historical coverage at underlying and exact option-contract level; distinguish absent rows from true zero volume/OI.
3. Quantify liquidity on a synchronized observation window: premium turnover, volume/OI, bid-ask spread and spread/mid, quote depth where available, active strikes, expiry coverage, missingness and tradeable-session counts.
4. Freeze a small candidate family and baselines before validation (trend/breakout; mean-reversion only if specified ex ante; volatility/Greeks/OI filters; defined-risk directional debit spreads; limited-risk vertical credit spreads only when executable legs and margin/costs are modeled).
5. Use strictly chronological training, validation and test periods; keep an independent holdout sealed until the test protocol is frozen.
6. Use date-effective lot sizes and charges. Model Paytm Money brokerage and statutory levies from verified schedules, plus spread, adverse slippage, latency and market-impact stress.
7. Estimate expectancy and uncertainty using independent day/expiry clusters; correct for multiple strategy trials; report drawdown, return on deployed capital, profit factor, tail loss, turnover, coverage and sensitivity.
8. Publish complete reproducible outputs and a manuscript; promote no strategy unless every preregistered evidence gate passes.

## 5. Bounded phases and gates

### Phase 103.0 — Universe freeze and registration (current)
- Freeze five symbols and register all hypotheses, restrictions, source leads, tests and phase stopping rules.
- Deliverables: universe manifest, plan, phase status, research/error/conversation logs, registration validator and manual GitHub Actions workflow.
- Exit gate: all five symbols are unique, sourced, in the NIFTY 50 snapshot and have a listed stock-options discovery reference.

### Phase 103.1 — Common-window data/source feasibility audit
- Check NSE reports/bhavcopies, authorised vendor/public datasets, GitHub, Kaggle and Hugging Face metadata/data where permitted; record exact licenses, terms, hashes, coverage and refresh costs.
- Compute comparable per-stock option liquidity diagnostics over the same dates. Verify point-in-time symbol/contract mappings and data rights before caching.
- Required fields depend on proposed strategy: timestamp, symbol, expiry, strike, CE/PE, OHLC or bid/ask, volume, OI, underlying spot, contract multiplier/lot size, corporate actions and exchange calendars.
- **STOP / NO-GO** if exact contract identity, permitted retention, or adequate sample cannot be established. A source lead or metadata response is not data evidence.

### Phase 103.2 — Canonical dataset and execution audit
- Build immutable source manifest, canonical tables and data-quality ledger; test duplicate keys, timestamp timezone, stale bars, corporate-action adjustments, expiry mapping, missing/zero distinction and contract multipliers.
- Validate bid/ask, liquidity/depth and timestamp synchronization. OHLC-only samples may support explicitly labelled proxy tests, never executable-fill claims.
- Cost engine reproduces broker and statutory charges by effective date; validate with worked examples or contract-note evidence if available.

### Phase 103.3 — Baseline and candidate specification
- Before looking at validation/test/holdout results, freeze baseline rules, entry/exit precedence, max risk, expiry handling and parameter grids.
- Use modest, interpretable candidate families and simple underlier/option baselines. No combinatorial unregistered sweep.
- All short option risk must be defined-risk in the initial candidate set. No naked short-option candidate.
- Record the hypothesis, causal rationale, features, time availability, permitted transformations and expected failure modes for each method.

### Phase 103.4 — Development and validation
- Training/development data select parameters; validation compares a small registered set using net expectancy and risk, not gross P&L alone.
- Avoid look-ahead, survivorship and selection bias; use corporate-action-aware spot data and only features available at signal time.
- Statistical inference uses chronological resampling clustered by date/expiry; multiple-testing adjustment is mandatory.

### Phase 103.5 — Frozen independent test and realistic execution
- Freeze code/rules/configuration before test run.
- Include Paytm Money brokerage, statutory fees/taxes, bid-ask spread, slippage, latency, partial-fill/legging risk and conservative price-path assumptions.
- Stress base and adverse costs, wider spread, delayed entry/exit, reduced liquidity and missed fills.
- Reject candidates with non-positive net expectancy, inadequate coverage, extreme tail/drawdown, fragile performance or confidence bounds that do not meet the prespecified hurdle.

### Phase 103.6 — Sealed holdout and decision
- Open the stock-options holdout once, only after the strategy set and all metrics are locked.
- Rank by evidence grade and risk-adjusted net outcome within comparable samples, not a cross-stock raw-rupee leaderboard.
- Any failure is a documented research result; do not retune on the holdout. A failed holdout ends that candidate.

### Phase 103.7 — Manuscript and bounded closeout
- Publish methods, data provenance, exclusions, results, statistical uncertainty, transaction-cost schedule, charts, tables, errors, limitations, conclusions and future work.
- Stop after this phase. Additional work requires a new user-authorized bounded plan.

## 6. Prespecified metrics and promotion rule

For each stock and pooled basket, report opportunity count; executed and excluded trades with reasons; net P&L; return on deployed capital; mean/median net trade; profit factor; win rate; maximum drawdown and drawdown duration; Sharpe/Sortino only when the sampling assumptions are defensible; worst trade/day; gap/tail exposure; turnover; fill rate; and results by stock, regime and expiry. Report gross and net separately.

A strategy may be labelled **candidate for further paper validation** only if:
- source rights and exact contract mappings pass;
- independently reconciled execution/accounting tests pass;
- predefined coverage threshold passes without selective exclusions;
- net expectancy remains positive under the registered base and adverse cost cases;
- independent test and holdout are not materially contradictory;
- statistical uncertainty and multiple-testing correction meet the preregistered hurdle;
- position sizing and worst-case risk are feasible.

No automated result can by itself authorise live deployment. The final report must plainly say “not established” when any gate is blocked.

## 7. Phase 103.1 first task

Do a metadata/rights audit first, then acquire/cache only authorised samples. Build a comparable liquidity coverage score before strategy backtests. If full historical option quote/depth data are unavailable, test a narrower EOD/defined-risk research question only if the exact strategy can be tested with defensible prices; label the evidence accordingly. Do not invent historical Greeks, spreads or order-book depth.


## Dhan Data API integration amendment — 2026-10-11

Primary authorized acquisition path requested for Phase 103.1: DhanHQ Data API using the repository Actions secret. Official documentation identifies POST /v2/charts/rollingoption for expired options on a rolling basis, with minute bars, up to five years, and a maximum 30-day window per call. Supported fields include OHLC, IV, volume, OI, strike and spot; stock options support ATM through ATM+3/ATM-3. The instrument security ID will be resolved fresh from Dhan's published instrument master rather than hardcoded.

- API docs: https://dhanhq.co/docs/v2/expired-options-data/
- Instrument master: https://dhanhq.co/docs/v2/instruments/
- Endpoint: https://api.dhan.co/v2/charts/rollingoption
- Secret reference: the workflow accepts DHAN_ACCESS_TOKEN, DHAN_API_ACCESS_TOKEN, DHAN_TOKEN or DHAN_DATA_API_TOKEN. Values must never be printed, committed or placed in artifacts.
- First smoke test: HDFCBANK, ICICIBANK, RELIANCE, SBIN and INFY; ATM monthly CALL and PUT; 2026-08-02 inclusive through 2026-09-01 exclusive. This 30-day window is a data-feasibility sample, not a strategy holdout or strategy-P&L sample.
- If successful, Phase 103.1 expands data coverage with rolling 30-day chunks, then audits actual returned rows, timestamp coverage, array-length integrity, missing-versus-zero OI and source/schema changes before candidate rules are developed.
- Rolling relative strikes may map to different actual strikes over time. Do not treat a single ATM-offset series as a persistent fixed-strike contract. Any later strategy must reconstruct contract identity using actual strike/expiry and must exclude intervals when contract identity cannot be preserved.
- This expired-options endpoint does not document historical bid/ask/depth. Quote quality, spread and fills cannot be called historically observed from this endpoint alone. Later P&L must either add an authorized historical quote source or transparently use a conservative, explicitly proxy-based execution model with a no-go gate where evidence is insufficient.
- Raw Dhan payload retention and redistribution rights are not yet verified. The bounded API workflow publishes aggregate audit statistics only; raw response rows stay ephemeral until allowed storage is established. This avoids exposing licensed market data in the public repository.

Phase 103.1 workflow: .github/workflows/phase103-dhan-data-api-audit.yml. The branch-push run and manual dispatch both perform unit tests, query the instrument master, call Dhan's expired stock-options endpoint, and automatically write the aggregate result/status/error checkpoint back to this branch.
