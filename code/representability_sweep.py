#!/usr/bin/env python3
"""representability_sweep.py — P1. protocol 이 개입하지 않는 축을 전 표본에 계산한다.

임베딩을 돌리지 않는다. graph metric Delta 하나에서 eigendecomposition 한 번이면
끝나므로, sweep 의 n_max(=6000, 앙상블 메모리 제약)를 따를 이유가 없다.

    B  = -1/2 C Delta^(2) C ,      mu_1 >= ... >= mu_N   (B 의 eigenvalue)
    D_p      = [ sum_{a>p} mu_a^+ + sum_a mu_a^- ] / sum_a |mu_a|
    D_p^dim  =   sum_{a>p} mu_a^+                       / sum_a |mu_a|
    D^neg    =                        sum_a mu_a^-      / sum_a |mu_a|

D_p = D_p^dim + D^neg 이고, D^neg 는 p 에 의존하지 않는다. 앞은 '차원이 모자란' 성분,
뒤는 '애초에 유클리드가 아닌' 성분이다. Schoenberg 판정에 의해 D_p = 0 인 것과
Delta 가 R^p 에서 정확히 실현되는 것이 동치이다.

loader 는 sweep 과 같은 경로를 쓴다 (run_nei_unified + force_unweighted). 그래야
N, E 가 기존 표와 일치한다.
"""
from __future__ import annotations

import argparse, os, sys, time, traceback
import numpy as np
import pandas as pd

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.dirname(_here))          # run_nei_unified 는 상위에 있다
import run_nei_unified as U
from nei_core import shortest_path_matrix
from run_referee_sweep import force_unweighted

P_LIST = (1, 2, 3, 5, 10)


def gram(Delta: np.ndarray) -> np.ndarray:
    """이중중심화. 큰 N 에서 임시배열을 줄이려고 제자리 연산을 쓴다."""
    B = Delta.astype(np.float64, copy=True)
    B *= B                                   # Delta^(2)
    rm = B.mean(axis=1, keepdims=True)
    gm = float(B.mean())
    B -= rm
    B -= rm.T
    B += gm
    B *= -0.5
    B += B.T                                 # 대칭화
    B *= 0.5
    return B


def analyze(path, n_max=12000):
    t0 = time.time()
    G_raw, meta = U.load_network(path)
    G = U.get_gcc(G_raw)
    N, E = G.number_of_nodes(), G.number_of_edges()
    base = dict(path=str(path), N=N, E=E)
    if N < 4:
        return {**base, "status": f"skipped: N={N} < 4"}
    if N > n_max:
        return {**base, "status": f"skipped: N={N} > n_max={n_max}"}

    w = meta.get("weight_for_nei", None)
    if w is not None and meta.get("dataset_type") == "generic" and force_unweighted(path):
        w = None
        meta["weight_definition"] = "unweighted (Table VI l_uv=1)"

    D = shortest_path_matrix(G, weight=w)
    if not np.all(np.isfinite(D)):
        return {**base, "status": "FAIL: 무한 거리 (비연결)"}

    mu = np.linalg.eigvalsh(gram(D))[::-1]
    tot = float(np.abs(mu).sum())
    if tot <= 0:
        return {**base, "status": "FAIL: 퇴화 spectrum"}

    pos = np.maximum(mu, 0.0)
    neg = float(np.maximum(-mu, 0.0).sum() / tot)      # p 무관
    out = {**base, "status": "ok",
           "weighted": w is not None,
           "weight_def": meta.get("weight_definition", ""),
           "D_neg": neg,
           "mu_max": float(mu[0]), "mu_min": float(mu[-1]),
           "mu_abs_sum": tot,
           "rank_eps": int((np.abs(mu) > 1e-10 * abs(mu[0])).sum()),
           "secs": 0.0}
    psum = float(pos.sum())
    for p in P_LIST:
        if p >= N:
            continue
        dim = float(pos[p:].sum() / tot)
        out[f"D{p}_dim"] = dim
        out[f"D{p}"] = dim + neg
        out[f"expl{p}"] = float(pos[:p].sum() / psum) if psum > 0 else float("nan")
    out["secs"] = round(time.time() - t0, 1)
    out["_mu"] = mu
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="*", default=U.DEFAULT_ROOTS)
    ap.add_argument("--paths-file", default=None,
                    help="확정된 표본 매니페스트. 주면 roots 스캔 대신 이 목록만 쓴다.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--spec-dir", default="repr_spectra")
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--shard-index", type=int, default=0)
    ap.add_argument("--n-max", type=int, default=12000)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()

    if a.paths_file:
        paths = [l.strip() for l in open(a.paths_file) if l.strip()]
    else:
        paths = U.filter_paths(U.scan_network_files(a.roots))
    paths = sorted(paths, key=lambda x: (os.path.getsize(x) if os.path.exists(x) else 0))
    paths = U.shard_list(paths, a.shard_index, a.num_shards)

    rows, done = [], set()
    if a.resume and os.path.exists(a.out):
        prev = pd.read_csv(a.out)
        for _, r in prev.iterrows():
            if str(r.get("status", "")).startswith(("ok", "skipped")):
                rows.append(r.to_dict()); done.add(str(r["path"]))
    os.makedirs(a.spec_dir, exist_ok=True)

    todo = [p for p in paths if str(p) not in done]
    print(f"{len(paths)} networks in shard {a.shard_index}/{a.num_shards} | {len(todo)} to do "
          f"-> {a.out}", flush=True)
    for i, p in enumerate(todo, 1):
        try:
            r = analyze(p, n_max=a.n_max)
        except Exception as e:
            r = dict(path=str(p), status=f"FAIL: {type(e).__name__}: {e}")
            traceback.print_exc()
        mu = r.pop("_mu", None)
        if mu is not None:
            k = min(300, mu.size)
            np.savez_compressed(
                os.path.join(a.spec_dir, os.path.basename(str(p)).rsplit(".", 1)[0] + ".npz"),
                mu_head=mu[:k].astype(np.float32), mu_tail=mu[-k:].astype(np.float32),
                N=r.get("N", 0), mu_abs_sum=r.get("mu_abs_sum", 0.0))
        rows.append(r)
        pd.DataFrame(rows).to_csv(a.out, index=False)
        st = r.get("status", "?")
        print(f"[{i}/{len(todo)}] {os.path.basename(str(p))[:44]:<46} N={r.get('N','?')} "
              f"D2={r.get('D2', float('nan')):.4f} Dneg={r.get('D_neg', float('nan')):.4f} "
              f"{r.get('secs',0)}s {st}", flush=True)
    print(f"done -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
