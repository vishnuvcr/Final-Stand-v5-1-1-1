"""Synthesize accepted Phase 95-99 evidence into a finite manuscript."""
from pathlib import Path
import csv,json,html,datetime,shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"results/phase100"
P95=ROOT/"evidence/phase95/results/phase95"
def readcsv(path):
 if not path.exists(): return []
 with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def readjson(path):
 try:return json.loads(path.read_text(encoding="utf-8"))
 except Exception:return {}
def fnum(x):
 try:return float(x)
 except Exception:return float("nan")
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 p95=P95 if (P95/"model_metrics.csv").exists() else ROOT/"results/phase95"
 metrics=readcsv(p95/"model_metrics.csv")
 ok=[r for r in metrics if r.get("status","OK")=="OK"]
 close=[r for r in ok if r.get("target")=="Close"]
 gains=[r for r in close if fnum(r.get("mae_improvement_vs_persistence"))>0]
 ci=[r for r in close if fnum(r.get("bootstrap_ci_low"))>0]
 sig=[r for r in close if fnum(r.get("mae_improvement_vs_persistence"))>0 and fnum(r.get("bootstrap_ci_low"))>0 and fnum(r.get("holm_p_value"))<.05]
 p96=[r for r in readcsv(ROOT/"results/phase96/metrics.csv") if r.get("strategy")!="buy_hold"]
 p97=readjson(ROOT/"results/phase97/summary.json");p98=readjson(ROOT/"results/phase98/summary.json");p99=readjson(ROOT/"results/phase99/summary.json")
 claim_rows=readcsv(p95/"paper_claim_status.csv")
 reconcile_note=("The latest Phase 95 paper-claim reconciliation completed; the ledger is included in this supplement." if claim_rows else "Phase 95 paper-claim reconciliation has not completed; source-specific statuses remain provisional.")
 if claim_rows: shutil.copy2(p95/"paper_claim_status.csv",OUT/"phase95_paper_claim_status.csv")
 paper_rows=[
 ("U01","Bansal et al. — multi-regressor stock-price forecasts","PARTIAL","Common NIFTY model-family screen; source universe/protocol not fully matched."),
 ("U02","Sherasiya — RF/XGBoost/LSTM options signals","DATA_BLOCKED","No point-in-time exact-contract training/label matrix; no option P&L."),
 ("U03","Bumrah & Budhani — NIFTY ANN with FX/FII features","PARTIAL","Common price-only screen; USD/INR and FII gross-flow inputs not matched."),
 ("U04","Sain & Singh — multi-window NIFTY model comparison","PARTIAL","Common daily model-family screen; source-specific protocol and feature ablations not fully matched."),
 ("U05","Atheetha et al. — monthly trend/seasonality options procedure","PARTIAL_DATA_BLOCKED","Rule extracted; exact-contract premiums/liquidity/early exits not available for historical replay."),
 ("U06","Naik & Inamdar — sentiment/news, LSTM and market features","DATA_BLOCKED","Point-in-time BERT/news, FII/DII, VIX and PCR modalities not reproduced in Phase 95."),
 ("U07","Chatterjee et al. — options payoff structures","PARTIAL_ANALYTICAL","13 payoff structures checked algebraically; historical trading P&L blocked; put-butterfly source ambiguity."),
 ("U08","Fathali et al. — NIFTY forecasting","PARTIAL","Common one-step screen does not recreate source sample/metric claim."),
 ("U09","Deep-learning NIFTY model families/hybrids","PARTIAL","Common-data family screen; source dataset/features/settings not matched."),
 ("U10","Moving-average NIFTY paper","PARTIAL","SMA/EMA sensitivity screen run; source-specific rules and statistical inference incomplete."),
 ("U11","NIFTY RNN/LSTM/CNN forecast comparison","PARTIAL","Common-data screen, not exact source replication."),
 ("U12","MLP/backprop OHLC forecast","PARTIAL","Common-data screen; source turnover/metric construction not reproduced."),
 ("U13","LSTM/backward feature elimination and RSI","PARTIAL","Price-only common screen; source horizon/features not fully matched."),
 ("U14","CCI options study by Shaha","DATA_BLOCKED","Phase 66 had zero completed trades; Phase 98 found no new qualified exact-contract source."),
 ]
 with (OUT/"paper_status.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.writer(f);w.writerow(["paper_id","paper_or_method","final_status","evidence_and_limitation"]);w.writerows(paper_rows)
 summary={"synthesis_date":datetime.datetime.now(datetime.timezone.utc).isoformat(),"phase95":{"metrics_rows":len(metrics),"close_rows":len(close),"positive_mae_gain_rows":len(gains),"ci_above_zero_rows":len(ci),"holm_significant_positive_gain_rows":len(sig)},"phase96":{"ma_variants":len(p96),"result_status":"signal_screen_only_partial"},"phase97":p97,"phase98":p98,"phase99":p99,"phase95_claim_ledger_rows":len(claim_rows),"phase95_reconciliation_complete":bool(claim_rows),"paper_count":len(paper_rows),"strategy_promoted":False,"holdout_2026_accessed":False}
 (OUT/"phase_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
 bars=[]
 for r in p96:
  val=100*fnum(r.get("total_return"))
  if val==val:bars.append((r.get("strategy","unknown"),val))
 buy=100*1.147323544903073;width=920;left=230;rowh=30;height=100+rowh*(len(bars)+1);scale=4.0
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<rect width="100%" height="100%" fill="white"/>','<text x="20" y="28" font-size="18" font-family="Arial">Phase 96: 2020–2025 total return comparison (sensitivity proxy)</text>']
 for i,(name,val) in enumerate(bars):
  y=55+i*rowh;svg.append(f'<text x="20" y="{y+17}" font-size="12" font-family="Arial">{html.escape(name)}</text>');svg.append(f'<rect x="{left}" y="{y}" width="{max(1,val*scale):.2f}" height="20" fill="#4e79a7"/>');svg.append(f'<text x="{left+max(1,val*scale)+6:.2f}" y="{y+15}" font-size="12" font-family="Arial">{val:.1f}%</text>')
 svg.append(f'<text x="{left}" y="{height-10}" font-size="12" font-family="Arial">Buy-and-hold benchmark: {buy:.1f}% total return (same dates; not directly investable spot)</text>');svg.append('</svg>')
 (OUT/"phase96_total_return.svg").write_text("\n".join(svg),encoding="utf-8")
 table="\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |" for r in paper_rows)
 manuscript=f"""# Reproducibility of NIFTY Forecasting and Options-Strategy Claims: A Bounded Review of 14 Uploaded Papers

**Research synthesis manuscript — Phase 100**  
**Evidence status:** mixed partial replications and explicit data blockers; no strategy promoted.

## Abstract
This study evaluates whether reported NIFTY forecasting and options-strategy claims across a fixed corpus of 14 uploaded papers can be independently reproduced using a bounded, auditable program. The program separates common-data model-family screening from exact paper reproduction, analytical option-payoff verification, and executable options profitability. Phase 95 completed 132 valid model/target/window rows with no model execution failures; the close-target screen is assessed against persistence and the reconciled bootstrap/Holm gates. Phase 96 tested six operationalized SMA/EMA variants over 1,486 sessions from 2020–2025; all variants returned less than the 114.7% buy-and-hold benchmark under a generic 0.05% turnover deduction, though two had higher unadjusted Sharpe estimates and lower drawdowns. Phase 97's 13-field exact-contract ML options gate and Phase 98's CCI source gate were data-blocked. Phase 99 verified payoff algebra for 13 structures but did not run a historical options backtest. The evidence does not support promotion of a profitable options strategy; data limitations are not treated as proof that source methods fail.

## 1. Research questions
1. Which source claims can be independently regenerated from the uploaded papers and eligible data?
2. Do daily NIFTY forecast models improve on persistence on aligned chronological dates under uncertainty and multiple-comparison controls?
3. Do moving-average/seasonality rules survive an out-of-sample screen and realistic execution constraints?
4. Can ML options signals and the CCI method be replayed using point-in-time exact contracts and costed fills?
5. Which claims remain partial, inconclusive, not reproduced, or data-blocked?

## 2. Aims and objectives
Map all 14 papers to explicit implementation states; reproduce the closest defensible methods without inventing missing settings; compare against appropriate baselines; enforce chronology/leakage controls; audit uncertainty; require Paytm Money costs, spread, slippage and stress for options P&L; and publish a finite, auditable conclusion.

## 3. Literature review and source claims
The corpus spans daily stock/index regressors and neural networks, multi-window NIFTY forecasting, sentiment and macro-feature hybrids, moving-average and seasonality methods, ML options buy/sell classifiers, the CCI NIFTY-options method, and payoff illustrations for directional/spread/butterfly/volatility strategies. Author-reported high accuracy or profitability remains a source claim until source-specific target, sample, features, split, metric and execution details are independently matched. Appendix A distinguishes source claims from replication status.

## 4. Methodology
### 4.1 Source-faithful extraction
For each method the protocol records target, horizon, frequency, inputs, dates, preprocessing, split, architecture/rules, baseline and metric. Missing details produce PARTIAL, DATA_BLOCKED or NOT_IDENTIFIABLE labels, not silent substitution.

### 4.2 Daily forecast screen
Phase 95 used Yahoo Finance daily NIFTY index data from 2007-09-17 through 2025-12-31, with a fixed 2025 test block and chronological training windows. It compared model families with persistence and recorded MAE/RMSE/R²/MAPE, directional metrics, bootstrap intervals and Holm-adjusted paired tests where available. External modalities not present in the price feed—FX, FII/DII, India VIX, PCR/Greeks and point-in-time news—were not fabricated.

### 4.3 Indicator screen
Phase 96 used SMA/EMA windows (5/20, 10/50, 20/100) with 2020–2025 scoring. Signals were lagged to avoid same-close look-ahead. A 0.05% turnover deduction is a sensitivity proxy, not verified Paytm Money charges. NIFTY spot is not itself an investable instrument; this is not options P&L.

### 4.4 Options gates and payoff algebra
Phase 97 required exact-contract identity, timestamp, expiry, strike, right, IV/Greeks, point-in-time underlying features, paper-faithful labels, source provenance, quote/fill evidence and a verified cost model. Phase 98 reconciled prior CCI zero-coverage and source qualification outcomes without repeating an identical failed replay. Phase 99 tested expiry payoff arithmetic with illustrative premiums; this validates formula transcription only, not entry signals or profitability.

### 4.5 Statistical analysis
Phase 95's primary endpoint is next-session close MAE improvement versus persistence, with paired uncertainty and multiplicity controls. Phase 96 descriptive Sharpe/return values are not inferentially confirmed and should not be ranked as evidence of an edge. No 2026 holdout was accessed.

## 5. Results
### 5.1 Forecasting
Phase 95's fixed run produced 132/132 valid rows and zero model execution failures. The initial primary endpoint showed no closing-price model/window row with a statistically established positive MAE gain under the bootstrap/Holm gate. A manifest serialization defect affected the automated paper-claim reconciliation; a parser correction is under rerun, so per-paper statuses remain provisional until that run succeeds. Common-data results do not disprove source papers whose data/features/splits/metrics were not matched.

### 5.2 Moving averages
Across 1,486 sessions, buy-and-hold total return was approximately 114.7%; SMA(5,20) 52.5%, SMA(10,50) 100.9%, SMA(20,100) 80.6%, EMA(5,20) 69.3%, EMA(10,50) 91.2%, EMA(20,100) 90.4%. Maximum drawdowns were smaller for the MA variants; SMA(10,50) and EMA(10,50) had unadjusted Sharpe estimates around 1.10 and 1.01 versus 0.81 for buy-and-hold. These are descriptive index-proxy values, not inferentially confirmed or executable option returns.

### 5.3 ML options and CCI
Phase 97's gate marked all 13 required controls blocked in audited artifacts; zero models were trained and no option P&L was computed. Phase 98 passed its corrected evidence-gate workflow and found no materially improved exact-contract source; the CCI method remains data-blocked, not shown unprofitable.

### 5.4 Payoff taxonomy
Phase 99 passed unit tests for 13 structures over nine illustrative expiry-price points. It flagged U07's “Short Butterfly” put section because the described legs—long one lower-strike put, short two middle-strike puts, long one higher-strike put—produce a long-butterfly payoff. Generic premiums/strikes are arithmetic examples, not historical quotes. Historical options P&L remains blocked.

## 6. Statistical interpretation and inferences
The evidence does not establish that high forecast accuracy or profitability claims have been fully reproduced across the corpus. The daily price-only screen did not establish robust close-forecast improvement over persistence; the MA screen trades off lower drawdown/volatility for lower cumulative return and lacks inference; options strategies remain data-blocked for executable backtests. A data blocker is not a negative profitability finding. Evidence is insufficient to promote a strategy.

## 7. Discussion
Three evidence levels must remain distinct: common-data model-family screening, analytical payoff verification, and executable strategy backtesting. The first can test limited baseline claims but not recreate external-modality papers; the second validates payoff arithmetic but not market timing; the third requires exact contracts and credible fills. Conflating these levels would overstate reproducibility.

## 8. Strengths
- Fixed corpus of 14 papers and explicit method register.
- Chronological splits, persistence baseline and inference gates in the forecast screen.
- Automated tests/workflows, cached data and auditable status/error logs.
- Explicit separation of source claims, partial operationalizations, payoff algebra and executable P&L.
- Sealed 2026 holdout preserved.

## 9. Limitations
- Phase 95 is not exact replication of every source-specific dataset, sample, metric, architecture or feature set.
- Phase 96 does not fully reproduce all source-specific seasonality/timing/stop rules.
- No exact-contract source-period option quote/depth/fill matrix was available for Phase 97/98/99 historical P&L.
- The generic turnover deduction is not verified Paytm Money cost history; no options costed P&L is reported.
- Some paper leg descriptions and terminology are internally inconsistent.
- Descriptive Sharpe estimates are not statistically confirmed.
- Phase 95 paper-level claim statuses require the corrected reconciliation run.

## 10. Conclusion
The bounded program produced forecast-screen outputs, a descriptive MA/EMA index screen, a fail-closed ML-options data gate, a CCI stopping decision, and unit-tested analytical payoff formulas. It has **not** produced an independently verified profitable options strategy. No strategy is promoted. This is insufficient validated evidence—not proof that all source strategies are false or unprofitable.

## 11. Future research
1. Acquire legally authorized source-period exact-contract options data with timestamp, expiry, strike, right, bid/ask/depth, trades, lot size and point-in-time Greeks/IV.
2. Reconstruct paper-specific datasets, splits, labels and metric definitions before comparing model accuracy.
3. Verify historical Paytm Money charges and model adverse slippage/latency.
4. Re-run U05 timing/seasonality rules only after contract-level data support strike selection and early-exit triggers.
5. Revisit U02 RF/XGBoost/LSTM only after exact feature/label coverage passes the gate.
6. Use a genuinely untouched future sample after all methods and thresholds are frozen; do not reuse the sealed 2026 holdout in this synthesis.

## References and source corpus
The fixed 14 PDFs are registered as U01–U14 in Phase 94. Filenames, method mapping and original author claims remain in the Phase 94 register; missing bibliographic details are not invented.

## Appendix A — Paper-level status ledger
| ID | Paper/method family | Final status | Evidence summary |
|---|---|---|---|
__PAPER_TABLE__

## Appendix B — Reproducibility gates
- Forecast: fixed dates, persistence baseline, source metrics, bootstrap uncertainty, paired tests and multiplicity adjustment.
- Options ML: exact-contract timestamp/expiry/strike/right, point-in-time features/labels, source provenance and quote/fill model.
- CCI: do not repeat identical zero-coverage run without materially better source data.
- Payoff: source leg audit and unit tests; historical P&L separate from intrinsic payoff.
- Economic: Paytm Money brokerage/levies, spread, slippage, latency and stressed costs.
- Governance: no holdout leakage; no strategy promotion absent all gates.

## Appendix C — Supplementary files
- paper_status.csv: machine-readable paper statuses.
- phase_summary.json: machine-readable phase-level outcome summary.
- phase96_total_return.svg: descriptive Phase 96 return comparison.
- Phase 95 model metrics, data manifest, modality status, coverage and phase95_paper_claim_status.csv.
- Phase 96 daily replay and metrics; Phase 97 data gate; Phase 98 evidence gate; Phase 99 payoff grid and source ambiguity ledger.
"""
 manuscript=manuscript.replace("__PAPER_TABLE__",table)
 (OUT/"MANUSCRIPT.md").write_text(manuscript,encoding="utf-8")
 (OUT/"SUPPLEMENTARY_MATERIALS.md").write_text("""# Phase 100 Supplementary Materials

## S1. Interpretation labels
- REPRODUCED: source method/data/metrics recreated within stated tolerances.
- PARTIAL: some source components reproduced, but one or more material components differ or remain missing.
- DATA_BLOCKED: required authorized data or exact operational rules unavailable.
- INCONCLUSIVE: data and test exist but uncertainty prevents a decisive result.
- NOT_REPRODUCED: valid attempt failed to reproduce source claim under matched conditions.
- NOT_IDENTIFIABLE: source does not define a unique implementable rule.

## S2. Cost requirements
No options result is economically accepted without broker-verified brokerage, statutory levies, spread, adverse slippage, latency, margin/funding and cost stress. Paytm Money must be modeled for the actual product/holding/contract.

## S3. Holdout governance
Phase 83's 2026 holdout remains sealed. This synthesis uses only registered historical evidence and the fixed 2020–2025 indicator screen.
""",encoding="utf-8")
 required=["Abstract","Research questions","Aims and objectives","Literature review","Methodology","Statistical analysis","Results","Discussion","Strengths","Limitations","Conclusion","Future research","Appendix A","Appendix B","Appendix C"]
 missing=[x for x in required if x.lower() not in manuscript.lower()]
 (OUT/"VALIDATION_REPORT.md").write_text("# Phase 100 Manuscript Validation\n\n"+("PASS" if not missing and len(paper_rows)==14 else "FAIL")+"\n\n- Paper status rows: "+str(len(paper_rows))+"\n- Required manuscript sections: "+str(len(required))+"\n- Missing headings: "+(", ".join(missing) if missing else "none")+"\n",encoding="utf-8")
 if missing or len(paper_rows)!=14:raise SystemExit(f"validation failed: missing={missing}, paper_rows={len(paper_rows)}")
 print(f"PASS: manuscript complete; {len(paper_rows)} papers; Phase95 close rows={len(close)}")
if __name__=="__main__":main()
