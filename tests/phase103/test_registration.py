import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "phase103_stock_options"))

from validate_registration import validate


class Phase103RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = validate(ROOT)

    def test_registration_passes(self):
        self.assertEqual(self.result["status"], "PASS", self.result["failures"])

    def test_five_unique_initial_stocks(self):
        self.assertEqual(self.result["stock_count"], 5)
        self.assertEqual(len(set(self.result["symbols"])), 5)

    def test_no_strategy_results_claimed(self):
        self.assertIn("no market data acquired", self.result["research_findings"])

    def test_all_registration_checks_are_green(self):
        self.assertEqual(self.result["checks_passed"], self.result["checks_total"])


if __name__ == "__main__":
    unittest.main()
