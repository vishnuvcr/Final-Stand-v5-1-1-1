import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from research.stop_loss_research import build_paths
from research.backtest_dynamic_n_corrected import TZ, load, normalize, exec_px, charges

OUT = Path(os.getenv("OUT_DIR", "results/dynamic_n_corrected/phase21_adverse_move_risk_control"))
TRAIN_END = pd.Timestamp("2023-12-31", tz=TZ)
VALIDATION_END = pd.Timestamp("2025-12-31", tz=TZ)
HOLDOUT_START = pd.Timestamp("2026-01-01", tz=TZ)

MOVE_THRESHOLDS = [200, 300, 400, 500, 600]
CONFIRM_BARS = [1, 5, 15]
SIGNAL_FAMILIES = ["spot_only", "negative_mtm", "negative_mtm_mfe50"]
HEDGE_POLICIES = ["target_or_baseline", "recover_zero_or_baseline"]


def max_dd(values):
    running = peak = dd = 0.0
    for x in values:
        running += float(x)
        peak = max(peak, running)
        dd = max(dd, peak - running)
    return dd


def stats(df):
    if df.empty:
        return dict(trades=0, base_net=0.0, candidate_net=0.0, net_uplift=0.0,
                    max_dd=0.0, base_dd=0.0, dd_change=0.0, adjustments=0,
                    winner_affected=0, loss_reduction=0.0, losses_eliminated=0,
                    worst_trade=0.0, p05_trade=0.0, hedge_gaps=0)
    loss_mask = df.base_net < 0
    return dict(
        trades=int(len(df)),
        base_net=float(df.base_net.sum()),
        candidate_net=float(df.candidate_net.sum()),
        net_uplift=float(df.net_uplift.sum()),
        max_dd=max_dd(df.candidate_net.tolist()),
        base_dd=max_dd(df.base_net.tolist()),
        dd_change=max_dd(df.candidate_net.tolist()) - max_dd(df.base_net.tolist()),
        adjustments=int(df.adjusted.sum()),
        winner_affected=int(df.winner_affected.sum()),
        loss_reduction=float(np.maximum(df.loc[loss_mask, "candidate_net"] - df.loc[loss_mask, "base_net"], 0.0).sum()),
        losses_eliminated=int(df.loss_eliminated.sum()),
        worst_trade=float(df.candidate_net.min()),
        p05_trade=float(df.candidate_net.quantile(0.05)),
        hedge_gaps=int(df.hedge_gap.sum()),
    )


def phase19_idx(t):
    expiry_date = pd.Timestamp(t["expiry"], tz=TZ).date()
    for i, p in enumerate(t["path"]):
        ts = pd.Timestamp(p["ts"])
        if (ts.date() == expiry_date and
            (ts.hour > 13 or (ts.hour == 13 and ts.minute >= 30)) and
            p["gross"] < 0 and p["mfe"] < 0.50 * t["target"]):
            return i
    return len(t["path"]) - 1


def load_spot():
    s = load("index/NIFTY.parquet")[["timestamp", "close"]].rename(columns={"close": "spot"})
    return s.set_index("timestamp")["spot"].to_dict()


def enrich(trades, spot_map):
    cache, out, errors = {}, [], []
    for t in trades:
        expiry = t["expiry"]
        try:
            if expiry not in cache:
                cache[expiry] = normalize(load(f"options/NIFTY/{expiry}.parquet"))
        except Exception as e:
            errors.append({"expiry": expiry, "error": repr(e)})
            continue
        df = cache[expiry]
        hedge_k = int(t["strikes"][0]) + 150 if t["option_type"] == "CE" else int(t["strikes"][0]) - 150
        q = df[(df.timestamp >= pd.Timestamp(t["entry_ts"])) &
               (df.timestamp <= pd.Timestamp(t["path"][-1]["ts"])) &
               (df.option_type == t["option_type"]) &
               (df.strike == hedge_k)]
        hedge_map = q.groupby("timestamp")["close"].last().to_dict() if not q.empty else {}
        entry_spot = spot_map.get(pd.Timestamp(t["entry_ts"]))
        if entry_spot is None:
            errors.append({"expiry": expiry, "error": "missing entry spot"})
            continue
        path = []
        for p in t["path"]:
            ts = pd.Timestamp(p["ts"])
            spot = spot_map.get(ts)
            if spot is None:
                continue
            path.append({**p, "spot": float(spot),
                         "hedge_raw": float(hedge_map[ts]) if ts in hedge_map else np.nan})
        if not path:
            errors.append({"expiry": expiry, "error": "no exact spot alignment"})
            continue
        for p in path:
            p["adverse_move"] = (p["spot"] - entry_spot) if t["direction"] == "BEARISH" else (entry_spot - p["spot"])
        out.append({**t, "entry_spot": float(entry_spot), "hedge_strike": hedge_k, "path": path})
    return out, errors


