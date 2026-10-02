# Research Log

## 2026-10-02 — Research restart
- Restarted because the prior implementation did not exactly match the latest strategy definition.
- Created phase-1-restart-strategy-v2.
- Prior global n=6..15 x Call/Put results are superseded.

## 2026-10-02 — Phase 2 execution
- Created phase-2-restart-v2.
- Successful primary run: 196 eligible trades.
- Net win rate 37.24%; mean net -₹303.48; total net -₹59,481.78.
- Direction: BEARISH 19 trades, BULLISH 177 trades.
- n distribution: 6=188, 7=6, 8=1, 15=1.

## 2026-10-02 — Phase 3 statistical analysis
- Created phase-3-restart-statistics.
- First statistical workflow failed during grouped aggregation; implementation was corrected to explicit group loops and rerun successfully.
- Overall profit factor: 0.719.
- Max drawdown on cumulative trade-order net P&L: -₹80,224.28.
- Bootstrap 95% CI for mean net P&L: -₹702.98 to ₹86.52.
- Bootstrap 95% CI for win rate: 30.61% to 44.39%.
- Yearly net P&L: 2021 -₹7,813.05; 2022 -₹1,314.54; 2023 -₹9,536.07; 2024 -₹4,283.23; 2025 -₹47,088.19; 2026 +₹10,553.30 through Sep-2026.
- Target exits: 73, all profitable in the sample; expiry exits: 123, all losses in the sample.
- Selected n was 6 on 188/196 trades.

## 2026-10-02 — Phase 3 completion
- Statistical artifacts persisted under results/restarted_v2/phase3/.
- Workflow restored to manual-only after autonomous execution.
- Next phase: robustness and sensitivity.

## 2026-10-02 — Phase 4 retry trigger
- Corrected a literal newline syntax error in the parameterized backtest before rerunning robustness scenarios.

## 2026-10-03 — Phase 4 completion
- GitHub Actions run 37048711849 completed all 15 planned robustness scenarios successfully.
- Verified scenario results were reconstructed from the successful runner log because the initial persistence push encountered a concurrent remote update.
- Persisted verified results in results/restarted_v2/phase4/VERIFIED_PHASE4_SUMMARY.md.
- Restored Phase 4 workflow to manual-only operation after execution.
- Primary 95%/1-tick/10:00/4-DTE result remained -₹59,481.78 total net P&L across 196 trades.
- DTE=3 sensitivity produced +₹2,603.15 in 197 trades; retained only as a robustness observation, not as a changed primary specification.

## 2026-10-03 — Phase 6 fixed OTM15 restart
- Prior v2 research is superseded for this restart.
- Locked new Stage 1 selector: X_call = OTM17 CE + OTM16 CE - OTM15 CE; X_put = OTM17 PE + OTM16 PE - OTM15 PE.
- Direction: X_call > X_put -> BEARISH; X_call < X_put -> BULLISH; equality -> no trade.
- Position is fixed OTM15/16/17; no high-n threshold or n optimization.
- Target remains T = 0.90 * selected X * lot quantity; otherwise expiry exit.
- Created Phase 7 primary backtest implementation and manual workflow.

## Phase 7 result — fixed OTM15 primary backtest
- Completed successfully on GitHub Actions.
- 195 completed trades; 8 expiries excluded/missing.
- Net P&L: -₹39,626.40; mean -₹203.21/trade; median -₹237.86/trade.
- Win rate after modeled costs: 25.13%.
- Gross P&L: -₹24,976.75; modeled costs: ₹14,649.65.
- Target exits: 49/195 (25.13%); expiry exits: 146/195 (74.87%).
- Target exits had 100% positive net P&L; expiry exits had 0% positive net P&L.
- Direction: 191 bullish/put trades, 4 bearish/call trades.
- This result is the locked primary Phase 7 result for statistical analysis; previous v2 results remain superseded.

## Phase 8 started
- Primary Phase 7 result locked.
- Statistical analysis includes profit factor, drawdown, trade-level dispersion, bootstrap confidence intervals, yearly results, direction decomposition and exit decomposition.

