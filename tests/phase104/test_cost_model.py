import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "phase104_eod_stock_options"))
from cost_model import exchange_transaction_rate, round_trip_cost


class Phase104CostModelTests(unittest.TestCase):
    def test_exchange_fee_rate_changes_on_march_1_2026(self):
        self.assertAlmostEqual(exchange_transaction_rate("2026-02-28"), 0.0003503)
        self.assertAlmostEqual(exchange_transaction_rate("2026-03-01"), 0.0003552)
        with self.assertRaises(ValueError):
            exchange_transaction_rate("2024-09-30")

    def test_option_stt_rate_changes_on_april_1_2026(self):
        before = round_trip_cost(50, 60, 150, "2026-03-31", brokerage_per_order=20)
        after = round_trip_cost(50, 60, 150, "2026-04-01", brokerage_per_order=20)
        self.assertAlmostEqual(before["stt_sell_rate"], 0.0010)
        self.assertAlmostEqual(after["stt_sell_rate"], 0.0015)
        self.assertGreater(after["stt_on_option_sale"], before["stt_on_option_sale"])

    def test_cost_breakdown_sums_and_labels_unmodelled_execution_costs(self):
        result = round_trip_cost(50, 60, 150, "2026-08-03", brokerage_per_order=20)
        components = [
            "brokerage", "exchange_transaction_charges", "sebi_turnover_fee",
            "gst_on_service_fees", "stt_on_option_sale", "stamp_duty_on_option_buy",
            "stt_on_exercise_if_applicable",
        ]
        self.assertAlmostEqual(result["total_reported_fees"], sum(result[k] for k in components), places=5)
        self.assertAlmostEqual(result["brokerage"], 40.0)
        self.assertAlmostEqual(result["buy_premium_turnover"], 7500.0)
        self.assertAlmostEqual(result["sell_premium_turnover"], 9000.0)
        self.assertIsNone(result["execution_spread_slippage_impact"])
        self.assertEqual(result["net_pnl_status"], "NOT_COMPUTABLE_WITHOUT_EXECUTABLE_FILL_MODEL")

    def test_brokerage_sensitivity_is_explicit(self):
        costs = [round_trip_cost(50, 60, 150, "2026-08-03", brokerage_per_order=b)["total_reported_fees"]
                 for b in (10, 15, 20)]
        self.assertLess(costs[0], costs[1])
        self.assertLess(costs[1], costs[2])

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            round_trip_cost(50, 60, 0, "2026-08-03")
        with self.assertRaises(ValueError):
            round_trip_cost(-1, 60, 150, "2026-08-03")
        with self.assertRaises(ValueError):
            round_trip_cost(50, 60, 150, "2026-08-03", exercised_intrinsic_value=-1)


if __name__ == "__main__":
    unittest.main()
