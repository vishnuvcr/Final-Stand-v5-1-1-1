import ast
import json
import math
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
HOLDOUT_END = pd.Timestamp("2026-12-31", tz=TZ)
OUT = Path("results/phase47_vix_source")
OUT.mkdir(parents=True, exist_ok=True)

# S1 is a newly testable four-leg calendar structure.
# S2 is the Profit Breakout monthly wide-range hedge reconstruction.
# S3 is an option-only proxy for the channel's Covered Call 2.0 because
# the source strategy explicitly requires a futures leg.
PRIMARY_STRATEGIES = [
    "double_calendar_straddle",
    "monthly_wide_range_hedge",
    "covered_call_2_proxy",
]
S2_SENSITIVITY = [0.25, 0.30, 0.35]

STATES = ["ALL", "LOW", "NORMAL", "HIGH", "SPIKE", "FALLING", "RISING", "HIGH_RISING"]

def as_tz(x):
    t = pd.Timestamp(x)
    return t.tz_localize(TZ) if t.tzinfo is None else t.tz_convert(TZ)

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
    d = as_tz(d)
    stt = 0.0015 if d >= pd.Timestamp("2026-04-01", tz=TZ) else 0.0010 if d >= pd.Timestamp("2024-10-01", tz=TZ) else 0.000625
    txn, ipft = (
        (0.000355299, 0.000000001) if d >= pd.Timestamp("2026-03-01", tz=TZ)
        else (0.0003503, 0.000005) if d >= pd.Timestamp("2024-10-01", tz=TZ)
        else (0.000495, 0.000005)
    )
    return stt, txn, 0.000001, ipft, 0.00003

def exec_px(px, action):
    slip = TICK
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
        if side == "sell":
            stt += sr * turnover * mult
        else:
            stamp += sd * turnover * mult
    gst = 0.18 * (brokerage + exchange + sebi + ipft)
    return brokerage + exchange + sebi + ipft + stt + stamp + gst