## Phase 8 execution note
- First push-triggered Phase 8 run was skipped because the workflow event/marker did not execute the job. A second explicit marker commit is being used.

## Phase 9 started
- Robustness will test target fraction (0.80/0.90/1.00), adverse slippage (0/1/2 ticks), entry time (09:45/10:00/10:15), DTE (3/4/5 sessions), and brokerage (0/10/20 per order).
- Primary remains fixed at 0.90 target, 1 tick slippage, 10:00, 4 DTE, ₹10/order.


## 2026-10-03 — AlgoTest contradiction audit
- Two user-supplied AlgoTest PDFs were inspected visually, including strategy configuration and result/report pages.
- AlgoTest call report shows 218 trades, overall profit ₹96,307.25, 99.08% win rate, entry 09:35, exit 15:14, 4 trading days before weekly expiry, 0% slippage, and quantity 65 in the displayed 2021 rows.
- AlgoTest put report shows 218 trades, overall profit ₹191,298.25, 98.62% win rate, entry 09:35, exit 15:14, 4 trading days before weekly expiry, 0% slippage, and quantity 65 in the displayed 2021 rows.
- The uploaded configurations visibly contain four legs. The call report uses buy OTM15 CE, sell OTM16 CE, and two sell OTM17 CE legs. The put report uses buy OTM15 PE, sell OTM16 PE, sell OTM17 CE, and an additional sell OTM17 PE leg. These are not the locked three-leg research structures.
- The AlgoTest reports also use fixed-time expiry-day exit rather than the locked target/expiry rule and do not visibly enable brokerage/taxes/slippage for the reported P&L.
- Therefore the headline AlgoTest results are not an apples-to-apples replication of the locked research strategy. An exact configuration-replication audit was inserted as Phase 9A before interpreting the discrepancy or finalizing robustness conclusions.


## 2026-10-03 — Corrected AlgoTest uploads
- User clarified that the previous two AlgoTest PDFs were the wrong files.
- The newly uploaded reports were inspected and are materially different from the prior mistaken uploads.
- Corrected put report: 3 legs — Buy OTM15 PE, Sell OTM16 PE, Sell OTM17 PE; entry 09:35; exit 15:14; 4 trading days before weekly expiry; 218 trades; displayed overall profit ₹138,258.25 and win rate 99.54%.
- Corrected call report: 3 legs — Buy OTM15 CE, Sell OTM16 CE, Sell OTM17 CE; entry 09:35; exit 15:14; 4 trading days before weekly expiry; 218 trades; displayed overall profit ₹43,267.25 and win rate 99.08%.
- These corrected reports are structurally aligned with the three-leg fixed OTM15/16/17 call and put components, but they still do not by themselves reproduce the locked research strategy because they independently backtest each side, use 09:35 entry and 15:14 expiry-day exit, and show target/stop-loss disabled. The research strategy additionally uses the X_call-versus-X_put selector, 10:00 entry, target T=0.90*X*lot with expiry fallback, and modeled execution costs.
- The earlier Phase 9A interpretation based on the mistaken files is superseded and must not be used as evidence.


## 2026-10-03 — Phase 9B execution
- Added `research/reproduce_algotest_components.py` to reproduce the corrected AlgoTest three-leg call and put component configurations on the validated HF overlap sample.
- Locked replication settings: 09:35 IST entry, 4 trading sessions before expiry, 15:14 IST expiry-day exit, OTM15/16/17, fixed quantity 65, zero modeled slippage, zero brokerage, and no target/stop-loss logic.
- The workflow will compare the overlap-period gross P&L with the user-supplied AlgoTest headline results while preserving the known date-coverage difference.

[RUN_PHASE9B]


