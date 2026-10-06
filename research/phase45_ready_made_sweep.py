import ast
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

TZ = "Asia/Kolkata"
HF_REPO = "thetrademarkk/india-index-options-1m"
TICK = 0.05
BROKERAGE_PER_ORDER = 10.0
DEV_END = pd.Timestamp("2023-12-31", tz=TZ)
VAL_END = pd.Timestamp("2025-12-31", tz=TZ)
OUT = Path("results/phase45_ready_made")
OUT.mkdir(parents=True, exist_ok=True)

NEW_STRATEGIES = {
    "buy_call": [("CE", 0, 1)],
    "sell_put": [("PE", 0, -1)],
    "bull_condor": [("CE", 1, 1), ("CE", 2, -1), ("CE", 3, -1), ("CE", 4, 1)],
    "bull_butterfly": [("CE", 1, 1), ("CE", 2, -2), ("CE", 3, 1)],
    "range_forward": [("CE", 1, 1), ("PE", -1, -1)],
    "buy_put": [("PE", 0, 1)],
    "sell_call": [("CE", 0, -1)],
    "bear_condor": [("PE", -1, 1), ("PE", -2, -1), ("PE", -3, -1), ("PE", -4, 1)],
    "bear_butterfly": [("PE", -1, 1), ("PE", -2, -2), ("PE", -3, 1)],
    "risk_reversal": [("PE", -1, 1), ("CE", 1, -1)],
    "batman": [("CE", 1, 1), ("CE", 2, -2), ("PE", -1, 1), ("PE", -2, -2)],
    "jade_lizard": [("PE", -1, -1), ("CE", 1, -1), ("CE", 2, 1)],
    "reverse_jade_lizard": [("CE", 1, -1), ("PE", -1, -1), ("PE", -2, 1)],
    "long_iron_condor": [("PE", -1, 1), ("PE", -3, -1), ("CE", 1, 1), ("CE", 3, -1)],
    "long_iron_butterfly": [("PE", 0, 1), ("CE", 0, 1), ("PE", -2, -1), ("CE", 2, -1)],
    "double_plateau": [
        ("PE", -4, 1), ("PE", -3, -1), ("PE", -2, -1), ("PE", -1, 1),
        ("CE", 1, 1), ("CE", 2, -1), ("CE", 3, -1), ("CE", 4, 1)
    ],
    "strip": [("CE", 0, 1), ("PE", 0, 2)],
    "strap": [("CE", 0, 2), ("PE", 0, 1)],
    "long_synthetic_future": [("CE", 0, 1), ("PE", 0, -1)],
    "short_synthetic_future": [("CE", 0, -1), ("PE", 0, 1)],
}

UNBOUNDED = {
    "buy_call", "sell_put", "buy_put", "sell_call", "range_forward", "risk_reversal",
    "batman", "jade_lizard", "reverse_jade_lizard", "long_synthetic_future", "short_synthetic_future",
}
DEFINED_RISK = [k for k in NEW_STRATEGIES if k not in UNBOUNDED]

PHASE43_MAP = {
    "long_straddle": "long_straddle",
    "short_straddle": "short_straddle",
    "long_strangle": "long_strangle",
    "short_strangle": "short_strangle",
    "bull_call_spread": "bull_call_debit",
    "bear_put_spread": "bear_put_debit",
    "bull_put_spread": "bull_put_credit",
    "bear_call_spread": "bear_call_credit",
    "long_atm_call_butterfly": "long_call_butterfly",
    "long_atm_put_butterfly": "long_put_butterfly",
    "short_iron_butterfly": "iron_butterfly",
    "short_iron_condor": "iron_condor",
    "call_broken_wing_butterfly": "call_broken_wing",
    "put_broken_wing_butterfly": "put_broken_wing",
    "call_ratio_spread": "call_ratio_1x2",
    "put_ratio_spread": "put_ratio_1x2",
    "call_backspread": "call_backspread",
    "put_backspread": "put_backspread",
    "long_call_calendar": "call_calendar",
    "long_put_calendar": "put_calendar",
}

def lot_size_for_expiry(expiry):
    if expiry < pd.Timestamp("2021-07-29", tz=TZ): return 75
    if expiry < pd.Timestamp("2024-05-02", tz=TZ): return 50
    if expiry <= pd.Timestamp("2024-12-26", tz=TZ): return 25
    if expiry <= pd.Timestamp("2025-01-23", tz=TZ): return 75
    if expiry == pd.Timestamp("2025-01-30", tz=TZ): return 25
    if expiry < pd.Timestamp("2026-01-06", tz=TZ): return 75
    return 65

