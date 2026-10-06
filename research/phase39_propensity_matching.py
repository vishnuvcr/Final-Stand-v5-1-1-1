import json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

ROOT=Path(".")
F=ROOT/"results/phase39_features/point_in_time_features.csv"
L=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
S=ROOT/"results/phase39_sequential_policy/sequential_trades.csv"
OUT=ROOT/"results/phase39_propensity"
OUT.mkdir(parents=True,exist_ok=True)

EXCLUDE={"entry_ts","expiry","split","control_direction","control_net_rupees","delta_pnl_call_minus_put"}
CALIPERS=[0.01,0.025,0.05,0.10]
K=1

def load():
    x=pd.read_csv(F)
    l=pd.read_csv(L)
    s=pd.read_csv(S,usecols=["entry_ts","action","shadow_control_direction","override","period"])
    # Sequential engine may contain repeated opportunities only when a new trade starts;
    # retain unique entry timestamps and require consistency.
    s=s.sort_values("entry_ts").drop_duplicates("entry_ts",keep="last")
    z=x.merge(l[["entry_ts","call_net_rupees","put_net_rupees","delta_pnl_call_minus_put"]],
              on="entry_ts",how="inner",validate="one_to_one")
    z=z.merge(s[["entry_ts","action","shadow_control_direction","override","period"]],
              on="entry_ts",how="left",validate="one_to_one")
    z["treatment"]=z["override"].fillna(False).astype(int)
    # Economic treatment effect: alternative arm minus canonical control.
    z["treatment_effect"]=np.where(
        z["control_direction"].eq("CALL"),
        z["put_net_rupees"]-z["call_net_rupees"],
        z["call_net_rupees"]-z["put_net_rupees"])
    assert len(z)==477
    assert int(z.treatment.sum())==7
    return z

def feature_cols(z):
    cols=[]
    for c in z.columns:
        if c in EXCLUDE or c in {"call_net_rupees","put_net_rupees","candidate_credit_diff_call_minus_put",
                                 "treatment","treatment_effect","action","shadow_control_direction","override","period"}:
            continue
        if pd.api.types.is_numeric_dtype(z[c]) and z[c].notna().mean()>=0.50 and z[c].nunique(dropna=True)>=5:
            cols.append(c)
    return cols

def prep(train,test,cols):
    imp=SimpleImputer(strategy="median").fit(train[cols])
    sc=StandardScaler().fit(imp.transform(train[cols]))
    return sc.transform(imp.transform(train[cols])),sc.transform(imp.transform(test[cols]))

def fit_propensity(train,test,cols):
    A,B=prep(train,test,cols)
    y=train.treatment.to_numpy()
    # Class weight keeps the tiny treated class represented; regularization prevents separation.
    m=LogisticRegression(max_iter=3000,C=0.1,class_weight="balanced",solver="liblinear").fit(A,y)
    return m.predict_proba(B)[:,1]

def match(att):
    treated=att[att.treatment==1].copy()
    control=att[att.treatment==0].copy()
    rows=[]
    if len(treated)==0 or len(control)==0: return pd.DataFrame()
    for _,r in treated.iterrows():
        d=np.abs(control.ps.to_numpy()-r.ps)
        j=int(np.argmin(d))
        rows.append({
            "treated_entry_ts":r.entry_ts,
            "treated_ps":float(r.ps),
            "control_entry_ts":control.iloc[j].entry_ts,
            "control_ps":float(control.iloc[j].ps),
            "abs_ps_distance":float(d[j]),
            "treated_effect":float(r.treatment_effect),
            "matched_control_effect":float(control.iloc[j].treatment_effect),
            "effect_difference":float(r.treatment_effect-control.iloc[j].treatment_effect),
            "treated_split":r.split,
            "control_split":control.iloc[j].split
        })
    return pd.DataFrame(rows)

def balance(df,cols):
    t=df[df.treatment==1]; c=df[df.treatment==0]
    out=[]
    for col in cols:
        a=t[col].dropna(); b=c[col].dropna()
        if len(a)<2 or len(b)<2: continue
        sa=a.std(ddof=1); sb=b.std(ddof=1)
        pooled=np.sqrt((sa**2+sb**2)/2)
        smd=float((a.mean()-b.mean())/pooled) if pooled>0 else 0.0
        out.append({"feature":col,"smd":smd,"abs_smd":abs(smd)})
    return pd.DataFrame(out).sort_values("abs_smd",ascending=False)

def summarize(name,df,matched):
    if matched.empty:
        return {"sample":name,"treated":int(df.treatment.sum()),"controls":int((df.treatment==0).sum()),
                "matched":0,"att":None,"ci_lo":None,"ci_hi":None}
    dif=matched.effect_difference.to_numpy(float)
    rng=np.random.default_rng(39039)
    boots=[]
    for _ in range(10000):
        boots.append(float(rng.choice(dif,size=len(dif),replace=True).mean()))
    return {"sample":name,"treated":int(df.treatment.sum()),"controls":int((df.treatment==0).sum()),
            "matched":len(dif),"att":float(dif.mean()),
            "ci_lo":float(np.quantile(boots,.025)),"ci_hi":float(np.quantile(boots,.975)),
            "median_match_distance":float(matched.abs_ps_distance.median()),
            "max_match_distance":float(matched.abs_ps_distance.max())}

