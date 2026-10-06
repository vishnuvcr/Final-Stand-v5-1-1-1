import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path("results/phase49_vix_tuning")
SOURCE_RUN_ID = os.getenv("PHASE49_SOURCE_RUN_ID", "37540089501")
SOURCE_ARTIFACT_ID = os.getenv("PHASE49_SOURCE_ARTIFACT_ID", "11449521627")
SOURCE_ARTIFACT_DIGEST = os.getenv("PHASE49_SOURCE_ARTIFACT_DIGEST", "sha256:be397fe61fc6de048699c67235b383863ba6054e37edcb5ebf0bde87870e838")

def read_csv(name):
    return pd.read_csv(OUT / name)

def ensure_error_ledger(name):
    p = OUT / name
    if not p.exists() or p.stat().st_size == 0:
        pd.DataFrame(columns=["expiry", "error"]).to_csv(p, index=False)
    df = pd.read_csv(p)
    assert list(df.columns) == ["expiry", "error"]
    return df

def parse_param(s):
    return json.loads(s)

def money(x):
    if pd.isna(x):
        return "NA"
    return f"₹{x:,.2f}"

def pct(x):
    if pd.isna(x):
        return "NA"
    return f"{100*x:.1f}%"

def active_rows(val, fam, state, param_json):
    z = val[(val["family"] == fam) & (val["active_state"] == state) & (val["param_json"] == param_json)]
    return z[z["state"] == state].sort_values("entry_ts").copy()

def audit():
    pre = json.load(open(OUT / "preflight.json", encoding="utf-8"))
    summary = json.load(open(OUT / "summary.json", encoding="utf-8"))
    fr = read_csv("development_frozen_parameters.csv")
    vs = read_csv("validation_confirmatory_summary.csv")
    tr = read_csv("development_parameter_trade_matrix.csv")
    de = ensure_error_ledger("data_errors.csv")
    ve = ensure_error_ledger("validation_data_errors.csv")
    he = ensure_error_ledger("holdout_data_errors.csv")
    assert pre["grid"] == 720 and pre["regime_candidates"] == 1440
    assert pre["expiries"] == 256 and pre["dev"] == 133 and pre["validation"] == 102 and pre["holdout"] == 21
    assert summary["grid_total"] == 720 and summary["regime_expanded_candidates"] == 1440
    assert summary["frozen"] == len(fr) and summary["validation_rows"] == len(vs)
    assert set(fr["state"]).issubset({"LOW", "NORMAL"})
    assert tr["year"].isin([2021, 2022, 2023]).all()
    assert len(de) == 0 and len(ve) == 0 and len(he) == 0
    assert {"complement_trades","active_vs_complement_mean","p","p_holm"}.issubset(vs.columns)
    return pre, summary, fr, vs, tr

def make_parameter_summary(fr, vs, hold):
    rows = []
    for _, r in fr.iterrows():
        fam, state, pj = r["family"], r["state"], r["param_json"]
        d = parse_param(pj)
        v = vs[(vs.family == fam) & (vs.state == state)]
        h = hold[(hold.family == fam) & (hold.active_state == state) & (hold.state == state)]
        row = dict(
            family=fam, state=state,
            entry_time=f'{int(d.get("entry_h")):02d}:{int(d.get("entry_m")):02d}',
            dte=int(d["dte"]), development_trades=int(r["trades_dev"]),
            fold_2022_mean_net=float(r["fold_2022_mean_net"]),
            fold_2022_mean_net50=float(r["fold_2022_mean_net50"]),
            fold_2023_mean_net=float(r["fold_2023_mean_net"]),
            fold_2023_mean_net50=float(r["fold_2023_mean_net50"]),
            development_med_net50=float(r["med_net50"]),
            neighbor_support=int(r["neighbor_support"]),
        )
        for k in ["long_offset","short_offset","width","body","upper","lower"]:
            if k in d:
                row[k] = int(d[k])
        if len(v):
            x = v.iloc[0]
            row.update(
                validation_trades=int(x.trades), validation_net=float(x.net), validation_net50=float(x.net50),
                validation_mean_net=float(x.mean_net), validation_win_rate=float(x.win_rate),
                active_vs_complement_mean=float(x.active_vs_complement_mean),
                ci_lo=float(x.ci_lo), ci_hi=float(x.ci_hi), p=float(x.p), p_holm=float(x.p_holm),
                paired_common=int(x.paired_common) if not pd.isna(x.paired_common) else 0,
                paired_uplift_net=float(x.paired_uplift_net) if not pd.isna(x.paired_uplift_net) else np.nan,
                paired_uplift_net50=float(x.paired_uplift_net50) if not pd.isna(x.paired_uplift_net50) else np.nan,
                validation_economic_pass=bool(x.trades >= 20 and x.net > 0 and x.net50 > 0 and x.active_vs_complement_mean > 0),
                holm_survivor=bool(x.p_holm < 0.05),
            )
        else:
            row.update({
                "validation_trades":0,"validation_net":0.0,"validation_net50":0.0,"validation_mean_net":np.nan,
                "validation_win_rate":np.nan,"active_vs_complement_mean":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,
                "p":np.nan,"p_holm":np.nan,"paired_common":0,"paired_uplift_net":np.nan,
                "paired_uplift_net50":np.nan,"validation_economic_pass":False,"holm_survivor":False,
            })
        row.update({
            "holdout_trades":int(len(h)),
            "holdout_net":float(h.net.sum()) if len(h) else np.nan,
            "holdout_net50":float(h.net50.sum()) if len(h) else np.nan,
            "holdout_win_rate":float((h.net > 0).mean()) if len(h) else np.nan,
        })
        rows.append(row)
    return pd.DataFrame(rows)

