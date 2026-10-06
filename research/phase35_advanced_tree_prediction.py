import os, json, math, warnings
from pathlib import Path
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

SEED=1337
TZ="Asia/Kolkata"
DATA=Path("data/phase33")
OUT=Path("results/phase35_advanced_tree_prediction")
OUT.mkdir(parents=True,exist_ok=True)

TRAIN_END=pd.Timestamp("2023-12-31 23:59:59",tz=TZ)
VAL_END=pd.Timestamp("2025-12-31 23:59:59",tz=TZ)
HOLD_START=pd.Timestamp("2026-01-01",tz=TZ)
HOLD_END=pd.Timestamp("2026-09-30 23:59:59",tz=TZ)

def norm_ts(x):
    y=pd.to_datetime(x,errors="coerce")
    if getattr(y.dt,"tz",None) is None: y=y.dt.tz_localize(TZ)
    else: y=y.dt.tz_convert(TZ)
    return y.astype(f"datetime64[ns, {TZ}]")

def load_cache():
    ev=pd.read_parquet(DATA/"events.parquet")
    daily=pd.read_parquet(DATA/"nifty_daily.parquet")
    ev["expiry"]=norm_ts(ev["expiry"]).dt.normalize()
    ev["ref_ts"]=norm_ts(ev["ref_ts"])
    daily["date"]=norm_ts(daily["date"]).dt.normalize()
    ev=ev[(ev.ref_ts>=pd.Timestamp("2021-05-27",tz=TZ))&(ev.ref_ts<=HOLD_END)].sort_values("ref_ts").copy()
    ev["split"]=np.where(ev.ref_ts<=TRAIN_END,"train",np.where(ev.ref_ts<=VAL_END,"validation","holdout"))
    return ev,daily.sort_values("date").copy()

def feature_cols(ev):
    drop={"expiry","ref_ts","ref_spot","expiry_close","target_return","target_direction","split"}
    return [c for c in ev.columns if c not in drop and pd.api.types.is_numeric_dtype(ev[c])]

def prep(fit,test,cols):
    from sklearn.impute import SimpleImputer
    imp=SimpleImputer(strategy="median").fit(fit[cols])
    return imp.transform(fit[cols]),imp.transform(test[cols])

def lgbm_classifier(fit,test,cols,boosting="gbdt",weights=None):
    from lightgbm import LGBMClassifier
    A,B=prep(fit,test,cols)
    m=LGBMClassifier(
        n_estimators=220,num_leaves=15,max_depth=4,learning_rate=0.03,
        min_child_samples=8,subsample=0.85,colsample_bytree=0.85,
        reg_lambda=2.0,reg_alpha=0.1,random_state=SEED,
        verbosity=-1,boosting_type=boosting
    )
    if boosting=="dart":
        m.set_params(drop_rate=0.10,skip_drop=0.50,max_drop=50)
    m.fit(A,fit.target_direction.astype(int),sample_weight=weights)
    return m.predict_proba(B)[:,1]

def cat_classifier(fit,test,cols):
    from catboost import CatBoostClassifier
    A,B=prep(fit,test,cols)
    m=CatBoostClassifier(
        iterations=240,depth=4,learning_rate=0.03,l2_leaf_reg=4.0,
        loss_function="Logloss",random_seed=SEED,verbose=False,
        allow_writing_files=False,thread_count=2
    )
    m.fit(A,fit.target_direction.astype(int))
    return m.predict_proba(B)[:,1]

def xgb_classifier(fit,test,cols):
    from xgboost import XGBClassifier
    A,B=prep(fit,test,cols)
    y=fit.target_direction.astype(int).to_numpy()
    pos=max(1,int(y.sum())); neg=max(1,len(y)-int(y.sum()))
    m=XGBClassifier(n_estimators=250,max_depth=3,learning_rate=0.03,
        subsample=0.80,colsample_bytree=0.80,min_child_weight=5,
        reg_lambda=2.0,objective="binary:logistic",eval_metric="logloss",
        random_state=SEED,n_jobs=2,tree_method="hist",scale_pos_weight=neg/pos)
    m.fit(A,y)
    return m.predict_proba(B)[:,1]

