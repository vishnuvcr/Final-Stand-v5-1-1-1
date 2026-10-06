import os, json, math, subprocess, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
SEED = 1337
TZ = "Asia/Kolkata"
DATA = Path("data/phase33")
OUT = Path("results/phase34_alternative_prediction")
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = pd.Timestamp("2023-12-31 23:59:59", tz=TZ)
VAL_END = pd.Timestamp("2025-12-31 23:59:59", tz=TZ)
HOLD_START = pd.Timestamp("2026-01-01", tz=TZ)
HOLD_END = pd.Timestamp("2026-09-30 23:59:59", tz=TZ)

def ensure(pkg, import_name=None):
    try:
        __import__(import_name or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def norm_ts(x):
    y = pd.to_datetime(x, errors="coerce")
    if getattr(y.dt, "tz", None) is None:
        y = y.dt.tz_localize(TZ)
    else:
        y = y.dt.tz_convert(TZ)
    return y.astype(f"datetime64[ns, {TZ}]")

def load_cache():
    ep = DATA / "events.parquet"
    dp = DATA / "nifty_daily.parquet"
    if not ep.exists() or not dp.exists():
        raise RuntimeError("Phase-33 cached event/daily data is missing")
    ev = pd.read_parquet(ep)
    daily = pd.read_parquet(dp)
    ev["expiry"] = norm_ts(ev["expiry"]).dt.normalize()
    ev["ref_ts"] = norm_ts(ev["ref_ts"])
    daily["date"] = norm_ts(daily["date"]).dt.normalize()
    return ev.sort_values("ref_ts"), daily.sort_values("date")

def split_of(ts):
    if ts <= TRAIN_END: return "train"
    if ts <= VAL_END: return "validation"
    if HOLD_START <= ts <= HOLD_END: return "holdout"
    return "other"

def feature_cols(ev):
    drop = {"expiry","ref_ts","ref_spot","expiry_close","target_return","target_direction","split"}
    return [c for c in ev.columns if c not in drop and pd.api.types.is_numeric_dtype(ev[c])]

def metric_block(y, p):
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score, log_loss, brier_score_loss
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1-1e-6)
    pr = (p >= 0.5).astype(int)
    return {
        "n": int(len(y)),
        "accuracy": float(accuracy_score(y, pr)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pr)),
        "roc_auc": float(roc_auc_score(y,p)) if len(np.unique(y))==2 else np.nan,
        "log_loss": float(log_loss(y, np.c_[1-p,p], labels=[0,1])),
        "brier": float(brier_score_loss(y,p)),
    }

def prep_tabular(fit_df, test_df, cols):
    from sklearn.impute import SimpleImputer
    imp = SimpleImputer(strategy="median").fit(fit_df[cols])
    return imp, imp.transform(fit_df[cols]), imp.transform(test_df[cols])

def fit_xgb(fit_df, test_df, cols):
    ensure("xgboost")
    from xgboost import XGBClassifier
    imp, a, b = prep_tabular(fit_df,test_df,cols)
    y = fit_df["target_direction"].astype(int).to_numpy()
    pos = max(1, int(y.sum())); neg = max(1, len(y)-int(y.sum()))
    m = XGBClassifier(
        n_estimators=250, max_depth=3, learning_rate=0.03,
        subsample=0.80, colsample_bytree=0.80, min_child_weight=5,
        reg_lambda=2.0, objective="binary:logistic", eval_metric="logloss",
        random_state=SEED, n_jobs=-1, tree_method="hist",
        scale_pos_weight=neg/pos
    )
    m.fit(a,y)
    return m.predict_proba(b)[:,1]

def fit_extra(fit_df, test_df, cols):
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import ExtraTreesClassifier
    imp,a,b=prep_tabular(fit_df,test_df,cols)
    m=ExtraTreesClassifier(
        n_estimators=400,max_depth=6,min_samples_leaf=4,
        class_weight="balanced",random_state=SEED,n_jobs=-1
    )
    m.fit(a,fit_df["target_direction"].astype(int))
    return m.predict_proba(b)[:,1]

def fit_hgb(fit_df, test_df, cols):
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import HistGradientBoostingClassifier
    imp,a,b=prep_tabular(fit_df,test_df,cols)
    m=HistGradientBoostingClassifier(
        max_iter=250,learning_rate=0.03,max_leaf_nodes=15,max_depth=4,
        min_samples_leaf=8,l2_regularization=1.0,random_state=SEED
    )
    m.fit(a,fit_df["target_direction"].astype(int))
    return m.predict_proba(b)[:,1]

