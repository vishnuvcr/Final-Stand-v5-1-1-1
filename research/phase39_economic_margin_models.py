import json, math, os
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import BayesianRidge, HuberRegressor, Ridge
from sklearn.neighbors import KNeighborsRegressor

ROOT=Path(".")
FEAT=ROOT/"results/phase39_features/point_in_time_features.csv"
LEDGER=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
OUT=ROOT/"results/phase39_model_screen"
OUT.mkdir(parents=True,exist_ok=True)
TZ="Asia/Kolkata"
SEED=1337
MAX_FEATURES=24
MARGIN_GRID=[0.0,250.0,500.0]
UNCERTAINTY_LAMBDA=1.0

def load():
    x=pd.read_csv(FEAT)
    y=pd.read_csv(LEDGER,usecols=["entry_ts","split","delta_pnl_call_minus_put","control_direction",
                                   "control_net_rupees","expiry"])
    x["entry_ts"]=pd.to_datetime(x["entry_ts"],utc=True).dt.tz_convert(TZ)
    y["entry_ts"]=pd.to_datetime(y["entry_ts"],utc=True).dt.tz_convert(TZ)
    z=x.merge(y,on=["entry_ts","split"],how="inner",suffixes=("_feature","_target"))
    z=z.sort_values("entry_ts").reset_index(drop=True)
    if len(z)!=477 or z.entry_ts.nunique()!=477:
        raise AssertionError("Model screen requires 477 unique fixed opportunities")
    return z

def eligible_cols(train):
    drop={"entry_ts","expiry","split","control_direction","control_net_rupees",
          "delta_pnl_call_minus_put","intraday_source_ts"}
    cols=[c for c in train.columns if c not in drop and pd.api.types.is_numeric_dtype(train[c])]
    cols=[c for c in cols if train[c].notna().sum()>0 and train[c].isna().mean()<=0.80]
    return cols

def select_and_prepare(train, test):
    y=train["delta_pnl_call_minus_put"].astype(float).to_numpy()
    cols=eligible_cols(train)
    if not cols:
        raise RuntimeError("No eligible features remain after missingness filter")
    X=train[cols].copy()
    A=SimpleImputer(strategy="median").fit_transform(X)
    # Spearman-equivalent rank correlation using training rows only.
    scores=[]
    yr=pd.Series(y).rank(method="average").to_numpy()
    for j,c in enumerate(cols):
        xr=pd.Series(A[:,j]).rank(method="average").to_numpy()
        s=np.corrcoef(xr,yr)[0,1] if np.std(xr)>0 and np.std(yr)>0 else 0.0
        scores.append((abs(float(s)) if np.isfinite(s) else 0.0,c))
    chosen=[c for _,c in sorted(scores,reverse=True)[:MAX_FEATURES]]
    imp=SimpleImputer(strategy="median").fit(train[chosen])
    sc=StandardScaler().fit(imp.transform(train[chosen]))
    A=sc.transform(imp.transform(train[chosen]))
    B=sc.transform(imp.transform(test[chosen]))
    return A,B,chosen

def fit_predict(method, train, test):
    A,B,chosen=select_and_prepare(train,test)
    y=train["delta_pnl_call_minus_put"].astype(float).to_numpy()
    if method=="BAYESIAN_RIDGE":
        m=BayesianRidge(alpha_1=1e-6,alpha_2=1e-6,lambda_1=1e-6,lambda_2=1e-6)
        m.fit(A,y)
        mu,sd=m.predict(B,return_std=True)
        pred=np.asarray(mu,float); unc=np.maximum(np.asarray(sd,float),1e-6)
    elif method=="HUBER":
        m=HuberRegressor(epsilon=1.35,alpha=1e-4,max_iter=2000)
        m.fit(A,y)
        pred=m.predict(B)
        resid=y-m.predict(A)
        mad=float(np.median(np.abs(resid-np.median(resid))))
        unc=np.full(len(B),max(1.4826*mad,1.0))
    elif method=="SPLINE_RIDGE":
        sp=SplineTransformer(n_knots=4,degree=3,include_bias=False)
        AA=sp.fit_transform(A); BB=sp.transform(B)
        m=Ridge(alpha=10.0)
        m.fit(AA,y)
        pred=m.predict(BB)
        resid=y-m.predict(AA)
        unc=np.full(len(B),max(float(np.std(resid,ddof=1)),1.0))
    elif method=="KNN":
        k=min(25,len(A))
        m=KNeighborsRegressor(n_neighbors=k,weights="distance",metric="euclidean")
        m.fit(A,y)
        pred=m.predict(B)
        dist,idx=m.kneighbors(B,n_neighbors=k,return_distance=True)
        w=1.0/np.maximum(dist,1e-6)
        vals=y[idx]
        mu=np.sum(w*vals,axis=1)/np.sum(w,axis=1)
        mad=np.sum(w*np.abs(vals-mu[:,None]),axis=1)/np.sum(w,axis=1)
        unc=np.maximum(1.4826*mad,1.0)
        pred=mu
    else:
        raise ValueError(method)
    return np.asarray(pred,float),np.asarray(unc,float),chosen

