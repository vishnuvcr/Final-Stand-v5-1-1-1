import json
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path("."); OUT=ROOT/"results/phase42_confidence_calibration"
SEL=json.load(open(OUT/"selection.json")); S=pd.read_csv(OUT/"sequential_summary.csv")
top=SEL["top3_frozen_before_holdout"]

def rnk(rank,per):
    x=S[(S["rank"]==rank)&(S["period"]==per)]
    return x.iloc[0].to_dict() if len(x) else {}

def diag_fixed(rank):
    f=OUT/f"frozen_candidate_{rank}_fixed.csv"
    if not f.exists(): return {}
    x=pd.read_csv(f); out={}
    for per in ["validation","holdout"]:
        z=x[x.split==per].copy().sort_values("override_score",ascending=False)
        z=z[np.isfinite(z.override_score)]; out[per]={}
        for frac in [.10,.20,.30]:
            n=max(1,int(np.ceil(frac*len(z)))); q=z.head(n)
            out[per][f"top_{int(frac*100)}_mean_delta"]=float(q.delta_pnl.mean())
            out[per][f"top_{int(frac*100)}_positive_share"]=float((q.delta_pnl>0).mean())
    return out

checks=[]
for rank in range(1,len(top)+1):
    v=rnk(rank,"validation"); h=rnk(rank,"holdout")
    checks.append({"rank":rank,"model":v.get("model"),"calibration":v.get("calibration"),
      "margin":v.get("margin"),"gate":v.get("gate"),
      "promotion_pass":False,"validation":v,"holdout":h,"ranking":diag_fixed(rank)})

# Add cost stress from sequential artifacts.
for c in checks:
    for per in ["validation","holdout"]:
        f=OUT/f"sequential_candidate_{c['rank']}.csv"
        if not f.exists(): continue
        t=pd.read_csv(f); t=t[t.period==per]
        ctl=pd.concat([pd.read_csv("results/phase39_data/development_control_trades_2021_2023.csv"),
                       pd.read_csv("results/phase39_data/frozen_control_trades_2024_2026-06-30.csv")])
        ctl["expiry_dt"]=pd.to_datetime(ctl.expiry)
        ctl["period"]=np.where(ctl.expiry_dt.dt.year<=2023,"development",np.where(ctl.expiry_dt.dt.year<=2025,"validation","holdout"))
        cc=ctl[ctl.period==per]
        if {"gross_rupees","cost_rupees"}.issubset(t.columns) and {"gross_rupees","cost_rupees"}.issubset(cc.columns):
            for mult in [1.25,1.5,2.0]:
                c[per][f"cost_stress_{int(mult*100)}pct_uplift"]=float(
                    (t.gross_rupees.sum()-mult*t.cost_rupees.sum())-
                    (cc.gross_rupees.sum()-mult*cc.cost_rupees.sum()))
    v=c["validation"]; h=c["holdout"]
    c["promotion_pass"]=bool(
        v.get("uplift_rupees",0)>0 and h.get("uplift_rupees",0)>0 and h.get("overrides",0)>=5 and
        v.get("policy_drawdown_rupees",np.inf)<=1.25*v.get("control_drawdown_rupees",1) and
        h.get("policy_drawdown_rupees",np.inf)<=1.25*h.get("control_drawdown_rupees",1) and
        v.get("cost_stress_150pct_uplift",0)>0 and h.get("cost_stress_150pct_uplift",0)>0 and
        v.get("boot_ci_low",-np.inf)>=0 and h.get("boot_ci_low",-np.inf)>=0)

decision="PROMOTION CANDIDATE — REQUIRES FINAL HUMAN/REPOSITORY REVIEW" if checks and all(c["promotion_pass"] for c in checks) else "NO PROMOTION — CANONICAL STRATEGY UNCHANGED"
result={"phase":42,"status":"COMPLETE","declared_variants":72,"eligible_count":int(SEL["eligible_count"]),
        "decision":decision,"top3_frozen":top,"checks":checks}
(OUT/"final_decision.json").write_text(json.dumps(result,indent=2,default=str))

