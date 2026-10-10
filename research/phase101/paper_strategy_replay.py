#!/usr/bin/env python3
"""Bounded Phase 101 proxy tests for PDF methods U02 and U05."""
# Environment revision: dependency versions are locked in requirements-phase101.txt.
from __future__ import annotations
import importlib, json, math, os, sys, traceback
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "phase101_pdf_strategy_tests"
PINNED_REVISION = "3eacf762d401efd9a08e804592fa7882b354c4a2"
HF_REPO = "thetrademarkk/india-index-options-1m"
TZ = "Asia/Kolkata"
DEV_END = pd.Timestamp("2023-12-31", tz=TZ)
VAL_START = pd.Timestamp("2024-01-01", tz=TZ)
VAL_END = pd.Timestamp("2025-12-31 23:59:59", tz=TZ)
CAPITAL_U02 = 100_000.0
CAPITAL_U05 = 300_000.0
SEED = 101021

def first_present(row, names):
    for name in names:
        if name and name in row.index:
            try:
                v = float(row[name])
                if np.isfinite(v): return v
            except (TypeError, ValueError): pass
    return np.nan

def first_present_column(df, names):
    lowered = {str(c).strip().lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lowered: return lowered[name.lower()]
    return None

def monthly_expected_target(wednesday_open, prior_same_month_returns):
    x = np.asarray(list(prior_same_month_returns), dtype=float)
    if x.size != 3 or not np.isfinite(x).all():
        raise ValueError("exactly three finite same-calendar-month returns are required")
    mean_ret = float(x.mean())
    return float(wednesday_open * (1.0 + mean_ret)), mean_ret

def option_exit_decision(entry_price, bar_high, bar_low, stop_active,
                         target_fraction=0.20, stop_fraction=0.30):
    target = float(entry_price) * (1.0 + target_fraction)
    stop = float(entry_price) * (1.0 - stop_fraction)
    target_hit = np.isfinite(bar_high) and float(bar_high) >= target
    stop_hit = bool(stop_active and np.isfinite(bar_low) and float(bar_low) <= stop)
    if target_hit and stop_hit: return "AMBIGUOUS_BOTH_STOP_FIRST"
    if stop_hit: return "STOP_30PCT"
    if target_hit: return "TARGET_20PCT"
    return None

def block_bootstrap_mean_ci(values, block_size=5, replicates=3000):
    """Circular moving-block bootstrap CI for mean net P&L/trade; descriptive only."""
    a = np.asarray(list(values), dtype=float)
    a = a[np.isfinite(a)]
    n = len(a)
    result = {"bootstrap_status": "SKIPPED_LT20_TRADES", "bootstrap_block_size": None,
              "bootstrap_replicates": 0, "mean_net_trade_ci95_low": None,
              "mean_net_trade_ci95_high": None}
    if n < 20:
        return result
    b = min(int(block_size), n)
    rng = np.random.default_rng(SEED + n + b)
    blocks_needed = int(np.ceil(n / b))
    means = np.empty(int(replicates), dtype=float)
    offsets = np.arange(b)
    for i in range(int(replicates)):
        starts = rng.integers(0, n, size=blocks_needed)
        ix = ((starts[:, None] + offsets[None, :]) % n).ravel()[:n]
        means[i] = float(a[ix].mean())
    lo, hi = np.quantile(means, [0.025, 0.975])
    return {"bootstrap_status": "COMPUTED_CIRCULAR_MOVING_BLOCK_CI",
            "bootstrap_block_size": b, "bootstrap_replicates": int(replicates),
            "mean_net_trade_ci95_low": float(lo), "mean_net_trade_ci95_high": float(hi)}

def net_trade_metrics(values):
    a = np.asarray(list(values), dtype=float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return {"completed_trades": 0, "status": "NOT_ESTIMABLE_ZERO_TRADES",
                "net_pnl_rupees": None, "mean_net_per_trade": None,
                "median_net_per_trade": None, "win_rate": None,
                "profit_factor": None, "max_trade_equity_drawdown_rupees": None,
                **block_bootstrap_mean_ci([])}
    eq = np.cumsum(a)
    peak = np.maximum.accumulate(np.r_[0.0, eq])[1:]
    wins, losses = a[a > 0], a[a < 0]
    pf = float(wins.sum()/abs(losses.sum())) if len(losses) else (float("inf") if len(wins) else None)
    return {"completed_trades": int(len(a)), "status": "COMPUTED",
            "net_pnl_rupees": float(a.sum()), "mean_net_per_trade": float(a.mean()),
            "median_net_per_trade": float(np.median(a)), "win_rate": float((a > 0).mean()),
            "profit_factor": pf, "max_trade_equity_drawdown_rupees": float(np.max(peak-eq)),
            **block_bootstrap_mean_ci(a, block_size=5)}


def _get_p66():
    p = ROOT / "evidence" / "phase66" / "research"
    if not p.is_dir(): raise FileNotFoundError(f"Phase 66 checkout absent: {p}")
    sys.path.insert(0, str(p))
    return importlib.import_module("phase66_paper_strategy_tests")

def _make_daily(index):
    z = index.copy(); z["session_date"] = z["timestamp"].dt.normalize()
    agg = {"open": ("open","first"), "high": ("high","max"), "low": ("low","min"),
           "close": ("close","last"), "first_ts": ("timestamp","first"), "last_ts": ("timestamp","last")}
    if "volume" in z.columns:
        z["volume"] = pd.to_numeric(z["volume"], errors="coerce"); agg["volume"] = ("volume","sum")
    d = z.groupby("session_date", sort=True).agg(**agg).sort_index()
    d["ret1"] = d.close.pct_change(); d["ret5"] = d.close.pct_change(5); d["ret20"] = d.close.pct_change(20)
    d["ma5_gap"] = d.close/d.close.rolling(5).mean()-1
    d["ma20_gap"] = d.close/d.close.rolling(20).mean()-1
    d["ma50_gap"] = d.close/d.close.rolling(50).mean()-1
    d["ema12_26_gap"] = d.close.ewm(span=12, adjust=False).mean()/d.close.ewm(span=26, adjust=False).mean()-1
    delta = d.close.diff(); gain = delta.clip(lower=0).rolling(14).mean(); loss = -delta.clip(upper=0).rolling(14).mean()
    d["rsi14"] = 100 - 100/(1 + gain/loss.replace(0, np.nan))
    d["rv20"] = d.ret1.rolling(20).std()*math.sqrt(252)
    d["intraday_range"] = (d.high-d.low)/d.close
    return d

def _load_yahoo(cache_file):
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    if cache_file.exists(): raw = pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
    else:
        import yfinance as yf
        raw = yf.download("^NSEI", start="2015-01-01", end="2026-01-01",
                          auto_adjust=False, progress=False, threads=False)
        if raw is None or raw.empty: raise RuntimeError("Yahoo Finance returned no daily ^NSEI data")
        if isinstance(raw.columns, pd.MultiIndex):
            l0 = list(map(str, raw.columns.get_level_values(0)))
            raw.columns = raw.columns.get_level_values(0) if "Open" in l0 else raw.columns.get_level_values(-1)
        if not {"Open","Close"}.issubset(raw.columns): raise RuntimeError("Yahoo data missing Open/Close")
        raw.index.name = "Date"; raw.to_csv(cache_file, index_label="Date")
    raw.columns = [str(c).strip().title() for c in raw.columns]
    raw.index = pd.to_datetime(raw.index, errors="coerce")
    raw = raw.loc[raw.index.notna()].sort_index()
    raw = raw.loc[(raw.index >= "2015-01-01") & (raw.index < "2026-01-01")]
    raw["period"] = raw.index.to_period("M"); returns = {}
    for period, g in raw.groupby("period", sort=True):
        g = g.dropna(subset=["Open","Close"])
        if not g.empty and float(g.Open.iloc[0]) > 0:
            returns[str(period)] = float(g.Close.iloc[-1]/g.Open.iloc[0]-1)
    return raw, returns

def _first_weekday(period, weekday):
    day = pd.Timestamp(period.start_time.date(), tz=TZ)
    return day + pd.Timedelta(days=(weekday-day.weekday()) % 7)

def _u05_entry_dates(period):
    """Forecast on the first calendar Wednesday; enter only on a later Thursday."""
    wed = _first_weekday(period, 2).normalize()
    thu = _first_weekday(period, 3).normalize()
    while thu <= wed:
        thu += pd.Timedelta(days=7)
    return wed, thu

def _day_bars(index, date):
    return index.loc[index.timestamp.dt.normalize().eq(pd.Timestamp(date).normalize())].sort_values("timestamp")

def _pick_snapshot(chain_day, side, target_strike, oi_col, vol_col):
    c = chain_day.loc[chain_day.option_type.eq(side)].copy()
    if c.empty: return None
    c["strike"] = pd.to_numeric(c.strike, errors="coerce"); c = c.loc[c.strike.notna()].copy()
    if c.empty: return None
    c["distance"] = (c.strike-float(target_strike)).abs()
    c["_oi"] = pd.to_numeric(c[oi_col], errors="coerce") if oi_col else np.nan
    c["_vol"] = pd.to_numeric(c[vol_col], errors="coerce") if vol_col else np.nan
    return c.sort_values(["distance","_oi","_vol"], ascending=[True,False,False], kind="stable").iloc[0]

def _trade_costs(p66, entry_ts, exit_ts, entry_raw, exit_raw, qty_lot):
    buy = float(p66.exec_px(entry_raw, "buy")); sell = float(p66.exec_px(exit_raw, "sell"))
    gross = (sell-buy)*qty_lot
    orders = [(entry_ts,"buy",buy),(exit_ts,"sell",sell)]
    fee10 = float(p66.charges(orders, qty_lot, 1.0))
    fee20 = fee10 + 10.0*len(orders)
    stress10 = float(p66.charges(orders, qty_lot, 1.5))
    stress20 = stress10 + 15.0*len(orders)
    # Paper-specific stress: 0.25% adverse entry/exit impact plus ₹50 per round trip.
    paper_net = (max(0.0, float(exit_raw)*0.9975)-float(entry_raw)*1.0025)*qty_lot-50.0
    return {"entry_exec": buy, "exit_exec": sell, "gross_net_of_tick_slippage": gross,
            "charges_10_per_order": fee10, "net_10_per_order": gross-fee10,
            "net_20_per_order": gross-fee20, "net_10_per_order_fee_stress_50pct": gross-stress10,
            "net_20_per_order_fee_stress_50pct": gross-stress20,
            "paper_025pct_each_side_plus_50_trade_cost_net": paper_net}

def _audit_row(base, status, reason):
    return {**base, "status": status, "failure_reason": reason}

def run_u05(p66, api, token, monthly, index, daily, month_returns, manifest):
    trades, audit = [], []
    equity = float(CAPITAL_U05)
    equity_peak = equity
    max_account_drawdown = 0.0
    for m, (expiry, filename) in sorted(monthly.items()):
        period = pd.Period(m, "M"); wed, thu = _u05_entry_dates(period)
        base = {"paper_id":"U05","month":m,"expiry":str(expiry.date()),"source_file":filename,
                "wednesday_date":str(wed.date()),"thursday_date":str(thu.date())}
        periods = [str(pd.Period(year=period.year-k, month=period.month, freq="M")) for k in (1,2,3)]
        prior = [month_returns.get(x,np.nan) for x in periods]
        if not np.isfinite(prior).all():
            audit.append(_audit_row(base,"BLOCKED_MISSING_THREE_PRIOR_RETURNS","Need three prior same-calendar-month returns")); continue
        if wed not in daily.index:
            audit.append(_audit_row(base,"EXCLUDED_FIRST_WEDNESDAY_NOT_SESSION","Literal first Wednesday absent; no holiday substitution")); continue
        if thu not in daily.index:
            audit.append(_audit_row(base,"EXCLUDED_FIRST_THURSDAY_NOT_SESSION","Literal first Thursday absent; no holiday substitution")); continue
        expected, mean_ret = monthly_expected_target(float(daily.loc[wed,"open"]), prior)
        side = "CE" if mean_ret > 0 else "PE" if mean_ret < 0 else None
        if side is None:
            audit.append(_audit_row({**base,"expected_price":expected},"EXCLUDED_ZERO_DIRECTION","Three-return mean equals zero")); continue
        cr, meta = p66.load_pinned(api, token, filename); manifest.setdefault("option_source_files_used",[]).append(meta)
        chain = p66.normalize_chain(cr); del cr
        oi_col = first_present_column(chain,["open_interest","oi","openinterest"])
        vol_col = first_present_column(chain,["volume","vol","traded_volume"])
        ibars = _day_bars(index,thu)
        ibars = ibars.loc[ibars.timestamp.dt.time.between(pd.Timestamp("09:15").time(),pd.Timestamp("09:20").time())]
        if ibars.empty:
            audit.append(_audit_row({**base,"mean_prior_same_month_return":mean_ret,"expected_price":expected,"direction":side},
                                    "BLOCKED_NO_THURSDAY_INDEX_BAR","No underlying bar 09:15–09:20")); del chain; continue
        # Use the earliest underlying minute in the opening window that also has a same-minute option quote.
        ix = None; entry_ts = None; spot = np.nan; pick = None
        for _, candidate in ibars.iterrows():
            candidate_ts = candidate.timestamp
            candidate_spot = first_present(candidate,["open","close"])
            candidate_pick = _pick_snapshot(chain.loc[chain.timestamp.eq(candidate_ts)],side,expected,oi_col,vol_col)
            if candidate_pick is not None and np.isfinite(candidate_spot):
                ix = candidate; entry_ts = candidate_ts; spot = candidate_spot; pick = candidate_pick
                break
        if pick is None:
            audit.append(_audit_row({**base,"mean_prior_same_month_return":mean_ret,"expected_price":expected,
                "direction":side,"opening_window":"09:15-09:20"},
                "BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION","No same-minute selected-side option row during 09:15–09:20")); del chain; continue
        strike = float(pick.strike); entry_raw = first_present(pick,["open","close"])
        lot = int(p66.lot_size_for_expiry(expiry))
        common = {**base,"mean_prior_same_month_return":mean_ret,"prior_same_month_periods":";".join(periods),
                  "expected_price":expected,"direction":side,"entry_ts":str(entry_ts),"entry_spot":spot,
                  "strike":strike,"option_entry_raw":entry_raw,"lot_size":lot,"account_equity_before":equity}
        if not np.isfinite(entry_raw) or entry_raw <= 0:
            audit.append(_audit_row(common,"BLOCKED_BAD_ENTRY_PRICE","Entry premium invalid")); del chain; continue
        entry_exec = float(p66.exec_px(entry_raw,"buy"))
        premium_per_lot = entry_exec * lot
        # The paper commits 90% of a ₹3 lakh account and reserves 10% as a safety margin.
        lots = int((equity * 0.90) // premium_per_lot) if premium_per_lot > 0 else 0
        if lots < 1:
            audit.append(_audit_row({**common,"one_lot_premium_cost":premium_per_lot},
                "EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY","One lot does not fit within 90% of current equity")); del chain; continue
        bars = chain.loc[chain.option_type.eq(side)&chain.strike.eq(strike)].sort_values("timestamp")
        bars = bars.loc[bars.timestamp.gt(entry_ts)&bars.timestamp.dt.date.lt(expiry.date())].copy()
        future_sessions = [pd.Timestamp(d) for d in daily.index if pd.Timestamp(d).date()>thu.date() and pd.Timestamp(d).date()<expiry.date()]
        stop_date = future_sessions[2] if len(future_sessions)>=3 else None
        result = None
        if {"high","low"}.issubset(bars.columns):
            for _, bar in bars.iterrows():
                active = stop_date is not None and bar.timestamp.normalize()>=stop_date.normalize()
                why = option_exit_decision(entry_raw,bar.high,bar.low,bool(active))
                if why:
                    xt = bar.timestamp+pd.Timedelta(minutes=1)
                    exitrow = bars.loc[bars.timestamp.eq(xt)]
                    if exitrow.empty: result={"status":"BLOCKED_NO_EXACT_NEXT_MINUTE_EXIT","reason":f"{why} has no +1 minute same-contract bar"}
                    else:
                        er=exitrow.iloc[0]; px=first_present(er,["open","close"])
                        result=({"status":"COMPLETED","exit_ts":xt,"exit_raw":px,"exit_reason":why,"trigger_ts":bar.timestamp}
                                if np.isfinite(px) and px>=0 else {"status":"BLOCKED_BAD_EXIT_PRICE","reason":"Next-minute exit price invalid"})
                    break
        if result is None:
            prior_days=[pd.Timestamp(d) for d in daily.index if pd.Timestamp(d).date()<expiry.date()]
            td=prior_days[-1] if prior_days else None
            term=bars.loc[bars.timestamp.dt.normalize().eq(td.normalize()) &
                          bars.timestamp.dt.time.between(pd.Timestamp("15:24").time(),pd.Timestamp("15:29").time())] if td is not None else pd.DataFrame()
            if term.empty: result={"status":"BLOCKED_NO_PENULTIMATE_EXIT_BAR","reason":"No penultimate-session exit bar"}
            else:
                er=term.iloc[-1]; px=first_present(er,["close"])
                result=({"status":"COMPLETED","exit_ts":er.timestamp,"exit_raw":px,"exit_reason":"PENULTIMATE_SESSION_CLOSE","trigger_ts":None}
                        if np.isfinite(px) and px>=0 else {"status":"BLOCKED_BAD_TERMINAL_EXIT_PRICE","reason":"Penultimate close invalid"})
        common["stop_activation_date"] = str(stop_date.date()) if stop_date is not None else None
        if result["status"] != "COMPLETED":
            audit.append(_audit_row(common,result["status"],result.get("reason",""))); del chain; continue
        cost = _trade_costs(p66,entry_ts,result["exit_ts"],entry_raw,result["exit_raw"],lot*lots)
        equity_before = equity
        net = float(cost["net_10_per_order"])
        equity = equity_before + net
        equity_peak = max(equity_peak,equity)
        drawdown = max(0.0,equity_peak-equity)
        max_account_drawdown = max(max_account_drawdown,drawdown)
        trade={**common,"exit_ts":str(result["exit_ts"]),"exit_reason":result["exit_reason"],
               "trigger_ts":str(result["trigger_ts"]),"option_exit_raw":float(result["exit_raw"]),
               "lots":lots,"capital_used_estimate":entry_exec*lot*lots,
               "account_equity_after":equity,"account_return_pct_on_opening_equity":100.0*net/equity_before if equity_before else None,
               "account_peak_to_date":equity_peak,"account_drawdown_from_peak":drawdown,**cost}
        trades.append(trade); audit.append({**common,"status":"COMPLETED","failure_reason":"",
                                            "lots":lots,"capital_used_estimate":entry_exec*lot*lots,
                                            "account_equity_after":equity,
                                            "exit_ts":str(result["exit_ts"]),"exit_reason":result["exit_reason"]})
        del chain
    met=net_trade_metrics([x["net_10_per_order"] for x in trades])
    summary={"paper_id":"U05","strategy":"three-year same-month return; first Wednesday forecast; first later Thursday option",
             "initial_account_equity":float(CAPITAL_U05),"ending_account_equity":float(equity),
             "account_return_pct":100.0*(equity/CAPITAL_U05-1.0),
             "max_account_drawdown_rupees":float(max_account_drawdown),
             "equity_deployment_limit_pct":90.0,
             "evaluation_months":len(audit),"audit_status_counts":dict(Counter(x["status"] for x in audit)),**met}
    for k in ["net_20_per_order","net_10_per_order_fee_stress_50pct","net_20_per_order_fee_stress_50pct",
              "paper_025pct_each_side_plus_50_trade_cost_net"]:
        summary[k]=float(sum(x[k] for x in trades)) if trades else None
    return trades,audit,summary

def _optional_value(row, aliases):
    return first_present(row,aliases)

def _option_daily_features(chain, expiry, daily, month):
    c=chain.copy(); c["session_date"]=c.timestamp.dt.normalize()
    volc=first_present_column(c,["volume","vol","traded_volume"])
    oic=first_present_column(c,["open_interest","oi","openinterest"])
    optional = {}
    for key, aliases in {
        "iv":["implied_volatility","impliedvolatility","iv","implied_vol"],
        "delta":["delta","option_delta"],"gamma":["gamma","option_gamma"],
        "theta":["theta","option_theta"],"vega":["vega","option_vega"]
    }.items():
        col=first_present_column(c,aliases)
        if col: optional[key]=col
    rows=[]
    for d,g in c.groupby("session_date",sort=True):
        if d not in daily.index: continue
        g=g.loc[g.timestamp.dt.time.between(pd.Timestamp("15:24").time(),pd.Timestamp("15:29").time())]
        if g.empty: continue
        snap=g.loc[g.timestamp.eq(g.timestamp.max())]; spot=float(daily.loc[d,"close"])
        ce=_pick_snapshot(snap,"CE",spot,oic,volc); pe=_pick_snapshot(snap,"PE",spot,oic,volc)
        rec={"date":pd.Timestamp(d),"source_month":month,"days_to_expiry":float((expiry.normalize()-pd.Timestamp(d).normalize()).days)}
        for side,row in [("ce",ce),("pe",pe)]:
            px=first_present(row,["close"]) if row is not None else np.nan
            rec[f"{side}_premium_spot"]=px/spot if np.isfinite(px) and spot>0 else np.nan
            vol=first_present(row,[volc]) if row is not None and volc else np.nan
            oi=first_present(row,[oic]) if row is not None and oic else np.nan
            rec[f"{side}_log_volume"]=float(np.log1p(max(vol,0))) if np.isfinite(vol) else np.nan
            rec[f"{side}_log_oi"]=float(np.log1p(max(oi,0))) if np.isfinite(oi) else np.nan
            for key,col in optional.items():
                rec[f"{side}_{key}"]=_optional_value(row,[col]) if row is not None else np.nan
        rec["atm_straddle_spot"]=rec["ce_premium_spot"]+rec["pe_premium_spot"]
        rows.append(rec)
    return rows

def build_u02_frame(p66,api,token,monthly,index,daily,manifest):
    rows=[]
    for m,(expiry,filename) in sorted(monthly.items()):
        raw,meta=p66.load_pinned(api,token,filename); manifest.setdefault("option_source_files_used",[]).append(meta)
        chain=p66.normalize_chain(raw); del raw
        rows.extend(_option_daily_features(chain,expiry,daily,m)); del chain
    if not rows: raise RuntimeError("no daily option-chain snapshots for U02")
    opt=pd.DataFrame(rows).drop_duplicates("date",keep="last").set_index("date").sort_index()
    base=["ret1","ret5","ret20","ma5_gap","ma20_gap","ma50_gap","ema12_26_gap","rsi14","rv20","intraday_range"]
    frame=daily[base].join(opt.drop(columns=["source_month"],errors="ignore"),how="inner")
    frame["next_date"]=daily.index.to_series().shift(-1).reindex(frame.index)
    frame["next_close"]=daily.close.shift(-1).reindex(frame.index)
    frame["spot_close"]=daily.close.reindex(frame.index)
    frame["next_return"]=frame.next_close/frame.spot_close-1
    frame["label_buy"]=(frame.next_return>0.01).astype(float)
    frame.loc[frame.next_date.isna(),"label_buy"]=np.nan
    frame["label_date"]=frame.next_date
    candidates=[x for x in frame.columns if x not in {"next_date","next_close","spot_close","next_return","label_buy","label_date"}]
    dev=frame.loc[(frame.index<=DEV_END.normalize())&frame.label_buy.notna()]
    eligible=[x for x in candidates if pd.to_numeric(dev[x],errors="coerce").notna().mean()>=0.50
              and pd.to_numeric(dev[x],errors="coerce").nunique(dropna=True)>1] if len(dev) else []
    frame=frame.replace([np.inf,-np.inf],np.nan)
    frame.attrs["eligible_features"]=eligible; frame.attrs["candidate_features"]=candidates
    return frame

def predict_models(frame):
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score,balanced_accuracy_score,precision_score,recall_score,f1_score,roc_auc_score
    feat=list(frame.attrs.get("eligible_features",[]))
    dat=frame.loc[frame.label_buy.notna()&frame.next_date.notna()].sort_index()
    train=dat.loc[(dat.index<=DEV_END.normalize())&(dat.label_date<=DEV_END.normalize())]
    valid=dat.loc[(dat.index>=VAL_START.normalize())&(dat.label_date<=VAL_END.normalize())]
    info={"eligible_features":feat,"all_candidate_features":frame.attrs.get("candidate_features",[]),
          "training_rows":len(train),"validation_rows":len(valid)}
    if len(feat)<3 or len(train)<100 or len(valid)<20 or train.label_buy.nunique()<2:
        return [],[],[{"model":"ALL","status":"DATA_BLOCKED_INSUFFICIENT_FEATURES_OR_SAMPLE",
          "eligible_feature_count":len(feat),"training_rows":len(train),"validation_rows":len(valid)}],info
    imp=SimpleImputer(strategy="median")
    xt=imp.fit_transform(train[feat].apply(pd.to_numeric,errors="coerce"))
    xv=imp.transform(valid[feat].apply(pd.to_numeric,errors="coerce"))
    yt=train.label_buy.astype(int).to_numpy(); yv=valid.label_buy.astype(int).to_numpy()
    models=[("RF",RandomForestClassifier(n_estimators=300,min_samples_leaf=5,
             class_weight="balanced_subsample",random_state=SEED,n_jobs=2))]
    try:
        from xgboost import XGBClassifier
        models.append(("XGBOOST",XGBClassifier(n_estimators=120,max_depth=3,learning_rate=0.04,
             subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,random_state=SEED,n_jobs=2,eval_metric="logloss")))
    except Exception: pass
    preds,metrics,status=[],[],[]
    def score(name,proba,pred,true,ntr,nva):
        return {"model":name,"status":"COMPLETED","training_rows":ntr,"validation_rows":nva,
          "positive_rate_train":float(yt.mean()),"positive_rate_validation":float(true.mean()),
          "accuracy":float(accuracy_score(true,pred)),"balanced_accuracy":float(balanced_accuracy_score(true,pred)),
          "precision_buy":float(precision_score(true,pred,zero_division=0)),
          "recall_buy":float(recall_score(true,pred,zero_division=0)),
          "f1_buy":float(f1_score(true,pred,zero_division=0)),
          "roc_auc":float(roc_auc_score(true,proba)) if len(np.unique(true))>1 else None,
          "always_sell_accuracy":float((true==0).mean()),
          "always_sell_balanced_accuracy":float(balanced_accuracy_score(true,np.zeros_like(true))),
          "eligible_feature_count":len(feat)}
    for name,model in models:
        try:
            model.fit(xt,yt); pr=model.predict_proba(xv)[:,list(model.classes_).index(1)]; yh=(pr>=0.5).astype(int)
            metrics.append(score(name,pr,yh,yv,len(train),len(valid))); status.append({"model":name,"status":"COMPLETED"})
            for dt,ld,truth,pred,prob in zip(valid.index,valid.label_date,yv,yh,pr):
                preds.append({"model":name,"signal_date":pd.Timestamp(dt),"entry_date":pd.Timestamp(ld),
                    "actual_label_buy":int(truth),"prediction_buy":int(pred),"probability_buy":float(prob)})
        except Exception as exc: status.append({"model":name,"status":"MODEL_FAILED","error":str(exc)[:500]})
    try:
        import tensorflow as tf
        tf.keras.utils.set_random_seed(SEED)
        scaler=StandardScaler(); scaler.fit(xt)
        # Scale every feature row using training-only preprocessing; sequence labels remain next-session returns.
        allx=imp.transform(dat[feat].apply(pd.to_numeric,errors="coerce")); alls=scaler.transform(allx)
        dates=[pd.Timestamp(x) for x in dat.index]; pos={d:i for i,d in enumerate(dates)}
        def sequences(part):
            xs,ys,dts,lds=[],[],[],[]
            for dt,row in part.iterrows():
                i=pos[pd.Timestamp(dt)]
                if i<4: continue
                ds=dates[i-4:i+1]
                if any(ds[j] not in pos for j in range(5)): continue
                if (ds[-1]-ds[0]).days>8: continue
                xs.append(alls[[pos[d] for d in ds],:]); ys.append(int(row.label_buy)); dts.append(pd.Timestamp(dt)); lds.append(pd.Timestamp(row.label_date))
            return np.asarray(xs,dtype=float),np.asarray(ys,dtype=int),dts,lds
        xseq,yseq,_,_=sequences(train); vseq,vy,vdates,vlabels=sequences(valid)
        if len(xseq)<100 or len(vseq)<20 or len(np.unique(yseq))<2:
            raise RuntimeError("insufficient five-session sequences for LSTM proxy")
        net=tf.keras.Sequential([tf.keras.layers.Input(shape=(5,len(feat))),tf.keras.layers.LSTM(8),tf.keras.layers.Dense(1,activation="sigmoid")])
        net.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),loss="binary_crossentropy")
        net.fit(xseq,yseq,epochs=8,batch_size=32,shuffle=False,verbose=0)
        pr=net.predict(vseq,verbose=0).reshape(-1); yh=(pr>=0.5).astype(int)
        metrics.append(score("LSTM5",pr,yh,vy,len(yseq),len(vy))); status.append({"model":"LSTM5","status":"COMPLETED"})
        for dt,ld,truth,pred,prob in zip(vdates,vlabels,vy,yh,pr):
            preds.append({"model":"LSTM5","signal_date":dt,"entry_date":ld,"actual_label_buy":int(truth),"prediction_buy":int(pred),"probability_buy":float(prob)})
    except Exception as exc: status.append({"model":"LSTM5","status":"MODEL_FAILED_OR_BLOCKED","error":str(exc)[:500]})
    if not any(x.get("model")=="XGBOOST" for x in status):
        status.append({"model":"XGBOOST","status":"MODEL_UNAVAILABLE","error":"xgboost import was unavailable"})
    info.update({"training_positive_rate":float(yt.mean()),"validation_positive_rate":float(yv.mean())})
    return preds,metrics,status,info

def simulate_u02(p66,api,token,monthly,index,predictions,manifest):
    """One non-overlapping long-option trade/day; model-specific ₹1 lakh equity account.

    Premium deployment is capped at 95% of current equity, preserving cash for charges.
    Account equity updates after each realized trade; when one lot no longer fits, entries
    are blocked instead of silently reusing the initial ₹1 lakh on every signal.
    """
    trades,audit=[],[]
    if not predictions:
        return trades,[{"status":"NO_MODEL_PREDICTIONS","reason":"Models emitted no validation predictions"}]
    pf=pd.DataFrame(predictions)
    pf["entry_month"]=pf.entry_date.map(lambda x:pd.Timestamp(x).strftime("%Y-%m"))
    for model, mp in pf.groupby("model",sort=True):
        equity=float(CAPITAL_U02)
        model_peak=equity
        for m,g in mp.groupby("entry_month",sort=True):
            if m not in monthly:
                for r in g.to_dict("records"):
                    audit.append({"model":model,"signal_date":str(r["signal_date"]),
                        "entry_date":str(r["entry_date"]),"status":"BLOCKED_NO_MONTHLY_OPTION_FILE","reason":m,
                        "account_equity":equity})
                continue
            expiry,filename=monthly[m]
            raw,meta=p66.load_pinned(api,token,filename)
            manifest.setdefault("option_source_files_used",[]).append(meta)
            chain=p66.normalize_chain(raw); del raw
            oic=first_present_column(chain,["open_interest","oi","openinterest"])
            volc=first_present_column(chain,["volume","vol","traded_volume"])
            for r in g.sort_values("entry_date").to_dict("records"):
                d=pd.Timestamp(r["entry_date"]).normalize()
                if equity <= 0:
                    audit.append({"model":model,"entry_date":str(d.date()),"status":"EXCLUDED_ACCOUNT_EQUITY_DEPLETED",
                                  "reason":"Model account equity is non-positive","account_equity":equity})
                    continue
                bars=_day_bars(index,d)
                bars=bars.loc[bars.timestamp.dt.time.between(pd.Timestamp("09:15").time(),pd.Timestamp("09:20").time())]
                if bars.empty:
                    audit.append({"model":model,"entry_date":str(d.date()),"status":"BLOCKED_NO_ENTRY_INDEX_BAR",
                                  "reason":"No 09:15-09:20 index bar","account_equity":equity}); continue
                side="CE" if int(r["prediction_buy"])==1 else "PE"
                ix=None; et=None; spot=np.nan; pick=None
                for _, candidate in bars.iterrows():
                    candidate_ts=candidate.timestamp
                    candidate_spot=first_present(candidate,["open","close"])
                    candidate_pick=_pick_snapshot(chain.loc[chain.timestamp.eq(candidate_ts)],side,candidate_spot,oic,volc)
                    if candidate_pick is not None and np.isfinite(candidate_spot):
                        ix=candidate; et=candidate_ts; spot=candidate_spot; pick=candidate_pick; break
                if pick is None:
                    audit.append({"model":model,"entry_date":str(d.date()),"signal_side":side,
                                  "status":"BLOCKED_NO_MATCHING_OPENING_WINDOW_OPTION",
                                  "reason":"No same-minute ATM-side contract during 09:15-09:20",
                                  "account_equity":equity}); continue
                strike=float(pick.strike); entry=first_present(pick,["open","close"])
                if not np.isfinite(entry) or entry<=0:
                    audit.append({"model":model,"entry_date":str(d.date()),"status":"BLOCKED_BAD_ENTRY_PRICE",
                                  "reason":"Entry premium invalid","account_equity":equity}); continue
                lot=int(p66.lot_size_for_expiry(expiry))
                entry_exec=float(p66.exec_px(entry,"buy"))
                premium_per_lot=entry_exec*lot
                # Keep 5% equity as a cash buffer for brokerage, exchange/STT/GST charges.
                lots=int((equity*0.95)//premium_per_lot) if premium_per_lot>0 else 0
                if lots<1:
                    audit.append({"model":model,"entry_date":str(d.date()),"entry_ts":str(et),"signal_side":side,
                                  "strike":strike,"status":"EXCLUDED_INSUFFICIENT_ACCOUNT_EQUITY",
                                  "reason":"A lot cannot be funded while preserving the 5% fee reserve",
                                  "account_equity":equity,"one_lot_premium_cost":premium_per_lot}); continue
                ct=chain.loc[chain.option_type.eq(side)&chain.strike.eq(strike)&chain.timestamp.dt.normalize().eq(d)].sort_values("timestamp")
                ex=ct.loc[ct.timestamp.dt.time.between(pd.Timestamp("15:25").time(),pd.Timestamp("15:30").time())]
                if ex.empty:
                    audit.append({"model":model,"entry_date":str(d.date()),"status":"BLOCKED_NO_EXIT_BAR",
                                  "reason":"No same-contract 15:25-15:30 bar","account_equity":equity}); continue
                xr=ex.iloc[-1]; xt=xr.timestamp; exitp=first_present(xr,["close"])
                if not np.isfinite(exitp) or exitp<0:
                    audit.append({"model":model,"entry_date":str(d.date()),"status":"BLOCKED_BAD_EXIT_PRICE",
                                  "reason":"Exit premium invalid","account_equity":equity}); continue
                cost=_trade_costs(p66,et,xt,entry,exitp,lot*lots)
                before=equity
                net=float(cost["net_10_per_order"])
                after=before+net
                model_peak=max(model_peak,after)
                account_dd=max(0.0,model_peak-after)
                rec={"paper_id":"U02","model":model,"signal_date":str(pd.Timestamp(r["signal_date"]).date()),
                  "entry_date":str(d.date()),"entry_ts":str(et),"exit_ts":str(xt),
                  "actual_label_buy":int(r["actual_label_buy"]),"prediction_buy":int(r["prediction_buy"]),
                  "probability_buy":float(r["probability_buy"]),"signal_side":side,"strike":strike,
                  "entry_spot":spot,"entry_option_raw":entry,"exit_option_raw":exitp,"lots":lots,
                  "lot_size":lot,"capital_used_estimate":entry_exec*lot*lots,
                  "account_equity_before":before,"account_equity_after":after,
                  "account_return_pct_on_opening_equity":100.0*net/before if before else None,
                  "account_peak_to_date":model_peak,"account_drawdown_from_peak":account_dd,
                  "equity_deployment_limit_pct":95.0,**cost}
                trades.append(rec)
                audit.append({"model":model,"entry_date":str(d.date()),"status":"COMPLETED","reason":"",
                              "side":side,"strike":strike,"lots":lots,"account_equity_before":before,
                              "account_equity_after":after})
                equity=after
            del chain
    return trades,audit

def paper_matrix(u02_metrics,u05_summary):
    u02="PROXY_TESTED" if any(x.get("status")=="COMPLETED" for x in u02_metrics) else "DATA_BLOCKED_OR_MODEL_FAILED"
    u05="PROXY_TESTED" if u05_summary.get("completed_trades",0)>0 else "INCONCLUSIVE_OR_DATA_BLOCKED"
    vals=[
    ("U01","Bansal multi-regressor stock-price forecasts","PARTIAL","Phase 95 common-data screen; original universe/protocol not matched."),
    ("U02","Sherasiya RF/XGBoost/LSTM NIFTY options signals",u02,"Phase 101 fixed chronological proxy; exact IV/Greeks and source configuration may be absent."),
    ("U03","Bumrah/Budhani ANN with USD/INR and FII inputs","PARTIAL","Phase 95 price-only screen; FX/FII inputs not matched."),
    ("U04","Sain/Singh multi-window NIFTY forecast","PARTIAL","Phase 95 common-data screen; exact source protocol not matched."),
    ("U05","Atheetha monthly trend/seasonality options rule",u05,"Phase 101 modern-sample proxy; dimensionally ambiguous expected-price formula operationalized."),
    ("U06","Naik/Inamdar sentiment/news plus LSTM","DATA_BLOCKED_SOURCE_MODALITIES","Point-in-time news/sentiment, FII/DII, VIX/PCR/Greeks not fully sourced as a joined feature panel."),
    ("U07","Chatterjee options payoff structures","PARTIAL_ANALYTICAL","Phase 99 checked 13 expiry-payoff structures over nine illustrative spot values; no historical entry strategy."),
    ("U08","Fathali/Kodia/Ben Said NIFTY forecast","PARTIAL","Phase 95 common-data screen; source-period and data split not fully matched."),
    ("U09","Kallimath deep-learning model family","PARTIAL","Phase 95 common-data screen; source-specific dataset/settings not matched."),
    ("U10","NIFTY moving-average paper","PARTIAL","Phase 96 descriptive SMA/EMA screen; not inferentially confirmed and not options P&L."),
    ("U11","NIFTY RNN/LSTM/CNN comparison","PARTIAL","Phase 95 common-data screen, not exact source replication."),
    ("U12","MLP/backprop OHLC forecast","PARTIAL","Phase 95 common-data screen; exact OHLC label construction not matched."),
    ("U13","LSTM backward feature elimination/RSI","PARTIAL","Phase 95 price-only screen; exact source feature-elimination protocol not matched."),
    ("U14","Shaha CCI NIFTY options rule","DATA_BLOCKED_ZERO_COMPLETED_TRADES","Phase 66 zero completed trades; Phases 67-68 found insufficient exact timing/contract coverage.")]
    return [{"paper_id":a,"paper_or_method":b,"phase101_status":c,"evidence_and_limitation":d} for a,b,c,d in vals]

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,default=str,allow_nan=False)+"\n",encoding="utf-8")