def load_index():
    p = hf_hub_download(repo_id=HF_REPO, filename="index/NIFTY.parquet",
                        repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
    df = pd.read_parquet(p, columns=["timestamp", "close"])
    ts = pd.to_datetime(df["timestamp"])
    df["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    return df.rename(columns={"close": "spot"}).drop_duplicates("timestamp").sort_values("timestamp")

def load_vix():
    x = pd.read_csv("data/phase40_vix/india_vix.csv")
    dc = next(c for c in x.columns if c.lower() == "date")
    cc = next(c for c in x.columns if c.lower() == "close")
    x["date"] = pd.to_datetime(x[dc]).dt.tz_localize(TZ)
    x["vix"] = pd.to_numeric(x[cc], errors="coerce")
    x = x[["date", "vix"]].dropna().drop_duplicates("date").sort_values("date")
    x["dvix"] = x["vix"].diff()
    return x

def state_flags(vix, entry_ts):
    prior = vix[vix["date"] < entry_ts.normalize()]
    if len(prior) < 60:
        return []
    cur = prior.iloc[-1]
    hist = prior.iloc[:-1]
    q25, q75 = hist["vix"].quantile(0.25), hist["vix"].quantile(0.75)
    d = hist["dvix"].dropna()
    pos = d[d > 0]
    dv = float(cur["dvix"]) if np.isfinite(cur["dvix"]) else np.nan
    out = ["ALL"]
    if float(cur["vix"]) <= q25:
        out.append("LOW")
    elif float(cur["vix"]) >= q75:
        out.append("HIGH")
    else:
        out.append("NORMAL")
    if len(pos) >= 20 and np.isfinite(dv) and dv >= pos.quantile(0.90):
        out.append("SPIKE")
    if len(d) >= 20 and np.isfinite(dv) and dv >= d.quantile(0.90):
        out.append("RISING")
    if len(d) >= 20 and np.isfinite(dv) and dv <= d.quantile(0.10):
        out.append("FALLING")
    if "HIGH" in out and "RISING" in out:
        out.append("HIGH_RISING")
    return sorted(set(out))

def prepare(df):
    z = df.copy()
    z["option_type"] = z["option_type"].astype(str).str.upper()
    z["strike"] = pd.to_numeric(z["strike"], errors="coerce")
    z["close"] = pd.to_numeric(z["close"], errors="coerce")
    ts = pd.to_datetime(z["timestamp"])
    z["timestamp"] = ts.dt.tz_localize(TZ) if ts.dt.tz is None else ts.dt.tz_convert(TZ)
    return z.dropna(subset=["timestamp", "option_type", "strike", "close"]).sort_values(
        ["timestamp", "option_type", "strike"], kind="stable"
    )

_FILE_CACHE = {}

def load_expiry(expiry, entry_ts=None, extra_day=None):
    expiry = as_tz(expiry)
    key = (expiry.date().isoformat(), str(entry_ts) if entry_ts is not None else None, str(extra_day) if extra_day is not None else None)
    if key in _FILE_CACHE:
        return _FILE_CACHE[key]
    file_key = expiry.date().isoformat()
    name = f"options/NIFTY/{file_key}.parquet"
    path = hf_hub_download(repo_id=HF_REPO, filename=name,
                           repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
    # Exact observed data only. Read just entry/exit windows when possible.
    tables = []
    windows = []
    if entry_ts is not None:
        windows.append((pd.Timestamp(entry_ts) - pd.Timedelta(minutes=1),
                        pd.Timestamp(entry_ts) + pd.Timedelta(minutes=1)))
    if extra_day is not None:
        day = pd.Timestamp(extra_day).normalize()
        windows.append((day, day + pd.Timedelta(hours=15, minutes=29)))
    else:
        windows.append((expiry.normalize(), expiry.normalize() + pd.Timedelta(hours=15, minutes=29)))
    try:
        for lo, hi in windows:
            try:
                t = pq.read_table(
                    path,
                    columns=["timestamp", "option_type", "strike", "close"],
                    filters=[("timestamp", ">=", lo.to_pydatetime()),
                             ("timestamp", "<=", hi.to_pydatetime())],
                )
                if t.num_rows:
                    tables.append(t.to_pandas())
            except Exception:
                pass
    except Exception:
        tables = []
    if not tables:
        z = prepare(pd.read_parquet(path, columns=["timestamp", "option_type", "strike", "close"]))
    else:
        z = prepare(pd.concat(tables, ignore_index=True))
    _FILE_CACHE[key] = z
    return z

def clear_cache_except(keys):
    for k in list(_FILE_CACHE):
        if k not in keys:
            del _FILE_CACHE[k]

def split_for(expiry):
    e = as_tz(expiry)
    if e <= DEV_END:
        return "development"
    if e <= VAL_END:
        return "validation"
    return "holdout"

def monthly_expiries(expiries):
    d = pd.DataFrame({"expiry": sorted(as_tz(x) for x in expiries)})
    d["ym"] = d.expiry.dt.to_period("M").astype(str)
    return list(d.groupby("ym")["expiry"].max().sort_values())

def entry_four_dte(index, expiry):
    e = as_tz(expiry).normalize()
    days = sorted(pd.Series(index["timestamp"].dt.normalize().unique()).tolist())
    prior = [d for d in days if d < e]
    if len(prior) < 4:
        return None
    return as_tz(prior[-4]) + pd.Timedelta(hours=10)

def entry_after_expiry(index, expiry):
    e = as_tz(expiry).normalize()
    days = sorted(pd.Series(index["timestamp"].dt.normalize().unique()).tolist())
    nxt = [d for d in days if d > e]
    if not nxt:
        return None
    return as_tz(nxt[0]) + pd.Timedelta(hours=10)

def find_next_expiry(expiries, expiry):
    es = sorted(as_tz(x) for x in expiries)
    e = as_tz(expiry)
    for x in es:
        if x > e:
            return x
    return None

def exact_row(snap, typ, strike):
    x = snap[(snap["option_type"] == typ) & (np.isclose(snap["strike"], strike, rtol=0, atol=1e-8))]
    if x.empty:
        return None
    return float(x.iloc[-1]["close"])

def common_exit_price(cur, entry_day, legs):
    # legs contains (expiry_key, typ, strike, qty)
    series = []
    for expiry_key, typ, strike, qty in legs:
        z = cur[expiry_key]
        day = pd.Timestamp(entry_day).normalize()
        s = z[(z["option_type"] == typ) &
              (np.isclose(z["strike"], strike, rtol=0, atol=1e-8)) &
              (z["timestamp"] >= day) &
              (z["timestamp"] <= day + pd.Timedelta(hours=15, minutes=29))]
        if s.empty:
            return None
        series.append(s.drop_duplicates("timestamp").set_index("timestamp")["close"])
    common = series[0].index
    for s in series[1:]:
        common = common.intersection(s.index)
        if len(common) == 0:
            return None
    exit_ts = common.max()
    prices = [float(s.loc[exit_ts]) for s in series]
    return exit_ts, prices

def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def bs_delta(spot, strike, t_years, sigma, typ):
    if not (spot > 0 and strike > 0 and t_years > 0 and sigma > 0):
        return np.nan
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * t_years) / (sigma * math.sqrt(t_years))
    if typ == "CE":
        return norm_cdf(d1)
    return norm_cdf(d1) - 1.0

def choose_delta_strike(snap, spot, sigma, expiry, entry_ts, typ, target_abs_delta):
    T = max((pd.Timestamp(expiry) - pd.Timestamp(entry_ts)).total_seconds() / (365.0 * 24 * 3600), 1e-8)
    z = snap[snap["option_type"] == typ].copy()
    if z.empty:
        return None
    target = target_abs_delta if typ == "CE" else -target_abs_delta
    z["delta"] = z["strike"].apply(
        lambda k: bs_delta(spot, float(k), T, sigma, typ)
    )
    z["err"] = (z["delta"] - target).abs()
    z = z.replace([np.inf, -np.inf], np.nan).dropna(subset=["err", "close"])
    if z.empty:
        return None
    return float(z.sort_values(["err", "strike"]).iloc[0]["strike"])

def choose_parity_strike(snap, prefer_spot):
    c = snap[snap["option_type"] == "CE"][["strike", "close"]].rename(columns={"close": "ce"})
    p = snap[snap["option_type"] == "PE"][["strike", "close"]].rename(columns={"close": "pe"})
    z = c.merge(p, on="strike", how="inner")
    if z.empty:
        return None
    z["premium_gap"] = (z["ce"] - z["pe"]).abs()
    z["spot_gap"] = (z["strike"] - prefer_spot).abs()
    return float(z.sort_values(["premium_gap", "spot_gap"]).iloc[0]["strike"])

def build_result(legs, books, entry_ts, exit_ts, lot):
    # legs: [(book, typ, strike, qty)]
    gross = 0.0
    orders = []
    for (book, typ, strike, qty), ep in zip(legs, books["entry_prices"]):
        xp = books["exit_prices"].pop(0)
        epx = exec_px(ep, "buy" if qty > 0 else "sell")
        xpx = exec_px(xp, "buy" if qty < 0 else "sell")
        gross += qty * (xpx - epx) * lot
        orders.append((entry_ts, "buy" if qty > 0 else "sell", epx * abs(qty)))
        orders.append((exit_ts, "buy" if qty < 0 else "sell", xpx * abs(qty)))
    c = charges(orders, lot, 1.0)
    c50 = charges(orders, lot, 1.5)
    return {"gross": gross, "cost": c, "net": gross - c, "net50": gross - c50,
            "orders": len(orders)}

def evaluate_legs(files, entry_ts, exit_day, legs):
    # legs: list of (expiry_key, typ, strike, qty)
    entry_prices = []
    for key, typ, strike, qty in legs:
        snap = files[key][files[key]["timestamp"] == entry_ts]
        px = exact_row(snap, typ, strike)
        if px is None:
            return None
        entry_prices.append(px)
    ex = common_exit_price(files, exit_day, legs)
    if ex is None:
        return None
    exit_ts, exit_prices = ex
    books = {"entry_prices": entry_prices, "exit_prices": list(exit_prices)}
    r = build_result(legs, books, entry_ts, exit_ts, lot_size_for_expiry(pd.Timestamp(legs[0][0] + "-01-01", tz=TZ)) if False else 1)
    return r, exit_ts, exit_prices

def strategy_trade_double_calendar(expiry, next_expiry, index, vix):
    entry_ts = entry_four_dte(index, expiry)
    if entry_ts is None:
        return None
    spotrow = index[index["timestamp"] == entry_ts]
    if spotrow.empty:
        return None
    spot = float(spotrow.iloc[-1]["spot"])
    cur = load_expiry(expiry, entry_ts, expiry)
    nxt = load_expiry(next_expiry, entry_ts, expiry)
    snap = cur[cur["timestamp"] == entry_ts]
    snapn = nxt[nxt["timestamp"] == entry_ts]
    if snap.empty or snapn.empty:
        return None
    atm = float(min(snap["strike"].unique(), key=lambda k: abs(float(k) - spot)))
    if exact_row(snap, "CE", atm) is None or exact_row(snap, "PE", atm) is None:
        return None
    if exact_row(snapn, "CE", atm) is None or exact_row(snapn, "PE", atm) is None:
        return None
    files = {"cur": cur, "nxt": nxt}
    legs = [
        ("cur", "CE", atm, -1), ("cur", "PE", atm, -1),
        ("nxt", "CE", atm, 1), ("nxt", "PE", atm, 1),
    ]
    entry_prices = [exact_row(cur if k=="cur" else nxt, t, s) for k,t,s,q in legs]
    if any(x is None for x in entry_prices):
        return None
    ex = common_exit_price(files, expiry, legs)
    if ex is None:
        return None
    exit_ts, exit_prices = ex
    lot = lot_size_for_expiry(expiry)
    gross = 0.0
    orders = []
    for leg, ep, xp in zip(legs, entry_prices, exit_prices):
        _, typ, strike, qty = leg
        epx = exec_px(ep, "buy" if qty > 0 else "sell")
        xpx = exec_px(xp, "buy" if qty < 0 else "sell")
        gross += qty * (xpx-epx) * lot
        orders += [(entry_ts, "buy" if qty > 0 else "sell", epx),
                   (exit_ts, "buy" if qty < 0 else "sell", xpx)]
    c=charges(orders, lot, 1.0)
    c50=charges(orders, lot, 1.5)
    return {"strategy":"double_calendar_straddle","expiry":str(expiry.date()),"entry_ts":str(entry_ts),
            "exit_ts":str(exit_ts),"net":gross-c,"net50":gross-c50,"gross":gross,"cost":c,
            "lot":lot,"legs":4,"source_exactness":"mechanical_proxy"}

def strategy_trade_mwh(expiry, next_expiry, index, vix, target_delta):
    entry_ts = entry_after_expiry(index, pd.Timestamp(expiry) - pd.offsets.MonthBegin(1))
    # The target current expiry is one monthly cycle after the prior monthly expiry.
    # Caller passes a monthly expiry and its predecessor.
    if entry_ts is None:
        return None
    # Recompute state from exact entry date.
    spotrow = index[index["timestamp"] == entry_ts]
    if spotrow.empty:
        return None
    spot = float(spotrow.iloc[-1]["spot"])
    prior = vix[vix["date"] < entry_ts.normalize()]
    if prior.empty:
        return None
    sigma = float(prior.iloc[-1]["vix"]) / 100.0
    cur = load_expiry(expiry, entry_ts, expiry)
    nxt = load_expiry(next_expiry, entry_ts, expiry)
    snap = cur[cur["timestamp"] == entry_ts]
    snapn = nxt[nxt["timestamp"] == entry_ts]
    if snap.empty or snapn.empty:
        return None
    ce = choose_delta_strike(snap, spot, sigma, expiry, entry_ts, "CE", target_delta)
    pe = choose_delta_strike(snap, spot, sigma, expiry, entry_ts, "PE", target_delta)
    h = choose_parity_strike(snapn, spot)
    if ce is None or pe is None or h is None:
        return None
    strikes = [("cur","CE",ce,-1),("cur","PE",pe,-1),("nxt","CE",h,1),("nxt","PE",h,1)]
    files={"cur":cur,"nxt":nxt}
    eps=[]
    for key,t,s,q in strikes:
        snapx=files[key][files[key]["timestamp"]==entry_ts]
        px=exact_row(snapx,t,s)
        if px is None:
            return None
        eps.append(px)
    ex=common_exit_price(files, expiry, strikes)
    if ex is None:
        return None
    exit_ts, xps = ex
    lot=lot_size_for_expiry(expiry)
    gross=0.0
    orders=[]
    for leg,ep,xp in zip(strikes,eps,xps):
        key,t,s,q=leg
        epx=exec_px(ep,"buy" if q>0 else "sell")
        xpx=exec_px(xp,"buy" if q<0 else "sell")
        gross += q*(xpx-epx)*lot
        orders += [(entry_ts,"buy" if q>0 else "sell",epx),
                   (exit_ts,"buy" if q<0 else "sell",xpx)]
    c=charges(orders,lot,1.0)
    c50=charges(orders,lot,1.5)
    return {"strategy":"monthly_wide_range_hedge","expiry":str(expiry.date()),"entry_ts":str(entry_ts),
            "exit_ts":str(exit_ts),"net":gross-c,"net50":gross-c50,"gross":gross,"cost":c,
            "lot":lot,"legs":4,"delta_target":target_delta,"source_exactness":"delta_proxy"}

def strategy_trade_cc2(expiry, next_expiry, index, vix):
    entry_ts = entry_four_dte(index, expiry)
    if entry_ts is None:
        return None
    spotrow=index[index["timestamp"]==entry_ts]
    if spotrow.empty:
        return None
    spot=float(spotrow.iloc[-1]["spot"])
    prior=vix[vix["date"]<entry_ts.normalize()]
    if prior.empty:
        return None
    sigma=float(prior.iloc[-1]["vix"])/100.0
    cur=load_expiry(expiry,entry_ts,expiry)
    nxt=load_expiry(next_expiry,entry_ts,expiry)
    snap=cur[cur["timestamp"]==entry_ts]
    snapn=nxt[nxt["timestamp"]==entry_ts]
    if snap.empty or snapn.empty:
        return None
    atm=float(min(snap["strike"].unique(), key=lambda k:abs(float(k)-spot)))
    put30=choose_delta_strike(snap,spot,sigma,expiry,entry_ts,"PE",0.30)
    call30=choose_delta_strike(snap,spot,sigma,expiry,entry_ts,"CE",0.30)
    nextcall=choose_delta_strike(snapn,spot,sigma,next_expiry,entry_ts,"CE",0.30)
    if any(x is None for x in [atm,put30,call30,nextcall]):
        return None
    legs=[("cur","CE",atm,1),("cur","PE",atm,-1),("cur","PE",put30,1),
          ("cur","CE",call30,-1),("nxt","CE",nextcall,-1)]
    files={"cur":cur,"nxt":nxt}
    eps=[]
    for key,t,s,q in legs:
        px=exact_row(files[key][files[key]["timestamp"]==entry_ts],t,s)
        if px is None: return None
        eps.append(px)
    ex=common_exit_price(files,expiry,legs)
    if ex is None: return None
    exit_ts,xps=ex
    lot=lot_size_for_expiry(expiry)
    gross=0.0
    orders=[]
    for leg,ep,xp in zip(legs,eps,xps):
        key,t,s,q=leg
        epx=exec_px(ep,"buy" if q>0 else "sell")
        xpx=exec_px(xp,"buy" if q<0 else "sell")
        gross += q*(xpx-epx)*lot
        orders += [(entry_ts,"buy" if q>0 else "sell",epx),
                   (exit_ts,"buy" if q<0 else "sell",xpx)]
    c=charges(orders,lot,1.0)
    c50=charges(orders,lot,1.5)
    return {"strategy":"covered_call_2_proxy","expiry":str(expiry.date()),"entry_ts":str(entry_ts),
            "exit_ts":str(exit_ts),"net":gross-c,"net50":gross-c50,"gross":gross,"cost":c,
            "lot":lot,"legs":5,"source_exactness":"synthetic_future_proxy",
            "put_delta_target":0.30,"call_delta_target":0.30}

def drawdown(vals):
    a=np.asarray(vals,float)
    if len(a)==0:
        return 0.0
    c=np.cumsum(a)
    return float(np.max(np.maximum.accumulate(c)-c))

def pf(vals):
    a=np.asarray(vals,float)
    pos=a[a>0].sum()
    neg=-a[a<0].sum()
    return float(pos/neg) if neg>0 else (np.inf if pos>0 else np.nan)

def parse_states(x):
    if isinstance(x,list):
        return x
    try:
        return json.loads(x)
    except Exception:
        try:
            return ast.literal_eval(x)
        except Exception:
            return []

def regime_test(z,state,seed=4701):
    a=z[z.active_states.apply(lambda x: state in parse_states(x))].net.to_numpy(float)
    b=z[z.active_states.apply(lambda x: state not in parse_states(x))].net.to_numpy(float)
    if len(a)<10 or len(b)<10:
        return {"n_active":len(a),"n_rest":len(b),"diff_mean":np.nan,"ci_lo":np.nan,"ci_hi":np.nan,"p":np.nan}
    rng=np.random.default_rng(seed)
    ia=rng.integers(0,len(a),size=(10000,len(a)))
    ib=rng.integers(0,len(b),size=(10000,len(b)))
    boots=a[ia].mean(axis=1)-b[ib].mean(axis=1)
    pooled=np.concatenate([a,b])
    n1=len(a)
    obs=a.mean()-b.mean()
    perms=np.empty(10000)
    for i in range(10000):
        p=rng.permutation(pooled)
        perms[i]=p[:n1].mean()-p[n1:].mean()
    return {"n_active":len(a),"n_rest":len(b),"diff_mean":float(obs),
            "ci_lo":float(np.quantile(boots,.025)),"ci_hi":float(np.quantile(boots,.975)),
            "p":float(np.mean(perms>=obs))}

def holm(ps):
    p=np.asarray(ps,float)
    order=np.argsort(np.nan_to_num(p,nan=1.0))
    out=np.ones(len(p))
    running=0.0
    for rank,i in enumerate(order):
        running=max(running,min(1.0,(len(p)-rank)*(p[i] if np.isfinite(p[i]) else 1.0)))
        out[i]=running
    return out

def audit_source_files(index, expiries):
    required = Path("data/phase40_vix/india_vix.csv")
    if not required.exists() or required.stat().st_size == 0:
        raise RuntimeError("F47-001 missing India VIX file")
    if index.empty or len(expiries)<20:
        raise RuntimeError("F47-002 insufficient index/expiry universe")
    # Verify representative current, next and monthly files exist and parse.
    m=monthly_expiries(expiries)
    sample=set()
    for e in m[:2]+m[-2:]:
        sample.add(e.date().isoformat())
        ne=find_next_expiry(m,e)
        if ne: sample.add(ne.date().isoformat())
    es=sorted(expiries)
    sample.update(x.date().isoformat() for x in es[:2]+es[-2:])
    for key in sorted(sample):
        name=f"options/NIFTY/{key}.parquet"
        p=hf_hub_download(repo_id=HF_REPO, filename=name,
                          repo_type="dataset", token=os.getenv("HF_TOKEN") or None)
        z=prepare(pd.read_parquet(p,columns=["timestamp","option_type","strike","close"]))
        if z.empty:
            raise RuntimeError(f"F47-003 empty option file {key}")
        if not {"CE","PE"}.issubset(set(z.option_type.unique())):
            raise RuntimeError(f"F47-004 missing CE/PE in {key}")
    return {"sample_files_checked":len(sample),"monthly_expiries":len(m)}

def main():
    # ---------------- PRE-FLIGHT ----------------
    index=load_index()
    vix=load_vix()
    base=Path("results/phase43_vix/strategy_trade_matrix_all_splits.csv")
    if not base.exists():
        raise RuntimeError("F47-005 accepted Phase-43 strategy matrix missing")
    bz=pd.read_csv(base)
    ts=pd.to_datetime(bz["entry_ts"])
    if ts.dt.tz is None:
        ts=ts.dt.tz_localize(TZ)
    bz["entry_ts"]=ts
    expiries=sorted(pd.to_datetime(bz["expiry"]).dt.tz_localize(TZ).drop_duplicates().tolist())
    preflight=audit_source_files(index,expiries)
    (OUT/"preflight.json").write_text(json.dumps(preflight,indent=2))
    monthly=monthly_expiries(expiries)
    if len(monthly)<20:
        raise RuntimeError("F47-006 fewer than 20 monthly expiries")
    # Definition audit.
    assert PRIMARY_STRATEGIES == ["double_calendar_straddle","monthly_wide_range_hedge","covered_call_2_proxy"]
    (OUT/"definition_audit.json").write_text(json.dumps({
        "strategies":PRIMARY_STRATEGIES,
        "monthly_delta_sensitivity":S2_SENSITIVITY,
        "holdout_start":"2026-01-01",
        "all_vix_states":STATES
    },indent=2))
    # ---------------- NUMERICAL EXECUTION ----------------
    rows=[]
    errors=[]
    # S1 monthly.
    for i,e in enumerate(monthly[:-1]):
        ne=find_next_expiry(monthly,e)
        if ne is None: continue
        try:
            r=strategy_trade_double_calendar(e,ne,index,vix)
            if r:
                r["split"]=split_for(e)
                r["active_states"]=json.dumps(state_flags(vix,pd.Timestamp(r["entry_ts"])))
                rows.append(r)
        except Exception as ex:
            errors.append({"strategy":"double_calendar_straddle","expiry":str(e.date()),"error":repr(ex)})
        clear_cache_except(set())
        if i%5==0:
            pd.DataFrame(rows).to_csv(OUT/"progress.csv",index=False)

    # S2 primary + sensitivity, using predecessor monthly expiry for entry.
    for i,e in enumerate(monthly[:-1]):
        ne=find_next_expiry(monthly,e)
        prev=monthly[i-1] if i>0 else None
        if ne is None or prev is None: continue
        entry=entry_after_expiry(index,prev)
        if entry is None: continue
        # Override the helper's entry inference by recording an exact expected entry; use a
        # local implementation to keep the registered S2 entry definition explicit.
        spotrow=index[index.timestamp==entry]
        if spotrow.empty: continue
        for td in S2_SENSITIVITY:
            try:
                spot=float(spotrow.iloc[-1].spot)
                prior=vix[vix.date < entry.normalize()]
                sigma=float(prior.iloc[-1].vix)/100.0
                cur=load_expiry(e,entry,e)
                nxt=load_expiry(ne,entry,e)
                snap=cur[cur.timestamp==entry]
                snapn=nxt[nxt.timestamp==entry]
                ce=choose_delta_strike(snap,spot,sigma,e,entry,"CE",td)
                pe=choose_delta_strike(snap,spot,sigma,e,entry,"PE",td)
                h=choose_parity_strike(snapn,spot)
                if any(x is None for x in [ce,pe,h]):
                    continue
                legs=[("cur","CE",ce,-1),("cur","PE",pe,-1),("nxt","CE",h,1),("nxt","PE",h,1)]
                eps=[exact_row((cur if k=="cur" else nxt)[(cur if k=="cur" else nxt).timestamp==entry],t,s) for k,t,s,q in legs]
                if any(x is None for x in eps): continue
                ex=common_exit_price({"cur":cur,"nxt":nxt},e,legs)
                if ex is None: continue
                exit_ts,xps=ex
                lot=lot_size_for_expiry(e)
                gross=0.0; orders=[]
                for leg,ep,xp in zip(legs,eps,xps):
                    _,t,s,q=leg
                    epx=exec_px(ep,"buy" if q>0 else "sell")
                    xpx=exec_px(xp,"buy" if q<0 else "sell")
                    gross += q*(xpx-epx)*lot
                    orders += [(entry,"buy" if q>0 else "sell",epx),
                               (exit_ts,"buy" if q<0 else "sell",xpx)]
                c=charges(orders,lot,1.0); c50=charges(orders,lot,1.5)
                rows.append({"strategy":"monthly_wide_range_hedge",
                             "expiry":str(e.date()),"entry_ts":str(entry),"exit_ts":str(exit_ts),
                             "split":split_for(e),"net":gross-c,"net50":gross-c50,"gross":gross,
                             "cost":c,"lot":lot,"legs":4,"delta_target":td,
                             "active_states":json.dumps(state_flags(vix,entry)),
                             "source_exactness":"delta_proxy"})
            except Exception as ex:
                errors.append({"strategy":"monthly_wide_range_hedge","expiry":str(e.date()),
                               "delta_target":td,"error":repr(ex)})
            clear_cache_except(set())

    # S3 weekly proxy.
    es=expiries
    for i,e in enumerate(es[:-1]):
        ne=es[i+1]
        try:
            r=strategy_trade_cc2(e,ne,index,vix)
            if r:
                r["split"]=split_for(e)
                r["active_states"]=json.dumps(state_flags(vix,pd.Timestamp(r["entry_ts"])))
                rows.append(r)
        except Exception as ex:
            errors.append({"strategy":"covered_call_2_proxy","expiry":str(e.date()),"error":repr(ex)})
        clear_cache_except(set())
        if i%20==0:
            pd.DataFrame(rows).to_csv(OUT/"progress.csv",index=False)

    trade=pd.DataFrame(rows)
    if trade.empty:
        raise RuntimeError("F47-007 no numerical rows generated")
    trade["strategy"]=trade.strategy.astype(str)
    trade["expiry"]=trade.expiry.astype(str)
    trade["entry_ts"]=pd.to_datetime(trade.entry_ts)
    trade["active_states"]=trade.active_states.fillna("[]")
    trade.to_csv(OUT/"source_strategy_trade_matrix.csv",index=False)
    pd.DataFrame(errors).to_csv(OUT/"data_errors.csv",index=False)

    # ---------------- ARTIFACT AUDIT ----------------
    dup=trade.duplicated(["strategy","expiry","entry_ts","delta_target"],keep=False)
    if dup.any():
        raise RuntimeError(f"F47-008 duplicate trade keys: {int(dup.sum())}")
    bad_split=trade[(trade.expiry >= "2026-01-01") & (trade.split != "holdout")]
    if not bad_split.empty:
        raise RuntimeError("F47-009 holdout split contamination")
    bad_pre=trade[(trade.expiry < "2024-01-01") & (trade.split != "development")]
    if not bad_pre.empty:
        raise RuntimeError("F47-010 development split contamination")
    missing_states=trade[trade.active_states.apply(lambda x: not isinstance(parse_states(x),list) or "ALL" not in parse_states(x))]
    if not missing_states.empty:
        raise RuntimeError("F47-011 missing ALL state labels")
    audit={"rows":int(len(trade)),"strategies":sorted(trade.strategy.unique().tolist()),
           "duplicate_keys":int(dup.sum()),"holdout_rows":int((trade.split=="holdout").sum()),
           "development_rows":int((trade.split=="development").sum()),
           "validation_rows":int((trade.split=="validation").sum()),
           "errors":int(len(errors))}
    (OUT/"artifact_audit.json").write_text(json.dumps(audit,indent=2))

    # ---------------- SUMMARY / INFERENCE ----------------
    summary=[]
    for (strategy,split),g in trade.groupby(["strategy","split"]):
        variants=sorted(g["delta_target"].dropna().unique().tolist()) if "delta_target" in g else [None]
        for variant in variants:
            z=g[g.delta_target==variant] if variant is not None else g
            for state in STATES:
                a=z[z.active_states.apply(lambda x: state in parse_states(x))]
                if len(a)==0: continue
                vals=a.net.to_numpy(float)
                summary.append({"strategy":strategy,"split":split,"state":state,"variant":variant,
                                "trades":len(a),"net":float(a.net.sum()),"net50":float(a.net50.sum()),
                                "mean_net":float(a.net.mean()),"win_rate":float((a.net>0).mean()),
                                "max_dd":drawdown(a.sort_values("expiry").net.to_numpy()),
                                "profit_factor":pf(vals)})
    s=pd.DataFrame(summary)
    s.to_csv(OUT/"strategy_vix_summary.csv",index=False)

    val=trade[trade.split=="validation"]
    tests=[]
    for (strategy,variant),g in val.groupby(["strategy","delta_target"]):
        if len(g)==0: continue
        for state in STATES[1:]:
            t=regime_test(g,state,seed=4701+hash((strategy,variant,state))%100000)
            tests.append({"strategy":strategy,"variant":variant,"state":state,**t})
    tt=pd.DataFrame(tests)
    if len(tt):
        tt["p_holm"]=holm(tt.p.to_numpy())
    tt.to_csv(OUT/"validation_regime_inference.csv",index=False)

    # Primary validation freeze: S1 and S2 at target .30 are eligible.
    # S2 .25/.35 are sensitivity only; S3 is diagnostic only.
    freeze_pool=s[(s.split=="validation")&(s.state!="ALL")&
                  (s.trades>=20)&(s.net>0)&(s.net50>0)&
                  ((s.strategy=="double_calendar_straddle")|
                   ((s.strategy=="monthly_wide_range_hedge")&(np.isclose(s.variant,0.30))))]
    freeze=freeze_pool.sort_values(["state","net50"],ascending=[True,False]).groupby("state",as_index=False).head(2)
    freeze.to_csv(OUT/"validation_freeze.csv",index=False)

    hold=trade[trade.split=="holdout"]
    hc=[]
    for r in freeze.itertuples(index=False):
        z=hold[hold.strategy==r.strategy]
        if r.strategy=="monthly_wide_range_hedge":
            z=z[np.isclose(z.delta_target,0.30)]
        z=z[z.active_states.apply(lambda x:r.state in parse_states(x))]
        if len(z)==0: continue
        hc.append({"strategy":r.strategy,"state":r.state,"variant":r.variant,"hold_trades":len(z),
                   "hold_net":float(z.net.sum()),"hold_net50":float(z.net50.sum()),
                   "hold_mean_net":float(z.net.mean()),"hold_win_rate":float((z.net>0).mean()),
                   "hold_max_dd":drawdown(z.sort_values("expiry").net.to_numpy()),
                   "hold_profit_factor":pf(z.net.to_numpy())})
    hc=pd.DataFrame(hc)
    hc.to_csv(OUT/"holdout_confirmation.csv",index=False)

    primary_v=s[(s.split=="validation")&(s.state!="ALL")&
                (s.trades>=20)&(s.net>0)&(s.net50>0)&
                (((s.strategy=="double_calendar_straddle")|
                  ((s.strategy=="monthly_wide_range_hedge")&np.isclose(s.variant,0.30))))]
    summary_json={
        "rows":int(len(trade)),
        "strategies":sorted(trade.strategy.unique().tolist()),
        "validation_working_states":int(len(primary_v)),
        "frozen_rows":int(len(freeze)),
        "holdout_rows":int(len(hc)),
        "holdout_positive":int((hc.hold_net>0).sum()) if len(hc) else 0,
        "holm_survivors":int((tt.p_holm<0.05).sum()) if len(tt) else 0,
        "errors":int(len(errors)),
    }
    (OUT/"summary.json").write_text(json.dumps(summary_json,indent=2))

    manuscript = [
        "# Phase 47 Manuscript — VIX Source-Strategy Numerical Backtest",
        "",
        "## Decision",
        "No strategy is promoted unless the preregistered validation, statistical, cost-stress and protected-holdout gates pass.",
        "",
        "## Source-derived strategies",
        "Double Calendar Straddle; Monthly Wide-Range Hedge; Covered Call 2.0 synthetic-future proxy.",
        "",
        "## VIX states",
        ", ".join(STATES),
        "",
        "## Numerical results",
        s[(s.split=="validation")&(s.state!="ALL")].sort_values(["state","net50"],ascending=[True,False]).head(40).to_markdown(index=False),
        "",
        "## Statistical inference",
        tt.sort_values("p_holm").head(40).to_markdown(index=False) if len(tt) else "No inference rows.",
        "",
        "## Frozen validation candidates",
        freeze.to_markdown(index=False) if len(freeze) else "None.",
        "",
        "## 2026 holdout confirmation",
        hc.to_markdown(index=False) if len(hc) else "No confirmation rows.",
        "",
        "## Execution and stress",
        "Historical lot sizes, Paytm Money brokerage and Indian statutory charges are applied. The +50% stress multiplies monetary fee/charge components by 1.5; the adverse ₹0.05 option tick remains fixed in this implementation.",
        "",
        "## Limitations",
        "S2 uses a reconstructed 0.30-delta rule because platform greeks are not stored in the underlying dataset. S3 is explicitly an option-only proxy for a strategy whose source implementation uses futures. Neither source claim is accepted as independent performance evidence."
    ]
    (OUT/"PHASE47_MANUSCRIPT.md").write_text("\n".join(manuscript))
    print(json.dumps(summary_json,indent=2))

if __name__ == "__main__":
    main()
