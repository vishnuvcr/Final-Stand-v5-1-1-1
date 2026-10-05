import os, re, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO="thetrademarkk/india-index-options-1m"; TZ="Asia/Kolkata"
START=pd.Timestamp((os.getenv("SAMPLE_START") or "2021-05-27"),tz=TZ)
END=pd.Timestamp((os.getenv("SAMPLE_END") or "2026-09-30"),tz=TZ)
OUT=Path("results/dynamic_strategy_phase32"); OUT.mkdir(parents=True,exist_ok=True)
TICK=0.05; SLIPPAGE_TICKS=float(os.getenv("SLIPPAGE_TICKS","1"))
LOTS=6; WIDTH=50.0; ENTRY_HOUR=9; ENTRY_MINUTE=20
BROKERAGE_PER_ORDER=10.0

def lot_size_for_expiry(expiry):
    if expiry<pd.Timestamp("2021-08-01",tz=TZ): return 75
    if expiry<pd.Timestamp("2024-05-02",tz=TZ): return 50
    if expiry<pd.Timestamp("2025-01-02",tz=TZ): return 25
    if expiry<pd.Timestamp("2026-01-06",tz=TZ): return 75
    return 65

def fee_rates(d):
    if d>=pd.Timestamp("2026-04-01",tz=TZ): stt=0.0015
    elif d>=pd.Timestamp("2024-10-01",tz=TZ): stt=0.0010
    else: stt=0.000625
    if d>=pd.Timestamp("2026-03-01",tz=TZ): txn,ipft=0.000355299,0.000000001
    elif d>=pd.Timestamp("2024-10-01",tz=TZ): txn,ipft=0.0003503,0.000005
    else: txn,ipft=0.000495,0.000005
    return stt,txn,0.000001,ipft,0.00003

def load(path):
    p=hf_hub_download(repo_id=REPO,filename=path,repo_type="dataset",token=os.getenv("HF_TOKEN") or None)
    df=pd.read_parquet(p); df["timestamp"]=pd.to_datetime(df["timestamp"])
    if df["timestamp"].dt.tz is None: df["timestamp"]=df["timestamp"].dt.tz_localize(TZ)
    else: df["timestamp"]=df["timestamp"].dt.tz_convert(TZ)
    return df

def exec_px(px,action):
    s=SLIPPAGE_TICKS*TICK
    return max(0.0,float(px)+s) if action=="buy" else max(0.0,float(px)-s)

def charges(orders,lot):
    brokerage=BROKERAGE_PER_ORDER*len(orders)
    exchange=sebi=ipft=stt=stamp=0.0
    qty=lot*LOTS
    for d,side,px in orders:
        sr,tx,se,ip,st=fee_rates(d); turnover=float(px)*qty
        exchange+=tx*turnover; sebi+=se*turnover; ipft+=ip*turnover
        if side=="sell": stt+=sr*turnover
        else: stamp+=st*turnover
    gst=.18*(brokerage+exchange+sebi+ipft)
    return brokerage+exchange+sebi+ipft+stt+stamp+gst

def norm_cdf(x):
    x=np.asarray(x,float); ax=np.abs(x); t=1/(1+.2316419*ax)
    poly=((((1.330274429*t-1.821255978)*t+1.781477937)*t-.356563782)*t+.319381530)*t
    pdf=np.exp(-.5*ax*ax)/np.sqrt(2*np.pi); cdf=1-pdf*poly
    return np.where(x>=0,cdf,1-cdf)

def bs_delta(S,K,T,sig,typ):
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8)
    d1=(np.log(S/K)+.5*sig*sig*T)/(sig*np.sqrt(T)); n=norm_cdf(d1)
    return n if typ=="CE" else n-1

def bs_price(S,K,T,sig,typ):
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8)
    d1=(np.log(S/K)+.5*sig*sig*T)/(sig*np.sqrt(T)); d2=d1-sig*np.sqrt(T)
    return S*norm_cdf(d1)-K*norm_cdf(d2) if typ=="CE" else K*norm_cdf(-d2)-S*norm_cdf(-d1)

