import json
import os
import re
from itertools import product
from pathlib import Path

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

ENTRY_TIMES = [930, 1000, 1030, 1100]
FAMILIES = ["bear_call_credit","bear_put_debit","put_backspread","put_broken_wing","iron_butterfly","call_backspread"]

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

def load_parquet(name):
    p = hf_hub_download(repo_id=HF_REPO, filename=name, repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
    df = pd.read_parquet(p)
    ts = pd.to_datetime(df["timestamp"])
    df["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
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
    return x[["date","vix"]].dropna().drop_duplicates("date").sort_values("date").assign(dvix=lambda z: z["vix"].diff())

def list_expiries():
    api = HfApi()
    out = []
    for f in api.list_repo_files(HF_REPO, repo_type="dataset"):
        m = re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet", f)
        if m:
            d = pd.Timestamp(m.group(1), tz=TZ)
            if START <= d <= END: out.append(d)
    return sorted(set(out))

def prepare(df):
    z = df.copy()
    z["option_type"] = z["option_type"].astype(str).str.upper()
    z["strike"] = pd.to_numeric(z["strike"], errors="coerce")
    z["close"] = pd.to_numeric(z["close"], errors="coerce")
    return z.dropna(subset=["timestamp","option_type","strike","close"]).sort_values(["timestamp","option_type","strike"], kind="stable")

def modal_step(snap):
    steps = []
    for typ in ["CE","PE"]:
        s = np.sort(snap.loc[snap["option_type"]==typ, "strike"].unique())
        d = np.round(np.diff(s), 8)
        d = d[d>0]
        if len(d):
            u,c = np.unique(d, return_counts=True)
            steps.append(float(u[np.argmax(c)]))
    return steps[0] if steps else None

def entry_ts_for(index, expiry, hhmm):
    days = sorted(index["timestamp"].dt.normalize().unique())
    prior = [d for d in days if d < expiry.normalize()]
    if len(prior) < 4: return None
    return prior[-4] + pd.Timedelta(hours=hhmm//100, minutes=hhmm%100)

def family_specs():
    out=[]
    for w in [2,3,4,5]: out.append(("bear_call_credit", {"w":w}))
    for w in [1,2,3,4]: out.append(("bear_put_debit", {"w":w}))
    for w in [1,2,3]: 
        out.append(("put_backspread", {"w":w}))
        out.append(("call_backspread", {"w":w}))
    for a,b in product([1,2,3],[1,2,3]):
        if a != b: out.append(("put_broken_wing", {"a":a,"b":b}))
    for w in [1,2,3,4,5]: out.append(("iron_butterfly", {"w":w}))
    return out

def make_legs(family,g):
    if family=="bear_call_credit": return [("CE",1,-1),("CE",g["w"],+1)]
    if family=="bear_put_debit": return [("PE",0,+1),("PE",-g["w"],-1)]
    if family=="put_backspread": return [("PE",0,-1),("PE",-g["w"],+2)]
    if family=="call_backspread": return [("CE",0,-1),("CE",g["w"],+2)]
    if family=="put_broken_wing": return [("PE",g["a"],+1),("PE",0,-2),("PE",-g["b"],+1)]
    if family=="iron_butterfly":
        w=g["w"]
        return [("CE",0,-1),("PE",0,-1),("CE",w,+1),("PE",-w,+1)]
    raise KeyError(family)

def split_for(expiry):
    return "development" if expiry <= DEV_END else "validation" if expiry <= VAL_END else "holdout"

def evaluate(cur, entry_ts, expiry, atm, step, lot, family, geom):
    legs = make_legs(family, geom)
    entry=[]; series=[]
    cutoff = expiry.normalize() + pd.Timedelta(hours=15, minutes=29)
    for typ, off, q in legs:
        k = float(atm + off*step)
        x = cur[(cur["timestamp"]==entry_ts)&(cur["option_type"]==typ)&(cur["strike"]==k)]
        if x.empty: return None
        entry.append(float(x.iloc[-1]["close"]))
        s = cur[(cur["option_type"]==typ)&(cur["strike"]==k)&(cur["timestamp"]>=expiry.normalize())&(cur["timestamp"]<=cutoff)]
        if s.empty: return None
        series.append(s.drop_duplicates("timestamp").set_index("timestamp")["close"])
    common = series[0].index
    for s in series[1:]: common = common.intersection(s.index)
    if len(common)==0: return None
    exit_ts = common.max()
    exits = [float(s.loc[exit_ts]) for s in series]
    gross=0.0; orders=[]
    for (typ,off,q), ep, xp in zip(legs,entry,exits):
        epx = exec_px(ep,"buy" if q>0 else "sell")
        xpx = exec_px(xp,"buy" if q<0 else "sell")
        gross += q*(xpx-epx)*lot
        orders += [(entry_ts,"buy" if q>0 else "sell",epx*abs(q)),
                   (exit_ts,"buy" if q<0 else "sell",xpx*abs(q))]
    c=charges(orders,lot,1.0); c50=charges(orders,lot,1.5)
    return {"net":gross-c,"net50":gross-c50}

def max_dd(x):
    if len(x)==0: return 0.0
    c=np.cumsum(np.asarray(x,float))
    return float(np.max(np.maximum.accumulate(c)-c))

def paired_stats(diff, seed=4402):
    a=np.asarray(diff,float); a=a[np.isfinite(a)]
    if len(a)<10: return {"n":len(a),"mean":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,"p":np.nan}
    rng=np.random.default_rng(seed)
    boot=a[rng.integers(0,len(a),size=(10000,len(a)))].mean(axis=1)
    signs=rng.choice([-1.,1.],size=(10000,len(a)))
    obs=float(a.mean())
    return {"n":len(a),"mean":obs,"ci_lo":float(np.quantile(boot,.025)),"ci_hi":float(np.quantile(boot,.975)),
            "p":float(np.mean((a*signs).mean(axis=1)>=obs))}

def holm(ps):
    p=np.asarray(ps,float); out=np.ones(len(p),float); order=np.argsort(np.nan_to_num(p,nan=1.0)); run=0.; m=len(p)
    for rank,i in enumerate(order):
        run=max(run,min(1.,(m-rank)*(p[i] if np.isfinite(p[i]) else 1.)))
        out[i]=run
    return out

def build_profiles():
    profiles=[]
    for ql in [.15,.20,.25,.30]:
        for qh in [.70,.75,.80,.85]:
            profiles.append((f"L{ql:.2f}_H{qh:.2f}", {"ql":ql,"qh":qh}))
    for qr in [.80,.85,.90,.95]:
        profiles.append((f"R{qr:.2f}", {"qr":qr}))
    for qf in [.05,.10,.15,.20]:
        profiles.append((f"F{qf:.2f}", {"qf":qf}))
    for qs in [.80,.85,.90,.95]:
        profiles.append((f"S{qs:.2f}", {"qs":qs}))
    for ql in [.15,.20,.25,.30]:
        for qh in [.70,.75,.80,.85]:
            for qr in [.80,.85,.90,.95]:
                profiles.append((f"L{ql:.2f}_H{qh:.2f}_R{qr:.2f}", {"ql":ql,"qh":qh,"qr":qr}))
    return profiles

def profile_active(vix, entry_ts, params, mode):
    prior=vix[vix["date"]<entry_ts.normalize()]
    if len(prior)<60: return False
    cur=prior.iloc[-1]; hist=prior.iloc[:-1]
    vl=float(cur["vix"]); dv=float(cur["dvix"]) if np.isfinite(cur["dvix"]) else np.nan
    if mode in ("LOW","NORMAL","HIGH","HIGH_RISING"):
        ql=hist["vix"].quantile(params["ql"]); qh=hist["vix"].quantile(params["qh"])
        level = mode=="LOW" and vl<=ql or mode=="NORMAL" and ql<vl<qh or mode=="HIGH" and vl>=qh
        if mode=="HIGH_RISING":
            d=hist["dvix"].dropna()
            return vl>=qh and np.isfinite(dv) and len(d)>=20 and dv>=d.quantile(params["qr"])
        return bool(level)
    d=hist["dvix"].dropna()
    if mode=="RISING": return np.isfinite(dv) and len(d)>=20 and dv>=d.quantile(params["qr"])
    if mode=="FALLING": return np.isfinite(dv) and len(d)>=20 and dv<=d.quantile(params["qf"])
    if mode=="SPIKE":
        pos=d[d>0]
        return np.isfinite(dv) and len(pos)>=20 and dv>=pos.quantile(params["qs"])
    return False

def profile_defs():
    p=build_profiles()
    out=[]
    for pid,par in p:
        if "ql" in par and "qr" in par:
            out.append((pid,"HIGH_RISING",par))
        elif "ql" in par:
            out += [(pid,"LOW",par),(pid,"NORMAL",par),(pid,"HIGH",par)]
        elif "qr" in par:
            out.append((pid,"RISING",par))
        elif "qf" in par:
            out.append((pid,"FALLING",par))
        elif "qs" in par:
            out.append((pid,"SPIKE",par))
    return list(dict((f"{pid}|{mode}",(pid,mode,par)) for pid,mode,par in out).values())

def main():
    if not Path("data/phase40_vix/india_vix.csv").exists(): raise FileNotFoundError("missing India VIX cache")
    idx=load_index(); vix=load_vix(); expiries=list_expiries(); cache={}
    base_rows=[]; errors=[]; specs=family_specs()
    ops=[]
    for ex in expiries:
        for tm in ENTRY_TIMES:
            ets=entry_ts_for(idx,ex,tm)
            if ets is None: continue
            z=idx[idx["timestamp"]==ets]
            if not z.empty: ops.append((ex,tm,ets,float(z.iloc[-1]["spot"])))
    for oi,(ex,tm,ets,spot) in enumerate(ops):
        try:
            if ex not in cache: cache[ex]=prepare(load_parquet(f"options/NIFTY/{ex.strftime('%Y-%m-%d')}.parquet"))
            cur=cache[ex]; snap=cur[cur["timestamp"]==ets]; step=modal_step(snap)
            if step is None or step<=0:
                errors.append({"expiry":str(ex.date()),"entry_time":tm,"reason":"missing_modal_step"}); continue
            strikes=snap["strike"].unique(); atm=float(min(strikes,key=lambda k:abs(float(k)-spot))); lot=lot_size_for_expiry(ex); split=split_for(ex)
            for family,geom in specs:
                r=evaluate(cur,ets,ex,atm,step,lot,family,geom)
                if r is not None:
                    base_rows.append({"expiry":str(ex.date()),"entry_time":tm,"entry_ts":str(ets),"split":split,
                                      "family":family,"geom":json.dumps(geom,sort_keys=True,separators=(",",":")),
                                      "net":r["net"],"net50":r["net50"]})
        except Exception as e:
            errors.append({"expiry":str(ex.date()),"entry_time":tm,"reason":repr(e)})
        if oi%40==0: pd.DataFrame(base_rows).to_csv(OUT/"progress_structure_matrix.csv",index=False)
    base=pd.DataFrame(base_rows)
    if base.empty: raise RuntimeError("no structure/time rows")
    base.to_csv(OUT/"stage1_structure_time_matrix.csv",index=False); pd.DataFrame(errors).to_csv(OUT/"data_errors.csv",index=False)

    defs=profile_defs(); dev=base[base.split=="development"]; val=base[base.split=="validation"]; hold=base[base.split=="holdout"]
    # Candidate search is strictly development-only. Validation is not used to rank or freeze.
    dev_candidates=[]
    for pid,mode,par in defs:
        for (family,geom,tm),g in dev.groupby(["family","geom","entry_time"]):
            if len(g)<15: continue
            active=[]
            for ex,ets in zip(g["expiry"],g["entry_ts"]):
                if profile_active(vix,pd.Timestamp(ets),par,mode): active.append(ex)
            if len(active)<10: continue
            gz=g[g["expiry"].isin(active)]
            common=g[["expiry","net","net50"]].merge(gz[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
            upl=common["net_cand"]-common["net_base"]
            st=paired_stats(upl)
            dev_candidates.append({"family":family,"geom":geom,"entry_time":int(tm),"profile_id":pid,"mode":mode,
                                  "dev_n":len(gz),"dev_net":float(gz.net.sum()),"dev_net50":float(gz.net50.sum()),
                                  "dev_dd":max_dd(gz.sort_values("expiry").net.to_numpy()),"dev_uplift":float(upl.sum()),
                                  "dev_uplift_mean":st["mean"],"dev_ci_lo":st["ci_lo"],"dev_ci_hi":st["ci_hi"]})
    dc=pd.DataFrame(dev_candidates)
    if dc.empty: raise RuntimeError("no development candidates")
    dc=dc[(dc.dev_net>=0)&(dc.dev_net50>0)&(dc.dev_uplift>0)].sort_values(["dev_uplift_mean","dev_net"],ascending=False)
    # Diversify the frozen development shortlist: max 5 per family, max 30 total.
    picked=[]
    counts={}
    for r in dc.itertuples(index=False):
        if counts.get(r.family,0)>=5: continue
        picked.append(r._asdict()); counts[r.family]=counts.get(r.family,0)+1
        if len(picked)>=30: break
    frozen_dev=pd.DataFrame(picked)
    frozen_dev.to_csv(OUT/"frozen_dev_shortlist.csv",index=False)
    frozen_dev.to_csv(OUT/"stage1_candidates.csv",index=False)

    # Validation confirmation only after the development freeze.
    val_rows=[]
    for r in frozen_dev.itertuples(index=False):
        g=val[(val.family==r.family)&(val.geom==r.geom)&(val.entry_time==r.entry_time)]
        a=[]
        for ex,ets in zip(g["expiry"],g["entry_ts"]):
            if profile_active(vix,pd.Timestamp(ets),build_profiles()[-1][1] if False else next(par for pid,mm,par in defs if pid==r.profile_id and mm==r.mode),r.mode):
                a.append(ex)
        gz=g[g.expiry.isin(a)]
        common=g[["expiry","net","net50"]].merge(gz[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
        uplift_vec=(common["net_cand"]-common["net_base"]).to_numpy(float)
        st=paired_stats(uplift_vec)
        pos=uplift_vec[uplift_vec>0]
        concentration=(float(pos.max()/pos.sum()) if len(pos) and pos.sum()>0 else np.nan)
        base_dd=max_dd(g.sort_values("expiry").net.to_numpy()) if len(g) else np.nan
        val_rows.append({**r._asdict(),"val_n":len(gz),"val_net":float(gz.net.sum()) if len(gz) else np.nan,
                         "val_net50":float(gz.net50.sum()) if len(gz) else np.nan,"val_dd":max_dd(gz.sort_values("expiry").net.to_numpy()) if len(gz) else np.nan,
                         "base_val_net":float(g.net.sum()) if len(g) else np.nan,"base_val_dd":base_dd,
                         "val_uplift":float(common.net_cand.sum()-common.net_base.sum()) if len(common) else np.nan,
                         "val_uplift_mean":st["mean"],"val_ci_lo":st["ci_lo"],"val_ci_hi":st["ci_hi"],"val_p":st["p"],"common_n":len(common),
                         "max_positive_uplift_share":concentration})
    vd=pd.DataFrame(val_rows)
    if len(vd):
        vd["validation_gate"]=(vd.val_n>=20)&(vd.val_net>0)&(vd.val_net50>0)&(vd.val_uplift>0)&(vd.val_ci_lo>0)&(vd.val_dd<=1.25*vd.base_val_dd)&(vd.max_positive_uplift_share<=0.40)
        vd["val_p_holm"]=holm(vd.val_p.fillna(1).to_numpy())
        vd["inference_survivor"]=vd["validation_gate"]&(vd.val_p_holm<0.05)
    vd.to_csv(OUT/"validation_confirmation.csv",index=False)

    # Open 2026 only for candidates that passed the frozen validation gate and Holm test.
    hs=vd[vd["inference_survivor"]].copy() if len(vd) else pd.DataFrame()
    hold_rows=[]
    for r in hs.itertuples(index=False):
        g=hold[(hold.family==r.family)&(hold.geom==r.geom)&(hold.entry_time==r.entry_time)]
        par=next(par for pid,mm,par in defs if pid==r.profile_id and mm==r.mode)
        hz=g[[profile_active(vix,pd.Timestamp(ets),par,r.mode) for ets in g.entry_ts]]
        if hz.empty: continue
        common=g[["expiry","net","net50"]].merge(hz[["expiry","net"]],on="expiry",suffixes=("_base","_cand"))
        st=paired_stats(common.net_cand-common.net_base)
        hold_rows.append({**r._asdict(),"hold_n":len(hz),"hold_net":float(hz.net.sum()),"hold_net50":float(hz.net50.sum()),
                          "hold_dd":max_dd(hz.sort_values("expiry").net.to_numpy()),"hold_uplift":float(common.net_cand.sum()-common.net_base.sum()),
                          "hold_uplift_mean":st["mean"],"hold_ci_lo":st["ci_lo"],"hold_ci_hi":st["ci_hi"],"hold_p":st["p"],"hold_common_n":len(common)})
    hd=pd.DataFrame(hold_rows)
    if len(hd):
        hd["hold_p_holm"]=holm(hd.hold_p.fillna(1).to_numpy())
        hd["promotion_gate"]=(hd.hold_n>=10)&(hd.hold_net>0)&(hd.hold_net50>0)&(hd.hold_uplift>0)&(hd.hold_ci_lo>0)&(hd.hold_p_holm<0.05)
    hd.to_csv(OUT/"frozen_holdout_confirmation.csv",index=False)

    summary={"status":"COMPLETE_STAGE1","families":6,"structure_time_rows":int(len(base)),
             "development_candidates":int(len(dc)),"frozen_dev_shortlist":int(len(frozen_dev)),
             "validation_pass":int(vd["validation_gate"].sum()) if len(vd) else 0,
             "validation_inference_survivors":int(vd["inference_survivor"].sum()) if len(vd) else 0,
             "holdout_candidates_tested":int(len(hd)),
             "holdout_promotion_survivors":int(hd["promotion_gate"].sum()) if len(hd) else 0,
             "holdout_opened_after_validation_freeze":bool(len(hd)),
             "decision":"PROMISING_STAGE2_REQUIRED" if len(hd) and hd["promotion_gate"].any() else "NO_STAGE1_PROMOTION"}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