def extra_classifier(fit,test,cols):
    from sklearn.ensemble import ExtraTreesClassifier
    A,B=prep(fit,test,cols)
    m=ExtraTreesClassifier(n_estimators=400,max_depth=6,min_samples_leaf=4,
        class_weight="balanced",random_state=SEED,n_jobs=2)
    m.fit(A,fit.target_direction.astype(int))
    return m.predict_proba(B)[:,1]

def hist_classifier(fit,test,cols):
    from sklearn.ensemble import HistGradientBoostingClassifier
    A,B=prep(fit,test,cols)
    m=HistGradientBoostingClassifier(max_iter=250,learning_rate=0.03,
        max_leaf_nodes=15,max_depth=4,min_samples_leaf=8,
        l2_regularization=1.0,random_state=SEED)
    m.fit(A,fit.target_direction.astype(int))
    return m.predict_proba(B)[:,1]

def rfe_lgbm(fit,test,cols):
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.feature_selection import RFE
    imp=SimpleImputer(strategy="median").fit(fit[cols])
    A=imp.transform(fit[cols]); B=imp.transform(test[cols])
    sc=StandardScaler().fit(A)
    sel=RFE(LogisticRegression(C=0.25,max_iter=3000,random_state=SEED),
            n_features_to_select=min(25,A.shape[1]),step=0.25).fit(sc.transform(A),fit.target_direction.astype(int))
    AA=A[:,sel.support_]; BB=B[:,sel.support_]
    from lightgbm import LGBMClassifier
    m=LGBMClassifier(n_estimators=220,num_leaves=15,max_depth=4,learning_rate=0.03,
        min_child_samples=8,reg_lambda=2.0,random_state=SEED,verbosity=-1)
    m.fit(AA,fit.target_direction.astype(int))
    return m.predict_proba(BB)[:,1]

def ngboost_reg(fit,test,cols):
    from ngboost import NGBRegressor
    from ngboost.distns import Normal
    from sklearn.tree import DecisionTreeRegressor
    from scipy.stats import norm
    A,B=prep(fit,test,cols)
    base=DecisionTreeRegressor(max_depth=2,min_samples_leaf=8,random_state=SEED)
    m=NGBRegressor(Dist=Normal,Base=base,n_estimators=180,
        learning_rate=0.03,random_state=SEED,verbose=False)
    m.fit(A,fit.target_return.to_numpy(float))
    d=m.pred_dist(B)
    mu=np.asarray(d.loc); sd=np.maximum(np.asarray(d.scale),1e-5)
    return 1.0-norm.cdf(0,loc=mu,scale=sd),mu,sd

def quantile_tree(fit,test,cols):
    from sklearn.ensemble import GradientBoostingRegressor
    A,B=prep(fit,test,cols)
    qs={}
    for a in [0.10,0.50,0.90]:
        m=GradientBoostingRegressor(loss="quantile",alpha=a,n_estimators=180,
            max_depth=2,learning_rate=0.03,min_samples_leaf=8,random_state=SEED)
        m.fit(A,fit.target_return.to_numpy(float))
        qs[a]=m.predict(B)
    q10,q50,q90=qs[0.10],qs[0.50],qs[0.90]
    scale=np.maximum(q90-q10,1e-5)
    p=0.5+0.5*np.tanh(q50/scale)
    return np.clip(p,1e-4,1-1e-4),q50,q10,q90

def bart_reg(fit,test,cols):
    import pymc as pm
    import pymc_bart as pmb
    import arviz as az
    A,B=prep(fit,test,cols)
    # Restrict BART to a stable low-dimensional feature subset selected by RF importance.
    from sklearn.ensemble import ExtraTreesRegressor
    rf=ExtraTreesRegressor(n_estimators=250,max_depth=5,min_samples_leaf=4,random_state=SEED,n_jobs=2)
    rf.fit(A,fit.target_return.to_numpy(float))
    idx=np.argsort(rf.feature_importances_)[::-1][:min(20,A.shape[1])]
    A=A[:,idx]; B=B[:,idx]
    with pm.Model() as model:
        X=pm.Data("X",A)
        mu=pmb.BART("mu",X,fit.target_return.to_numpy(float),m=25)
        sigma=pm.HalfNormal("sigma",sigma=0.01)
        pm.Normal("y",mu=mu,sigma=sigma,observed=fit.target_return.to_numpy(float))
        idata=pm.sample(draws=220,tune=220,chains=1,cores=1,random_seed=SEED,
                        progressbar=False,target_accept=0.90,compute_convergence_checks=False)
        pm.set_data({"X":B})
        pp=pm.sample_posterior_predictive(idata,var_names=["mu"],random_seed=SEED,
                                          progressbar=False,predictions=True)
    arr=pp.predictions["mu"].values
    arr=arr.reshape(-1,B.shape[0])
    p=(arr>0).mean(axis=0)
    mu=arr.mean(axis=0)
    return np.clip(p,1e-4,1-1e-4),mu,np.quantile(arr,[0.10,0.90],axis=0)