def fit_svm(fit_df, test_df, cols):
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC
    imp,a,b=prep_tabular(fit_df,test_df,cols)
    sc=StandardScaler().fit(a)
    m=SVC(C=1.0,gamma="scale",class_weight="balanced",probability=True,random_state=SEED)
    m.fit(sc.transform(a),fit_df["target_direction"].astype(int))
    return m.predict_proba(sc.transform(b))[:,1]

def fit_elastic(fit_df,test_df,cols):
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    imp,a,b=prep_tabular(fit_df,test_df,cols)
    sc=StandardScaler().fit(a)
    m=LogisticRegression(
        penalty="elasticnet",solver="saga",C=0.20,l1_ratio=0.50,
        class_weight="balanced",max_iter=5000,random_state=SEED
    )
    m.fit(sc.transform(a),fit_df["target_direction"].astype(int))
    return m.predict_proba(sc.transform(b))[:,1]

def seq_features(daily):
    d=daily.sort_values("date").copy()
    r=np.log(d["close"]/d["close"].shift(1))
    out=pd.DataFrame({"date":d["date"]})
    for n in [1,3,5,10,20]:
        out[f"ret{n}"]=np.log(d["close"]/d["close"].shift(n))
    for n in [5,10,20]:
        out[f"vol{n}"]=r.rolling(n).std()
        out[f"range{n}"]=np.log(d["high"]/d["low"]).rolling(n).mean()
    out["rsi14"]=100-100/(1+(d["close"].diff().clip(lower=0).rolling(14).mean()/(-d["close"].diff().clip(upper=0)).rolling(14).mean().replace(0,np.nan)))
    ema12=d["close"].ewm(span=12,adjust=False).mean()
    ema26=d["close"].ewm(span=26,adjust=False).mean()
    out["macd"]=ema12-ema26
    out["ma_gap20"]=d["close"]/d["close"].rolling(20).mean()-1
    return out

def build_sequences(ev_subset,daily):
    sf=seq_features(daily).sort_values("date")
    cols=[c for c in sf.columns if c!="date"]
    X=[]; y=[]; used=[]
    for _,row in ev_subset.sort_values("ref_ts").iterrows():
        ref=pd.Timestamp(row["ref_ts"]).normalize()
        prior=sf[sf["date"]<ref].tail(30)
        if len(prior)<30 or prior[cols].isna().any().any():
            continue
        X.append(prior[cols].to_numpy(float))
        y.append(float(row["target_return"]))
        used.append(row["ref_ts"])
    return np.asarray(X,float), np.asarray(y,float), used, cols

def fit_transformer(fit_df,test_df,daily):
    ensure("torch")
    import torch
    from torch import nn
    from sklearn.preprocessing import StandardScaler
    torch.manual_seed(SEED); np.random.seed(SEED)
    Xtr,ytr,_,cols=build_sequences(fit_df,daily)
    Xte,_,used,_=build_sequences(test_df,daily)
    if len(Xtr)<30 or len(Xte)!=len(test_df):
        return pd.Series(0.5,index=test_df.index).to_numpy()
    sc=StandardScaler().fit(Xtr.reshape(-1,Xtr.shape[-1]))
    A=sc.transform(Xtr.reshape(-1,Xtr.shape[-1])).reshape(Xtr.shape)
    B=sc.transform(Xte.reshape(-1,Xte.shape[-1])).reshape(Xte.shape)
    xt=torch.tensor(A,dtype=torch.float32); yt=torch.tensor(ytr,dtype=torch.float32).view(-1,1)
    class Net(nn.Module):
        def __init__(self,nf):
            super().__init__()
            self.inp=nn.Linear(nf,32)
            self.pos=nn.Parameter(torch.zeros(1,30,32))
            enc=nn.TransformerEncoderLayer(d_model=32,nhead=4,dim_feedforward=64,dropout=0.10,batch_first=True)
            self.enc=nn.TransformerEncoder(enc,num_layers=1)
            self.fc=nn.Linear(32,1)
        def forward(self,x):
            z=self.inp(x)+self.pos[:,:x.shape[1],:]
            z=self.enc(z)
            return self.fc(z[:,-1,:])
    net=Net(Xtr.shape[-1]); opt=torch.optim.Adam(net.parameters(),lr=0.003)
    loss=nn.MSELoss()
    for _ in range(50):
        opt.zero_grad(); pred=net(xt); l=loss(pred,yt); l.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(),1.0); opt.step()
    sd=max(float(np.std(ytr,ddof=1)),1e-4)
    net.eval(); probs=[]
    with torch.no_grad():
        for z in B:
            mu=float(net(torch.tensor(z[None,:,:],dtype=torch.float32)).item())
            probs.append(0.5*(1+math.erf((mu/sd)/math.sqrt(2))))
    return np.asarray(probs)

