import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge, LogisticRegression

import phase41_regime_policy_screen as p41

ROOT=Path(".")
OUT=ROOT/"results/phase42_rank_policy"
OUT.mkdir(parents=True, exist_ok=True)

RANKS={"TOP_5":0.95,"TOP_10":0.90,"TOP_20":0.80}
GATES=["ALL","HIGH_VIX"]
WARMUP=100
BOOT=10000

def build_model():
    return Pipeline([
        ("impute",SimpleImputer(strategy="median")),
        ("scale",StandardScaler()),
        ("spline",SplineTransformer(n_knots=4,degree=2,include_bias=False)),
        ("ridge",Ridge(alpha=10.0))
    ])

def feature_frame(df):
    return p41.add_vix_features(df)

def expanding_predictions(z):
    pred=np.full(len(z),np.nan)
    y=z["delta_pnl_call_minus_put"].to_numpy(float)
    X=feature_frame(z)
    for i in range(len(z)):
        if i<WARMUP: continue
        m=build_model()
        m.fit(X.iloc[:i],y[:i])
        pred[i]=float(m.predict(X.iloc[[i]])[0])
    return pred

def benefit(z,pred):
    ctl=z["control_direction"].astype(str).to_numpy()
    return np.where(ctl=="CALL",-pred,pred)

def gate_ok(row,gate):
    if gate=="ALL": return True
    if gate=="HIGH_VIX": return bool(row["india_vix_high"])
    raise ValueError(gate)

def policy(z, pred, rank_name, gate):
    sc=benefit(z,pred)
    hist=[]
    threshold=np.full(len(z),np.nan)
    pct=np.full(len(z),np.nan)
    override=np.zeros(len(z),dtype=bool)
    for i,s in enumerate(sc):
        finite=np.asarray(hist,dtype=float)
        finite=finite[np.isfinite(finite)]
        if len(finite)>=WARMUP and np.isfinite(s):
            q=float(np.quantile(finite,RANKS[rank_name]))
            threshold[i]=q
            pct[i]=float((finite<=s).mean())
            override[i]=bool(s>0 and s>=q and gate_ok(z.iloc[i],gate))
        if np.isfinite(s):
            hist.append(float(s))
    ctl=z["control_net_rupees"].to_numpy(float)
    alt=np.where(z["control_direction"].astype(str).to_numpy()=="CALL",
                 z["put_net_rupees"].to_numpy(float),z["call_net_rupees"].to_numpy(float))
    net=np.where(override,alt,ctl)
    return pd.DataFrame({
        "entry_ts":z["entry_ts"],"expiry":z["expiry"],"split":z["split"],
        "control_direction":z["control_direction"],"control_net_rupees":ctl,
        "alt_net_rupees":alt,"delta_pnl":z["delta_pnl_call_minus_put"],
        "pred_delta":pred,"rank_score":sc,"rank_threshold":threshold,
        "rank_percentile":pct,"override":override,"policy_net_rupees":net,
        "india_vix_level":z["india_vix_level"],"india_vix_ret1":z["india_vix_ret1"],"india_vix_high":z["india_vix_high"],
        "india_vix_rising":z["india_vix_rising"],"india_vix_high_rising":z["india_vix_high_rising"],
        "global_VIX":z["global_VIX"],"global_VIX_ret1":z["global_VIX_ret1"],
        "nifty_daily_rv_20d":z["nifty_daily_rv_20d"],"nifty_gap_from_prev_close":z["nifty_gap_from_prev_close"],
        "atm_iv_skew":z["atm_iv_skew"],"atm_pcr_oi":z["atm_pcr_oi"]
    })

def maxdd(x):
    a=np.asarray(x,float)
    if len(a)==0:return 0.0
    eq=np.cumsum(a); pk=np.maximum.accumulate(np.r_[0.0,eq])
    return float((pk[1:]-eq).max())