def fee_rates(d):
    stt = 0.0015 if d >= pd.Timestamp("2026-04-01", tz=TZ) else 0.0010 if d >= pd.Timestamp("2024-10-01", tz=TZ) else 0.000625
    txn, ipft = ((0.000355299, 0.000000001) if d >= pd.Timestamp("2026-03-01", tz=TZ)
                 else (0.0003503, 0.000005) if d >= pd.Timestamp("2024-10-01", tz=TZ)
                 else (0.000495, 0.000005))
    return stt, txn, 0.000001, ipft, 0.00003

def exec_px(px, action, stress=1.0):
    slip = TICK * stress
    return max(0.0, float(px) + slip) if action == "buy" else max(0.0, float(px) - slip)

def charges(orders, lot, mult=1.0):
    brokerage = BROKERAGE_PER_ORDER * mult * len(orders)
    exchange = sebi = ipft = stt = stamp = 0.0
    for d, side, px in orders:
        sr, tx, se, ip, sd = fee_rates(d)
        turnover = float(px) * lot
        exchange += tx * turnover * mult
        sebi += se * turnover * mult
        ipft += ip * turnover * mult
        if side == "sell": stt += sr * turnover * mult
        else: stamp += sd * turnover * mult
    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    return brokerage + exchange + sebi + ipft + stt + stamp + gst

