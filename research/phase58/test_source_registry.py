import json
import unittest
from pathlib import Path
from validate_source_registry import build_report, REGISTRY


class SourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_all_sources_have_explicit_access_and_license_decisions(self):
        report=build_report(self.registry)
        self.assertEqual(report["source_count"],6)
        self.assertEqual(report["sources_eligible_for_automated_replay"],[])

    def test_stockmojo_is_not_automated(self):
        source=next(s for s in self.registry["sources"] if s["id"]=="stockmojo_timeseries")
        self.assertFalse(source["automation_eligible"])
        self.assertIn("MANUAL",source["decision"])

    def test_public_samples_are_not_full_history_proof(self):
        for source in self.registry["sources"]:
            self.assertFalse(source["historical_bid_ask_depth_verified"])
            self.assertFalse(source["exact_timestamps_verified"])

    def test_no_purchase_or_terms_violation(self):
        report=build_report(self.registry)
        self.assertFalse(report["purchase_made"])
        self.assertFalse(report["scraping_against_terms"])
        self.assertFalse(report["strategy_promotion_allowed"])

    def test_frozen_times_are_preserved(self):
        report=build_report(self.registry)
        self.assertEqual(report["required_timestamps_ist"]["entries"],["09:45","13:00"])
        self.assertEqual(report["required_timestamps_ist"]["exit"],"15:15")


if __name__=="__main__":
    unittest.main()
