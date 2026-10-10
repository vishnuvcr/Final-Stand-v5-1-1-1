"""Deterministic signal-level MA replay; not an options execution simulator."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / ".cache/phase95/nifty_daily.csv"
OUT = ROOT / "results/phase96"

def load_prices(path: Path = DATA) -> pd.DataFrame:
    if not path.exists():
        import yfinance as yf
        path.parent.mkdir(parents=True, exist_ok=True)
        downloaded = yf.download("^NSEI", start="2004-01-01", end="2026-01-01", auto_adjust=False, progress=False, threads=False, multi_level_index=False)
        if downloaded.empty:
            raise RuntimeError("Yahoo Finance returned no NIFTY daily data")
        downloaded.to_csv(path)
    df = pd.read_csv(path)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(c[0]) for c in df.columns]
    date_col = next((c for c in df.columns if str(c).lower() in {"date", "datetime"}), None)
    if date_col is None:
        raise ValueError("No date column in cached data")
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.tz_convert(None)
    df = df.rename(columns={date_col: "date"})
    cols = {str(c).lower(): c for c in df.columns}
    close_col = cols.get("close")
    open_col = cols.get("open")
    if close_col is None or open_col is None:
        raise ValueError("Open and Close columns required")
    df["close"] = pd.to_numeric(df[close_col], errors="coerce")
    df["open"] = pd.to_numeric(df[open_col], errors="coerce")
    df = df[["date", "open", "close"]].dropna().sort_values("date").drop_duplicates("date")
    if df.empty or df["date"].max() >= pd.Timestamp("2026-01-01"):
        raise ValueError("Empty dataset or forbidden 2026+ data in Phase 96 input")
    return df.reset_index(drop=True)

def replay(df: pd.DataFrame, kind: str, short: int, long: int) -> pd.DataFrame:
    if short <= 0 or long <= short:
        raise ValueError("Require 0 < short < long")
    x = df.copy()
    if kind == "SMA":
        fast = x.close.rolling(short, min_periods=short).mean()
        slow = x.close.rolling(long, min_periods=long).mean()
    elif kind == "EMA":
        fast = x.close.ewm(span=short, adjust=False, min_periods=short).mean()
        slow = x.close.ewm(span=long, adjust=False, min_periods=long).mean()
    else:
        raise ValueError(f"Unknown average type: {kind}")
    # Signal known after close; apply it from next session's open onward.
    x["signal"] = (fast > slow).astype(float).shift(1).fillna(0.0)
    x["asset_return"] = x.close.pct_change().fillna(0.0)
    # Close-to-close returns, position decided using previous close: no same-bar look-ahead.
    x["strategy_return_gross"] = x.signal * x.asset_return
    x["turnover"] = x.signal.diff().abs().fillna(x.signal.abs())
    x["strategy_return_net_proxy"] = x.strategy_return_gross - x.turnover * 0.0005
    x["buy_hold_return"] = x.asset_return
    x["equity_strategy"] = (1 + x.strategy_return_net_proxy).cumprod()
    x["equity_buy_hold"] = (1 + x.buy_hold_return).cumprod()
    return x

def stats(r: pd.Series, equity: pd.Series, name: str) -> dict:
    r = r.replace([np.inf, -np.inf], np.nan).dropna()
    dd = equity / equity.cummax() - 1
    std = r.std(ddof=1)
    return {
        "strategy": name, "sessions": int(len(r)),
        "total_return": float((1 + r).prod() - 1) if len(r) else None,
        "annualized_volatility": float(std * np.sqrt(252)) if len(r) > 1 else None,
        "sharpe_rf0": float(r.mean() / std * np.sqrt(252)) if len(r) > 1 and std > 0 else None,
        "max_drawdown": float(dd.min()) if len(dd) else None,
        "hit_rate": float((r > 0).mean()) if len(r) else None,
    }

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_prices()
    # Fixed OOS block; indicator warm-up may use pre-period history but P&L is scored only in period.
    rows, curves = [], []
    for kind in ("SMA", "EMA"):
        for short, long in ((5,20),(10,50),(20,100)):
            x = replay(df, kind, short, long)
            test = x[(x.date >= "2020-01-01") & (x.date < "2026-01-01")].copy()
            test["equity_strategy"] = (1 + test["strategy_return_net_proxy"]).cumprod()
            test["equity_buy_hold"] = (1 + test["buy_hold_return"]).cumprod()
            rows.append(stats(test.strategy_return_net_proxy, test.equity_strategy, f"{kind}_{short}_{long}_net_proxy"))
            rows.append(stats(test.buy_hold_return, test.equity_buy_hold, "buy_hold"))
            test["strategy"] = f"{kind}_{short}_{long}"
            curves.append(test[["date","strategy","signal","turnover","strategy_return_gross","strategy_return_net_proxy","buy_hold_return"]])
    pd.DataFrame(rows).to_csv(OUT / "metrics.csv", index=False)
    pd.concat(curves).to_csv(OUT / "daily_replay.csv", index=False)
    (OUT / "data_manifest.json").write_text(json.dumps({
        "source_file": str(DATA.relative_to(ROOT)), "rows": len(df),
        "first_date": str(df.date.min().date()), "last_date": str(df.date.max().date()),
        "evaluation_start": "2020-01-01", "evaluation_end_exclusive": "2026-01-01",
        "note": "0.05% turnover deduction is a transparent sensitivity proxy, not a verified historical Paytm Money fee schedule; index is not directly investable and this is not options P&L."
    }, indent=2))
    report = ["# Phase 96 Signal-Level Replay", "", "## Interpretation guardrail",
      "These are operationalized SMA/EMA sensitivity variants, not exact reproductions where source parameters are unspecified. The underlying NIFTY spot index is not directly investable. The 0.05% turnover deduction is a sensitivity proxy, not verified Paytm Money costs. No option P&L is inferred.",
      "", f"Input observations: {len(df)}; scored sessions per variant: {int(((df.date >= '2020-01-01') & (df.date < '2026-01-01')).sum())}.",
      "", "## Results", "", pd.DataFrame(rows).to_markdown(index=False), "",
      "## Limitations", "No exact listed-option contract data are used. Month/seasonality and first-Thursday/stop-loss rules are not backtested unless the source register provides fully specified rules. A simple return replay is exploratory and has no significance claim."]
    (OUT / "REPORT.md").write_text("\n".join(report) + "\n")
if __name__ == "__main__":
    main()
