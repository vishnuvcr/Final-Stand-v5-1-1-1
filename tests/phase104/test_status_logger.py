import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "phase104_eod_stock_options"))
from record_phase104_status import apply_audit_state


class Phase104StatusLoggerTests(unittest.TestCase):
    def test_successful_data_rerun_does_not_reopen_closed_phase(self):
        current = "# Status\n\n**State:** COMPLETE — EOD IDENTITY PASS; EXECUTION GATE NO-GO\n"
        self.assertEqual(apply_audit_state(current, "PASS_EOD_CONTRACT_IDENTITY"), current)

    def test_open_phase_gets_interim_data_gate_state(self):
        current = "# Status\n\n**State:** REGISTERED; AUDIT PENDING\n"
        out = apply_audit_state(current, "PASS_EOD_CONTRACT_IDENTITY")
        self.assertIn("**State:** PHASE 104.1 EOD CONTRACT IDENTITY PASS; EXECUTION/COST GATES PENDING", out)

    def test_failed_data_gate_updates_open_phase_without_claiming_pass(self):
        current = "# Status\n\n**State:** REGISTERED; AUDIT PENDING\n"
        out = apply_audit_state(current, "FAIL_EOD_DATA_QUALITY_GATE")
        self.assertIn("**State:** PHASE 104.1 EOD AUDIT COMPLETED; DATA/IDENTITY QUALITY GATE NOT PASSED", out)


if __name__ == "__main__":
    unittest.main()