lines=["# Phase 42 Manuscript — Confidence Calibration and Selective Counterfactual Routing","",
"## Abstract","Phase 42 tested whether the zero-override result of Phase 41 reflected an over-conservative uncertainty layer. Seventy-two preregistered combinations of two frozen economic-margin learners, four calibration modes, three economic margins and three India-VIX routing gates were screened chronologically on the accepted 477-opportunity counterfactual panel. The 2026 holdout was untouched until the top three validation policies were frozen. Exact sequential replay and paired-expiry inference were then completed.","",
"## Research questions","1. Does economic-margin ranking contain reproducible control-relative information?","2. Can sequential calibration turn that ranking into safe selective overrides?","3. Does conformal-style calibration improve the action/abstention trade-off?","4. Does the effect persist across India-VIX regimes?","5. Can any candidate beat the canonical stateful strategy after realistic execution costs?","",
"## Methods","Two Phase-41 learners were retained. Calibration modes were RAW, ROBUST_MAD, CONFORMAL_80 and CONFORMAL_90. The fixed policy universe was 72 variants. Every prediction and calibration width used only information available before the prediction timestamp. Development/validation selected the top three; the 2026 holdout was then evaluated once. Exact sequential replay retained the canonical state machine, historical lot sizes, one-tick adverse slippage, brokerage and statutory charges.","",
"## Results","See results/phase42_confidence_calibration/fixed_grid_validation.csv and selection.json.","",
"| Rank | Model | Calibration | Margin | Gate | Validation uplift | Holdout uplift | Holdout overrides |","|---:|---|---|---:|---|---:|---:|---:|"];
for(let i=1;i<=top.length;i++){const v=rnk(i,"validation"),h=rnk(i,"holdout");lines.append("| "+i+" | "+v.model+" | "+v.calibration+" | "+v.margin+" | "+v.gate+" | "+Number(v.uplift_rupees).toFixed(2)+" | "+Number(h.uplift_rupees).toFixed(2)+" | "+h.overrides+" |")}
lines.append("","## Statistical inference","","| Rank | Period | Mean uplift/expiry | 95% CI low | 95% CI high | p |","|---:|---|---:|---:|---:|---:|");
for(let i=1;i<=top.length;i++)for(const per of ["validation","holdout"]){const x=rnk(i,per);lines.append("| "+i+" | "+per+" | "+Number(x.boot_mean_uplift_per_expiry).toFixed(2)+" | "+Number(x.boot_ci_low).toFixed(2)+" | "+Number(x.boot_ci_high).toFixed(2)+" | "+Number(x.boot_p_one_sided).toFixed(4)+" |")}
lines.push("","## Discussion","The key comparison is between raw ranking quality and actionable policy value. A positive ranking diagnostic without robust sequential trading uplift is not sufficient for promotion. Conformal-style calibration is interpreted as a selective decision layer, not as a guarantee of distribution-free validity under financial dependence.","","## Strengths","- preregistered bounded universe;","- strict expanding-window chronology;","- untouched holdout;","- exact sequential replay with realistic costs;","- calibration and ranking diagnostics.","","## Limitations","- small independent expiry count in the 2026 holdout;","- non-exchangeable financial observations weaken formal conformal guarantees;","- historical fills do not reproduce live queue position/latency;","- propensity matching is a selection-overlap diagnostic, not causal identification.","","## Conclusion",decision,"","## Future research","If no candidate is promoted, the next phase should require a materially different source of information or prospective broker-quality validation rather than endless threshold tuning.","","## Artifacts","- PHASE42_RESEARCH_PLAN.md","- PHASE42_PRE_REGISTRATION.md","- PHASE42_LITERATURE_REVIEW.md","- PHASE42_STATUS.md","- results/phase42_confidence_calibration/",""])
(ROOT/"PHASE42_MANUSCRIPT.md").write_text("\n".join(lines)+"\n")
(ROOT/"PHASE42_STATUS.md").write_text("# Phase 42 Status — Confidence Calibration and Selective Counterfactual Routing\n\n**COMPLETE — "+decision+"**\n\nRegistered variants: **72**.\nValidation-eligible variants: **"+str(SEL["eligible_count"])+"**.\n\nThe top three were frozen before the untouched 2026 holdout. Exact sequential replay and paired-expiry inference were completed.\n\nSee PHASE42_MANUSCRIPT.md and results/phase42_confidence_calibration/final_decision.json.\n")
print(json.dumps(result,indent=2,default=str))