def fit_tcn(fit_df,test_df,daily):
    ensure("torch")
    import torch
    from torch import nn
    from sklearn.preprocessing import StandardScaler
    torch.manual_seed(SEED); np.random.seed(SEED)
    Xtr,ytr,_,cols=build_sequences(fit_df,daily)
    Xte,_,used,_=build_sequences(test_df,daily)
    if len(Xtr)<30 or len(Xte)!=len(test_df):
        return np.full(len(test_df),0.5)
    sc=StandardScaler().fit(Xtr.reshape(-1,Xtr.shape[-1]))
    A=sc.transform(Xtr.reshape(-1,Xtr.shape[-1])).reshape(Xtr.shape)
    B=sc.transform(Xte.reshape(-1,Xte.shape[-1])).reshape(Xte.shape)
    xt=torch.tensor(A.transpose(0,2,1),dtype=torch.float32); yt=torch.tensor(ytr,dtype=torch.float32).view(-1,1)
    class Block(nn.Module):
        def __init__(self,dil):
            super().__init__()
            self.conv=nn.Conv1d(16,16,3,padding=2*dil,dilation=dil)
            self.act=nn.ReLU()
            self.drop=nn.Dropout(0.10)
        def forward(self,x):
            z=self.drop(self.act(self.conv(x)))
            return z[:,:,:x.shape[-1]]
    class Net(nn.Module):
        def __init__(self,nf):
            super().__init__()
            self.inp=nn.Conv1d(nf,16,1)
            self.b1=Block(1); self.b2=Block(2); self.b3=Block(4)
            self.fc=nn.Linear(16,1)
        def forward(self,x):
            z=self.inp(x); z=self.b1(z); z=self.b2(z); z=self.b3(z)
            return self.fc(z.mean(dim=2))
    net=Net(Xtr.shape[-1]); opt=torch.optim.Adam(net.parameters(),lr=0.003); loss=nn.MSELoss()
    for _ in range(50):
        opt.zero_grad(); pred=net(xt); l=loss(pred,yt); l.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(),1.0); opt.step()
    sd=max(float(np.std(ytr,ddof=1)),1e-4)
    net.eval(); probs=[]
    with torch.no_grad():
        for z in B.transpose(0,2,1):
            mu=float(net(torch.tensor(z[None,:,:],dtype=torch.float32)).item())
            probs.append(0.5*(1+math.erf((mu/sd)/math.sqrt(2))))
    return np.asarray(probs)