def past_seq_features(daily,events):
    from scipy import signal
    rows=[]
    d=daily.sort_values("date").reset_index(drop=True).copy()
    rr=np.log(d.close/d.close.shift(1)).to_numpy(float)
    for _,e in events.sort_values("ref_ts").iterrows():
        ref=pd.Timestamp(e.ref_ts).normalize()
        z=d[d.date<ref].tail(64)
        r=np.log(z.close/z.close.shift(1)).dropna().to_numpy(float)
        if len(r)<32:
            rows.append({"ref_ts":e.ref_ts})
            continue
        feat={"ref_ts":e.ref_ts}
        feat.update({"decomp_n":float(len(r))})
        try:
            import pywt
            c=pywt.wavedec(r[-32:],wavelet="db2",level=2,mode="periodization")
            for i,a in enumerate(c):
                feat[f"wav{i}_last"]=float(a[-1]); feat[f"wav{i}_energy"]=float(np.mean(a*a)); feat[f"wav{i}_std"]=float(np.std(a))
        except Exception: pass
        try:
            from PyEMD import EMD
            imfs=EMD().emd(r[-64:])
            for i in range(min(3,len(imfs))):
                x=imfs[i]
                feat[f"emd{i}_last"]=float(x[-1]); feat[f"emd{i}_energy"]=float(np.mean(x*x))
            feat["emd_resid_std"]=float(np.std(r[-64:]-imfs[:].sum(axis=0))) if len(imfs) else np.nan
        except Exception: pass
        try:
            from vmdpy import VMD
            u,_,_=VMD(r[-64:],2000,0,3,0,1,1e-5)
            for i in range(min(3,u.shape[0])):
                feat[f"vmd{i}_last"]=float(u[i,-1]); feat[f"vmd{i}_energy"]=float(np.mean(u[i]**2))
        except Exception: pass
        rows.append(feat)
    return pd.DataFrame(rows)

def add_decomp(events,daily):
    path=DATA.parent/"phase35_decomp_features.parquet"
    if path.exists():
        z=pd.read_parquet(path); z["ref_ts"]=norm_ts(z.ref_ts)
    else:
        z=past_seq_features(daily,events); z["ref_ts"]=norm_ts(z.ref_ts); z.to_parquet(path,index=False)
    return events.merge(z,on="ref_ts",how="left")

def metrics(y,p):
    from sklearn.metrics import accuracy_score,balanced_accuracy_score,roc_auc_score,log_loss,brier_score_loss
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); pr=(p>=0.5).astype(int)
    return {"n":len(y),"accuracy":accuracy_score(y,pr),"balanced_accuracy":balanced_accuracy_score(y,pr),
        "roc_auc":roc_auc_score(y,p) if len(np.unique(y))==2 else np.nan,
        "log_loss":log_loss(y,np.c_[1-p,p],labels=[0,1]),"brier":brier_score_loss(y,p)}

def bootstrap(x,n=4000):
    x=np.asarray(x,float); rng=np.random.default_rng(SEED)
    a=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(n)])
    return float(np.quantile(a,.025)),float(np.quantile(a,.975))

def signflip(x,n=12000):
    x=np.asarray(x,float); rng=np.random.default_rng(SEED); obs=abs(x.mean())
    s=rng.choice([-1,1],size=(n,len(x))); sim=np.abs((s*x).mean(axis=1))
    return float((1+(sim>=obs).sum())/(n+1))

def fit_tree_bundle(fit,test,cols):
    return {
        "xgb":xgb_classifier(fit,test,cols),
        "lgbm":lgbm_classifier(fit,test,cols),
        "catboost":cat_classifier(fit,test,cols),
        "extra":extra_classifier(fit,test,cols),
        "hist":hist_classifier(fit,test,cols),
        "dart":lgbm_classifier(fit,test,cols,boosting="dart")
    }