METHODS=["BAYESIAN_RIDGE","HUBER","SPLINE_RIDGE","KNN"]

def action_from_control(control,pred,unc,margin):
    imp=np.where(control=="CALL",-pred,pred)
    score=imp-UNCERTAINTY_LAMBDA*unc
    override=score>margin
    action=np.where(override,np.where(control=="CALL","PUT","CALL"),control)
    return action.astype(str),override,imp,score

def fixed_drawdown(pnl):
    eq=np.cumsum(pnl)
    peak=np.maximum.accumulate(np.r_[0.0,eq])
    dd=peak[1:]-eq
    return float(dd.max()) if len(dd) else 0.0

def paired_expiry_bootstrap(uplift_by_expiry,B=10000,seed=1337):
    rng=np.random.default_rng(seed)
    x=np.asarray(uplift_by_expiry,float)
    means=[]
    n=len(x)
    for _ in range(B):
        means.append(float(np.mean(x[rng.integers(0,n,n)])))
    return {"mean":float(np.mean(x)),"lo":float(np.quantile(means,0.025)),
            "hi":float(np.quantile(means,0.975)),"p_positive":float(np.mean(np.asarray(means)>0))}

def evaluate_window(frame,pred,unc):
    rows=[]
    for margin in MARGIN_GRID:
        action,override,imp,score=action_from_control(frame.control_direction.to_numpy(),pred,unc,margin)
        chosen=np.where(action=="CALL",frame.call_net_rupees if "call_net_rupees" in frame else np.nan,
                        frame.put_net_rupees if "put_net_rupees" in frame else np.nan)
        if np.isnan(chosen).all():
            chosen=None
        rows.append((margin,action,override,imp,score))
    return rows

