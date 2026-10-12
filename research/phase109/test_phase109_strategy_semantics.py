import unittest

import strategy_evaluator as evaluator


class StrategySemanticTests(unittest.TestCase):
    def test_exact_core_mapping_never_uses_substring_fallback(self):
        supported = {
            "ROC_MOMENTUM", "EMA_CROSS", "EMA_SLOPE", "RETURN_ZSCORE_FADE",
            "RSI_REBOUND", "BOLLINGER_REVERSION", "EMA_DEVIATION_FADE",
            "RELATIVE_STRENGTH",
        }
        for core in supported:
            with self.subTest(core=core):
                self.assertEqual(evaluator.core_method(core), core)

        blocked = [
            "ATR_NORMALIZED_MOMENTUM", "FUTURES_BASIS_MOMENTUM",
            "OPEN_GAP_CONTINUATION", "GLOBAL_OVERNIGHT_LEAD_LAG",
            "VOLUME_BREAKOUT", "IV_RV_SPREAD", "SYNTHETIC_FUTURE_PARITY",
            "NEWS_SENTIMENT_SURPRISE", "DII_FII_FLOW_REGIME", "VWAP_REVERSION",
        ]
        for core in blocked:
            with self.subTest(core=core):
                self.assertIsNone(evaluator.core_method(core))

    def test_cross_asset_confirmation_is_blocked(self):
        prices = [100.0 + i for i in range(20)]
        out = evaluator.make_signal(
            "ROC_MOMENTUM", "CROSS_ASSET", "NONE", prices, prices,
            [12.0] * len(prices), 15, 16,
            {"lookback_sessions": 3, "move_threshold_pct": 0.5},
            "NIFTY", {},
        )
        self.assertEqual(out, (0, "CONFIRMATION_NOT_IMPLEMENTED"))

    def test_undefined_realized_vol_target_is_blocked(self):
        prices = [100.0 + i for i in range(20)]
        out = evaluator.make_signal(
            "ROC_MOMENTUM", "NONE", "REALIZED_VOL_LOW_HIGH", prices, prices,
            [12.0] * len(prices), 15, 16,
            {"lookback_sessions": 3, "move_threshold_pct": 0.5},
            "NIFTY", {},
        )
        self.assertEqual(out, (0, "REGIME_NOT_IMPLEMENTED"))

    def test_ema_slope_is_not_ordinary_return_momentum(self):
        rising = [100.0 + 2.0 * i for i in range(40)]
        falling = [200.0 - 2.0 * i for i in range(40)]
        self.assertEqual(evaluator.compute_signal("EMA_SLOPE", rising, 30, 5, 0.1), 1)
        self.assertEqual(evaluator.compute_signal("EMA_SLOPE", falling, 30, 5, 0.1), -1)

    def test_ema_cross_requires_sign_crossing(self):
        rising = [100.0] * 20 + [101.0, 102.0, 103.0, 104.0]
        falling = [100.0] * 20 + [99.0, 98.0, 97.0, 96.0]
        flat = [100.0] * 30
        self.assertEqual(evaluator.compute_signal("EMA_CROSS", rising, 20, 5, 0.1), 1)
        self.assertEqual(evaluator.compute_signal("EMA_CROSS", falling, 20, 5, 0.1), -1)
        self.assertEqual(evaluator.compute_signal("EMA_CROSS", flat, 25, 5, 0.1), 0)

    def test_stop_and_target_profile_percentages_are_parsed(self):
        self.assertEqual(evaluator.parse_risk_profile("STOP_10PCT_PREMIUM"), (0.1, None))
        self.assertEqual(evaluator.parse_risk_profile("TARGET_30PCT_PREMIUM"), (None, 0.3))
        self.assertEqual(
            evaluator.parse_risk_profile("STOP_20PCT_TARGET_30PCT_PREMIUM"),
            (0.2, 0.3),
        )
        self.assertEqual(evaluator.parse_risk_profile("NO_STOP_NO_TARGET"), (None, None))

    def test_engine_version_prevents_reuse_of_v1_cursor(self):
        self.assertEqual(evaluator.ENGINE_VERSION, "phase109-eod-engine-v2-semantics")


if __name__ == "__main__":
    unittest.main()
