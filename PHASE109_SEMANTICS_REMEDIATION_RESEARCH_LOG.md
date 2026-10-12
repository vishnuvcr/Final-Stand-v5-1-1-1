# Phase 109 semantic remediation research log

## 2026-10-12 — Source audit
- Read current Phase 109 plan, status, research/error/chat logs, evaluator/workflow, shard summary/progress and source-feasibility reports before editing.
- Parent evaluator run [38216687089](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38216687089) completed successfully, and its automatic continuation [run 38219270449](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38219270449) was observed in progress during resume.
- The latest parent v1 published checkpoint is two completed ranges: 4,000 configurations, 96,000 cost rows, 590,000 remaining. That is workflow progress, not a profitability conclusion.
- Static review discovered name-substring fallback, invalid cross-asset confirmation semantics, undefined target state for realised-volatility regimes, EMA slope aliasing and lack of a crossing condition for EMA crossover.
- Opened an isolated branch so the parent workflow and published checkpoint remain preserved.
- V2 exact allowlist, semantic tests and engine-version cursor reset are implemented; actual Actions execution and empirical metrics are not yet verified.
- Transaction-cost assumptions remain 24 scenarios; OHLC fills are execution proxies; no strategy is promoted.

## 2026-10-12 — Semantic test pass and cache-gated restart

- Automated semantic test run [38221129326](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221129326) passed 26/26 tests (offline Phase 109 test suite).
- The first corrected v2 evaluator run [38221168260](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221168260) resolved its cursor to 0 but stopped before loading/evaluating strategies because the sibling branch could not restore the parent's private Actions cache: `Private NSE data cache is missing`. This is not a performance result.
- Corrected the branch-local source acquisition workflow to rebuild/cache official NSE/index/VIX/Dhan features once, publish aggregate reports only, and dispatch the evaluator after the cache-producing job ends and source gates pass. Acquisition run [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) is the current source gate.
- Continue only with the bounded evaluator if exact-option rows, historical lot sizes and nonempty official index/VIX context pass; otherwise preserve a blocked decision. No strategy promoted.

## 2026-10-12 — Risk-profile parser correction
- Found an additional variable-application defect in the stop/target parser while reviewing the registered risk grid. Fixed parsing for `STOP_10/20/30PCT`, `TARGET_10/20/30PCT` and combined profiles using `parse_risk_profile()`.
- Added a regression test for stop-only, target-only, combined and no-barrier configurations. Updated test workflow run [38221764332](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221764332) is queued at log time; no PASS claim yet.
- The source acquisition remains in progress in [run 38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273). No v2 configuration P&L has been scored.

## 2026-10-12 08:08 UTC — Corrected semantic tests passed
- [Run 38221764332](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221764332) passed **27/27** offline tests, including stop/target percentage parsing. This is code verification, not empirical profitability evidence.
- The v2 evaluator remains pending usable source cache: acquisition run [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) is still in progress. No v2 returns have been generated.

## 2026-10-12 08:31 UTC — Chain-feature throughput correction

- Reviewed the remediation plan/status/error/chat logs, current evaluator implementation, and active Actions runs before editing.
- Identified duplicated aggregate_chain_features work inside the per-configuration loop. Replaced it with a shard-start precomputation for the supported NIFTY and BANKNIFTY feature series; each configuration reuses the same point-in-time aggregated feature mapping.
- Added a regression test for one aggregation call per supported symbol. Workflow [38224068522](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38224068522) passed 29/29 offline tests.
- Acquisition workflow [38221333273](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38221333273) completed NSE options acquisition, Dhan rolling-options acquisition and index futures extraction; IV/Greeks is the active step, with index/VIX context and reconciliation still pending.
- The current v2 grid has not yet been empirically scored. No strategy results are inferred from a running job or registered configuration count.

## 2026-10-12 08:48 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v2-semantics processed cursor [0,2,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 2,000; remaining 170,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 08:50 UTC — Paytm Money / NSE cost-source recheck

- Checked Paytm Money's official F&O FAQ: ₹10 per unique order that gets executed. Registered cases remain ₹10/₹15/₹20 per order; 2 executed orders generate twice the per-order brokerage in the round-trip fee model. The user's individual contract note/add-ons remain unverified.
- Checked NSE's current official STT table: options-sale STT is 0.15% from 2026-04-01 (0.10% through 2026-03-31). Checked NSE Circular FA73061: equity-options exchange transaction outflow effective 2026-03-01 is ₹3,552 per crore plus ₹0.01 per crore IPFT; model stores these separately.
- Added a regression test for pre/post-March exchange charges, pre/post-April STT, and two-order brokerage. Test runs [38225975745](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225975745) passed 33 tests and [38226082378](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226082378) passed 34 tests after the result-filename isolation test was added.
- Adjusted displayed rate-field precision only; no fee arithmetic or resulting P&L values were altered. Full model fees remain under all 24 brokerage/slippage/fee-stress cases.
- Official sources: [Paytm Money F&O FAQ](https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web), [NSE STT table](https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax), [NSE Circular FA73061](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf), and [NSE levies guide](https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies).

## 2026-10-12 08:59 UTC — Special-session archive probes and v4 gate