def implied_delta(price,S,K,T,typ):
    p=np.asarray(price,float); s=np.asarray(S,float); t=np.asarray(T,float)
    intrinsic=np.maximum(s-K,0) if typ=="CE" else np.maximum(K-s,0)
    valid=np.isfinite(p)&np.isfinite(s)&np.isfinite(t)&(t>0)&(s>0)&(p>=intrinsic-1e-7)&(p>1e-8)
    out=np.full(p.shape,np.nan)
    if not valid.any(): return out
    idx=np.where(valid)[0]; pp=p[idx]; ss=s[idx]; tt=t[idx]
    lo=np.full_like(pp,1e-5); hi=np.full_like(pp,5.0); x=np.full_like(pp,.30)
    for _ in range(16):
        d1=(np.log(ss/K)+.5*x*x*tt)/(x*np.sqrt(tt))
        px=bs_price(ss,K,tt,x,typ); v=ss*np.exp(-.5*d1*d1)/np.sqrt(2*np.pi)*np.sqrt(tt)
        xn=np.clip(x-(px-pp)/np.maximum(v,1e-10),lo,hi)
        bad=~np.isfinite(xn)|(v<1e-10); xn[bad]=(lo[bad]+hi[bad])/2
        pxn=bs_price(ss,K,tt,xn,typ); low=pxn<pp
        lo=np.where(low,xn,lo); hi=np.where(low,hi,xn); x=xn
    residual=np.abs(bs_price(ss,K,tt,x,typ)-pp); good=residual<=.03
    out[idx[good]]=bs_delta(ss[good],K,tt,x[good],typ)
    return out

def nearest_delta_strike(q,spot,ts,typ,target):
    sub=q[q.option_type==typ].copy()
    if sub.empty: return None
    expiry=sub.expiry_ts.iloc[0]; T=max((expiry-ts).total_seconds()/31557600.0,1e-10)
    ds=implied_delta(sub.close.to_numpy(float),np.full(len(sub),spot),sub.strike.to_numpy(float),np.full(len(sub),T),typ)
    ok=np.isfinite(ds)
    if not ok.any(): return None
    z=sub.loc[ok].copy(); z["delta"]=ds[ok]
    i=(z.delta-target).abs().idxmin()
    return float(z.loc[i,"strike"]),float(z.loc[i,"delta"])

def expiry_list(api):
    out=[]
    for f in api.list_repo_files(REPO,repo_type="dataset"):
        m=re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$",f)
        if m:
            d=pd.Timestamp(m.group(1),tz=TZ)
            if START<=d<=END: out.append(d)
    monthly={(d.year,d.month):max(x for x in out if x.year==d.year and x.month==d.month) for d in out}
    return [d for d in sorted(set(out)) if monthly[(d.year,d.month)]!=d]