def hmm_predict(test_df,daily):
    ensure("hmmlearn")
    from hmmlearn.hmm import GaussianHMM
    from sklearn.preprocessing import StandardScaler
    d=daily.sort_values("date").copy()
    r=np.log(d["close"]/d["close"].shift(1))
    d["ret1"]=r; d["vol20"]=r.rolling(20).std()
    probs=[]
    for _,row in test_df.sort_values("ref_ts").iterrows():
        ref=pd.Timestamp(row["ref_ts"]).normalize()
        hist=d[d["date"]<ref].dropna(subset=["ret1","vol20"]).reset_index(drop=True)
        if len(hist)<250:
            probs.append(0.5); continue
        sc=StandardScaler().fit(hist[["ret1","vol20"]])
        X=sc.transform(hist[["ret1","vol20"]])
        try:
            hmm=GaussianHMM(n_components=3,covariance_type="diag",n_iter=100,random_state=SEED,tol=1e-4)
            hmm.fit(X)
            post=hmm.predict_proba(X)
            state=int(np.argmax(post[-1]))
            # Number of trading sessions from the reference day to expiry.
            future_dates=d[(d["date"]>=ref)&(d["date"]<=pd.Timestamp(row["expiry"]).normalize())]["date"].tolist()
            h=max(1,len(future_dates))
            y=np.log(d["close"].shift(-h)/d["close"])
            usable=(d["date"]<ref)&y.notna()
            state_series=pd.Series(hmm.predict(X),index=hist.index)
            hist_states=state_series.reindex(hist.index)
            hist_dates=hist["date"]
            target_by_date=pd.Series(y.to_numpy(),index=d.index)
            # Align state-labelled history with original d positions via dates.
            tmp=pd.DataFrame({"date":hist_dates.to_numpy(),"state":hist_states.to_numpy()})
            yy=pd.DataFrame({"date":d["date"].to_numpy(),"hret":y.to_numpy()})
            tmp=tmp.merge(yy,on="date",how="left")
            tmp=tmp[tmp["date"]<ref]
            candidates=tmp[tmp["state"]==state]["hret"].dropna()
            if len(candidates)<12:
                candidates=tmp["hret"].dropna()
            p=float((np.sum(candidates>0)+1)/(len(candidates)+2)) if len(candidates) else 0.5
            probs.append(p)
        except Exception:
            probs.append(0.5)
    return np.asarray(probs)

def bootstrap_ci(x,n=3000):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if not len(x): return [np.nan,np.nan]
    rng=np.random.default_rng(SEED)
    means=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(n)])
    return [float(np.quantile(means,0.025)),float(np.quantile(means,0.975))]

def signflip_pvalue(x,n=10000):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if not len(x): return np.nan
    obs=abs(x.mean()); rng=np.random.default_rng(SEED)
    signs=rng.choice([-1.0,1.0],size=(n,len(x)))
    sims=np.abs((signs*x).mean(axis=1))
    return float((1+np.sum(sims>=obs))/(n+1))

