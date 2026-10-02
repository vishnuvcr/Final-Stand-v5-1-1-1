import os, re
from pathlib import Path
import pandas as pd
import numpy as np
from huggingface_hub import HfApi, hf_hub_download

REPO="thetrademarkk/india-index-options-1m"
START=pd.Timestamp(os.getenv("START_DATE","2024-01-01"),tz="Asia/Kolkata")
END=pd.Timestamp(os.getenv("END_DATE","2026-09-30"),tz="Asia/Kolkata")
OUT=Path("results"); OUT.mkdir(parents=True,exist_ok=True)
SLIPPAGE_TICKS=float(os.getenv("SLIPPAGE_TICKS","1"))
TICK=float(os.getenv("OPTION_TICK","0.05"))
LOT_SIZE=int(os.getenv("LOT_SIZE","75"))

def fee_model(d):
    if d >= pd.Timestamp("2026-04-01",tz="Asia/Kolkata"): stt=0.0015
    elif d >= pd.Timestamp("2024-10-01",tz="Asia/Kolkata"): stt=0.0010
    else: stt=0.000625
    txn=0.0003503 if d >= pd.Timestamp("2024-10-01",tz="Asia/Kolkata") else 0.000495
    return stt,txn,0.000001,0.000001,0.00003

def exec_px(px,action):
    return max(0.0,px+(SLIPPAGE_TICKS*TICK if action=="buy" else -SLIPPAGE_TICKS*TICK))

def charges(entry,exit_,d):
    stt,txn,sebi,ipft,stamp=fee_model(d)
    turnover=sum(p for _,p in entry+exit_)
    sells=sum(p for s,p in entry+exit_ if s=="sell")
    buys=sum(p for s,p in entry+exit_ if s=="buy")
    brokerage=60.0
    exchange=txn*turnover*LOT_SIZE
    sebi_fee=sebi*turnover*LOT_SIZE
    ipft_fee=ipft*turnover*LOT_SIZE
    stt_fee=stt*sells*LOT_SIZE
    stamp_fee=stamp*buys*LOT_SIZE
    gst=0.18*(brokerage+exchange+sebi_fee+ipft_fee)
    return brokerage+exchange+sebi_fee+ipft_fee+stt_fee+stamp_fee+gst

def payoff(side,S,k6,k7,k8,p):
    if side=="PUT": return max(k6-S,0)-max(k7-S,0)-max(k8-S,0)+p
    return max(S-k6,0)-max(S-k7,0)-max(S-k8,0)+p

def load(path):
    p=hf_hub_download(repo_id=REPO,filename=path,repo_type="dataset",token=(os.getenv("HF_TOKEN") or None))
    df=pd.read_parquet(p)
    df["timestamp"]=pd.to_datetime(df["timestamp"])
    if df["timestamp"].dt.tz is None: df["timestamp"]=df["timestamp"].dt.tz_localize("Asia/Kolkata")
    else: df["timestamp"]=df["timestamp"].dt.tz_convert("Asia/Kolkata")
    return df

