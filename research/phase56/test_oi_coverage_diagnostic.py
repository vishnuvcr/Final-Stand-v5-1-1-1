import unittest

from oi_coverage_diagnostic import classify_source_row


class OICoverageClassificationTests(unittest.TestCase):
    def test_missing_exact_row_is_not_zero_oi(self):
        self.assertEqual(classify_source_row(0, []), "MISSING_EXACT_PRIOR_ROW")

    def test_duplicate_exact_rows_fail_closed(self):
        self.assertEqual(classify_source_row(2, [0.0, 200.0]), "DUPLICATE_EXACT_PRIOR_ROWS")

    def test_null_oi_is_distinct(self):
        self.assertEqual(classify_source_row(1, [None]), "NULL_OI")

    def test_zero_oi_is_distinct(self):
        self.assertEqual(classify_source_row(1, [0.0]), "ZERO_OI")

    def test_below_gate_oi_is_distinct(self):
        self.assertEqual(classify_source_row(1, [99.0]), "BELOW_GATE_OI")

    def test_gate_boundary_passes(self):
        self.assertEqual(classify_source_row(1, [100.0]), "PASS_OI_GATE")


if __name__ == "__main__":
    unittest.main()