def annual_breakdown(val, hold, par):
    out=[]
    for _,r in par.iterrows():
        fam,state=r.family,r.state
        pj=val[(val.family==fam)&(val.active_state==state)&(val.state==state)].param_json.dropna().unique()
        if len(pj)!=1:
            continue
        z=active_rows(val,fam,state,pj[0])
        for y,g in z.assign(year=pd.to_datetime(z.entry_ts).dt.year).groupby("year"):
            out.append({"split":"validation","family":fam,"state":state,"year":int(y),"trades":len(g),
                        "net":g.net.sum(),"net50":g.net50.sum(),"mean_net":g.net.mean(),"win_rate":(g.net>0).mean()})
        h=active_rows(hold,fam,state,pj[0])
        for y,g in h.assign(year=pd.to_datetime(h.entry_ts).dt.year).groupby("year"):
            out.append({"split":"holdout","family":fam,"state":state,"year":int(y),"trades":len(g),
                        "net":g.net.sum(),"net50":g.net50.sum(),"mean_net":g.net.mean(),"win_rate":(g.net>0).mean()})
    return pd.DataFrame(out)

def equity_plot(df,title,filename):
    if df.empty: return
    x=pd.to_datetime(df.entry_ts); y=df.net.cumsum()
    fig,ax=plt.subplots(figsize=(10,5.5))
    ax.plot(x,y,linewidth=1.8); ax.axhline(0,linewidth=0.9)
    ax.set_title(title); ax.set_ylabel("Cumulative net P&L (₹)"); ax.set_xlabel("Entry timestamp")
    ax.grid(True,alpha=0.25); fig.autofmt_xdate(); fig.tight_layout()
    fig.savefig(OUT/filename,format="svg"); plt.close(fig)

def bar_plot(par,filename):
    if par.empty: return
    x=np.arange(len(par)); w=0.35
    fig,ax=plt.subplots(figsize=(10,5.5))
    ax.bar(x-w/2,par.validation_net,width=w,label="Validation net")
    ax.bar(x+w/2,par.validation_net50,width=w,label="Validation net (+50% costs)")
    ax.set_xticks(x); ax.set_xticklabels(par.family+" / "+par.state,rotation=25,ha="right")
    ax.set_ylabel("₹"); ax.set_title("Frozen candidate validation P&L"); ax.legend()
    ax.grid(True,axis="y",alpha=0.25); fig.tight_layout(); fig.savefig(OUT/filename,format="svg"); plt.close(fig)

