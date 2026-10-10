#!/usr/bin/env python3
"""Phase 95 common-data replication runner; common NIFTY adaptation != exact paper reproduction."""
from __future__ import annotations
import hashlib, json, math, random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import AdaBoostRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge, SGDRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[2]
OUT, CACHE = ROOT / "results/phase95", ROOT / ".cache/phase95"
CACHE_CSV = CACHE / "nifty_daily.csv"
TRAIN_END, TEST_END = pd.Timestamp("2025-01-01"), pd.Timestamp("2026-01-01")
WINDOWS, SEQ_LEN, SEED, BOOTSTRAPS, BLOCK_LEN = (5, 10, 20), 20, 90210, 2000, 5
CLASSICAL = ("linear_regression","lasso","ridge","elastic_net","sgd_regressor","svr","knn","decision_tree","random_forest","gradient_boosting","adaboost","xgboost","mlp","slp","rbf_network")
SEQUENCE = ("rnn","lstm","gru","cnn","tcn","lstm_gru","cnn_rnn","cnn_tcn","lstm_tcn","backward_elimination_lstm")
PAPER_MAP = {
 "linear_regression":"U01/U04/U09","lasso":"U04","ridge":"U04","elastic_net":"U04","sgd_regressor":"U04",
 "svr":"U01/U03/U04","knn":"U01/U04","decision_tree":"U01/U04","random_forest":"U02/U04",
 "gradient_boosting":"U04","adaboost":"U04","xgboost":"U02/U04","mlp":"U03/U04/U12","slp":"U03",
 "rbf_network":"U03","rnn":"U09/U11","lstm":"U01/U08/U09/U11/U13","gru":"U09","cnn":"U09/U11",
 "tcn":"U09","lstm_gru":"U09","cnn_rnn":"U09","cnn_tcn":"U09","lstm_tcn":"U09",
 "backward_elimination_lstm":"U13"
}

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def flatten_yf(frame: pd.DataFrame) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0) if "^NSEI" in set(frame.columns.get_level_values(-1)) else [str(c[0]) for c in frame.columns]
    frame.columns = [str(c).strip().title() for c in frame.columns]
    return frame.rename(columns={"Adj Close":"Adjclose"})

