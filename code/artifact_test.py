#!/usr/bin/env python3
"""artifact_test.py — NEI 신호가 SMACOF 의 인공물인지 판정한다.

물어야 할 것은 두 가지이고 서로 다르다.

  (A) cMDS 는 초기조건이 없다.
      닫힌 형태(이중중심화 -> 고유분해)이므로 D 가 유일하고 I = 0 은 정리이다.
      여기서는 수치로 확인만 한다.

  (B) SMACOF 의 종점 분산이 landscape 때문인가, 수렴 실패 때문인가.
      결정적 시험은 '같은 X0 에서 다른 최적화기'이다. 전혀 다른 알고리즘이
      같은 X0 에서 같은 종점에 도달하면 그 종점은 landscape 의 성질이지
      최적화기의 성질이 아니다. 갈라지면 적어도 하나가 수렴하지 못한 것이다.

비교하는 네 경로
  cmds        결정론적 닫힌 형태
  smacof300   현재 논문 설정 (max_iter=300)
  smacof10k   거의 소진시킨 설정 (max_iter=10000, eps 1e-12)
  lbfgs       stress 를 직접 L-BFGS 로 최소화 (해석적 gradient)

보고하는 것
  I           쌍별 상대분산의 평균
  eta_g       ||g||/sqrt(S_Delta)   무차원 정류성 지표
  agree       같은 X0 에서 smacof 종점과 lbfgs 종점의 거리행렬 상대차
"""
from __future__ import annotations

import sys
import numpy as np
import networkx as nx
from scipy.optimize import minimize
from sklearn.manifold import smacof


# ---------------------------------------------------------------- 그래프
def load(path):
    G = nx.Graph()
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln[0] in "%#":
                continue
            p = ln.replace(",", " ").split()
            if len(p) < 2:
                continue
            try:
                a, b = int(float(p[0])), int(float(p[1]))
            except ValueError:
                continue
            if a != b:
                G.add_edge(a, b)
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    n = G.number_of_nodes()
    idx = {v: i for i, v in enumerate(G)}
    D = np.zeros((n, n))
    for s, dd in nx.all_pairs_shortest_path_length(G):
        for t, l in dd.items():
            D[idx[s], idx[t]] = l
    return D, n, G.number_of_edges()


# ---------------------------------------------------------------- stress
def stress_and_grad(x, Delta, n, p):
    X = x.reshape(n, p)
    diff = X[:, None, :] - X[None, :, :]
    d = np.sqrt((diff ** 2).sum(-1))
    np.fill_diagonal(d, 1.0)
    r = d - Delta
    np.fill_diagonal(r, 0.0)
    F = 0.5 * (r ** 2).sum()                    # i<j 합 = 전체합/2
    w = r / d
    np.fill_diagonal(w, 0.0)
    g = (w[:, :, None] * diff).sum(1) * 2.0
    return F, g.ravel() * 0.5                    # 0.5 는 F 의 계수와 일관


def grad_norm(X, Delta):
    n, p = X.shape
    _, g = stress_and_grad(X.ravel(), Delta, n, p)
    return float(np.linalg.norm(g))


# ---------------------------------------------------------------- cMDS
def cmds(Delta, p):
    n = Delta.shape[0]
    D2 = Delta ** 2
    rm = D2.mean(1, keepdims=True)
    G = -0.5 * (D2 - rm - rm.T + D2.mean())
    w, V = np.linalg.eigh(0.5 * (G + G.T))
    o = np.argsort(w)[::-1][:p]
    return V[:, o] * np.sqrt(np.maximum(w[o], 0.0))


# ---------------------------------------------------------------- NEI
def dmat(X):
    d = X[:, None, :] - X[None, :, :]
    return np.sqrt((d ** 2).sum(-1))


def nei(Ds):
    A = np.stack(Ds)                              # (M,n,n)
    iu = np.triu_indices(A.shape[1], 1)
    P = A[:, iu[0], iu[1]]                        # (M, npair)
    mu = P.mean(0)
    ok = mu > 0
    return float((P.var(0)[ok] / mu[ok] ** 2).mean())


def main():
    p = 2
    M = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    Delta, n, E = load(sys.argv[1])
    S = (Delta[np.triu_indices(n, 1)] ** 2).sum()
    sq = np.sqrt(S)
    rng = np.random.default_rng(42)
    X0 = [rng.random((n, p)) for _ in range(M)]
    name = sys.argv[1].split("/")[-1]
    print(f"\n### {name}   N={n} E={E} M={M}")

    # (A) cMDS
    Dc = dmat(cmds(Delta, p))
    print(f"  cMDS       I = {nei([Dc, Dc, Dc]):.3e}   (초기조건 없음; 정리상 정확히 0)")

    res = {}
    for tag, mi, eps in [("smacof300", 300, 1e-10), ("smacof10k", 10000, 1e-12)]:
        Ds, gs, hit = [], [], 0
        for x0 in X0:
            Y, _, ni = smacof(Delta, n_components=p, init=x0.copy(), n_init=1,
                              max_iter=mi, eps=eps, random_state=0,
                              normalized_stress=False, return_n_iter=True)
            Ds.append(dmat(Y)); gs.append(grad_norm(Y, Delta) / sq); hit += (ni >= mi)
        res[tag] = Ds
        print(f"  {tag:<10} I = {nei(Ds):.3e}   eta_g 중앙 {np.median(gs):.2e}"
              f"   cap 소진 {hit}/{M}")

    Ds, gs = [], []
    for x0 in X0:
        r = minimize(stress_and_grad, x0.ravel(), args=(Delta, n, p), jac=True,
                     method="L-BFGS-B", options=dict(maxiter=20000, ftol=1e-16, gtol=1e-12))
        Y = r.x.reshape(n, p)
        Ds.append(dmat(Y)); gs.append(grad_norm(Y, Delta) / sq)
    res["lbfgs"] = Ds
    print(f"  {'lbfgs':<10} I = {nei(Ds):.3e}   eta_g 중앙 {np.median(gs):.2e}")

    # (B) 같은 X0 에서 최적화기 간 종점 일치
    for a, b in [("smacof300", "lbfgs"), ("smacof10k", "lbfgs"),
                 ("smacof300", "smacof10k")]:
        rel = [np.linalg.norm(res[a][k] - res[b][k]) /
               max(np.linalg.norm(res[b][k]), 1e-300) for k in range(M)]
        rel = np.array(rel)
        print(f"  일치 {a:<10} vs {b:<10} 상대차 중앙 {np.median(rel):.3e}"
              f"  |  <1e-3 인 run {int((rel < 1e-3).sum())}/{M}")


if __name__ == "__main__":
    main()