def baseline_rows(trades):
    rows = {}
    for t in trades:
        i = phase19_idx(t)
        p = t["path"][i]
        raw = p["raw_exit"]
        xp = (exec_px(raw[0], "sell"), exec_px(raw[1], "buy"), exec_px(raw[2], "buy"))
        e = pd.Timestamp(t["entry_ts"]); x = pd.Timestamp(p["ts"])
        entry_orders = [(e, "buy", t["entry_exec"][0]), (e, "sell", t["entry_exec"][1]), (e, "sell", t["entry_exec"][2])]
        exit_orders = [(x, "sell", xp[0]), (x, "buy", xp[1]), (x, "buy", xp[2])]
        rows[t["expiry"]] = {
            "base_net": float(p["gross"]) - charges(entry_orders, exit_orders, t["lot"]),
            "base_exit_ts": x,
        }
    return rows


def trigger_idx(t, threshold, family, confirm):
    def cond(p):
        if p["adverse_move"] < threshold:
            return False
        if family in ("negative_mtm", "negative_mtm_mfe50") and p["gross"] >= 0:
            return False
        if family == "negative_mtm_mfe50" and p["mfe"] >= 0.50 * t["target"]:
            return False
        return True
    path = t["path"]
    if confirm == 1:
        for i, p in enumerate(path):
            if cond(p):
                return i
        return None
    for i in range(len(path) - confirm + 1):
        ok = True
        for j in range(confirm):
            if not cond(path[i + j]):
                ok = False; break
            if j and (pd.Timestamp(path[i+j]["ts"]) - pd.Timestamp(path[i+j-1]["ts"])).total_seconds() != 60:
                ok = False; break
        if ok:
            return i
    return None


def original_net(t, p):
    raw = p["raw_exit"]
    xp = (exec_px(raw[0], "sell"), exec_px(raw[1], "buy"), exec_px(raw[2], "buy"))
    e = pd.Timestamp(t["entry_ts"]); x = pd.Timestamp(p["ts"])
    oe = [(e, "buy", t["entry_exec"][0]), (e, "sell", t["entry_exec"][1]), (e, "sell", t["entry_exec"][2])]
    ox = [(x, "sell", xp[0]), (x, "buy", xp[1]), (x, "buy", xp[2])]
    return float(p["gross"]) - charges(oe, ox, t["lot"])


def eval_stop(trades, base, thr, family, confirm):
    rows = []
    for t in trades:
        b = base[t["expiry"]]
        i = trigger_idx(t, thr, family, confirm)
        if i is None or pd.Timestamp(t["path"][i]["ts"]) >= b["base_exit_ts"]:
            rows.append({"expiry":t["expiry"],"base_net":b["base_net"],"candidate_net":b["base_net"],"net_uplift":0.0,"adjusted":False,"winner_affected":False,"loss_eliminated":False,"hedge_gap":False})
            continue
        p = t["path"][i]; net = original_net(t,p)
        rows.append({"expiry":t["expiry"],"base_net":b["base_net"],"candidate_net":net,"net_uplift":net-b["base_net"],"adjusted":True,"winner_affected":b["base_net"]>0,"loss_eliminated":b["base_net"]<0 and net>=0,"hedge_gap":False})
    return pd.DataFrame(rows)