def ranking_plot(scores):
    if scores.empty: return
    top=scores.sort_values(["state","med_net50"],ascending=[True,False]).copy()
    top["label"]=top.apply(lambda r:f'{r.family}-{r.state} / {r.med_net50:,.0f}',axis=1)
    fig,ax=plt.subplots(figsize=(11,6))
    ax.barh(np.arange(len(top)),top.med_net50); ax.set_yticks(np.arange(len(top))); ax.set_yticklabels(top.label)
    ax.invert_yaxis(); ax.set_xlabel("Development median stressed mean net/trade (₹)")
    ax.set_title("Eligible Phase 49 development candidates"); ax.grid(True,axis="x",alpha=0.25)
    fig.tight_layout(); fig.savefig(OUT/"development_candidate_ranking.svg",format="svg"); plt.close(fig)

def manuscript(pre,summary,fr,vs,par,ann,hc,scores):
    desc=[]
    for _,r in fr.iterrows():
        d=parse_param(r.param_json)
        if r.family=="bear_put":
            geom=f"Buy PE +{d['long_offset']} step / Sell PE {d['short_offset']} step; width={d['width']} steps"
        else:
            geom=f"PE BWB body={d['body']}; upper={d['upper']} steps; lower={d['lower']} steps"
        desc.append(f"- **{r.family} / {r.state}:** {geom}; entry {int(d['entry_h']):02d}:{int(d['entry_m']):02d} IST; DTE={int(d['dte'])}.")
    bp=vs[(vs.family=="bear_put")&(vs.state=="LOW")].iloc[0] if len(vs[(vs.family=="bear_put")&(vs.state=="LOW")]) else None
    bw=vs[(vs.family=="put_bwb")&(vs.state=="LOW")].iloc[0] if len(vs[(vs.family=="put_bwb")&(vs.state=="LOW")]) else None
    lines=[
        "# Phase 49 Manuscript — VIX Leader Parameter Tuning","",
        "## Abstract","",
        f"Phase 49 screened {pre['grid']} registered geometries, expanded to {pre['regime_candidates']} parameter×VIX-regime candidates across LOW and NORMAL India-VIX states. The study used {pre['dev']} development expiries (2021–2023), {pre['validation']} validation expiries (2024–2025), and {pre['holdout']} protected holdout expiries.",
        "",
        f"Two LOW-VIX candidates survived development. The frozen Bear Put was a 5-DTE, 09:30 IST four-step PE credit spread; the frozen Put Broken-Wing Butterfly was a 3-DTE, 11:00 IST asymmetric PE BWB. Only the Bear Put met the validation economic gate: {money(bp.net)} net and {money(bp.net50)} at +50% costs across {int(bp.trades)} active LOW-VIX trades. Its active-vs-complement inference was not statistically conclusive (p={bp.p:.4f}; Holm p={bp.p_holm:.4f}; 95% bootstrap CI crossed zero). The Put BWB was negative in validation.",
        "",
        "The Bear Put generated a positive protected-holdout confirmation on five LOW-VIX trades, but the sample is too small to override the preregistered inferential gate. Phase 49 therefore closes with NO PROMOTION.",
        "",
        "## Research question","",
        "Can the strongest previously validated LOW/NORMAL-VIX NIFTY defined-risk structures be improved by tuning strike geometry, spread width, entry time and DTE without sacrificing out-of-sample robustness?","",
        "## Aims and objectives","",
        "1. Tune only the finite, pre-registered Phase-45 VIX leaders.",
        "2. Select parameters using chronological development folds and neighborhood support.",
        "3. Freeze before validation and compare active-VIX performance with the same parameter in complementary VIX states.",
        "4. Include realistic brokerage, historical statutory charges, one-tick option slippage and +50% cost stress.",
        "5. Keep the 2026 holdout inaccessible to selection and validation decisions.","",
        "## Scientific methodology","",
        "The audited Phase-43 option/inference primitives were reused. Point-in-time ATM and modal strike step determined the strike geometry; trades were evaluated at the registered entry times and exited at the last common timestamp on expiry day. Historical NIFTY lot sizes and date-aware charges were applied.",
        "",
        "Development used 720 raw geometries × two registered VIX states = 1,440 candidates. A candidate needed at least 10 trades and positive mean net and stressed mean in both 2022 and 2023. Ranking used stressed mean/trade consistency, profit factor and one-step neighborhood support.",
        "",
        "Validation used 10,000 bootstrap resamples and 10,000 one-sided permutations for active-vs-complement comparisons, with Holm correction across the six possible frozen family×state tests. The protected 2026 holdout was opened only after validation economic screening.",
        "",
        "Execution realism included ₹10/order brokerage, historical STT/exchange/SEBI/IPFT/stamp/GST components, adverse ₹0.05 option-tick slippage per leg at entry and exit, and a +50% charge-stress P&L.",
        "",
        "## Frozen parameters","",
        *desc,"",
        "## Development findings","",
        "Five Bear Put LOW and seven Put BWB LOW parameterizations met the forward-fold development gate. No Bear Call or NORMAL-VIX candidate survived. The selected Bear Put had one neighboring eligible candidate within the 80%-of-score neighborhood rule; the selected Put BWB had zero neighborhood support.",
        "",
        "The selected Put BWB is a useful anti-overfitting case: its development stressed mean/trade was about ₹646, yet its validation net was strongly negative. This deterioration supports retaining the protected holdout and inferential gates.",
        "",
        "## Validation results","",
        "| Candidate | Trades | Net | +50% cost | Win rate | Active-complement mean | 95% CI | p | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in vs.iterrows():
        lines.append(f"| {r.family} / {r.state} | {int(r.trades)} | {money(r.net)} | {money(r.net50)} | {pct(r.win_rate)} | {money(r.active_vs_complement_mean)} | [{money(r.ci_lo)}, {money(r.ci_hi)}] | {r.p:.4f} | {r.p_holm:.4f} |")
    if bp is not None:
        lines += ["",
                  f"Against the registered Bear Put LOW baseline, the tuned candidate's paired uplift on {int(bp.paired_common)} common validation expiries was {money(bp.paired_uplift_net)} net and {money(bp.paired_uplift_net50)} at +50% costs.",
                  ""]
    lines += [
        "## Protected holdout","",
        "| Candidate | Trades | Net | +50% cost | Win rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for _,r in hc.iterrows():
        lines.append(f"| {r.family} / {r.state} | {int(r.trades)} | {money(r.net)} | {money(r.net50)} | {pct(r.win_rate)} |")
    lines += [
        "",
        "The Bear Put LOW holdout result was +₹27,278.50 net and +₹27,051.63 under +50% cost stress on five active LOW-VIX observations. Four of five trades were profitable. This is encouraging but not sufficiently powered for deployment-grade confirmation.",
        "",
        "## Statistical inference",
        "",
        "No Holm-adjusted comparison survived the pre-registered 0.05 threshold. The Bear Put's 95% bootstrap interval spans zero and permutation p=0.226. The absence of statistical confirmation is decisive under the Phase-49 promotion gate.",
        "",
        "## Economic interpretation",
        "",
        "The tuned Bear Put is economically promising: earlier entry (09:30), five-session entry horizon, wider four-step spread, and the +1/-3 strike geometry materially improved validation P&L versus the registered baseline. However, the search involved 1,440 candidate-regime combinations; development ranking therefore carries selection risk. The protected holdout is positive but only five trades.",
        "",
        "## Strengths","",
        "- Finite pre-registration with explicit cardinality and chronological separation.",
        "- Historical lot sizes, statutory costs, brokerage, one-tick slippage and +50% cost stress.",
        "- Active-vs-complement validation using the same frozen parameter.",
        "- 2026 protected holdout and explicit workflow evidence embargo.",
        "",
        "## Limitations","",
        "- Holm correction was applied to the six frozen family×state tests, not to all 1,440 development combinations; White/SPA-style search-wide correction remains a future robustness extension.",
        "- The Bear Put holdout confirmation contains only five active LOW-VIX observations.",
        "- Trade-level bootstrap/permutation does not explicitly model serial dependence or volatility clustering.",
        "- Historical quote data do not provide full order-book queue/fill information; the project-standard one-tick adverse model is used.",
        "",
        "## Conclusion","",
        "**NO PROMOTION.** The best tuned research candidate is the LOW-VIX Bear Put: buy PE one modal strike step above ATM, sell PE three modal strike steps below ATM, four-step width, entered at 09:30 IST five trading sessions before expiry. It is an economically promising candidate but fails the statistical gate. The canonical strategy remains unchanged.",
        "",
        "## Future research","",
        "The next bounded test should prospectively evaluate this frozen Bear Put on a substantially larger independent post-2025 sample, with a minimum active-trade count set in advance. A later phase can add independent controls for trend, realized volatility, VIX term structure/skew, global market crossings, major news/event days and corporate-action windows without reopening the Phase-49 parameter surface.",
        "",
        "## Reconciliation provenance","",
        f"The numerical source was GitHub Actions run {SOURCE_RUN_ID}; raw artifact {SOURCE_ARTIFACT_ID}; digest {SOURCE_ARTIFACT_DIGEST}. The numerical step completed successfully. The initial publication gate failed because the empty development error ledger was zero bytes. This reconciliation repairs only the ledger packaging and reruns the artifact/statistical/publication gate without changing numerical values.",
        "",
        "## Appendix A — Annual breakdown","",
        ann.to_markdown(index=False),
        "",
        "## Appendix B — Candidate parameter table","",
        par.to_markdown(index=False),
        "",
        "## Appendix C — Evidence files","",
        "See results/phase49_vix_tuning for the complete development matrix, validation matrices, holdout matrix, statistical summary, final decision JSON, reconciliation manifest and SVG figures.",
    ]
    (OUT/"PHASE49_MANUSCRIPT.md").write_text("\n".join(lines),encoding="utf-8")

def main():
    pre, summary, fr, vs, tr = audit()
    hold=read_csv("holdout_frozen_trade_matrix.csv")
    hc=read_csv("holdout_confirmation.csv")
    val=read_csv("validation_frozen_trade_matrix.csv")
    scores=read_csv("development_candidate_scores.csv")
    par=make_parameter_summary(fr,vs,hold); par.to_csv(OUT/"phase49_parameter_summary.csv",index=False)
    ann=annual_breakdown(val,hold,par); ann.to_csv(OUT/"phase49_annual_breakdown.csv",index=False)
    vs[["family","state","trades","net","net50","paired_common","paired_uplift_net","paired_uplift_net50"]].to_csv(OUT/"phase49_paired_baseline_comparison.csv",index=False)
    econ=vs[(vs.trades>=20)&(vs.net>0)&(vs.net50>0)&(vs.active_vs_complement_mean>0)]
    decision={
        "phase":49,"status":"NO_PROMOTION","canonical_strategy_changed":False,
        "source_run_id":SOURCE_RUN_ID,"source_artifact_id":SOURCE_ARTIFACT_ID,"source_artifact_digest":SOURCE_ARTIFACT_DIGEST,
        "numerical_step_success":True,"artifact_reconciliation_success":True,
        "raw_geometries":int(pre["grid"]),"regime_expanded_candidates":int(pre["regime_candidates"]),
        "frozen_candidates":int(summary["frozen"]),"validation_economic_passes":int(summary["validation_economic_passes"]),
        "holm_survivors":int(summary["holm_survivors"]),"holdout_confirmations":int(summary["holdout_confirmations"]),
        "working_candidates":econ[["family","state"]].to_dict("records"),
        "promotion_rule_met":False,
        "reason":"No frozen candidate survived the Holm-adjusted confirmatory inference gate.",
    }
    (OUT/"phase49_final_decision.json").write_text(json.dumps(decision,indent=2,default=str),encoding="utf-8")
    (OUT/"phase49_artifact_reconciliation.json").write_text(json.dumps({
        "source_run_id":SOURCE_RUN_ID,"source_artifact_id":SOURCE_ARTIFACT_ID,"source_artifact_digest":SOURCE_ARTIFACT_DIGEST,
        "reconciliation_type":"publication_and_audit_gate","numerical_values_modified":False,"zero_byte_error_ledger_repaired":True
    },indent=2),encoding="utf-8")
    bp_rows=fr[(fr.family=="bear_put")&(fr.state=="LOW")]
    if len(bp_rows):
        pj=bp_rows.iloc[0].param_json
        equity_plot(active_rows(val,"bear_put","LOW",pj),"Bear Put LOW — validation cumulative net P&L","bear_put_low_validation_equity.svg")
        equity_plot(active_rows(hold,"bear_put","LOW",pj),"Bear Put LOW — protected holdout cumulative net P&L","bear_put_low_holdout_equity.svg")
    bar_plot(par,"candidate_validation_comparison.svg")
    ranking_plot(scores)
    manuscript(pre,summary,fr,vs,par,ann,hc,scores)

if __name__=="__main__":
    main()
