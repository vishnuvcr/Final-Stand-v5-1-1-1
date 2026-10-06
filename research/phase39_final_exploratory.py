import json, math
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer

ROOT=Path(".")
DATA=ROOT/"results/phase39_features/point_in_time_features.csv"
LEDGER=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
OUT=ROOT/"results/phase39_final_exploratory"
OUT.mkdir(parents=True,exist_ok=True)

WARMUP=100
BATCH=20
MARGINS=[0.0,250.0,500.0]
FEATURES=["candidate_credit_diff_call_minus_put","candidate_iv_skew_25","atm_iv_skew",
          "atm_pcr_oi","atm_pcr_volume","nifty_ret_15m","nifty_ret_60m","nifty_rv_60m",
          "nifty_daily_ret_5d","nifty_daily_rv_20d","global_VIX","global_SP500_ret1",
          "global_NASDAQ_ret1","global_USDINR_ret1","flow_fii_net_z20","flow_dii_net_z20",
          "sent_sent_mean"]

def load():
    x=pd.read_csv(DATA); y=pd.read_csv(LEDGER,usecols=["entry_ts","expiry","split","call_net_rupees","put_net_rupees"])
    x["entry_ts"]=pd.to_datetime(x.entry_ts); y["entry_ts"]=pd.to_datetime(y.entry_ts)
    z=x.merge(y,on=["entry_ts","expiry","split"],validate="one_to_one")
    assert len(z)==477 and z.entry_ts.nunique()==477
    return z.sort_values("entry_ts").reset_index(drop=True)

def action(control,mu,unc,margin):
    imp=np.where(control=="CALL",-mu,mu)
    ov=(imp-unc)>margin
    a=control.copy(); a[ov]=np.where(a[ov]=="CALL","PUT","CALL")
    return a,ov

def dd(x):
    e=np.cumsum(np.asarray(x,float)); p=np.maximum.accumulate(np.r_[0,e]); return float(np.max(p[1:]-e))

def bootstrap(u,exp,B=10000,seed=1337):
    g=pd.DataFrame({"e":exp,"u":u}).groupby("e").u.sum().to_numpy(float)
    rng=np.random.default_rng(seed); sims=np.empty(B)
    for i in range(B): sims[i]=rng.choice(g,size=len(g),replace=True).sum()
    return float(g.sum()),float(np.quantile(sims,.025)),float(np.quantile(sims,.975)),float((sims>0).mean())

def fit_symbolic(train,test):
    feats=[f for f in FEATURES if f in train.columns and train[f].notna().sum()>=5]
    feats=feats[:17]
    pipe=Pipeline([
      ("imp",SimpleImputer(strategy="median")),
      ("scale",StandardScaler()),
      ("poly",PolynomialFeatures(degree=2,include_bias=False)),
      ("enet",ElasticNet(alpha=0.20,l1_ratio=0.85,max_iter=20000,random_state=1337))
    ])
    pipe.fit(train[feats],train.delta_pnl_call_minus_put)
    mu=pipe.predict(test[feats])
    resid=train.delta_pnl_call_minus_put.to_numpy()-pipe.predict(train[feats])
    unc=np.full(len(test),max(float(np.std(resid,ddof=1)),1.0))
    return mu,unc,len(feats),int(np.count_nonzero(pipe.named_steps["enet"].coef_))

def fit_gam(train,test):
    feats=[c for c in train.columns if c.startswith(("nifty_","atm_","candidate_","global_","flow_","sent_")) and pd.api.types.is_numeric_dtype(train[c])]
    feats=[c for c in feats if train[c].isna().mean()<=.50 and train[c].nunique(dropna=True)>=5]
    imp=SimpleImputer(strategy="median"); sc=StandardScaler()
    A=sc.fit_transform(imp.fit_transform(train[feats])); B=sc.transform(imp.transform(test[feats]))
    sp=SplineTransformer(n_knots=4,degree=2,include_bias=False); AA=sp.fit_transform(A); BB=sp.transform(B)
    m=Ridge(alpha=10.0).fit(AA,train.delta_pnl_call_minus_put)
    mu=m.predict(BB); resid=train.delta_pnl_call_minus_put.to_numpy()-m.predict(AA)
    unc=np.full(len(test),max(float(np.std(resid,ddof=1)),1.0))
    return mu,unc

