import unittest
import pandas as pd
from research.phase103.novel_intraday_strategies import (
    adverse_fill, block_bootstrap, charges, compression_setup, find_failed_break_signal,
    find_orb_signal, first_complete_open, opening_range, prior_vix_low, source_coverage_stats,
)

class Phase103StrategyUnitTests(unittest.TestCase):
    def test_adverse_fills_are_conservative(self):
        self.assertAlmostEqual(adverse_fill(10.0, "buy", ticks=1), 10.05)
        self.assertAlmostEqual(adverse_fill(10.0, "sell", ticks=1), 9.95)
        self.assertGreater(adverse_fill(10.0, "buy", ticks=2, impact_pct=0.0025), 10.10)
        self.assertLess(adverse_fill(10.0, "sell", ticks=2, impact_pct=0.0025), 9.90)

    def test_charges_increase_with_registered_stress(self):
        orders = [
            {"timestamp": pd.Timestamp("2025-01-02", tz="Asia/Kolkata"), "side": "buy", "price": 100.0, "qty": 1, "lot": 75},
            {"timestamp": pd.Timestamp("2025-01-02", tz="Asia/Kolkata"), "side": "sell", "price": 110.0, "qty": 1, "lot": 75},
        ]
        self.assertGreater(charges(orders, 1.5, 20.0), charges(orders, 1.0, 10.0))

    def test_opening_range_uses_completed_bars(self):
        ts = pd.date_range("2025-01-02 09:15", periods=15, freq="min", tz="Asia/Kolkata")
        bars = pd.DataFrame({"timestamp": ts, "open": [10]*15, "high": list(range(20,35)),
                             "low": list(range(5,20)), "close": [10]*15})
        high, low = opening_range(bars)
        self.assertEqual(high, 34.0)
        self.assertEqual(low, 5.0)

    def test_orb_requires_cross_market_signal_to_agree(self):
        ts = pd.date_range("2025-01-02 09:15", periods=20, freq="min", tz="Asia/Kolkata")
        bars = pd.DataFrame({"timestamp": ts, "open": [100]*20, "high": [101]*20, "low": [99]*20, "close": [100]*20})
        bars.loc[bars.timestamp.dt.strftime("%H:%M") == "09:30", "close"] = 102
        self.assertIsNotNone(find_orb_signal(bars, 101.5, 98.5, 1))
        self.assertIsNone(find_orb_signal(bars, 101.5, 98.5, -1))
        self.assertIsNone(find_orb_signal(bars, 101.5, 98.5, None))

    def test_failed_breakout_requires_subsequent_reclaim(self):
        ts = pd.date_range("2025-01-02 09:30", periods=4, freq="min", tz="Asia/Kolkata")
        bars = pd.DataFrame({"timestamp": ts, "open": [100]*4, "high": [102,103,101,100],
                             "low": [99,100,98,99], "close": [101,102,100,100]})
        sig = find_failed_break_signal(bars, 100.5, 98.5)
        self.assertIsNotNone(sig)
        self.assertEqual(sig["direction"], -1)
        self.assertEqual(sig["signal_ts"], ts[2])

    def test_compression_requires_twenty_prior_ranges_and_low_vix(self):
        prior = list(range(20,40))
        self.assertTrue(compression_setup(10.0, prior, True))
        self.assertFalse(compression_setup(10.0, prior, False))
        self.assertFalse(compression_setup(10.0, prior[:-1], True))
        self.assertFalse(compression_setup(40.0, prior, True))

    def test_vix_gate_uses_prior_day_only(self):
        vix = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=65, freq="D"), "close": [10.0]*64 + [1000.0]})
        eligible, level, _ = prior_vix_low(vix, pd.Timestamp("2024-03-06"))
        self.assertFalse(eligible)
        self.assertEqual(level, 1000.0)

    def test_fill_skips_partial_snapshot_without_forward_fill(self):
        day = pd.Timestamp("2025-01-02", tz="Asia/Kolkata")
        t0, t1, t2 = day + pd.Timedelta(minutes=10), day + pd.Timedelta(minutes=11), day + pd.Timedelta(minutes=12)
        legs = [("CE", 100.0, 1), ("CE", 200.0, -1)]
        snapshots = {t1: {("CE", 100.0): {"open": 2.0}},
                     t2: {("CE", 100.0): {"open": 2.5}, ("CE", 200.0): {"open": 1.0}}}
        result = first_complete_open(t0, t2, [t0, t1, t2], snapshots, legs)
        self.assertEqual(result[0], t2)
        self.assertEqual(result[1][("CE", 100.0)], 2.5)
        self.assertIsNone(first_complete_open(t0, t1, [t0, t1], snapshots, legs))

    def test_feature_coverage_is_bounded_by_sample_sessions_and_strictly_lagged(self):
        frame = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
            "ret": [0.1, 0.2, float("nan"), 0.4],
        })
        sessions = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
        stats = source_coverage_stats(frame, list(sessions), ["ret"])
        self.assertEqual(stats["sample_sessions"], 3)
        self.assertEqual(stats["covered_sessions"], 2)
        self.assertAlmostEqual(stats["coverage_pct"], 200.0 / 3.0)
        self.assertLessEqual(stats["coverage_pct"], 100.0)

    def test_bootstrap_does_not_infer_from_tiny_sample(self):
        result = block_bootstrap([1.0, -1.0, 2.0], seed=10)
        self.assertEqual(result["status"], "NOT_ESTIMABLE_LT30_SESSIONS")
        self.assertIsNone(result["ci95_low"])

if __name__ == "__main__":
    unittest.main()
