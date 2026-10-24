#!/usr/bin/env python3
"""Phase 112: fixed-entry one-leg Greek stop combinations; no parameter tuning."""
from __future__ import annotations
import gc, hashlib, itertools, json, math, os, re, sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"results"/"phase112"
sys.path.insert(0,str(ROOT/"research"))
import phase111_zigzag_weekly_expiry as base
HF_REPO=base.HF_REPO; TZ=base.TZ; RATE=base.RATE; YEAR_DAYS=base.YEAR_DAYS
ENTRY_TIME,SELECT_TIME,EXIT_TIME,EXPIRY_CLOSE="10:00:00","09:59:00","10:00:00","15:30:00"
REPS,SEED=1000,20261024; PRIMARY_COST_ID="B20_S0.25_F1.0"
FIXED={"delta":.50,"gamma":.20,"vega":.20,"theta":.25,"rho":.0005}
SWEEP={"delta":(.30,.40,.50,.60),"gamma":(.05,.10,.20,.30),"vega":(.05,.10,.20,.30),
       "theta":(0.,.25,.50),"rho":(.0001,.0005,.001,.0025)}
METRICS=("delta","gamma","vega","theta","rho")

def now(): return datetime.now(timezone.utc).isoformat()
def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
    return h.hexdigest()
def cdf(x): return .5*(1+math.erf(x/math.sqrt(2)))
def pdf(x): return math.exp(-.5*x*x)/math.sqrt(2*math.pi)

def greeks(s,k,t,v,typ):
    if typ not in ("CE","PE") or min(s,k,t,v)<=0 or not all(math.isfinite(x) for x in (s,k,t,v)): return None
    rt=math.sqrt(t); d1=(math.log(s/k)+(RATE+.5*v*v)*t)/(v*rt); d2=d1-v*rt
    dl=base.delta(s,k,t,v,typ); ga=pdf(d1)/(s*v*rt); ve=s*pdf(d1)*rt/100
    common=-s*pdf(d1)*v/(2*rt); disc=math.exp(-RATE*t)
    if typ=="CE":
        th=(common-RATE*k*disc*cdf(d2))/YEAR_DAYS; rh=k*t*disc*cdf(d2)/100
    else:
        th=(common+RATE*k*disc*cdf(-d2))/YEAR_DAYS; rh=-k*t*disc*cdf(-d2)/100
    out={"delta":float(dl),"gamma":float(ga),"vega":float(ve),"theta":float(th),"rho":float(rh)}
    return out if all(math.isfinite(x) for x in out.values()) else None

def candidates():
    out=[{"candidate_id":"NO_STOP_REFERENCE","name":"NO STOP","thresholds":{},"aggregation":"NONE","active_count":0}]
    for metric,ts in SWEEP.items():
        for th in ts:
            out.append({"candidate_id":f"{metric.upper()}_{th:g}","name":f"{metric.upper()}={th:g}",
                        "thresholds":{metric:float(th)},"aggregation":"ANY","active_count":1})
    for n in range(2,6):
        for subset in itertools.combinations(METRICS,n):
            ths={m:float(FIXED[m]) for m in subset}
            for agg in ("ANY","ALL"):
                name="+".join(f"{m.upper()}={ths[m]:g}" for m in subset)+f"|{agg}"
                out.append({"candidate_id":"COMBO_"+"_".join(subset)+"_"+agg,"name":name,
                            "thresholds":ths,"aggregation":agg,"active_count":n})
    ids=[x["candidate_id"] for x in out]
    if len(ids)!=72 or len(set(ids))!=72: raise AssertionError(f"Candidate registry should have 72 unique rows, got {len(ids)}")
    return out

def trigger(metrics,ths,agg):
    if not ths: return np.zeros(len(next(iter(metrics.values()))),dtype=bool)
    checks=[]
    for key,th in ths.items():
        x=np.asarray(metrics[key],float)
        checks.append(np.isfinite(x)&(x<=th) if key=="theta" else np.isfinite(x)&(x>=th))
    a=np.vstack(checks)
    return np.any(a,axis=0) if agg=="ANY" else np.all(a,axis=0)

def bootci(values,seed):
    a=np.asarray(values,float)
    if len(a)<2 or not np.isfinite(a).all(): return None,None
    rng=np.random.default_rng(seed); idx=rng.integers(0,len(a),size=(REPS,len(a)))
    b=a[idx].mean(axis=1)
    return float(np.quantile(b,.025)),float(np.quantile(b,.975))

