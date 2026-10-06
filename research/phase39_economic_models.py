# Phase 39 Step 3 — chronological economic-margin models on fixed opportunities
import json, math, warnings
from pathlib import Path
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import BayesianRidge, LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
from sklearn.decomposition import PCA

SEED=1337
ROOT=Path(".")
DATA=ROOT/"results/phase39_features/point_in_time_features.csv"
LEDGER=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
OUT=ROOT/"results/phase39_models"
OUT.mkdir(parents=True,exist_ok=True)

LABELS={"control_direction","control_net_rupees","delta_pnl_call_minus_put","expiry","entry_ts","split"}
WARMUP=100
BATCH=20

def select_features(df):
    dev=df[df.split=="development"]
    cols=[]
    for c in df.columns:
        if c in LABELS or not pd.api.types.is_numeric_dtype(df[c]):
            continue
        miss=float(dev[c].isna().mean())
        nun=int(dev[c].nunique(dropna=True))
        if miss <= 0.50 and nun >= 5:
            cols.append(c)
    return cols

def prep_fit_predict(train, test, features):
    imp=SimpleImputer(strategy="median", add_indicator=False)
    A=imp.fit_transform(train[features])
    B=imp.transform(test[features])
    sc=StandardScaler()
    return sc.fit_transform(A), sc.transform(B)

def fit_bayes(train,test,features):
    A,B=prep_fit_predict(train,test,features)
    m=BayesianRidge(alpha_1=1.0,alpha_2=1.0,lambda_1=1e-6,lambda_2=1e-6,max_iter=1000)
    m.fit(A,train.delta_pnl_call_minus_put.to_numpy(float))
    mu,sd=m.predict(B,return_std=True)
    return mu,np.maximum(sd,1.0)

def fit_crol(train,test,features):
    return fit_bayes(train,test,features)

def fit_bradley(train,test,features):
    A,B=prep_fit_predict(train,test,features)
    y=(train.delta_pnl_call_minus_put.to_numpy(float)>0).astype(int)
    m=LogisticRegression(C=0.50,class_weight="balanced",max_iter=2000,random_state=SEED)
    m.fit(A,y)
    p=m.predict_proba(B)[:,1]
    # Convert pairwise preference probability to a monotone pseudo-margin for comparison.
    scale=max(float(np.nanmedian(np.abs(train.delta_pnl_call_minus_put))),1.0)
    mu=(2*p-1)*scale
    sd=np.full(len(p),scale)
    return mu,sd

def fit_dynamic_logit(train,test,features):
    A,B=prep_fit_predict(train,test,features)
    y=(train.delta_pnl_call_minus_put.to_numpy(float)>0).astype(int)
    ages=np.arange(len(y))[::-1]
    w=np.exp(-0.010*ages)
    m=LogisticRegression(C=0.50,max_iter=2000,random_state=SEED)
    m.fit(A,y,sample_weight=w)
    p=m.predict_proba(B)[:,1]
    scale=max(float(np.nanmedian(np.abs(train.delta_pnl_call_minus_put))),1.0)
    return (2*p-1)*scale, np.full(len(p),scale)

def fit_gp(train,test,features):
    A,B=prep_fit_predict(train,test,features)
    ncomp=min(12,A.shape[1],max(2,A.shape[0]-1))
    pca=PCA(n_components=ncomp,random_state=SEED)
    A=pca.fit_transform(A); B=pca.transform(B)
    kernel=ConstantKernel(1.0,(1e-3,1e3))*Matern(length_scale=1.0,nu=2.5)+WhiteKernel(noise_level=1.0,noise_level_bounds=(1e-3,1e5))
    m=GaussianProcessRegressor(kernel=kernel,alpha=1e-6,normalize_y=True,random_state=SEED,n_restarts_optimizer=0)
    m.fit(A,train.delta_pnl_call_minus_put.to_numpy(float))
    mu,sd=m.predict(B,return_std=True)
    return mu,np.maximum(sd,1.0)

def fit_gam(train,test,features):
    pipe=Pipeline([
        ("imp",SimpleImputer(strategy="median")),
        ("scale",StandardScaler()),
        ("spline",SplineTransformer(n_knots=4,degree=2)),
        ("ridge",Ridge(alpha=10.0))
    ])
    pipe.fit(train[features],train.delta_pnl_call_minus_put.to_numpy(float))
    mu=pipe.predict(test[features])
    resid=train.delta_pnl_call_minus_put.to_numpy(float)-pipe.predict(train[features])
    sd=np.full(len(mu),max(float(np.std(resid,ddof=1)),1.0))
    return mu,sd