def main():
    spot=load("index/NIFTY.parquet")[["timestamp","close"]].rename(columns={"close":"spot"})
    api=HfApi(token=os.getenv("HF_TOKEN"))
    files=api.list_repo_files(REPO,repo_type="dataset")
    exps=[]
    for f in files:
        m=re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$",f)
        if m:
            d=pd.Timestamp(m.group(1),tz="Asia/Kolkata")
            if START<=d<=END: exps.append(d)
    trades=[]; missing=[]
    for exp in sorted(set(exps)):
        entry_ts=(exp-pd.Timedelta(days=4)).normalize()+pd.Timedelta(hours=10)
        sr=spot[spot.timestamp==entry_ts]
        if sr.empty: missing.append([str(exp.date()),"missing 10:00 spot"]); continue
        s0=float(sr.iloc[0].spot)
        try: df=load(f"options/NIFTY/{exp.strftime('%Y-%m-%d')}.parquet")
        except Exception as e: missing.append([str(exp.date()),"download/read "+repr(e)]); continue
        strikes=sorted(df.strike.dropna().astype(float).unique())
        atm=min(strikes,key=lambda x:abs(x-s0))
        puts=[x for x in strikes if x<atm]; calls=[x for x in strikes if x>atm]
        if len(puts)<8 or len(calls)<8: missing.append([str(exp.date()),"fewer than 8 OTM strikes"]); continue
        ks={"PUT":(puts[-6],puts[-7],puts[-8]),"CALL":(calls[5],calls[6],calls[7])}
        px={}
        ok=True
        for side,(k6,k7,k8) in ks.items():
            typ="PE" if side=="PUT" else "CE"
            q=df[(df.timestamp==entry_ts)&(df.option_type.str.upper()==typ)&(df.strike.astype(float).isin([k6,k7,k8]))]
            vals={float(r.strike):float(r.close) for _,r in q.iterrows()}
            if any(k not in vals for k in [k6,k7,k8]): ok=False
            px[side]=[vals.get(k6,np.nan),vals.get(k7,np.nan),vals.get(k8,np.nan)]
        if not ok: missing.append([str(exp.date()),"missing entry leg quote"]); continue
        rawP={s:v[1]+v[2]-v[0] for s,v in px.items()}
        side="PUT" if rawP["PUT"]>=rawP["CALL"] else "CALL"
        k6,k7,k8=ks[side]; p6,p7,p8=px[side]
        ep6,ep7,ep8=exec_px(p6,"buy"),exec_px(p7,"sell"),exec_px(p8,"sell")
        entryP=ep7+ep8-ep6
        end_ts=exp.normalize()+pd.Timedelta(hours=15,minutes=29)
        typ="PE" if side=="PUT" else "CE"
        q=df[(df.timestamp>=entry_ts)&(df.timestamp<=end_ts)&(df.option_type.str.upper()==typ)&(df.strike.astype(float).isin([k6,k7,k8]))]
        piv=q.pivot_table(index="timestamp",columns="strike",values="close",aggfunc="last").dropna(subset=[k6,k7,k8])
        if piv.empty: missing.append([str(exp.date()),"no complete 3-leg minute"]); continue
        target=entryP
        exit_ts=piv.index[-1]; reason="EXPIRY"; xp=None; mfe=-1e99
        for ts,row in piv.iterrows():
            m6,m7,m8=float(row[k6]),float(row[k7]),float(row[k8])
            mtm=(m7+m8-m6)-entryP
            mfe=max(mfe,mtm)
            if mtm>=target:
                exit_ts=ts; reason="TARGET"; xp=(m6,m7,m8); break
        if xp is None:
            r=piv.loc[exit_ts]; xp=(float(r[k6]),float(r[k7]),float(r[k8]))
        x6,x7,x8=xp
        xp6,xp7,xp8=exec_px(x6,"sell"),exec_px(x7,"buy"),exec_px(x8,"buy")
        gross=(ep6-xp6)+(xp7-ep7)+(xp8-ep8)
        c=charges([("buy",ep6),("sell",ep7),("sell",ep8)],[("sell",xp6),("buy",xp7),("buy",xp8)],entry_ts)
        net=gross-c/LOT_SIZE
        trades.append({"expiry":str(exp.date()),"entry_ts":str(entry_ts),"exit_ts":str(exit_ts),"strategy":side,"spot_entry":s0,"atm":atm,"k6":k6,"k7":k7,"k8":k8,"raw_P":rawP[side],"entry_P":entryP,"flatline_target":target,"gross_points":gross,"charges_rupees":c,"net_points":net,"net_rupees_lot":net*LOT_SIZE,"exit_reason":reason,"mfe_points":mfe})
    tr=pd.DataFrame(trades); tr.to_csv(OUT/"trades.csv",index=False)
    pd.DataFrame(missing,columns=["expiry","reason"]).to_csv(OUT/"missing.csv",index=False)
    if not tr.empty:
        sm=tr.groupby("strategy").agg(trades=("expiry","count"),win_rate=("net_points",lambda x:(x>0).mean()),mean_net_points=("net_points","mean"),median_net_points=("net_points","median"),sum_net_points=("net_points","sum"),mean_charges=("charges_rupees","mean"),target_exit_rate=("exit_reason",lambda x:(x=="TARGET").mean()),mean_mfe=("mfe_points","mean")).reset_index()
        sm.to_csv(OUT/"summary.csv",index=False)
        print(sm.to_string(index=False))
        print("TOTAL_TRADES",len(tr),"TOTAL_NET_POINTS",tr.net_points.sum())
    else: print("NO_TRADES")

if __name__=="__main__": main()
