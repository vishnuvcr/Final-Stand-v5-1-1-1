import json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import ndtr

from phase43_vix_strategy_sweep import (
    TZ, START, END, DEV_END, VAL_END,
    load_parquet, load_vix, vix_state,
    charges, exec_px, lot_size_for_expiry
)

TT07_ENGINE_REV = "50B-TT07-COVERAGE-V2"
OUT = Path("results/phase50b/tt07_dynamic_ic_ratio_replay")
OUT.mkdir(parents=True, exist_ok=True)

ENTRY_START = pd.Timestamp("09:20").time()
ENTRY_END = pd.Timestamp("15:29").time()
EXIT_START = pd.Timestamp("15:15").time()
R = 0.0

INDEX = None
EXPIRIES = None
OPTION_CACHE = {}

STATE_SPECS = {
    0: [("CE", 0.30, -1), ("PE", -0.30, -1), ("CE", 0.10, +1), ("PE", -0.10, +1)],
    1: [("CE", 0.50, +1), ("CE", 0.40, -2), ("CE", 0.10, +1)],
    2: [("PE", -0.50, +1), ("PE", -0.40, -2), ("PE", -0.10, +1)],
    3: [("CE", 0.40, +1), ("CE", 0.30, -2), ("CE", 0.08, +1)],
    4: [("PE", -0.40, +1), ("PE", -0.30, -2), ("PE", -0.08, +1)],
    5: [("CE", 0.40, +1), ("CE", 0.30, -2), ("CE", 0.08, +1)],
    6: [("PE", -0.40, +1), ("PE", -0.30, -2), ("PE", -0.08, +1)],
}

TRANSITIONS = {
    0: {"low_ce": 1, "low_pe": 2},
    1: {"low": 3, "high": 2},
    2: {"low": 4, "high": 1},
    3: {"low": 5, "high": 2},
    4: {"low": 6, "high": 1},
    5: {"low": 3},
    6: {"low": 4},
}

def clean_ts(df):
    x = df.copy()
    x["timestamp"] = pd.to_datetime(x["timestamp"])
    if x["timestamp"].dt.tz is None:
        x["timestamp"] = x["timestamp"].dt.tz_localize(TZ)
    else:
        x["timestamp"] = x["timestamp"].dt.tz_convert(TZ)
    x["strike"] = pd.to_numeric(x["strike"], errors="coerce")
    x["close"] = pd.to_numeric(x["close"], errors="coerce")
    x["option_type"] = x["option_type"].astype(str).str.upper()
    x = x.dropna(subset=["timestamp", "strike", "close"])
    return x.sort_values(["timestamp", "option_type", "strike"]).set_index("timestamp", drop=False)

def get_index():
    global INDEX
    if INDEX is None:
        x = load_parquet("index/NIFTY.parquet")
        x = x[["timestamp", "close"]].rename(columns={"close": "spot"})
        x = x.drop_duplicates("timestamp").sort_values("timestamp")
        INDEX = x
    return INDEX

def get_expiries():
    global EXPIRIES
    if EXPIRIES is None:
        z = pd.read_csv("results/phase43_vix/strategy_trade_matrix_all_splits.csv", usecols=["expiry"])
        EXPIRIES = sorted({pd.Timestamp(v).tz_localize(TZ) for v in z["expiry"].dropna()})
    return EXPIRIES

def get_option(expiry):
    if expiry not in OPTION_CACHE:
        OPTION_CACHE[expiry] = clean_ts(
            load_parquet(f"options/NIFTY/{expiry.strftime('%Y-%m-%d')}.parquet")
        )
    return OPTION_CACHE[expiry]

def snapshot(df, ts):
    try:
        z = df.loc[pd.Timestamp(ts)]
    except KeyError:
        return df.iloc[0:0]
    if isinstance(z, pd.Series):
        z = z.to_frame().T
    return z.drop_duplicates(["option_type", "strike"], keep="last")