## 2026-10-03 — Critical strike-mapping correction
- The Phase 9B component reproduction produced strongly negative call/put results instead of matching the user-supplied AlgoTest reports. Inspection of the reproduced strikes showed the implementation had selected the 15th/16th/17th available quoted strikes rather than exact OTM15/16/17 strike levels.
- Example: on 2021-05-28, the implementation selected call strikes 16200/16400/16500, skipping the exact 16250/16300 ladder levels. The AlgoTest screenshot semantics use consecutive OTM strikes on the ₹50 NIFTY strike ladder.
- NSE's documented NIFTY strike scheme is ₹50 for weekly/monthly contracts; therefore exact OTM15/16/17 must be ATM±750/800/850 respectively. citeturn166378search0turn166378search18
- This is a critical implementation error. Initial Phase 7/8/9 numeric results are superseded and must not be interpreted as evidence for the strategy.
- New Phase 7B repair branch created; corrected primary and corrected AlgoTest component reproduction will be rerun before any robustness or final conclusion.


## 2026-10-03 — Phase 7B corrected primary execution
- Corrected OTM mapping is now exact ATM±15/16/17 strike intervals using the NIFTY ₹50 strike ladder.
- The original Phase 7/8/9 results are formally superseded.
- Primary settings remain 10:00 IST, 4 trading sessions before expiry, 0.90×X target, one adverse tick per leg, date-aware lot sizes and ₹10/order brokerage.

[RUN_PHASE7B]


## 2026-10-03 — Phase 9C corrected AlgoTest reproduction
- Rerun the two corrected AlgoTest component strategies using exact NIFTY OTM15/16/17 strike distances on the ₹50 strike ladder.
- Settings: 09:35 IST entry, 4 trading sessions before expiry, fixed 15:14 IST expiry-day exit, fixed quantity 65, zero slippage, zero brokerage, no target/stop-loss.
- Compare the validated HF overlap period with the user-supplied full-period AlgoTest headline results.

[RUN_PHASE9C]


## 2026-10-03 — Critical P&L sign correction
- The corrected strike mapping still produced near-total losses, which triggered a manual leg-by-leg check against the uploaded AlgoTest report.
- The check exposed a second critical implementation error: the backtest P&L formula had inverted the long and short leg signs.
- Correct convention: long OTM15 contributes `exit - entry`; short OTM16/17 contribute `entry - exit`.
- The first uploaded AlgoTest call trade confirms this exactly: buy 1.90 -> 0.05 = -120.25; sell 1.70 -> 0.05 = +107.25; sell 1.80 -> 0.05 = +113.75; total = +100.75 for quantity 65.
- Therefore Phase 7B, Phase 9B and Phase 9C numerical outputs are superseded. A full corrected primary rerun is required before any further robustness or inference.


## 2026-10-03 — Phase 7C corrected P&L primary execution
- Exact strike mapping and long/short P&L signs are now corrected.
- All previous Phase 7/8/9/9A numerical results are superseded pending this rerun.

[RUN_PHASE7C]


## 2026-10-03 — Phase 9E corrected robustness execution
- Phase 9 robustness is restarted from the corrected strike mapping and corrected long/short P&L accounting.
- The 15 pre-registered scenarios are unchanged: target fraction 0.80/0.90/1.00 × slippage 0/1/2 ticks; entry 09:45/10:15; DTE 3/5; brokerage ₹0/₹20 per order.
- All earlier Phase 9 numerical outputs are superseded.

[RUN_PHASE9E]


## 2026-10-03 — Phase 8B corrected statistical analysis
- Statistical analysis is rerun from the corrected Phase 7C primary trade ledger.
- Prior Phase 8 results are superseded because the earlier primary used incorrect strike mapping and inverted P&L signs.

[RUN_PHASE8B]


## 2026-10-03 — Phase 7D fee audit
- Audited the transaction/IPFT cost model against NSE circulars. STT rates are aligned with NSE's published rates; option transaction/IPFT components were corrected for the 2024-10 and 2026-03 changes.
- The pre-2024-10 transaction assumption remains a conservative project assumption because broker-level pass-through can differ by historical exchange slab.
- Rerun the corrected primary so reported net P&L uses the audited charge model.

[RUN_PHASE7D]


## 2026-10-03 — Phase 9F fee-audited robustness
- Re-run the pre-registered 15 robustness scenarios from the fee-audited primary code so sensitivity and primary use the same cost model.
- No strategy parameters are changed by this audit.

[RUN_PHASE9F]
