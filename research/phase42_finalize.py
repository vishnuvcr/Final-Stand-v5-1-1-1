import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(".")
OUT=ROOT/"results/phase42_rank_policy"
SEL=json.load(open(OUT/"selection.json"))
SEQ=pd.read_csv(OUT/"sequential_summary.csv")
TOP=SEL["top3_frozen_before_holdout"]

def row(rank,per):
    x=SEQ[(SEQ["rank"]==rank)&(SEQ["period"]==per)]
    return x.iloc[0].to_dict() if len(x) else {}

def diag(per):
    p=OUT/f"diagnostics_{per}.json"
    return json.load(open(p)) if p.exists() else {}

def concentration(rank):
    f=OUT/f"sequential_candidate_{rank}.csv"
    if not f.exists():
        return {}
    a=pd.read_csv(f)
    if a.empty:
        return {}
    ctl=pd.concat([
        pd.read_csv("results/phase39_data/development_control_trades_2021_2023.csv"),
        pd.read_csv("results/phase39_data/frozen_control_trades_2024_2026-06-30.csv")
    ],ignore_index=True)
    ctl["period"]=np.where(pd.to_datetime(ctl["expiry"]).dt.year<=2023,"development",
                           np.where(pd.to_datetime(ctl["expiry"]).dt.year<=2025,"validation","holdout"))
    out={}
    for per in ["validation","holdout"]:
        aa=a[a["period"]==per]
        cc=ctl[ctl["period"]==per]
        if aa.empty:
            out[per]={"max_abs_share":float("inf"),"max_abs_expiry_uplift":0.0,"positive_sum":0.0}
            continue
        d=aa.groupby("expiry")["policy_net_rupees"].sum()-cc.groupby("expiry")["net_rupees"].sum()
        z=d.to_numpy(float)
        pos=float(z[z>0].sum()) if np.any(z>0) else 0.0
        out[per]={"max_abs_share":float(np.max(np.abs(z))/pos) if pos>0 else float("inf"),
                  "max_abs_expiry_uplift":float(np.max(np.abs(z))) if len(z) else 0.0,
                  "positive_sum":pos}
    return out

def action_asym(rank):
    f=OUT/f"sequential_candidate_{rank}.csv"
    if not f.exists():
        return {}
    a=pd.read_csv(f)
    out={}
    for per in ["validation","holdout"]:
        z=a[a["period"]==per]
        out[per]={
            "call_trades":int((z["action"]=="CALL").sum()),
            "put_trades":int((z["action"]=="PUT").sum()),
            "call_net":float(z.loc[z["action"]=="CALL","policy_net_rupees"].sum()),
            "put_net":float(z.loc[z["action"]=="PUT","policy_net_rupees"].sum())
        }
    return out

dv=diag("validation")
dh=diag("holdout")
checks=[]
for rank in range(1,len(TOP)+1):
    v=row(rank,"validation")
    h=row(rank,"holdout")
    cc=concentration(rank)
    rv=dv.get("ranking",{})
    rh=dh.get("ranking",{})
    mono_v=bool(rv.get("top_5_mean_delta",-np.inf)>=rv.get("top_10_mean_delta",-np.inf)>=rv.get("top_20_mean_delta",-np.inf))
    mono_h=bool(rh.get("top_5_mean_delta",-np.inf)>=rh.get("top_10_mean_delta",-np.inf)>=rh.get("top_20_mean_delta",-np.inf))
    checks.append({
        "rank":rank,
        "rank_cutoff":v.get("rank_cutoff"),
        "gate":v.get("gate"),
        "promotion_pass":all([
            float(v.get("uplift_rupees",0))>0,
            float(h.get("uplift_rupees",0))>0,
            float(v.get("boot_ci_lo",np.nan))>=0,
            float(h.get("boot_ci_lo",np.nan))>=0,
            float(v.get("policy_dd",np.inf))<=1.25*float(v.get("control_dd",np.inf)),
            float(h.get("policy_dd",np.inf))<=1.25*float(h.get("control_dd",np.inf)),
            float(v.get("cost_stress_150pct_uplift",np.nan))>0,
            float(h.get("cost_stress_150pct_uplift",np.nan))>0,
            int(h.get("overrides",0))>=5,
            cc.get("validation",{}).get("max_abs_share",np.inf)<=0.40,
            cc.get("holdout",{}).get("max_abs_share",np.inf)<=0.40,
            mono_v,mono_h
        ]),
        "checks":{
            "positive_validation":float(v.get("uplift_rupees",0))>0,
            "positive_holdout":float(h.get("uplift_rupees",0))>0,
            "validation_ci_lower_nonnegative":float(v.get("boot_ci_lo",np.nan))>=0,
            "holdout_ci_lower_nonnegative":float(h.get("boot_ci_lo",np.nan))>=0,
            "validation_drawdown_ok":float(v.get("policy_dd",np.inf))<=1.25*float(v.get("control_dd",np.inf)),
            "holdout_drawdown_ok":float(h.get("policy_dd",np.inf))<=1.25*float(h.get("control_dd",np.inf)),
            "validation_plus50_cost_positive":float(v.get("cost_stress_150pct_uplift",np.nan))>0,
            "holdout_plus50_cost_positive":float(h.get("cost_stress_150pct_uplift",np.nan))>0,
            "holdout_overrides_at_least_5":int(h.get("overrides",0))>=5,
            "expiry_concentration_validation_ok":cc.get("validation",{}).get("max_abs_share",np.inf)<=0.40,
            "expiry_concentration_holdout_ok":cc.get("holdout",{}).get("max_abs_share",np.inf)<=0.40,
            "ranking_monotone_validation":mono_v,
            "ranking_monotone_holdout":mono_h
        },
        "concentration":cc,
        "action_asymmetry":action_asym(rank)
    })