def quote(z, opt, strike):
    if z is None or z.empty or strike is None:
        return None
    q = z[(z.option_type == opt) & np.isclose(z.strike, float(strike), rtol=0, atol=1e-8)]
    return None if q.empty else float(q.iloc[-1].close)

def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def bs_price(s, k, t, sigma, call):
    if t <= 0:
        return max(s-k, 0.0) if call else max(k-s, 0.0)
    if sigma <= 0:
        return math.exp(-R*t) * (max(s-k, 0.0) if call else max(k-s, 0.0))
    q = math.sqrt(t)
    d1 = (math.log(s/k) + (R + 0.5*sigma*sigma)*t) / (sigma*q)
    d2 = d1 - sigma*q
    if call:
        return s*norm_cdf(d1) - k*math.exp(-R*t)*norm_cdf(d2)
    return k*math.exp(-R*t)*norm_cdf(-d2) - s*norm_cdf(-d1)

def bs_delta(s, k, t, sigma, call):
    if t <= 0:
        if call:
            return 1.0 if s > k else 0.0
        return -1.0 if s < k else 0.0
    d1 = (math.log(s/k) + (R + 0.5*sigma*sigma)*t) / (sigma*math.sqrt(t))
    return norm_cdf(d1) if call else norm_cdf(d1) - 1.0

def nearest_delta(z, spot, ts, expiry, opt, target):
    q = z[z.option_type == opt][["strike", "close"]].drop_duplicates("strike")
    if q.empty or not np.isfinite(spot) or spot <= 0:
        return None
    k = q.strike.to_numpy(dtype=float)
    p = q.close.to_numpy(dtype=float)
    t = max(
        (expiry.normalize() + pd.Timedelta(hours=15, minutes=30) - pd.Timestamp(ts)).total_seconds(),
        1.0
    ) / (365*24*3600)
    valid = np.isfinite(k) & np.isfinite(p) & (k > 0) & (p > 0)
    if not np.any(valid):
        return None
    k, p = k[valid], p[valid]
    intrinsic = np.maximum(spot-k, 0.0) if opt == "CE" else np.maximum(k-spot, 0.0)
    upper = np.full_like(k, spot) if opt == "CE" else k
    valid2 = (p > intrinsic + 1e-8) & (p < upper)
    if not np.any(valid2):
        return None
    k, p = k[valid2], p[valid2]
    sigma = np.clip(np.sqrt(2*np.pi/max(t, 1e-12))*p/max(spot, 1e-9), 0.05, 2.5)
    sqrt_t = math.sqrt(t)
    disc = math.exp(-R*t)
    for _ in range(7):
        d1 = (np.log(spot/k) + (R + 0.5*sigma*sigma)*t) / (sigma*sqrt_t)
        d2 = d1 - sigma*sqrt_t
        if opt == "CE":
            model = spot*ndtr(d1) - k*disc*ndtr(d2)
        else:
            model = k*disc*ndtr(-d2) - spot*ndtr(-d1)
        diff = model - p
        vega = spot*np.exp(-0.5*d1*d1)/math.sqrt(2*np.pi)*sqrt_t
        good = vega > 1e-10
        if not np.any(good):
            break
        sigma = np.where(good, np.clip(sigma-diff/vega, 1e-5, 8.0), sigma)
    d1 = (np.log(spot/k) + (R + 0.5*sigma*sigma)*t) / (sigma*sqrt_t)
    delta = ndtr(d1) if opt == "CE" else ndtr(d1) - 1.0
    err = np.abs(delta - target)
    best = np.nanmin(err)
    candidates = k[np.isclose(err, best, rtol=0, atol=1e-12)]
    return float(np.min(candidates))

def build_state(state, z, spot, ts, expiry):
    raw = STATE_SPECS[state]
    legs = {}
    for opt, target, qty in raw:
        strike = nearest_delta(z, spot, ts, expiry, opt, target)
        if strike is None:
            return None
        key = (opt, float(strike))
        legs[key] = legs.get(key, 0) + qty
    legs = {k:int(q) for k,q in legs.items() if q != 0}
    if not legs:
        return None
    if any(quote(z, opt, strike) is None for (opt, strike) in legs):
        return None
    return legs