def main():
    z=load()
    cols=feature_cols(z)
    # Fit propensity only on development, then freeze the propensity model for validation/holdout.
    dev=z[z.split=="development"].copy()
    val=z[z.split=="validation"].copy()
    hold=z[z.split=="holdout"].copy()
    # Because treatment is policy-generated, development has the only defensible fitting sample.
    # If treatment is too sparse, report non-identifiability rather than inventing a model.
    if int(dev.treatment.sum())<3:
        raise RuntimeError("Development treatment count too small for propensity model.")
    ps_dev=fit_propensity(dev,dev,cols)
    # For validation/holdout, fit the same development model explicitly.
    A,B=prep(dev, val, cols)
    m=LogisticRegression(max_iter=3000,C=0.1,class_weight="balanced",solver="liblinear").fit(A,dev.treatment.to_numpy())
    ps_val=m.predict_proba(B)[:,1]
    A,H=prep(dev, hold, cols)
    ps_hold=m.predict_proba(H)[:,1]
    dev=dev.copy(); val=val.copy(); hold=hold.copy()
    dev["ps"]=ps_dev; val["ps"]=ps_val; hold["ps"]=ps_hold

    allrows=[]
    for per,df in [("development",dev),("validation",val),("holdout",hold)]:
        for cal in CALIPERS:
            mt=match(df)
            if not mt.empty:
                mt=mt[mt.abs_ps_distance<=cal].copy()
            sm=summarize(per,df,mt)
            sm["caliper"]=cal
            allrows.append(sm)
            if not mt.empty:
                mt["caliper"]=cal; mt["period"]=per
                mt.to_csv(OUT/f"matches_{per}_{str(cal).replace('.','p')}.csv",index=False)

    # Overall overlap and balance diagnostics.
    overlap=pd.DataFrame({
      "period":["development","validation","holdout"],
      "treated":[int(dev.treatment.sum()),int(val.treatment.sum()),int(hold.treatment.sum())],
      "control":[int((dev.treatment==0).sum()),int((val.treatment==0).sum()),int((hold.treatment==0).sum())],
      "ps_treated_min":[float(dev.loc[dev.treatment==1,"ps"].min()) if dev.treatment.sum() else np.nan,
                        float(val.loc[val.treatment==1,"ps"].min()) if val.treatment.sum() else np.nan,
                        float(hold.loc[hold.treatment==1,"ps"].min()) if hold.treatment.sum() else np.nan],
      "ps_treated_max":[float(dev.loc[dev.treatment==1,"ps"].max()) if dev.treatment.sum() else np.nan,
                        float(val.loc[val.treatment==1,"ps"].max()) if val.treatment.sum() else np.nan,
                        float(hold.loc[hold.treatment==1,"ps"].max()) if hold.treatment.sum() else np.nan],
      "ps_control_min":[float(dev.loc[dev.treatment==0,"ps"].min()),float(val.loc[val.treatment==0,"ps"].min()),float(hold.loc[hold.treatment==0,"ps"].min())],
      "ps_control_max":[float(dev.loc[dev.treatment==0,"ps"].max()),float(val.loc[val.treatment==0,"ps"].max()),float(hold.loc[hold.treatment==0,"ps"].max())]
    })
    bal=balance(dev,cols)
    pd.DataFrame(allrows).to_csv(OUT/"propensity_results.csv",index=False)
    overlap.to_csv(OUT/"propensity_overlap.csv",index=False)
    bal.to_csv(OUT/"development_balance.csv",index=False)

    # Primary interpretation: validation/holdout ATT is not estimable if there are no treated units.
    summary={
      "status":"COMPLETE",
      "total_rows":len(z),
      "development_treated":int(dev.treatment.sum()),
      "validation_treated":int(val.treatment.sum()),
      "holdout_treated":int(hold.treatment.sum()),
      "feature_count":len(cols),
      "primary_estimand":"ATT of Sparse-GAM override versus matched no-override opportunities, measured by alternative-minus-control net P&L",
      "calipers":CALIPERS,
      "development_att_caliper_0.05":next(x for x in allrows if x["period"]=="development" and x["caliper"]==0.05),
      "validation_att_identifiable":bool(val.treatment.sum()>0),
      "holdout_att_identifiable":bool(hold.treatment.sum()>0),
      "warning":"Treatment is policy-generated and extremely sparse; propensity matching cannot establish causal efficacy with seven overrides."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    print(pd.DataFrame(allrows).to_string(index=False))

if __name__=="__main__":
    main()