def acquire_daily_data() -> tuple[pd.DataFrame, dict[str,Any]]:
    CACHE.mkdir(parents=True,exist_ok=True)
    url="https://finance.yahoo.com/quote/%5ENSEI/history/"
    if CACHE_CSV.exists():
        try:
            d=pd.read_csv(CACHE_CSV,parse_dates=["Date"]).set_index("Date")
            d.index=pd.to_datetime(d.index).tz_localize(None)
            d=d.loc[(d.index>="2004-01-01")&(d.index<"2026-01-01")]
            if {"Open","High","Low","Close"}.issubset(d.columns) and len(d)>=2500 and d.index.max()<TEST_END:
                return d.sort_index(),{"source":"Yahoo Finance ^NSEI","source_url":url,"cache_used":True,"retrieved_at_utc":None,"requested_start":"2004-01-01","requested_end_exclusive":"2026-01-01","rows":int(len(d)),"first_date":str(d.index.min().date()),"last_date":str(d.index.max().date()),"sha256":sha256_file(CACHE_CSV)}
        except Exception: pass
    import yfinance as yf
    d=yf.download("^NSEI",start="2004-01-01",end="2026-01-01",auto_adjust=False,progress=False,actions=False,group_by="column",threads=False)
    if d is None or d.empty: raise RuntimeError("Yahoo Finance returned empty ^NSEI daily data")
    d=flatten_yf(d)
    d.index=pd.to_datetime(d.index).tz_localize(None); d.index.name="Date"
    missing={"Open","High","Low","Close"}-set(d.columns)
    if missing: raise ValueError(f"required OHLC fields missing: {sorted(missing)}; got {list(d.columns)}")
    d=d.loc[(d.index>="2004-01-01")&(d.index<"2026-01-01")]
    d=d[~d.index.duplicated(keep="last")].sort_index().replace([np.inf,-np.inf],np.nan).dropna(subset=["Open","High","Low","Close"])
    if len(d)<2500: raise ValueError(f"insufficient rows for the registered long-window study: {len(d)}")
    d.to_csv(CACHE_CSV,index_label="Date",float_format="%.8f")
    info={"source":"Yahoo Finance ^NSEI","source_url":url,"cache_used":False,"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"requested_start":"2004-01-01","requested_end_exclusive":"2026-01-01","rows":int(len(d)),"first_date":str(d.index.min().date()),"last_date":str(d.index.max().date()),"sha256":sha256_file(CACHE_CSV),"note":"Raw bars remain in Actions cache; not committed."}
    return d,info

def add_features(raw: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    d=raw.copy().sort_index()
    required=["Open","High","Low","Close"]
    if not set(required).issubset(d.columns): raise ValueError("OHLC fields required")
    vol=d["Volume"] if "Volume" in d.columns else pd.Series(0.0,index=d.index)
    if vol.isna().all(): vol=pd.Series(0.0,index=d.index)
    X=pd.DataFrame(index=d.index)
    for c in required: X[c.lower()+"_t"]=pd.to_numeric(d[c],errors="coerce")
    X["volume_t"]=pd.to_numeric(vol,errors="coerce").fillna(0.0)
    ret=d["Close"].pct_change()
    for lag in (1,5,10,20): X[f"ret_{lag}"]=ret if lag==1 else d["Close"].pct_change(lag)
    for win in (5,20,50): X[f"sma_gap_{win}"]=d["Close"]/d["Close"].rolling(win).mean()-1
    X["ema_gap_12"]=d["Close"]/d["Close"].ewm(span=12,adjust=False).mean()-1
    X["ema_gap_26"]=d["Close"]/d["Close"].ewm(span=26,adjust=False).mean()-1
    delta=d["Close"].diff(); gain=delta.clip(lower=0).rolling(14).mean(); loss=-delta.clip(upper=0).rolling(14).mean()
    rs=gain/loss.replace(0,np.nan); X["rsi14"]=(100-100/(1+rs))/100
    X["volatility20"]=ret.rolling(20).std(); X["range_pct"]=(d["High"]-d["Low"])/d["Close"]
    y=pd.DataFrame(index=d.index); y["TargetDate"]=pd.Series(d.index,index=d.index).shift(-1)
    for c in ("Open","High","Low","Close"): y["target_"+c.lower()]=d[c].shift(-1)
    for c in ("Open","High","Low","Close"): y["previous_"+c.lower()]=d[c]
    X=X.replace([np.inf,-np.inf],np.nan)
    valid=X.notna().all(axis=1)
    X=X.loc[valid].astype(float); y=y.loc[valid]
    valid=y["TargetDate"].notna() & y.filter(like="target_").notna().all(axis=1)
    return X.loc[valid],y.loc[valid]

def make_estimator(name: str):
    r= {"linear_regression":lambda:LinearRegression(),
        "lasso":lambda:Lasso(alpha=.001,max_iter=10000,random_state=SEED),
        "ridge":lambda:Ridge(alpha=1.0),
        "elastic_net":lambda:ElasticNet(alpha=.001,l1_ratio=.5,max_iter=10000,random_state=SEED),
        "sgd_regressor":lambda:SGDRegressor(max_iter=2500,tol=1e-4,random_state=SEED),
        "svr":lambda:SVR(C=10,epsilon=.05,kernel="rbf"),
        "knn":lambda:KNeighborsRegressor(n_neighbors=10,weights="distance"),
        "decision_tree":lambda:DecisionTreeRegressor(max_depth=4,min_samples_leaf=5,random_state=SEED),
        "random_forest":lambda:RandomForestRegressor(n_estimators=100,max_depth=5,min_samples_leaf=3,n_jobs=1,random_state=SEED),
        "gradient_boosting":lambda:GradientBoostingRegressor(n_estimators=100,max_depth=2,learning_rate=.05,random_state=SEED),
        "adaboost":lambda:AdaBoostRegressor(estimator=DecisionTreeRegressor(max_depth=2,random_state=SEED),n_estimators=80,learning_rate=.05,random_state=SEED),
        "mlp":lambda:MLPRegressor(hidden_layer_sizes=(32,16),max_iter=250,early_stopping=True,random_state=SEED),
        "slp":lambda:MLPRegressor(hidden_layer_sizes=(),activation="identity",solver="lbfgs",max_iter=500,random_state=SEED)}
    if name=="xgboost":
        from xgboost import XGBRegressor
        model=XGBRegressor(n_estimators=120,max_depth=3,learning_rate=.03,subsample=.9,colsample_bytree=.9,objective="reg:squarederror",n_jobs=1,random_state=SEED,verbosity=0)
    elif name=="rbf_network":
        return Pipeline([("scale",StandardScaler()),("rbf",RBFSampler(gamma=.1,n_components=100,random_state=SEED)),("ridge",Ridge(alpha=1.0))])
    else: model=r[name]()
    return Pipeline([("scale",StandardScaler()),("model",model)])

def block_bootstrap_ci(x: np.ndarray,rng:np.random.Generator,n_boot:int=BOOTSTRAPS,block_len:int=BLOCK_LEN)->tuple[float,float]:
    x=np.asarray(x,float); n=len(x)
    if n<max(30,block_len*3): return float("nan"),float("nan")
    means=np.empty(n_boot); n_blocks=math.ceil(n/block_len)
    for b in range(n_boot):
        ids=[]
        for _ in range(n_blocks):
            start=int(rng.integers(0,n)); ids.extend((start+k)%n for k in range(block_len))
        means[b]=np.mean(x[np.asarray(ids[:n])])
    return float(np.quantile(means,.025)),float(np.quantile(means,.975))

def hac_p_value(x: np.ndarray)->float:
    if len(x)<30: return float("nan")
    import statsmodels.api as sm
    fit=sm.OLS(np.asarray(x,float),np.ones((len(x),1))).fit()
    robust=fit.get_robustcov_results(cov_type="HAC",maxlags=5)
    return float(2*stats.t.sf(abs(float(robust.tvalues[0])),df=max(1,len(x)-1)))

def select_features(X: pd.DataFrame,y: pd.Series,name:str)->list[str]:
    if name!="backward_elimination_lstm": return list(X.columns)
    scores=mutual_info_regression(X,y,random_state=SEED)
    order=np.argsort(np.nan_to_num(scores,nan=-1.0))[::-1]
    return list(X.columns[order[:min(8,max(3,math.ceil(len(order)/2)))]])

def fit_sequence(name:str,X:pd.DataFrame,y:pd.Series,train:np.ndarray,test:np.ndarray)->np.ndarray:
    import torch
    from torch import nn
    import torch.nn.functional as F
    torch.manual_seed(SEED); np.random.seed(SEED); torch.set_num_threads(1)
    tr=np.flatnonzero(train); te=np.flatnonzero(test)
    if len(tr)<200 or len(te)<30: raise ValueError("sequence sample gate failed")
    selected=select_features(X.iloc[tr],y.iloc[tr].reset_index(drop=True),name)
    xsc=StandardScaler().fit(X[selected].iloc[tr])
    xs=xsc.transform(X[selected]).astype(np.float32)
    ysc=StandardScaler().fit(y.iloc[tr].to_numpy().reshape(-1,1))
    ys=ysc.transform(y.to_numpy().reshape(-1,1)).astype(np.float32).ravel()
    seq=np.zeros((len(xs),SEQ_LEN,len(selected)),dtype=np.float32)
    for i in range(SEQ_LEN-1,len(xs)): seq[i]=xs[i-SEQ_LEN+1:i+1]
    tr=tr[tr>=SEQ_LEN-1]; te=te[te>=SEQ_LEN-1]
    if len(tr)<200 or len(te)<30: raise ValueError("insufficient rows after sequence-lookback exclusion")
    class Net(nn.Module):
        def __init__(self,k,nf):
            super().__init__(); self.k=k
            self.r1=None; self.r2=None; self.c1=None; self.t1=None; self.t2=None
            if k in ("rnn","lstm","gru"):
                self.r1={"rnn":nn.RNN,"lstm":nn.LSTM,"gru":nn.GRU}[k](nf,16,batch_first=True); dim=16
            elif k=="cnn": self.c1=nn.Conv1d(nf,16,3); dim=16
            elif k=="tcn": self.t1=nn.Conv1d(nf,16,3); self.t2=nn.Conv1d(16,16,3,dilation=2); dim=16
            else:
                if k in ("lstm_gru","lstm_tcn"): self.r1=nn.LSTM(nf,16,batch_first=True)
                else: self.c1=nn.Conv1d(nf,16,3)
                if k=="lstm_gru": self.r2=nn.GRU(nf,16,batch_first=True)
                elif k=="cnn_rnn": self.r2=nn.RNN(nf,16,batch_first=True)
                elif k in ("cnn_tcn","lstm_tcn"): self.t1=nn.Conv1d(nf,16,3); self.t2=nn.Conv1d(16,16,3,dilation=2)
                dim=32
            self.out=nn.Sequential(nn.Linear(dim,16),nn.ReLU(),nn.Linear(16,1))
        def rnn(self,m,x):
            z=m(x); z=z[0] if isinstance(z,tuple) else z
            return z[:,-1,:]
        def cnn(self,x):
            z=F.pad(x.transpose(1,2),(2,0)); z=torch.relu(self.c1(z)); return z[:,:,-1]
        def tcn(self,x):
            z=torch.relu(self.t1(F.pad(x.transpose(1,2),(2,0))))
            z=torch.relu(self.t2(F.pad(z,(4,0)))); return z[:,:,-1]
        def forward(self,x):
            k=self.k
            if k in ("rnn","lstm","gru"): z=self.rnn(self.r1,x)
            elif k=="cnn": z=self.cnn(x)
            elif k=="tcn": z=self.tcn(x)
            elif k=="lstm_gru": z=torch.cat([self.rnn(self.r1,x),self.rnn(self.r2,x)],1)
            elif k=="cnn_rnn": z=torch.cat([self.cnn(x),self.rnn(self.r2,x)],1)
            elif k=="cnn_tcn": z=torch.cat([self.cnn(x),self.tcn(x)],1)
            else: z=torch.cat([self.rnn(self.r1,x),self.tcn(x)],1)
            return self.out(z).squeeze(-1)
    kind="lstm" if name=="backward_elimination_lstm" else name
    net=Net(kind,len(selected)); opt=torch.optim.Adam(net.parameters(),lr=.005,weight_decay=1e-4); loss=nn.MSELoss()
    xt=torch.tensor(seq[tr]); yt=torch.tensor(ys[tr]); xv=torch.tensor(seq[te])
    net.train()
    for _ in range(12):
        order=torch.randperm(len(tr))
        for start in range(0,len(order),64):
            b=order[start:start+64]; opt.zero_grad(set_to_none=True); lv=loss(net(xt[b]),yt[b]); lv.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(),2.0); opt.step()
    net.eval()
    with torch.no_grad(): pp=ysc.inverse_transform(net(xv).cpu().numpy().reshape(-1,1)).ravel()
    result=np.full(len(X),np.nan); result[te]=pp
    return result

def run_suite(X:pd.DataFrame,T:pd.DataFrame):
    metric=[]; pred_store={}; cover=[]; dates=pd.to_datetime(T["TargetDate"])
    for yrs in WINDOWS:
        start=TRAIN_END-pd.DateOffset(years=yrs)
        for target in ("Close","Open","High","Low"):
            tr=((dates>=start)&(dates<TRAIN_END)).to_numpy()
            te=((dates>=TRAIN_END)&(dates<TEST_END)).to_numpy()
            tri=np.flatnonzero(tr); tei=np.flatnonzero(te); tk="target_"+target.lower()
            if len(tri)<200 or len(tei)<30:
                cover.append({"target":target,"train_window_years":yrs,"status":"DATA_BLOCKED","train_rows":len(tri),"test_rows":len(tei),"reason":"minimum sample gate failed"}); continue
            names=list(CLASSICAL) if target in ("Close","Open") else ["mlp","slp"]
            if target=="Close": names+=list(SEQUENCE)
            for name in names:
                try:
                    yy=T[tk].astype(float)
                    if name in SEQUENCE:
                        pp=fit_sequence(name,X,yy,tr,te)
                        valid=tei[np.isfinite(pp[tei])]
                        if len(valid)<30: raise ValueError("too few sequence predictions")
                        y=yy.iloc[valid].to_numpy(); pred=pp[valid]; base=T[f"previous_{target.lower()}"].iloc[valid].to_numpy()
                        td=dates.iloc[valid]; prev=T["previous_close"].iloc[valid].to_numpy()
                    else:
                        est=TransformedTargetRegressor(regressor=make_estimator(name),transformer=StandardScaler())
                        est.fit(X.iloc[tri],yy.iloc[tri]); pred=np.asarray(est.predict(X.iloc[tei]),float)
                        y=yy.iloc[tei].to_numpy(); base=T[f"previous_{target.lower()}"].iloc[tei].to_numpy()
                        td=dates.iloc[tei]; prev=T["previous_close"].iloc[tei].to_numpy()
                        valid=tei
                    err=pred-y; baseerr=base-y; mae=float(np.mean(abs(err))); bmae=float(np.mean(abs(baseerr)))
                    r2=float(1-np.sum(err**2)/np.sum((y-np.mean(y))**2)) if np.sum((y-np.mean(y))**2)>0 else None
                    row={"paper_method_ids":PAPER_MAP.get(name,""),"model":name,"target":target,"train_window_years":yrs,
                         "train_rows":len(tri),"test_rows":len(y),"test_first":str(pd.to_datetime(td).min().date()),"test_last":str(pd.to_datetime(td).max().date()),
                         "mae":mae,"rmse":float(np.sqrt(np.mean(err**2))),"r2":r2,
                         "mape_pct":float(np.mean(abs(err/np.where(abs(y)<1e-9,np.nan,y)))*100),
                         "persistence_mae":bmae,"mae_improvement_vs_persistence":bmae-mae,
                         "directional_accuracy_pct":float(np.mean(np.sign(pred-prev)==np.sign(y-prev))*100) if target=="Close" else None,
                         "bootstrap_ci_low":None,"bootstrap_ci_high":None,"hac_p_value":None,"holm_p_value":None,
                         "decision_vs_persistence":"PENDING_INFERENCE","status":"OK",
                         "replication_scope":"PARTIAL_COMMON_NIFTY_ADAPTATION"}
                    metric.append(row); pred_store[(target,yrs,name)]={"y":y,"pred":pred,"baseline":base}
                except Exception as e:
                    metric.append({"paper_method_ids":PAPER_MAP.get(name,""),"model":name,"target":target,"train_window_years":yrs,
                                   "train_rows":len(tri),"test_rows":len(tei),"status":"MODEL_FAILED","error":f"{type(e).__name__}: {str(e)[:250]}",
                                   "replication_scope":"PARTIAL_COMMON_NIFTY_ADAPTATION"})
                    with (OUT/"model_errors.log").open("a",encoding="utf-8") as f: f.write(f"{datetime.now(timezone.utc).isoformat()} {target}/{yrs}/{name}: {type(e).__name__}: {e}\\n")
            cover.append({"target":target,"train_window_years":yrs,"status":"SAMPLE_GATE_PASS","train_rows":len(tri),"test_rows":len(tei),"reason":"fixed target window; baseline available"})
    rng=np.random.default_rng(SEED); valid_p=[]; valid_rows=[]
    for row in metric:
        key=(row.get("target"),row.get("train_window_years"),row.get("model"))
        if key not in pred_store: continue
        z=pred_store[key]; improvement=abs(z["baseline"]-z["y"])-abs(z["pred"]-z["y"])
        lo,hi=block_bootstrap_ci(improvement,rng); p=hac_p_value(improvement)
        row["bootstrap_ci_low"]=lo; row["bootstrap_ci_high"]=hi; row["hac_p_value"]=p
        row["decision_vs_persistence"]="MAE_GAIN_CI_ABOVE_ZERO" if np.isfinite(lo) and lo>0 else "MAE_WORSENING_CI_BELOW_ZERO" if np.isfinite(hi) and hi<0 else "NO_CLEAR_INCREMENTAL_MAE_GAIN"
        if np.isfinite(p): valid_p.append(p); valid_rows.append(row)
    if valid_p:
        adj=multipletests(valid_p,method="holm")[1]
        for row,p in zip(valid_rows,adj):
            row["holm_p_value"]=float(p)
            if row["decision_vs_persistence"]=="MAE_GAIN_CI_ABOVE_ZERO" and p>=.05: row["decision_vs_persistence"]="CI_GAIN_BUT_HOLM_P_NOT_SIGNIFICANT"
    return metric,pred_store,pd.DataFrame(cover)

def write_outputs(raw,manifest,metrics,coverage,blocker=None):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"data_manifest.json").write_text(json.dumps(manifest,indent=2,default=str)+"\\n",encoding="utf-8")
    pd.DataFrame(metrics).to_csv(OUT/"model_metrics.csv",index=False); coverage.to_csv(OUT/"coverage.csv",index=False)
    mods=[
      ("NIFTY OHLC daily","AVAILABLE" if raw is not None else "DATA_BLOCKED","used in Phase 95"),
      ("USD/INR","NOT_ACQUIRED","U03 external-input reproduction remains partial"),
      ("FII/DII gross flows","NOT_VALIDATED","not silently substituted"),
      ("India VIX","NOT_ACQUIRED_IN_THIS_RUNNER","U06 feature model not fully reproduced"),
      ("Historical PCR and Greeks","DATA_GATE_PENDING","exact option-chain data required"),
      ("Point-in-time news/BERT sentiment","DATA_GATE_PENDING","U06 multimodal model not run"),
      ("Exact listed options quotes/depth","DATA_GATE_PENDING","no option P&L in Phase 95")]
    pd.DataFrame([{"input":a,"status":b,"note":c} for a,b,c in mods]).to_csv(OUT/"modality_status.csv",index=False)
    ok=[r for r in metrics if r.get("status")=="OK"]; fail=[r for r in metrics if r.get("status")=="MODEL_FAILED"]
    top=sorted(ok,key=lambda r:r["mae_improvement_vs_persistence"],reverse=True)[:10]
    lines=["# Phase 95 — Daily Forecast Model Replication Report","",f"Run UTC: {datetime.now(timezone.utc).isoformat()}",
      f"Status: {'DATA_BLOCKED' if blocker else 'COMPLETED_WITH_MODEL_FAILURES' if fail else 'COMPLETED'}","",
      "## Evidence boundary","This is a common-data NIFTY adaptation, not exact replication of every source's stock universe, period, external features or disclosed hyperparameters. Forecast accuracy is not options profitability. No strategy is promoted.","",
      "## Data provenance",f"- Source: {manifest.get('source','unknown')}",f"- Dates: {manifest.get('first_date')} to {manifest.get('last_date')}",
      f"- Rows: {manifest.get('rows')}",f"- SHA-256: {manifest.get('sha256')}",f"- Cache used: {manifest.get('cache_used')}",f"- Blocker: {blocker or 'none'}","",
      "## Coverage",f"- Successful model/target/window rows: {len(ok)}",f"- Explicit model failures: {len(fail)}",
      "- Common test targets are restricted to 2025; no 2026 targets are scored.",
      "- Inference: circular moving-block bootstrap CI (5 sessions, 2,000 draws), HAC paired loss-difference p-values (lag 5), and Holm correction.","",
      "## Top ten by MAE improvement over persistence (descriptive only)","",
      "| Model | Target | Training years | OOS n | MAE | Persistence MAE | Improvement | Bootstrap CI | Holm p | Decision |",
      "|---|---|---:|---:|---:|---:|---:|---|---:|---|"]
    for r in top:
        lo,hi=r.get("bootstrap_ci_low"),r.get("bootstrap_ci_high"); ci=f"[{lo:.4f}, {hi:.4f}]" if lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi) else "n/a"
        hp=r.get("holm_p_value"); ps=f"{hp:.4g}" if hp is not None and np.isfinite(hp) else "n/a"
        lines.append(f"| {r['model']} | {r['target']} | {r['train_window_years']} | {r['test_rows']} | {r['mae']:.4f} | {r['persistence_mae']:.4f} | {r['mae_improvement_vs_persistence']:.4f} | {ci} | {ps} | {r['decision_vs_persistence']} |")
    lines += ["","## Limitations and paper-specific blockers",
      "- USD/INR, historical FII/DII, India VIX, PCR, options Greeks and point-in-time news were not supplied by the primary price feed. The multimodal papers remain partial/data-gated.",
      "- U12's source includes turnover; Yahoo index volume is not asserted to be equivalent.",
      "- The common 2025 test period is chronological relative to this runner's fit but may overlap the source data period of newer papers. It is not automatically post-publication validation.",
      "- Price-level R-squared can be inflated by persistence. Consider error improvement, return/directional skill and calibrated confidence, not accuracy alone.",
      "- Fixed settings are transparent operationalizations when source-specific settings are unavailable. Exact paper-metric reproduction must be separately audited.",
      "- Options P&L is not calculated in this phase; no promotion.", "",
      "## Artifacts","- \`model_metrics.csv\`: metrics/failures/inference","- \`coverage.csv\`: target/window sample gates",
      "- \`modality_status.csv\`: unavailable external inputs","- \`data_manifest.json\`: source provenance/hash","- \`run_summary.json\`: machine-readable decision"]
    (OUT/"REPORT.md").write_text("\\n".join(lines)+"\\n",encoding="utf-8")
    # Machine-readable plot data are displayed in the report; this plot is generated only if metrics exist.
    try:
        import matplotlib.pyplot as plt
        if ok:
            show=sorted(ok,key=lambda r:r["mae_improvement_vs_persistence"],reverse=True)[:15]
            fig,ax=plt.subplots(figsize=(11,6)); labels=[f"{r['model']} / {r['target']} / {r['train_window_years']}y" for r in show]
            vals=[r["mae_improvement_vs_persistence"] for r in show]
            ax.barh(labels[::-1],vals[::-1]); ax.axvline(0,color="black",linewidth=.8)
            ax.set_xlabel("MAE improvement over persistence (index points; positive is better)")
            ax.set_title("Phase 95 — descriptive top 15 model comparisons"); fig.tight_layout()
            fig.savefig(OUT/"comparison.svg",format="svg"); plt.close(fig)
    except Exception as e:
        with (ROOT/"PHASE95_ERROR_LOG.md").open("a",encoding="utf-8") as f: f.write(f"\\n## E95-PLOT\\n- {type(e).__name__}: {e}\\n")
    summary={"phase":95,"status":"DATA_BLOCKED" if blocker else "COMPLETED_WITH_MODEL_FAILURES" if fail else "COMPLETED",
      "run_at_utc":datetime.now(timezone.utc).isoformat(),"valid_metric_rows":len(ok),"model_failure_rows":len(fail),
      "all_metrics_rows":len(metrics),"raw_data_committed":False,"phase83_holdout_accessed":False,
      "strategy_promoted":False,"blocked_reason":blocker}
    (OUT/"run_summary.json").write_text(json.dumps(summary,indent=2)+"\\n",encoding="utf-8")
    (ROOT/"PHASE95_STATUS.md").write_text(
      "# Phase 95 Status — Daily Forecast Replication\\n\\n"
      f"**Last run:** {summary['run_at_utc']}\\n**Status:** {summary['status']}\\n"
      f"**Valid metric rows:** {len(ok)}; **model failures:** {len(fail)}\\n**Data blocker:** {blocker or 'none'}\\n**Strategy promotion:** NONE\\n\\n"
      "- [Plan](PHASE95_RESEARCH_PLAN.md)\\n- [Report](results/phase95/REPORT.md)\\n- [Metrics](results/phase95/model_metrics.csv)\\n"
      "- [Data manifest](results/phase95/data_manifest.json)\\n- [Coverage](results/phase95/coverage.csv)\\n- [Modality status](results/phase95/modality_status.csv)\\n"
      "- [Error log](PHASE95_ERROR_LOG.md)\\n- [Research log](PHASE95_RESEARCH_LOG.md)\\n- [Chat log](PHASE95_CHAT_LOG.md)\\n\\n"
      "Common-data forecasts are partial unless source protocols and metrics are matched. No options P&L is calculated in this phase. Phase 83 holdout remains sealed.\\n",encoding="utf-8")
    if blocker or fail:
        with (ROOT/"PHASE95_ERROR_LOG.md").open("a",encoding="utf-8") as f:
            if blocker: f.write(f"\\n## E95-DATA — {summary['run_at_utc']}\\n- Data blocker: {blocker}\\n- No metric was fabricated.\\n")
            if fail:
                f.write(f"\\n## E95-MODEL — {summary['run_at_utc']}\\n- Failed model rows: {len(fail)}\\n")
                for r in fail[:30]: f.write(f"- {r.get('target')}/{r.get('train_window_years')}y/{r.get('model')}: {r.get('error')}\\n")
    with (ROOT/"PHASE95_RESEARCH_LOG.md").open("a",encoding="utf-8") as f:
        f.write(f"\\n## Automated run — {summary['run_at_utc']}\\n- Status: {summary['status']}\\n- Valid metric rows: {len(ok)}\\n- Failed model rows: {len(fail)}\\n- Data blocker: {blocker or 'none'}\\n- Strategy promoted: none; Phase 83 accessed: no.\\n")

