import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("evidence_gate.py")
spec = importlib.util.spec_from_file_location("phase60_gate", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class EvidenceGateTests(unittest.TestCase):
    def test_frozen_phase52_thresholds_are_monotonic(self):
        result = mod.evaluate()
        self.assertEqual(result["status"], "NO_GO_EMPIRICAL_FACTOR_STRATEGY_TESTING_DATA_EVIDENCE_INSUFFICIENT")
        counts = result["cross_phase_evidence"]["phase54_coverage_sensitivity"]["eligible_rows"]
        self.assertEqual(counts, [1,1,8,24,55,91,150,227,298,345,380])
        self.assertEqual(sorted(counts), counts)
        self.assertFalse(result["frozen_rules"]["holdout_used"])
        self.assertFalse(result["frozen_rules"]["strategy_promoted"])

    def test_source_gate_requires_zero_accepted_sources(self):
        result = mod.evaluate()
        self.assertEqual(result["source_audit"]["authorized_exact_prior_minute_oi_sources"], 0)
        self.assertEqual(result["source_audit"]["authorized_exact_quote_depth_sources"], 0)

    def test_report_is_no_go_not_a_profitability_claim(self):
        result = mod.evaluate()
        self.assertIn("not a defensible profitability conclusion", result["conclusion"])
        self.assertEqual(result["cross_phase_evidence"]["phase57_independent_reproduction"]["mismatches"], 0)


if __name__ == "__main__":
    unittest.main()
