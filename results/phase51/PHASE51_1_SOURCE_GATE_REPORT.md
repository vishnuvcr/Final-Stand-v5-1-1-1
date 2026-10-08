# Phase 51-1 Source-Gate Report

## Decision

**PHASE 51-1 STOP — DATA AVAILABILITY / NO OOS REPLAY**

The frozen fresh out-of-sample window remains **2026-04-21 through 2026-08-04**, inclusive. No strategy P&L, statistical inference, candidate ranking, or promotion decision has been produced from this window.

The spot source gate passed. The original NIFTY 1-minute options source does not cover the final two weekly expiries, and the tested public supplemental source failed both endpoint coverage and common-expiry equivalence. The authenticated Upstox recovery path is currently blocked because the repository does not contain the required `UPSTOX_ACCESS_TOKEN` secret.

## Frozen sample

- OOS start: 2026-04-21
- OOS end: 2026-08-04
- Frozen before any strategy OOS P&L inspection
- The window must not be shortened to 2026-07-21 or earlier.

## Data-gate results

| Gate | Source / test | Result | Consequence |
|---|---|---:|---|
| Spot endpoint/session integrity | technovusin/nifty50-historical-data | PASS | Source frozen for replay |
| Spot common-period agreement | 16,467 common minute rows vs original spot source | PASS | No material systematic discrepancy |
| Primary option source | rissin/nse-options-intraday | FAIL | Stops at 2026-07-21 |
| Public option augmentation | thetrademarkk/india-index-options-1m | FAIL | Cannot fill 2026-07-28 / 2026-08-04 |
| Authenticated Upstox contract path | Upstox expired-contract API | BLOCKED | Secret not configured |
| Fresh OOS replay | TT-03 / TT-03 OTM350 | **NOT RUN** | Correct fail-closed outcome |

## Spot validation

Validated source: `technovusin/nifty50-historical-data`, 1-minute NIFTY files for April-August 2026.

The frozen OOS period contains 27,375 spot-minute rows from 2026-04-21 09:15 IST through 2026-08-04 15:29 IST.

Against the originally selected spot source, the common-period comparison contains 16,467 rows with:

- median absolute difference: 0.000 NIFTY points
- p99 absolute difference: approximately 0.767 points
- p95 relative difference: approximately 0.042 bp

The registered overlap gate passed.

The alternative Jitendra12421 fallback was rejected separately because it contained material intraday gaps/fragments on 2026-05-25, 2026-06-25 and 2026-07-08. It is not used as a replay source.

## Options-source limitation

The frozen RISSIN option file:

- repository: `rissin/nse-options-intraday`
- file: `upstox_intraday/NIFTY/NIFTY_2026.parquet`
- SHA-256: `bae9943b2fa99ee9c1214fb7c695b84f9f661a050a5cd04d9c5c2ffc7bc59f73`
- size: 394,805,617 bytes
- observed weekly expiries end at 2026-07-21
- missing: **2026-07-28 and 2026-08-04**

### Rejected public augmentation

Tested source: `thetrademarkk/india-index-options-1m`.

The nominal 2026-07-28 file ends on 2026-07-02, and the nominal 2026-08-04 file also ends on 2026-07-02. Therefore neither file can supply the required late-July/early-August OOS observations.

Before endpoint inspection alone was treated as decisive, common-expiry equivalence was also tested against the original RISSIN source. Exact matched-row coverage was:

| Common expiry | Exact matched rows | Coverage vs RISSIN |
|---|---:|---:|
| 2026-07-07 | 336,794 | 34.57% |
| 2026-07-14 | 153,174 | 14.95% |
| 2026-07-21 | 38,578 | 4.60% |

The preregistered requirement is at least 10,000 exact matched rows **and at least 80% coverage** of the comparable original rows, with the registered price-consistency thresholds. The supplemental source failed the coverage gate.

## Authenticated recovery path

The repo contains a dedicated Upstox acquisition path for 2026-07-28 and 2026-08-04.

The source-gate workflow run **37839447686** failed before downloading the contracts because `UPSTOX_ACCESS_TOKEN` is not configured in the repository. Therefore no authenticated option data were assumed or fabricated.

Upstox's official documentation provides the required expired-contract endpoint and documents 1-minute expired historical candles; the 1-minute expired-candle capability is restricted to Upstox Plus. 

## Scientific interpretation

This is a **data-availability stop, not a strategy failure**.

It would be methodologically invalid to:

1. shorten the OOS window after discovering the coverage defect;
2. drop the 2026-07-28 and 2026-08-04 expiries after seeing that they are missing;
3. silently substitute a source with materially incomplete common-period coverage;
4. synthesize missing option prices or call them observed;
5. calculate TT-03/OTM350 P&L and then choose whichever source produces the preferable result.

Accordingly, Phase 51-1 terminates before OOS P&L.

## Required condition to resume

Resume only after a full-coverage, auditable 1-minute option source is available for the frozen 2026-04-21 through 2026-08-04 window, including the 2026-07-28 and 2026-08-04 weekly expiry blocks.

The replacement must pass the already-registered source-quality and common-period validation gates before any strategy P&L is inspected.

## Phase disposition

- 51-0 registry/data freeze: PASS
- 51-1 cost/data acquisition and source gates: **STOP — DATA AVAILABILITY**
- 51-2 bid/ask/liquidity model: NOT STARTED
- 51-3 capacity/slippage stress: NOT STARTED
- 51-4 fresh OOS replay: NOT STARTED
- 51-5 inference/robustness: NOT STARTED
- 51-6 manuscript/closeout: NOT STARTED

No Phase-51 strategy has been promoted.
