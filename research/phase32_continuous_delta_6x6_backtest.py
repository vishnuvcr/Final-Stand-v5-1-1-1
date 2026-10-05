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
LOTS=6; WIDTH=50.0; ENTRY_HOUR=9; ENTRY_MINUTE=20; LAST_ENTRY_HOUR=15; LAST_ENTRY_MINUTE=28
BROKERAGE_PER_ORDER=10.0

def lot_size_for_expiry(expiry):
    # Expiry-specific NIFTY market-lot transitions from NSE circulars.
    # 75 -> 50: first revised weekly expiry Aug-2021; July-2021 monthly was
    # already revised to 50, so use 29-Jul-2021 as the practical cutoff.
    # 50 -> 25: first revised weekly expiry 02-May-2024.
    # 25 -> 75: last weekly old = 19-Dec-2024; first weekly new = 02-Jan-2025.
    # The Jan-2025 monthly expiry (30-Jan-2025) remained on 25; first revised
    # monthly expiry was 27-Feb-2025.
    # 75 -> 65: first revised weekly expiry 06-Jan-2026; first revised monthly
    # expiry 27-Jan-2026.
    if expiry < pd.Timestamp("2021-07-29",tz=TZ):
        return 75
    if expiry < pd.Timestamp("2024-05-02",tz=TZ):
        return 50
    if expiry <= pd.Timestamp("2024-12-26",tz=TZ):
        return 25
    if expiry <= pd.Timestamp("2025-01-23",tz=TZ):
        return 75
    if expiry == pd.Timestamp("2025-01-30",tz=TZ):
        return 25
    if expiry < pd.Timestamp("2026-01-06",tz=TZ):
        return 75
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
    S=np.asarray(S,float); K=np.asarray(K,float); T=np.asarray(T,float); sig=np.asarray(sig,float)
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8)
    d1=(np.log(S/K)+.5*sig*sig*T)/(sig*np.sqrt(T)); n=norm_cdf(d1)
    return n if typ=="CE" else n-1

def bs_price(S,K,T,sig,typ):
    S=np.asarray(S,float); K=np.asarray(K,float); T=np.asarray(T,float); sig=np.asarray(sig,float)
    T=np.maximum(T,1e-10); sig=np.maximum(sig,1e-8)
    d1=(np.log(S/K)+.5*sig*sig*T)/(sig*np.sqrt(T)); d2=d1-sig*np.sqrt(T)
    return S*norm_cdf(d1)-K*norm_cdf(d2) if typ=="CE" else K*norm_cdf(-d2)-S*norm_cdf(-d1)

def implied_delta(price,S,K,T,typ):
    p=np.asarray(price,float); s=np.asarray(S,float); t=np.asarray(T,float); K=np.asarray(K,float)
    intrinsic=np.maximum(s-K,0) if typ=="CE" else np.maximum(K-s,0)
    valid=np.isfinite(p)&np.isfinite(s)&np.isfinite(t)&(t>0)&(s>0)&(p>=intrinsic-1e-7)&(p>1e-8)
    out=np.full(p.shape,np.nan)
    if not valid.any(): return out
    idx=np.where(valid)[0]; pp=p[idx]; ss=s[idx]; tt=t[idx]; kk=K[idx]
    lo=np.full_like(pp,1e-5); hi=np.full_like(pp,5.0); x=np.full_like(pp,.30)
    for _ in range(16):
        d1=(np.log(ss/kk)+.5*x*x*tt)/(x*np.sqrt(tt))
        px=bs_price(ss,kk,tt,x,typ); v=ss*np.exp(-.5*d1*d1)/np.sqrt(2*np.pi)*np.sqrt(tt)
        xn=np.clip(x-(px-pp)/np.maximum(v,1e-10),lo,hi)
        bad=~np.isfinite(xn)|(v<1e-10); xn[bad]=(lo[bad]+hi[bad])/2
        pxn=bs_price(ss,kk,tt,xn,typ); low=pxn<pp
        lo=np.where(low,xn,lo); hi=np.where(low,hi,xn); x=xn
    residual=np.abs(bs_price(ss,kk,tt,x,typ)-pp); good=residual<=.03
    out[idx[good]]=bs_delta(ss[good],kk[good],tt[good],x[good],typ)
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

def available_expiry_files(api):
    out=set()
    for f in api.list_repo_files(REPO,repo_type="dataset"):
        m=re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$",f)
        if m:
            out.add(pd.Timestamp(m.group(1),tz=TZ))
    return out

