import unittest

from research.phase102.final_strategy_ranking import close


class Phase102HelperTests(unittest.TestCase):
    def test_close_within_tolerance(self):
        self.assertTrue(close(100.0, 100.01, tolerance=0.02))

    def test_close_outside_tolerance(self):
        self.assertFalse(close(100.0, 100.03, tolerance=0.02))


if __name__ == "__main__":
    unittest.main()