def summary(rows,expected,seed,with_stats):
    if not rows:
        return {"expected_campaigns":expected,"trades":0,"coverage_pct":0.0 if expected else None,
          "gross_pnl_inr":None,"net_pnl_inr":None,"mean_net_trade_inr":None,"median_net_trade_inr":None,
          "return_on_entry_credit_pct":None,"win_rate_pct":None,"profit_factor":None,"max_drawdown_inr":None,
          "stop_hit_rate_pct":None,"paired_uplift_vs_no_stop_inr":None,"paired_uplift_vs_delta050_inr":None,
          "mean_net_ci95_low":None,"mean_net_ci95_high":None,"paired_ci95_low":None,"paired_ci95_high":None,"p_value":None}
    a=np.array([r["net"] for r in rows],float); gp=sum(r["gross"] for r in rows); pos=a[a>0].sum(); neg=-a[a<0].sum()
    dd=np.maximum.accumulate(np.maximum(np.cumsum(a),0))-np.cumsum(a); credits=sum(r["credit"] for r in rows)
    upl=[r["uplift_no_stop"] for r in rows if r["uplift_no_stop"] is not None]
    dupl=[r["uplift_delta050"] for r in rows if r["uplift_delta050"] is not None]
    if with_stats:
        lo,hi=bootci(a,seed); ulo,uhi=bootci(upl,seed+1)
        from scipy.stats import ttest_1samp
        p=float(ttest_1samp(a,0,alternative="greater").pvalue) if len(a)>=2 else None
        if p is not None and not math.isfinite(p): p=None
    else: lo=hi=ulo=uhi=p=None
    return {"expected_campaigns":expected,"trades":len(rows),"coverage_pct":100*len(rows)/expected if expected else 0.,
      "gross_pnl_inr":float(gp),"net_pnl_inr":float(a.sum()),"mean_net_trade_inr":float(a.mean()),"median_net_trade_inr":float(np.median(a)),
      "return_on_entry_credit_pct":100*float(a.sum())/credits if credits else None,"win_rate_pct":100*float(np.mean(a>0)),
      "profit_factor":float(pos/neg) if neg>0 else ("INF" if pos>0 else None),"max_drawdown_inr":float(dd.max()),
      "stop_hit_rate_pct":100*float(np.mean([r["stopped"] for r in rows])),
      "paired_uplift_vs_no_stop_inr":float(sum(upl)) if upl else None,
      "paired_uplift_vs_delta050_inr":float(sum(dupl)) if dupl else None,
      "mean_net_ci95_low":lo,"mean_net_ci95_high":hi,"paired_ci95_low":ulo,"paired_ci95_high":uhi,"p_value":p}

