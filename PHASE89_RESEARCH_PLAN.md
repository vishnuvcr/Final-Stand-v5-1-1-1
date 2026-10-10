# Phase 89 — Dhan rolling-options feature study

Date registered: 2026-10-10  
Branch: `phase-89-rolling-options-feature-study`  
Status: PREREGISTERED; one bounded historical study to run automatically after workflow commit.

## Rationale and evidence boundary
Phase 88 established that Dhan's `POST /v2/charts/rollingoption` endpoint returns aligned ATM-relative five-minute option OHLC, IV, volume, strike, OI, spot and timestamp arrays for four CALL/PUT probes across 2026-07-28 and 2026-08-04 (608 candles total). That was data-shape/coverage evidence, not a feature-impact or profitability result.

Phase 89 expands the evidence over calendar 2025 only. The Phase 83 protected 2026 holdout is explicitly out of scope and must not be requested, loaded, cached, inspected, or used to select features or thresholds.

## Research question
Do point-in-time rolling ATM-relative option features—mean implied volatility, put-minus-call IV skew, call/put open-interest imbalance, and recent total-OI change—contain an out-of-sample association with the NIFTY spot's next-15-minute absolute move or signed return?

## Aims and objectives
1. Collect a fixed, bounded 2025 sample from Dhan's already-qualified expired-options endpoint.
2. Validate response status, required array presence/alignment, duplicate timestamps, call/put timestamp joins and underlying-spot consistency.
3. Build only timestamp-aligned features available at time t and outcomes over the following 15 minutes.
4. Separate January–June development, July–September validation and October–December confirmatory OOS results chronologically.
5. Test four preregistered OOS hypotheses with day-clustered standard errors and Holm correction.
6. Report data gaps and uncertainty; keep market-feature association separate from executable options strategy profitability.
7. Persist aggregate results and machine-readable audit artifacts to the repository; cache API response files in the repository-scoped GitHub Actions cache rather than logging or committing raw prices/payloads.

## Frozen date/sample specification
- Underlying: NIFTY index options; Dhan `securityId=13`, `exchangeSegment=NSE_FNO`, `instrument=OPTIDX`.
- API: `POST https://api.dhan.co/v2/charts/rollingoption`.
- Interval: five minutes.
- Rolling expiry: `expiryFlag=MONTH`, `expiryCode=1`, `strike=ATM`.
- Sides: CALL (`ce`) and PUT (`pe`).
- Requested arrays: open, high, low, close, IV, volume, strike, OI, spot and timestamp.
- Date period: 2025-01-01 inclusive to 2026-01-01 exclusive. Split into conservative requests of at most 28 calendar days each; overlap/duplicate timestamps are deduplicated after audit. No 2026 dates may be requested.
- Cache: stable key `phase89-dhan-rolling-2025-v1`; cache keys and workflow summaries must not expose access tokens or raw responses.
- Raw prices and response bodies stay in runner cache only; do not commit them or include them in logs/artifacts.

## Chronological splits and preregistered tests
- DEV: 2025-01-01 through 2025-07-01 exclusive.
- VALIDATION: 2025-07-01 through 2025-10-01 exclusive.
- CONFIRMATORY OOS: 2025-10-01 through 2026-01-01 exclusive.
- Target 1: absolute NIFTY spot return over exactly the next 15 minutes, expressed in basis points.
- Target 2: signed NIFTY spot return over exactly the next 15 minutes, expressed in basis points.
- Hypothesis 1: mean CALL/PUT ATM IV at t is associated with absolute next-15-minute spot return.
- Hypothesis 2: PUT IV minus CALL IV at t is associated with signed next-15-minute spot return.
- Hypothesis 3: (CALL OI − PUT OI) / (CALL OI + PUT OI) at t is associated with signed next-15-minute spot return.
- Hypothesis 4: the trailing three-bar percentage change in total CALL+PUT OI at t is associated with signed next-15-minute spot return.
- All four OOS tests are two-sided; family-wise significance threshold 0.05; Holm correction across exactly these four hypotheses. No extra confirmatory features, thresholds, horizons, or multiple-testing families may be added after inspection.
- Fit each one-feature regression independently within each split using feature z-scores within that split and OLS with standard errors clustered by trading session/date. DEV and validation coefficients describe sign replication only; confirmatory inference is the OOS Holm-adjusted family.
- Missing rows are not imputed. Forward targets only use pairs exactly 15 minutes apart; trailing changes require valid past timestamps and stay within the same session. CALL/PUT data must join on exact timestamps.

## Quality / stopping gates
- Every requested interval/side is recorded with status, row count, array-alignment result and sanitized error class.
- Use available valid data even when some windows fail, but label study inconclusive if fewer than 30 OOS sessions or fewer than 1,000 valid OOS observations are available.
- At least 30 OOS session clusters are required for confirmatory results. If this fails, do not interpret p-values as confirmatory.
- Report missing or invalid requests, session counts, paired rows, and the number of sessions covered. No silent truncation.
- Stop after this one registered date range and four primary hypotheses. Do not start optimization or another data expansion phase automatically.
- A significant association is not a trading strategy. No options-entry/exit replay, P&L claim, or promotion is possible from rolling ATM-relative OHLC alone.

## Explicit limitations and excluded fields
The tested endpoint does not establish historical fixed-contract identity, bid/ask, order-book depth, executable fills, Greeks, futures/synthetic futures, VIX, DII/FII flows, news, or corporate-action context. Phase 89 therefore studies only available IV/OI/volume/spot features and does not claim to cover those excluded factors. Features based on option premium changes are omitted because rolling ATM strike changes can create discontinuities.

## Statistical output
- Per-window CALL/PUT API coverage ledger (counts/status/field alignment only).
- Daily paired-sample coverage counts.
- Per-split coefficient, standard error, confidence interval, raw p-value and sample/session count for each registered hypothesis.
- Four OOS raw p-values and Holm-adjusted p-values.
- A plain-language results/status summary, data-quality diagnostics and reproducibility metadata.
- No row-level or raw-price data committed; raw payload files remain in the Actions cache only.

## Cost / execution-quality gate
Paytm Money brokerage, exchange/statutory charges, bid/ask spread, slippage and latency are mandatory before any later execution-quality replay. They are not invented or approximated in this feature-association phase because no fills or strategy trades are simulated.

## Sources
- Dhan expired-options data: https://dhanhq.co/docs/v2/expired-options-data/
- Dhan historical data: https://dhanhq.co/docs/v2/historical-data/
- Phase 87 API shape qualification and Phase 88 four-series coverage audit (prior branch records and workflow results).
