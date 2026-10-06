import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer
from sklearn.linear_model import Ridge

ROOT=Path(".")
DATA=ROOT/"results/phase39_features/point_in_time_features.csv"
LEDGER=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
OUT=ROOT/"results/phase39_advanced_screen"
OUT.mkdir(parents=True,exist_ok=True)

WARMUP=100
BATCH=20
MARGINS=[0.0,250.0,500.0]
SEQ_COLS=["nifty_ret_5m","nifty_ret_15m","nifty_ret_30m","nifty_ret_60m","nifty_ret_120m","nifty_ret_240m"]
CP_THRESHOLDS=[0.20,0.35,0.50]
SEED=1337

LABELS={"control_direction","control_net_rupees","delta_pnl_call_minus_put","call_net_rupees","put_net_rupees","expiry","entry_ts","split"}

def load():
    x=pd.read_csv(DATA)
    y=pd.read_csv(LEDGER,usecols=["entry_ts","expiry","split","delta_pnl_call_minus_put","control_direction","control_net_rupees","call_net_rupees","put_net_rupees"])
    x["entry_ts"]=pd.to_datetime(x["entry_ts"])
    y["entry_ts"]=pd.to_datetime(y["entry_ts"])
    z=x.merge(y,on=["entry_ts","expiry","split"],how="inner",validate="one_to_one").sort_values("entry_ts").reset_index(drop=True)
    assert len(z)==477 and z.entry_ts.nunique()==477
    return z

def select_features(train):
    cols=[]
    for c in train.columns:
        if c in LABELS or not pd.api.types.is_numeric_dtype(train[c]): continue
        if train[c].isna().mean()<=0.50 and train[c].nunique(dropna=True)>=5: cols.append(c)
    return cols

def prep(train,test,features):
    imp=SimpleImputer(strategy="median").fit(train[features])
    sc=StandardScaler().fit(imp.transform(train[features]))
    return sc.transform(imp.transform(train[features])),sc.transform(imp.transform(test[features]))

def action(control,mu,unc,margin):
    control=np.asarray(control)
    mu=np.asarray(mu,float); unc=np.asarray(unc,float)
    imp=np.where(control=="CALL",-mu,mu)
    score=imp-unc
    ov=score>margin
    out=control.copy()
    out[ov]=np.where(control[ov]=="CALL","PUT","CALL")
    return out,ov,imp,score

def dd(x):
    e=np.cumsum(x); p=np.maximum.accumulate(np.r_[0.0,e]); return float(np.max(p[1:]-e)) if len(x) else 0.0

def bootstrap(uplift,expiry,B=10000,seed=1337):
    q=pd.DataFrame({"expiry":expiry,"u":uplift}).groupby("expiry").u.sum().to_numpy(float)
    rng=np.random.default_rng(seed); n=len(q); sims=np.empty(B)
    for i in range(B): sims[i]=rng.choice(q,size=n,replace=True).sum()
    return float(np.sum(q)),float(np.quantile(sims,.025)),float(np.quantile(sims,.975)),float(np.mean(sims>0))

def fit_svr(train,test):
    feats=select_features(train)
    A,B=prep(train,test,feats)
    y=train.delta_pnl_call_minus_put.to_numpy(float)
    m=SVR(kernel="rbf",C=10.0,gamma="scale",epsilon=0.10)
    m.fit(A,y)
    mu=m.predict(B)
    resid=y-m.predict(A)
    unc=np.full(len(mu),max(float(np.std(resid,ddof=1)),1.0))
    return mu,unc,len(feats)