grid=pd.read_csv(OUT/"fixed_grid_validation.csv")
g=grid.sort_values("validation_uplift",ascending=True)
plt.figure(figsize=(10,6))
plt.barh(g["rank_cutoff"]+" | "+g["gate"],g["validation_uplift"])
plt.axvline(0,linewidth=1)
plt.title("Phase 42 validation uplift across six preregistered selective policies")
plt.xlabel("Validation uplift vs canonical control (rupees)")
plt.tight_layout()
plt.savefig(OUT/"phase42_validation_grid.png",dpi=160)
plt.close()

bars=[]
for rank in range(1,len(TOP)+1):
    v=row(rank,"validation");h=row(rank,"holdout")
    bars.append({
        "candidate":"Rank %d: %s / %s"%(rank,v.get("rank_cutoff",""),v.get("gate","")),
        "Validation":float(v.get("uplift_rupees",0)),
        "Holdout":float(h.get("uplift_rupees",0))
    })
pdf=pd.DataFrame(bars).set_index("candidate")
pdf.plot(kind="bar",figsize=(10,6))
plt.axhline(0,linewidth=1)
plt.ylabel("Sequential uplift vs canonical control (rupees)")
plt.title("Phase 42 frozen top-three sequential replay")
plt.tight_layout()
plt.savefig(OUT/"phase42_top3_sequential.png",dpi=160)
plt.close()

lines=[
"# Phase 42 Manuscript — Rank-to-Action Selective Policy",
"",
"## Abstract",
"",
"Phase 42 tested whether the ranking signal identified in Phase 41 could be converted into a selective trading policy without introducing another unrestricted predictive model family. Six pre-registered policies reused the leading Phase-41 spline-Ridge economic-margin model and selected only opportunities in the historical top 5%, 10% or 20% of model score, with either no VIX gate or a high-VIX gate. Exact chronology, the untouched 2026 holdout and the established one-tick slippage/cost model were retained.",
"",
"## Research questions",
"",
"1. Does raw directional economic-benefit score contain usable selective-ranking information?",
"2. Can controlled score coverage produce a positive, robust trading uplift?",
"3. Does high India VIX improve selective routing?",
"4. Does the result survive exact sequential replay and cost stress?",
"",
"## Methods",
"",
"Fixed sample: 477 opportunities (271 development, 172 validation, 34 holdout). One leading model was used. The score was the predicted control-relative economic benefit. For each timestamp, the score threshold was an empirical quantile of earlier scores only. Six candidates crossed three coverage targets (5%, 10%, 20%) with two routing gates (ALL, HIGH_VIX).",
"",
"## Results",
"",
"![Validation grid](results/phase42_rank_policy/phase42_validation_grid.png)",
"",
"| Rank | Cutoff | Gate | Validation uplift | Holdout uplift | Holdout overrides |",
"|---:|---|---|---:|---:|---:|"
]
for i in range(1,len(TOP)+1):
    v=row(i,"validation");h=row(i,"holdout")
    lines.append("| %d | %s | %s | %.2f | %.2f | %d |"%(i,v.get("rank_cutoff",""),v.get("gate",""),float(v.get("uplift_rupees",0)),float(h.get("uplift_rupees",0)),int(h.get("overrides",0))))
lines += [
"",
"![Sequential top three](results/phase42_rank_policy/phase42_top3_sequential.png)",
"",
"### Paired-expiry inference",
"",
"| Rank | Period | Mean uplift/expiry | 95% CI low | 95% CI high | p |",
"|---:|---|---:|---:|---:|---:|"
]
for i in range(1,len(TOP)+1):
    for per in ["validation","holdout"]:
        z=row(i,per)
        lines.append("| %d | %s | %.2f | %.2f | %.2f | %.4f |"%(i,per,float(z.get("boot_mean",np.nan)),float(z.get("boot_ci_lo",np.nan)),float(z.get("boot_ci_hi",np.nan)),float(z.get("boot_p_one_sided",np.nan))))
