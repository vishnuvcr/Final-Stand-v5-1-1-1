import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge

ROOT=Path(".")
FEATURE=ROOT/"results/phase39_features/point_in_time_features.csv"
LEDGER=ROOT/"results/phase39_counterfactual/fixed_opportunity_ledger.csv"
OUT=ROOT/"results/phase39_hedge_screen"
OUT.mkdir(parents=True,exist_ok=True)

WARMUP=100
BATCH=20
MARGINS=[0.0,250.0,500.0]
ETA_GRID=[0.00001,0.00002,0.00005]
DECAY_GRID=[1.0,0.995,0.99]
SCALE=1000.0
LABELS={"control_direction","control_net_rupees","delta_pnl_call_minus_put","call_net_rupees","put_net_rupees","expiry","entry_ts","split"}

def load():
    x=pd.read_csv(FEATURE)
    y=pd.read_csv(LEDGER,usecols=["entry_ts","expiry","split","call_net_rupees","put_net_rupees"])
    z=x.merge(y,on=["entry_ts","expiry","split"],how="inner",validate="one_to_one").sort_values("entry_ts").reset_index(drop=True)
    assert len(z)==477 and z.entry_ts.nunique()==477
    return z

def select_features(train):
    return [c for c in train.columns if c not in LABELS
            and pd.api.types.is_numeric_dtype(train[c])
            and train[c].isna().mean()<=0.50 and train[c].nunique(dropna=True)>=5]

def fit_margin(train,test):
    feats=select_features(train)
    imp=SimpleImputer(strategy="median").fit(train[feats])
    sc=StandardScaler().fit(imp.transform(train[feats]))
    A=sc.transform(imp.transform(train[feats]))
    B=sc.transform(imp.transform(test[feats]))
    sp=SplineTransformer(n_knots=4,degree=2,include_bias=False)
    AA=sp.fit_transform(A); BB=sp.transform(B)
    y=train.delta_pnl_call_minus_put.to_numpy(float)
    m=Ridge(alpha=10.0).fit(AA,y)
    mu=m.predict(BB)
    resid=y-m.predict(AA)
    unc=np.full(len(test),max(float(np.std(resid,ddof=1)),1.0))
    return mu,unc

def gam_actions(control,mu,unc,margin):
    improve=np.where(control=="CALL",-mu,mu)
    score=improve-unc
    ov=score>margin
    act=control.copy()
    act[ov]=np.where(act[ov]=="CALL","PUT","CALL")
    return act,ov

def hedge(actions_rewards,eta,decay):
    # Two experts: canonical control (expert 0) and GAM override policy (expert 1).
    w=np.array([1.0,1.0],float)
    chosen=[]
    weight_rows=[]
    cum=np.zeros(2)
    for r0,r1 in actions_rewards:
        # deterministic pre-decision weights based solely on past rewards
        z=eta*cum/SCALE
        z=z-np.max(z)
        w=np.exp(z); w=w/w.sum()
        pick=int(np.argmax(w))  # deterministic best-expert action
        chosen.append(pick)
        weight_rows.append((w[0],w[1],pick,cum[0],cum[1]))
        r=np.array([r0,r1],float)
        cum=decay*cum+r
    return np.asarray(chosen),np.asarray(weight_rows),cum