- The refreshed NSE index history has 748 unique observations per series across 2023-10-03–2026-10-08. This is over 90% of weekdays in the registered window.
- Calendar comparison found five observed NIFTY 50 sessions without an option archive in the weekday-only request table: 2023-11-12, 2024-01-20, 2024-05-18, 2025-02-01 and 2026-02-01. Changed the acquisition code to include observed NIFTY 50 session dates that fall outside Monday–Friday, and added a network-free test for weekend session discovery.
- Added engine v4, which starts a new cursor and a unique v4_session_coverage results filename. v4 blocks scoring unless the official VIX/index history meets the 90% threshold and any remaining option/index session gaps are explicitly attempted and bounded.
- Latest full test workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed 38 tests. The previous v3 evaluator [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004) is diagnostic only.
- The updated source workflow [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) is queued behind run [38225253211](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38225253211); the latest v4 evaluator workflow [38226876860](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876860) remains pending. No v4 shard result or promotion is claimed.

## 2026-10-12 09:03 UTC — Official context coverage passes

- The refreshed public context summary reports 748 unique valid dates each for India VIX, NIFTY 50 and NIFTY BANK, against a required 711 dates (90% of 789 weekdays). There are zero failed chunk-series calls, zero duplicate date rows and zero invalid/missing OHLC rows.
- Calendar reconciliation reports 743 valid options-archive dates, all with NIFTY 50 observations; five observed NIFTY 50 sessions lack valid option archives. Those sessions remain unavailable for option trade replay and are not imputed.
- This clears the historical context-density gate, but does not validate strategy profitability. The evaluator has advanced to `phase109-eod-engine-v4-session-coverage`, requiring a fresh cursor. Earlier v1/v2/v3 result rows cannot be reused as v4.
- Regression workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed. Updated source workflow [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) is active; v4 evaluator run [38227220343](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227220343) is pending behind older run [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004).

## 2026-10-12 09:04 UTC — Source-order correctness and current workflow state

- Reviewed the remediation plan, live status, research/error/chat logs, v4 evaluator and workflow before changing workflow orchestration.
- Corrected the source workflow order: official India VIX/NIFTY 50/NIFTY BANK context and its observed-session calendar now refresh before NSE option archive probing. This ensures special weekend sessions discovered by the current run are available to the archive request builder, instead of relying on a possibly stale committed CSV.
- The archive request includes weekdays plus observed official NIFTY 50 dates outside weekdays. Any unavailable archive remains an explicit no-archive status; no options rows are imputed.
- Replaced stale-run concurrency settings with cancel-in-progress on source/evaluator workflows. Obsolete source run [38226910940](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226910940) was cancelled; corrected source run [38227481409](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227481409) is active. V4 evaluator run [38227487048](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38227487048) is pending behind old diagnostic v3 run [38226206004](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226206004), which had processed 800/2,000 configs at the most recent logs.
- Latest complete regression workflow [38226876842](https://github.com/vishnuvcr/Final-Stand-v5-1-1-1/actions/runs/38226876842) passed 38/38 tests. No v4 shard or strategy promotion is yet verified.

## 2026-10-12 09:39 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [0,2,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 2,000; remaining 170,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 10:35 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [2,000,4,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 4,000; remaining 168,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 11:57 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [4,000,6,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 6,000; remaining 166,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 13:13 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [6,000,8,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 8,000; remaining 164,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 13:22 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [8,000,10,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 10,000; remaining 162,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 13:36 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [10,000,12,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 12,000; remaining 160,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 13:51 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [12,000,14,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 14,000; remaining 158,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 14:04 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [14,000,16,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 16,000; remaining 156,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 14:22 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [16,000,18,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 18,000; remaining 154,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 14:36 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [18,000,20,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 20,000; remaining 152,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 14:45 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [20,000,22,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 22,000; remaining 150,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 14:49 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [22,000,24,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 24,000; remaining 148,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 14:53 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [24,000,26,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 26,000; remaining 146,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 14:57 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [26,000,28,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 28,000; remaining 144,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:00 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [28,000,30,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 30,000; remaining 142,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:04 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [30,000,32,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 32,000; remaining 140,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:09 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [32,000,34,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 34,000; remaining 138,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:14 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [34,000,36,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 36,000; remaining 136,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:18 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [36,000,38,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 38,000; remaining 134,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:22 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [38,000,40,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 40,000; remaining 132,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:25 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [40,000,42,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 42,000; remaining 130,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:33 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [42,000,44,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 44,000; remaining 128,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:46 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [44,000,46,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 46,000; remaining 126,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:50 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [46,000,48,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 48,000; remaining 124,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 15:59 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [48,000,50,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 50,000; remaining 122,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:05 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [50,000,52,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 52,000; remaining 120,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:16 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [52,000,54,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 54,000; remaining 118,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:21 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [54,000,56,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 56,000; remaining 116,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:28 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [56,000,58,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 58,000; remaining 114,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:33 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [58,000,60,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 60,000; remaining 112,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:39 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [60,000,62,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 62,000; remaining 110,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:46 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [62,000,64,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 64,000; remaining 108,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 16:54 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [64,000,66,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 66,000; remaining 106,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 17:05 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [66,000,68,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 68,000; remaining 104,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 17:20 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [68,000,70,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 70,000; remaining 102,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 17:30 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [70,000,72,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 72,000; remaining 100,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 17:45 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [72,000,74,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 74,000; remaining 98,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 17:50 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [74,000,76,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 76,000; remaining 96,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 18:01 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [76,000,78,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 78,000; remaining 94,800. These remain EOD execution proxies, not verified fills.

## 2026-10-12 18:15 UTC — Corrected v2 evaluator checkpoint
- Engine phase109-eod-engine-v4-session-coverage processed cursor [78,000,80,000); attempted 2,000 configurations and emitted 48,000 cost rows.
- Cumulative attempted 80,000; remaining 92,800. These remain EOD execution proxies, not verified fills.