def expiry_boot(frame,split):
    d=frame[frame["split"]==split].copy()
    p=d.groupby("expiry")["policy_net_rupees"].sum()
    c=d.groupby("expiry")["control_net_rupees"].sum()
    keys=p.index.intersection(c.index)
    diff=(p.loc[keys]-c.loc[keys]).to_numpy(float)
    if len(diff)==0:return {"n":0}
    rng=np.random.default_rng(52000)
    idx=rng.integers(0,len(diff),size=(BOOT,len(diff)))
    means=diff[idx].mean(axis=1)
    signs=rng.choice([-1.0,1.0],size=(BOOT,len(diff)))
    null=(diff*signs).mean(axis=1)
    obs=float(diff.mean())
    return {
        "n":int(len(diff)),"mean":obs,"total":float(diff.sum()),
        "ci_lo":float(np.quantile(means,.025)),"ci_hi":float(np.quantile(means,.975)),
        "total_ci_lo":float(np.quantile(means*len(diff),.025)),
        "total_ci_hi":float(np.quantile(means*len(diff),.975)),
        "p_one_sided":float((np.sum(null>=obs)+1)/(BOOT+1)),
        "positive_expiry_share":float(np.mean(diff>0))
    }

def prop_match(sc,split,fit_period):
    d=sc[sc["split"]==split].copy()
    treated=int(d["override"].sum())
    if treated==0:return {"split":split,"treated":0,"matched":0,"att":None}
    cols=p41.STATE_FEATURES
    tr=d[d["split"]==split]
    fit=sc[sc["split"].isin(fit_period)].copy()
    Xfit=fit[cols].replace([np.inf,-np.inf],np.nan).fillna(fit[cols].median(numeric_only=True)).fillna(0)
    t=fit["override"].astype(int).to_numpy()
    if t.sum()<2 or (t==0).sum()<5:
        return {"split":split,"treated":treated,"matched":0,"att":None}
    scaler=StandardScaler().fit(Xfit)
    lr=LogisticRegression(max_iter=2000,class_weight="balanced").fit(scaler.transform(Xfit),t)
    X=d[cols].replace([np.inf,-np.inf],np.nan).fillna(fit[cols].median(numeric_only=True)).fillna(0)
    d["ps"]=lr.predict_proba(scaler.transform(X))[:,1]
    hi=d["india_vix_high"].astype(int).to_numpy(); tt=np.where(d["override"].to_numpy())[0]; cc=np.where(~d["override"].to_numpy())[0]
    used=set(); diffs=[]
    for i in tt:
        pool=[j for j in cc if j not in used and hi[j]==hi[i]]
        if not pool:continue
        j=min(pool,key=lambda k:abs(d.iloc[k]["ps"]-d.iloc[i]["ps"]))
        if abs(d.iloc[j]["ps"]-d.iloc[i]["ps"])<=0.05:
            diffs.append(float(d.iloc[i]["delta_pnl"]-d.iloc[j]["delta_pnl"])); used.add(j)
    if not diffs:return {"split":split,"treated":treated,"matched":0,"att":None,"common_support_fraction":0.0}
    x=np.asarray(diffs,float); rng=np.random.default_rng(52001)
    sims=rng.choice(x,size=(10000,len(x)),replace=True).mean(axis=1)
    return {"split":split,"treated":treated,"matched":int(len(x)),"att":float(x.mean()),
            "ci_lo":float(np.quantile(sims,.025)),"ci_hi":float(np.quantile(sims,.975)),
            "common_support_fraction":float(len(x)/treated)}

def ranking_curve(sc,split):
    d=sc[sc["split"]==split].copy()
    d=d[np.isfinite(d["rank_score"])].sort_values("rank_score",ascending=False)
    out={"split":split,"rows":int(len(d))}
    for frac in (0.05,0.10,0.20):
        n=max(1,int(np.ceil(frac*len(d))))
        x=d.head(n)["delta_pnl"].to_numpy(float)
        out[f"top_{int(frac*100)}_mean_delta"]=float(x.mean())
        out[f"top_{int(frac*100)}_positive_share"]=float((x>0).mean())
    return out