def expected_weekly_expiries(spot):
    # NIFTY weekly expiry was Thursday through contracts expiring on/before
    # 2025-08-28 and Tuesday for contracts expiring on/after 2025-09-01.
    # If the scheduled day is a market holiday, NSE uses the previous trading
    # day. Build the calendar from the observed NIFTY trading dates.
    trading_days=sorted(set(pd.to_datetime(spot.timestamp.dt.normalize())))
    trading_set=set(trading_days)
    if not trading_days:
        return []
    first_day=min(trading_days).normalize()
    last_day=max(trading_days).normalize()
    weeks=pd.date_range(first_day-pd.Timedelta(days=7),last_day+pd.Timedelta(days=7),freq="W-MON",tz=TZ)
    out=[]
    for monday in weeks:
        if monday<first_day-pd.Timedelta(days=7) or monday>last_day:
            continue
        scheduled_wd=1 if monday>=pd.Timestamp("2025-09-01",tz=TZ) else 3
        scheduled=monday+pd.Timedelta(days=scheduled_wd)
        candidates=[d for d in trading_days if monday<=d<=scheduled]
        if not candidates:
            continue
        expiry=max(candidates)
        if first_day<=expiry<=last_day and START<=expiry<=END:
            out.append(expiry)
    return sorted(set(out))

def run_expiry(expiry,option_df,spot_df,target_dir,window_start):
    df=option_df.copy()
    expiry_ts=expiry+pd.Timedelta(hours=15,minutes=30)
    df["expiry_ts"]=expiry_ts
    spot_df=spot_df.sort_values("timestamp").copy()
    timeline=spot_df[
        (spot_df.timestamp>window_start)
        &(spot_df.timestamp<=expiry+pd.Timedelta(hours=15,minutes=29))
    ].drop_duplicates("timestamp").reset_index(drop=True)
    trades=[]; skips=[]
    cursor=0

    # Chronological event loop. Once a position is opened, the cursor advances
    # only to the actual observed exit timestamp, preventing impossible
    # re-entry before a future exit that has already been selected.
    while cursor < len(timeline):
        ts=pd.Timestamp(timeline.at[cursor,"timestamp"])
        day=ts.normalize()

        # No new positions on expiry day or in the final 120 seconds.
        if day==expiry.normalize():
            break
        if ts.hour<ENTRY_HOUR or (ts.hour==ENTRY_HOUR and ts.minute<ENTRY_MINUTE):
            cursor += 1
            continue
        if ts.hour>LAST_ENTRY_HOUR or (ts.hour==LAST_ENTRY_HOUR and ts.minute>=LAST_ENTRY_MINUTE):
            cursor += 1
            continue

        spot=float(timeline.at[cursor,"spot"])
        typ="CE" if target_dir==1 else "PE"
        target=0.25 if typ=="CE" else -0.25
        snap=df[df.timestamp==ts]
        if snap.empty:
            cursor += 1
            continue

        found=nearest_delta_strike(snap,spot,ts,typ,target)
        if found is None:
            skips.append([str(ts),"no_entry_delta"])
            cursor += 1
            continue

        short_k,entry_delta=found
        long_k=short_k+WIDTH if typ=="CE" else short_k-WIDTH
        legs=df[
            (df.timestamp==ts)
            &(df.option_type==typ)
            &(df.strike.isin([short_k,long_k]))
        ]
        if len(legs)<2:
            skips.append([str(ts),"missing_entry_legs"])
            cursor += 1
            continue

        q={float(x.strike):float(x.close) for _,x in legs.iterrows()}
        if short_k not in q or long_k not in q:
            skips.append([str(ts),"missing_entry_prices"])
            cursor += 1
            continue

        short_entry=q[short_k]; long_entry=q[long_k]
        lot=lot_size_for_expiry(expiry)

        # Monitor only after the actual entry timestamp. The first qualifying
        # observation is the exit; no later observation may be used first.
        path=df[
            (df.timestamp>ts)
            &(df.timestamp<=expiry+pd.Timedelta(hours=15,minutes=29))
            &(df.option_type==typ)
            &(df.strike.isin([short_k,long_k]))
        ].pivot_table(
            index="timestamp",columns="strike",values="close",aggfunc="last"
        ).dropna(subset=[short_k,long_k])

        if path.empty:
            skips.append([str(ts),"no_complete_exit_path"])
            break

        path=path.reset_index().merge(
            timeline[["timestamp","spot"]],
            on="timestamp",how="inner"
        ).sort_values("timestamp").reset_index(drop=True)

        # Vectorized exit-delta inversion over the full future path.
        # This is computationally equivalent to the prior minute-by-minute
        # calculation but materially faster for the 1-minute historical sample.
        tleft=np.maximum(
            (expiry_ts-pd.to_datetime(path.timestamp)).dt.total_seconds().to_numpy(float)
            /31557600.0,
            1e-10
        )
        deltas=implied_delta(
            path[short_k].to_numpy(float),
            path.spot.to_numpy(float),
            np.full(len(path),short_k,float),
            tleft,
            typ
        )
        hit=(deltas>=.50)|(deltas<=.04) if typ=="CE" else (deltas<=-.50)|(deltas>=-.04)
        hit_idx=np.flatnonzero(np.isfinite(deltas)&hit)
        if len(hit_idx):
            eidx=int(hit_idx[0])
            exit_row=path.iloc[eidx]
            exit_delta=float(deltas[eidx])
            exit_reason="DELTA_EXIT"
        else:
            exit_row=path.iloc[-1]
            exit_delta=np.nan
            exit_reason="CONTRACT_EXPIRY"

        if exit_row is None:
            exit_row=path.iloc[-1]
            exit_reason="CONTRACT_EXPIRY"

        exit_ts=pd.Timestamp(exit_row.timestamp)
        ep_long=exec_px(long_entry,"buy")
        ep_short=exec_px(short_entry,"sell")
        xp_short=exec_px(float(exit_row[short_k]),"buy")
        xp_long=exec_px(float(exit_row[long_k]),"sell")

        gross=((ep_short-xp_short)+(xp_long-ep_long))*lot*LOTS
        orders=[
            (ts,"sell",ep_short),(ts,"buy",ep_long),
            (exit_ts,"buy",xp_short),(exit_ts,"sell",xp_long)
        ]
        cost=charges(orders,lot)
        net=gross-cost
        if net>0:
            direction_after=target_dir
        elif net<0:
            direction_after=-target_dir
        else:
            direction_after=target_dir
        win=net>0

        trades.append({
            "expiry":str(expiry.date()),
            "entry_ts":str(ts),
            "exit_ts":str(exit_ts),
            "direction":"CALL" if typ=="CE" else "PUT",
            "short_delta_entry":entry_delta,
            "short_delta_exit":exit_delta,
            "short_strike":short_k,
            "long_strike":long_k,
            "lot_size":lot,
            "gross_rupees":gross,
            "cost_rupees":cost,
            "net_rupees":net,
            "exit_reason":exit_reason,
            "direction_after":"CALL" if direction_after==1 else "PUT"
        })

        target_dir=direction_after

        # Advance strictly beyond the realized exit. This is the critical
        # state-machine guard against lookahead/overlapping re-entry.
        future_idx=np.flatnonzero(timeline.timestamp.to_numpy()==exit_ts)
        if len(future_idx)==0:
            break
        cursor=int(future_idx[0])+1

    return trades,skips,target_dir

