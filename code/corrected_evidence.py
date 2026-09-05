#!/usr/bin/env python3
"""Acceptance-aware raw-stress experiments. No rejected run is encoded as NEI=0.

The attempted run is the Monte Carlo unit. Graphs remain the outer unit.
Artifact generation is separate from the static website and preserves legacy data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import networkx as nx
import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform
from sklearn import __version__ as sklearn_version
from sklearn.manifold import smacof
from threadpoolctl import threadpool_limits

from calibration_null import fg, Dp, gradient_check
from polish_certify import projected_spectrum


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_write(path, value):
    """Generated result artifact, not source editing. Atomic, finite JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    tmp.replace(path)


def nei_pairs(pairs):
    p = np.asarray(pairs, dtype=float)
    if p.ndim != 2 or min(p.shape) < 1 or not np.isfinite(p).all() or np.any(p < 0):
        raise ValueError("require finite nonnegative attempted/accepted run vectors")
    mean = p.mean(axis=0)
    if np.any(mean <= 0):
        raise ValueError("undefined NEI: nonpositive pair mean")
    return float(np.mean(np.var(p, axis=0, ddof=0) / mean**2))


def bootstrap_nei(pairs, repetitions, seed):
    """Ordinary whole-vector percentile bootstrap; not a finite-sample certificate."""
    p = np.asarray(pairs)
    if len(p) < 2:
        return None, np.array([])
    rng = np.random.default_rng(seed)
    # Center before squaring: raw-second-moment subtraction destroys a small floor.
    base = p.mean(axis=0)
    z = p - base
    weights = rng.multinomial(len(p), np.full(len(p), 1 / len(p)), size=repetitions) / len(p)
    out = []
    for w in np.array_split(weights, max(1, (repetitions + 63) // 64)):
        dz = w @ z
        mean = base + dz
        var = np.maximum(w @ (z*z) - dz*dz, 0.0)
        out.extend(np.mean(var / mean**2, axis=1).tolist())
    values = np.asarray(out)
    return np.quantile(values, [.025, .975]).tolist(), values


def wilson(k, n):
    if n == 0:
        return None
    z = 1.959963984540054
    p = k / n
    center = (p + z*z/(2*n)) / (1+z*z/n)
    radius = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [float(max(0., center-radius)), float(min(1., center+radius))]


def recurrence(pairs, accepted, batches, scale, epsilon):
    """Frozen sequential complete-link discovery partition, then validation.

    Validation assigned iff within epsilon of EVERY member of exactly one
    discovery class. Multiple matches are ambiguous, zero matches unmatched.
    No single-link chaining and no update of discovery classes from validation.
    These classes are resolution clusters, not certified algorithmic basins.
    """
    from scipy.cluster.hierarchy import linkage, fcluster
    ix = np.flatnonzero(accepted & (batches == 0))
    jx = np.flatnonzero(accepted & (batches == 1))
    if len(ix) == 0:
        return {"discovery_accepted": 0, "validation_accepted": int(len(jx)),
                "classes": None, "unmatched": None, "ambiguous": None}
    if len(ix) == 1:
        labels = np.ones(1, dtype=int)
    else:
        labels = fcluster(linkage(pdist(pairs[ix]) / scale, method="complete"),
                          t=epsilon, criterion="distance")
    groups = [ix[labels == v] for v in sorted(set(labels))]
    counts = np.zeros(len(groups), dtype=int)
    unmatched = ambiguous = 0
    for j in jx:
        matches = [i for i, group in enumerate(groups)
                   if np.max(np.linalg.norm(pairs[group] - pairs[j], axis=1))/scale <= epsilon]
        if len(matches) == 1:
            counts[matches[0]] += 1
        elif not matches:
            unmatched += 1
        else:
            ambiguous += 1
    return {"epsilon_D": epsilon, "discovery_accepted": int(len(ix)),
            "validation_accepted": int(len(jx)), "classes": len(groups),
            "discovery_occupancy": [len(g) for g in groups],
            "validation_matches": counts.tolist(),
            "recurrent_classes": int(np.sum(counts > 0)),
            "unmatched": unmatched, "ambiguous": ambiguous,
            "unmatched_fraction": unmatched/len(jx) if len(jx) else None,
            "unmatched_wilson95_conditional_on_discovery": wilson(unmatched, len(jx))}


def gates(record, protocol, exact_control):
    reasons = []
    if not record.get("optimizer_success", False):
        reasons.append("optimizer_unsuccessful")
    for key in ("stress", "eta_g", "chi_coll", "lambda_min_over_kappa"):
        if record.get(key) is None or not np.isfinite(record[key]):
            reasons.append("nonfinite_" + key)
    if record.get("eta_g", np.inf) > protocol["tau_g"]:
        reasons.append("stationarity")
    if record.get("chi_coll", -np.inf) < protocol["tau_c"]:
        reasons.append("collision")
    if not record.get("hessian_tested", False):
        reasons.append("hessian_unavailable")
    elif record["inertia"][0] > 0:
        reasons.append("negative_quotient_curvature")
    numerical = not reasons
    control = numerical and (record.get("phi", np.inf) <= protocol["tau_phi"])
    record.update(admissible=numerical, numerical_admissible=numerical,
                  analysis_admissible=control if exact_control else numerical,
                  control_admissible=control if exact_control else None,
                  failures=reasons)
    return record


def diagnose(x, delta, result, protocol, exact_control):
    n,p = x.shape
    x = x - x.mean(axis=0)
    pairs = pdist(x)
    target = delta[np.triu_indices(n, 1)]
    s = float(target@target)
    f,g = fg(x.ravel(), delta, n,p)
    record = {"optimizer_success": bool(result.success), "optimizer_status": int(result.status),
              "optimizer_message": str(result.message), "iterations": int(result.nit),
              "function_evaluations": int(result.nfev), "stress": f,
              "phi": float(np.sqrt(f/s)), "normalized_stress": f/s,
              "eta_g": float(np.linalg.norm(g)/np.sqrt(s)),
              "gradient_inf": float(np.max(np.abs(g))),
              "chi_coll": float(pairs.min()/np.sqrt(s/len(target))),
              "min_pair_distance": float(pairs.min()), "hessian_tested": False,
              "lambda_min_over_kappa": None, "lambda_min": None, "kappa_plus": None,
              "inertia": None, "gauge_rank": None}
    eigenvalues = np.full(n*p, np.nan)
    if record["chi_coll"] >= protocol["tau_c"]:
        w, kappa, q = projected_spectrum(x, delta, k=None)
        cutoff = protocol["tau_h_rel"] * max(kappa, np.finfo(float).tiny)
        record.update(hessian_tested=True, kappa_plus=kappa, lambda_min=float(w[0]),
                      lambda_min_over_kappa=float(w[0]/max(kappa,np.finfo(float).tiny)),
                      inertia=[int(np.sum(w < -cutoff)),int(np.sum(np.abs(w) <= cutoff)),
                               int(np.sum(w > cutoff))], gauge_rank=q)
        eigenvalues[:len(w)] = w
    return x,pairs,eigenvalues,gates(record,protocol,exact_control)


def task_one(task):
    threadpool_limits(1)
    graph_path, protocol, run_id, seed, config_hash = task
    graph_path = Path(graph_path)
    output = graph_path.parent.parent / "runs" / graph_path.stem / f"run-{run_id:04d}.npz"
    meta_path = output.with_suffix(".json")
    if output.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta["config_sha256"] != config_hash:
            raise ValueError("resume protocol mismatch")
        expected={"graph_sha256":digest(graph_path),"artifact_sha256":digest(output),
                  "run_id":run_id,"seed":seed,"batch":run_id//protocol["batch_size"]}
        if any(meta.get(key)!=value for key,value in expected.items()):
            raise ValueError("resume artifact, input, or attempted-run identity mismatch")
        return graph_path.stem, run_id, True
    graph = json.loads(graph_path.read_text())
    n = graph["n"]
    if "delta" in graph:
        delta = np.asarray(graph["delta"], dtype=float)
    else:
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(graph["edges"])
        if not nx.is_connected(g):
            raise ValueError("inputs must already have a documented connectedness policy")
        delta = np.asarray(nx.floyd_warshall_numpy(g, nodelist=list(range(n))), dtype=float)
    x0 = np.random.default_rng(seed).random((n,protocol["p"]))
    configs = graph.get("rungs", ["primary"])
    all_rungs = protocol["rungs"]
    records,coords,vectors,spectra = [],[],[],[]
    started = time.monotonic()
    try:
        y,stress,it = smacof(delta, n_components=protocol["p"], init=x0.copy(), n_init=1,
                            max_iter=protocol["smacof_max_iter"], eps=protocol["smacof_eps"],
                            normalized_stress=False, return_n_iter=True, random_state=0)
        y -= y.mean(axis=0)
        raw_pair = pdist(y)
        raw_f,raw_g = fg(y.ravel(),delta,n,protocol["p"])
        s = float(np.sum(delta[np.triu_indices(n,1)]**2))
        for name in configs:
            rung = all_rungs[name]
            try:
                result = minimize(fg,y.ravel().copy(),args=(delta,n,protocol["p"]),
                                  jac=True,method="L-BFGS-B",
                                  options={"maxiter":protocol["max_iter"],
                                           "maxfun":protocol["max_fun"],"maxls":50,
                                           "ftol":rung["ftol"],"gtol":rung["gtol"]})
                x,vec,eig,rec = diagnose(result.x.reshape(n,protocol["p"]),delta,result,
                                       protocol,graph["exact_control"])
                rec.update(rung=name,smacof_iterations=int(it),raw_stress=raw_f,
                           raw_eta_g=float(np.linalg.norm(raw_g)/np.sqrt(s)))
            except (FloatingPointError,ValueError,np.linalg.LinAlgError) as error:
                x = np.full_like(y,np.nan);vec = np.full(len(raw_pair),np.nan)
                eig = np.full(n*protocol["p"],np.nan)
                rec = {"rung":name,"admissible":False,"control_admissible":False,
                       "failures":["numerical_exception"],"exception":str(error)}
            records.append(rec);coords.append(x);vectors.append(vec);spectra.append(eig)
    except (FloatingPointError,ValueError,np.linalg.LinAlgError) as error:
        y = np.full_like(x0,np.nan); raw_pair=np.full(n*(n-1)//2,np.nan)
        for name in configs:
            records.append({"rung":name,"admissible":False,"control_admissible":False,
                            "failures":["smacof_exception"],"exception":str(error)})
            coords.append(y);vectors.append(raw_pair);spectra.append(np.full(n*protocol["p"],np.nan))
    output.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(output, x0=x0, x_raw=y, x_terminal=np.asarray(coords),
                        pairs=np.asarray(vectors), pairs_raw=raw_pair,
                        quotient_spectra=np.asarray(spectra))
    json_write(meta_path,{"config_sha256":config_hash,"graph_sha256":digest(graph_path),
                         "run_id":run_id,"batch":run_id//protocol["batch_size"],
                         "seed":seed,"rungs":records,"seconds":time.monotonic()-started,
                         "artifact_sha256":digest(output)})
    return graph_path.stem,run_id,False


def run_study(root, workers):
    root=Path(root)
    config_path=root/"protocol.json"
    config=json.loads(config_path.read_text())
    protocol=config["protocol"]
    config_hash=digest(config_path)
    checks={"gradient_directional_error":gradient_check(),
            "numpy":np.__version__,"scipy":scipy.__version__,"sklearn":sklearn_version,
            "networkx":nx.__version__,"python":platform.python_version(),
            "platform":platform.platform(),"workers":workers,"blas_threads_per_worker":1,
            "config_sha256":config_hash,
            "code_sha256":{name:digest(Path(__file__).parent/name)
                           for name in ("corrected_evidence.py","calibration_null.py",
                                        "polish_certify.py","graph_null_ensemble.py")}}
    check_path=root/"execution.json"
    if check_path.exists():
        old=json.loads(check_path.read_text())
        if old["code_sha256"] != checks["code_sha256"]:
            raise ValueError("cannot resume results under changed scientific implementation")
    json_write(check_path,checks)
    tasks=[]
    for path in sorted((root/"graphs").glob("*.json")):
        spec=json.loads(path.read_text())
        for i in range(protocol["M"]):
            seed=int(np.random.SeedSequence([config["seed"],spec["seed_id"],i]).generate_state(1)[0])
            tasks.append((str(path),protocol,i,seed,config_hash))
    print(f"START {len(tasks)} attempted runs, workers={workers}, config={config_hash[:12]}",flush=True)
    done=0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(task_one,t):t for t in tasks}
        for future in as_completed(futures):
            name,i,resumed=future.result()
            done+=1
            if done%100==0 or done==len(tasks):
                print(f"PROGRESS {done}/{len(tasks)} {name} run={i} resumed={resumed}",flush=True)
    json_write(root/"completion.json",{"attempted_tasks":len(tasks),"completed_tasks":done,
               "config_sha256":config_hash,"complete":True})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study",type=Path)
    parser.add_argument("--workers",type=int,default=4)
    args=parser.parse_args()
    run_study(args.study,args.workers)


if __name__=="__main__":
    main()