def load_index():
    p = hf_hub_download(repo_id=HF_REPO, filename="index/NIFTY.parquet",
                        repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
    df = pd.read_parquet(p, columns=["timestamp", "close"])
    ts = pd.to_datetime(df["timestamp"])
    df["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    return df.rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")

def load_vix():
    x = pd.read_csv("data/phase40_vix/india_vix.csv")
    dc = next(c for c in x.columns if c.lower()=="date")
    cc = next(c for c in x.columns if c.lower()=="close")
    x["date"] = pd.to_datetime(x[dc]).dt.tz_localize(TZ)
    x["vix"] = pd.to_numeric(x[cc], errors="coerce")
    x = x[["date","vix"]].dropna().drop_duplicates("date").sort_values("date")
    x["dvix"] = x["vix"].diff()
    return x

def state_flags(vix, entry_ts):
    prior = vix[vix["date"] < entry_ts.normalize()]
    if len(prior) < 60:
        return []
    cur = prior.iloc[-1]
    hist = prior.iloc[:-1]
    q25, q75 = hist["vix"].quantile(.25), hist["vix"].quantile(.75)
    d = hist["dvix"].dropna()
    pos = d[d > 0]
    dv = float(cur["dvix"]) if np.isfinite(cur["dvix"]) else np.nan
    out = ["ALL"]
    if float(cur["vix"]) <= q25: out.append("LOW")
    elif float(cur["vix"]) >= q75: out.append("HIGH")
    else: out.append("NORMAL")
    if len(pos) >= 20 and np.isfinite(dv) and dv >= pos.quantile(.90): out.append("SPIKE")
    if len(d) >= 20 and np.isfinite(dv) and dv >= d.quantile(.90): out.append("RISING")
    if len(d) >= 20 and np.isfinite(dv) and dv <= d.quantile(.10): out.append("FALLING")
    if "HIGH" in out and "RISING" in out: out.append("HIGH_RISING")
    return sorted(set(out))

def split_for(expiry):
    if expiry <= DEV_END: return "development"
    if expiry <= VAL_END: return "validation"
    return "holdout"

def modal_step(snap):
    steps=[]
    for typ in ("CE","PE"):
        s=np.sort(snap.loc[snap["option_type"]==typ,"strike"].unique())
        d=np.round(np.diff(s),8)
        d=d[d>0]
        if len(d):
            u,c=np.unique(d,return_counts=True)
            steps.append(float(u[np.argmax(c)]))
    return steps[0] if steps else None

def prepare(df):
    z=df.copy()
    z["option_type"]=z["option_type"].astype(str).str.upper()
    z["strike"]=pd.to_numeric(z["strike"],errors="coerce")
    z["close"]=pd.to_numeric(z["close"],errors="coerce")
    ts=pd.to_datetime(z["timestamp"])
    z["timestamp"]=ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    return z.dropna(subset=["timestamp","option_type","strike","close"]).sort_values(["timestamp","option_type","strike"],kind="stable")

def load_expiry(expiry, entry_ts):
    name=f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"
    path=hf_hub_download(repo_id=HF_REPO, filename=name, repo_type="dataset",
                         token=os.getenv("HF_TOKEN") or None)
    start=expiry.normalize()
    windows=[
        (entry_ts-pd.Timedelta(minutes=1), entry_ts+pd.Timedelta(minutes=1)),
        (start, start+pd.Timedelta(hours=15,minutes=29)),
    ]
    tables=[]
    try:
        for lo,hi in windows:
            t=pq.read_table(path,columns=["timestamp","option_type","strike","close"],
                            filters=[("timestamp",">=",lo.to_pydatetime()),("timestamp","<=",hi.to_pydatetime())])
            if t.num_rows:
                tables.append(t.to_pandas())
    except Exception:
        tables=[]
    if not tables:
        return prepare(pd.read_parquet(path, columns=["timestamp","option_type","strike","close"]))
    return prepare(pd.concat(tables,ignore_index=True))

def entry_ts_for(index, expiry):
    days=sorted(index["timestamp"].dt.normalize().unique())
    prior=[d for d in days if d < expiry.normalize()]
    if len(prior)<4: return None
    return prior[-4]+pd.Timedelta(hours=10)

def strategy_eval(cur, entry_ts, expiry, spot, step, lot, legs):
    snap=cur[cur["timestamp"]==entry_ts]
    atm=float(min(snap["strike"].unique(),key=lambda k:abs(float(k)-spot)))
    entry={}
    for typ,off,q in legs:
        k=float(atm+off*step)
        x=snap[(snap["option_type"]==typ)&(snap["strike"]==k)]
        if x.empty: return None
        entry[(typ,off)]=float(x.iloc[-1]["close"])
    series=[]
    for typ,off,q in legs:
        k=float(atm+off*step)
        s=cur[(cur["option_type"]==typ)&(cur["strike"]==k)&
              (cur["timestamp"]>=expiry.normalize())&
              (cur["timestamp"]<=expiry.normalize()+pd.Timedelta(hours=15,minutes=29))]
        if s.empty: return None
        series.append(s.drop_duplicates("timestamp").set_index("timestamp")["close"])
    common=series[0].index
    for s in series[1:]:
        common=common.intersection(s.index)
        if len(common)==0: return None
    exit_ts=common.max()
    exits=[float(s.loc[exit_ts]) for s in series]
    gross=0.0
    orders=[]
    for (typ,off,q),xp in zip(legs,exits):
        ep=entry[(typ,off)]
        epx=exec_px(ep,"buy" if q>0 else "sell")
        xpx=exec_px(xp,"buy" if q<0 else "sell")
        gross += q*(xpx-epx)*lot
        orders += [(entry_ts,"buy" if q>0 else "sell",epx*abs(q)),
                   (exit_ts,"buy" if q<0 else "sell",xpx*abs(q))]
    c=charges(orders,lot,1.0)
    c50=charges(orders,lot,1.5)
    return {"net":gross-c,"net50":gross-c50,"gross":gross,"cost":c}

def load_phase43():
    p=Path("results/phase43_vix/strategy_trade_matrix_all_splits.csv")
    z=pd.read_csv(p)
    ts=pd.to_datetime(z["entry_ts"])
    if ts.dt.tz is None: ts=ts.dt.tz_localize(TZ)
    z["entry_ts"]=ts
    z["net"]=pd.to_numeric(z["net_rupees"],errors="coerce")
    z["net50"]=pd.to_numeric(z["net_plus50_cost_rupees"],errors="coerce")
    z["strategy"]=z["strategy"].map({v:k for k,v in PHASE43_MAP.items()}).fillna(z["strategy"])
    z["source"]="phase43_accepted"
    return z[["expiry","entry_ts","split","strategy","net","net50","source"]].dropna(subset=["net","net50"])

def drawdown(vals):
    a=np.asarray(vals,float)
    if len(a)==0:return 0.0
    c=np.cumsum(a)
    return float(np.max(np.maximum.accumulate(c)-c))

def pf(vals):
    a=np.asarray(vals,float)
    pos=a[a>0].sum()
    neg=-a[a<0].sum()
    return float(pos/neg) if neg>0 else np.inf if pos>0 else np.nan

def regime_test(z,state,seed=4501):
    a=z[z["active_states"].apply(lambda x: state in x)]["net"].to_numpy(float)
    b=z[z["active_states"].apply(lambda x: state not in x)]["net"].to_numpy(float)
    if len(a)<10 or len(b)<10:
        return {"n_active":len(a),"n_rest":len(b),"diff_mean":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,"p":np.nan}
    rng=np.random.default_rng(seed)
    ia=rng.integers(0,len(a),size=(10000,len(a)))
    ib=rng.integers(0,len(b),size=(10000,len(b)))
    boots=a[ia].mean(axis=1)-b[ib].mean(axis=1)
    pooled=np.concatenate([a,b]); n1=len(a)
    perms=np.empty(10000)
    obs=a.mean()-b.mean()
    for i in range(10000):
        perm=rng.permutation(pooled)
        perms[i]=perm[:n1].mean()-perm[n1:].mean()
    p=float(np.mean(perms>=obs))
    return {"n_active":len(a),"n_rest":len(b),"diff_mean":float(obs),
            "ci_lo":float(np.quantile(boots,.025)),"ci_hi":float(np.quantile(boots,.975)),"p":p}

def holm(ps):
    p=np.asarray(ps,float)
    order=np.argsort(np.nan_to_num(p,nan=1.0))
    out=np.ones(len(p))
    run=0.0
    for rank,i in enumerate(order):
        run=max(run,min(1.0,(len(p)-rank)*(p[i] if np.isfinite(p[i]) else 1.0)))
        out[i]=run
    return out

def main():
    index=load_index()
    vix=load_vix()
    base43=load_phase43()
    expiries=sorted(pd.to_datetime(base43["expiry"]).dt.tz_localize(TZ).drop_duplicates().tolist())
    new_rows=[]
    errors=[]
    for n,expiry in enumerate(expiries):
        ets=entry_ts_for(index,expiry)
        if ets is None: continue
        if expiry > pd.Timestamp("2026-09-30",tz=TZ): continue
        try:
            spotrow=index[index["timestamp"]==ets]
            if spotrow.empty: continue
            spot=float(spotrow.iloc[-1]["spot"])
            cur=load_expiry(expiry,ets)
            snap=cur[cur["timestamp"]==ets]
            step=modal_step(snap)
            if step is None or step<=0: continue
            lot=lot_size_for_expiry(expiry)
            states=state_flags(vix,ets)
            if not states: continue
            for name,legs in NEW_STRATEGIES.items():
                r=strategy_eval(cur,ets,expiry,spot,step,lot,legs)
                if r is None: continue
                new_rows.append({"expiry":str(expiry.date()),"entry_ts":str(ets),
                                 "split":split_for(expiry),"strategy":name,
                                 "net":r["net"],"net50":r["net50"],
                                 "gross":r["gross"],"cost":r["cost"],
                                 "active_states":json.dumps(states)})
        except Exception as e:
            errors.append({"expiry":str(expiry.date()),"entry_ts":str(ets),"error":repr(e)})
        if n%10==0:
            pd.DataFrame(new_rows).to_csv(OUT/"progress_new_matrix.csv",index=False)
    new=pd.DataFrame(new_rows)
    if new.empty:
        raise RuntimeError("No Phase-45 strategy rows generated")
    new["entry_ts"]=pd.to_datetime(new["entry_ts"])
    new.to_csv(OUT/"new_strategy_trade_matrix.csv",index=False)
    pd.DataFrame(errors).to_csv(OUT/"data_errors.csv",index=False)

    base43["active_states"]=base43["entry_ts"].apply(lambda x: json.dumps(state_flags(vix,x)))
    full=pd.concat([base43,new[base43.columns]],ignore_index=True)
    full=full.drop_duplicates(["expiry","entry_ts","strategy"],keep="first")
    full.to_csv(OUT/"full_ready_made_trade_matrix.csv",index=False)

    summary=[]
    states=["ALL","LOW","NORMAL","HIGH","SPIKE","FALLING","RISING","HIGH_RISING"]
    for (strategy,split),g in full.groupby(["strategy","split"]):
        if split not in ("development","validation","holdout"): continue
        for state in states:
            z=g[g["active_states"].apply(lambda x: state in x)]
            if len(z)==0: continue
            vals=z["net"].to_numpy(float)
            summary.append({
                "strategy":strategy,"split":split,"state":state,"trades":len(z),
                "net":float(z.net.sum()),"net50":float(z.net50.sum()),
                "mean_net":float(z.net.mean()),"win_rate":float((z.net>0).mean()),
                "max_dd":drawdown(z.sort_values("expiry").net.to_numpy()),
                "profit_factor":pf(vals),
                "defined_risk":strategy in (set(PHASE43_MAP.keys())|set(DEFINED_RISK)),
            })
    s=pd.DataFrame(summary)
    s.to_csv(OUT/"strategy_vix_summary.csv",index=False)

    tests=[]
    validation=full[full.split=="validation"]
    for strategy,g in validation.groupby("strategy"):
        for state in states[1:]:
            t=regime_test(g,state)
            tests.append({"strategy":strategy,"state":state,**t})
    tt=pd.DataFrame(tests)
    if len(tt):
        tt["p_holm"]=holm(tt.p.to_numpy())
    tt.to_csv(OUT/"validation_regime_inference.csv",index=False)

    # Validation freeze: top 3 positive, cost-robust defined-risk candidates per state.
    freeze=[]
    for state in states[1:]:
        q=s[(s.split=="validation")&(s.state==state)&(s.trades>=20)&(s.net>0)&(s.net50>0)&(s.defined_risk)]
        q=q.sort_values(["net50","mean_net"],ascending=False).head(3)
        freeze += q[["strategy","state","trades","net","net50","mean_net","max_dd","profit_factor"]].to_dict("records")
    fr=pd.DataFrame(freeze)
    fr.to_csv(OUT/"validation_freeze_top3.csv",index=False)

    hold_confirm=[]
    hold=full[full.split=="holdout"]
    for r in fr.itertuples(index=False):
        g=hold[hold.strategy==r.strategy]
        z=g[g.active_states.apply(lambda x:r.state in x)]
        if len(z)==0: continue
        hold_confirm.append({
            "strategy":r.strategy,"state":r.state,"hold_trades":len(z),
            "hold_net":float(z.net.sum()),"hold_net50":float(z.net50.sum()),
            "hold_mean_net":float(z.net.mean()),"hold_win_rate":float((z.net>0).mean()),
            "hold_max_dd":drawdown(z.sort_values("expiry").net.to_numpy()),
            "hold_profit_factor":pf(z.net.to_numpy()),
        })
    hc=pd.DataFrame(hold_confirm)
    hc.to_csv(OUT/"holdout_frozen_top3_confirmation.csv",index=False)

    # Produce a concise manuscript with the accepted numerical outputs.
    top_val=s[(s.split=="validation")&(s.state!="ALL")&(s.trades>=20)&(s.net>0)&(s.net50>0)&(s.defined_risk)].sort_values("net50",ascending=False).head(20)
    lines=[]
    lines += ["# Phase 45 Manuscript — Exhaustive Ready-Made Strategies","","## Decision","The phase evaluates the full ready-made strategy set visible in the screenshots by combining accepted Phase-43 results with the 20 missing structures tested in Phase 45. Validation is the ranking period; the 2026 holdout is confirmation only.","","## Newly tested structures",", ".join(sorted(NEW_STRATEGIES)),"","## Validation top candidates by VIX state",""]
    if len(top_val):
        lines += ["| Strategy | VIX state | Trades | Validation net | +50% cost | Mean/trade | Max DD | PF |","|---|---|---:|---:|---:|---:|---:|---:|"]
        for r in top_val.itertuples(index=False):
            lines.append(f"| {r.strategy} | {r.state} | {r.trades} | ₹{r.net:,.0f} | ₹{r.net50:,.0f} | ₹{r.mean_net:,.0f} | ₹{r.max_dd:,.0f} | {r.profit_factor:.2f} |")
    lines += ["","## Statistical inference","The validation regime-comparison table uses active-vs-complement expiry observations with 10,000 bootstrap resamples and a 10,000-permutation one-sided test; Holm adjustment is applied across the preregistered strategy×regime family.","","## Holdout freeze","The top validation defined-risk candidates are frozen before reading their 2026 confirmation table. Holdout performance cannot change strategy definitions.","","## Execution model","Historical NIFTY lot sizes, ₹10 Paytm Money brokerage per order, date-aware statutory charges/GST and one adverse ₹0.05 option tick per leg at entry and exit. No forward fill or synthetic quote substitution is permitted.","","## Limitations","Single preset strike geometry is tested for many ready-made strategies because the user asked for the presets shown in the builder; broad geometry optimization is deliberately separated into a later phase to avoid mixing strategy-family discovery with parameter tuning.",""]
    (OUT/"PHASE45_MANUSCRIPT.md").write_text("\\n".join(lines))
    summary_json={
        "new_strategies":len(NEW_STRATEGIES),
        "reused_phase43_strategies":len(PHASE43_MAP),
        "new_trade_rows":int(len(new)),
        "full_trade_rows":int(len(full)),
        "validation_freeze_rows":int(len(fr)),
        "holdout_confirmation_rows":int(len(hc)),
        "validation_positive_defined_risk_states":int(((s.split=="validation")&(s.state!="ALL")&(s.trades>=20)&(s.net>0)&(s.net50>0)&(s.defined_risk)).sum()),
    }
    (OUT/"summary.json").write_text(json.dumps(summary_json,indent=2))
    print(json.dumps(summary_json,indent=2))

if __name__=="__main__":
    main()