def main():
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    spot=load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})
    expected=expected_weekly_expiries(spot)
    available=available_expiry_files(api)
    expiries=[]
    all_skips=[]; all_trades=[]; target_dir=1
    for expiry in expected:
        if expiry not in available:
            all_skips.append([str(expiry.date()),"missing_expiry_file","expected weekly expiry absent from dataset"])
            break
        expiries.append(expiry)
    if not expiries:
        raise RuntimeError("Phase 32 found no contiguous expiry files in the requested sample")

    coverage={"dataset_repo":REPO,"requested_start":str(START.date()),"requested_end":str(END.date()),
              "first_expected_expiry":str(expected[0].date()) if expected else None,
              "last_contiguous_expiry":str(expiries[-1].date()),
              "expected_expiries":len(expected),"contiguous_expiries":len(expiries),
              "coverage_rule":"stop at first missing weekly-expiry file or incomplete contract path"}
    for i,expiry in enumerate(expiries):
        try: od=load(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet")
        except Exception as e:
            all_skips.append([str(expiry.date()),"load",repr(e)]); break
        od["option_type"]=od.option_type.astype(str).str.upper()
        od["strike"]=pd.to_numeric(od.strike,errors="coerce")
        od=od.dropna(subset=["strike","timestamp","close"])
        option_max=od.timestamp.max()
        required_last=expiry+pd.Timedelta(hours=15,minutes=29)
        if pd.isna(option_max) or option_max<required_last:
            all_skips.append([str(expiry.date()),"incomplete_expiry_data",f"last_option_timestamp={option_max}"])
            break
        prev_expiry=expiries[i-1] if i>0 else None
        window_start=prev_expiry+pd.Timedelta(hours=15,minutes=30) if prev_expiry is not None else expiry
        sd=spot[(spot.timestamp>window_start)&(spot.timestamp<=required_last)].copy()
        if sd.empty or sd.timestamp.max()<required_last:
            all_skips.append([str(expiry.date()),"incomplete_spot_data",f"last_spot_timestamp={sd.timestamp.max() if not sd.empty else None}"])
            break
        tr,sk,target_dir=run_expiry(expiry,od,sd,target_dir,window_start)
        all_trades.extend(tr)
        all_skips.extend([[str(expiry.date()),*x] for x in sk])
        print(f"expiry {expiry.date()} trades={len(tr)} direction={'CALL' if target_dir==1 else 'PUT'}",flush=True)
    coverage["processed_expiries"]=len(set(t["expiry"] for t in all_trades))
    coverage["last_trade_expiry"]=max([t["expiry"] for t in all_trades],default=None)
    with open(OUT/"coverage.json","w") as fh: json.dump(coverage,fh,indent=2)
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
