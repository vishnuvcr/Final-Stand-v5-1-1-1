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
    def test_partial_leg_payload_blocks_threshold_estimation(self):
        rows = [
            {"configuration_id":"a","event_id":"e","status":"EXCLUDED_OHLC_RANGE_PROXY","split":"development",
             "family_id":"BEAR_CALL_SPREAD","resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":500,"entry_status":"PASS","entry_range_proxy_pct":5.5}])},
            {"configuration_id":"b","event_id":"e","status":"BLOCKED_LEG_ELIGIBILITY","split":"development",
             "family_id":"BUY_CALL","resolved_legs_json":json.dumps([
                 {"leg_id":"L1","prior_oi":0,"status":"PRIOR_OI_MISSING_OR_BELOW_GATE"}])},
        ]
        out = mod.analyze(rows)
        self.assertEqual(out["status"], "OHLC_REFERENCE_SENSITIVITY_BLOCKED_INCOMPLETE_LEG_EVIDENCE")
        self.assertEqual(out["complete_leg_payload_rows"], 1)
        self.assertEqual(out["partial_leg_payload_rows"], 1)
        self.assertFalse(out["threshold_sensitivity"][0]["computable"])
        self.assertIsNone(out["threshold_sensitivity"][0]["eligible_rows"])
        self.assertFalse(out["frozen_rules"]["historical_pnl_recalculated"])
        self.assertFalse(out["frozen_rules"]["live_execution_or_promotion_allowed"])

    def test_empty_or_bad_schema_is_rejected(self):
        with self.assertRaises(ValueError):
            mod.analyze([])
        with self.assertRaises(ValueError):
            mod.analyze([{"status":"PASS"}])

if __name__ == "__main__":
    unittest.main()

# Trigger validation after workflow persistence fix; test logic unchanged.