def leg_quote_complete(legs, z):
    return bool(legs) and all(quote(z, opt, strike) is not None for (opt, strike) in legs)

def execute_open_close(position, new_legs, ts, z, lot):
    # Transactional transition: validate every exit and entry quote before
    # mutating cash or the live-leg ledger. This prevents partial cash mutation
    # if a later leg is missing at the transition timestamp.
    old_legs = list(position["legs"].items())
    new_legs = list(new_legs.items())
    for (opt, strike), _qty in old_legs + new_legs:
        if quote(z, opt, strike) is None:
            return False

    orders = []
    cash_delta = 0.0
    for (opt, strike), qty in old_legs:
        px = quote(z, opt, strike)
        side = "sell" if qty > 0 else "buy"
        ep = exec_px(px, side)
        cash_delta += (ep if side == "sell" else -ep) * abs(qty) * lot
        orders.append((pd.Timestamp(ts), side, ep*abs(qty)))

    for (opt, strike), qty in new_legs:
        px = quote(z, opt, strike)
        side = "buy" if qty > 0 else "sell"
        ep = exec_px(px, side)
        cash_delta += (-ep if side == "buy" else ep) * abs(qty) * lot
        orders.append((pd.Timestamp(ts), side, ep*abs(qty)))

    position["cash"] += cash_delta
    position["legs"] = dict(new_legs)
    position["orders"].extend(orders)
    return True

def enter_position(state, ts, spot, expiry, z, lot, vix):
    legs = build_state(state, z, spot, ts, expiry)
    if legs is None:
        return None
    pos = {
        "state": int(state),
        "legs": dict(legs),
        "cash": 0.0,
        "orders": [],
        "lot": lot,
        "entry_ts": pd.Timestamp(ts),
        "entry_spot": float(spot),
        "expiry": expiry,
        "vix": vix["vix"] if vix else np.nan,
        "vix_state": vix["level_state"] if vix else None,
        "states_path": [int(state)],
        "transition_count": 0,
    }
    for (opt, strike), qty in legs.items():
        px = quote(z, opt, strike)
        side = "buy" if qty > 0 else "sell"
        ep = exec_px(px, side)
        pos["cash"] += (-ep if side == "buy" else ep) * abs(qty) * lot
        pos["orders"].append((pd.Timestamp(ts), side, ep*abs(qty)))
    return pos

def transition_trigger(pos, z, spot, ts, expiry):
    state = pos["state"]
    if state == 0:
        # Evaluate the two short legs that were actually opened at entry.
        for opt, transition_name in [("CE","low_ce"), ("PE","low_pe")]:
            short_legs = [
                (strike, qty) for (o, strike), qty in pos["legs"].items()
                if o == opt and qty < 0
            ]
            if not short_legs:
                continue
            strike = short_legs[0][0]
            px = quote(z, opt, strike)
            if px is None:
                continue
            d = option_delta(px, spot, strike, ts, expiry, opt)
            if d is not None and abs(d) <= 0.10:
                return TRANSITIONS[state].get(transition_name)
        return None

    short_opt = {
        1:"CE", 2:"PE", 3:"CE", 4:"PE", 5:"CE", 6:"PE"
    }[state]
    short_legs = [
        (strike, qty) for (opt, strike), qty in pos["legs"].items()
        if opt == short_opt and qty < 0
    ]
    if not short_legs:
        return None
    strike = short_legs[0][0]
    px = quote(z, short_opt, strike)
    if px is None:
        return None
    d = option_delta(px, spot, strike, ts, expiry, short_opt)
    if d is None:
        return None
    if abs(d) <= 0.10:
        return TRANSITIONS[state].get("low")
    if abs(d) >= 0.65:
        return TRANSITIONS[state].get("high")
    return None