def _fmt(v):
    if v is None or (isinstance(v,(float,np.floating)) and not np.isfinite(v)): return "not estimable"
    if isinstance(v,(float,np.floating)): return f"{v:,.4f}"
    return str(v)

def _write_report(matrix,u05,u02_metrics,u02_summaries,model_status,info,manifest,validation):
    lines=[
    "# Phase 101 — Full PDF Strategy Replication Gap-Fill","",
    f"**Status:** {validation['overall_status']}  ","**Decision:** no strategy promoted  ",
    f"**Pinned dataset revision:** {PINNED_REVISION}  ",
    f"**Data end:** {manifest.get('underlying_last_timestamp_used')}  ",
    "**2026 options holdout:** not downloaded or evaluated.","",
    "## 1. Research question and scope",
    "This bounded follow-up tests U02 (RF/XGBoost/LSTM Buy/Sell options method) and U05 (monthly seasonality options procedure) where modern historical data allow proxy replay. Other methods are reconciled from the verified earlier phase outputs; they are not mislabelled as new tests.","",
    "## 2. Data/provenance",
    f"- Historical option dataset: {HF_REPO}, pinned revision {PINNED_REVISION}, CC-BY-NC-4.0. Raw data are not published.",
    f"- Eligible monthly expiry files: {manifest.get('monthly_expiry_file_count')}; underlying minute rows: {manifest.get('underlying_rows')}; sessions: {manifest.get('underlying_sessions')}.",
    f"- Last underlying timestamp used: {manifest.get('underlying_last_timestamp_used')}; latest selected expiry: {manifest.get('maximum_option_expiry_selected')}.",
    f"- Yahoo daily history for monthly-return calculation: {manifest.get('yahoo_daily_start')} through {manifest.get('yahoo_daily_end')} ({manifest.get('yahoo_daily_rows')} observations).","",
    "## 3. U05 — monthly seasonality options rule",
    "Source wording uses an ambiguous expression equivalent to opening price plus average return. This run uses Wednesday open × (1 + the mean of the preceding three annual returns for the same calendar month). The first calendar Wednesday supplies the forecast; entry is on the first calendar Thursday strictly after that Wednesday to prevent look-ahead. No holiday substitution is made. Positive mean selects CE and negative mean selects PE. Entry strike is closest to the expected index level at the first 09:15–09:20 opening-window minute with matching underlying and option bars; only contemporaneous OI/volume can break ties.",
    "The test uses the paper’s ₹3,00,000 initial capital, deploying no more than 90% of current equity per monthly trade; equity is carried forward and 10% is held as a safety reserve. Target is a 20% premium gain and a 30% premium stop that activates on the third subsequent trading session. If target and stop are both crossed inside one minute, stop is prioritized. Trigger exits require the exact next-minute bar; absent a target/stop, exit uses an observed penultimate-session bar before expiry.","",
    f"- Months audited: {u05.get('evaluation_months')}; completed trades: {u05.get('completed_trades')}; status: {u05.get('status')}.",
    f"- Initial/ending account equity: ₹{_fmt(u05.get('initial_account_equity'))} / ₹{_fmt(u05.get('ending_account_equity'))}; account return: {_fmt(u05.get('account_return_pct'))}%; max account drawdown: ₹{_fmt(u05.get('max_account_drawdown_rupees'))}.",
    f"- Mean net P&L/trade 95% circular moving-block bootstrap interval: {_fmt(u05.get('mean_net_trade_ci95_low'))} to {_fmt(u05.get('mean_net_trade_ci95_high'))}; status: {u05.get('bootstrap_status')}.",
    f"- Net P&L at ₹10/order: {_fmt(u05.get('net_pnl_rupees'))}; mean/trade: {_fmt(u05.get('mean_net_per_trade'))}; median: {_fmt(u05.get('median_net_per_trade'))}; win rate: {_fmt(u05.get('win_rate'))}; PF: {_fmt(u05.get('profit_factor'))}; max trade drawdown: {_fmt(u05.get('max_trade_equity_drawdown_rupees'))}.",
    f"- Net at ₹20/order: {_fmt(u05.get('net_20_per_order'))}; +50% charges stress: {_fmt(u05.get('net_10_per_order_fee_stress_50pct'))}; ₹20/order + stress: {_fmt(u05.get('net_20_per_order_fee_stress_50pct'))}; extra hypothetical 0.25% each-side impact plus ₹50/trade (not specified by U05): {_fmt(u05.get('paper_025pct_each_side_plus_50_trade_cost_net'))}.",
    "- A zero-trade sample is NOT ESTIMABLE, never reported as evidence of zero return. This does not recreate the original source period.","",
    "## 4. U02 — machine-learning Buy/Sell option method",
    "The source label is implemented as next-session NIFTY close return greater than 1% = Buy; otherwise Sell. Train window ends in 2023; validation is 2024–2025. RF, XGBoost and a 5-session LSTM use fixed settings and no validation tuning. Features include past returns, moving-average gaps, RSI, realized volatility/range, ATM call/put premium ratios, straddle/spot ratio, days-to-expiry and log OI/volume if available. IV/Greeks are used only when they exist and are sufficiently populated in the training sample; missing features are not fabricated.",
    "A predicted Buy buys the nearest available ATM call; predicted Sell buys the nearest available ATM put on the next trading session. Entry uses the first matching underlying-option timestamp within 09:15–09:20; exit uses the last available 15:25–15:30 bar for that contract. Each model has a separate ₹1,00,000 account; position size compounds trade-by-trade, premium deployment is capped at 95% of current equity, and entry is blocked if one lot cannot be funded while preserving the 5% fee reserve.","",
    "### Prediction metrics","| Model | Status | Train rows | Validation rows | Accuracy | Balanced accuracy | Buy precision | Buy recall | F1 | ROC AUC | Always-sell accuracy |",
    "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in u02_metrics:
        lines.append("| "+" | ".join(str(x) for x in [r.get("model",""),r.get("status",""),r.get("training_rows",""),r.get("validation_rows",""),
          _fmt(r.get("accuracy")),_fmt(r.get("balanced_accuracy")),_fmt(r.get("precision_buy")),_fmt(r.get("recall_buy")),
          _fmt(r.get("f1_buy")),_fmt(r.get("roc_auc")),_fmt(r.get("always_sell_accuracy"))])+" |")
    lines += ["","### Costed options results","| Model | Trades | Net P&L ₹10/order | Mean/trade 95% block-bootstrap CI | Ending account equity ₹ | Account return % | Net ₹20/order sensitivity | +50% fee stress | Win rate | Max account drawdown ₹ |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in u02_summaries:
        ci = (f"{_fmt(r.get('mean_net_trade_ci95_low'))} to {_fmt(r.get('mean_net_trade_ci95_high'))}"
              if r.get("bootstrap_status") == "COMPUTED_CIRCULAR_MOVING_BLOCK_CI"
              else str(r.get("bootstrap_status", "NOT_ESTIMABLE")))
        lines.append("| "+" | ".join(str(x) for x in [r.get("model",""),r.get("completed_trades",0),_fmt(r.get("net_pnl_rupees")),
          ci,_fmt(r.get("ending_account_equity")),_fmt(r.get("account_return_pct")),
          _fmt(r.get("net_20_per_order")),_fmt(r.get("net_10_per_order_fee_stress_50pct")),
          _fmt(r.get("win_rate")),_fmt(r.get("max_account_drawdown_rupees"))])+ " |")
    lines += ["","### Model statuses"]
    for r in model_status: lines.append(f"- {r.get('model')}: {r.get('status')} — {r.get('error','')}")
    lines += ["",f"- Training/validation feature rows: {info.get('training_rows')} / {info.get('validation_rows')}.",
      "- Option bars are OHLC, not bid/ask/depth. This is a proxy model and not the original paper's exact reproduction.","",
      "## 5. Reconciled coverage of every uploaded PDF","| ID | Paper/method | Phase 101 status | Evidence and limitation |","|---|---|---|---|"]
    for r in matrix:
        lines.append(f"| {r['paper_id']} | {r['paper_or_method']} | {r['phase101_status']} | {r['evidence_and_limitation']} |")
    lines += ["","## 6. Costs and statistical inference",
      "The mean net P&L/trade confidence interval uses a deterministic circular moving-block bootstrap (5-trade blocks, 3,000 resamples), and is reported only for at least 20 completed trades. The seasonality sample has fewer than 20 trades, so no bootstrap precision is claimed. Fee-stress totals are alternative charge scenarios on the primary simulated position path, not separately re-sized equity curves.",
      "Baseline uses the repository’s date-effective charge helper, ₹10/order brokerage, one ₹0.05 adverse tick per fill, statutory/exchange fees and GST where implemented. Sensitivities add ₹20/order brokerage, +50% charge stress, and a paper-specific 0.25% adverse price impact per side plus ₹50/trade. These are simulated costs, not verified historical Paytm Money contract notes or proof of executable fills.",
      "Classification accuracy alone is not evidence of profitable trading. U02 accounting is sequential per-model equity rather than reusing the initial ₹1 lakh on every trade. Sparse trades, missing coverage and confidence intervals crossing zero are not robust evidence. No strategy is promoted.","",
      "## 7. Strengths and limitations",
      "Strengths: pinned provenance; chronological development/validation split; no 2026 option data; explicit opportunity exclusions; training-only feature eligibility/imputation; conservative handling of bars that hit both target and stop.",
      "Limitations: U02 and U05 do not recreate original paper periods or every undocumented choice; U05 expected-price arithmetic is ambiguous; full IV/Greeks/news inputs may be absent; OHLC cannot reproduce spread, depth, queue position, latency or broker contract notes; U06 remains blocked without point-in-time sentiment/news/FII/DII modalities.","",
      "## 8. Conclusion and future work",
      "Phase 101 adds two source-informed options strategy proxy tests to the previous forecasting, SMA/EMA, CCI and payoff-algebra screens. If no strategy satisfies coverage, sample-size, positive cost-stress and uncertainty criteria, no strategy is promoted. This is insufficient evidence, not proof that every PDF method is unprofitable. Future work requires authorized exact-period contracts, quote/depth data, verified broker charges, point-in-time external modalities and a new bounded plan.","",
      "## 9. Output files",
      "See paper_test_matrix.csv; u05_opportunity_audit.csv; u05_trade_ledger.csv; u05_summary.csv; u02_model_metrics.csv; u02_model_status.csv; u02_predictions.csv; u02_coverage_audit.csv; u02_trade_ledger.csv; u02_strategy_summary.csv; phase101_source_manifest.json; validation_report.json; net_pnl_comparison.svg."]
    (OUT/"PHASE101_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def _write_figure(u05,u02_summaries):
    import matplotlib.pyplot as plt
    vals=[]
    if u05.get("net_pnl_rupees") is not None: vals.append(("U05 seasonality",float(u05["net_pnl_rupees"])))
    for r in u02_summaries:
        if r.get("net_pnl_rupees") is not None: vals.append((f"U02 {r['model']}",float(r["net_pnl_rupees"])))
    fig,ax=plt.subplots(figsize=(9,4.5))
    if vals:
        ax.bar([x[0] for x in vals],[x[1] for x in vals]); ax.axhline(0,linewidth=.8)
        ax.tick_params(axis="x",rotation=25); ax.set_ylabel("Net P&L (₹; validation, ₹10/order)")
        ax.set_title("PDF-derived strategy proxy P&L — descriptive only")
    else:
        ax.text(.5,.5,"No completed trade sample; P&L not estimable",ha="center",va="center",transform=ax.transAxes); ax.set_axis_off()
    fig.tight_layout(); fig.savefig(OUT/"net_pnl_comparison.svg",format="svg"); plt.close(fig)

def run():
    OUT.mkdir(parents=True,exist_ok=True); errors=[]
    manifest={"dataset":HF_REPO,"revision":PINNED_REVISION,"license":"CC-BY-NC-4.0; aggregate derived results only",
      "date_window":{"start":"2021-05-27","end":"2025-12-31"},"holdout_2026_option_files_downloaded":0,"option_source_files_used":[]}
    try:
        p66=_get_p66()
        if p66.REVISION!=PINNED_REVISION: raise RuntimeError("Phase 66 pinned revision mismatch")
        from huggingface_hub import HfApi
        token=os.getenv("HF_TOKEN") or None; api=HfApi()
        monthly,files=p66.source_manifest(api,token)
        monthly={m:v for m,v in monthly.items() if pd.Timestamp(v[0]).date()<=pd.Timestamp("2025-12-31").date()}
        manifest["monthly_expiry_file_count"]=len(monthly); manifest["eligible_expiry_file_count"]=len(files)
        manifest["monthly_expiry_files"]=[{"month":m,"expiry":str(v[0].date()),"file":v[1]} for m,v in sorted(monthly.items())]
        ir,im=p66.load_pinned(api,token,"index/NIFTY.parquet"); manifest["underlying_file"]=im
        index=p66.normalize_index(ir); del ir; index=index.loc[index.timestamp<=VAL_END].copy()
        daily=_make_daily(index)
        manifest.update({"underlying_rows":int(len(index)),"underlying_sessions":int(len(daily)),
          "underlying_last_timestamp_used":str(index.timestamp.max()),
          "maximum_option_expiry_selected":str(max(pd.Timestamp(v[0]) for v in monthly.values()).date())})
        if manifest["maximum_option_expiry_selected"]>"2025-12-31": raise RuntimeError("2026 holdout guard failed")
        yahoo,returns=_load_yahoo(ROOT/".cache"/"phase101"/"yahoo_nifty_daily.csv")
        manifest.update({"yahoo_daily_rows":len(yahoo),"yahoo_daily_start":str(yahoo.index.min().date()),
          "yahoo_daily_end":str(yahoo.index.max().date())})
        u05tr,u05aud,u05sum=run_u05(p66,api,token,monthly,index,daily,returns,manifest)
        pd.DataFrame(u05tr).to_csv(OUT/"u05_trade_ledger.csv",index=False)
        pd.DataFrame(u05aud).to_csv(OUT/"u05_opportunity_audit.csv",index=False)
        pd.DataFrame([u05sum]).to_csv(OUT/"u05_summary.csv",index=False)
        frame=build_u02_frame(p66,api,token,monthly,index,daily,manifest)
        preds,metrics,status,info=predict_models(frame)
        pd.DataFrame(preds).to_csv(OUT/"u02_predictions.csv",index=False)
        pd.DataFrame(metrics).to_csv(OUT/"u02_model_metrics.csv",index=False)
        pd.DataFrame(status).to_csv(OUT/"u02_model_status.csv",index=False)
        write_json(OUT/"u02_feature_manifest.json",{"eligible_features":info.get("eligible_features",[]),
          "all_candidate_features":info.get("all_candidate_features",[]),"training_rows":info.get("training_rows"),
          "validation_rows":info.get("validation_rows"),"training_positive_rate":info.get("training_positive_rate"),
          "validation_positive_rate":info.get("validation_positive_rate"),
          "feature_selection":"eligible only when >=50% of training rows non-missing and variable"})
        u02tr,u02aud=simulate_u02(p66,api,token,monthly,index,preds,manifest)
        pd.DataFrame(u02tr).to_csv(OUT/"u02_trade_ledger.csv",index=False)
        pd.DataFrame(u02aud).to_csv(OUT/"u02_coverage_audit.csv",index=False)
        sums=[]
        models=sorted(set([r["model"] for r in preds]+[r.get("model","") for r in metrics]))
        for m in models:
            tt=sorted([r for r in u02tr if r["model"]==m], key=lambda x:x["entry_date"])
            mm=net_trade_metrics([r["net_10_per_order"] for r in tt])
            ending=float(tt[-1]["account_equity_after"]) if tt else float(CAPITAL_U02)
            s={"paper_id":"U02","model":m,**mm,
               "initial_account_equity":float(CAPITAL_U02),
               "ending_account_equity":ending,
               "account_return_pct":100.0*(ending/CAPITAL_U02-1.0),
               "max_account_drawdown_rupees":float(max((r["account_drawdown_from_peak"] for r in tt),default=0.0)),
               "premium_deployment_cap_pct":95.0}
            for k in ["net_20_per_order","net_10_per_order_fee_stress_50pct","net_20_per_order_fee_stress_50pct","paper_025pct_each_side_plus_50_trade_cost_net"]:
                s[k]=float(sum(x[k] for x in tt)) if tt else None
            s["coverage_status_counts"]=dict(Counter(x.get("status","") for x in u02aud if x.get("model")==m)); sums.append(s)
        pd.DataFrame(sums).to_csv(OUT/"u02_strategy_summary.csv",index=False)
        manifest["unique_option_files_read"]=len(set(x["path"] for x in manifest["option_source_files_used"]))
        manifest["u05_trade_count"]=len(u05tr); manifest["u02_prediction_count"]=len(preds); manifest["u02_trade_count"]=len(u02tr)
        manifest["model_status_counts"]=dict(Counter(x.get("status","") for x in status)); manifest["model_info"]=info
        write_json(OUT/"phase101_source_manifest.json",manifest)
        matrix=paper_matrix(metrics,u05sum); pd.DataFrame(matrix).to_csv(OUT/"paper_test_matrix.csv",index=False)
        validation={"phase":101,"overall_status":"COMPLETED_WITH_EXPLICIT_LIMITATIONS","paper_rows":len(matrix),
          "expected_paper_rows":14,"u05_opportunity_rows":len(u05aud),"u05_trade_rows":len(u05tr),
          "u02_metric_rows":len(metrics),"u02_predictions":len(preds),"u02_trade_rows":len(u02tr),
          "holdout_2026_option_files_downloaded":0,"latest_underlying_timestamp":manifest["underlying_last_timestamp_used"],
          "max_selected_expiry":manifest["maximum_option_expiry_selected"],"zero_trade_metric_policy":"NOT_ESTIMABLE_ZERO_TRADES",
          "strategy_promoted":False,"limitations":["U02 and U05 are proxy tests, not exact original-period replications",
          "U06 external modalities remain blocked","U07 payoff algebra and prior Phase 95/96/66 outcomes are carried forward"]}
        if len(matrix)!=14: raise RuntimeError("paper matrix requires 14 rows")
        if manifest["holdout_2026_option_files_downloaded"]!=0: raise RuntimeError("holdout guard failed")
        write_json(OUT/"validation_report.json",validation)
        _write_report(matrix,u05sum,metrics,sums,status,info,manifest,validation); _write_figure(u05sum,sums)
    except Exception as exc:
        errors.append({"type":type(exc).__name__,"error":str(exc),"traceback":traceback.format_exc()[-8000:]})
        write_json(OUT/"phase101_runtime_error.json",{"status":"DATA_OR_RUNTIME_BLOCKED","errors":errors,
          "strategy_promoted":False,"holdout_2026_option_files_downloaded":0})
        raise
    finally:
        if errors:
            with (OUT/"phase101_error_rows.jsonl").open("a",encoding="utf-8") as f:
                for e in errors: f.write(json.dumps(e)+"\n")

if __name__=="__main__": run()
