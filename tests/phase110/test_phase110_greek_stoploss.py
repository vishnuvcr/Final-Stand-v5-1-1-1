import math
import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from research.phase110_greek_stoploss import (
    RATE, YEAR_DAYS, bs_price, implied_vol, bs_greeks, historical_lot_size,
    make_configs, make_cost_grid, premium_fee_model, find_exit, condition_matrix,
    holm_adjust, expected_market_minutes,
)
import numpy as np
import pandas as pd


class GreekMathTests(unittest.TestCase):
    def test_black_scholes_iv_round_trip_calls_and_puts(self):
        spot, strike, tau, sigma = 25000.0, 25200.0, 7.0 / YEAR_DAYS, 0.22
        for typ in ("CE", "PE"):
            premium = bs_price(spot, strike, tau, sigma, typ)
            iv = implied_vol(spot, strike, tau, premium, typ)
            self.assertIsNotNone(iv)
            self.assertAlmostEqual(iv, sigma, places=6)
            g = bs_greeks(spot, strike, tau, iv, typ)
            self.assertIsNotNone(g)
            self.assertGreater(g["gamma"], 0)
            self.assertGreater(g["vega"], 0)
            if typ == "CE":
                self.assertGreater(g["delta"], 0)
                self.assertLessEqual(g["delta"], 1)
            else:
                self.assertLess(g["delta"], 0)
                self.assertGreaterEqual(g["delta"], -1)

    def test_short_position_signs_are_opposite_long_signs(self):
        s, k, t, vol = 25000.0, 25000.0, 4 / YEAR_DAYS, 0.2
        call = bs_greeks(s, k, t, vol, "CE")
        put = bs_greeks(s, k, t, vol, "PE")
        short_delta = -(call["delta"] + put["delta"])
        short_gamma = -(call["gamma"] + put["gamma"])
        short_vega = -(call["vega"] + put["vega"])
        self.assertAlmostEqual(call["delta"] - put["delta"], 1.0, places=10)
        self.assertLess(short_gamma, 0)
        self.assertLess(short_vega, 0)
        self.assertTrue(math.isfinite(short_delta))

    def test_deep_itm_european_put_iv_respects_discounted_lower_bound(self):
        spot, strike, tau, sigma = 24000.0, 30000.0, 7.0 / YEAR_DAYS, 0.22
        premium = bs_price(spot, strike, tau, sigma, "PE")
        self.assertLess(premium, strike - spot)
        iv = implied_vol(spot, strike, tau, premium, "PE")
        self.assertIsNotNone(iv)
        self.assertAlmostEqual(iv, sigma, places=6)

    def test_invalid_price_rejected(self):
        self.assertIsNone(implied_vol(25000, 24000, 7/YEAR_DAYS, 1.0, "CE"))


class GridAndCostTests(unittest.TestCase):
    def test_config_grid_is_finite_unique_and_includes_all_four_delta_040_meanings(self):
        cfgs = make_configs()
        ids = [x["config_id"] for x in cfgs]
        self.assertEqual(len(cfgs), 4294)
        self.assertEqual(len(ids), len(set(ids)))
        net = [x for x in cfgs if x["active_count"] == 1 and x["delta_mode"] == "NET_ABS" and x["delta_threshold"] == 0.4]
        gross = [x for x in cfgs if x["active_count"] == 1 and x["delta_mode"] == "GROSS_ABS" and x["delta_threshold"] == 0.4]
        self.assertEqual(len(net), 1)
        self.assertEqual(len(gross), 1)
        self.assertEqual(net[0]["aggregation"], "ANY")

    def test_cost_grid_is_24_unique_cases(self):
        costs = make_cost_grid()
        self.assertEqual(len(costs), 24)
        self.assertEqual(len({x["cost_id"] for x in costs}), 24)

    def test_historical_lot_size_boundaries(self):
        expected = {
            "2021-07-29": 75,
            "2021-08-05": 50,
            "2024-04-25": 50,
            "2024-05-02": 25,
            "2024-12-19": 25,
            "2025-01-02": 75,
            "2025-12-23": 75,
            "2026-01-06": 65,
            "2024-04-29": None,
            "2024-12-26": None,
            "2026-01-02": None,
        }
        for expiry, size in expected.items():
            self.assertEqual(historical_lot_size(expiry), size, expiry)

    def test_fee_model_arithmetic_and_date_aware_stt(self):
        cost = {"cost_id": "TEST", "brokerage_per_order": 20.0, "slippage_per_unit": 0.25, "fee_multiplier": 1.0}
        got = premium_fee_model(100, 100, 50, 50, 50, "2025-06-12", cost)
        self.assertIsNotNone(got)
        self.assertAlmostEqual(got["gross_pnl_inr"], 5000.0, places=7)
        self.assertAlmostEqual(got["slippage_cost_inr"], 50.0, places=7)
        self.assertAlmostEqual(got["brokerage_inr"], 80.0, places=7)
        self.assertAlmostEqual(got["stt_inr"], ((99.75*2)*50)*0.001, places=7)
        self.assertAlmostEqual(got["net_pnl_inr"], 5000-got["total_costs_inr"], places=7)
        new_rate = premium_fee_model(100, 100, 50, 50, 65, "2026-06-09", cost)
        self.assertAlmostEqual(new_rate["stt_inr"], ((99.75*2)*65)*0.0015, places=7)



    def test_expected_market_minutes_skips_overnights_weekends_and_nonmarket_minutes(self):
        # These sparse timestamps mark observed NSE sessions. The helper should
        # construct the active session grid, not an impossible wall-clock minute range.
        sess_dates = ["2025-06-05", "2025-06-06", "2025-06-09", "2025-06-10", "2025-06-11", "2025-06-12"]
        spot = {}
        for d in sess_dates:
            for clock in ("09:15:00", "15:29:00"):
                ts = pd.Timestamp(f"{d} {clock}", tz="Asia/Kolkata")
                spot[ts] = {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}
        entry = pd.Timestamp("2025-06-05 10:00:00", tz="Asia/Kolkata")
        exit_ts = pd.Timestamp("2025-06-12 14:00:00", tz="Asia/Kolkata")
        spot[entry] = {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}
        spot[exit_ts] = {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}
        got = expected_market_minutes(entry, exit_ts, spot)
        self.assertIn(entry, got)
        self.assertIn(exit_ts, got)
        self.assertGreater(len(got), 2000)
        self.assertLess(len(got), 2200)
        self.assertFalse(any(ts.weekday() >= 5 for ts in got))
        self.assertFalse(any(ts.date() == entry.date() and ts < entry for ts in got))
        self.assertFalse(any(ts.date() == exit_ts.date() and ts > exit_ts for ts in got))
        # Overnight is not treated as one-minute spacing; each series interval is session-local.
        deltas = pd.Series(got).diff().dropna()
        self.assertTrue((deltas >= pd.Timedelta(minutes=1)).all())
        self.assertTrue((deltas <= pd.Timedelta(days=1)).all())