def run_expiry(expiry,option_df,spot_df,target_dir):
    df=option_df.copy(); df["expiry_ts"]=expiry+pd.Timedelta(hours=15,minutes=30)
    spot_df=spot_df.sort_values("timestamp")
    days=sorted(pd.to_datetime(spot_df.timestamp.dt.normalize().unique()))
    trades=[]; skips=[]
    pos=None
    # Work through all minutes up to expiry; entries are blocked on expiry day.
    for day in days:
        if day>expiry.normalize(): break
        day_spot=spot_df[spot_df.timestamp.dt.normalize()==day]
        if day_spot.empty: continue
        if pos is not None:
            # carried position is handled by the global minute loop below
            pass
        if day==expiry.normalize(): continue
        # entry candidates only if flat and direction points here; after an exit the next candidate is later in same day.
        for ts in day_spot.timestamp.tolist():
            if ts.hour<ENTRY_HOUR or (ts.hour==ENTRY_HOUR and ts.minute<ENTRY_MINUTE): continue
            if pos is not None: break
            row=day_spot[day_spot.timestamp==ts]
            spot=float(row.spot.iloc[0])
            typ="CE" if target_dir==1 else "PE"
            target=0.25 if typ=="CE" else -0.25
            snap=df[df.timestamp==ts]
            if snap.empty: continue
            found=nearest_delta_strike(snap,spot,ts,typ,target)
            if found is None: skips.append([str(ts),"no_entry_delta"]); continue
            short_k,entry_delta=found
            long_k=short_k+WIDTH if typ=="CE" else short_k-WIDTH
            legs=df[(df.timestamp==ts)&(df.option_type==typ)&(df.strike.isin([short_k,long_k]))]
            if len(legs)<2: skips.append([str(ts),"missing_entry_legs"]); continue
            q={float(x.strike):float(x.close) for _,x in legs.iterrows()}
            if short_k not in q or long_k not in q: continue
            short_entry=q[short_k]; long_entry=q[long_k]
            pos={"entry_ts":ts,"typ":typ,"short_k":short_k,"long_k":long_k,"short_entry":short_entry,"long_entry":long_entry,"entry_delta":entry_delta,"lot":lot_size_for_expiry(expiry)}
            # monitor all subsequent timestamps until exit/expiry using selected short leg
            path=df[(df.timestamp>ts)&(df.timestamp<=expiry+pd.Timedelta(hours=15,minutes=29))&(df.option_type==typ)&(df.strike.isin([short_k,long_k]))].pivot_table(index="timestamp",columns="strike",values="close",aggfunc="last")
            path=path.dropna(subset=[short_k,long_k])
            spot_path=spot_df[(spot_df.timestamp>ts)&(spot_df.timestamp<=expiry+pd.Timedelta(hours=15,minutes=29))][["timestamp","spot"]]
            path=path.reset_index().merge(spot_path,on="timestamp",how="inner").sort_values("timestamp")
            exit_row=None; exit_reason=None; exit_delta=np.nan
            expiry_ts=expiry+pd.Timedelta(hours=15,minutes=30)
            for _,pr in path.iterrows():
                tleft=max((expiry_ts-pr.timestamp).total_seconds()/31557600.0,1e-10)
                d=implied_delta(np.asarray([pr[short_k]]),np.asarray([pr.spot]),np.asarray([short_k]),np.asarray([tleft]),typ)[0]
                if not np.isfinite(d): continue
                hit=(d>=.50 or d<=.04) if typ=="CE" else (d<=-.50 or d>=-.04)
                if hit:
                    exit_row=pr; exit_delta=d; exit_reason="DELTA_EXIT"; break
            if exit_row is None and not path.empty:
                exit_row=path.iloc[-1]; exit_reason="CONTRACT_EXPIRY"
            if exit_row is None:
                skips.append([str(ts),"no_complete_exit_path"]); pos=None; continue
            ep_long=exec_px(long_entry,"buy"); ep_short=exec_px(short_entry,"sell")
            xp_short=exec_px(float(exit_row[short_k]),"buy"); xp_long=exec_px(float(exit_row[long_k]),"sell")
            # short sells at entry, buys at exit; long buys at entry, sells at exit
            gross=((ep_short-xp_short)+(xp_long-ep_long))*pos["lot"]*LOTS
            orders=[(ts,"sell",ep_short),(ts,"buy",ep_long),(pd.Timestamp(exit_row.timestamp),"buy",xp_short),(pd.Timestamp(exit_row.timestamp),"sell",xp_long)]
            cost=charges(orders,pos["lot"]); net=gross-cost
            win=net>0
            trades.append({"expiry":str(expiry.date()),"entry_ts":str(ts),"exit_ts":str(exit_row.timestamp),"direction":"CALL" if typ=="CE" else "PUT","short_delta_entry":entry_delta,"short_delta_exit":exit_delta,"short_strike":short_k,"long_strike":long_k,"lot_size":pos["lot"],"gross_rupees":gross,"cost_rupees":cost,"net_rupees":net,"exit_reason":exit_reason,"direction_after":"CALL" if ((target_dir==1 and win) or (target_dir==-1 and not win)) else "PUT"})
            target_dir=target_dir if win else -target_dir
            pos=None
            # continue scanning; target_dir is global within this expiry
    return trades,skips,target_dir

