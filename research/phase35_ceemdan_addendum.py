import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
SEED=1337; TZ="Asia/Kolkata"; DATA=Path("data/phase33"); OUT=Path("results/phase35_advanced_tree_prediction")
TE=pd.Timestamp("2023-12-31 23:59:59",tz=TZ); VE=pd.Timestamp("2025-12-31 23:59:59",tz=TZ); HS=pd.Timestamp("2026-01-01",tz=TZ); HE=pd.Timestamp("2026-09-30 23:59:59",tz=TZ)
def norm(x):
 y=pd.to_datetime(x,errors="coerce")
 y=y.dt.tz_localize(TZ) if getattr(y.dt,"tz",None) is None else y.dt.tz_convert(TZ)
 return y.astype(f"datetime64[ns, {TZ}]")
def load():
 e=pd.read_parquet(DATA/"events.parquet"); d=pd.read_parquet(DATA/"nifty_daily.parquet")
 e["expiry"]=norm(e.expiry).dt.normalize(); e["ref_ts"]=norm(e.ref_ts); d["date"]=norm(d.date).dt.normalize()
 e=e[(e.ref_ts>=pd.Timestamp("2021-05-27",tz=TZ))&(e.ref_ts<=HE)].sort_values("ref_ts").copy()
 e["split"]=np.where(e.ref_ts<=TE,"train",np.where(e.ref_ts<=VE,"validation","holdout"))
 return e,d.sort_values("date")
def decomp(e,d):
 p=Path("data/phase35_ceemdan_features.parquet")
 if p.exists():
  z=pd.read_parquet(p); z["ref_ts"]=norm(z.ref_ts); return z
 from PyEMD import CEEMDAN
 rows=[]
 for _,r in e.iterrows():
  z=d[d.date<pd.Timestamp(r.ref_ts).normalize()].tail(64)
  x=np.log(z.close/z.close.shift(1)).dropna().to_numpy(float)
  feat={"ref_ts":r.ref_ts}
  if len(x)>=32:
   ce=CEEMDAN(trials=20,epsilon=0.005,noise_scale=0.2)
   ce.noise_seed(SEED)
   imfs=ce.ceemdan(x[-64:])
   for i in range(min(4,len(imfs))):
    a=imfs[i]; feat[f"ceemdan{i}_last"]=float(a[-1]); feat[f"ceemdan{i}_energy"]=float(np.mean(a*a)); feat[f"ceemdan{i}_std"]=float(np.std(a))
   feat["ceemdan_resid"]=float(x[-1]-imfs[:,-1].sum()) if imfs.size else np.nan
  rows.append(feat)
 z=pd.DataFrame(rows); z["ref_ts"]=norm(z.ref_ts); z.to_parquet(p,index=False); return z
def feat(e):
 drop={"expiry","ref_ts","ref_spot","expiry_close","target_return","target_direction","split"}
 return [c for c in e.columns if c not in drop and pd.api.types.is_numeric_dtype(e[c])]
def fit(f,t,cols):
 from sklearn.impute import SimpleImputer
 from lightgbm import LGBMClassifier
 imp=SimpleImputer(strategy="median").fit(f[cols]); A=imp.transform(f[cols]); B=imp.transform(t[cols])
 m=LGBMClassifier(n_estimators=220,num_leaves=15,max_depth=4,learning_rate=.03,min_child_samples=8,reg_lambda=2,verbosity=-1,random_state=SEED)
 m.fit(A,f.target_direction.astype(int)); return m.predict_proba(B)[:,1]
def metric(y,p):
 from sklearn.metrics import accuracy_score,balanced_accuracy_score,roc_auc_score,log_loss,brier_score_loss
 return {"n":len(y),"accuracy":accuracy_score(y,p>=.5),"balanced_accuracy":balanced_accuracy_score(y,p>=.5),"roc_auc":roc_auc_score(y,p) if len(np.unique(y))==2 else np.nan,"log_loss":log_loss(y,np.c_[1-p,p],labels=[0,1]),"brier":brier_score_loss(y,p)}
def boot(x,n=4000):
 rng=np.random.default_rng(SEED); a=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(n)]); return float(np.quantile(a,.025)),float(np.quantile(a,.975))
def sf(x,n=12000):
 rng=np.random.default_rng(SEED); o=abs(x.mean()); s=rng.choice([-1,1],size=(n,len(x))); z=np.abs((s*x).mean(axis=1)); return float((1+(z>=o).sum())/(n+1))
def main():
 e,d=load(); z=decomp(e,d); ee=e.drop(columns=[c for c in z.columns if c!="ref_ts" and c in e.columns],errors="ignore").merge(z,on="ref_ts",how="left")
 base=feat(ee); cols=[c for c in base if not c.startswith("ceemdan")]+[c for c in base if c.startswith("ceemdan")]
 tr=ee[ee.split=="train"].copy(); va=ee[ee.split=="validation"].copy(); ho=ee[ee.split=="holdout"].copy()
 rows=[]; econ=[]
 for sp,f,t in [("validation",tr,va),("holdout",pd.concat([tr,va]).sort_values("ref_ts"),ho)]:
  p=fit(f,t,cols); rows.append(pd.DataFrame({"split":sp,"ref_ts":t.ref_ts.to_numpy(),"expiry":t.expiry.to_numpy(),"target_return":t.target_return.to_numpy(),"target_direction":t.target_direction.to_numpy(),"ceemdan_tree_prob":p}))
  sr=np.where(p>=.5,1,-1)*t.target_return.to_numpy(float); lo,hi=boot(sr); econ.append({"split":sp,"model":"ceemdan_tree","hit_rate":float((sr>0).mean()),"mean_signed_log_return":float(sr.mean()),"sum_signed_log_return":float(sr.sum()),"bootstrap_ci_low":lo,"bootstrap_ci_high":hi,"signflip_pvalue":sf(sr)})
 pr=pd.concat(rows,ignore_index=True); pr.to_csv(OUT/"ceemdan_tree_predictions.csv",index=False)
 met=pd.DataFrame([{"split":sp,"model":"ceemdan_tree",**metric(g.target_direction,g.ceemdan_tree_prob)} for sp,g in pr.groupby("split")]); met.to_csv(OUT/"ceemdan_tree_metrics.csv",index=False)
 pd.DataFrame(econ).to_csv(OUT/"ceemdan_tree_economic.csv",index=False)
 print(met.to_string(index=False)); print(pd.DataFrame(econ).to_string(index=False))
if __name__=="__main__": main()
