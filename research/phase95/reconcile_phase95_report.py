#!/usr/bin/env python3
"""Reconcile Phase 95 primary endpoint and source-claim coverage."""
import csv,json,math
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"results/phase95"
def readcsv(p):
 with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def n(r,k):
 try:return float(r.get(k,""))
 except:return float("nan")
metrics=readcsv(OUT/"model_metrics.csv"); ok=[r for r in metrics if r.get("status")=="OK"]
close=[r for r in ok if r.get("target")=="Close"]; opened=[r for r in ok if r.get("target")=="Open"]
pos=[r for r in close if n(r,"mae_improvement_vs_persistence")>0]
ci=[r for r in close if n(r,"bootstrap_ci_low")>0]
sig=[r for r in close if n(r,"mae_improvement_vs_persistence")>0 and n(r,"bootstrap_ci_low")>0 and n(r,"holm_p_value")<.05]
directions=[n(r,"directional_accuracy_pct") for r in close if math.isfinite(n(r,"directional_accuracy_pct"))]
manifest_text=(OUT/"data_manifest.json").read_text(encoding="utf-8")
# Earlier writer emitted a literal backslash-n suffix; tolerate it for compatibility.
manifest_text=manifest_text.removesuffix(chr(92)+"n")
manifest=json.loads(manifest_text)
claims=[
("U01","Five regressors vs LSTM on 12 Indian stocks; SMAPE/RMSE/R2","Common NIFTY screen only; source universe, exact dates/split and source inputs not matched.","PARTIAL_COMMON_SCREEN_ONLY"),
("U02","RF/XGBoost/LSTM options signals and reported trading metrics","No source options feature matrix, exact signals or executable options P&L in Phase 95.","DATA_GATE_PENDING"),
("U03","SVM/RBF/MLP/SLP with USD/INR and FII gross buy/sell","Price-only approximation; exogenous data and source split configurations not matched.","PARTIAL_COMMON_SCREEN_ONLY"),
("U04","5/10/20-year daily NIFTY model comparisons","Windows/families tested on common 2025 test; source ablations/tuning/protocol need matching.","PARTIAL_COMMON_SCREEN_ONLY"),
("U06","LSTM+BERT with news, FII/DII, India VIX and PCR","Historical external modalities not used; full multimodal method untested.","DATA_GATE_PENDING"),
("U08","LSTM NIFTY forecast; source-reported 83.88% accuracy","Common one-step 2025 test differs from source sample and metric; claim not recreated.","PARTIAL_COMMON_SCREEN_ONLY"),
("U09","RNN/LSTM/GRU/CNN/TCN and hybrids on source Kaggle data","Yahoo price-only data; source options/OI features and optimizer sweep not reproduced.","PARTIAL_COMMON_SCREEN_ONLY"),
("U11","RNN/LSTM/CNN forecast comparison","Common-data family screen only; source settings/data/split need matching.","PARTIAL_COMMON_SCREEN_ONLY"),
("U12","MLP/backprop next-day OHLC; source-reported 99.2152% accuracy","Approximation only; source turnover feature and scaled metric not reproduced.","PARTIAL_COMMON_SCREEN_ONLY"),
("U13","LSTM/backward-elimination LSTM, RSI14 and longer horizon","Common one-step price-only variant; source horizon/features/protocol not reproduced.","PARTIAL_COMMON_SCREEN_ONLY"),
("U05/U07","Source-described options payoff structures","Reserved for Phase 99 source extraction and eligible-contract replay with all-in costs.","QUEUED_PHASE_99"),
("U10/U14","Remaining methods in the 14-paper corpus","Queued in the registered Phase 96–100 sequence, outside Phase 95 runner.","QUEUED_LATER_PHASE")]
with (OUT/"paper_claim_status.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.writer(f);w.writerow(["paper_id","source_claim_or_method","phase95_observation","reproduction_status"]);w.writerows(claims)
lines=["# Phase 95 — Reconciled primary endpoint","", "Run reconciliation: "+datetime.now(timezone.utc).isoformat(),"",
"## Primary endpoint: next-session closing price","",
f"- Successful closing-price model/window comparisons: {len(close)}.",
f"- Positive MAE-improvement point estimates: {len(pos)}/{len(close)}.",
f"- Bootstrap 95% intervals entirely above zero: {len(ci)}/{len(close)}.",
f"- Positive gain with interval above zero and Holm-adjusted p below 0.05: {len(sig)}/{len(close)}.",
(f"- Directional accuracy range: {min(directions):.2f}%–{max(directions):.2f}%." if directions else "- Direction accuracy unavailable."),
"- In this common-data screen, no closing-price variant establishes a statistically reliable MAE improvement over last-close persistence. This does not refute the original papers: most source-specific data, targets, metrics, splits and external inputs have not been matched.","",
"| Closing model | Train years | MAE | Persistence MAE | Improvement | Bootstrap 95% CI | Holm p | Direction accuracy |",
"|---|---:|---:|---:|---:|---|---:|---:|"]
for r in sorted(close,key=lambda r:n(r,"mae_improvement_vs_persistence"),reverse=True)[:12]:
 lines.append(f"| {r['model']} | {r['train_window_years']} | {n(r,'mae'):.4f} | {n(r,'persistence_mae'):.4f} | {n(r,'mae_improvement_vs_persistence'):.4f} | [{n(r,'bootstrap_ci_low'):.4f}, {n(r,'bootstrap_ci_high'):.4f}] | {n(r,'holm_p_value'):.4g} | {n(r,'directional_accuracy_pct'):.2f}% |")
lines += ["","## Supplemental opening-price results","",f"- Successful opening-price comparisons: {len(opened)}.","- Opening-price results are a separate endpoint; the overall top-ten table across targets must not be used as the primary close result.","","## Paper claim status","","- See paper_claim_status.csv. The common-data screen is not exact source reproduction.","- U02 options claims and U06 multimodal claims remain data-gated; source payoff methods are queued for Phase 99.","","## Limitations","","- The 2025 test is not necessarily post-publication for the newest papers.","- Source datasets, metric definitions, forecast horizons, splits and external features must be matched before a claim can be called reproduced.","- High price-level R-squared is not proof of incremental forecasting skill or tradable alpha.","- Phase 95 is a forecast comparison, not an options backtest. No strategy is promoted; Phase 83's 2026 holdout remains sealed."]
(OUT/"PRIMARY_ENDPOINT_RECONCILIATION.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
p=OUT/"REPORT.md"; report=p.read_text(encoding="utf-8")
marker="## Reconciled primary endpoint"
if marker in report: report=report[:report.index(marker)].rstrip()
report += "\n\n"+marker+"\n\n"+"\n".join(lines[3:])+"\n\nSee paper_claim_status.csv for the source-by-source coverage ledger; no paper is labelled exactly reproduced by this common-data screen.\n"
p.write_text(report,encoding="utf-8")
status=("# Phase 95 Status — Daily Forecast Replication\n\n"
f"**Last reconciliation:** {datetime.now(timezone.utc).isoformat()}\n**Status:** COMPLETED — common-data screen; exact paper replication remains partial/data-gated\n"
f"**Valid metric rows:** {len(ok)}; **model failures:** {sum(r.get('status')=='MODEL_FAILED' for r in metrics)}\n"
f"**Close endpoint:** {len(pos)}/{len(close)} positive point estimates; {len(ci)} CI-above-zero; {len(sig)} Holm-significant gains\n**Strategy promotion:** NONE\n\n"
"- [Plan](PHASE95_RESEARCH_PLAN.md)\n- [Report](results/phase95/REPORT.md)\n- [Primary endpoint](results/phase95/PRIMARY_ENDPOINT_RECONCILIATION.md)\n- [Metrics](results/phase95/model_metrics.csv)\n- [Paper claim status](results/phase95/paper_claim_status.csv)\n- [Manifest](results/phase95/data_manifest.json)\n- [Error log](PHASE95_ERROR_LOG.md)\n- [Research log](PHASE95_RESEARCH_LOG.md)\n- [Chat log](PHASE95_CHAT_LOG.md)\n\nCommon-data screening is not exact source reproduction. No options P&L is calculated in Phase 95. Phase 83 holdout remains sealed.\n")
(ROOT/"PHASE95_STATUS.md").write_text(status,encoding="utf-8")
readme=ROOT/"README.md"
if readme.exists():
 t=readme.read_text(encoding="utf-8"); a="<!-- PHASE95_LATEST_STATUS_START -->"; b="<!-- PHASE95_LATEST_STATUS_END -->"
 block=(a+"\n# Current research checkpoint — Phase 95\n\n**Status: common-data forecast screen complete; exact paper replication and options strategy replay continue in registered phases. No strategy promoted.**\n\n"
 f"- Closing-price comparisons: {len(close)}; positive MAE gain {len(pos)}/{len(close)}; interval above zero {len(ci)}/{len(close)}; Holm-significant positive gains {len(sig)}/{len(close)}.\n"
 f"- Yahoo Finance ^NSEI: {manifest.get('first_date')} to {manifest.get('last_date')}; {manifest.get('rows')} observations; SHA-256 {manifest.get('sha256')}.\n"
 "- 2026 holdout accessed: no. Raw market data committed: no. Phase 95 is not options P&L.\n\n"
 "- [Phase 95 plan](PHASE95_RESEARCH_PLAN.md) · [status](PHASE95_STATUS.md) · [report](results/phase95/REPORT.md) · [primary endpoint](results/phase95/PRIMARY_ENDPOINT_RECONCILIATION.md) · [metrics](results/phase95/model_metrics.csv) · [claim ledger](results/phase95/paper_claim_status.csv) · [error log](PHASE95_ERROR_LOG.md)\n"+b)
 if a in t and b in t:
  i=t.index(a);j=t.index(b,i)+len(b);t=t[:i]+block+t[j:]
 else:t=block+"\n\n"+t
 readme.write_text(t,encoding="utf-8")
with (ROOT/"PHASE95_RESEARCH_LOG.md").open("a",encoding="utf-8") as f:
 f.write(f"\n## Primary endpoint reconciliation — {datetime.now(timezone.utc).isoformat()}\n- Close comparisons {len(close)}; positive point estimates {len(pos)}; intervals above zero {len(ci)}; Holm-significant positive gains {len(sig)}.\n- Added source-claim status ledger; no exact source replication claimed.\n- Updated Phase 95 status and README checkpoint.\n")
print(json.dumps({"status":"RECONCILED","close_rows":len(close),"positive":len(pos),"ci_above_zero":len(ci),"holm_significant":len(sig),"claim_rows":len(claims)}))
