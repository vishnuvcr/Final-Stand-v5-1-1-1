import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "ohlc_reference_sensitivity.py"
spec = importlib.util.spec_from_file_location("phase54_sensitivity", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class Phase54Tests(unittest.TestCase):
    def test_complete_range_legs_and_explicit_oi_block_compute_safely(self):
        rows = [
            {"configuration_id":"a","event_id":"e","status":"EXCLUDED_OHLC_RANGE_PROXY","split":"development",
             "family_id":"BEAR_CALL_SPREAD","exclusion_reason":"L1 OHLC range above gate",
             "resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":500,"prior_oi_status":"PASS","entry_status":"PASS","entry_range_proxy_pct":5.5},
                 {"leg_id":"L2","prior_oi":600,"prior_oi_status":"PASS","entry_status":"PASS","entry_range_proxy_pct":3.0}])},
            {"configuration_id":"b","event_id":"e","status":"BLOCKED_LEG_ELIGIBILITY","split":"development",
             "family_id":"BUY_CALL","exclusion_reason":"a required selected leg lacks exact prior-bar OI at or above 100",
             "resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":0,"status":"PRIOR_OI_MISSING_OR_BELOW_GATE"}])},
        ]
        out = mod.analyze(rows)
        self.assertEqual(out["status"], "OHLC_REFERENCE_SENSITIVITY_COMPUTED_COVERAGE_ONLY")
        self.assertEqual(out["known_hard_oi_block_rows"], 1)
        self.assertEqual(out["threshold_sensitivity"][0]["eligible_rows"], 0)
        self.assertEqual(out["threshold_sensitivity"][0]["oi_or_legs_rejected_rows"], 1)
        self.assertEqual(out["threshold_sensitivity"][0]["range_rejected_rows"], 1)
        threshold6 = next(x for x in out["threshold_sensitivity"] if x["threshold_pct"] == 6)
        self.assertEqual(threshold6["eligible_rows"], 1)
        self.assertEqual(threshold6["reconciliation_total"], 2)
        self.assertTrue(out["frozen_rules"]["threshold_sensitivity_computed"])
        self.assertFalse(out["frozen_rules"]["historical_pnl_recalculated"])
        self.assertFalse(out["frozen_rules"]["live_execution_or_promotion_allowed"])

    def test_partial_range_leg_payload_blocks_threshold_estimation(self):
        rows = [
            {"configuration_id":"a","event_id":"e","status":"EXCLUDED_OHLC_RANGE_PROXY","split":"development",
             "family_id":"BEAR_CALL_SPREAD","exclusion_reason":"L1 range gate",
             "resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":500,"prior_oi_status":"PASS","entry_status":"PASS","entry_range_proxy_pct":5.5}])},
            {"configuration_id":"b","event_id":"e","status":"BLOCKED_LEG_ELIGIBILITY","split":"development",
             "family_id":"BUY_CALL","exclusion_reason":"a required selected leg lacks exact prior-bar OI at or above 100",
             "resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":0,"status":"PRIOR_OI_MISSING_OR_BELOW_GATE"}])},
        ]
        out = mod.analyze(rows)
        self.assertEqual(out["status"], "OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE")
        self.assertEqual(out["known_hard_oi_block_rows"], 1)
        self.assertFalse(out["threshold_sensitivity"][0]["computable"])
        self.assertIsNone(out["threshold_sensitivity"][0]["eligible_rows"])

    def test_empty_or_bad_schema_is_rejected(self):
        with self.assertRaises(ValueError):
            mod.analyze([])
        with self.assertRaises(ValueError):
            mod.analyze([{"status":"PASS"}])


if __name__ == "__main__":
    unittest.main()
