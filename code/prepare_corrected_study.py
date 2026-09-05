#!/usr/bin/env python3
"""Freeze a bounded unweighted study before optimizer outcomes are inspected.

This is not the full historical network corpus. Input eligibility is declared
by parseability, unweighted policy, size, and provenance, never observed NEI.
Private input paths and raw coordinates stay in the local study directory.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import re
import networkx as nx
import numpy as np
from scipy.spatial.distance import pdist, squareform
from corrected_evidence import digest, json_write
from graph_null_ensemble import (degree_preserving_connected_null, connected_gnm_null,
                                 ConnectedGnmSamplingError,graph_diagnostics)


RUNG_NAMES = ["g6","g10","primary","g18","f12","f16"]
PROTOCOL = {
    "p":2,"M":100,"batch_size":50,"pair_weights":"all off-diagonal pairs, w=1",
    "initialization":"absolute iid U[0,1] coordinates; Delta kept in original units; no scale-equivariance claim",
    "independent_batches":2,"smacof_max_iter":3000,"smacof_eps":1e-12,
    "max_iter":50000,"max_fun":200000,"max_line_search_steps":50,
    "tau_g":1e-9,"tau_c":1e-8,"tau_h_rel":1e-9,"tau_phi":1e-6,
    "epsilon_D":1e-5,"epsilon_D_sensitivity":[1e-6,1e-5,1e-4,1e-3],
    "tau_g_sensitivity":[1e-10,1e-9,1e-8,1e-7],
    "bootstrap_repetitions":999,
    "rungs":{
        "g6":{"gtol":1e-6,"ftol":1e-20},
        "g10":{"gtol":1e-10,"ftol":1e-20},
        "primary":{"gtol":1e-14,"ftol":1e-20},
        "g18":{"gtol":1e-18,"ftol":1e-20},
        "f12":{"gtol":1e-14,"ftol":1e-12},
        "f16":{"gtol":1e-14,"ftol":1e-16}
    },
    "policy":"success AND finite AND stationarity AND collision AND n_negative=0; no adaptive rescue",
    "control_policy":"numerical acceptance AND sqrt(F/S_delta)<=tau_phi for exact-target controls only",
    "interpretation":"conditional admissible-law NEI; candidates, not exact minima or thermodynamic degeneracy"
}


def canonical_spec(key,label,g,seed_id,kind="synthetic",exact=False,anchor=False):
    nodes=sorted(g.nodes())
    g=nx.convert_node_labels_to_integers(g,ordering="sorted")
    if not nx.is_connected(g):
        raise ValueError(f"{key}: disconnected source requires an explicit policy")
    return {"id":key,"label":label,"kind":kind,"n":len(g),"m":g.number_of_edges(),
            "edges":sorted([sorted(e) for e in g.edges()]),"seed_id":seed_id,
            "source_labels":[str(v) for v in nodes],"exact_control":exact,
            "null_anchor":anchor,"rungs":RUNG_NAMES,
            "graph_diagnostics":graph_diagnostics(g)}


def load_real(entry,seed_id):
    path=Path(entry["path"])
    if digest(path) != entry["source_sha256"]:
        raise ValueError("input source hash mismatch")
    if entry["weighted"]:
        raise ValueError("weighted-null specification is outside this unweighted study")
    g=nx.Graph(); removed_loops=duplicates=0;edge_lines=0
    for lineno,line in enumerate(path.read_text().splitlines(),1):
        if not line.strip() or line.lstrip().startswith(("#","%")):
            continue
        fields=re.split(r"[\s,]+",line.strip())
        if len(fields)<2:
            raise ValueError(f"{entry['id']}:{lineno} malformed edge line")
        a,b=int(fields[0]),int(fields[1])
        g.add_nodes_from([a,b]);edge_lines+=1
        if a==b:
            removed_loops+=1
        else:
            duplicates+=int(g.has_edge(a,b))
            g.add_edge(a,b)
    if len(g)!=entry["expected_n"] or g.number_of_edges()!=entry["expected_e"]:
        raise ValueError(f"independent parser N/E mismatch: {entry['id']} {len(g)},{g.number_of_edges()}")
    spec=canonical_spec(entry["id"],entry["label"],g,seed_id,"real",anchor=True)
    spec["source_provenance"]=entry
    spec["preprocessing"]={"header":False,"columns_used":[0,1],"weight":None,
                           "ignored_extra_columns":True,"edge_lines":edge_lines,
                           "self_loops_removed":removed_loops,"duplicate_edges_collapsed":duplicates,
                           "largest_component_substitution":False}
    return spec


def null_task(task):
    root,anchor,ensemble,index,seed,burn_multiple,gnm_count=task
    root=Path(root)
    graph=nx.Graph()
    graph.add_nodes_from(range(anchor["n"]));graph.add_edges_from(anchor["edges"])
    if ensemble=="gnm":
        try:
            generated=connected_gnm_null(len(graph),graph.number_of_edges(),n_samples=gnm_count,
                                         seed=seed,max_attempts_per_sample=10000)
        except ConnectedGnmSamplingError as exc:
            json_write(root/"null_meta"/f"{anchor['id']}--gnm-failed.json",
                       {"status":"generation_failed","reason":str(exc),"metadata":exc.metadata})
            return anchor["id"],ensemble,0
        graphs=generated["graphs"]
    else:
        generated=degree_preserving_connected_null(
            graph,n_samples=1,burnin_attempts=burn_multiple*graph.number_of_edges(),
            thinning_attempts=0,seed=seed,trace_every=max(1,10*graph.number_of_edges()))
        graphs=generated["graphs"]
    meta_name=f"{anchor['id']}--{ensemble}-{index:03d}"
    json_write(root/"null_meta"/(meta_name+".json"),generated["metadata"])
    for offset,g in enumerate(graphs):
        i=index+offset
        key=f"{anchor['id']}--{ensemble}-{i:03d}"
        spec=canonical_spec(key,key,g,int(np.random.SeedSequence([seed,i,811]).generate_state(1)[0]),
                            "graph_null")
        spec.update(anchor_id=anchor["id"],ensemble=ensemble,rungs=["primary"],
                    null_metadata=f"null_meta/{meta_name}.json",
                    duplicate_of_input=bool(set(map(tuple,spec["edges"]))==
                                             set(map(tuple,anchor["edges"]))))
        json_write(root/"graphs"/(key+".json"),spec)
    return anchor["id"],ensemble,len(graphs)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study",type=Path)
    parser.add_argument("--inputs",required=True,type=Path)
    parser.add_argument("--workers",type=int,default=4)
    args=parser.parse_args()
    root=args.study
    if (root/"protocol.json").exists():
        raise RuntimeError("refusing to overwrite a frozen study; choose a new study directory")
    root.mkdir(parents=True,exist_ok=True)
    input_manifest=json.loads(args.inputs.read_text())
    specs=[]
    fixed=[
        ("path60","Path P60",nx.path_graph(60),True,False),
        ("path120","Path P120",nx.path_graph(120),True,False),
        ("grid8","Lattice 8x8",nx.grid_2d_graph(8,8),False,True),
        ("grid12","Lattice 12x12",nx.grid_2d_graph(12,12),False,False),
        ("cycle60","Cycle C60",nx.cycle_graph(60),False,False),
        ("ring4_60","Regular ring N60 k4",nx.watts_strogatz_graph(60,4,0,seed=3),False,True),
        ("er100","ER N100 p0.06 seed3",nx.gnp_random_graph(100,.06,seed=3),False,True),
        ("ba100","BA N100 m2 seed3",nx.barabasi_albert_graph(100,2,seed=3),False,True),
        ("er120","ER N120 p0.05 seed3",nx.gnp_random_graph(120,.05,seed=3),False,False),
        ("ba120","BA N120 m2 seed3",nx.barabasi_albert_graph(120,2,seed=3),False,False),
    ]
    for i,(key,label,g,exact,anchor) in enumerate(fixed):
        # Historical synthetic generation used the LCC. Record before/after explicitly;
        # this preprocessing is NEVER performed on matched nulls.
        original_n,original_m=len(g),g.number_of_edges()
        g=g.subgraph(max(nx.connected_components(g),key=len)).copy()
        spec=canonical_spec(key,label,g,100+i,"synthetic",exact,anchor)
        spec["source_generation"]={"seed":3,"original_n":original_n,"original_m":original_m,
                                  "lcc_preprocessing":True,"lcc_changed":len(g)!=original_n}
        specs.append(spec)
    target=np.random.default_rng(8031).normal(size=(20,2))
    delta=squareform(pdist(target))
    specs.append({"id":"euclidean20","label":"Exact full-rank Euclidean target N20",
                  "kind":"metric_control","n":20,"m":190,"delta":delta.tolist(),
                  "target_coordinates":target.tolist(),"seed_id":8032,
                  "exact_control":True,"null_anchor":False,"rungs":RUNG_NAMES})
    for i,entry in enumerate(input_manifest["graphs"]):
        specs.append(load_real(entry,1000+i))
    config={"study_id":root.name,"seed":2026090501,"status_at_freeze":"prospective",
            "protocol":PROTOCOL,"input_manifest_sha256":digest(args.inputs),
            "scope":"bounded corrected controls + three unweighted real networks; NOT full historical sweep",
            "null_design":{"B_degree":20,"B_gnm":20,"B_degree_long":8,
                           "degree_attempts_per_edge":100,"degree_long_attempts_per_edge":500,
                           "degree_sampling":"independent fresh seeded chain per endpoint; finite-time kernel",
                           "uniform_mixing_certified":False,"gnm_attempt_cap_per_sample":10000,
                           "gnm_failure_policy":"record failure, do not substitute LCC or real graph",
                           "inference_unit":"graph realization outside, attempted embedding vector inside"},
            "input_graphs":[{k:s[k] for k in ("id","label","kind","n","m","exact_control","null_anchor")}
                            for s in specs],
            "selection_rule":"fixed synthetic controls and three independently parsed unweighted source files; no selection by NEI",
            "negative_results":"retain all failures, low acceptance, nonrecurrence, opposite-signed contrasts",
            "publication":"only summaries and hashes automatic; raw source data and coordinates local",
            "outstanding":"weighted-null repair, full-corpus loader audit, full sweep and M200/400 extension"}
    json_write(root/"protocol.json",config)
    for spec in specs:
        json_write(root/"graphs"/(spec["id"]+".json"),spec)
    print(f"FROZEN {digest(root/'protocol.json')} source_graphs={len(specs)}",flush=True)
    tasks=[]
    for spec in specs:
        if not spec["null_anchor"]:
            continue
        for ensemble,count,burn in (("degree",20,100),("degree_long",8,500)):
            for index in range(count):
                seed=int(np.random.SeedSequence([config["seed"],spec["seed_id"],
                                                900 if ensemble=="degree" else 901,index]).generate_state(1)[0])
                tasks.append((str(root),spec,ensemble,index,seed,burn,0))
        seed=int(np.random.SeedSequence([config["seed"],spec["seed_id"],902]).generate_state(1)[0])
        tasks.append((str(root),spec,"gnm",0,seed,0,20))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in as_completed([pool.submit(null_task,t) for t in tasks]):
            anchor,ensemble,count=result.result()
            print(f"NULL {anchor} {ensemble} generated={count}",flush=True)
    graph_files=sorted((root/"graphs").glob("*.json"))
    json_write(root/"input_hashes.json",{p.name:digest(p) for p in graph_files})
    print(f"READY graphs={len(graph_files)} attempted_runs={len(graph_files)*PROTOCOL['M']}",flush=True)


if __name__=="__main__":
    main()