def main():
    z=load(); dev=z[z.split=="development"].reset_index(drop=True); val=z[z.split=="validation"].reset_index(drop=True)
    parts=[]; sym_stats=[]
    for start in range(WARMUP,len(dev),BATCH):
        end=min(start+BATCH,len(dev)); tr=dev.iloc[:start]; te=dev.iloc[start:end]
        mu,unc,nf,nnz=fit_symbolic(tr,te)
        a,ov=action(te.control_direction.to_numpy(),mu,unc,500.0)
        uplift=np.asarray(np.where(a=="CALL",te.call_net_rupees,te.put_net_rupees))-te.control_net_rupees.to_numpy()
        sym_stats.append({"entry_start":str(te.entry_ts.iloc[0]),"features":nf,"nonzero_terms":nnz,"oof_uplift":float(uplift.sum())})
    # Development fixed margin selection for symbolic model.
    sym_best=None
    for margin in MARGINS:
        us=[]; ex=[]
        for start in range(WARMUP,len(dev),BATCH):
            end=min(start+BATCH,len(dev)); tr=dev.iloc[:start]; te=dev.iloc[start:end]
            mu,unc,_,_=fit_symbolic(tr,te); a,ov=action(te.control_direction.to_numpy(),mu,unc,margin)
            us.extend((np.asarray(np.where(a=="CALL",te.call_net_rupees,te.put_net_rupees))-te.control_net_rupees.to_numpy()).tolist()); ex.extend(te.expiry.tolist())
        score=sum(us)-0.10*np.std(us)*math.sqrt(len(us))
        if sym_best is None or score>sym_best[0]: sym_best=(score,margin,us,ex)
    margin=float(sym_best[1])
    vu=[]; vex=[]
    for start in range(0,len(val),BATCH):
        end=min(start+BATCH,len(val)); te=val.iloc[start:end]
        mu,unc,_,_=fit_symbolic(dev,te); a,ov=action(te.control_direction.to_numpy(),mu,unc,margin)
        u=np.asarray(np.where(a=="CALL",te.call_net_rupees,te.put_net_rupees))-te.control_net_rupees.to_numpy()
        vu.extend(u.tolist()); vex.extend(te.expiry.tolist())
    sym_boot=bootstrap(np.asarray(vu),vex)

    # Research-only full-information exponential-weights expert aggregation.
    # Experts: canonical control; premium-geometry expert; Sparse-GAM expert.
    eta_grid=[0.00001,0.00003,0.0001]
    def run_agg(eta,frame,train_only=False):
        w=np.ones(3); rows=[]; total=0.0
        history=[]
        for start in range(0,len(frame),BATCH):
            te=frame.iloc[start:min(start+BATCH,len(frame))]
            # Canonical action.
            ea=[(te.control_direction=="CALL").astype(int).to_numpy()]
            geom=(te.candidate_credit_diff_call_minus_put>0).fillna(False).astype(int).to_numpy()
            ea.append(geom)
            mu,unc=fit_gam(dev if frame is val else frame.iloc[:max(start, WARMUP)],te) if len(frame.iloc[:max(start,WARMUP)])>=WARMUP or frame is val else (np.zeros(len(te)),np.ones(len(te))*1e9)
            ga,gov=action(te.control_direction.to_numpy(),mu,unc,500.0)
            ea.append((ga=="CALL").astype(int))
            expert_actions=np.vstack(ea).T
            # Score each expert by its counterfactual net arm at this opportunity.
            expert_pnl=np.where(expert_actions==1,te.call_net_rupees.to_numpy()[:,None],te.put_net_rupees.to_numpy()[:,None])
            p= w/w.sum()
            score=expert_actions.dot(p)
            selected=(score>=0.5).astype(int)
            selected_pnl=np.asarray(np.where(selected==1,te.call_net_rupees,te.put_net_rupees))
            total+=float(selected_pnl.sum())
            # Full-information historical expert reward update; diagnostic only.
            avg=np.mean(expert_pnl,axis=0)
            centered=np.clip(avg/5000.0,-5,5)
            w*=np.exp(eta*centered)
            rows.append((te.entry_ts.iloc[-1],float(selected_pnl.sum()),*w))
        return total,pd.DataFrame(rows,columns=["ts","selected_pnl","w_control","w_geometry","w_gam"])
    best=None
    for eta in eta_grid:
        net,_=run_agg(eta,dev)
        key=net
        if best is None or key>best[0]: best=(key,eta)
    agg_eta=float(best[1])
    agg_val,agg_trace=run_agg(agg_eta,val)
    # Note: this is not holdout evidence and is explicitly diagnostic because expert rewards use historical counterfactual arms.
    out={
      "status":"COMPLETE","holdout_evaluated":False,
      "symbolic_margin":margin,"symbolic_validation_uplift":sym_boot[0],"symbolic_bootstrap_lo":sym_boot[1],
      "symbolic_bootstrap_hi":sym_boot[2],"symbolic_bootstrap_p_positive":sym_boot[3],
      "expert_aggregation_eta":agg_eta,"expert_aggregation_validation_net":float(agg_val),
      "expert_aggregation_diagnostic_only":True,
      "decision":"NO_HOLDOUT_OR_PROMOTION"
    }
    pd.DataFrame(sym_stats).to_csv(OUT/"symbolic_oof_trace.csv",index=False)
    agg_trace.to_csv(OUT/"expert_aggregation_trace.csv",index=False)
    (OUT/"summary.json").write_text(json.dumps(out,indent=2))
    (OUT/"status.json").write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