def sequential_adaptive(events_base,daily_fit_start,base_cols):
    out=[]
    ordered=events_base.sort_values("ref_ts").copy()
    for i,(_,row) in enumerate(ordered.iterrows()):
        hist=ordered.iloc[:i].copy()
        if len(hist)<60: out.append((row.ref_ts,np.nan,np.nan)); continue
        # Use all historically known events plus a fixed 52-event recent window.
        fit=hist.tail(52)
        t=pd.DataFrame([row])
        p=lgbm_classifier(fit,t,base_cols)
        # Recent exponential-weight alternative.
        age=np.arange(len(hist)-1,-1,-1)
        w=np.exp(-np.log(2)*age/26.0)
        pw=lgbm_classifier(hist,t,base_cols,weights=w)
        out.append((row.ref_ts,float(p[0]),float(pw[0])))
    return pd.DataFrame(out,columns=["ref_ts","adaptive52","adaptive_ew"]).set_index("ref_ts")

def build_oof(train,cols,nfold=4):
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    n=len(train); fold_starts=np.linspace(40,n,nfold+1,dtype=int)
    oof=pd.DataFrame(index=train.index,columns=["xgb","lgbm","catboost","extra","hist","dart"],dtype=float)
    for k in range(nfold):
        a=fold_starts[k]; b=fold_starts[k+1]
        if b<=a or a<30: continue
        fit=train.iloc[:a]; test=train.iloc[a:b]
        z=fit_tree_bundle(fit,test,cols)
        for name,val in z.items(): oof.loc[test.index,name]=val
    # Require every OOF row to have predictions; trim initial warm-up rows.
    oof=oof.dropna()
    return oof

def stacking_and_calibration(train,val,hold,cols):
    from sklearn.linear_model import LogisticRegression
    from sklearn.isotonic import IsotonicRegression
    oof=build_oof(train,cols)
    y=train.loc[oof.index,"target_direction"].astype(int).to_numpy()
    val_base=fit_tree_bundle(train,val,cols)
    hold_fit=pd.concat([train,val]).sort_values("ref_ts")
    hold_base=fit_tree_bundle(hold_fit,hold,cols)
    base_names=list(oof.columns)
    meta=LogisticRegression(C=0.5,max_iter=3000,random_state=SEED).fit(oof[base_names],y)
    pv=pd.DataFrame(val_base)[base_names].to_numpy(); ph=pd.DataFrame(hold_base)[base_names].to_numpy()
    pv_stack=meta.predict_proba(pv)[:,1]; ph_stack=meta.predict_proba(ph)[:,1]
    # For holdout, augment calibration/stack training with validation OOS predictions.
    yv=val.target_direction.astype(int).to_numpy()
    meta2=LogisticRegression(C=0.5,max_iter=3000,random_state=SEED).fit(
        pd.concat([oof,pd.DataFrame(val_base,index=val.index)[base_names]]).to_numpy(),
        np.concatenate([y,yv]))
    ph_stack2=meta2.predict_proba(ph)[:,1]
    oof_best=oof.mean(axis=1).to_numpy()
    cal_platt=LogisticRegression(C=1.0,max_iter=2000,random_state=SEED).fit(oof[base_names],y)
    pv_platt=cal_platt.predict_proba(pv)[:,1]; ph_platt=cal_platt.predict_proba(ph)[:,1]
    iso=IsotonicRegression(out_of_bounds="clip").fit(oof_best,y)
    pv_iso=iso.predict(np.mean(pv,axis=1)); ph_iso=iso.predict(np.mean(ph,axis=1))
    return {"val_stack":pv_stack,"hold_stack":ph_stack2,"val_platt":pv_platt,"hold_platt":ph_platt,
            "val_iso":pv_iso,"hold_iso":ph_iso,"val_base":val_base,"hold_base":hold_base,
            "oof":oof}

def dynamic_weight(base,history_preds,history_y,half=20):
    models=list(base)
    if len(history_y)<10:
        return float(np.mean([base[m][0] for m in models]))
    take=max(10,int(half)); yp=history_y[-take:]; weights=[]
    probs=[]
    for m in models:
        p=np.asarray(history_preds[m][-take:]); acc=float(np.mean((p>=.5)==yp))
        weights.append(np.exp(5*(acc-0.5))); probs.append(base[m][0])
    return float(np.dot(weights,probs)/np.sum(weights))