def simulate_fixed(z,split,margin,eta,decay):
    d=z[z.split==split].reset_index(drop=True)
    # Chronological expanding-window GAM rewards.
    rewards=[]; rows=[]
    if split=="development":
        # Fit only once per chronological batch; Hedge weights still update after every observation.
        for start in range(0,len(d),BATCH):
            end=min(start+BATCH,len(d))
            if start < WARMUP:
                warm=min(end,WARMUP)
                for i in range(start,warm):
                    cr=float(d.control_net_rupees.iloc[i])
                    rewards.append((cr,cr))
                    rows.append((d.entry_ts.iloc[i],cr,cr,False))
                if end<=WARMUP:
                    continue
                start_pred=WARMUP
            else:
                start_pred=start
            train=d.iloc[:start_pred]
            test=d.iloc[start_pred:end]
            mu,unc=fit_margin(train,test)
            act,ov_arr=gam_actions(test.control_direction.to_numpy(),mu,unc,margin)
            for j in range(len(test)):
                i=start_pred+j
                cr=float(test.control_net_rupees.iloc[j])
                gr=float(test.put_net_rupees.iloc[j] if act[j]=="PUT" else test.call_net_rupees.iloc[j])
                rewards.append((cr,gr))
                rows.append((test.entry_ts.iloc[j],cr,gr,bool(ov_arr[j])))
    else:
        # Validation uses all development data to fit a model at each batch, but Hedge only updates online.
        dev=z[z.split=="development"].reset_index(drop=True)
        for start in range(0,len(d),BATCH):
            end=min(start+BATCH,len(d))
            test=d.iloc[start:end]
            mu,unc=fit_margin(dev,test)
            act,ov_arr=gam_actions(test.control_direction.to_numpy(),mu,unc,margin)
            for j in range(len(test)):
                i=start+j
                control_r=float(test.control_net_rupees.iloc[j])
                gam_r=float(test.put_net_rupees.iloc[j] if act[j]=="PUT" else test.call_net_rupees.iloc[j])
                rewards.append((control_r,gam_r))
                rows.append((test.entry_ts.iloc[j],control_r,gam_r,bool(ov_arr[j])))
    pick,wrows,cum=hedge(rewards,eta,decay)
    rarr=np.asarray(rewards,float)
    chosen=np.where(pick==0,rarr[:,0],rarr[:,1])
    return float(chosen.sum()),chosen,pick,wrows,pd.DataFrame(rows,columns=["entry_ts","control_r","gam_r","gam_override"])

def main():
    z=load()
    dev_scores=[]
    # Select only on development.
    for margin in MARGINS:
        for eta in ETA_GRID:
            for decay in DECAY_GRID:
                net,chosen,pick,wrows,rows=simulate_fixed(z,"development",margin,eta,decay)
                dev_scores.append({"margin":margin,"eta":eta,"decay":decay,"dev_hedge_net":net,
                                   "dev_control_net":float(z[z.split=="development"].control_net_rupees.sum()),
                                   "dev_uplift":net-float(z[z.split=="development"].control_net_rupees.sum()),
                                   "expert1_share":float((pick==1).mean())})
    dev=pd.DataFrame(dev_scores).sort_values(["dev_uplift","expert1_share","eta"],ascending=[False,False,True]).reset_index(drop=True)
    best=dev.iloc[0].to_dict()

    val_net,chosen,pick,wrows,rows=simulate_fixed(z,"validation",float(best["margin"]),float(best["eta"]),float(best["decay"]))
    val=z[z.split=="validation"]
    val_control=float(val.control_net_rupees.sum())

    dev.to_csv(OUT/"development_hedge_grid.csv",index=False)
    rows.to_csv(OUT/"validation_expert_rewards.csv",index=False)
    pd.DataFrame(wrows,columns=["control_weight","gam_weight","selected_expert","control_cum_reward","gam_cum_reward"]).to_csv(OUT/"validation_weights.csv",index=False)

    result={
      "status":"COMPLETE",
      "selected_margin":float(best["margin"]),
      "selected_eta":float(best["eta"]),
      "selected_decay":float(best["decay"]),
      "development_hedge_net":float(best["dev_hedge_net"]),
      "development_control_net":float(best["dev_control_net"]),
      "development_uplift":float(best["dev_uplift"]),
      "validation_hedge_net":val_net,
      "validation_control_net":val_control,
      "validation_uplift":val_net-val_control,
      "validation_expert1_share":float((pick==1).mean()),
      "holdout_evaluated":False
    }
    (OUT/"summary.json").write_text(json.dumps(result,indent=2))
    (OUT/"status.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    print(dev.head(10).to_string(index=False))

if __name__=="__main__":
    main()