class ExitTimingTests(unittest.TestCase):
    def test_stop_uses_next_minute_open_not_signal_bar(self):
        ts = pd.Timestamp("2025-06-05 10:00:00", tz="Asia/Kolkata")
        ev = {
            "metrics": {"net_abs_delta": np.array([0.2, 0.41, 0.7]),
                        "gross_abs_delta": np.array([0.2, 0.41, 0.7]),
                        "gamma_risk": np.array([0.1,0.2,0.3]),
                        "vega_risk": np.array([0.1,0.2,0.3]),
                        "theta_ratio": np.array([1.0,0.9,0.8])},
            "signal_timestamps": [ts, ts+pd.Timedelta(minutes=1), ts+pd.Timedelta(minutes=2)],
            "exit_timestamps": [ts+pd.Timedelta(minutes=1), ts+pd.Timedelta(minutes=2), ts+pd.Timedelta(minutes=3)],
            "exit_call_open": np.array([111.0, 222.0, 333.0]),
            "exit_put_open": np.array([44.0, 55.0, 66.0]),
            "base_call_exit": 777.0, "base_put_exit": 888.0,
            "exit_ts": pd.Timestamp("2025-06-12 14:00:00", tz="Asia/Kolkata"),
        }
        cfg = {"active_count":1, "delta_threshold":0.4, "delta_mode":"NET_ABS",
               "gamma_threshold":None, "vega_threshold":None, "theta_threshold":None, "aggregation":"ANY"}
        xc, xp, xt, reason, idx = find_exit(ev, cfg)
        self.assertEqual((xc,xp), (222.0,55.0))
        self.assertEqual(xt, ts+pd.Timedelta(minutes=2))
        self.assertEqual(reason, "GREEK_STOP_NEXT_OPEN")
        self.assertEqual(idx, 1)

    def test_no_stop_uses_fixed_expiry_day_1400_reference(self):
        ts = pd.Timestamp("2025-06-05 10:00:00", tz="Asia/Kolkata")
        ev = {"base_call_exit":100.0,"base_put_exit":50.0,
              "exit_ts":pd.Timestamp("2025-06-12 14:00:00",tz="Asia/Kolkata"),
              "signal_timestamps":[ts],"metrics":{}}
        cfg = {"active_count":0}
        self.assertEqual(find_exit(ev,cfg), (100.0,50.0,ev["exit_ts"],"FIXED_14_00",None))

    def test_any_vs_all_semantics(self):
        ev={"metrics":{"net_abs_delta":np.array([0.5,0.5]),
                       "gross_abs_delta":np.array([0.5,0.5]),
                       "gamma_risk":np.array([0.05,0.25]),
                       "vega_risk":np.array([0.1,0.1]),
                       "theta_ratio":np.array([0.2,0.2])},
            "signal_timestamps":[1,2]}
        any_cfg={"delta_threshold":0.4,"delta_mode":"NET_ABS","gamma_threshold":0.2,
                 "vega_threshold":None,"theta_threshold":None,"aggregation":"ANY"}
        all_cfg={**any_cfg,"aggregation":"ALL"}
        self.assertEqual(condition_matrix(ev,any_cfg).tolist(),[True,True])
        self.assertEqual(condition_matrix(ev,all_cfg).tolist(),[False,True])


class StatisticsTests(unittest.TestCase):
    def test_holm_step_down_adjusted_p_values_are_bounded_and_ordered(self):
        got=holm_adjust({"a":0.01,"b":0.04,"c":0.03,"d":1.0})
        self.assertTrue(all(0 <= x <= 1 for x in got.values()))
        p=sorted([0.01,0.03,0.04,1.0])
        adj=sorted(got.values())
        self.assertEqual(adj,sorted(adj))
        self.assertAlmostEqual(got["a"],0.04)
        self.assertGreaterEqual(got["b"],0.06)


if __name__ == "__main__":
    unittest.main()