def eval_hedge(trades, base, thr, family, confirm, policy):
    rows = []
    for t in trades:
        b = base[t["expiry"]]
        i = trigger_idx(t, thr, family, confirm)
        if i is None or pd.Timestamp(t["path"][i]["ts"]) >= b["base_exit_ts"]:
            rows.append({"expiry":t["expiry"],"base_net":b["base_net"],"candidate_net":b["base_net"],"net_uplift":0.0,"adjusted":False,"winner_affected":False,"loss_eliminated":False,"hedge_gap":False})
            continue
        tp = t["path"][i]
        if not np.isfinite(tp["hedge_raw"]):
            rows.append({"expiry":t["expiry"],"base_net":b["base_net"],"candidate_net":b["base_net"],"net_uplift":0.0,"adjusted":True,"winner_affected":b["base_net"]>0,"loss_eliminated":False,"hedge_gap":True})
            continue
        hedge_buy = exec_px(tp["hedge_raw"], "buy")
        candidates = []
        for j in range(i, len(t["path"])):
            hp = t["path"][j]
            if not np.isfinite(hp["hedge_raw"]):
                continue
            repaired = hp["gross"] + (exec_px(hp["hedge_raw"], "sell") - hedge_buy) * t["lot"]
            if policy == "recover_zero_or_baseline" and repaired >= 0:
                candidates.append(j); break
            if policy == "target_or_baseline" and repaired >= t["target"]:
                candidates.append(j); break
        if candidates:
            j = candidates[0]
        else:
            eligible = [k for k in range(i, len(t["path"])) if np.isfinite(t["path"][k]["hedge_raw"]) and pd.Timestamp(t["path"][k]["ts"]) <= b["base_exit_ts"]]
            if not eligible:
                rows.append({"expiry":t["expiry"],"base_net":b["base_net"],"candidate_net":b["base_net"],"net_uplift":0.0,"adjusted":True,"winner_affected":b["base_net"]>0,"loss_eliminated":False,"hedge_gap":True})
                continue
            j = eligible[-1]
        hp = t["path"][j]
        repaired = hp["gross"] + (exec_px(hp["hedge_raw"], "sell") - hedge_buy) * t["lot"]
        raw = hp["raw_exit"]; xp = (exec_px(raw[0],"sell"),exec_px(raw[1],"buy"),exec_px(raw[2],"buy"))
        e = pd.Timestamp(t["entry_ts"]); trig_ts = pd.Timestamp(tp["ts"]); x = pd.Timestamp(hp["ts"])
        oe = [(e,"buy",t["entry_exec"][0]),(e,"sell",t["entry_exec"][1]),(e,"sell",t["entry_exec"][2])]
        ox = [(x,"sell",xp[0]),(x,"buy",xp[1]),(x,"buy",xp[2]),(trig_ts,"buy",hedge_buy),(x,"sell",exec_px(hp["hedge_raw"],"sell"))]
        net = repaired - charges(oe,ox,t["lot"])
        rows.append({"expiry":t["expiry"],"base_net":b["base_net"],"candidate_net":float(net),"net_uplift":float(net-b["base_net"]),"adjusted":True,"winner_affected":b["base_net"]>0,"loss_eliminated":b["base_net"]<0 and net>=0,"hedge_gap":False})
    return pd.DataFrame(rows)


def split(df):
    e = pd.to_datetime(df["expiry"]).dt.tz_localize(TZ)
    return df[e<=TRAIN_END].copy(), df[(e>TRAIN_END)&(e<=VALIDATION_END)].copy(), df[e>=HOLDOUT_START].copy()


