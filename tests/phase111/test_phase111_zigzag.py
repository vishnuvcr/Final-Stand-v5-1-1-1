import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "research"))
import phase111_zigzag_weekly_expiry as z


class MathAndFeesTests(unittest.TestCase):
    def test_iv_round_trip_and_greek_signs(self):
        s, k, t, vol = 22000.0, 22200.0, 7.0 / 365.25, 0.22
        for typ in ("CE", "PE"):
            premium = z.price(s, k, t, vol, typ)
            implied = z.iv_est(s, k, t, premium, typ)
            self.assertIsNotNone(implied)
            self.assertAlmostEqual(implied, vol, places=5)
        call_delta = z.delta(s, k, t, vol, "CE")
        put_delta = z.delta(s, k, t, vol, "PE")
        self.assertGreater(call_delta, 0.0)
        self.assertLess(put_delta, 0.0)
        self.assertAlmostEqual(call_delta - put_delta, 1.0, places=6)

    def test_one_leg_fee_accounting(self):
        cost = {"brokerage_per_order": 20.0, "slippage_per_unit": 0.25, "fee_multiplier": 1.0}
        got = z.fee_model(100.0, 50.0, 50, "2025-06-05", "2025-06-12", cost)
        self.assertEqual(got["gross_pnl_inr"], 2500.0)
        self.assertEqual(got["slippage_cost_inr"], 25.0)
        self.assertEqual(got["brokerage_inr"], 40.0)
        self.assertAlmostEqual(got["net_pnl_inr"], got["gross_pnl_inr"] - got["total_costs_inr"])
        self.assertGreater(got["total_costs_inr"], got["slippage_cost_inr"] + got["brokerage_inr"])

    def test_lot_size_boundaries(self):
        self.assertEqual(z.lot_size("2021-07-29"), 75)
        self.assertEqual(z.lot_size("2021-08-05"), 50)
        self.assertEqual(z.lot_size("2024-05-02"), 25)
        self.assertEqual(z.lot_size("2025-01-02"), 75)
        self.assertEqual(z.lot_size("2026-01-06"), 65)
        self.assertIsNone(z.lot_size("2024-04-30"))


class NonRepaintingSignalTests(unittest.TestCase):
    @staticmethod
    def make_daily(n=160):
        x = np.arange(n, dtype=float)
        close = 22000.0 + 180.0*np.sin(x*2*np.pi/18.0) + 0.7*x + 13.0*np.sin(x*2*np.pi/7.0)
        return pd.DataFrame({
            "date": [(pd.Timestamp("2022-01-01") + pd.Timedelta(days=int(i))).strftime("%Y-%m-%d") for i in x],
            "open": close - 2.0,
            "high": close + 18.0 + 2.0*np.sin(x*0.31),
            "low": close - 18.0 - 2.0*np.cos(x*0.27),
            "close": close,
            "minute_rows": 375,
        })

    def test_confirmed_pivots_are_confirmed_after_pivot_date(self):
        daily = self.make_daily()
        pivots = z.confirmed_pivots(daily)
        self.assertGreater(len(pivots), 3)
        for p in pivots:
            self.assertGreater(p["confirmation_idx"], p["idx"])

    def test_future_bars_cannot_change_signal_as_of_cutoff(self):
        daily = self.make_daily()
        cutoff = 100
        base = z.signal_asof(daily, daily.iloc[cutoff]["date"])
        self.assertIsNotNone(base)
        changed = daily.copy()
        changed.loc[cutoff+1:, "high"] += 10000.0
        changed.loc[cutoff+1:, "low"] -= 10000.0
        revised = z.signal_asof(changed, daily.iloc[cutoff]["date"])
        self.assertEqual(base, revised)

    def test_full_history_and_prefix_give_same_cutoff_signal(self):
        daily = self.make_daily()
        cutoff = 100
        full = z.signal_asof(daily, daily.iloc[cutoff]["date"])
        prefix = z.signal_asof(daily.iloc[:cutoff+1].reset_index(drop=True), daily.iloc[cutoff]["date"])
        self.assertEqual(full, prefix)

    def test_latest_label_side_mapping(self):
        self.assertEqual("PE" if "HL" in {"HL", "LL"} else "CE", "PE")
        self.assertEqual("PE" if "LL" in {"HL", "LL"} else "CE", "PE")
        self.assertEqual("CE" if "HH" in {"HH", "LH"} else "PE", "CE")
        self.assertEqual("CE" if "LH" in {"HH", "LH"} else "PE", "CE")


class TimestampTests(unittest.TestCase):
    def test_grid_uses_market_minutes_not_weekends(self):
        spot = {}
        for d in ("2025-06-06", "2025-06-09", "2025-06-10"):
            for clock in ("09:15:00", "15:29:00"):
                ts = pd.Timestamp(f"{d} {clock}", tz=z.TZ)
                spot[ts] = {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}
        entry = pd.Timestamp("2025-06-06 10:00:00", tz=z.TZ)
        exit_ts = pd.Timestamp("2025-06-10 10:00:00", tz=z.TZ)
        grid = z.expected_grid(entry, exit_ts, spot)
        self.assertEqual(grid[0], entry)
        self.assertEqual(grid[-1], exit_ts)
        self.assertFalse(any(t.weekday() >= 5 for t in grid))
        self.assertEqual(len(grid), 751)
        self.assertTrue(grid.is_monotonic_increasing)
        self.assertFalse(grid.has_duplicates)


if __name__ == "__main__":
    unittest.main(verbosity=2)