def main():
    random.seed(SEED); np.random.seed(SEED); OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"model_errors.log").write_text("",encoding="utf-8")
    manifest={"source":"Yahoo Finance ^NSEI","requested_start":"2004-01-01","requested_end_exclusive":"2026-01-01","test_start":"2025-01-01","test_end_exclusive":"2026-01-01","raw_data_committed":False,"phase83_holdout_accessed":False}
    try:
        raw,info=acquire_daily_data(); manifest.update(info); X,T=add_features(raw)
        metrics,preds,cov=run_suite(X,T); write_outputs(raw,manifest,metrics,cov)
        print(json.dumps({"status":"COMPLETED","metrics_rows":len(metrics),"valid":sum(r.get("status")=="OK" for r in metrics),"failed":sum(r.get("status")=="MODEL_FAILED" for r in metrics),"sha256":manifest.get("sha256")},indent=2))
    except Exception as e:
        reason=f"{type(e).__name__}: {str(e)}"
        manifest.update({"rows":0,"first_date":None,"last_date":None,"sha256":None,"cache_used":False,"source_error":reason})
        write_outputs(None,manifest,[],pd.DataFrame([{"status":"DATA_BLOCKED","reason":reason}]),blocker=reason)
        print(json.dumps({"status":"DATA_BLOCKED","reason":reason},indent=2))
if __name__=="__main__": main()