lines += [
"",
"### Cost stress",
"",
"| Rank | Period | +25% | +50% | +100% |",
"|---:|---|---:|---:|---:|"
]
for i in range(1,len(TOP)+1):
    for per in ["validation","holdout"]:
        z=row(i,per)
        lines.append("| %d | %s | %.2f | %.2f | %.2f |"%(i,per,float(z.get("cost_stress_125pct_uplift",np.nan)),float(z.get("cost_stress_150pct_uplift",np.nan)),float(z.get("cost_stress_200pct_uplift",np.nan))))
lines += [
"",
"### Ranking diagnostics",
"",
"Validation: "+json.dumps(dv.get("ranking",{}))+".",
"Holdout: "+json.dumps(dh.get("ranking",{}))+".",
"",
"### Propensity diagnostics",
"",
"Validation: "+json.dumps(dv.get("propensity",{}))+".",
"Holdout: "+json.dumps(dh.get("propensity",{}))+".",
"",
"## Decision",
"",
"| Rank | Promotion result |",
"|---:|---|"
]
for c in checks:
    lines.append("| %d | %s |"%(c["rank"],"PASS" if c["promotion_pass"] else "FAIL"))
lines += [
"",
"## Discussion",
"",
"Phase 42 directly tested the bottleneck exposed by Phase 41: the model had useful ranking signal but its uncertainty-penalized action rule produced no overrides. Selective coverage separates ranking quality from action density. A positive ranking curve without positive sequential policy value is not a tradable edge.",
"",
"## Strengths",
"",
"- No new classifier family; the leading Phase-41 model was retained.",
"- Explicit historical-score coverage controls and strict point-in-time percentile construction.",
"- Exact sequential replay, one-tick adverse slippage, brokerage and statutory charges.",
"- Untouched 2026 holdout and paired-expiry inference.",
"",
"## Limitations",
"",
"- The holdout contains only 20 expiry blocks.",
"- Rank thresholds control action coverage but are not causal treatment-effect estimators.",
"- Historical execution assumptions remain imperfect relative to live bid/ask and fill queue.",
"",
"## Conclusion",
"",
"The Phase-42 candidate family is closed under its preregistered scope. The canonical stateful strategy remains unchanged unless a candidate satisfies every promotion gate.",
"",
"## Future direction",
"",
"Prospective broker-quality paper validation remains preferable to expanding model search. If selective ranking shows repeated out-of-sample value without promotion, the next phase should isolate economic regime or spread-geometry interactions rather than add model complexity.",
"",
"## Reproducibility artifacts",
"",
"- PHASE42_RESEARCH_PLAN.md",
"- PHASE42_PRE_REGISTRATION.md",
"- PHASE42_LITERATURE_REVIEW.md",
"- results/phase42_rank_policy/fixed_grid_validation.csv",
"- results/phase42_rank_policy/selection.json",
"- results/phase42_rank_policy/frozen_top3_fixed_results.csv",
"- results/phase42_rank_policy/sequential_summary.csv",
"- results/phase42_rank_policy/diagnostics_validation.json",
"- results/phase42_rank_policy/diagnostics_holdout.json",
"- ERROR_LOG.md",
"- RESEARCH_LOG.md"
]
(OUT/"PHASE42_MANUSCRIPT_GENERATED.md").write_text("\n".join(lines)+"\n")
(ROOT/"PHASE42_MANUSCRIPT.md").write_text("\n".join(lines)+"\n")
decision="PROMOTED" if checks and checks[0]["promotion_pass"] else "NO PROMOTION — CANONICAL STRATEGY UNCHANGED"
status={"phase":42,"status":"COMPLETE","decision":decision,"declared_variants":6,"eligible_count":int(SEL.get("eligible_count",0)),
        "top3_frozen":TOP,"promotion_checks":checks,
        "validation_diagnostics":dv,"holdout_diagnostics":dh}
(OUT/"final_decision.json").write_text(json.dumps(status,indent=2,default=str))
(ROOT/"PHASE42_STATUS.md").write_text("# Phase 42 Status — Rank-to-Action Selective Policy\n\n**COMPLETE — "+decision+"**\n\nSix pre-registered selective ranking policies were evaluated. Exact sequential replay, paired-expiry inference, cost stress and ranking diagnostics were completed.\n\nDeclared variants: 6\nValidation-eligible variants: "+str(int(SEL.get("eligible_count",0)))+"\n\nSee PHASE42_MANUSCRIPT.md and results/phase42_rank_policy/final_decision.json.\n")
for name in ["RESEARCH_LOG.md","ERROR_LOG.md"]:
    p=ROOT/name
    txt=p.read_text()
    if name=="RESEARCH_LOG.md":
        txt+="\n\n## 2026-10-06 — Phase 42 closeout\n- Completed the six-variant selective rank-to-action phase with exact sequential replay, paired-expiry inference, cost stress and diagnostics.\n- Final decision is recorded in results/phase42_rank_policy/final_decision.json.\n"
    else:
        txt+="\n\n## 2026-10-06 — Phase 42 closeout\n- Accepted evidence is limited to the successful Phase-42 workflow after preflight, syntax audit, fixed-opportunity selection, sequential replay and closeout.\n"
    p.write_text(txt)
print(json.dumps(status,indent=2,default=str))