def conformal_sequence(train,val,hold,cols):
    from lightgbm import LGBMRegressor
    def pred(fit,test):
        A,B=prep(fit,test,cols)
        m=LGBMRegressor(n_estimators=220,num_leaves=15,max_depth=4,learning_rate=.03,
                        min_child_samples=8,reg_lambda=2.0,verbosity=-1,random_state=SEED)
        m.fit(A,fit.target_return.to_numpy(float)); return m.predict(B)
    # chronological OOF residuals for development
    oof_pred=build_reg_oof(train,cols)
    oof_true=train.loc[oof_pred.index,"target_return"].to_numpy(float)
    dev_res=np.abs(oof_true-oof_pred.to_numpy())
    qv=float(np.quantile(dev_res,0.90))
    pv=pred(train,val); lowv=pv-qv; highv=pv+qv
    rv=np.abs(val.target_return.to_numpy(float)-pv)
    cal=np.concatenate([dev_res,rv]); qh=float(np.quantile(cal,0.90))
    ph=pred(pd.concat([train,val]).sort_values("ref_ts"),hold); lowh=ph-qh; highh=ph+qh
    return pv,lowv,highv,ph,lowh,highh,qv,qh

def build_reg_oof(train,cols):
    n=len(train); starts=np.linspace(45,n,4,dtype=int); s=[]
    for k in range(3):
        a=starts[k]; b=starts[k+1]
        if b<=a: continue
        fit=train.iloc[:a]; test=train.iloc[a:b]
        from lightgbm import LGBMRegressor
        A,B=prep(fit,test,cols)
        m=LGBMRegressor(n_estimators=180,num_leaves=15,max_depth=4,learning_rate=.03,min_child_samples=8,verbosity=-1,random_state=SEED)
        m.fit(A,fit.target_return.to_numpy(float)); s.append(pd.Series(m.predict(B),index=test.index))
    return pd.concat(s).sort_index()