def main():
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    spot=load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})
    expiries=expiry_list(api); all_trades=[]; all_skips=[]; target_dir=1
    for i,expiry in enumerate(expiries):
        try: od=load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet")
        except Exception as e: all_skips.append([str(expiry.date()),"load",repr(e)]); continue
        od["option_type"]=od.option_type.astype(str).str.upper(); od["strike"]=pd.to_numeric(od.strike,errors="coerce"); od=od.dropna(subset=["strike","timestamp","close"])
        sd=spot[(spot.timestamp>=expiry-pd.Timedelta(days=14))&(spot.timestamp<=expiry)].copy()
        if sd.empty: continue
        tr,sk,target_dir=run_expiry(expiry,od,sd,target_dir); all_trades.extend(tr); all_skips.extend([[str(expiry.date()),*x] for x in sk])
        print(f"expiry {expiry.date()} trades={len(tr)} direction={'CALL' if target_dir==1 else 'PUT'}",flush=True)
    tr=pd.DataFrame(all_trades)
    if tr.empty:
        pd.DataFrame(columns=["expiry","reason","detail"]).to_csv(OUT/"skips.csv",index=False); raise RuntimeError("Phase 32 produced zero trades")
    tr["cum_net"]=tr.net_rupees.cumsum(); tr["peak"]=tr.cum_net.cummax(); tr["drawdown"]=tr.peak-tr.cum_net
    tr.to_csv(OUT/"trades.csv",index=False); pd.DataFrame(all_skips,columns=["expiry","reason","detail"]).to_csv(OUT/"skips.csv",index=False)
    profits=tr.loc[tr.net_rupees>0,"net_rupees"].sum(); losses=-tr.loc[tr.net_rupees<0,"net_rupees"].sum()
    byyear=tr.assign(year=pd.to_datetime(tr.exit_ts).dt.year).groupby("year").agg(trades=("net_rupees","size"),net=("net_rupees","sum"),win_rate=("net_rupees",lambda x:(x>0).mean()),mean_net=("net_rupees","mean")).reset_index()
    bydir=tr.groupby("direction").agg(trades=("net_rupees","size"),net=("net_rupees","sum"),win_rate=("net_rupees",lambda x:(x>0).mean()),mean_net=("net_rupees","mean")).reset_index()
    summary={"trades":len(tr),"net_pnl":float(tr.net_rupees.sum()),"gross_pnl":float(tr.gross_rupees.sum()),"costs":float(tr.cost_rupees.sum()),"win_rate":float((tr.net_rupees>0).mean()),"profit_factor":float(profits/losses) if losses else None,"max_drawdown":float(tr.drawdown.max()),"call_trades":int((tr.direction=="CALL").sum()),"put_trades":int((tr.direction=="PUT").sum()),"delta_exit_trades":int((tr.exit_reason=="DELTA_EXIT").sum()),"expiry_termination_trades":int((tr.exit_reason=="CONTRACT_EXPIRY").sum()),"slippage_ticks":SLIPPAGE_TICKS,"lots_per_leg":LOTS,"width":WIDTH}
    pd.DataFrame([summary]).to_csv(OUT/"summary.csv",index=False); byyear.to_csv(OUT/"yearly_statistics.csv",index=False); bydir.to_csv(OUT/"direction_statistics.csv",index=False)
    print(json.dumps(summary,indent=2)); print(byyear.to_string(index=False))
if __name__=="__main__": main()
