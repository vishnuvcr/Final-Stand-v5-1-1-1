#!/usr/bin/env python3
"""Sequential out-of-sample factor-selector screen on frozen Phase45 outcomes and Phase39 features.

This tests selectors on existing fixed-template outcomes. It is not the complete
Phase52 structural-parameter replay and does not invent missing futures data.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

TZ = "Asia/Kolkata"
META = {"entry_ts","expiry","split","control_direction","control_net_rupees",
        "delta_pnl_call_minus_put","intraday_source_ts"}
RISK_LIMITED = {
 "buy_call","buy_put","bull_call_spread","bear_put_spread","bull_put_spread","bear_call_spread",
 "long_straddle","long_strangle","bull_condor","bear_condor","bull_butterfly","bear_butterfly",
 "long_iron_condor","long_iron_butterfly","double_plateau","strip","strap",
 "long_atm_call_butterfly","long_atm_put_butterfly","short_iron_butterfly","short_iron_condor",
 "call_broken_wing_butterfly","put_broken_wing_butterfly","long_call_calendar","long_put_calendar",
 "bull_call_debit","bear_put_debit","bull_put_credit","bear_call_credit","long_call_butterfly","long_put_butterfly",
 "iron_butterfly","iron_condor","call_broken_wing","put_broken_wing","call_backspread","put_backspread","call_calendar","put_calendar"
}
FACTOR_FEATURES = {
 "GREEKS_SURFACE_ROUTER":["atm_ce_delta","atm_pe_delta","atm_ce_iv","atm_pe_iv","atm_iv_skew","candidate_iv_skew_25","iv_term_premium_ratio","atm_straddle","call_25_delta","put_25_delta"],
 "OI_FLOW_ROUTER":["atm_pcr_oi","candidate_oi_pcr_25","near_atm_oi_pcr","atm_pcr_volume","near_atm_volume_pcr","atm_ce_oi","atm_pe_oi","call_25_oi","put_25_oi"],
 "SPOT_PROXY_ONLY":["nifty_ret_15m","nifty_ret_60m","nifty_daily_ret_1d","nifty_daily_ret_5d","nifty_ma_gap_15m","nifty_rv_15m","nifty_rv_60m","nifty_range_15m"],
 "GLOBAL_SENTIMENT_PROXY":["global_SP500_ret1","global_NASDAQ_ret1","global_VIX_ret1","global_NIKKEI_ret1","global_SENSEX_ret1","global_GOLD_ret1","global_CRUDE_ret1","global_USDINR_ret1","sent_sent_mean","sent_sent_pos","sent_sent_neg"]
}
MULTI = [
 ("TREND_X_IV_SKEW","nifty_ret_60m","atm_iv_skew"),
 ("DAILY_TREND_X_PCR","nifty_daily_ret_1d","atm_pcr_oi"),
 ("SPOT_TREND_X_GLOBAL_VIX","nifty_ret_60m","global_VIX_ret1")
]

def ts_ist(s):
    x=pd.to_datetime(s,errors="coerce")
    return x.dt.tz_localize(TZ) if getattr(x.dt,"tz",None) is None else x.dt.tz_convert(TZ)

def parse_vix(x):
    try: states=set(json.loads(x)) if isinstance(x,str) else set(x or [])
    except Exception: states=set()
    for s in ("HIGH_RISING","SPIKE","HIGH","LOW","NORMAL","RISING","FALLING"):
        if s in states:return s
    return "UNAVAILABLE"

def read_join(trades_path,features_path):
    t=pd.read_csv(trades_path,low_memory=False); f=pd.read_csv(features_path,low_memory=False)
    if "net" not in t and "net_rupees" in t:t["net"]=t["net_rupees"]
    if "net50" not in t and "net_plus50_cost_rupees" in t:t["net50"]=t["net_plus50_cost_rupees"]
    req={"expiry","entry_ts","split","strategy","net","net50","active_states"}
    if req-set(t):raise ValueError("Trade matrix missing columns: "+str(sorted(req-set(t))))
    if {"expiry","entry_ts"}-set(f):raise ValueError("Feature panel missing expiry/entry_ts")
    t["entry_ts"]=ts_ist(t["entry_ts"]); f["entry_ts"]=ts_ist(f["entry_ts"])
    t["expiry_key"]=pd.to_datetime(t["expiry"],errors="coerce").dt.strftime("%Y-%m-%d")
    f["expiry_key"]=pd.to_datetime(f["expiry"],errors="coerce").dt.strftime("%Y-%m-%d")
    f=f.dropna(subset=["entry_ts","expiry_key"]).sort_values(["expiry_key","entry_ts"])
    fcols=[c for c in f if c not in META and c!="expiry_key"]
    for c in fcols:f[c]=pd.to_numeric(f[c],errors="coerce")
    byexp={k:g.reset_index(drop=True) for k,g in f.groupby("expiry_key",sort=False)}
    blocks=[]; lag_values=[]
    for key, tg in t.groupby("expiry_key",sort=False):
        fg=byexp.get(key); b=tg.copy()
        if fg is None or fg.empty:
            for c in fcols:b[c]=np.nan
            b["feature_lag_minutes"]=np.nan;blocks.append(b);continue
        fns=fg.entry_ts.astype("int64").to_numpy();tns=tg.entry_ts.astype("int64").to_numpy()
        ii=np.searchsorted(fns,tns,side="right")-1
        ok=ii>=0; lag=np.full(len(tg),np.nan)
        lag[ok]=(tns[ok]-fns[ii[ok]])/60e9
        ok &= np.isfinite(lag)&(lag>=0)&(lag<=1440)
        for c in fcols:
            a=np.full(len(tg),np.nan)
            if ok.any():a[ok]=fg[c].to_numpy()[ii[ok]]
            b[c]=a
        b["feature_lag_minutes"]=lag;blocks.append(b)
    z=pd.concat(blocks,ignore_index=True)
    z["net"]=pd.to_numeric(z.net,errors="coerce");z["net50"]=pd.to_numeric(z.net50,errors="coerce")
    # cost routines scale charges/slippage linearly in the source backtest; this is a
    # modelled +100% friction sensitivity, not an actual brokerage statement.
    z["net100"]=2*z.net50-z.net
    z["expiry_key"]=pd.to_datetime(z.expiry,errors="coerce").dt.strftime("%Y-%m-%d")
    z["expiry_date"]=pd.to_datetime(z.expiry,errors="coerce")
    z["entry_date"]=z.entry_ts.dt.strftime("%Y-%m-%d")
    z["vix_state"]=z.active_states.apply(parse_vix)
    z["feature_matched"]=z.feature_lag_minutes.between(0,1440,inclusive="both")
    audit={"trade_rows_input":int(len(t)),"feature_rows_input":int(len(f)),
      "trade_rows_with_asof_feature_match":int(z.feature_matched.sum()),
      "feature_match_rate":float(z.feature_matched.mean()) if len(z) else 0.0,
      "feature_match_by_split":{str(k):{"rows":int(len(g)),"matched_rows":int(g.feature_matched.sum()),"coverage":float(g.feature_matched.mean()),"matched_unique_expiries":int(g.loc[g.feature_matched,"expiry_key"].nunique())} for k,g in z.groupby("split",dropna=False)},
      "median_feature_lag_minutes":float(z.loc[z.feature_matched,"feature_lag_minutes"].median()) if z.feature_matched.any() else None,
      "max_feature_lag_minutes":float(z.loc[z.feature_matched,"feature_lag_minutes"].max()) if z.feature_matched.any() else None,
      "source_strategies":sorted(z.strategy.dropna().astype(str).unique().tolist()),
      "risk_limited_strategies_available":sorted(set(z.strategy.dropna().astype(str))&RISK_LIMITED)}
    return z,audit,fcols

def bins(data,feature,edges):
    x=pd.to_numeric(data[feature],errors="coerce").replace([np.inf,-np.inf],np.nan)
    out=pd.Series("UNAVAILABLE",index=data.index,dtype="object")
    if not edges:return out
    labels=["LOW","MID","HIGH"] if len(edges)==2 else ["LOW","HIGH"]
    ok=x.notna()
    out.loc[ok]=pd.cut(x.loc[ok],[-np.inf,*edges,np.inf],labels=labels,include_lowest=True,duplicates="drop").astype(str)
    return out

def edges_from(train,feature):
    x=pd.to_numeric(train[feature],errors="coerce").replace([np.inf,-np.inf],np.nan).dropna()
    if len(x)<20 or x.nunique()<2:return []
    a,b=float(x.quantile(1/3)),float(x.quantile(2/3))
    if not np.isfinite(a) or not np.isfinite(b) or a>=b:
        m=float(x.median());return [m] if np.isfinite(m) else []
    return [a,b]

def multi_bins(data,spec,edge_map):
    _,f1,f2=spec;b1=bins(data,f1,edge_map.get(f1,[]));b2=bins(data,f2,edge_map.get(f2,[]))
    s=b1.astype(str)+"__X__"+b2.astype(str);s[(b1=="UNAVAILABLE")|(b2=="UNAVAILABLE")]="UNAVAILABLE";return s

def strategy_universe(data):
    found=sorted(set(data.strategy.dropna().astype(str))&RISK_LIMITED)
    if len(found)<5:raise ValueError(f"Only {len(found)} risk-limited legacy strategies recognised: {found}")
    return found

def best_strategy(train,universe,min_n=8):
    g=train[train.strategy.isin(universe)].groupby("strategy").net50.agg(["mean","count"])
    g=g[(g["count"]>=min_n)&g["mean"].notna()]
    if g.empty:
        g=train[train.strategy.isin(universe)].groupby("strategy").net50.mean().dropna()
        if g.empty:raise ValueError("No usable risk-limited outcomes in training")
        return str(g.idxmax())
    return str(g.sort_values(["mean","count"],ascending=[False,False]).index[0])

def fit_map(train,universe,state,fallback,min_n=8):
    z=train.copy();z["_state"]=state.reindex(z.index).fillna("UNAVAILABLE").astype(str);mapping={}
    for st,g in z.groupby("_state",sort=True):
        q=g[g.strategy.isin(universe)];counts=q.groupby("strategy").size();keep=counts[counts>=min_n].index;q=q[q.strategy.isin(keep)]
        mapping[str(st)]=str(q.groupby("strategy").net50.mean().idxmax()) if len(q) and st!="UNAVAILABLE" else fallback
    return mapping

def paired_test(d,seed=5201,reps=5000,block_len=3):
    # Circular moving-block bootstrap preserves short-range serial dependence
    # across consecutive expiry observations. Sign-flip nulls use the same block
    # length rather than assuming every adjacent expiry is independent.
    x=np.asarray(d,float);x=x[np.isfinite(x)]
    if len(x)<8:return None,None,None
    rng=np.random.default_rng(seed);n=len(x);block_len=max(1,min(block_len,n//2));blocks=int(math.ceil(n/block_len))
    starts=rng.integers(0,n,size=(reps,blocks))
    offsets=np.arange(block_len)
    idx=((starts[:,:,None]+offsets[None,None,:])%n).reshape(reps,-1)[:,:n]
    means=x[idx].mean(axis=1)
    block_ids=np.minimum(np.arange(n)//block_len,blocks-1)
    signs=rng.choice(np.array([-1.0,1.0]),size=(reps,blocks))
    null=(x[None,:]*signs[:,block_ids]).mean(axis=1)
    p=(1+int(np.sum(null>=float(x.mean()))))/(reps+1)
    return float(np.quantile(means,.025)),float(np.quantile(means,.975)),float(p)

def metrics(selected,baseline):
    if selected.empty:return {"n":0}
    z=selected.sort_values("expiry_date");b=baseline.drop_duplicates("expiry_key").set_index("expiry_key")
    a=z.drop_duplicates("expiry_key").set_index("expiry_key")
    common=a.index.intersection(b.index);diff=a.loc[common,"net50"].to_numpy()-b.loc[common,"net50"].to_numpy()
    lo,hi,p=paired_test(diff)
    vals=z.net50.to_numpy(float);pos=vals[vals>0].sum();neg=-vals[vals<0].sum();cum=np.cumsum(vals)
    return {"n":int(z.expiry_key.nunique()),"net":float(z.net.sum()),"net50":float(z.net50.sum()),"net100":float(z.net100.sum()),
      "mean_net":float(z.net.mean()),"mean_net50":float(z.net50.mean()),"win_rate_net":float((z.net>0).mean()),
      "profit_factor_net50":float(pos/neg) if neg>0 else (float("inf") if pos>0 else None),
      "max_drawdown_net50":float(np.max(np.maximum.accumulate(cum)-cum)) if len(cum) else 0.0,
      "paired_common_expiries_vs_fixed":int(len(common)),"paired_mean_uplift_net50":float(diff.mean()) if len(diff) else None,
      "paired_bootstrap_ci95_lo":lo,"paired_bootstrap_ci95_hi":hi,"paired_signflip_p_one_sided":p}

def holm(pvalues):
    p=np.asarray([float(v) if v is not None and np.isfinite(v) else 1.0 for v in pvalues]);order=np.argsort(p);out=np.ones(len(p));cur=0.
    for rank,i in enumerate(order):cur=max(cur,min(1.,(len(p)-rank)*p[i]));out[i]=cur
    return [float(v) for v in out]

def collapse_predictions(test,states,mapping,fallback):
    episodes=test.sort_values(["expiry_key","entry_ts"]).drop_duplicates("expiry_key").copy()
    states=states.reindex(episodes.index).fillna("UNAVAILABLE").astype(str)
    pred=states.map(mapping).fillna(fallback)
    lookup=test.set_index(["expiry_key","strategy"],drop=False);chosen=[];fixed=[]
    for key,strategy in zip(episodes.expiry_key,pred):
        try:
            v=lookup.loc[(key,strategy)];chosen.append(v.iloc[0] if isinstance(v,pd.DataFrame) else v)
        except KeyError:continue
        try:
            v=lookup.loc[(key,fallback)];fixed.append(v.iloc[0] if isinstance(v,pd.DataFrame) else v)
        except KeyError:continue
    a=pd.DataFrame(chosen).drop_duplicates("expiry_key");b=pd.DataFrame(fixed).drop_duplicates("expiry_key")
    # Use identical expiry support for both the routed strategy and fixed baseline.
    # Do not let an expiry with a missing baseline outcome inflate selector totals.
    common=set(a["expiry_key"]) & set(b["expiry_key"])
    a=a[a["expiry_key"].isin(common)].sort_values("expiry_date").reset_index(drop=True)
    b=b[b["expiry_key"].isin(common)].sort_values("expiry_date").reset_index(drop=True)
    return a,b,pred,episodes

def run(trades_path,features_path,outdir,leakage_audit_path):
    outdir.mkdir(parents=True,exist_ok=True)
    source_audit=json.loads(Path(leakage_audit_path).read_text())
    if source_audit.get("status") != "PASS":
        raise RuntimeError("Phase39 point-in-time feature audit did not PASS")
    rules=source_audit.get("point_in_time_rules",{})
    if rules.get("interpolation") != "forbidden" or rules.get("forward_fill") != "forbidden":
        raise RuntimeError("Phase39 feature audit does not explicitly prohibit interpolation/forward fill")
    joined,audit,all_features=read_join(trades_path,features_path)
    audit["source_feature_leakage_audit_status"]=source_audit.get("status")
    audit["source_feature_rules"]=rules
    (outdir/"input_audit.json").write_text(json.dumps(audit,indent=2,allow_nan=False)+"\n")
    # PA-004: preserve and report point-in-time feature overlap rather than requiring
    # 90% of all legacy rows. This is allowed only as an exploratory matched-sample pilot:
    # >=50% overall and separately in development/validation, plus >=20 matched
    # validation expiries. Holdout is reported only if it independently meets that same
    # coverage/sample threshold; otherwise it remains explicitly unevaluated.
    low_coverage = audit["feature_match_rate"] < .50
    for split_name in {"development", "validation"}:
        block = audit.get("feature_match_by_split", {}).get(split_name, {"coverage": 0.0, "matched_unique_expiries": 0})
        if block["coverage"] < .50:
            low_coverage = True
        if split_name == "validation" and block["matched_unique_expiries"] < 20:
            low_coverage = True
    holdout_coverage = audit.get("feature_match_by_split", {}).get("holdout", {"coverage": 0.0, "matched_unique_expiries": 0})
    holdout_ready = holdout_coverage["coverage"] >= .50 and holdout_coverage["matched_unique_expiries"] >= 20
    if low_coverage:
        blocked = {
          "status": "BLOCKED_LOW_FEATURE_COVERAGE_NO_PERFORMANCE_ANALYSIS",
          "input_sha256": {"trade_matrix": hashlib.sha256(Path(trades_path).read_bytes()).hexdigest(), "feature_panel": hashlib.sha256(Path(features_path).read_bytes()).hexdigest()},
          "input_audit": audit, "risk_limited_strategy_count": 0, "selected_feature_by_mode": {},
          "limitations": ["Point-in-time feature overlap failed the preregistered coverage/sample gate; no factor P&L analysis was run."]
        }
        (outdir / "summary.json").write_text(json.dumps(blocked, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (outdir / "REPORT.md").write_text("# Phase 52 — Legacy Factor-Selector Pilot\n\n**Status:** blocked by point-in-time feature coverage. No factor or strategy performance analysis was run.\n\n" + json.dumps(audit, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": blocked["status"], "input_audit": audit}, indent=2, allow_nan=False))
        return blocked
    data=joined[joined.feature_matched&joined.net.notna()&joined.net50.notna()].copy()
    universe=strategy_universe(data);data=data[data.strategy.isin(universe)].copy()
    dev=data[data.split=="development"].copy();val=data[data.split=="validation"].copy();hold=data[data.split=="holdout"].copy()
    if min(len(dev),len(val))==0:raise RuntimeError(f"empty required split after filters: dev={len(dev)}, val={len(val)}, hold={len(hold)}")
    dates=np.array(sorted(pd.to_datetime(dev.entry_date).dropna().unique()))
    if len(dates)<30:raise RuntimeError(f"too few development dates for sequential fit/tune: {len(dates)}")
    cut=max(10,min(len(dates)-5,int(len(dates)*.70)));fit_end=pd.Timestamp(dates[cut-1]);tune_start=pd.Timestamp(dates[cut])
    fit=dev[pd.to_datetime(dev.entry_date)<=fit_end].copy();tune=dev[pd.to_datetime(dev.entry_date)>=tune_start].copy()
    baseline_fit=best_strategy(fit,universe,min_n=10)
    specs={"VIX_ROUTER":[("India_VIX_state","VIX")]}
    for group,feats in FACTOR_FEATURES.items():specs[group]=[(f,("NUM",f)) for f in feats if f in data.columns]
    specs["MULTI_FACTOR_ROUTER"]=[(n,("MULTI",(n,a,b))) for n,a,b in MULTI if a in data and b in data]
    tuned=[];chosen_specs={}
    for mode,variants in specs.items():
        for label,spec in variants:
            if spec=="VIX":
                fit_state=fit.vix_state.astype(str);tune_state=tune.vix_state.astype(str);em={}
            elif spec[0]=="NUM":
                f=spec[1]
                if min(fit[f].notna().mean(),tune[f].notna().mean())<.80:continue
                em={f:edges_from(fit,f)}
                if not em[f]:continue
                fit_state=bins(fit,f,em[f]);tune_state=bins(tune,f,em[f])
            else:
                _,f1,f2=spec[1]
                if min(fit[f1].notna().mean(),fit[f2].notna().mean(),tune[f1].notna().mean(),tune[f2].notna().mean())<.80:continue
                em={f1:edges_from(fit,f1),f2:edges_from(fit,f2)}
                if not all(em.values()):continue
                fit_state=multi_bins(fit,spec[1],em);tune_state=multi_bins(tune,spec[1],em)
            m=fit_map(fit,universe,fit_state,baseline_fit)
            a,b,pred,ep=collapse_predictions(tune,tune_state,m,baseline_fit)
            if a.empty or b.empty or len(a)<8:continue
            pairs=a.drop_duplicates("expiry_key").set_index("expiry_key").net50-b.drop_duplicates("expiry_key").set_index("expiry_key").net50
            uplift=float(pairs.mean()) if len(pairs) else -np.inf
            tuned.append({"mode":mode,"feature":label,"n_tune_expiries":int(len(pairs)),"mean_uplift_net50":uplift,"total_uplift_net50":float(pairs.sum()),"coverage":float(len(pairs)/tune.expiry_key.nunique())})
            chosen_specs[mode+"|"+label]={"spec":spec,"edges":em}
    if not tuned:raise RuntimeError("No selector met the point-in-time coverage/sample requirements")
    tune_df=pd.DataFrame(tuned).sort_values(["mode","mean_uplift_net50"],ascending=[True,False]);tune_df.to_csv(outdir/"development_tuning_candidates.csv",index=False)
    features_by_mode={mode:str(g.iloc[0].feature) for mode,g in tune_df.groupby("mode",sort=True)}
    baseline=best_strategy(dev,universe,min_n=10)
    results=[];selected_trades=[]
    for mode,label in features_by_mode.items():
        spec=chosen_specs[mode+"|"+label]["spec"]
        if spec=="VIX":
            dev_state=dev.vix_state.astype(str)
            state_map={"development":dev_state,"validation":val.vix_state.astype(str),"holdout":hold.vix_state.astype(str)}
            desc="India VIX level/spike/rising/falling states from Phase45's prior-session-only feature code"
        elif spec[0]=="NUM":
            f=spec[1];em={f:edges_from(dev,f)}
            state_map={s:bins(x,f,em[f]) for s,x in [("development",dev),("validation",val),("holdout",hold)]}
            desc={"feature":f,"development_only_quantile_cutpoints":em[f]}
        else:
            _,f1,f2=spec[1];em={f1:edges_from(dev,f1),f2:edges_from(dev,f2)}
            state_map={s:multi_bins(x,spec[1],em) for s,x in [("development",dev),("validation",val),("holdout",hold)]}
            desc={"features":[f1,f2],"development_only_quantile_cutpoints":em}
        mapping=fit_map(dev,universe,dev_state if spec=="VIX" else state_map["development"],baseline)
        test_sets=[("development_in_sample",dev),("validation",val)]
        if holdout_ready:
            test_sets.append(("holdout",hold))
        for split,test in test_sets:
            a,b,pred,episodes=collapse_predictions(test,state_map["development" if split=="development_in_sample" else ("validation" if split=="validation" else "holdout")],mapping,baseline)
            m=metrics(a,b);m.update({"mode":mode,"selected_feature":label,"split":split,"result_status":"DESCRIPTIVE_OR_VALIDATION_ONLY_NO_PROMOTION","fixed_baseline_strategy":baseline,"routing_rule":desc,
             "strategy_distribution":a.strategy.value_counts().to_dict() if len(a) else {},"n_expiries_available":int(test.expiry_key.nunique())})
            results.append(m)
            if len(a):
                a=a.copy();a["mode"]=mode;a["selected_feature"]=label;a["evaluation_split"]=split;selected_trades.append(a)
        if not holdout_ready:
            results.append({"mode":mode,"selected_feature":label,"split":"holdout","result_status":"HOLDOUT_NOT_EVALUATED_LOW_FEATURE_COVERAGE_OR_SAMPLE",
              "fixed_baseline_strategy":baseline,"n":0,"net":None,"net50":None,"net100":None,"paired_mean_uplift_net50":None,
              "paired_bootstrap_ci95_lo":None,"paired_bootstrap_ci95_hi":None,"paired_signflip_p_one_sided":None,
              "n_expiries_available":int(hold.expiry_key.nunique()),"strategy_distribution":{}})
    rd=pd.DataFrame(results)
    vi=rd.split=="validation"
    rd.loc[vi,"holm_p_uplift_net50"]=holm(rd.loc[vi,"paired_signflip_p_one_sided"].tolist())
    rd.to_csv(outdir/"selector_results.csv",index=False)
    if selected_trades:pd.concat(selected_trades,ignore_index=True).to_csv(outdir/"selected_trade_rows.csv",index=False)
    avail={}
    for group,cols in FACTOR_FEATURES.items():
        avail[group]={"available":[c for c in cols if c in data.columns],"missing":[c for c in cols if c not in data.columns],
          "nonmissing_rate_by_split":{s:{c:float(data.loc[data.split==s,c].notna().mean()) if c in data else None for c in cols} for s in ["development","validation","holdout"]}}
    out={
      "status":"FACTOR_SELECTOR_VALIDATION_ONLY_HOLDOUT_BLOCKED_NO_PROMOTION" if not holdout_ready else "FACTOR_SELECTOR_PILOT_COMPLETE_NO_PROMOTION",
      "input_sha256":{"trade_matrix":hashlib.sha256(Path(trades_path).read_bytes()).hexdigest(),"feature_panel":hashlib.sha256(Path(features_path).read_bytes()).hexdigest()},
      "source_feature_leakage_audit_status":source_audit.get("status"),
      "input_audit":audit,"risk_limited_strategy_universe":universe,"risk_limited_strategy_count":len(universe),
      "split_unique_expiries":{s:int(data.loc[data.split==s,"expiry_key"].nunique()) for s in ["development","validation","holdout"]},
      "holdout_evaluated":bool(holdout_ready),"holdout_coverage_gate":holdout_coverage,
      "development_fit_end":str(fit_end.date()),"development_tune_start":str(tune_start.date()),
      "fixed_baseline_strategy_dev_fit":baseline_fit,"fixed_baseline_strategy_dev_all":baseline,
      "selected_feature_by_mode":features_by_mode,"factor_availability":avail,
      "not_available_in_seed_panel":["NIFTY futures basis/OI/volume","synchronized synthetic-future divergence","NSE/BSE breadth","timestamp-verified intraday news","point-in-time corporate-action feed"],
      "cost_stress_notes":"The +100% cost stress is derived as 2*net50-net because source costs were multiplied linearly; ₹20/order Paytm Money sensitivity is not available from this frozen outcome matrix.",
      "limitations":["This is a factor selector screen on legacy fixed-entry/expiry-exit outcomes, not the full Phase52 config grid.","Only explicitly risk-limited legacy strategy labels are eligible; unknown/undefined-tail templates are excluded.","FII/DII availability was reported missing through development/validation in the previous Phase39 leakage audit; no primary selector claim is made for those features.","The source matrix does not contain futures basis or matched synthetic-future series. SPOT_PROXY_ONLY is not a futures test.","The 2026 holdout is evaluated only if its feature coverage is >=50% and at least 20 expiry sessions; otherwise the pilot does not make a holdout performance claim.","No result implies profitability in all regimes or authorizes live trading."] }
    (outdir/"summary.json").write_text(json.dumps(out,indent=2,default=str,allow_nan=False)+"\n")
    lines=["# Phase 52 — Legacy Factor-Selector Pilot","","Status: exploratory selector screen only; no promotion.",
      "",f"- Legacy trade rows: {audit['trade_rows_input']:,}; matched point-in-time rows: {audit['trade_rows_with_asof_feature_match']:,} ({audit['feature_match_rate']:.1%}).",
      f"- Recognized risk-limited legacy strategies: {len(universe)}.",
      f"- Development fit ends {fit_end.date()}; tuning starts {tune_start.date()}; 2024–25 validation and 2026 holdout were not used to fit the selected feature/mapping.",
      f"- Fixed baseline chosen on development: {baseline}.","","## Results","","| Mode | Chosen feature | Split | N expiries | Net ₹ | Net +50% stress ₹ | Net +100% modelled stress ₹ | Mean uplift vs fixed ₹/expiry | 95% block-bootstrap CI | Raw one-sided p | Holm-adjusted p |",
      "|---|---|---|---:|---:|---:|---:|---:|---|---:|"]
    for _,r in rd.iterrows():
        ci="—" if pd.isna(r.get("paired_bootstrap_ci95_lo")) else f"[{r['paired_bootstrap_ci95_lo']:.0f}, {r['paired_bootstrap_ci95_hi']:.0f}]"
        rawp=r.get("paired_signflip_p_one_sided",np.nan)
        hp=r.get("holm_p_uplift_net50",np.nan)
        lines.append(f"| {r['mode']} | {r['selected_feature']} | {r['split']} | {r.get('n',0)} | {r.get('net',np.nan):.0f} | {r.get('net50',np.nan):.0f} | {r.get('net100',np.nan):.0f} | {r.get('paired_mean_uplift_net50',np.nan):.0f} | {ci} | {rawp:.4f} | {hp:.4f} |")
    lines += ["","## Untested factor blocks","",
      "The audited legacy feature panel lacks synchronized NIFTY futures basis/OI/volume and exact-timestamp synthetic-future data. Those factors are not tested here. News, corporate actions and breadth are likewise unavailable. A daily sentiment feature is only a proxy and is not equivalent to timestamped news.",
      "","This run is a first out-of-sample selection screen over available frozen outcomes. It does not mean all 312 registered hypotheses or all finite parameter combinations have been replayed. No candidate is promoted from this pilot."]
    (outdir/"REPORT.md").write_text("\n".join(lines)+"\n")
    return out

def self_test():
    x=pd.DataFrame({"v":[1.,2.,3.]});e=[1.5,2.5];b=bins(x,"v",e)
    assert [str(v) for v in b]==["LOW","MID","HIGH"], f"unexpected bin labels: {list(b)}"
    x1=pd.DataFrame({"expiry_key":["a","a"],"strategy":["x","y"],"net50":[1.,2.],"net":[1.,2.],"net100":[1.,2.],"expiry_date":pd.to_datetime(["2026-01-01","2026-01-01"])})
    m=metrics(x1.iloc[[1]],x1.iloc[[0]])
    assert m["n"]==1 and m["paired_mean_uplift_net50"]==1.0
    ci,hi,p=paired_test(np.array([1.,2.,1.,2.,1.,2.,1.,2.,1.,2.,1.,2.]))
    assert ci is not None and hi is not None and p is not None
    print("SELF_TEST_PASS: training-only binning, complete risk-limited aliases and block-paired expiry metrics")

def main():
    p=argparse.ArgumentParser();p.add_argument("--trades",type=Path,required=True);p.add_argument("--features",type=Path,required=True);p.add_argument("--leakage-audit",type=Path,required=True);p.add_argument("--out",type=Path,required=True);p.add_argument("--self-test",action="store_true");a=p.parse_args()
    if a.self_test:self_test()
    s=run(a.trades,a.features,a.out,a.leakage_audit)
    print(json.dumps({"status":s["status"],"trade_rows":s["input_audit"]["trade_rows_input"],"feature_match_rate":s["input_audit"]["feature_match_rate"],"risk_limited_strategy_count":s["risk_limited_strategy_count"],"selected_feature_by_mode":s["selected_feature_by_mode"],"results_path":str(a.out)},indent=2,default=str))
if __name__=="__main__": main()