def fit_knn(train,test,features):
    A,B=prep_fit_predict(train,test,features)
    k=min(25,max(5,int(round(math.sqrt(len(train))))))
    m=KNeighborsRegressor(n_neighbors=k,weights="distance",p=2)
    m.fit(A,train.delta_pnl_call_minus_put.to_numpy(float))
    mu=m.predict(B)
    # Distance-derived uncertainty is conservative and only used for reporting.
    dist,_=m.kneighbors(B,n_neighbors=min(k,A.shape[0]))
    sd=np.maximum(np.std(dist,axis=1),0.25)*max(float(np.nanmedian(np.abs(train.delta_pnl_call_minus_put))),1.0)
    return mu,sd

MODELS={
    "CROL_bayesian_margin":fit_crol,
    "Bayesian_counterfactual_margin":fit_bayes,
    "Bradley_Terry_preference":fit_bradley,
    "Dynamic_Bayesian_logistic":fit_dynamic_logit,
    "Gaussian_process_margin":fit_gp,
    "Sparse_GAM_margin":fit_gam,
    "Weighted_kNN_analog":fit_knn,
}

def action_from_margin(control,mu,sd,margin,z):
    ctrl=np.asarray(control)
    mu=np.asarray(mu,float); sd=np.asarray(sd,float)
    out=ctrl.astype(object).copy()
    good_up=(mu-z*sd)>margin
    good_down=(mu+z*sd)<-margin
    put_override=(ctrl=="PUT")&good_up
    call_override=(ctrl=="CALL")&good_down
    out[put_override]="CALL"
    out[call_override]="PUT"
    return out

def action_net(action,df):
    return np.where(action=="CALL",df.call_net_rupees.to_numpy(float),df.put_net_rupees.to_numpy(float))

def max_drawdown(x):
    eq=np.cumsum(np.asarray(x,float))
    peak=np.maximum.accumulate(np.r_[0.0,eq])
    dd=np.r_[0.0,eq]-peak
    return float(dd.min())

def expiry_bootstrap(uplift,expiries,seed=SEED,n=5000):
    q=pd.DataFrame({"expiry":expiries,"uplift":uplift}).groupby("expiry",as_index=False)["uplift"].sum()
    vals=q.uplift.to_numpy(float)
    rng=np.random.default_rng(seed)
    sims=np.empty(n)
    for i in range(n):
        sims[i]=rng.choice(vals,size=len(vals),replace=True).sum()
    return float(q.uplift.sum()),float(np.quantile(sims,0.025)),float(np.quantile(sims,0.975)),int(len(vals))

def tune_threshold(oof):
    best=None
    for margin in [0.0,100.0,250.0,500.0,750.0,1000.0]:
        for z in [0.0,0.5,1.0,1.28,1.64]:
            a=action_from_margin(oof.control_direction.to_numpy(),oof.mu.to_numpy(),oof.sd.to_numpy(),margin,z)
            net=action_net(a,oof)
            uplift=net-oof.control_net_rupees.to_numpy(float)
            overrides=int(np.sum(a!=oof.control_direction.to_numpy()))
            if overrides<10:
                continue
            score=float(uplift.sum()-0.10*np.std(uplift)*math.sqrt(len(uplift)))
            key=(score,float(uplift.sum()),-overrides)
            if best is None or key>best[0]:
                best=(key,margin,z,overrides,float(uplift.sum()))
    if best is None:
        return 500.0,1.0
    return float(best[1]),float(best[2])

