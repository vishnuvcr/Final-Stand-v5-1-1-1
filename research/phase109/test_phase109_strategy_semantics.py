import unittest
from datetime import date, timedelta
from unittest import mock

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

    def test_signal_direction_maps_to_exact_nse_option_side(self):
        self.assertEqual(evaluator.option_side_from_direction(1), "CE")
        self.assertEqual(evaluator.option_side_from_direction(-1), "PE")
        self.assertIsNone(evaluator.option_side_from_direction(0))
        self.assertIsNone(evaluator.option_side_from_direction(None))

    def test_chain_features_are_precomputed_once_per_supported_symbol(self):
        dates = ["2026-01-01", "2026-01-02", "2026-01-03"]
        sentinel = {"NIFTY": {("NIFTY", 0): {"ce_oi": 1}},
                    "BANKNIFTY": {("BANKNIFTY", 0): {"pe_oi": 2}}}
        with mock.patch.object(
            evaluator, "aggregate_chain_features",
            side_effect=lambda data, symbol, dates: sentinel[symbol],
        ) as aggregate:
            result = evaluator.precompute_chain_features({}, dates)
        self.assertEqual(set(result), set(evaluator.INDEX_SYMBOLS))
        self.assertEqual(result, sentinel)
        self.assertEqual(aggregate.call_count, len(evaluator.INDEX_SYMBOLS))

    def test_truncated_official_context_fails_closed(self):
        start = date(2023, 10, 1)
        end = date(2026, 10, 9)
        all_dates = [
            start + timedelta(days=i)
            for i in range((end - start).days)
            if (start + timedelta(days=i)).weekday() < 5
        ]
        truncated = all_dates[:218]
        vix = {d: 12.0 for d in truncated}
        index = {
            "NIFTY": {d: 22000.0 for d in truncated},
            "BANKNIFTY": {d: 48000.0 for d in truncated},
        }
        with self.assertRaisesRegex(RuntimeError, "OFFICIAL_CONTEXT_COVERAGE_GATE_FAILED"):
            evaluator.validate_context_coverage(all_dates, vix, index)

    def test_sufficient_official_context_coverage_passes_gate(self):
        start = date(2023, 10, 1)
        end = date(2026, 10, 9)
        all_dates = [
            start + timedelta(days=i)
            for i in range((end - start).days)
            if (start + timedelta(days=i)).weekday() < 5
        ]
        covered = all_dates[:740]
        vix = {d: 12.0 for d in covered}
        index = {
            "NIFTY": {d: 22000.0 for d in covered},
            "BANKNIFTY": {d: 48000.0 for d in covered},
        }
        result = evaluator.validate_context_coverage(all_dates, vix, index)
        self.assertTrue(result["coverage_pass"])
        self.assertGreater(result["minimum_unique_dates_per_series"], 218)

    def test_result_filename_keeps_engine_versions_separate(self):
        name = evaluator.shard_result_filename("selection", "000000000-000002000")
        self.assertEqual(
            name,
            "phase109_eval_v3_context_coverage_000000000-000002000.csv.gz",
        )
        self.assertNotEqual(name, "phase109_eval_000000000-000002000.csv.gz")

    def test_engine_version_prevents_reuse_of_v1_cursor(self):
        self.assertEqual(evaluator.ENGINE_VERSION, "phase109-eod-engine-v3-context-coverage")


if __name__ == "__main__":
    unittest.main()
