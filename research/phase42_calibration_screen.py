import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor

import phase41_regime_policy_screen as p41

ROOT=Path(".")
OUT=ROOT/"results/phase42_confidence_calibration"
OUT.mkdir(parents=True,exist_ok=True)

MODELS=["SPLINE_RIDGE_VIX","EXTRATREES_VIX"]
CALIBRATIONS=["RAW","ROBUST_MAD","CONFORMAL_80","CONFORMAL_90"]
MARGINS=[0.0,250.0,500.0]
GATES=["ALL","HIGH_VIX","HIGH_VIX_RISING"]
WARMUP=100
WINDOW=60

def model(name):
    return p41.build_model(name)

def Xify(frame):
    return p41.add_vix_features(frame)

def calibration_width(mode,resid):
    x=np.asarray(resid[-WINDOW:],float)
    x=x[np.isfinite(x)]
    if mode=="RAW":
        return 0.0
    if len(x)<20:
        return np.nan
    if mode=="ROBUST_MAD":
        med=np.median(x)
        return float(max(1.4826*np.median(np.abs(x-med)),50.0))
    q=float(np.quantile(np.abs(x),0.80 if mode=="CONFORMAL_80" else 0.90))
    return max(q,50.0)

def expanding_scores(z,name,mode):
    X=Xify(z)
    y=z["delta_pnl_call_minus_put"].to_numpy(float)
    pred=np.full(len(z),np.nan); width=np.full(len(z),np.nan)
    for i in range(len(z)):
        if i<WARMUP: continue
        m=model(name)
        m.fit(X.iloc[:i],y[:i])
        pred[i]=float(m.predict(X.iloc[[i]])[0])
        fit=np.asarray(m.predict(X.iloc[:i]),float)
        width[i]=calibration_width(mode,y[:i]-fit)
    benefit=np.where(z["control_direction"].astype(str).to_numpy()=="CALL",-pred,pred)
    score=benefit-width
    return pred,width,score

def policy(z,pred,width,score,margin,gate):
    allowed=np.array([p41.gate_ok(r,gate) for _,r in z.iterrows()])
    override=np.isfinite(score)&np.isfinite(width)&allowed&(score>margin)
    ctl=z["control_net_rupees"].to_numpy(float)
    alt=np.where(z["control_direction"].astype(str).to_numpy()=="CALL",
                 z["put_net_rupees"].to_numpy(float),
                 z["call_net_rupees"].to_numpy(float))
    net=np.where(override,alt,ctl)
    return pd.DataFrame({
        "entry_ts":z["entry_ts"],"expiry":z["expiry"],"split":z["split"],
        "control_direction":z["control_direction"],"control_net_rupees":ctl,
        "alt_net_rupees":alt,"delta_pnl":z["delta_pnl_call_minus_put"],
        "pred_delta":pred,"calibration_width":width,"override_score":score,
        "override":override,"policy_net_rupees":net,
        "india_vix_level":z["india_vix_level"],"india_vix_high":z["india_vix_high"],
        "india_vix_rising":z["india_vix_rising"],"india_vix_high_rising":z["india_vix_high_rising"],
        "global_VIX":z["global_VIX"],"global_VIX_ret1":z["global_VIX_ret1"],
        "nifty_daily_rv_20d":z["nifty_daily_rv_20d"],
        "nifty_gap_from_prev_close":z["nifty_gap_from_prev_close"],
        "atm_iv_skew":z["atm_iv_skew"],"atm_pcr_oi":z["atm_pcr_oi"]
    })

def stats(fr,split):
    return p41.stats(fr,split)

def main():
    z,thr=p41.load()
    assert len(z)==477
    rows=[]
    cache={}
    for name in MODELS:
        for cal in CALIBRATIONS:
            pred,width,score=expanding_scores(z,name,cal)
            cache[(name,cal)]=(pred,width,score)
            for margin in MARGINS:
                for gate in GATES:
                    fr=policy(z,pred,width,score,margin,gate)
                    d=stats(fr,"development"); v=stats(fr,"validation")
                    rows.append({
                        "model":name,"calibration":cal,"margin":margin,"gate":gate,
                        "development_uplift":d["uplift_rupees"],
                        "validation_uplift":v["uplift_rupees"],
                        "development_overrides":d["overrides"],
                        "validation_overrides":v["overrides"],
                        "validation_override_rate":v["override_rate"],
                        "validation_policy_dd":v["policy_max_drawdown_rupees"],
                        "validation_control_dd":v["control_max_drawdown_rupees"]
                    })
    grid=pd.DataFrame(rows).sort_values(["validation_uplift","development_uplift"],ascending=False).reset_index(drop=True)
    grid.to_csv(OUT/"fixed_grid_validation.csv",index=False)
    eligible=grid[(grid.development_uplift>=0)&(grid.validation_uplift>0)&
                  (grid.validation_overrides>=5)&(grid.validation_override_rate<=.25)&
                  (grid.validation_policy_dd<=1.25*grid.validation_control_dd)]
    top=eligible.head(3).copy()
    fallback=""
    if top.empty:
        top=grid.head(3).copy()
        fallback="No variant passed the registered safety screen; top three validation-ranked variants are diagnostic only."
    selected=top.to_dict("records")
    for rank,rec in enumerate(selected,1):
        pred,width,score=cache[(rec["model"],rec["calibration"])]
        fr=policy(z,pred,width,score,float(rec["margin"]),rec["gate"])
        fr.to_csv(OUT/f"frozen_candidate_{rank}_fixed.csv",index=False)
    (OUT/"selection.json").write_text(json.dumps({
        "declared_variants":len(MODELS)*len(CALIBRATIONS)*len(MARGINS)*len(GATES),
        "eligible_count":len(eligible),"fallback_reason":fallback,
        "top3_frozen_before_holdout":selected,"vix_thresholds":thr
    },indent=2,default=str))
    print(grid.head(12).to_string(index=False))
    print("eligible",len(eligible))
    print(json.dumps(selected,indent=2,default=str))

if __name__=="__main__":
    main()