def main():
    raw = build_paths()
    spot_map = load_spot()
    trades, errors = enrich(raw, spot_map)
    if not trades:
        raise RuntimeError("No trades after exact spot alignment")
    base = baseline_rows(trades)
    detail = {}; rows = []
    for thr in MOVE_THRESHOLDS:
        for c in CONFIRM_BARS:
            for fam in SIGNAL_FAMILIES:
                name=f"stop_move{thr}_c{c}_{fam}"
                df=eval_stop(trades,base,thr,fam,c); detail[name]=df
                rows.append({"variant":name,"family":"early_exit","threshold":thr,"confirm":c,"signal":fam,**stats(df)})
                for policy in HEDGE_POLICIES:
                    hname=f"hedge_move{thr}_c{c}_{fam}_{policy}"
                    hdf=eval_hedge(trades,base,thr,fam,c,policy); detail[hname]=hdf
                    rows.append({"variant":hname,"family":"tail_hedge","threshold":thr,"confirm":c,"signal":fam,"policy":policy,**stats(hdf)})
    grid=pd.DataFrame(rows)
    selected_train=[]
    for name,df in detail.items():
        tr,va,ho=split(df); s=stats(tr)
        selected_train.append({"variant":name,"train_net_uplift":s["net_uplift"],"train_winner_affected":s["winner_affected"],"train_loss_reduction":s["loss_reduction"],"train_hedge_gaps":s["hedge_gaps"]})
    train=pd.DataFrame(selected_train)
    safe=train[(train.train_winner_affected==0)&(train.train_hedge_gaps==0)]
    if safe.empty:
        raise RuntimeError("No training-safe rule")
    chosen=safe.sort_values(["train_net_uplift","train_loss_reduction"],ascending=[False,False]).iloc[0]["variant"]
    sdf=detail[chosen]; tr,va,ho=split(sdf); full=pd.concat([tr,va,ho],ignore_index=True)
    st,sv,sh,sf=map(stats,[tr,va,ho,full])
    promotion=(sv["net_uplift"]>0 and sh["net_uplift"]>0 and sv["winner_affected"]==0 and sh["winner_affected"]==0 and sv["max_dd"]<=sv["base_dd"]*1.05 and sh["max_dd"]<=sh["base_dd"]*1.05 and sv["hedge_gaps"]==0 and sh["hedge_gaps"]==0)
    fam_rows=[]
    for fam in ["early_exit","tail_hedge"]:
        candidates=train[train.variant.isin(grid[grid.family==fam].variant)&(train.train_winner_affected==0)&(train.train_hedge_gaps==0)]
        if candidates.empty: continue
        nm=candidates.sort_values(["train_net_uplift","train_loss_reduction"],ascending=[False,False]).iloc[0]["variant"]
        fdf=detail[nm]; ft,fv,fh=split(fdf)
        fam_rows.append({"family":fam,"training_selected_variant":nm,"train_uplift":stats(ft)["net_uplift"],"validation_uplift":stats(fv)["net_uplift"],"holdout_uplift":stats(fh)["net_uplift"],"full_uplift":stats(pd.concat([ft,fv,fh],ignore_index=True))["net_uplift"],"validation_winner_affected":stats(fv)["winner_affected"],"holdout_winner_affected":stats(fh)["winner_affected"],"validation_dd_change":stats(fv)["dd_change"],"holdout_dd_change":stats(fh)["dd_change"]})
    OUT.mkdir(parents=True,exist_ok=True)
    grid.to_csv(OUT/"phase21_full_grid.csv",index=False)
    train.to_csv(OUT/"phase21_training_selection_grid.csv",index=False)
    sdf.to_csv(OUT/"selected_variant_full_trade_level.csv",index=False)
    pd.DataFrame(fam_rows).to_csv(OUT/"family_selected_summary.csv",index=False)
    if errors: pd.DataFrame(errors).to_csv(OUT/"data_alignment_errors.csv",index=False)
    report=f"""# Phase 21 — Pre-Expiry Adverse-Move Risk Control

## Selected candidate
**{chosen}**

## Training
{st}

## Validation
{sv}

## 2026 holdout
{sh}

## Full sample
{sf}

## Promotion screen
**{promotion}**

Required: positive validation and holdout uplift, zero baseline-positive trades affected, no more than 5% max-drawdown deterioration, and zero hedge execution gaps.

## Family comparison
{pd.DataFrame(fam_rows).to_string(index=False)}

The comparator is the frozen Phase-20 strategy. No payoff-boundary rule was introduced. Exact timestamps, corrected strike mapping, corrected long/short signs, historical lot sizes, adverse ₹0.05 option slippage, ₹10/order brokerage and audited statutory charges are retained.
"""
    (OUT/"PHASE21_CONCLUSION.md").write_text(report,encoding="utf-8")
    pd.DataFrame([{"selected_variant":chosen,"promotion":promotion,"train_uplift":st["net_uplift"],"validation_uplift":sv["net_uplift"],"holdout_uplift":sh["net_uplift"],"full_uplift":sf["net_uplift"]}]).to_csv(OUT/"phase21_status.csv",index=False)
    print(report)


if __name__=="__main__":
    main()