def option_delta(price, spot, strike, ts, expiry, opt):
    if not all(np.isfinite(v) for v in [price, spot, strike]) or price <= 0 or spot <= 0 or strike <= 0:
        return None
    t = max(
        (expiry.normalize() + pd.Timedelta(hours=15, minutes=30) - pd.Timestamp(ts)).total_seconds(),
        1.0
    ) / (365*24*3600)
    intrinsic = math.exp(-R*t)*max(spot-strike, 0.0) if opt == "CE" else math.exp(-R*t)*max(strike-spot, 0.0)
    upper = spot if opt == "CE" else strike*math.exp(-R*t)
    if price <= intrinsic + 1e-8 or price >= upper:
        return None
    sigma = float(np.clip(np.sqrt(2*np.pi/max(t,1e-12))*price/max(spot,1e-9), 0.05, 2.5))
    q = math.sqrt(t)
    disc = math.exp(-R*t)
    for _ in range(7):
        d1 = (math.log(spot/strike) + (R + 0.5*sigma*sigma)*t) / (sigma*q)
        d2 = d1 - sigma*q
        model = (
            spot*norm_cdf(d1) - strike*disc*norm_cdf(d2)
            if opt == "CE"
            else strike*disc*norm_cdf(-d2) - spot*norm_cdf(-d1)
        )
        diff = model-price
        vega = spot*math.exp(-0.5*d1*d1)/math.sqrt(2*math.pi)*q
        if vega < 1e-10:
            break
        sigma = max(1e-5, min(8.0, sigma-diff/vega))
    return bs_delta(spot, strike, t, sigma, opt == "CE")

def close_position(pos, ts, z):
    if not leg_quote_complete(pos["legs"], z):
        return None
    gross = pos["cash"]
    orders = list(pos["orders"])
    for (opt, strike), qty in pos["legs"].items():
        px = quote(z, opt, strike)
        side = "sell" if qty > 0 else "buy"
        ep = exec_px(px, side)
        gross += (ep if side == "sell" else -ep) * abs(qty) * pos["lot"]
        orders.append((pd.Timestamp(ts), side, ep*abs(qty)))
    cost = charges(orders, pos["lot"], 1.0)
    cost50 = charges(orders, pos["lot"], 1.5)
    cost20 = charges(orders, pos["lot"], 1.0, brokerage_per_order=20.0)
    cost20_50 = charges(orders, pos["lot"], 1.5, brokerage_per_order=20.0)
    return {
        "expiry": str(pos["expiry"].date()),
        "entry_ts": str(pos["entry_ts"]),
        "exit_ts": str(ts),
        "entry_spot": pos["entry_spot"],
        "lot": pos["lot"],
        "gross": gross,
        "cost": cost,
        "net": gross-cost,
        "net50": gross-cost50,
        "net20": gross-cost20,
        "net20_50": gross-cost20_50,
        "vix": pos["vix"],
        "vix_state": pos["vix_state"],
        "transitions": pos["transition_count"],
        "states_path": "->".join(map(str,pos["states_path"])),
    }

def monthly_expiries(all_expiries):
    by_month = {}
    for e in all_expiries:
        key = (e.year, e.month)
        by_month[key] = max(by_month.get(key, e), e)
    return [by_month[k] for k in sorted(by_month)]

def campaign_entry_day(monthly, i, index):
    mexp = monthly[i]
    if i == 0:
        dates = index[(index.timestamp.dt.year == mexp.year) &
                      (index.timestamp.dt.month == mexp.month) &
                      (index.timestamp.dt.weekday == 4)].timestamp.dt.normalize().unique()
    else:
        prev = monthly[i-1]
        dates = index[(index.timestamp.dt.normalize() > prev.normalize()) &
                      (index.timestamp.dt.normalize() < mexp.normalize()) &
                      (index.timestamp.dt.weekday == 4)].timestamp.dt.normalize().unique()
    if len(dates) == 0:
        return None
    return pd.Timestamp(sorted(dates)[0]).tz_localize(TZ) if pd.Timestamp(sorted(dates)[0]).tzinfo is None else pd.Timestamp(sorted(dates)[0])

