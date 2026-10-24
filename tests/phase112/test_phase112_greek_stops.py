import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"research"))
import phase112_greek_stop_combinations as g


class GreekFormulaTests(unittest.TestCase):
    def test_greek_signs_and_finiteness(self):
        s,k,t,v=22000.0,22200.0,5.0/365.25,0.23
        call=g.greeks(s,k,t,v,"CE")
        put=g.greeks(s,k,t,v,"PE")
        self.assertIsNotNone(call); self.assertIsNotNone(put)
        self.assertGreater(call["delta"],0); self.assertLess(put["delta"],0)
        self.assertGreater(call["gamma"],0); self.assertGreater(put["gamma"],0)
        self.assertGreater(call["vega"],0); self.assertGreater(put["vega"],0)
        self.assertLess(call["rho"],0) is False
        self.assertLess(put["rho"],0)
        self.assertTrue(all(np.isfinite(list(call.values()))))
        self.assertAlmostEqual(call["delta"]-put["delta"],1.0,places=5)

    def test_vega_units_and_rho_decay_with_time(self):
        short=g.greeks(22000,22200,2/365.25,.24,"CE")
        longer=g.greeks(22000,22200,20/365.25,.24,"CE")
        self.assertGreater(short["vega"],0)
        self.assertLess(abs(short["rho"]),abs(longer["rho"]))

    def test_exact_registered_candidate_count(self):
        cfg=g.candidates()
        self.assertEqual(len(cfg),72)
        self.assertEqual(len({x["candidate_id"] for x in cfg}),72)
        self.assertEqual(sum(x["active_count"]==0 for x in cfg),1)
        self.assertEqual(sum(x["active_count"]==1 for x in cfg),19)
        self.assertEqual(sum(x["active_count"]>=2 for x in cfg),52)

class StopLogicTests(unittest.TestCase):
    def test_any_triggers_on_first_metric_breach(self):
        metrics={"delta":np.array([.2,.4,.51]),"gamma":np.array([.1,.25,.15]),
                 "vega":np.array([.1,.1,.1]),"theta":np.array([1.,.9,.8]),"rho":np.array([0.,0.,0.])}
        fired=g.trigger(metrics,{"delta":.5,"gamma":.2},"ANY")
        self.assertEqual(np.flatnonzero(fired).tolist(),[1,2])

    def test_all_requires_same_minute_breach(self):
        metrics={"delta":np.array([.51,.2,.6]),"gamma":np.array([.1,.25,.21]),
                 "vega":np.array([.1,.3,.3]),"theta":np.array([1.,1.,1.]),"rho":np.array([0.,0.,0.])}
        fired=g.trigger(metrics,{"delta":.5,"gamma":.2,"vega":.2},"ALL")
        self.assertEqual(np.flatnonzero(fired).tolist(),[2])

    def test_theta_is_inverse_threshold(self):
        metrics={"delta":np.array([.2,.2,.2]),"gamma":np.array([0.,0.,0.]),
                 "vega":np.array([0.,0.,0.]),"theta":np.array([.8,.25,-.1]),"rho":np.array([0.,0.,0.])}
        fired=g.trigger(metrics,{"theta":.25},"ANY")
        self.assertEqual(np.flatnonzero(fired).tolist(),[1,2])

    def test_fee_model_pnl_reconciles(self):
        cost={"brokerage_per_order":20.0,"slippage_per_unit":.25,"fee_multiplier":1.0}
        f=g.base.fee_model(100,50,50,"2025-06-05","2025-06-12",cost)
        self.assertIsNotNone(f)
        self.assertAlmostEqual(f["net_pnl_inr"],f["gross_pnl_inr"]-f["total_costs_inr"])
        self.assertEqual(f["gross_pnl_inr"],2500.0)
        self.assertEqual(f["slippage_cost_inr"],25.0)
        self.assertEqual(f["brokerage_inr"],40.0)

if __name__=="__main__":
    unittest.main(verbosity=2)
