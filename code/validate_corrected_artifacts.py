#!/usr/bin/env python3
"""Independent read-only audit of every saved terminal in a corrected study."""
import argparse
import json
from pathlib import Path
import numpy as np
import networkx as nx
from scipy.spatial.distance import pdist, squareform
from threadpoolctl import threadpool_limits
from corrected_evidence import digest,json_write


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study",type=Path)
    args=parser.parse_args();root=args.study
    threadpool_limits(1)
    config=json.loads((root/"protocol.json").read_text());policy=config["protocol"]
    checks=json.loads((root/"execution.json").read_text())
    if digest(root/"protocol.json")!=checks["config_sha256"]:
        raise ValueError("protocol hash changed")
    for name,h in checks["code_sha256"].items():
        if digest(Path(__file__).parent/name)!=h:
            raise ValueError("executed scientific implementation changed: "+name)
    input_hashes=json.loads((root/"input_hashes.json").read_text())
    graph_checks=terminals=attempts=0
    max_pair_error=max_stress_error=max_eta_error=0.
    for path in sorted((root/"graphs").glob("*.json")):
        if digest(path)!=input_hashes[path.name]:
            raise ValueError("frozen graph changed")
        spec=json.loads(path.read_text());n=spec["n"]
        if "delta" in spec:
            delta=np.asarray(spec["delta"])
        else:
            g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(spec["edges"])
            assert len(g)==n and g.number_of_edges()==spec["m"] and nx.is_connected(g)
            assert nx.number_of_selfloops(g)==0
            if spec["kind"]=="graph_null":
                parent=json.loads((root/"graphs"/(spec["anchor_id"]+".json")).read_text())
                assert n==parent["n"] and spec["m"]==parent["m"]
                if spec["ensemble"].startswith("degree"):
                    gp=nx.Graph();gp.add_nodes_from(range(n));gp.add_edges_from(parent["edges"])
                    assert dict(g.degree())==dict(gp.degree())
            delta=np.asarray(nx.floyd_warshall_numpy(g,nodelist=range(n)))
        target=delta[np.triu_indices(n,1)];S=float(target@target)
        assert np.isfinite(delta).all() and S>0 and np.all(target>0)
        graph_checks+=1
        for i in range(policy["M"]):
            stem=root/"runs"/path.stem/f"run-{i:04d}"
            meta=json.loads(stem.with_suffix(".json").read_text())
            assert meta["artifact_sha256"]==digest(stem.with_suffix(".npz"))
            assert meta["graph_sha256"]==digest(path)
            assert meta["config_sha256"]==checks["config_sha256"]
            expected_seed=int(np.random.SeedSequence([config["seed"],spec["seed_id"],i]).generate_state(1)[0])
            assert meta["seed"]==expected_seed and meta["run_id"]==i
            assert meta["batch"]==i//policy["batch_size"]
            with np.load(stem.with_suffix(".npz"),allow_pickle=False) as a:
                np.testing.assert_array_equal(a["x0"],np.random.default_rng(expected_seed).random((n,policy["p"])))
                for j,rec in enumerate(meta["rungs"]):
                    terminals+=1
                    assert rec["rung"]==spec["rungs"][j]
                    x=a["x_terminal"][j]
                    if not np.isfinite(x).all():
                        assert not rec["admissible"]
                        continue
                    pair=pdist(x)
                    error=float(np.max(np.abs(pair-a["pairs"][j])))
                    max_pair_error=max(max_pair_error,error)
                    assert error<=1e-12*max(1.,float(pair.max()))
                    residual=pair-target
                    f=float(residual@residual)
                    ferr=abs(f-rec["stress"])/max(1.,f)
                    max_stress_error=max(max_stress_error,ferr)
                    assert ferr<1e-10
                    distance=squareform(pair)
                    np.fill_diagonal(distance,1.)
                    coefficients=1.-delta/distance
                    np.fill_diagonal(coefficients,0.)
                    # Independent Laplacian-form gradient, unlike the executed
                    # pair-difference summation. Absolute audit tolerance because
                    # a numerical-floor gradient is not relatively resolvable.
                    gradient=2*(coefficients.sum(axis=1)[:,None]*x-coefficients@x)
                    eta=float(np.linalg.norm(gradient)/np.sqrt(S))
                    max_eta_error=max(max_eta_error,abs(eta-rec["eta_g"]))
                    assert abs(eta-rec["eta_g"])<1e-11
                    np.testing.assert_allclose(rec["phi"],np.sqrt(f/S),rtol=1e-6,atol=1e-13)
                    np.testing.assert_allclose(rec["chi_coll"],pair.min()/np.sqrt(S/len(pair)),rtol=1e-10)
                    if rec["hessian_tested"]:
                        w=a["quotient_spectra"][j]
                        w=w[np.isfinite(w)]
                        assert len(w)==n*policy["p"]-rec["gauge_rank"]
                        kap=float(np.maximum(w,0).sum()/len(w))
                        tol=policy["tau_h_rel"]*max(kap,np.finfo(float).tiny)
                        assert rec["inertia"]==[int(np.sum(w < -tol)),int(np.sum(abs(w)<=tol)),int(np.sum(w>tol))]
                    admissible=bool(rec["optimizer_success"] and rec["eta_g"]<=policy["tau_g"]
                                    and rec["chi_coll"]>=policy["tau_c"]
                                    and rec["hessian_tested"] and rec["inertia"][0]==0)
                    assert rec["admissible"]==admissible
                    if spec["exact_control"]:
                        assert rec["control_admissible"]==(admissible and rec["phi"]<=policy["tau_phi"])
            attempts+=1
        if graph_checks%20==0:
            print(f"AUDIT graphs={graph_checks} attempts={attempts} terminals={terminals}",flush=True)
    result={"status":"pass","graphs":graph_checks,"attempts":attempts,"terminals":terminals,
            "all_artifact_hashes":True,"all_input_hashes":True,"all_attempt_seeds":True,
            "all_terminal_pair_reconstructions":True,"all_gate_reconstructions":True,
            "max_pair_reconstruction_error":max_pair_error,"max_stress_relative_error":max_stress_error,
            "max_eta_absolute_error":max_eta_error,"all_gradients_independently_recomputed":True,
            "independent_hessian_derivatives":"separate deterministic unit tests; stored spectrum inertia checked here",
            "config_sha256":checks["config_sha256"],"validator_sha256":digest(__file__)}
    json_write(root/"artifact_audit.json",result)
    print(json.dumps(result,indent=2),flush=True)


if __name__=="__main__":
    main()
