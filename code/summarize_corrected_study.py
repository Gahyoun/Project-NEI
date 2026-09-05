#!/usr/bin/env python3
"""Generate finite-protocol evidence summaries without upgrading the full corpus.

All intervals are approximate resampling summaries. No graph-null p-value is
reported: finite-time rewiring is not a certified uniform randomization test.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import networkx as nx
from scipy.spatial.distance import pdist
from threadpoolctl import threadpool_limits
from corrected_evidence import (nei_pairs,bootstrap_nei,wilson,recurrence,
                                json_write,digest)
from calibration_null import Dp


def quantiles(a):
    values=np.asarray([v for v in a if v is not None],dtype=float)
    values=values[np.isfinite(values)]
    return np.quantile(values,[0,.5,1]).tolist() if len(values) else None


def estimate(pairs,mask,repetitions,seed):
    accepted=pairs[mask]
    if len(accepted)<2:
        return {"M_accepted":len(accepted),"nei":None,"bootstrap_percentile95":None,
                "reason":"fewer than two accepted runs"},np.array([])
    value=nei_pairs(accepted)
    interval,boot=bootstrap_nei(accepted,repetitions,seed)
    z=accepted/accepted.mean(axis=0)/np.sqrt(accepted.shape[1])
    z-=z.mean(axis=0)
    gram=z@z.T/len(z)
    tr=float(np.trace(gram));sq=float(np.sum(gram*gram))
    deff=tr*tr/sq if sq>0 else None
    return {"M_accepted":len(accepted),"nei":value,"bootstrap_percentile95":interval,
            "d_eff_pair_standardized":deff,
            "covariance_rank_ceiling":min(len(z)-1,z.shape[1]),
            "trace_identity_absolute_error":abs(tr-value),
            "interval_warning":"whole-run percentile bootstrap; finite-M coverage and unseen classes not certified"},boot


def paired_contrast(pairs_a,mask_a,pairs_b,mask_b,B,seed):
    """Same attempted rows resampled jointly; each accepted law renormalized."""
    rng=np.random.default_rng(seed)
    M=len(pairs_a)
    counts=rng.multinomial(M,np.full(M,1/M),size=B).astype(float)
    def draws(p,mask):
        if mask.sum()<2:
            return np.full(B,np.nan)
        p=p[mask];w=counts[:,mask]
        denom=w.sum(axis=1)
        good=denom>=2
        w=np.divide(w,denom[:,None],out=np.zeros_like(w),where=denom[:,None]>0)
        base=p.mean(axis=0);z=p-base
        out=np.full(B,np.nan)
        for idx in np.array_split(np.arange(B),max(1,(B+63)//64)):
            dz=w[idx]@z
            var=np.maximum(w[idx]@(z*z)-dz*dz,0)
            out[idx]=np.mean(var/(base+dz)**2,axis=1)
        out[~good]=np.nan
        return out
    difference=draws(pairs_b,mask_b)-draws(pairs_a,mask_a)
    finite=np.isfinite(difference)
    interval=np.quantile(difference[finite],[.025,.975]).tolist() if finite.mean()>=.95 else None
    common=mask_a&mask_b
    return {"definition":"NEI(target rung conditional law) - NEI(primary conditional law)",
            "paired_bootstrap_percentile95":interval,
            "interval_condition":"conditional on bootstrap replicates with at least two accepted rows in each arm; interval withheld below 95% valid replicates",
            "valid_bootstrap_fraction":float(finite.mean()),
            "both_accepted":int(common.sum()),
            "primary_only_accepted":int(np.sum(mask_a&~mask_b)),
            "target_only_accepted":int(np.sum(mask_b&~mask_a)),
            "neither_accepted":int(np.sum(~mask_a&~mask_b)),
            "common_subset_nei_difference_sensitivity":
                nei_pairs(pairs_b[common])-nei_pairs(pairs_a[common]) if common.sum()>=2 else None,
            "common_subset_note":"different selection-conditioned estimand; not replacement for primary laws"}


def summarize_graph(root,path,config):
    graph=json.loads(path.read_text())
    protocol=config["protocol"];M=protocol["M"];B=protocol["bootstrap_repetitions"]
    ids=graph["rungs"];rungs=[];arrays=[];raw=[];batches=[]
    for i in range(M):
        stem=root/"runs"/path.stem/f"run-{i:04d}"
        meta=json.loads(stem.with_suffix(".json").read_text())
        if meta["config_sha256"] != digest(root/"protocol.json"):
            raise ValueError("mixed protocol")
        if digest(stem.with_suffix(".npz")) != meta["artifact_sha256"]:
            raise ValueError("artifact hash mismatch")
        if meta["graph_sha256"] != digest(path):
            raise ValueError("graph changed since execution")
        with np.load(stem.with_suffix(".npz"),allow_pickle=False) as data:
            arrays.append(data["pairs"]);raw.append(data["pairs_raw"])
        rungs.append(meta["rungs"]);batches.append(meta["batch"])
    pairs=np.asarray(arrays);raw=np.asarray(raw);batches=np.asarray(batches)
    if "delta" in graph:
        delta=np.asarray(graph["delta"])
    else:
        g=nx.Graph();g.add_nodes_from(range(graph["n"]));g.add_edges_from(graph["edges"])
        delta=np.asarray(nx.floyd_warshall_numpy(g,nodelist=range(len(g))))
    target=delta[np.triu_indices(len(delta),1)];S=float(target@target)
    out={k:graph[k] for k in ("id","label","kind","n","m","exact_control","null_anchor")}
    out.update(S_delta=S,s_delta=float(np.sqrt(S/len(target))),D2=Dp(delta),
               graph_sha256=digest(path),rungs={},recurrence={},rarefaction={})
    if graph["kind"]=="real":
        entry=graph["source_provenance"]
        out["source"]={k:entry[k] for k in ("id","source_sha256","weighted","expected_n","expected_e")}
        out["preprocessing"]=graph["preprocessing"]
    for key in ("anchor_id","ensemble","duplicate_of_input","source_generation","graph_diagnostics","null_metadata"):
        if key in graph:
            out[key]=graph[key]
    masks={};boot_primary=np.array([])
    for r,name in enumerate(ids):
        records=[row[r] for row in rungs]
        accepted=np.asarray([rec["admissible"] for rec in records],dtype=bool)
        masks[name]=accepted
        est,boot=estimate(pairs[:,r],accepted,B,config["seed"]+graph["seed_id"]+r)
        if name=="primary":
            boot_primary=boot
        failures=Counter(reason for rec in records for reason in rec["failures"])
        est.update(M_attempted=M,alpha=float(accepted.mean()),alpha_wilson95=wilson(int(accepted.sum()),M),
                   failures=dict(failures),optimizer_success=sum(bool(rec.get("optimizer_success")) for rec in records),
                   optimizer_termination=dict(Counter(rec.get("optimizer_message","exception") for rec in records)),
                   hessian_tested=sum(rec.get("hessian_tested",False) for rec in records),
                   eta_g_all_min_median_max=quantiles([rec.get("eta_g") for rec in records]),
                   chi_coll_all_min_median_max=quantiles([rec.get("chi_coll") for rec in records]),
                   lambda_ratio_all_min_median_max=quantiles([rec.get("lambda_min_over_kappa") for rec in records]),
                   phi_all_min_median_max=quantiles([rec.get("phi") for rec in records]),
                   stress_all_min_median_max=quantiles([rec.get("normalized_stress") for rec in records]))
        finite=np.isfinite(pairs[:,r]).all(axis=1)
        est["nei_finite_ungated_diagnostic"]=nei_pairs(pairs[finite,r]) if finite.sum()>=2 else None
        if graph["exact_control"]:
            ctrl=np.asarray([bool(rec.get("control_admissible")) for rec in records])
            ctrl_est,_=estimate(pairs[:,r],ctrl,B,config["seed"]+graph["seed_id"]+r+80)
            ctrl_est.update(alpha_control=float(ctrl.mean()),alpha_control_wilson95=wilson(int(ctrl.sum()),M),
                            target_fit_rejections=int(np.sum(accepted&~ctrl)))
            est["exact_target_control"]=ctrl_est
        out["rungs"][name]=est
    pi=ids.index("primary"); primary=pairs[:,pi];accepted=masks["primary"]
    out["raw_smacof_nei_ungated"]=nei_pairs(raw) if np.isfinite(raw).all() else None
    if accepted.sum()>=2:
        out["rho_D_max_accepted"]=float(pdist(primary[accepted]).max()/np.sqrt(S))
    else:
        out["rho_D_max_accepted"]=None
    for epsilon in protocol["epsilon_D_sensitivity"]:
        out["recurrence"][str(epsilon)]=recurrence(primary,accepted,batches,np.sqrt(S),epsilon)
    for count in (25,50,100):
        mask=accepted & (np.arange(M)<count)
        out["rarefaction"][str(count)]={"attempted":count,"accepted":int(mask.sum()),
                  "nei":nei_pairs(primary[mask]) if mask.sum()>=2 else None}
    out["batch_estimates"]=[]
    for batch in (0,1):
        mask=accepted & (batches==batch)
        out["batch_estimates"].append({"batch":batch,"attempted":int(np.sum(batches==batch)),
                    "accepted":int(mask.sum()),"nei":nei_pairs(primary[mask]) if mask.sum()>=2 else None})
    out["gate_sensitivity"]={}
    recs=[row[pi] for row in rungs]
    for tau in protocol["tau_g_sensitivity"]:
        mask=np.asarray([bool(rec.get("optimizer_success",False)) and
                         rec.get("eta_g",np.inf)<=tau and rec.get("chi_coll",-1)>=protocol["tau_c"]
                         and rec.get("hessian_tested",False) and rec["inertia"][0]==0 for rec in recs])
        out["gate_sensitivity"][str(tau)]={"accepted":int(mask.sum()),
                  "nei":nei_pairs(primary[mask]) if mask.sum()>=2 else None}
    out["paired_rung_contrasts"]={}
    for r,name in enumerate(ids):
        if name!="primary":
            out["paired_rung_contrasts"][name]=paired_contrast(primary,accepted,pairs[:,r],masks[name],
                                                             B,config["seed"]+graph["seed_id"]+r)
    return out,boot_primary


def graph_contrasts(summaries,boot,config):
    rows=[];rng=np.random.default_rng(config["seed"]+909)
    B=config["protocol"]["bootstrap_repetitions"]
    for anchor in [g for g in summaries if g["null_anchor"]]:
        ar=anchor["rungs"]["primary"]
        for ensemble in ("degree","gnm","degree_long"):
            requested=config["null_design"]["B_"+ensemble]
            group=[g for g in summaries if g.get("anchor_id")==anchor["id"] and g.get("ensemble")==ensemble]
            available=[g for g in group if g["rungs"]["primary"]["nei"] is not None]
            vals=np.asarray([g["rungs"]["primary"]["nei"] for g in available])
            complete=len(group)==requested and len(available)==requested
            row={"anchor_id":anchor["id"],"ensemble":ensemble,
                 "generated_graphs":len(group),"estimable_graphs":len(available),
                 "requested_graphs":requested,
                 "anchor_nei":ar["nei"],"anchor_alpha":ar["alpha"],
                 "null_acceptance_min_median_max":quantiles([g["rungs"]["primary"]["alpha"] for g in group]),
                 "available_null_nei_mean_descriptive":float(vals.mean()) if len(vals) else None,
                 "null_nei_mean":float(vals.mean()) if complete else None,
                 "null_nei_sd_between_graph_estimates":float(vals.std(ddof=1)) if len(vals)>1 else None,
                 "contrast":None,"outer_graph_percentile95":None,"nested_resampling95_sensitivity":None,
                 "complete_requested_ensemble":complete,
                 "p_value":None,
                 "outer_graph_interval_definition":"anchor point estimate minus bootstrap mean of null-graph point estimates; anchor finite-M uncertainty excluded",
                 "nested_interval_definition":"anchor accepted-run bootstrap minus outer-null bootstrap with within-null accepted-run resampling",
                 "inference_note":"finite-M contrast; percentile intervals approximate; no exact randomization p-value"}
            if complete and len(available)>=2 and ar["nei"] is not None:
                row["contrast"]=ar["nei"]-float(vals.mean())
                idx=rng.integers(len(vals),size=(B,len(vals)))
                outer=ar["nei"]-vals[idx].mean(axis=1)
                row["outer_graph_percentile95"]=np.quantile(outer,[.025,.975]).tolist()
                aboot=boot[anchor["id"]]
                if len(aboot):
                    draws_a=rng.choice(aboot,size=B)
                    nested=np.empty_like(idx,dtype=float)
                    for b in range(B):
                        for j,k in enumerate(idx[b]):
                            nested[b,j]=rng.choice(boot[available[k]["id"]])
                    row["nested_resampling95_sensitivity"]=np.quantile(draws_a-nested.mean(axis=1),[.025,.975]).tolist()
            if not complete:
                row["selection_warning"]="requested ensemble incomplete or contains undefined-NEI nulls; available-only mean is descriptive and unconditional null contrast withheld"
            rows.append(row)
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study",type=Path)
    args=parser.parse_args();root=args.study
    threadpool_limits(1)
    config=json.loads((root/"protocol.json").read_text())
    if not json.loads((root/"completion.json").read_text())["complete"]:
        raise ValueError("study incomplete")
    summaries=[];boot={}
    for i,path in enumerate(sorted((root/"graphs").glob("*.json"))):
        out,draws=summarize_graph(root,path,config)
        summaries.append(out);boot[out["id"]]=draws
        json_write(root/"summaries"/(out["id"]+".json"),out)
        if (i+1)%10==0:
            print(f"SUMMARY {i+1}",flush=True)
    contrasts=graph_contrasts(summaries,boot,config)
    failed=[]
    for path in sorted((root/"null_meta").glob("*failed.json")):
        failure=json.loads(path.read_text())
        failure.update(anchor_id=path.name.split("--gnm-failed.json")[0],ensemble="gnm")
        failed.append(failure)
    result={"schema_version":"corrected-study-summary/v1","summarizer_sha256":digest(__file__),
            "study_id":root.name,"status":"bounded corrected study complete; full corpus pending",
            "config_sha256":digest(root/"protocol.json"),
            "execution":json.loads((root/"execution.json").read_text()),
            "protocol":config["protocol"],"null_design":config["null_design"],
            "graph_count":len(summaries),"attempted_runs":len(summaries)*config["protocol"]["M"],
            "terminal_optimizations":sum(len(g["rungs"])*config["protocol"]["M"] for g in summaries),
            "sources":[g for g in summaries if g["kind"]!="graph_null"],
            "null_graphs":[g for g in summaries if g["kind"]=="graph_null"],
            "graph_contrasts":contrasts,"null_generation_failures":failed,
            "scope":config["scope"],"outstanding":config["outstanding"],
            "interpretation_limits":[
                "Finite-time degree rewiring kernel, not certified uniform connected degree ensemble.",
                "No full-corpus claim from a three-real-network bounded study.",
                "Admissibility is numerical; strict/global/equal-energy minima not certified.",
                "M=100 is attempted count. Conditional empirical counts and acceptance separately reported.",
                "Resampling intervals have no guaranteed small-sample coverage or unseen-class correction.",
                "No automatic interpretation of a near-zero Hessian mode as a continuous family."]}
    json_write(root/"summary.json",result)
    print(f"SUMMARY COMPLETE graphs={len(summaries)} contrasts={len(contrasts)}",flush=True)


if __name__=="__main__":
    main()
