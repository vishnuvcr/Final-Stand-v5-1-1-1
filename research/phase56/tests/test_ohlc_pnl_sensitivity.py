import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "ohlc_pnl_sensitivity.py"
spec = importlib.util.spec_from_file_location("phase56_pnl", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def leg(
    *,
    leg_id="L1",
    side="BUY",
    range_pct=1.5,
    oi=1000,
    oi_status="PASS",
    entry_open=100.0,
    exit_open=120.0,
):
    return {
        "leg_id": leg_id,
        "side": side,
        "quantity_lots": 1,
        "lot_size": 50,
        "strike": 22000,
        "option_type": "CE",
        "expiry": "2025-03-13",
        "entry_status": "PASS",
        "prior_oi_status": oi_status,
        "range_proxy_status": "PASS" if range_pct <= 2 else "EXCLUDED",
        "exit_status": "PASS",
        "prior_oi": oi,
        "entry_range_proxy_pct": range_pct,
        "entry_open": entry_open,
        "exit_open": exit_open,
    }


def row(*, status="REPLAY_PASS", event_id="evt1", legs=None, reason="all gates passed", family="BUY_CALL"):
    legs = legs or [leg()]
    return {
        "configuration_id": "cfg1",
        "candidate_id": "candidate1",
        "family_id": family,
        "selector_mode": "BASELINE",
        "split": "development",
        "event_id": event_id,
        "expiry": "2025-03-13",
        "entry_ts": "2025-03-13T09:45:00+05:30",
        "exit_ts": "2025-03-13T15:15:00+05:30",
        "status": status,
        "exclusion_reason": reason,
        "option_source_sha256": "testhash",
        "resolved_legs_json": json.dumps(legs),
    }


class Phase56Tests(unittest.TestCase):
    def test_adverse_fill_and_brokerage_math(self):
        item = row()
        legs = mod.legs_for(item)
        base = mod.compute_trade_scenario(item, legs, 10.0, 0.05)
        self.assertEqual(base["order_count"], 2)
        self.assertEqual(base["leg_count"], 1)
        self.assertAlmostEqual(base["gross_pnl_inr"], 995.0, places=8)
        self.assertAlmostEqual(base["fees_brokerage_inr"], 20.0, places=8)
        self.assertGreaterEqual(base["fees_total_inr"], base["fees_brokerage_inr"])
        more_slippage = mod.compute_trade_scenario(item, legs, 10.0, 0.50)
        self.assertLessEqual(more_slippage["gross_pnl_inr"], base["gross_pnl_inr"])
        higher_brokerage = mod.compute_trade_scenario(item, legs, 20.0, 0.05)
        self.assertLess(higher_brokerage["net_pnl_inr"], base["net_pnl_inr"])

    def test_oi_hard_block_never_passes_even_at_diagnostic_threshold(self):
        blocked = row(
            status="BLOCKED_LEG_ELIGIBILITY",
            reason="a required selected leg lacks exact prior-bar OI at or above 100",
            legs=[leg(oi=0, oi_status="FAIL")],
        )
        validated = mod.validate_ledger([blocked], strict_parent=False)
        item = validated["details"][0]
        for threshold in mod.THRESHOLDS:
            eligible, reason = mod.classify_at_threshold(item, threshold)
            self.assertFalse(eligible)
            self.assertEqual(reason, "REQUIRED_LEG_PRIOR_OI_BELOW_100")

    def test_threshold_changes_eligibility_not_price_references(self):
        row5 = row(
            status="EXCLUDED_OHLC_RANGE_PROXY",
            reason="L1 OHLC range proxy exceeds gate 2",
            legs=[leg(range_pct=5.5)],
        )
        validated = mod.validate_ledger([row5], strict_parent=False)
        item = validated["details"][0]
        self.assertFalse(mod.classify_at_threshold(item, 5)[0])
        self.assertTrue(mod.classify_at_threshold(item, 6)[0])
        self.assertTrue(mod.classify_at_threshold(item, 1000)[0])
        self.assertAlmostEqual(item["legs"][0]["entry_open"], 100.0)

    def test_multileg_quantity_and_orders_are_charged_per_fill(self):
        condor_legs = [
            leg(leg_id="L1", side="SELL", range_pct=1.0),
            leg(leg_id="L2", side="BUY", range_pct=1.5, entry_open=40.0, exit_open=20.0),
            leg(leg_id="L3", side="SELL", range_pct=1.2, entry_open=30.0, exit_open=10.0),
            leg(leg_id="L4", side="BUY", range_pct=1.8, entry_open=5.0, exit_open=2.0),
        ]
        item = row(
            status="REPLAY_PASS",
            legs=condor_legs,
            family="SHORT_IRON_CONDOR",
        )
        result = mod.compute_trade_scenario(item, condor_legs, 10.0, 0.05)
        self.assertEqual(result["leg_count"], 4)
        self.assertEqual(result["order_count"], 8)
        self.assertAlmostEqual(result["fees_brokerage_inr"], 80.0, places=8)

    def test_analyze_keeps_fixed_scenario_grid_and_omits_oi_blocks_from_pnl(self):
        rows = [
            row(status="EXCLUDED_OHLC_RANGE_PROXY", reason="L1 OHLC range proxy exceeds gate 2", legs=[leg(range_pct=5.5)]),
            row(
                status="BLOCKED_LEG_ELIGIBILITY",
                event_id="evt2",
                reason="a required selected leg lacks exact prior-bar OI at or above 100",
                legs=[leg(oi=0, oi_status="FAIL")],
            ),
        ]
        result = mod.analyze(rows, strict_parent=False)
        self.assertEqual(len(result["threshold_summary"]), len(mod.THRESHOLDS) * 2 * len(mod.SLIPPAGE_CASES))
        self.assertEqual(len(result["trade_scenarios"]), sum(result["threshold_eligible_rows"].values()) * 2 * len(mod.SLIPPAGE_CASES))
        self.assertFalse(any(x["event_id"] == "evt2" for x in result["trade_scenarios"]))
        self.assertTrue(all(x["promotion_eligible"] is False for x in result["robustness_screen"]))
        self.assertFalse(result["invariants"]["holdout_used"])
        self.assertFalse(result["invariants"]["live_execution_or_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