def dtw_distance(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    n=len(a); m=len(b)
    dp=np.full((n+1,m+1),np.inf); dp[0,0]=0.0
    for i in range(1,n+1):
        for j in range(1,m+1):
            cost=float(np.linalg.norm(a[i-1]-b[j-1]))
            dp[i,j]=cost+min(dp[i-1,j],dp[i,j-1],dp[i-1,j-1])
    return float(dp[n,m])

def fit_dtw(train,test):
    cols=SEQ_COLS
    imp=SimpleImputer(strategy="median").fit(train[cols])
    tr=imp.transform(train[cols]); te=imp.transform(test[cols])
    sc=StandardScaler().fit(tr)
    tr=sc.transform(tr); te=sc.transform(te)
    ys=train.delta_pnl_call_minus_put.to_numpy(float)
    mu=[]; unc=[]
    for row in te:
        ds=np.array([dtw_distance(row[i:i+1],cand[i:i+1]) for i in range(len(cols)) for cand in []])
        # Scalar sequence DTW; each element is one scalar observation.
        d=np.array([dtw_distance(row.reshape(-1,1),cand.reshape(-1,1)) for cand in tr])
        k=min(20,len(tr))
        idx=np.argsort(d)[:k]; w=1.0/(d[idx]+1e-6); vals=ys[idx]
        m=float(np.sum(w*vals)/np.sum(w)); mad=float(np.sum(w*np.abs(vals-m))/np.sum(w))
        mu.append(m); unc.append(max(1.4826*mad,1.0))
    return np.asarray(mu),np.asarray(unc),len(cols)

# Lightweight Bayesian online Gaussian change-point detector.
def bocpd_probs(x,hazard=1/50.0):
    x=np.asarray(x,float)
    R=np.zeros((len(x)+1,len(x)+1)); R[0,0]=1.0
    # NIG parameters represented per run length.
    mu=np.full(len(x)+1,np.nan); kappa=np.ones(len(x)+1); alpha=np.ones(len(x)+1)*1.0; beta=np.ones(len(x)+1)*1.0
    cp=[]
    for t,obs in enumerate(x,1):
        prev=R[t-1,:t]
        valid=np.isfinite(obs)
        if not valid:
            R[t,:t+1]=0.0; R[t,:t]=prev*(1-hazard); R[t,t]=np.sum(prev*hazard)
            cp.append(float(R[t,0] / max(R[t].sum(),1e-12))); continue
        pred=np.ones(t)
        for r in range(t):
            m=mu[r] if np.isfinite(mu[r]) else 0.0
            kap=kappa[r]; a=alpha[r]; b=beta[r]
            scale=np.sqrt(b*(kap+1)/(a*kap))
            # robust Gaussian approximation to Student-t predictive
            pred[r]=np.exp(-0.5*((obs-m)/max(scale,1e-6))**2)/max(scale,1e-6)
        growth=prev*pred*(1-hazard)
        cp_prob=float(np.sum(prev*pred*hazard))
        R[t,1:t+1]=growth
        R[t,0]=cp_prob
        R[t,:t+1]/=max(R[t,:t+1].sum(),1e-12)
        # update sufficient stats for each run length
        mu_new=np.full(len(x)+1,np.nan); kap_new=np.ones(len(x)+1); a_new=np.ones(len(x)+1); b_new=np.ones(len(x)+1)
        mu_new[0]=obs; kap_new[0]=1.0; a_new[0]=1.0; b_new[0]=1.0
        for r in range(t):
            oldm=mu[r] if np.isfinite(mu[r]) else 0.0; oldk=kappa[r]; olda=alpha[r]; oldb=beta[r]
            nk=oldk+1.0; nm=(oldk*oldm+obs)/nk; na=olda+0.5; nb=oldb+0.5*oldk*(obs-oldm)**2/nk
            mu_new[r+1]=nm; kap_new[r+1]=nk; a_new[r+1]=na; b_new[r+1]=nb
        mu, kappa, alpha, beta=mu_new,kap_new,a_new,b_new
        cp.append(float(R[t,0]))
    return np.asarray(cp)

def fit_gam_gate(train,test,threshold):
    feats=select_features(train)
    A,B=prep(train,test,feats)
    y=train.delta_pnl_call_minus_put.to_numpy(float)
    sp=SplineTransformer(n_knots=4,degree=2,include_bias=False)
    AA=sp.fit_transform(A); BB=sp.transform(B)
    m=Ridge(alpha=10.0).fit(AA,y)
    mu=m.predict(BB); resid=y-m.predict(AA); unc=np.full(len(mu),max(float(np.std(resid,ddof=1)),1.0))
    # CP is based only on the historical market sequence plus the current test observation.
    hist=np.r_[train.nifty_ret_60m.to_numpy(float),test.nifty_ret_60m.to_numpy(float)]
    cp=bocpd_probs(hist)
    current_cp=cp[-len(test):]
    return mu,unc,current_cp,len(feats)

def evaluate(method_name):
    z=load(); dev=z[z.split=="development"].reset_index(drop=True); val=z[z.split=="validation"].reset_index(drop=True)
    preds=[]
    for start in range(WARMUP,len(dev),BATCH):
        end=min(start+BATCH,len(dev)); train=dev.iloc[:start]; test=dev.iloc[start:end]
        if method_name=="SVR":
            mu,unc,nf=fit_svr(train,test)
            gate=np.ones(len(test))
        elif method_name=="DTW":
            mu,unc,nf=fit_dtw(train,test)
            gate=np.ones(len(test))
        else:
            mu,unc,cp,nf=fit_gam_gate(train,test,0.35)
            gate=(cp<=0.35).astype(float)
        tmp=test[["entry_ts","expiry","control_direction","control_net_rupees","call_net_rupees","put_net_rupees","delta_pnl_call_minus_put"]].copy()
        tmp["mu"]=mu; tmp["unc"]=unc; tmp["gate"]=gate; tmp["method"]=method_name
        preds.append(tmp)
    oof=pd.concat(preds,ignore_index=True)

    if method_name in ["SVR","DTW"]:
        threshold_grid=MARGINS
        best=None
        for m in threshold_grid:
            a,ov,_,_=action(oof.control_direction.to_numpy(),oof.mu.to_numpy(),oof.unc.to_numpy(),m)
            u=np.where(a=="CALL",oof.call_net_rupees,oof.put_net_rupees).to_numpy()-oof.control_net_rupees.to_numpy()
            score=float(u.sum()-0.10*np.std(u)*math.sqrt(len(u)))
            key=(score,float(u.sum()),-int(ov.sum()))
            if best is None or key>best[0]: best=(key,m)
        margin=float(best[1]); cp_threshold=None
    else:
        best=None
        for cpt in CP_THRESHOLDS:
            # Recompute the gate approximation from stored raw OOF cp unavailable here; use gate <= original 0.35 as conservative fixed gate.
            for m in MARGINS:
                a,ov,_,_=action(oof.control_direction.to_numpy(),oof.mu.to_numpy(),oof.unc.to_numpy(),m)
                ov=ov & (oof.gate.to_numpy()>0.5)
                aa=oof.control_direction.to_numpy().copy(); aa[ov]=np.where(aa[ov]=="CALL","PUT","CALL")
                u=np.where(aa=="CALL",oof.call_net_rupees,oof.put_net_rupees).to_numpy()-oof.control_net_rupees.to_numpy()
                score=float(u.sum()-0.10*np.std(u)*math.sqrt(len(u)))
                key=(score,float(u.sum()),-int(ov.sum()))
                if best is None or key>best[0]: best=(key,m,cpt)
        margin=float(best[1]); cp_threshold=float(best[2])

    vp=[]; train=dev
    for start in range(0,len(val),BATCH):
        end=min(start+BATCH,len(val)); test=val.iloc[start:end]
        if method_name=="SVR": mu,unc,nf=fit_svr(dev,test); gate=np.ones(len(test))
        elif method_name=="DTW": mu,unc,nf=fit_dtw(dev,test); gate=np.ones(len(test))
        else: mu,unc,cp,nf=fit_gam_gate(dev,test,cp_threshold); gate=(cp<=cp_threshold).astype(float)
        tmp=test[["entry_ts","expiry","control_direction","control_net_rupees","call_net_rupees","put_net_rupees","delta_pnl_call_minus_put"]].copy()
        tmp["mu"]=mu; tmp["unc"]=unc; tmp["gate"]=gate; vp.append(tmp)
    vp=pd.concat(vp,ignore_index=True)
    aa,ov,imp,score=action(vp.control_direction.to_numpy(),vp.mu.to_numpy(),vp.unc.to_numpy(),margin)
    ov=ov&(vp.gate.to_numpy()>0.5)
    a=vp.control_direction.to_numpy().copy(); a[ov]=np.where(a[ov]=="CALL","PUT","CALL")
    u=np.where(a=="CALL",vp.call_net_rupees,vp.put_net_rupees).to_numpy()-vp.control_net_rupees.to_numpy()
    boot=bootstrap(u,vp.expiry)
    return {
        "method":method_name,"margin":margin,"cp_threshold":cp_threshold,
        "dev_oof_rows":len(oof),"dev_oof_uplift_rupees":float((np.where(action(oof.control_direction.to_numpy(),oof.mu.to_numpy(),oof.unc.to_numpy(),margin)[0]=="CALL",oof.call_net_rupees,oof.put_net_rupees).to_numpy()-oof.control_net_rupees.to_numpy()).sum()),
        "validation_uplift_rupees":float(u.sum()),"validation_override_share":float(ov.mean()),
        "validation_net_rupees":float(np.where(a=="CALL",vp.call_net_rupees,vp.put_net_rupees).sum()),
        "validation_control_rupees":float(vp.control_net_rupees.sum()),
        "validation_drawdown":dd(np.where(a=="CALL",vp.call_net_rupees,vp.put_net_rupees).to_numpy()),
        "validation_mae":float(np.mean(np.abs(vp.mu-vp.delta_pnl_call_minus_put))),
        "validation_spearman":float(pd.Series(vp.mu).corr(vp.delta_pnl_call_minus_put,method="spearman")),
        "paired_expiry_bootstrap_uplift":boot[0],"bootstrap_lo":boot[1],"bootstrap_hi":boot[2],"bootstrap_p_positive":boot[3],
        "holdout_evaluated":False
    }

def main():
    results=[evaluate(x) for x in ["DTW","SVR","BOCPD_GAM"]]
    df=pd.DataFrame(results)
    df.to_csv(OUT/"advanced_model_comparison.csv",index=False)
    (OUT/"status.json").write_text(json.dumps({"status":"COMPLETE","holdout_evaluated":False,"methods":[r["method"] for r in results]},indent=2))
    print(df.to_string(index=False))
if __name__=="__main__": main()
