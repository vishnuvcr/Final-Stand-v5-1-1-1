import unittest
import pandas as pd

from cost_aware_range_sensitivity import THRESHOLDS, summarize_costs


class Phase57Tests(unittest.TestCase):
    def test_threshold_grid_is_frozen_and_ordered(self):
        self.assertEqual(THRESHOLDS, [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 1000])

    def test_cost_summary_reports_unique_events_separately(self):
        costs = pd.DataFrame([
            {"threshold_pct": 10, "split": "development", "brokerage_per_order_inr": 20,
             "slippage_stress_pct": 0, "net_pnl_inr": 10.0, "event_id": "e1"},
            {"threshold_pct": 10, "split": "development", "brokerage_per_order_inr": 20,
             "slippage_stress_pct": 0, "net_pnl_inr": -5.0, "event_id": "e1"},
            {"threshold_pct": 10, "split": "development", "brokerage_per_order_inr": 20,
             "slippage_stress_pct": 0, "net_pnl_inr": 2.0, "event_id": "e2"},
        ])
        summary = summarize_costs(costs, pd.DataFrame(), ["threshold_pct", "split"])
        self.assertEqual(int(summary.iloc[0]["executed_configuration_event_rows"]), 3)
        self.assertEqual(int(summary.iloc[0]["unique_event_ids"]), 2)
        self.assertEqual(float(summary.iloc[0]["aggregate_config_event_net_pnl_inr_not_portfolio"]), 7.0)

    def test_empty_costs_is_safe(self):
        self.assertTrue(summarize_costs(pd.DataFrame(), pd.DataFrame(), ["threshold_pct"]).empty)


if __name__ == "__main__":
    unittest.main()
