import json
import os
import re
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

TZ = "Asia/Kolkata"
HF_REPO = "thetrademarkk/india-index-options-1m"
START = pd.Timestamp("2021-05-27", tz=TZ)
END = pd.Timestamp("2026-09-30", tz=TZ)
DEV_END = pd.Timestamp("2023-12-31", tz=TZ)
VAL_END = pd.Timestamp("2025-12-31", tz=TZ)

TICK = 0.05
BROKERAGE_PER_ORDER = 10.0
OUT = Path("results/phase44_vix_tuning")
OUT.mkdir(parents=True, exist_ok=True)

# Phase-44 registered candidate families only.
FAMILIES = {
    "bear_call_credit": [("CE", "short", 1), ("CE", "long", 3)],
    "bear_put_debit": [("PE", "long", 0), ("PE", "short", -1)],
    "put_backspread": [("PE", "short", 0), ("PE", "long2", -1)],
    "put_broken_wing": [("PE", "long", 2), ("PE", "short2", 0), ("PE", "long", -1)],
    "iron_butterfly": [("CE", "short", 0), ("PE", "short", 0), ("CE", "long", 2), ("PE", "long", -2)],
    "call_backspread": [("CE", "short", 0), ("CE", "long2", 1)],
}

def lot_size_for_expiry(expiry):
    if expiry < pd.Timestamp("2021-07-29", tz=TZ):
        return 75
    if expiry < pd.Timestamp("2024-05-02", tz=TZ):
        return 50
    if expiry <= pd.Timestamp("2024-12-26", tz=TZ):
        return 25
    if expiry <= pd.Timestamp("2025-01-23", tz=TZ):
        return 75
    if expiry == pd.Timestamp("2025-01-30", tz=TZ):
        return 25
    if expiry < pd.Timestamp("2026-01-06", tz=TZ):
        return 75
    return 65

def fee_rates(d):
    if d >= pd.Timestamp("2026-04-01", tz=TZ):
        stt = 0.0015
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        stt = 0.0010
    else:
        stt = 0.000625
    if d >= pd.Timestamp("2026-03-01", tz=TZ):
        txn, ipft = 0.000355299, 0.000000001
    elif d >= pd.Timestamp("2024-10-01", tz=TZ):
        txn, ipft = 0.0003503, 0.000005
    else:
        txn, ipft = 0.000495, 0.000005
    return stt, txn, 0.000001, ipft, 0.00003

def exec_px(px, action, stress=1.0):
    slip = TICK * stress
    return max(0.0, float(px) + slip) if action == "buy" else max(0.0, float(px) - slip)

def charges(orders, lot_size, cost_mult=1.0):
    brokerage = BROKERAGE_PER_ORDER * cost_mult * len(orders)
    exchange = sebi = ipft = stt = stamp = 0.0
    for d, side, px in orders:
        sr, tx, se, ip, sd = fee_rates(d)
        turnover = float(px) * lot_size
        exchange += tx * turnover * cost_mult
        sebi += se * turnover * cost_mult
        ipft += ip * turnover * cost_mult
        if side == "sell":
            stt += sr * turnover * cost_mult
        else:
            stamp += sd * turnover * cost_mult
    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    return brokerage + exchange + sebi + ipft + stt + stamp + gst