def prep_event(df,spot,expiry,prev,entry_date,sig,lot):
    c,why=base.choose_contract(df,sig,expiry,entry_date,spot)
    if c is None:return None,why
    ent=pd.Timestamp(f"{entry_date} {ENTRY_TIME}",tz=TZ); ex=pd.Timestamp(f"{expiry} {EXIT_TIME}",tz=TZ)
    grid=base.expected_grid(ent,ex,spot)
    if len(grid)<2 or grid[0]!=ent or grid[-1]!=ex:return None,"INVALID_SESSION_GRID"
    op=df.loc[df.option_type.eq(sig["side"])&np.isclose(df.strike.to_numpy(float),float(c["strike"]),rtol=0,atol=1e-9)&df.timestamp.between(ent,ex)].copy()
    if op.timestamp.duplicated(keep=False).any():return None,"CONFLICTING_CONTRACT_MINUTE"
    op=op.set_index("timestamp").reindex(grid)
    if op.open.isna().any() or op.close.isna().any():return None,"INCOMPLETE_OPTION_PATH"
    spots=[spot.get(t) for t in grid]
    if any(x is None for x in spots):return None,"INCOMPLETE_SPOT_PATH"
    if any(not base.valid_ohlc(op.iloc[i]) or not base.valid_ohlc(spots[i]) for i in range(len(grid))):return None,"INVALID_MONITORING_OHLC"
    entryspot=spot.get(ent)
    if entryspot is None:return None,"MISSING_ENTRY_SPOT"
    entry=float(c["entry_price"]); expclose=pd.Timestamp(f"{expiry} {EXPIRY_CLOSE}",tz=TZ)
    tau0=(expclose-ent).total_seconds()/(YEAR_DAYS*86400)
    v0=base.iv_est(float(entryspot["open"]),float(c["strike"]),tau0,entry,sig["side"])
    if v0 is None:return None,"INVALID_ENTRY_IV"
    g0=greeks(float(entryspot["open"]),float(c["strike"]),tau0,v0,sig["side"])
    if g0 is None:return None,"INVALID_ENTRY_GREEKS"
    short_theta=-g0["theta"]
    if not math.isfinite(short_theta) or short_theta<=0:return None,"NONPOSITIVE_ENTRY_SHORT_THETA"
    m={k:[] for k in METRICS}
    for i,ts in enumerate(grid[:-1]):
        tau=(expclose-(ts+pd.Timedelta(minutes=1))).total_seconds()/(YEAR_DAYS*86400)
        s=float(spots[i]["close"]); p=float(op.iloc[i]["close"])
        iv=base.iv_est(s,float(c["strike"]),tau,p,sig["side"])
        if iv is None:return None,"INVALID_MONITORING_IV"
        g=greeks(s,float(c["strike"]),tau,iv,sig["side"])
        if g is None:return None,"INVALID_MONITORING_GREEKS"
        m["delta"].append(abs(g["delta"]))
        m["gamma"].append(abs(g["gamma"])*.5*(.005*s)**2/entry)
        m["vega"].append(abs(g["vega"]*5.0)/entry)
        m["theta"].append((-g["theta"])/short_theta)
        m["rho"].append(abs(g["rho"])/entry)
    return {"event_id":f"{prev}_{expiry}_{entry_date}","previous_expiry":prev,"expiry":expiry,"entry_date":entry_date,
      "split":"development" if expiry<="2023-12-31" else ("validation" if expiry<="2025-12-31" else "holdout"),
      "signal_label":sig["label"],"signal_side":sig["side"],"pivot_date":sig["pivot_date"],"confirmed_date":sig["confirmed_date"],
      "strike":float(c["strike"]),"selection_delta":float(c["selection_delta"]),"entry_delta":float(c["entry_delta"]),
      "entry_price":entry,"entry_ts":ent.isoformat(),"scheduled_exit_price":float(op.iloc[-1]["open"]),
      "scheduled_exit_ts":ex.isoformat(),"scheduled_exit_date":expiry,"lot_size":int(lot),"grid":grid,
      "exit_opens":op.open.to_numpy(float)[1:],"metrics":{k:np.asarray(v,float) for k,v in m.items()}}, "PASS"

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for p in OUT.iterdir():
        if p.is_dir():
            import shutil;shutil.rmtree(p)
        else:p.unlink()
    token=os.getenv("HF_TOKEN"); rev_req=os.getenv("PHASE112_DATASET_REVISION","main") or "main"
    api=HfApi(token=token or None); rev=str(api.dataset_info(repo_id=HF_REPO,revision=rev_req).sha)
    names=api.list_repo_files(repo_id=HF_REPO,repo_type="dataset",revision=rev)
    efiles={}
    for name in names:
        ma=re.fullmatch(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet",name)
        if ma:efiles[ma.group(1)]=name
    expiries=sorted(efiles)
    if len(expiries)<3:raise RuntimeError("Too few expiry files in data revision")
    ipath=Path(hf_hub_download(repo_id=HF_REPO,filename="index/NIFTY.parquet",repo_type="dataset",revision=rev,token=token))
    spot,dups=base.load_index(ipath);daily,incomplete=base.daily_candles(spot)
    if daily.empty:raise RuntimeError("No complete NIFTY daily candles")
    daily_idx={str(x):i for i,x in enumerate(daily.date.tolist())}
    sessions=sorted({t.date().isoformat() for t in spot})
    scheduled=[];excluded=[];manifest=[];events=[]
    for j in range(1,len(expiries)):
        prev,exp=expiries[j-1],expiries[j];gap=(date.fromisoformat(exp)-date.fromisoformat(prev)).days
        if not 4<=gap<=10:continue
        nextdays=[d for d in sessions if date.fromisoformat(d)>date.fromisoformat(prev)]
        eid=f"{prev}_{exp}_{nextdays[0] if nextdays else 'NO_ENTRY'}"
        if not nextdays:excluded.append({"event_id":eid,"expiry":exp,"reason":"NO_NEXT_OBSERVED_SESSION"});continue
        ent=nextdays[0];split="development" if exp<="2023-12-31" else ("validation" if exp<="2025-12-31" else "holdout")
        scheduled.append({"event_id":eid,"previous_expiry":prev,"expiry":exp,"entry_date":ent,"split":split,"gap_days":gap})
        if prev not in daily_idx:excluded.append({"event_id":eid,"expiry":exp,"reason":"PREVIOUS_EXPIRY_DAILY_CANDLE_INCOMPLETE"});continue
        sig=base.signal_asof(daily,prev)
        if sig is None:excluded.append({"event_id":eid,"expiry":exp,"reason":"NO_CONFIRMED_PIVOT_SIGNAL"});continue
        lot=base.lot_size(exp)
        if lot is None:excluded.append({"event_id":eid,"expiry":exp,"reason":"UNSUPPORTED_HISTORICAL_LOT_SIZE_DATE"});continue
        try:
            fp=Path(hf_hub_download(repo_id=HF_REPO,filename=efiles[exp],repo_type="dataset",revision=rev,token=token))
            df,audit=base.normalize_options(fp,exp)
            manifest.append({"expiry":exp,"file":efiles[exp],"sha256":sha256(fp),"bytes":fp.stat().st_size,"status":"PASS",**audit})
            ev,reason=prep_event(df,spot,exp,prev,ent,sig,lot)
            if ev is None:excluded.append({"event_id":eid,"expiry":exp,"reason":reason})
            else:events.append(ev)
            del df;gc.collect()
        except Exception as e:
            manifest.append({"expiry":exp,"file":efiles.get(exp),"status":"ERROR","error_type":type(e).__name__})
            excluded.append({"event_id":eid,"expiry":exp,"reason":"SOURCE_OR_PROCESSING_ERROR","detail":f"{type(e).__name__}: {str(e)[:160]}"})
    cfgs=candidates()
    pd.DataFrame(manifest).to_csv(OUT/"source_manifest.csv",index=False)
    pd.DataFrame(scheduled).to_csv(OUT/"scheduled_campaigns.csv",index=False)
    pd.DataFrame(excluded).to_csv(OUT/"campaign_exclusions.csv",index=False)
    splitnames=("development","validation","holdout")
    sched={s:sum(x["split"]==s for x in scheduled) for s in splitnames}
    elig={s:sum(x["split"]==s for x in events) for s in splitnames}
    exits={}
    for ev in events:
        exits[(ev["event_id"],"NO_STOP_REFERENCE")]={"price":ev["scheduled_exit_price"],"ts":ev["scheduled_exit_ts"],"stopped":False}
        for cfg in cfgs:
            if not cfg["active_count"]:continue
            hits=np.flatnonzero(trigger(ev["metrics"],cfg["thresholds"],cfg["aggregation"]))
            if len(hits)==0:
                exits[(ev["event_id"],cfg["candidate_id"])]={"price":ev["scheduled_exit_price"],"ts":ev["scheduled_exit_ts"],"stopped":False}
            else:
                h=int(hits[0]);grid=ev["grid"]
                if h>=len(ev["exit_opens"]):raise RuntimeError("Stop has no next-minute open; refuse to fabricate fill")
                exits[(ev["event_id"],cfg["candidate_id"])]={"price":float(ev["exit_opens"][h]),"ts":grid[h+1].isoformat(),
                  "stopped":True,"trigger_ts":grid[h].isoformat(),"trigger_delta":float(ev["metrics"]["delta"][h])}
    costs=base.COSTS; primary=next(x for x in costs if x["cost_id"]==PRIMARY_COST_ID)
    no_stop={};delta050=next(x for x in cfgs if x["candidate_id"]=="DELTA_0.5")
    gridrows=[];ledger=[]
    for cost in costs:
        bmap={};dmap={}
        for ev in events:
            b=base.fee_model(ev["entry_price"],ev["scheduled_exit_price"],ev["lot_size"],ev["entry_date"],ev["expiry"],cost)
            bmap[ev["event_id"]]=b
            dex=exits[(ev["event_id"],delta050["candidate_id"])]
            d=base.fee_model(ev["entry_price"],dex["price"],ev["lot_size"],ev["entry_date"],pd.Timestamp(dex["ts"]).date().isoformat(),cost)
            dmap[ev["event_id"]]=d["net_pnl_inr"]
        for split in splitnames:
            se=[e for e in events if e["split"]==split]
            for cfg in cfgs:
                rows=[]
                for ev in se:
                    ex=exits[(ev["event_id"],cfg["candidate_id"])]
                    f=bmap[ev["event_id"]] if not cfg["active_count"] else base.fee_model(
                      ev["entry_price"],ex["price"],ev["lot_size"],ev["entry_date"],pd.Timestamp(ex["ts"]).date().isoformat(),cost)
                    if f is None:raise RuntimeError("Fee model rejected a candidate fill")
                    rows.append({"net":float(f["net_pnl_inr"]),"gross":float(f["gross_pnl_inr"]),
                      "credit":float(f["entry_credit_inr"]),"stopped":ex["stopped"],
                      "uplift_no_stop":float(f["net_pnl_inr"]-bmap[ev["event_id"]]["net_pnl_inr"]) if cfg["active_count"] else None,
                      "uplift_delta050":float(f["net_pnl_inr"]-dmap[ev["event_id"]]) if cfg["candidate_id"]!="DELTA_0.5" else None})
                    if cost["cost_id"]==PRIMARY_COST_ID:
                        ledger.append({"event_id":ev["event_id"],"split":split,"candidate_id":cfg["candidate_id"],"candidate":cfg["name"],
                          "expiry":ev["expiry"],"side":ev["signal_side"],"signal_label":ev["signal_label"],"strike":ev["strike"],
                          "selected_abs_delta":abs(ev["selection_delta"]),"entry_ts":ev["entry_ts"],"exit_ts":ex["ts"],
                          "stop_hit":ex["stopped"],"exit_reason":"GREEK_STOP_NEXT_OPEN" if ex["stopped"] else "SCHEDULED_EXPIRY_EXIT",
                          "trigger_timestamp":ex.get("trigger_ts"),"trigger_delta":ex.get("trigger_delta"),
                          "gross_pnl_inr":f["gross_pnl_inr"],"net_pnl_inr":f["net_pnl_inr"],"total_costs_inr":f["total_costs_inr"],
                          "slippage_cost_inr":f["slippage_cost_inr"],"brokerage_inr":f["brokerage_inr"],"stt_inr":f["stt_inr"],
                          "exchange_fee_inr":f["exchange_fee_inr"],"ipft_inr":f["ipft_inr"],"sebi_fee_inr":f["sebi_fee_inr"],
                          "stamp_duty_inr":f["stamp_duty_inr"],"gst_inr":f["gst_inr"]})
                stats=summary(rows,sched[split],SEED+len(gridrows),cost["cost_id"]==PRIMARY_COST_ID)
                gridrows.append({"split":split,"candidate_id":cfg["candidate_id"],"name":cfg["name"],
                  "active_greeks":"+".join(cfg["thresholds"]) or "NONE","thresholds_json":json.dumps(cfg["thresholds"],sort_keys=True),
                  "aggregation":cfg["aggregation"],**cost,**stats})
    grid=pd.DataFrame(gridrows)
    grid.to_csv(OUT/"candidate_cost_grid.csv",index=False)
    pd.DataFrame(ledger).to_csv(OUT/"campaign_ledger_primary.csv",index=False)
    (OUT/"candidate_registry.json").write_text(json.dumps(cfgs,indent=2)+"\n")
    reason_counts=dict(Counter(x["reason"] for x in excluded))
    sums={"generated_at_utc":now(),"dataset_repo":HF_REPO,"dataset_revision_requested":rev_req,"dataset_revision_resolved_sha":rev,
      "index_sha256":sha256(ipath),"index_bytes":ipath.stat().st_size,"expiry_file_count":len(expiries),"first_expiry":expiries[0],
      "last_expiry":expiries[-1],"complete_daily_candles":int(len(daily)),"incomplete_daily_sessions":int(incomplete),
      "duplicate_index_timestamps":int(dups),"scheduled_campaigns":len(scheduled),"eligible_campaigns":len(events),
      "excluded_campaigns":len(excluded),"scheduled_by_split":sched,"eligible_by_split":elig,"candidate_count":len(cfgs),
      "single_greek_sensitivity_configs":19,"multi_greek_configs":52,"cost_scenarios":len(costs),"grid_rows":len(gridrows),
      "fixed_combo_thresholds":FIXED,"primary_cost_id":PRIMARY_COST_ID,
      "signal_parity":"NOT VERIFIED: causal Python ZigZag proxy; original external ZigLib body not supplied",
      "status":"EMPIRICAL_SCREEN_COMPLETE_NO_PROMOTION" if events else "BLOCKED_NO_VALID_CAMPAIGNS",
      "strategy_promotion":"NONE","tester_review":"WAIVED BY USER"}
    (OUT/"summary.json").write_text(json.dumps(sums,indent=2)+"\n")
    (OUT/"coverage.json").write_text(json.dumps({"scheduled":len(scheduled),"eligible":len(events),"excluded":len(excluded),
      "scheduled_by_split":sched,"eligible_by_split":elig,"exclusion_reasons":reason_counts},indent=2)+"\n")
    figs=[]
    try:
        import matplotlib;matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fd=OUT/"figures";fd.mkdir(parents=True,exist_ok=True)
        prim=grid.loc[grid.cost_id.eq(PRIMARY_COST_ID)]
        for sp in splitnames:
            q=prim.loc[prim.split.eq(sp)].sort_values("net_pnl_inr",ascending=True)
            if q.empty:continue
            fig,ax=plt.subplots(figsize=(13,9)); vals=[float(v) if pd.notna(v) else 0 for v in q.net_pnl_inr]
            ax.barh(q.name.tolist(),vals);ax.axvline(0,linewidth=1);ax.set_xlabel("Net P&L INR (one lot)")
            ax.set_title("Greek stop candidate outcomes: "+sp);fig.tight_layout()
            p=fd/("primary_costs_"+sp+".svg");fig.savefig(p,format="svg");plt.close(fig);figs.append(str(p.relative_to(ROOT)))
    except Exception as e:(OUT/"figure_error.txt").write_text(f"{type(e).__name__}: {e}\n")
    prim=grid.loc[grid.cost_id.eq(PRIMARY_COST_ID)]
    report=["# Phase 112 — Greek Stop-Loss Combination Report","",f"Generated UTC: {sums['generated_at_utc']}",
      f"Status: {sums['status']}; strategy promotion: NONE.","", "## Coverage",
      f"Dataset revision {rev}; expiries {expiries[0]} through {expiries[-1]}.",
      f"Scheduled / eligible / excluded: {len(scheduled)} / {len(events)} / {len(excluded)}.",
      f"Eligible by split: {json.dumps(elig)}; exclusion reasons: {json.dumps(reason_counts,sort_keys=True)}.",
      "", "## Frozen candidate design",
      "72 candidates: 19 single-Greek threshold variations, 52 multi-Greek subset rules (OR/AND), and no-stop baseline.",
      f"Fixed multi-Greek thresholds: {json.dumps(FIXED,sort_keys=True)}. Full thresholds are in PHASE112_RESEARCH_PLAN.md and candidate_registry.json.",
      "Gamma is normalized as a 0.5% spot-shock convexity estimate/entry premium; Vega as 5 IV-points impact/entry premium; Theta relative to entry short-theta; Rho as rate-point sensitivity/entry premium.",
      "Every completed-minute trigger fills at next exact observed minute open. The 24 cost scenarios include date-effective modeled charges and slippage.",
      "", "## Primary cost case B20_S0.25_F1.0",
      "| Split | Candidate | Trades/expected | Net P&L ₹ | Mean ₹ | Win % | Max DD ₹ | Stop % | Uplift vs no-stop ₹ |",
      "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for sp in splitnames:
        for cid in ("NO_STOP_REFERENCE","DELTA_0.5"):
            q=prim.loc[(prim.split.eq(sp))&(prim.candidate_id.eq(cid))]
            if len(q):
                r=q.iloc[0]; up="—" if pd.isna(r.paired_uplift_vs_no_stop_inr) else f"{r.paired_uplift_vs_no_stop_inr:.2f}"
                report.append(f"| {sp} | {r['name']} | {int(r.trades)}/{int(r.expected_campaigns)} | {r.net_pnl_inr:.2f} | {r.mean_net_trade_inr:.2f} | {r.win_rate_pct:.1f} | {r.max_drawdown_inr:.2f} | {r.stop_hit_rate_pct:.1f} | {up} |")
    report += ["","Full 72 × 24 × 3 rows are in candidate_cost_grid.csv. Primary-cost campaign records are in campaign_ledger_primary.csv.",
      "Holdout is not used to select a winner. Bootstrap intervals and one-sided tests are descriptive only and the grid creates multiple-comparison risk.",
      "", "## Decision and limitations",
      "No strategy is promoted. The supplied Pine source imports external DevLucem/ZigLib/1, whose library body was not provided; the Python pivot engine remains a causal proxy. Minute Black–Scholes Greeks, fixed rate/yield, partial CC BY-NC 4.0 option data, OHLC simulated fills and approximate Paytm Money cost assumptions limit conclusions. A sparse holdout or nominal p-value is not proof of an edge.",
      "", "## Artifacts","- summary.json, coverage.json, candidate_registry.json, source_manifest.csv, scheduled_campaigns.csv, campaign_exclusions.csv",
      "- candidate_cost_grid.csv and campaign_ledger_primary.csv",*[f"- {p}" for p in figs]]
    (OUT/"PHASE112_REPORT.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    manuscript="""# Phase 112 Research Manuscript — Greek Stop-Loss Combinations

## Abstract
This fixed-rule experiment tests five Greek stop features for single-leg weekly NIFTY options chosen from a daily ZigZag-style pivot. It compares single-Greek thresholds and every multi-Greek subset with OR/AND triggers against Delta-only and no-stop references after modeled costs. The original TradingView ZigLib source is not embedded in the Pine provided; all results remain proxy-based and no candidate is promoted.

## Research question, aim and objectives
Determine whether Gamma, Vega, Theta or Rho adds value to the existing Delta stop. Keep entry, selection, timestamp rules and scheduled exit frozen. Test all 72 candidates with 24 fee/slippage cases and chronological splits.

## Methodology
Confirmed HL/LL sells a PE; HH/LH sells a CE. Select closest valid absolute delta 0.10 from the exact 09:59 close; enter exact 10:00 open next session after prior expiry. Exit scheduled expiry day at 10:00. A completed-minute close triggers a stop, filled on the next observed minute open. Greeks are inferred from European Black–Scholes at 6% rate and zero dividend. Gamma and Vega are normalized to entry premium and preset shocks; Theta is relative to initial short-theta; Rho is a 1-percentage-point rate sensitivity fraction. No interpolation or invented fill is permitted.

## Statistical analysis
Report development (through 2023), validation (2024–2025), and available holdout (2026 onward). Full candidate-by-cost outcomes and primary-cost trade ledger are machine-readable. Bootstrap CIs and p-values are descriptive, not proof; multiple comparisons and serial dependence limit inference. Holdout is not ranked.

## Results
See PHASE112_REPORT.md, candidate_cost_grid.csv, coverage.json and campaign_exclusions.csv. Empty estimates are null, not measured zero-return outcomes.

## Discussion
Additional Greeks can stop a losing option earlier but can also truncate profitable theta decay. Gamma/Vega shock proxies and Rho sensitivity are model definitions, not validated execution-risk quantities. Rho may rarely trigger on short weekly maturities. OHLC fills, constant volatility/rate assumptions, data coverage selection and the missing ZigLib source limit strategy-specific claims.

## Strengths and limitations
Strengths: frozen signal, exact time joins, five Greeks, all subsets, OR/AND logic, fixed thresholds, 24 cost scenarios and matched no-stop comparisons. Limitations: unverified indicator parity, model Greeks, partial option source, simulated fills, multiple-comparison risk and sparse holdout.

## Conclusion and future direction
Do not promote a stop rule from this exploratory replay alone. Any follow-up should be bounded and use confirmed TradingView label fixtures and stronger quote data without re-tuning against holdout.
"""
    (OUT/"PHASE112_MANUSCRIPT.md").write_text(manuscript,encoding="utf-8")
    print(json.dumps({"status":sums["status"],"revision":rev,"scheduled":len(scheduled),"eligible":len(events),
      "excluded":len(excluded),"candidates":len(cfgs),"costs":len(costs),"grid_rows":len(gridrows)},indent=2))
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/"runtime_error.json").write_text(json.dumps({"status":"RUNTIME_ERROR","created_at_utc":now(),
          "error_type":type(e).__name__,"error":str(e)[:1600]},indent=2)+"\n",encoding="utf-8")
        raise
