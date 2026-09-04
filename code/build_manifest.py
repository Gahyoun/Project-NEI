#!/usr/bin/env python3
"""build_manifest.py — 표본 정의를 확정한다.

어떤 수치를 보고하기 전에 '무엇이 표본인가' 가 먼저 정해져야 한다. 현재 파일 목록은
세 가지 문제를 갖고 있다.

  (1) .cleaned.tsv 파생본이 원본과 함께 들어 있다. 일부는 loader 가 실패하고
      일부는 수치 병리를 낸다.
  (2) 같은 network 가 다른 이름으로 두 번 들어 있다. 파일명 기준 중복 제거로는
      잡히지 않는다 — power-US-Grid.mtx 와 inf-power 2.mtx 가 그 예다.
  (3) loader 가 조용히 실패해 N=2 같은 조각을 내놓는다.

그래서 **내용 기준**으로 중복을 제거한다. 두 가지 해시를 쓴다.

  edge_hash : GCC 의 정렬된 edge 목록 해시. label 이 같은 완전 중복을 정확히 잡는다.
  wl_hash   : Weisfeiler-Lehman graph hash. label 이 달라도 같은 구조를 잡는다.
              완전한 isomorphism invariant 는 아니지만 (N,E) 와 함께 쓰면 실용상 안전하다.

대표는 파생본이 아닌 것, 그 다음 경로가 짧은 것을 고른다.
"""
from __future__ import annotations
import hashlib, json, os, sys, traceback

_here = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [_here, os.path.dirname(_here)]
import networkx as nx
import run_nei_unified as U

N_MIN = 20


def edge_hash(G):
    e = sorted(tuple(sorted((str(u), str(v)))) for u, v in G.edges())
    h = hashlib.sha1()
    for u, v in e:
        h.update(u.encode()); h.update(b"\x00"); h.update(v.encode()); h.update(b"\x01")
    return h.hexdigest()[:16]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out/sample_manifest.json"
    paths = U.filter_paths(U.scan_network_files(U.DEFAULT_ROOTS))
    paths = sorted(paths, key=lambda p: (os.path.getsize(p) if os.path.exists(p) else 0))
    recs = []
    for i, p in enumerate(paths, 1):
        r = {"path": str(p), "base": os.path.basename(str(p)),
             "derived": str(p).endswith(".cleaned.tsv")}
        try:
            G_raw, meta = U.load_network(p)
            G = U.get_gcc(G_raw)
            r.update(N=G.number_of_nodes(), E=G.number_of_edges(),
                     weighted=bool(meta.get("weighted")),
                     weight_def=meta.get("weight_definition", ""),
                     rule=meta.get("special_rule", ""),
                     dataset=meta.get("dataset_type", ""))
            if r["N"] < N_MIN:
                r["status"] = f"drop: N={r['N']} < {N_MIN} (loader 실패 의심)"
            else:
                r["status"] = "ok"
                r["edge_hash"] = edge_hash(G)
                try:
                    r["wl_hash"] = nx.weisfeiler_lehman_graph_hash(G, iterations=3)
                except Exception:
                    r["wl_hash"] = None
        except Exception as e:
            r["status"] = f"FAIL: {type(e).__name__}: {str(e)[:90]}"
        recs.append(r)
        print(f"[{i}/{len(paths)}] {r['base'][:52]:<54} {r.get('N','?'):>6} {r['status'][:44]}",
              flush=True)

    ok = [r for r in recs if r["status"] == "ok"]
    # 내용 기준 그룹. wl_hash 가 있으면 (wl,N,E), 없으면 edge_hash 로.
    groups = {}
    for r in ok:
        key = (r["wl_hash"], r["N"], r["E"]) if r.get("wl_hash") else ("eh", r["edge_hash"])
        groups.setdefault(key, []).append(r)
    for g in groups.values():
        g.sort(key=lambda r: (r["derived"], len(r["path"]), r["path"]))
        g[0]["role"] = "representative"
        for d in g[1:]:
            d["role"] = "duplicate"
            d["duplicate_of"] = g[0]["base"]

    reps = [r for r in ok if r.get("role") == "representative"]
    dups = [r for r in ok if r.get("role") == "duplicate"]
    bad = [r for r in recs if r["status"] != "ok"]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump({"n_files": len(recs), "n_representative": len(reps),
               "n_duplicate": len(dups), "n_excluded": len(bad),
               "records": recs}, open(out, "w"), ensure_ascii=False, indent=1)
    with open(os.path.splitext(out)[0] + "_paths.txt", "w") as fh:
        for r in sorted(reps, key=lambda r: r["N"]):
            fh.write(r["path"] + "\n")
    print(f"\n파일 {len(recs)} | 대표 {len(reps)} | 중복 {len(dups)} | 제외 {len(bad)}")
    print(f"-> {out}")
    if dups:
        print("\n중복으로 접힌 것:")
        for d in dups:
            print(f"  {d['base'][:48]:<50} -> {d['duplicate_of'][:44]}")
    if bad:
        print("\n제외:")
        for b in bad:
            print(f"  {b['base'][:48]:<50} {b['status'][:56]}")


if __name__ == "__main__":
    main()