def main():
    index = get_index()
    vix = load_vix()
    monthly = [e for e in monthly_expiries(get_expiries()) if START <= e <= END]

    rows = []
    gaps = []
    errors = []
    transition_diag = []
    entry_exclusions = []
    trade_id = 1

    for i, mexp in enumerate(monthly):
        entry_day = campaign_entry_day(monthly, i, index)
        if entry_day is None or entry_day >= mexp.normalize():
            entry_exclusions.append({"expiry":str(mexp.date()),"reason":"no_valid_source_friday_entry_day"})
            continue
        regular=index[(index.timestamp.dt.normalize()==entry_day.normalize())&
                      (index.timestamp.dt.time>=pd.Timestamp("09:15").time())&
                      (index.timestamp.dt.time<=pd.Timestamp("15:30").time())]
        if regular.empty:
            entry_exclusions.append({"expiry":str(mexp.date()),"reason":"no_normal_09:15_to_15:30_session"})
            continue
        try:
            chain = get_option(mexp)
        except Exception as exc:
            errors.append({"expiry":str(mexp.date()),"error":f"load option chain: {exc}"})
            gaps.append({"trade_id":trade_id,"expiry":str(mexp.date()),"entry_ts":str(entry_day.date()),"gap_type":"missing_entry_option_chain"})
            trade_id += 1
            continue

        dayidx = index[(index.timestamp.dt.normalize() == entry_day.normalize()) &
                       (index.timestamp.dt.time >= ENTRY_START) &
                       (index.timestamp.dt.time <= ENTRY_END)]
        pos = None
        entry_vix = None
        entered=False
        for ts in dayidx.timestamp.tolist():
            ts = pd.Timestamp(ts)
            z = snapshot(chain, ts)
            if pos is None:
                spot = float(index.loc[index.timestamp == ts].iloc[-1].spot)
                pos = enter_position(0, ts, spot, mexp, z, lot_size_for_expiry(mexp), vix_state(vix, ts))
                if pos is None:
                    continue
                pos["trade_id"] = trade_id
                trade_id += 1
                entered=True
                entry_vix = pos["vix_state"]
                continue

        if pos is None:
            if not entered:
                gaps.append({"trade_id":trade_id,"expiry":str(mexp.date()),
                             "entry_ts":str(entry_day.date()),
                             "gap_type":"missing_complete_initial_ic_entry_at_or_after_09:20"})
                trade_id += 1
            continue

        # Re-scan from entry to expiry using observed index timestamps.
        obs = index[(index.timestamp >= pos["entry_ts"]) & (index.timestamp <= mexp.normalize()+pd.Timedelta(hours=15,minutes=29))]
        for ts in obs.timestamp.tolist():
            ts = pd.Timestamp(ts)
            z = snapshot(chain, ts)
            if z.empty:
                continue
            spot = float(index.loc[index.timestamp == ts].iloc[-1].spot)

            if ts.normalize() == mexp.normalize() and ts.time() >= EXIT_START:
                if leg_quote_complete(pos["legs"], z):
                    out = close_position(pos, ts, z)
                    if out is not None:
                        rows.append(dict(trade_id=pos["trade_id"], **out))
                        pos = None
                        break
                continue

            nxt = transition_trigger(pos, z, spot, ts, mexp)
            if nxt is None:
                continue

            target = build_state(nxt, z, spot, ts, mexp)
            if target is None or not leg_quote_complete(target, z):
                transition_diag.append({
                    "trade_id":pos["trade_id"],"timestamp":str(ts),
                    "from_state":pos["state"],"target_state":nxt,
                    "reason":"incomplete_target_state_quotes"
                })
                continue

            old_state = pos["state"]
            ok = execute_open_close(pos, target, ts, z, pos["lot"])
            if not ok:
                transition_diag.append({
                    "trade_id":pos["trade_id"],"timestamp":str(ts),
                    "from_state":old_state,"target_state":nxt,
                    "reason":"transition_execution_quote_gap"
                })
                continue
            pos["state"] = int(nxt)
            pos["states_path"].append(int(nxt))
            pos["transition_count"] += 1
            continue

        if pos is not None:
            gaps.append({
                "trade_id":pos["trade_id"],
                "expiry":str(mexp.date()),
                "entry_ts":str(pos["entry_ts"]),
                "gap_type":"missing_complete_universal_exit_quote"
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(OUT/"tt07_trades.csv", index=False)
    else:
        pd.DataFrame(columns=["trade_id","expiry","entry_ts","exit_ts","net","net50","net20","net20_50","vix_state"]).to_csv(OUT/"tt07_trades.csv", index=False)
    pd.DataFrame(gaps, columns=["trade_id","expiry","entry_ts","gap_type"]).to_csv(OUT/"coverage_gaps.csv", index=False)
    pd.DataFrame(entry_exclusions,columns=["expiry","reason"]).to_csv(OUT/"entry_exclusions.csv",index=False)
    pd.DataFrame(errors, columns=["expiry","error"]).to_csv(OUT/"data_errors.csv", index=False)
    pd.DataFrame(transition_diag).to_csv(OUT/"transition_diagnostics.csv", index=False)

    expiry_series = pd.to_datetime(df["expiry"], utc=True).dt.tz_convert(TZ) if not df.empty else pd.Series(dtype=f"datetime64[ns,{TZ}]")
    splits = []
    for name, mask in [
        ("DEV", expiry_series <= DEV_END),
        ("VAL", (expiry_series > DEV_END) & (expiry_series <= VAL_END)),
        ("HOLD", expiry_series > VAL_END),
    ]:
        z = df[mask] if not df.empty else df
        splits.append({
            "split":name,"trades":len(z),
            "net":float(z.net.sum()) if len(z) else 0.0,
            "net50":float(z.net50.sum()) if len(z) else 0.0,
            "net20":float(z.net20.sum()) if len(z) else 0.0,
            "net20_50":float(z.net20_50.sum()) if len(z) else 0.0,
            "win_rate":float(z.net.gt(0).mean()) if len(z) else 0.0
        })
    pd.DataFrame(splits).to_csv(OUT/"split_summary.csv", index=False)

    if not df.empty:
        vx = df.groupby("vix_state").agg(
            trades=("net","size"), net=("net","sum"), net50=("net50","sum"),
            net20=("net20","sum"), net20_50=("net20_50","sum"),
            mean=("net","mean"), win_rate=("net", lambda s: float(s.gt(0).mean()))
        ).reset_index()
        vx.to_csv(OUT/"vix_summary.csv", index=False)
        by_state = df.groupby("states_path").agg(trades=("net","size"),net=("net","sum")).reset_index()
        by_state.to_csv(OUT/"state_path_summary.csv", index=False)
    else:
        pd.DataFrame(columns=["vix_state","trades","net","net50","net20","net20_50","mean","win_rate"]).to_csv(OUT/"vix_summary.csv", index=False)
        pd.DataFrame(columns=["states_path","trades","net"]).to_csv(OUT/"state_path_summary.csv", index=False)

    candidate = len(df) + len(gaps)
    summary = {
        "strategy":"TT-07",
        "engine_revision":TT07_ENGINE_REV,
        "trades":len(df),
        "candidate_trades":candidate,
        "coverage_exclusions":len(gaps),"entry_exclusions":len(entry_exclusions),
        "coverage_rate":len(df)/candidate if candidate else 0.0,
        "transition_diagnostic_rows":len(transition_diag),
        "net":float(df.net.sum()) if not df.empty else 0.0,
        "net50":float(df.net50.sum()) if not df.empty else 0.0,
        "net20":float(df.net20.sum()) if not df.empty else 0.0,
        "net20_50":float(df.net20_50.sum()) if not df.empty else 0.0,
        "by_vix":(df.groupby("vix_state").agg(
            trades=("net","size"),net=("net","sum"),net50=("net50","sum"),
            net20=("net20","sum"),net20_50=("net20_50","sum")
        ).reset_index().to_dict("records") if not df.empty else [])
    }
    (OUT/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