def main():
    ev,daily=load_cache()
    ev=ev[(ev["ref_ts"]>=pd.Timestamp("2021-05-27",tz=TZ))&(ev["ref_ts"]<=HOLD_END)].copy()
    ev["split"]=ev["ref_ts"].map(split_of)
    train=ev[ev["split"]=="train"].copy()
    val=ev[ev["split"]=="validation"].copy()
    hold=ev[ev["split"]=="holdout"].copy()
    cols=feature_cols(ev)
    if len(train)<60 or len(val)<20 or len(hold)<10:
        raise RuntimeError("Insufficient event counts")

    parts=[]
    for split,test in [("validation",val),("holdout",hold)]:
        fit=train if split=="validation" else pd.concat([train,val]).sort_values("ref_ts")
        row=test[["expiry","ref_ts","target_return","target_direction"]].copy()
        for name,fn in [
            ("xgb",fit_xgb),("extra_trees",fit_extra),("hist_gb",fit_hgb),
            ("svm_rbf",fit_svm),("elastic_net",fit_elastic)
        ]:
            try:
                row[name+"_prob"]=fn(fit,test,cols)
            except Exception as exc:
                print("MODEL_ERROR",name,split,repr(exc),flush=True)
                row[name+"_prob"]=0.5
        try: row["hmm_regime_prob"]=hmm_predict(test,daily)
        except Exception as exc:
            print("MODEL_ERROR hmm",split,repr(exc),flush=True); row["hmm_regime_prob"]=0.5
        try: row["transformer_prob"]=fit_transformer(fit,test,daily)
        except Exception as exc:
            print("MODEL_ERROR transformer",split,repr(exc),flush=True); row["transformer_prob"]=0.5
        try: row["tcn_prob"]=fit_tcn(fit,test,daily)
        except Exception as exc:
            print("MODEL_ERROR tcn",split,repr(exc),flush=True); row["tcn_prob"]=0.5
        row["new_equal_8_prob"]=row[[c for c in row.columns if c.endswith("_prob") and c not in ["new_equal_8_prob","tree_equal_3_prob"]]].mean(axis=1)
        row["tree_equal_3_prob"]=row[["xgb_prob","extra_trees_prob","hist_gb_prob"]].mean(axis=1)
        row["split"]=split
        parts.append(row)
    pred=pd.concat(parts,ignore_index=True).sort_values("ref_ts")
    pred.to_csv(OUT/"model_predictions.csv",index=False)

    model_names=["xgb","extra_trees","hist_gb","svm_rbf","elastic_net","hmm_regime","transformer","tcn","new_equal_8","tree_equal_3"]
    metrics=[]
    for split in ["validation","holdout"]:
        q=pred[pred["split"]==split]
        for model in model_names:
            metrics.append({"split":split,"model":model,**metric_block(q["target_direction"],q[model+"_prob"])})
    # Phase-33 RF control, rebuilt with the registered parameters.
    try:
        from sklearn.impute import SimpleImputer
        from sklearn.ensemble import RandomForestClassifier
        for split,test in [("validation",val),("holdout",hold)]:
            fit=train if split=="validation" else pd.concat([train,val]).sort_values("ref_ts")
            imp=SimpleImputer(strategy="median").fit(fit[cols])
            rf=RandomForestClassifier(n_estimators=300,max_depth=5,min_samples_leaf=4,class_weight="balanced_subsample",random_state=SEED,n_jobs=-1)
            rf.fit(imp.transform(fit[cols]),fit["target_direction"].astype(int))
            p=rf.predict_proba(imp.transform(test[cols]))[:,1]
            metrics.append({"split":split,"model":"rf_phase33_control",**metric_block(test["target_direction"],p)})
            pred.loc[pred["split"]==split,"rf_phase33_prob"]=p
    except Exception as exc:
        print("RF_CONTROL_ERROR",repr(exc),flush=True)
        pred["rf_phase33_prob"]=0.5
    pred.to_csv(OUT/"model_predictions.csv",index=False)

    # Baselines.
    baseline=[]
    for split,test in [("validation",val),("holdout",hold)]:
        prior=train if split=="validation" else pd.concat([train,val])
        rate=float(prior["target_direction"].mean())
        for name,p in [("constant",np.full(len(test),rate)),("always_up",np.ones(len(test))),("always_down",np.zeros(len(test)))]:
            baseline.append({"split":split,"model":name,**metric_block(test["target_direction"],p)})
    pd.DataFrame(baseline).to_csv(OUT/"baseline_metrics.csv",index=False)
    metrics.extend(baseline)
    pd.DataFrame(metrics).to_csv(OUT/"model_metrics.csv",index=False)

    econ=[]
    cols_for_econ=model_names+["rf_phase33"]
    for split in ["validation","holdout"]:
        q=pred[pred["split"]==split].copy()
        for model in cols_for_econ:
            p=q[model+"_prob"]
            signed=np.where(p>=0.5,1.0,-1.0)*q["target_return"].to_numpy(float)
            lo,hi=bootstrap_ci(signed)
            econ.append({
                "split":split,"model":model,"hit_rate":float((signed>0).mean()),
                "mean_signed_log_return":float(signed.mean()),
                "sum_signed_log_return":float(signed.sum()),
                "bootstrap_ci_low":lo,"bootstrap_ci_high":hi,
                "signflip_pvalue":signflip_pvalue(signed)
            })
    pd.DataFrame(econ).to_csv(OUT/"directional_economic_diagnostic.csv",index=False)

    yr=[]
    for split in ["validation","holdout"]:
        q=pred[pred["split"]==split].copy(); q["year"]=pd.to_datetime(q["expiry"]).dt.year
        for y,g in q.groupby("year"):
            for model in model_names+["rf_phase33"]:
                p=g[model+"_prob"]; hit=float(((p>=0.5).astype(int)==g["target_direction"]).mean())
                sr=np.where(p>=0.5,1,-1)*g["target_return"].to_numpy(float)
                yr.append({"split":split,"year":int(y),"model":model,"n":int(len(g)),"accuracy":hit,"mean_signed_log_return":float(sr.mean())})
    pd.DataFrame(yr).to_csv(OUT/"yearly_stability.csv",index=False)

    # Decision screen is descriptive; no new model is promoted here.
    m=pd.read_csv(OUT/"model_metrics.csv")
    b=pd.read_csv(OUT/"baseline_metrics.csv")
    e=pd.read_csv(OUT/"directional_economic_diagnostic.csv")
    rows=[]
    baseline_hold=float(b[(b.split=="holdout")&(b.model=="always_down")]["accuracy"].iloc[0])
    baseline_val=max(float(b[(b.split=="validation")&(b.model==x)]["accuracy"].iloc[0]) for x in ["constant","always_up","always_down"])
    for model in model_names:
        vm=float(m[(m.split=="validation")&(m.model==model)]["accuracy"].iloc[0])
        hm=float(m[(m.split=="holdout")&(m.model==model)]["accuracy"].iloc[0])
        eh=e[(e.split=="holdout")&(e.model==model)].iloc[0]
        rows.append({
            "model":model,
            "validation_accuracy":vm,
            "holdout_accuracy":hm,
            "validation_beats_simple_baseline":vm>baseline_val,
            "holdout_beats_always_down":hm>baseline_hold,
            "holdout_signed_return_ci_excludes_zero":bool(eh["bootstrap_ci_low"]>0 or eh["bootstrap_ci_high"]<0),
            "promotion":"NO — separate trading overlay phase required"
        })
    pd.DataFrame(rows).to_csv(OUT/"PHASE34_DECISION_TABLE.csv",index=False)

    meta={
        "phase":"34",
        "reference":"D-6 calendar days at exactly 10:00 IST",
        "events_total":int(len(ev)),
        "train_events":int(len(train)),
        "validation_events":int(len(val)),
        "holdout_events":int(len(hold)),
        "feature_count":int(len(cols)),
        "models_tested":["XGBoost","ExtraTrees","HistGradientBoosting","RBF-SVM","Elastic-Net Logistic","HMM-Regime","Tiny Transformer","TCN-lite","NEW_EQUAL_8","TREE_EQUAL_3"],
        "control":"Phase-33 Random Forest",
        "note":"Predictive research only; no option P&L overlay was executed in Phase 34."
    }
    with open(OUT/"coverage_and_metadata.json","w") as f: json.dump(meta,f,indent=2)

    # Manuscript.
    bestv=m[(m.split=="validation") & (m.model.isin(model_names))].sort_values(["log_loss","accuracy"]).iloc[0]
    besth=m[(m.split=="holdout") & (m.model.isin(model_names))].sort_values(["log_loss","accuracy"]).iloc[0]
    manuscript=f"""# Phase 34 Manuscript — Alternative NIFTY D−6 Prediction Models

## Abstract
Phase 34 tested eight model families not used as primary models in Phase 33: XGBoost, ExtraTrees, histogram gradient boosting, RBF-SVM, elastic-net logistic regression, a point-in-time HMM regime model, a compact Transformer and a compact temporal-convolution model. Two fixed ensembles were also evaluated. The reference remained exactly 10:00 IST on six calendar days before expiry, with chronological development, validation and untouched 2026 holdout periods.

## Sample
{len(ev)} eligible events: {len(train)} development, {len(val)} validation and {len(hold)} holdout.

## Methods
All tabular models use the same Phase-33 point-in-time event feature set. Sequence models use 30 completed NIFTY sessions before each reference. The HMM is fitted only to daily data strictly before each test reference. No hyperparameter tuning was performed on the holdout.

## Results
The best new-family validation model by log loss was **{bestv['model']}** (accuracy {bestv['accuracy']:.3f}, log loss {bestv['log_loss']:.4f}). The best new-family holdout model by log loss was **{besth['model']}** (accuracy {besth['accuracy']:.3f}, log loss {besth['log_loss']:.4f}). Exact model-by-model results are in PHASE34_DECISION_TABLE.csv and model_metrics.csv.

## Statistical inference
Bootstrap confidence intervals and sign-flip tests were computed for model-signed expiry-horizon log returns. These diagnostics are predictive diagnostics, not executable option P&L.

## Decision
No model is promoted directly to trading from this phase. Any candidate that appears attractive must survive a separate frozen direction-overlay backtest against the canonical strategy with Paytm Money brokerage, statutory charges, slippage, fill constraints and expiry-gap handling.

## Limitations
The event sample remains small, the 2026 holdout contains only 22 events, and deep sequence models have limited statistical degrees of freedom. Public option-chain and sentiment coverage is incomplete and therefore cannot be interpreted as universally available live information.

## Conclusion
Phase 34 provides an expanded model-family comparison without changing the canonical strategy. The research stops here unless a new phase is explicitly registered for a trading overlay or a materially different forecasting family.
"""
    (OUT/"PHASE34_ALTERNATIVE_PREDICTION_MANUSCRIPT.md").write_text(manuscript,encoding="utf-8")

    print(json.dumps(meta,indent=2))
    print(pd.DataFrame(metrics).to_string(index=False))

if __name__=="__main__":
    main()