def main():
    z,thr=p41.load()
    pred=expanding_predictions(z)
    screen=z[z["split"].isin(["development","validation"])].copy().reset_index(drop=True)
    pred_screen=pred[:len(screen)]
    rows=[]; panels={}
    for rank_name in RANKS:
        for gate in GATES:
            pol=policy(screen,pred_screen,rank_name,gate)
            dev=pol[pol["split"]=="development"]; val=pol[pol["split"]=="validation"]
            du=float(dev["policy_net_rupees"].sum()-dev["control_net_rupees"].sum())
            vu=float(val["policy_net_rupees"].sum()-val["control_net_rupees"].sum())
            rows.append({"rank_cutoff":rank_name,"gate":gate,"development_uplift":du,"validation_uplift":vu,
                          "development_overrides":int(dev["override"].sum()),"validation_overrides":int(val["override"].sum()),
                          "validation_override_rate":float(val["override"].mean()),
                          "validation_policy_dd":maxdd(val["policy_net_rupees"]),
                          "validation_control_dd":maxdd(val["control_net_rupees"])})
    grid=pd.DataFrame(rows).sort_values(["validation_uplift","development_uplift"],ascending=False).reset_index(drop=True)
    grid.to_csv(OUT/"fixed_grid_validation.csv",index=False)
    eligible=grid[(grid.development_uplift>=0)&(grid.validation_uplift>0)&
                  (grid.validation_overrides>=5)&(grid.validation_override_rate<=0.20)&
                  (grid.validation_policy_dd<=1.25*grid.validation_control_dd)]
    top=eligible.head(3)
    fallback=""
    if top.empty:
        top=grid.head(3); fallback="No candidate passed the preregistered development/validation gate; top three are diagnostic only."
    selected=top.to_dict(orient="records")
    for rank,rec in enumerate(selected,1):
        panel=policy(z,pred,str(rec["rank_cutoff"]),str(rec["gate"]))
        panel["policy_id"]=rank
        panels[rank]=panel
        for split in ["development","validation","holdout"]:
            b=expiry_boot(panel,split)
            d=panel[panel["split"]==split]
            rows2={"rank":rank,**rec,"split":split,
                   "control_net_rupees":float(d["control_net_rupees"].sum()),
                   "policy_net_rupees":float(d["policy_net_rupees"].sum()),
                   "uplift_rupees":float(d["policy_net_rupees"].sum()-d["control_net_rupees"].sum()),
                   "overrides":int(d["override"].sum()),
                   "override_rate":float(d["override"].mean()) if len(d) else 0.0,
                   "policy_dd":maxdd(d["policy_net_rupees"]),"control_dd":maxdd(d["control_net_rupees"])}
            rows2.update({f"boot_{k}":v for k,v in b.items()})
            rows.append(rows2)
        panel.to_csv(OUT/f"fixed_frozen_candidate_{rank}.csv",index=False)
    finalgrid=pd.DataFrame(rows)
    finalgrid.to_csv(OUT/"frozen_top3_fixed_results.csv",index=False)
    if panels:
        leading=panels[1]
        for split,fit in [("validation",["development"]),("holdout",["development","validation"])]:
            (OUT/f"diagnostics_{split}.json").write_text(json.dumps({
                "rank_cutoff":selected[0]["rank_cutoff"],"gate":selected[0]["gate"],
                "propensity_fit_period":"+".join(fit),
                "propensity":prop_match(leading,split,fit),
                "ranking":ranking_curve(leading,split)
            },indent=2,default=str))
        leading.to_csv(OUT/"leading_policy_fixed_ledger.csv",index=False)
    sel={"declared_variants":6,"eligible_count":int(len(eligible)),"fallback_reason":fallback,
         "top3_frozen_before_holdout":selected,"vix_thresholds":thr}
    (OUT/"selection.json").write_text(json.dumps(sel,indent=2,default=str))
    (ROOT/"PHASE42_STATUS.md").write_text(
        "# Phase 42 Status — Rank-to-Action Selective Policy\n\n"
        "**STEP 1 COMPLETE — TOP 3 FROZEN; EXACT SEQUENTIAL REPLAY NEXT**\n\n"
        f"Declared variants: 6. Validation-eligible variants: {len(eligible)}.\n\n"
        f"{fallback}\n\nThe 2026 holdout is frozen from selection.\n"
    )
    print(json.dumps(sel,indent=2,default=str))

if __name__=="__main__":main()