def main():
    z=load()
    outcome_cols=pd.read_csv(LEDGER,usecols=["entry_ts","call_net_rupees","put_net_rupees","control_net_rupees","expiry"])
    outcome_cols["entry_ts"]=pd.to_datetime(outcome_cols["entry_ts"],utc=True).dt.tz_convert(TZ)
    z=z.merge(outcome_cols,on=["entry_ts","expiry","control_net_rupees"],how="left",suffixes=("","_out"))
    dev=z[z.split=="development"].copy()
    val=z[z.split=="validation"].copy()
    hold=z[z.split=="holdout"].copy()

    prediction_rows=[]
    # Validation: one-step expanding walk-forward, initial training = complete development.
    for method in METHODS:
        train=dev.copy()
        for _,row in val.iterrows():
            test=pd.DataFrame([row])
            pred,unc,chosen=fit_predict(method,train,test)
            prediction_rows.append({"method":method,"split":"validation","entry_ts":row.entry_ts,
                                    "pred_delta":float(pred[0]),"pred_unc":float(unc[0]),
                                    "n_features":len(chosen),"features":"|".join(chosen)})
            train=pd.concat([train,test],ignore_index=True)
        # Holdout only after the validation configuration is selected later.
    pred_df=pd.DataFrame(prediction_rows)

    # Validation scoring for every fixed CROL margin.
    metrics=[]
    preds=pred_df.merge(val[["entry_ts","control_direction","delta_pnl_call_minus_put","control_net_rupees",
                              "call_net_rupees","put_net_rupees","expiry"]],on="entry_ts",how="left")
    for method in METHODS:
        q=preds[preds.method==method].copy()
        err=q.pred_delta-q.delta_pnl_call_minus_put
        base_rmse=float(np.sqrt(np.mean(err**2))); base_mae=float(np.mean(np.abs(err)))
        rank_corr=float(q.pred_delta.corr(q.delta_pnl_call_minus_put,method="spearman"))
        sign_acc=float((np.sign(q.pred_delta)==np.sign(q.delta_pnl_call_minus_put)).mean())
        for margin in MARGIN_GRID:
            act,ov,imp,score=action_from_control(q.control_direction.to_numpy(),q.pred_delta.to_numpy(),q.pred_unc.to_numpy(),margin)
            pnl=np.where(act=="CALL",q.call_net_rupees.to_numpy(),q.put_net_rupees.to_numpy())
            uplift=pnl-q.control_net_rupees.to_numpy()
            q2=q.copy(); q2["uplift"]=uplift
            exp=q2.groupby("expiry",as_index=False).uplift.sum()["uplift"].to_numpy()
            boot=paired_expiry_bootstrap(exp)
            metrics.append({
                "method":method,"margin":margin,"rmse":base_rmse,"mae":base_mae,"spearman":rank_corr,
                "sign_accuracy":sign_acc,"overrides":int(ov.sum()),"override_share":float(ov.mean()),
                "selected_net_rupees":float(pnl.sum()),"control_net_rupees":float(q.control_net_rupees.sum()),
                "uplift_rupees":float(uplift.sum()),"mean_uplift":float(uplift.mean()),
                "median_uplift":float(np.median(uplift)),"win_share":float((uplift>0).mean()),
                "max_drawdown_selected":fixed_drawdown(pnl),
                "bootstrap_mean_expiry_uplift":boot["mean"],"bootstrap_lo":boot["lo"],"bootstrap_hi":boot["hi"],
                "bootstrap_p_positive":boot["p_positive"]
            })
    mdf=pd.DataFrame(metrics).sort_values(["uplift_rupees","bootstrap_p_positive"],ascending=[False,False])
    mdf.to_csv(OUT/"validation_screen.csv",index=False)

    # Freeze selected model + margin from validation, then walk the holdout chronologically.
    eligible=mdf[(mdf.uplift_rupees>0)&(mdf.bootstrap_p_positive>=0.50)]
    if eligible.empty:
        selected=mdf.iloc[0]
        selection_reason="No validation candidate met the positive-uplift screen; top validation uplift retained for diagnostic holdout only and cannot be promoted."
        holdout_promotable=False
    else:
        selected=eligible.iloc[0]
        selection_reason="Highest validation uplift among candidates satisfying positive validation uplift and non-adverse paired-bootstrap tendency."
        holdout_promotable=True
    method=selected.method; margin=float(selected.margin)

    train=pd.concat([dev,val],ignore_index=True)
    hold_rows=[]
    for _,row in hold.iterrows():
        test=pd.DataFrame([row])
        pred,unc,chosen=fit_predict(method,train,test)
        act,ov,imp,score=action_from_control(np.array([row.control_direction]),pred,unc,margin)
        action=str(act[0])
        pnl=float(row.call_net_rupees if action=="CALL" else row.put_net_rupees)
        hold_rows.append({"entry_ts":row.entry_ts,"expiry":row.expiry,"control_direction":row.control_direction,
                          "action":action,"override":bool(ov[0]),"pred_delta":float(pred[0]),"pred_unc":float(unc[0]),
                          "pred_alt_improvement":float(imp[0]),"decision_score":float(score[0]),"margin":margin,
                          "selected_net_rupees":pnl,"control_net_rupees":float(row.control_net_rupees)})
        # In online use, this historical observation becomes available only after its opportunity resolves.
        train=pd.concat([train,test],ignore_index=True)
    hdf=pd.DataFrame(hold_rows)
    hdf.to_csv(OUT/"holdout_fixed_opportunity_screen.csv",index=False)

    # Summary, with holdout explicitly diagnostic until sequential replay is complete.
    summary={
        "status":"COMPLETE",
        "methods":METHODS,"margin_grid":MARGIN_GRID,"uncertainty_lambda":UNCERTAINTY_LAMBDA,
        "validation_rows":len(val),"holdout_rows":len(hold),
        "selected_model":method,"selected_margin":margin,
        "selection_reason":selection_reason,
        "validation_selected_uplift_rupees":float(selected.uplift_rupees),
        "validation_selected_bootstrap_ci":[float(selected.bootstrap_lo),float(selected.bootstrap_hi)],
        "diagnostic_holdout_selected_net_rupees":float(hdf.selected_net_rupees.sum()),
        "diagnostic_holdout_control_net_rupees":float(hdf.control_net_rupees.sum()),
        "diagnostic_holdout_uplift_rupees":float((hdf.selected_net_rupees-hdf.control_net_rupees).sum()),
        "holdout_promotable":False,
        "fixed_opportunity_only":True
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    (OUT/"status.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    print(mdf.head(20).to_string(index=False))

if __name__=="__main__":
    main()