def run_model(name,fit_fn,df,features):
    dev=df[df.split=="development"].sort_values("entry_ts").reset_index(drop=True)
    val=df[df.split=="validation"].sort_values("entry_ts").reset_index(drop=True)
    preds=[]
    for start in range(WARMUP,len(dev),BATCH):
        end=min(start+BATCH,len(dev))
        train=dev.iloc[:start]
        test=dev.iloc[start:end]
        mu,sd=fit_fn(train,test,features)
        tmp=test[["entry_ts","expiry","split","control_direction","control_net_rupees","call_net_rupees","put_net_rupees","delta_pnl_call_minus_put"]].copy()
        tmp["model"]=name; tmp["mu"]=mu; tmp["sd"]=sd
        preds.append(tmp)
    oof=pd.concat(preds,ignore_index=True) if preds else pd.DataFrame()
    if oof.empty:
        raise RuntimeError(f"no development OOF predictions for {name}")
    margin,z=tune_threshold(oof)
    # Refit through all development and predict validation in chronological expanding batches.
    vpred=[]
    for start in range(0,len(val),BATCH):
        end=min(start+BATCH,len(val))
        test=val.iloc[start:end]
        mu,sd=fit_fn(dev,test,features)
        tmp=test[["entry_ts","expiry","split","control_direction","control_net_rupees","call_net_rupees","put_net_rupees","delta_pnl_call_minus_put"]].copy()
        tmp["model"]=name; tmp["mu"]=mu; tmp["sd"]=sd
        vpred.append(tmp)
    vp=pd.concat(vpred,ignore_index=True)
    a=action_from_margin(vp.control_direction.to_numpy(),vp.mu.to_numpy(),vp.sd.to_numpy(),margin,z)
    net=action_net(a,vp)
    uplift=net-vp.control_net_rupees.to_numpy(float)
    bootstrap=expiry_bootstrap(uplift,vp.expiry)
    oof_a=action_from_margin(oof.control_direction.to_numpy(),oof.mu.to_numpy(),oof.sd.to_numpy(),margin,z)
    oof_u=action_net(oof_a,oof)-oof.control_net_rupees.to_numpy(float)
    result={
        "model":name,"features":len(features),"margin":margin,"confidence_z":z,
        "dev_oof_rows":len(oof),"dev_oof_uplift_rupees":float(oof_u.sum()),
        "dev_oof_override_share":float(np.mean(oof_a!=oof.control_direction.to_numpy())),
        "validation_rows":len(vp),"validation_net_rupees":float(net.sum()),
        "validation_control_rupees":float(vp.control_net_rupees.sum()),
        "validation_uplift_rupees":float(uplift.sum()),
        "validation_override_share":float(np.mean(a!=vp.control_direction.to_numpy())),
        "validation_max_drawdown_rupees":max_drawdown(net),
        "validation_mean_selected_rupees":float(net.mean()),
        "validation_mae":float(np.mean(np.abs(vp.mu-vp.delta_pnl_call_minus_put))),
        "validation_spearman":float(pd.Series(vp.mu).corr(pd.Series(vp.delta_pnl_call_minus_put),method="spearman")),
        "paired_expiry_bootstrap":{"uplift_rupees":bootstrap[0],"ci_low":bootstrap[1],"ci_high":bootstrap[2],"expiries":bootstrap[3]},
    }
    vp["selected_action"]=a
    vp["selected_net_rupees"]=net
    vp["uplift_rupees"]=uplift
    return result,oof,vp

def main():
    df=pd.read_csv(DATA)
    ledger=pd.read_csv(LEDGER,usecols=["entry_ts","expiry","split","control_direction","control_net_rupees","call_net_rupees","put_net_rupees","delta_pnl_call_minus_put"])
    df["entry_ts"]=pd.to_datetime(df["entry_ts"])
    ledger["entry_ts"]=pd.to_datetime(ledger["entry_ts"])
    if len(df)!=477 or len(ledger)!=477 or df["entry_ts"].nunique()!=477 or ledger["entry_ts"].nunique()!=477:
        raise AssertionError("Expected 477 unique feature rows and 477 unique fixed-opportunity rows")
    df=df.merge(ledger,on=["entry_ts","expiry","split"],how="inner",validate="one_to_one")
    if len(df)!=477:
        raise AssertionError("Feature/ledger join lost fixed opportunities")
    df=df.sort_values("entry_ts").reset_index(drop=True)
    features=select_features(df)
    if len(features)<100:
        raise AssertionError(f"Unexpectedly small primary feature set: {len(features)}")
    results=[]; all_oof=[]; all_val=[]
    for name,fn in MODELS.items():
        print("RUN",name,flush=True)
        res,oof,vp=run_model(name,fn,df,features)
        results.append(res); all_oof.append(oof); all_val.append(vp)
        pd.concat([oof,vp],ignore_index=True).to_csv(OUT/f"{name}_predictions.csv",index=False)
        print(json.dumps(res,indent=2),flush=True)
    pd.DataFrame(results).sort_values(["validation_uplift_rupees","validation_max_drawdown_rupees"],ascending=[False,True]).to_csv(OUT/"model_comparison.csv",index=False)
    (OUT/"locked_feature_list.json").write_text(json.dumps({"feature_count":len(features),"features":features,"eligibility":"development missingness <=50% and >=5 unique non-missing values"},indent=2))
    summary={"status":"COMPLETE","models":list(MODELS),"features":len(features),"holdout_evaluated":False,
             "validation_control_rupees":float(df[df.split=="validation"].control_net_rupees.sum())}
    (OUT/"status.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
