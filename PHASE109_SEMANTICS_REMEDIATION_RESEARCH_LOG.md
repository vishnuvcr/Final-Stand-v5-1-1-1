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
