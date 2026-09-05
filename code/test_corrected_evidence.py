#!/usr/bin/env python3
"""Deterministic regressions for the evidence-producing runner."""
import unittest
import numpy as np
from scipy.optimize import OptimizeResult
from scipy.spatial.distance import pdist, squareform
from corrected_evidence import nei_pairs, bootstrap_nei, recurrence, diagnose, gates, wilson


class EvidenceTests(unittest.TestCase):
    def test_nei_domain_and_range(self):
        self.assertEqual(nei_pairs(np.array([[1.,2.],[1.,2.]])),0)
        self.assertAlmostEqual(nei_pairs(np.array([[3.,6.],[0.,0.],[0.,0.]])),2)
        with self.assertRaises(ValueError):
            nei_pairs(np.zeros((3,2)))

    def test_bootstrap_preserves_small_floor(self):
        p=np.array([[1.,2.],[1+1e-10,2-1e-10],[1-1e-10,2+1e-10]])
        ci,draws=bootstrap_nei(p,100,10)
        self.assertGreater(ci[1],0)
        self.assertLess(ci[1],1e-18)
        _,scaled=bootstrap_nei(7*p,100,10)
        np.testing.assert_allclose(draws,scaled,rtol=1e-4,atol=1e-28)

    def test_recurrence_without_validation_leakage(self):
        p=np.array([[1.],[1.01],[3.],[1.005],[3.001],[7.]])
        r=recurrence(p,np.ones(6,dtype=bool),np.array([0,0,0,1,1,1]),1.,.1)
        self.assertEqual(r["classes"],2)
        self.assertEqual(r["recurrent_classes"],2)
        self.assertEqual(r["unmatched"],1)
        self.assertEqual(sorted(r["discovery_occupancy"]),[1,2])

    def test_gate_success_not_sufficient(self):
        policy={"tau_g":1e-9,"tau_c":1e-8,"tau_phi":1e-6}
        record={"optimizer_success":True,"stress":1.,"eta_g":1e-4,"chi_coll":.2,
                "lambda_min_over_kappa":.1,"hessian_tested":True,"inertia":[0,0,3],
                "phi":.2}
        result=gates(record,policy,False)
        self.assertFalse(result["admissible"])
        self.assertIn("stationarity",result["failures"])

    def test_exact_full_rank_target_and_scaling(self):
        x=np.array([[0.,0.],[1.,0.],[.2,1.2],[1.4,1.1]])
        policy={"tau_g":1e-9,"tau_c":1e-8,"tau_phi":1e-6,"tau_h_rel":1e-9}
        result=OptimizeResult(success=True,status=0,message="exact analytic control",nit=0,nfev=0)
        records=[]
        for scale in (1e-3,1.,1e3):
            z=scale*x
            _,_,_,r=diagnose(z,squareform(pdist(z)),result,policy,True)
            self.assertTrue(r["admissible"])
            self.assertTrue(r["control_admissible"])
            self.assertEqual(r["gauge_rank"],3)
            self.assertEqual(r["inertia"],[0,0,5])
            records.append(r)
        np.testing.assert_allclose([r["chi_coll"] for r in records],records[1]["chi_coll"])
        np.testing.assert_allclose([r["lambda_min_over_kappa"] for r in records],
                                   records[1]["lambda_min_over_kappa"])

    def test_wilson_failure_report(self):
        self.assertGreater(wilson(0,100)[1],0)
        self.assertLess(wilson(100,100)[0],1)
        self.assertIsNone(wilson(0,0))

    def test_calibration_requires_target_fit(self):
        policy={"tau_g":1e-9,"tau_c":1e-8,"tau_phi":1e-6}
        record={"optimizer_success":True,"stress":1.,"eta_g":1e-12,"chi_coll":.2,
                "lambda_min_over_kappa":.1,"hessian_tested":True,"inertia":[0,0,3],
                "phi":.2}
        result=gates(record,policy,True)
        self.assertTrue(result["numerical_admissible"])
        self.assertFalse(result["control_admissible"])
        self.assertFalse(result["analysis_admissible"])


if __name__=="__main__":
    unittest.main()