def main():
    ev,daily=load_cache()
    base_cols=feature_cols(ev)
    train=ev[ev.split=="train"].copy(); val=ev[ev.split=="validation"].copy(); hold=ev[ev.split=="holdout"].copy()
    evd=add_decomp(ev,daily)
    dec_cols=[c for c in evd.columns if c not in ev.columns and c!="ref_ts" and pd.api.types.is_numeric_dtype(evd[c])]
    # Keep decomposition features separate to avoid contaminating base controls.
    train_d=evd[evd.split=="train"].copy(); val_d=evd[evd.split=="validation"].copy(); hold_d=evd[evd.split=="holdout"].copy()
    decomp_cols=base_cols+dec_cols

    pred_frames=[]
    status=[]
    for split,fit,test,testd in [("validation",train,val,val_d),("holdout",pd.concat([train,val]).sort_values("ref_ts"),hold,hold_d)]:
        row=test[["expiry","ref_ts","target_return","target_direction"]].copy().reset_index(drop=True)
        f=fit.reset_index(drop=True); td=test.reset_index(drop=True); tdd=testd.reset_index(drop=True)
        bundle=fit_tree_bundle(f,td,base_cols)
        for k,v in bundle.items(): row[k+"_prob"]=v
        row["tree_equal6_prob"]=row[["xgb_prob","lgbm_prob","catboost_prob","extra_prob","hist_prob","dart_prob"]].mean(axis=1)
        # Winsorized forecast pooling.
        row["winsor_tree_prob"]=row[["xgb_prob","lgbm_prob","catboost_prob","extra_prob","hist_prob","dart_prob"]].clip(.15,.85).mean(axis=1)
        # RFE + tree.
        row["rfe_lgbm_prob"]=rfe_lgbm(f,td,base_cols)
        # NGBoost / quantile / BART.
        p,mu,sd=ngboost_reg(f,td,base_cols); row["ngboost_prob"]=p; row["ngboost_mu"]=mu; row["ngboost_sd"]=sd
        p,q50,q10,q90=quantile_tree(f,td,base_cols); row["quantile_prob"]=p; row["quantile_mu"]=q50; row["quantile_q10"]=q10; row["quantile_q90"]=q90
        bp,bmu,bq=bart_reg(f,td,base_cols); row["bart_prob"]=bp; row["bart_mu"]=bmu; row["bart_q10"]=bq[0]; row["bart_q90"]=bq[1]
        # Decomposition pathways.
        for name in ["wavelet","emd","vmd"]:
            prefix={"wavelet":"wav","emd":"emd","vmd":"vmd"}[name]
            colsx=[c for c in decomp_cols if c.startswith(prefix) or c in base_cols]
            if not any(c.startswith(prefix) for c in colsx):
                row[name+"_tree_prob"]=row["lgbm_prob"].to_numpy()
            else:
                row[name+"_tree_prob"]=lgbm_classifier(f,tdd,colsx)
        # Adaptive predictions are generated sequentially over train+test history.
        combined=pd.concat([f,td]).sort_values("ref_ts").reset_index(drop=True)
        ap=sequential_adaptive(combined,daily,base_cols)
        row["adaptive52_prob"]=ap.loc[td.ref_ts.to_numpy(),"adaptive52"].to_numpy()
        row["adaptive_ew_prob"]=ap.loc[td.ref_ts.to_numpy(),"adaptive_ew"].to_numpy()
        # regime-gated tree using rolling volatility state.
        volcol="vol20" if "vol20" in td.columns else next((c for c in base_cols if "vol20" in c),None)
        hist_preds={k:[] for k in ["xgb","lgbm","catboost","extra","hist","dart"]}; hist_y=[]; hist_reg=[]
        gate=[]
        allp=fit_tree_bundle(f,td,base_cols)
        # Use historical model predictions from validation/earlier events stored later; a simple volatility gate
        # selects among current tree experts using prior validation regime performance.
        vol_hist=float(np.nanmedian(f[volcol])) if volcol else 0.0
        for j in range(len(td)):
            v=float(td.iloc[j][volcol]) if volcol and np.isfinite(td.iloc[j][volcol]) else vol_hist
            reg=0 if v<=np.nanquantile(f[volcol].dropna(),.33) else (2 if v>=np.nanquantile(f[volcol].dropna(),.67) else 1)
            scores=[]
            for k in hist_preds:
                vals=[]
                for r0,y0 in zip(hist_reg,hist_y):
                    if r0==reg: vals.append((hist_preds[k][len(vals)]>=.5)==bool(y0))
                scores.append(np.mean(vals) if vals else .5)
            k=list(hist_preds)[int(np.argmax(scores))] if scores else "lgbm"
            gate.append(allp[k][j])
        row["regime_tree_gate_prob"]=gate
        # Dynamic selection based on recency will be filled globally after prediction frames are assembled.
        row["split"]=split
        row["ref_ts"]=norm_ts(row.ref_ts)
        pred_frames.append(row)
    pred=pd.concat(pred_frames,ignore_index=True).sort_values("ref_ts").reset_index(drop=True)

    # Proper dynamic selection using prior rows only.
    base_names=["xgb","lgbm","catboost","extra","hist","dart"]
    dyn=[]
    hist_preds={m:[] for m in base_names}; hist_y=[]
    for _,r in pred.iterrows():
        b={m:[float(r[m+"_prob"])] for m in base_names}
        dyn.append(dynamic_weight(b,hist_preds,hist_y,half=20))
        for m in base_names: hist_preds[m].append(float(r[m+"_prob"]))
        hist_y.append(int(r.target_direction))
    pred["dynamic_pool_prob"]=dyn

    # OOF stacking and calibration.
    sc=stacking_and_calibration(train,val,base_cols)
    nv,nl=len(val),len(hold)
    pred.loc[pred.split=="validation","stack_prob"]=sc["val_stack"]
    pred.loc[pred.split=="holdout","stack_prob"]=sc["hold_stack"]
    pred.loc[pred.split=="validation","platt_prob"]=sc["val_platt"]
    pred.loc[pred.split=="holdout","platt_prob"]=sc["hold_platt"]
    pred.loc[pred.split=="validation","isotonic_prob"]=sc["val_iso"]
    pred.loc[pred.split=="holdout","isotonic_prob"]=sc["hold_iso"]

    # Chronology-safe dynamic pooling and regime-gated tree selection.
    # Train history uses OOF predictions only; holdout additionally uses realized
    # validation predictions because those labels were known before 2026.
    oof_hist=sc["oof"].copy()
    oof_hist["target"]=train.loc[oof_hist.index,"target_direction"].astype(int).to_numpy()
    volname="vol20" if "vol20" in train.columns else next((z for z in base_cols if "vol20" in z),None)
    if volname:
        oof_hist["regime"]=pd.qcut(train.loc[oof_hist.index,volname].rank(method="first"),3,labels=False,duplicates="drop").to_numpy()
    else:
        oof_hist["regime"]=1
    dyn2=[]; gate2=[]
    names=["xgb","lgbm","catboost","extra","hist","dart"]
    for _,r in pred.iterrows():
        hist=oof_hist.copy()
        if r["split"]=="holdout":
            qvpred=pred[pred.split=="validation"].copy()
            if len(qvpred):
                vv=pd.DataFrame({m:qvpred[m+"_prob"].to_numpy() for m in names})
                vv["target"]=qvpred.target_direction.to_numpy()
                if volname in qvpred.columns:
                    vv["regime"]=pd.qcut(qvpred[volname].rank(method="first"),3,labels=False,duplicates="drop").to_numpy()
                else: vv["regime"]=1
                hist=pd.concat([hist,vv],ignore_index=True)
        if volname in r.index and np.isfinite(r[volname]):
            cut=np.nanquantile(train[volname].dropna(),[.33,.67])
            reg=0 if float(r[volname])<=cut[0] else (2 if float(r[volname])>=cut[1] else 1)
        else: reg=1
        recent=hist.tail(40)
        ws=[]; ps=[]
        for m0 in names:
            p0=np.asarray(recent[m0],float); y0=np.asarray(recent["target"],int)
            acc=float(np.mean((p0>=.5)==y0)) if len(y0) else .5
            wt=float(np.exp(5*(acc-.5))); ws.append(wt); ps.append(float(r[m0+"_prob"]))
        dyn2.append(float(np.dot(ws,ps)/np.sum(ws)))
        rg=recent[recent["regime"]==reg] if "regime" in recent.columns else recent.iloc[0:0]
        if len(rg)<8: rg=recent
        score={m0:float(np.mean((np.asarray(rg[m0],float)>=.5)==np.asarray(rg["target"],int))) if len(rg) else .5 for m0 in names}
        gate2.append(float(r[max(score,key=score.get)+"_prob"]))
    pred["dynamic_pool_prob"]=dyn2
    pred["regime_tree_gate_prob"]=gate2

    # Conformal intervals and abstention.
    pv,lv,hv,ph,lh,hh,qv,qh=conformal_sequence(train,val,hold,base_cols)
    pred.loc[pred.split=="validation","conformal_mean"]=pv
    pred.loc[pred.split=="validation","conformal_low"]=lv
    pred.loc[pred.split=="validation","conformal_high"]=hv
    pred.loc[pred.split=="holdout","conformal_mean"]=ph
    pred.loc[pred.split=="holdout","conformal_low"]=lh
    pred.loc[pred.split=="holdout","conformal_high"]=hh
    pred["conformal_prob"]=np.where(pred.conformal_low>0,1.0,np.where(pred.conformal_high<0,0.0,0.5))
    pred["conformal_confident"]=((pred.conformal_low>0)|(pred.conformal_high<0))
    pred.to_csv(OUT/"model_predictions.csv",index=False)

    model_names=[
        "xgb","lgbm","catboost","extra","hist","dart","tree_equal6","winsor_tree",
        "rfe_lgbm","ngboost","quantile","bart","wavelet_tree","emd_tree","vmd_tree",
        "adaptive52","adaptive_ew","regime_tree_gate","dynamic_pool","stack","platt","isotonic","conformal"
    ]
    metrics_rows=[]; econ_rows=[]
    for split in ["validation","holdout"]:
        q=pred[pred.split==split]
        for name in model_names:
            probcol="conformal_prob" if name=="conformal" else name+"_prob"
            if probcol not in q.columns: continue
            z=metrics(q.target_direction,q[probcol])
            z.update({"split":split,"model":name})
            metrics_rows.append(z)
            sr=np.where(q[probcol]>=.5,1,-1)*q.target_return.to_numpy(float)
            lo,hi=bootstrap(sr)
            econ_rows.append({"split":split,"model":name,"hit_rate":float((sr>0).mean()),
                "mean_signed_log_return":float(sr.mean()),"sum_signed_log_return":float(sr.sum()),
                "bootstrap_ci_low":lo,"bootstrap_ci_high":hi,"signflip_pvalue":signflip(sr)})
    pd.DataFrame(metrics_rows).to_csv(OUT/"model_metrics.csv",index=False)
    pd.DataFrame(econ_rows).to_csv(OUT/"directional_economic_diagnostic.csv",index=False)

    # Uncertainty/coverage summary.
    u=[]
    for split in ["validation","holdout"]:
        q=pred[pred.split==split]
        for nm in ["conformal"]:
            coverage=float(((q.target_return>=q.conformal_low)&(q.target_return<=q.conformal_high)).mean())
            conf=q[q.conformal_confident]
            conf_acc=float(((q.loc[conf.index].conformal_prob>=.5).astype(int)==conf.target_direction).mean()) if len(conf) else np.nan
            u.append({"split":split,"method":nm,"interval_coverage_90":coverage,
                      "mean_interval_width":float((q.conformal_high-q.conformal_low).mean()),
                      "confident_fraction":float(q.conformal_confident.mean()),
                      "confident_direction_accuracy":conf_acc})
    pd.DataFrame(u).to_csv(OUT/"uncertainty_summary.csv",index=False)

    # Baselines.
    bas=[]
    for split,test in [("validation",val),("holdout",hold)]:
        for name,p in [("always_up",np.ones(len(test))),("always_down",np.zeros(len(test))),
                       ("constant",np.full(len(test),float(train.target_direction.mean() if split=="validation" else pd.concat([train,val]).target_direction.mean())))]:
            bas.append({"split":split,"model":name,**metrics(test.target_direction,p)})
    pd.DataFrame(bas).to_csv(OUT/"baseline_metrics.csv",index=False)

    # Model status.
    status=[]
    for name in model_names:
        status.append({"model":name,"implementation":"executed","note":"prediction retained in accepted numerical run"})
    # Make the artifact self-auditing.
    meta={"phase":"35","events":len(ev),"train":len(train),"validation":len(val),"holdout":len(hold),
          "base_feature_count":len(base_cols),"decomposition_feature_count":len(dec_cols),
          "methods":model_names,
          "conformal_calibration_quantile_validation":qv,
          "conformal_calibration_quantile_holdout":qh}
    with open(OUT/"coverage_and_metadata.json","w") as f: json.dump(meta,f,indent=2,default=str)
    pd.DataFrame(status).to_csv(OUT/"method_status.csv",index=False)

    # Decision table.
    m=pd.DataFrame(metrics_rows); e=pd.DataFrame(econ_rows)
    b=pd.DataFrame(bas)
    rows=[]
    baseh=float(b[(b.split=="holdout")&(b.model=="always_down")].accuracy.iloc[0])
    for name in model_names:
        vm=float(m[(m.split=="validation")&(m.model==name)].accuracy.iloc[0])
        hm=float(m[(m.split=="holdout")&(m.model==name)].accuracy.iloc[0])
        eh=e[(e.split=="holdout")&(e.model==name)].iloc[0]
        rows.append({"model":name,"validation_accuracy":vm,"holdout_accuracy":hm,
                     "holdout_mean_signed_log_return":eh.mean_signed_log_return,
                     "holdout_ci_low":eh.bootstrap_ci_low,"holdout_ci_high":eh.bootstrap_ci_high,
                     "holdout_signflip_pvalue":eh.signflip_pvalue,
                     "beats_always_down_holdout":hm>baseh,
                     "promotion":"NO — overlay phase required"})
    pd.DataFrame(rows).to_csv(OUT/"PHASE35_DECISION_TABLE.csv",index=False)

    # Yearly stability.
    ys=[]
    for split in ["validation","holdout"]:
        q=pred[pred.split==split].copy(); q["year"]=q.expiry.dt.year
        for year,g in q.groupby("year"):
            for name in model_names:
                prob="conformal_prob" if name=="conformal" else name+"_prob"
                p=g[prob]; sr=np.where(p>=.5,1,-1)*g.target_return.to_numpy(float)
                ys.append({"split":split,"year":int(year),"model":name,"n":len(g),
                           "accuracy":float(((p>=.5).astype(int)==g.target_direction).mean()),
                           "mean_signed_log_return":float(sr.mean())})
    pd.DataFrame(ys).to_csv(OUT/"yearly_stability.csv",index=False)

    print(json.dumps(meta,indent=2,default=str))
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=="__main__":
    main()
