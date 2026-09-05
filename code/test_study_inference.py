#!/usr/bin/env python3
"""Regression tests for attempted-row and graph-level aggregation."""
import unittest
import numpy as np
from summarize_corrected_study import paired_contrast,estimate,graph_contrasts


class StudyInferenceTests(unittest.TestCase):
    def test_identical_rungs_paired_difference_zero(self):
        p=np.array([[1.,3.],[2.,2.],[3.,1.],[4.,2.]])
        mask=np.ones(4,dtype=bool)
        r=paired_contrast(p,mask,p,mask,200,7)
        np.testing.assert_equal(r["paired_bootstrap_percentile95"],[0.,0.])
        self.assertEqual(r["both_accepted"],4)

    def test_gate_changes_preserve_attempted_denominator(self):
        p=np.array([[1.,3.],[2.,2.],[3.,1.],[4.,2.]])
        a=np.array([1,1,1,0],dtype=bool)
        b=np.array([0,1,1,1],dtype=bool)
        r=paired_contrast(p,a,p,b,500,10)
        self.assertEqual(r["both_accepted"],2)
        self.assertEqual(r["primary_only_accepted"],1)
        self.assertEqual(r["target_only_accepted"],1)
        self.assertEqual(r["common_subset_nei_difference_sensitivity"],0.)

    def test_insufficient_acceptance_not_zero(self):
        p=np.array([[1.,2.],[3.,4.]])
        result,draws=estimate(p,np.array([True,False]),100,8)
        self.assertIsNone(result["nei"])
        self.assertEqual(len(draws),0)

    def test_graph_unit_not_run_count(self):
        def item(key,value,anchor=False):
            return {"id":key,"null_anchor":anchor,"rungs":{"primary":{"nei":value,"alpha":1}}}
        a=item("real",.1,True)
        n1=item("n1",.2);n2=item("n2",.4)
        for n in (n1,n2):
            n.update(anchor_id="real",ensemble="degree")
        boot={"real":np.full(100,.1),"n1":np.full(100,.2),"n2":np.full(100,.4)}
        cfg={"seed":3,"protocol":{"bootstrap_repetitions":100},
             "null_design":{"B_degree":20,"B_gnm":20,"B_degree_long":8}}
        result=graph_contrasts([a,n1,n2],boot,cfg)
        degree=result[0]
        self.assertEqual(degree["estimable_graphs"],2)
        self.assertFalse(degree["complete_requested_ensemble"])
        self.assertIsNone(degree["contrast"])
        self.assertIsNone(degree["outer_graph_percentile95"])
        self.assertIsNone(degree["nested_resampling95_sensitivity"])
        self.assertIsNone(degree["null_nei_mean"])
        self.assertAlmostEqual(degree["available_null_nei_mean_descriptive"],.3)
        self.assertIn("selection_warning",degree)
        self.assertIsNone(degree["p_value"])

    def test_outer_interval_excludes_anchor_run_uncertainty(self):
        a={"id":"a","null_anchor":True,"rungs":{"primary":{"nei":.1,"alpha":1}}}
        n={"id":"n","null_anchor":False,"anchor_id":"a","ensemble":"degree",
           "rungs":{"primary":{"nei":.3,"alpha":1}}}
        n2={**n,"id":"n2"}
        boot={"a":np.linspace(0,.2,100),"n":np.full(100,.3),"n2":np.full(100,.3)}
        cfg={"seed":3,"protocol":{"bootstrap_repetitions":100},
             "null_design":{"B_degree":2,"B_gnm":2,"B_degree_long":2}}
        row=graph_contrasts([a,n,n2],boot,cfg)[0]
        np.testing.assert_allclose(row["outer_graph_percentile95"],[-.2,-.2])
        self.assertGreater(np.ptp(row["nested_resampling95_sensitivity"]),.1)


if __name__=="__main__":
    unittest.main()