def load_parquet(name):
    p = hf_hub_download(repo_id=HF_REPO, filename=name, repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
    df = pd.read_parquet(p)
    ts = pd.to_datetime(df["timestamp"])
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize(TZ)
    else:
        ts = ts.dt.tz_convert(TZ)
    df["timestamp"] = ts
    return df

def load_index():
    x = load_parquet("index/NIFTY.parquet")
    return x[["timestamp","close"]].rename(columns={"close":"spot"}).drop_duplicates("timestamp").sort_values("timestamp")

def load_vix():
    p = Path("data/phase40_vix/india_vix.csv")
    x = pd.read_csv(p)
    dc = next(c for c in x.columns if c.lower()=="date")
    cc = next(c for c in x.columns if c.lower()=="close")
    x["date"] = pd.to_datetime(x[dc]).dt.tz_localize(TZ)
    x["vix"] = pd.to_numeric(x[cc], errors="coerce")
    x = x[["date","vix"]].dropna().drop_duplicates("date").sort_values("date")
    x["dvix"] = x["vix"].diff()
    return x

def list_expiries():
    api = HfApi()
    out=[]
    for f in api.list_repo_files(HF_REPO, repo_type="dataset"):
        m=re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet", f)
        if m:
            d=pd.Timestamp(m.group(1),tz=TZ)
            if START <= d <= END:
                out.append(d)
    return sorted(set(out))

def modal_step(snap):
    vals=[]
    for typ in ["CE","PE"]:
        s=np.sort(pd.to_numeric(snap.loc[snap["option_type"].astype(str).str.upper()==typ,"strike"],errors="coerce").dropna().unique())
        d=np.round(np.diff(s),8)
        d=d[d>0]
        if len(d):
            u,c=np.unique(d,return_counts=True)
            vals.append(float(u[np.argmax(c)]))
    return vals[0] if vals else None

def prepare(df):
    z=df.copy()
    z["option_type"]=z["option_type"].astype(str).str.upper()
    z["strike"]=pd.to_numeric(z["strike"],errors="coerce")
    z["close"]=pd.to_numeric(z["close"],errors="coerce")
    return z.dropna(subset=["timestamp","option_type","strike","close"]).sort_values(["timestamp","option_type","strike"])

def entry_day_ts(index, expiry, time):
    days=sorted(index["timestamp"].dt.normalize().unique())
    prior=[d for d in days if d < expiry.normalize()]
    if len(prior)<4:
        return None
    return prior[-4] + pd.Timedelta(hours=time//100, minutes=time%100)

def vix_thresholds(vix, entry_day, ql, qh, qr, qf, qs):
    prior=vix[vix["date"] < entry_day.normalize()]
    if len(prior)<60: return None
    cur=prior.iloc[-1]
    hist=prior.iloc[:-1]
    out={}
    out["vix"]=float(cur["vix"])
    out["dvix"]=float(cur["dvix"]) if np.isfinite(cur["dvix"]) else np.nan
    out["qL"]=float(hist["vix"].quantile(ql))
    out["qH"]=float(hist["vix"].quantile(qh))
    d=hist["dvix"].dropna()
    out["qR"]=float(d.quantile(qr)) if len(d)>=20 else np.nan
    out["qF"]=float(d.quantile(qf)) if len(d)>=20 else np.nan
    pos=d[d>0]
    out["qS"]=float(pos.quantile(qs)) if len(pos)>=20 else np.nan
    return out

def state_matches(st, mode):
    if st is None: return False
    if mode=="LOW": return st["vix"]<=st["qL"]
    if mode=="NORMAL": return st["qL"]<st["vix"]<st["qH"]
    if mode=="HIGH": return st["vix"]>=st["qH"]
    if mode=="RISING": return np.isfinite(st["dvix"]) and np.isfinite(st["qR"]) and st["dvix"]>=st["qR"]
    if mode=="FALLING": return np.isfinite(st["dvix"]) and np.isfinite(st["qF"]) and st["dvix"]<=st["qF"]
    if mode=="SPIKE": return np.isfinite(st["dvix"]) and np.isfinite(st["qS"]) and st["dvix"]>=st["qS"]
    if mode=="HIGH_RISING": return st["vix"]>=st["qH"] and np.isfinite(st["dvix"]) and np.isfinite(st["qR"]) and st["dvix"]>=st["qR"]
    return False

def specs():
    out=[]
    for w in [2,3,4,5]:
        out.append({"family":"bear_call_credit","geom":{"w":w}})
    for w in [1,2,3,4]:
        out.append({"family":"bear_put_debit","geom":{"w":w}})
    for w in [1,2,3]:
        out.append({"family":"put_backspread","geom":{"w":w}})
        out.append({"family":"call_backspread","geom":{"w":w}})
    for a,b in product([1,2,3],[1,2,3]):
        if a!=b:
            out.append({"family":"put_broken_wing","geom":{"a":a,"b":b}})
    for w in [1,2,3,4,5]:
        out.append({"family":"iron_butterfly","geom":{"w":w}})
    return out

def make_legs(family,g):
    if family=="bear_call_credit":
        return [("CE",1,-1),("CE",g["w"],+1)]
    if family=="bear_put_debit":
        return [("PE",0,+1),("PE",-g["w"],-1)]
    if family=="put_backspread":
        return [("PE",0,-1),("PE",-g["w"],+2)]
    if family=="call_backspread":
        return [("CE",0,-1),("CE",g["w"],+2)]
    if family=="put_broken_wing":
        return [("PE",g["a"],+1),("PE",0,-2),("PE",-g["b"],+1)]
    if family=="iron_butterfly":
        w=g["w"]
        return [("CE",0,-1),("PE",0,-1),("CE",w,+1),("PE",-w,+1)]
    raise KeyError(family)

def eval_trade(cur, entry_ts, expiry, atm, step, lot, family, g):
    legs=make_legs(family,g)
    entry=[]
    series=[]
    for typ,off,q in legs:
        k=float(atm+off*step)
        x=cur[(cur["timestamp"]==entry_ts)&(cur["option_type"]==typ)&(cur["strike"]==k)]
        if x.empty: return None
        entry.append(float(x.iloc[-1]["close"]))
        s=cur[(cur["option_type"]==typ)&(cur["strike"]==k)&(cur["timestamp"]>=expiry.normalize())&(cur["timestamp"]<=expiry.normalize()+pd.Timedelta(hours=15,minutes=29))]
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
    for (typ,off,q),ep,xp in zip(legs,entry,exits):
        epx=exec_px(ep,"buy" if q>0 else "sell")
        xpx=exec_px(xp,"buy" if q<0 else "sell")
        gross += q*(xpx-epx)*lot
        orders.append((entry_ts,"buy" if q>0 else "sell",epx*abs(q)))
        orders.append((exit_ts,"buy" if q<0 else "sell",xpx*abs(q)))
    cost=charges(orders,lot,1.0)
    cost50=charges(orders,lot,1.5)
    return {"net":gross-cost,"net50":gross-cost50,"gross":gross,"cost":cost,"entry":entry,"series":series,"legs":legs,"exit_ts":exit_ts}

def dd(x):
    if len(x)==0:return 0.0
    c=np.cumsum(np.asarray(x,float))
    return float(np.max(np.maximum.accumulate(c)-c))

def paired_stats(x):
    a=np.asarray(x,float)
    a=a[np.isfinite(a)]
    if len(a)<10:
        return {"n":len(a),"mean":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,"p":np.nan}
    rng=np.random.default_rng(4401)
    signs=rng.choice([-1.,1.],size=(10000,len(a)))
    vals=(a*signs).mean(axis=1)
    boots=a[rng.integers(0,len(a),size=(10000,len(a)))].mean(axis=1)
    obs=a.mean()
    return {"n":len(a),"mean":float(obs),"ci_lo":float(np.quantile(boots,.025)),"ci_hi":float(np.quantile(boots,.975)),"p":float(np.mean(vals>=obs))}

def holm(ps):
    p=np.asarray(ps,float)
    if len(p)==0:return []
    order=np.argsort(np.nan_to_num(p,nan=1.0))
    out=np.empty(len(p),float); run=0.
    m=len(p)
    for rank,i in enumerate(order):
        run=max(run,min(1.,(m-rank)*(p[i] if np.isfinite(p[i]) else 1.)))
        out[i]=run
    return out.tolist()

def main():
    if not Path("data/phase40_vix/india_vix.csv").exists():
        raise FileNotFoundError("missing VIX cache")
    idx=load_index()
    vix=load_vix()
    expiries=list_expiries()
    cache={}
    states_cache={}
    specs0=specs()
    rows=[]
    errors=[]

    # Build opportunities once.
    ops=[]
    for expiry in expiries:
        for tm in [930,1000,1030,1100]:
            ets=entry_day_ts(idx,expiry,tm)
            if ets is None: continue
            z=idx[idx["timestamp"]==ets]
            if z.empty: continue
            ops.append((expiry,tm,ets,float(z.iloc[-1]["spot"])))

    for oi,(expiry,tm,ets,spot) in enumerate(ops):
        try:
            if expiry not in cache:
                cache[expiry]=prepare(load_parquet(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet"))
            cur=cache[expiry]
            snap=cur[cur["timestamp"]==ets]
            step=modal_step(snap)
            if step is None or step<=0:
                errors.append({"expiry":str(expiry.date()),"time":tm,"reason":"missing_step"})
                continue
            strikes=snap["strike"].unique()
            atm=float(min(strikes,key=lambda k:abs(float(k)-spot)))
            lot=lot_size_for_expiry(expiry)
            split="development" if expiry<=DEV_END else "validation" if expiry<=VAL_END else "holdout"
            skey=(str(expiry.date()),tm)
            states_cache[skey]=vix_thresholds(vix,ets,0.25,0.75,0.90,0.10,0.90)
            st=states_cache[skey]

            for sp in specs0:
                r=eval_trade(cur,ets,expiry,atm,step,lot,sp["family"],sp["geom"])
                if r is None: continue
                rows.append({
                    "expiry":str(expiry.date()),"entry_time":tm,"entry_ts":str(ets),"split":split,
                    "family":sp["family"],"geom":json.dumps(sp["geom"],sort_keys=True),
                    "vix":st["vix"] if st else np.nan,"dvix":st["dvix"] if st else np.nan,
                    "net":r["net"],"net50":r["net50"]
                })
        except Exception as e:
            errors.append({"expiry":str(expiry.date()),"time":tm,"reason":repr(e)})
        if oi%40==0:
            pd.DataFrame(rows).to_csv(OUT/"progress_stage1.csv",index=False)

    trades=pd.DataFrame(rows)
    if trades.empty: raise RuntimeError("no tuning rows produced")
    trades.to_csv(OUT/"stage1_structure_time_matrix.csv",index=False)
    pd.DataFrame(errors).to_csv(OUT/"data_errors.csv",index=False)

    # Add VIX state columns for every threshold candidate using only entry-date history.
    threshold_grid=[]
    for ql in [.15,.20,.25,.30]:
        for qh in [.70,.75,.80,.85]:
            if qh>ql: threshold_grid.append((ql,qh,.90,.10,.90))
    rows2=[]
    for r in trades.itertuples(index=False):
        ets=pd.Timestamp(r.entry_ts)
        # entry_ts is localized; threshold calculations re-use only prior dates.
        st=vix_thresholds(vix,ets,*threshold_grid[0]) if False else None
        base=vix[vix["date"]<ets.normalize()]
        cur=base.iloc[-1]
        hist=base.iloc[:-1]
        d=hist["dvix"].dropna()
        for qi,(ql,qh,qr,qf,qs) in enumerate(threshold_grid):
            row=r._asdict()
            row["threshold_id"]=f"L{ql:.2f}_H{qh:.2f}_R{qr:.2f}_F{qf:.2f}_S{qs:.2f}"
            row["LOW"]=bool(cur["vix"]<=hist["vix"].quantile(ql))
            row["NORMAL"]=bool(hist["vix"].quantile(ql)<cur["vix"]<hist["vix"].quantile(qh))
            row["HIGH"]=bool(cur["vix"]>=hist["vix"].quantile(qh))
            row["RISING"]=bool(np.isfinite(cur["dvix"]) and cur["dvix"]>=d.quantile(qr))
            row["FALLING"]=bool(np.isfinite(cur["dvix"]) and cur["dvix"]<=d.quantile(qf))
            pos=d[d>0]
            row["SPIKE"]=bool(np.isfinite(cur["dvix"]) and len(pos)>=20 and cur["dvix"]>=pos.quantile(qs))
            row["HIGH_RISING"]=row["HIGH"] and row["RISING"]
            rows2.append(row)
    x=pd.DataFrame(rows2)
    # Development screen over finite candidate variants.
    dev=x[x["split"]=="development"]
    val=x[x["split"]=="validation"]
    hold=x[x["split"]=="holdout"]
    candidates=[]
    modes=["LOW","NORMAL","HIGH","SPIKE","FALLING","RISING","HIGH_RISING"]
    for (family,geom,tm,tid),g in dev.groupby(["family","geom","entry_time","threshold_id"]):
        # Same variant without VIX filter
        key=(family,geom,tm)
        base_dev=dev[(dev["family"]==family)&(dev["geom"]==geom)&(dev["entry_time"]==tm)]
        base_val=val[(val["family"]==family)&(val["geom"]==geom)&(val["entry_time"]==tm)]
        if len(g)<15 or len(base_dev)<15: continue
        for mode in modes:
            gz=g[g[mode]]
            if len(gz)<10: continue
            for side,name in [(base_val,"ALL")]:
                pass
            vmask=(val["family"]==family)&(val["geom"]==geom)&(val["entry_time"]==tm)&(val["threshold_id"]==tid)
            # Need the mode values for this threshold.
            vv=x[(x["split"]=="validation")&(x["family"]==family)&(x["geom"]==geom)&(x["entry_time"]==tm)&(x["threshold_id"]==tid)]
            vv=vv[vv[mode]]
            if len(vv)<20: continue
            common=base_val[["expiry","net"]].merge(vv[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
            st=paired_stats(common["net_cand"]-common["net_base"]) if len(common)>=10 else {"n":len(common),"mean":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,"p":np.nan}
            candidates.append({
                "family":family,"geom":geom,"entry_time":tm,"threshold_id":tid,"mode":mode,
                "dev_n":len(gz),"dev_net":float(gz["net"].sum()),"dev_mean":float(gz["net"].mean()),
                "val_n":len(vv),"val_net":float(vv["net"].sum()),"val_mean":float(vv["net"].mean()),
                "val_cost50":float(vv["net50"].sum()),
                "val_dd":dd(vv.sort_values("expiry")["net"].to_numpy()),
                "base_val_net":float(base_val["net"].sum()),
                "uplift":float(common["net_cand"].sum()-common["net_base"].sum()) if len(common) else np.nan,
                "uplift_mean":st["mean"],"uplift_ci_lo":st["ci_lo"],"uplift_ci_hi":st["ci_hi"],"uplift_p":st["p"],
                "common_n":len(common)
            })
    cg=pd.DataFrame(candidates)
    if cg.empty: raise RuntimeError("no candidate rows")
    cg["selected_dev"]=(cg["dev_net"]>=0)&(cg["val_net"]>0)&(cg["val_cost50"]>0)&(cg["val_n"]>=20)&(cg["uplift"]>0)&(cg["uplift_ci_lo"]>0)
    cg=cg.sort_values(["selected_dev","uplift_mean","val_net"],ascending=[False,False,False])
    cg.to_csv(OUT/"stage1_candidates.csv",index=False)

    # Freeze top 15 validation-eligible candidates before holdout.
    frozen=cg[cg["selected_dev"]].head(15).copy()
    frozen.to_csv(OUT/"frozen_stage1.csv",index=False)

    # Holm correction within the frozen candidate family (if present).
    if len(frozen):
        ps=holm(frozen["uplift_p"].fillna(1).to_numpy())
        frozen["uplift_p_holm"]=ps
        frozen["final_stage1_eligible"]=frozen["uplift_p_holm"]<0.05
    frozen.to_csv(OUT/"frozen_stage1.csv",index=False)

    # Holdout is now opened only for the frozen stage-1 rows.
    hold_rows=[]
    for fr in frozen.itertuples(index=False):
        hz=hold[(hold["family"]==fr.family)&(hold["geom"]==fr.geom)&(hold["entry_time"]==fr.entry_time)&(hold["threshold_id"]==fr.threshold_id)]
        hz=hz[hz[fr.mode]]
        base=hold[(hold["family"]==fr.family)&(hold["geom"]==fr.geom)&(hold["entry_time"]==fr.entry_time)]
        common=base[["expiry","net"]].merge(hz[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
        hold_rows.append({
            "family":fr.family,"geom":fr.geom,"entry_time":fr.entry_time,"threshold_id":fr.threshold_id,"mode":fr.mode,
            "hold_n":len(hz),"hold_net":float(hz["net"].sum()) if len(hz) else np.nan,
            "hold_net50":float(hz["net50"].sum()) if len(hz) else np.nan,
            "hold_dd":dd(hz.sort_values("expiry")["net"].to_numpy()) if len(hz) else np.nan,
            "hold_uplift":float(common["net_cand"].sum()-common["net_base"].sum()) if len(common) else np.nan
        })
    pd.DataFrame(hold_rows).to_csv(OUT/"frozen_stage1_holdout.csv",index=False)

    # Summary.
    decision="NO_PROMOTION"
    if len(frozen) and frozen["final_stage1_eligible"].any():
        decision="STAGE1_CANDIDATES_EXIST"
    summary={
        "status":"COMPLETE_TUNING_STAGE1",
        "families":6,
        "stage1_rows":int(len(trades)),
        "candidate_rows":int(len(cg)),
        "frozen_candidates":int(len(frozen)),
        "holm_survivors":int(frozen["final_stage1_eligible"].sum()) if len(frozen) else 0,
        "holdout_opened_after_freeze":bool(len(frozen)),
        "decision":decision
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
