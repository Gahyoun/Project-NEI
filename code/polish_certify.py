#!/usr/bin/env python3
"""polish_certify.py — landscape 축퇴가 실재하는지, SMACOF 의 수렴 실패인지 가른다.

논증
----
SMACOF 종점은 stationary point 가 아니다. sklearn 의 정지규칙은 상대 stress
개선량이지 optimality gap 이 아니어서, 실측 eta_g 가 L-BFGS 보다 4-5 자릿수 크다.
그 상태의 terminal ensemble 로는 '서로 다른 minimizer 인가, 같은 minimizer 근처에서
멈춘 것인가' 를 구분할 수 없다.

그래서 각 SMACOF terminal 을 L-BFGS 로 **다듬는다(polish)**. eta_g 를 1e-9 아래로
내리면 두 가지가 동시에 해결된다.

  1. 다듬은 점이 진짜 stationary point 인지 projected Hessian 으로 인증할 수 있다.
     E(p) zero mode 를 제거한 뒤 음의 eigenvalue 가 없으면 local minimizer 이다.

  2. 서로 다른 minimizer 사이 거리는 O(1) 인데 같은 minimizer 안의 수치산포는
     O(1e-9) 가 된다. cutoff 를 보정할 필요 없이 K 가 결정된다. 지금까지 K 를
     정하지 못한 것은 landscape 때문이 아니라 수렴을 안 했기 때문이다.

판정
----
  polish 후에도 I 가 살아남고 음의 eigenvalue 가 없으면  -> landscape 축퇴 (물리)
  polish 후 I 가 무너지면                                -> SMACOF 수렴 실패 (인공물)
"""
from __future__ import annotations

import sys
import numpy as np
import networkx as nx
from scipy.optimize import minimize
from sklearn.manifold import smacof


# ---------------------------------------------------------------- 입력
def load(path):
    G = nx.Graph()
    for ln in open(path):
        ln = ln.strip()
        if not ln or ln[0] in "%#":
            continue
        q = ln.replace(",", " ").split()
        if len(q) < 2:
            continue
        try:
            a, b = int(float(q[0])), int(float(q[1]))
        except ValueError:
            continue
        if a != b:
            G.add_edge(a, b)
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    n = G.number_of_nodes()
    ix = {v: i for i, v in enumerate(G)}
    D = np.zeros((n, n))
    for s, dd in nx.all_pairs_shortest_path_length(G):
        for t, l in dd.items():
            D[ix[s], ix[t]] = l
    return D, n, G.number_of_edges()


# ---------------------------------------------------------------- stress
def _dist(X):
    d = X[:, None, :] - X[None, :, :]
    return np.sqrt((d ** 2).sum(-1)), d


def fg(x, Delta, n, p):
    X = x.reshape(n, p)
    d, diff = _dist(X)
    np.fill_diagonal(d, 1.0)
    r = d - Delta
    np.fill_diagonal(r, 0.0)
    F = 0.5 * (r ** 2).sum()
    w = r / d
    np.fill_diagonal(w, 0.0)
    return F, ((w[:, :, None] * diff).sum(1)).ravel()


# ---------------------------------------------------------------- Hessian
def rigid_basis(X):
    """E(p) zero mode: translation p 개 + rotation p(p-1)/2 개. 정규직교화해 반환."""
    n, p = X.shape
    cols = []
    for a in range(p):
        T = np.zeros((n, p)); T[:, a] = 1.0
        cols.append(T.ravel())
    Xc = X - X.mean(0)
    for a in range(p):
        for b in range(a + 1, p):
            R = np.zeros((n, p))
            R[:, a] = -Xc[:, b]; R[:, b] = Xc[:, a]
            cols.append(R.ravel())
    B = np.column_stack(cols)
    Q, _ = np.linalg.qr(B)
    return Q


def hessian(X, Delta):
    """stress 의 좌표 Hessian. B_ij = u u^T + (1 - delta/d)(I - u u^T)."""
    n, p = X.shape
    d, diff = _dist(X)
    np.fill_diagonal(d, np.inf)
    H = np.zeros((n * p, n * p))
    I = np.eye(p)
    for i in range(n):
        for j in range(i + 1, n):
            dij = d[i, j]
            u = diff[i, j] / dij
            B = np.outer(u, u) + (1.0 - Delta[i, j] / dij) * (I - np.outer(u, u))
            si, sj = i * p, j * p
            H[si:si + p, si:si + p] += B
            H[sj:sj + p, sj:sj + p] += B
            H[si:si + p, sj:sj + p] -= B
            H[sj:sj + p, si:si + p] -= B
    return H


def projected_spectrum(X, Delta, k=12):
    """E(p) zero mode 를 제거한 Hessian 의 하단 eigenvalue 와 positive scale."""
    n, p = X.shape
    H = hessian(X, Delta)
    Q = rigid_basis(X)
    P = np.eye(n * p) - Q @ Q.T
    Hp = P @ H @ P
    w = np.linalg.eigvalsh(0.5 * (Hp + Hp.T))
    q = Q.shape[1]
    w = w[q:]                                   # 제거한 zero mode 개수만큼 버린다
    pos = w[w > 0]
    kappa = pos.sum() / max(w.size, 1)
    return w[:k], float(kappa)


def dmat(X):
    d = X[:, None, :] - X[None, :, :]
    return np.sqrt((d ** 2).sum(-1))


def nei(Ds):
    A = np.stack(Ds); iu = np.triu_indices(A.shape[1], 1)
    Pm = A[:, iu[0], iu[1]]; mu = Pm.mean(0); ok = mu > 0
    return float((Pm.var(0)[ok] / mu[ok] ** 2).mean())


def main():
    path = sys.argv[1]
    M = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    p = 2
    Delta, n, E = load(path)
    sq = np.sqrt((Delta[np.triu_indices(n, 1)] ** 2).sum())
    rng = np.random.default_rng(42)
    print(f"\n### {path.split('/')[-1]}  N={n} E={E} M={M}", flush=True)

    raw, pol, eta_r, eta_p, dF, coords = [], [], [], [], [], []
    for m in range(M):
        x0 = rng.random((n, p))
        Y, _ = smacof(Delta, n_components=p, init=x0.copy(), n_init=1,
                      max_iter=300, eps=1e-10, random_state=0, normalized_stress=False)
        F0, g0 = fg(Y.ravel(), Delta, n, p)
        raw.append(dmat(Y)); eta_r.append(np.linalg.norm(g0) / sq)
        r = minimize(fg, Y.ravel(), args=(Delta, n, p), jac=True, method="L-BFGS-B",
                     options=dict(maxiter=50000, ftol=1e-18, gtol=1e-14))
        Z = r.x.reshape(n, p)
        F1, g1 = fg(r.x, Delta, n, p)
        pol.append(dmat(Z)); coords.append(Z); eta_p.append(np.linalg.norm(g1) / sq)
        dF.append((F0 - F1) / max(F0, 1e-300))

    print(f"  eta_g   SMACOF {np.median(eta_r):.2e}  ->  polish {np.median(eta_p):.2e}"
          f"   ({np.median(eta_r)/max(np.median(eta_p),1e-300):.0e} 배 개선)")
    print(f"  stress 가 polish 로 더 내려간 비율(중앙) {np.median(dF):.3e}")
    I0, I1 = nei(raw), nei(pol)
    print(f"  I  SMACOF {I0:.4e}  ->  polish {I1:.4e}   (비 {I1/max(I0,1e-300):.3f})")

    # ── minimizer 인증: E(p) zero mode 를 뺀 뒤 음의 eigenvalue 를 센다
    nsub = min(M, 8)
    print(f"  projected Hessian 인증 ({nsub}개 표본):")
    negs, ratios = [], []
    for m in range(nsub):
        Z = coords[m]
        w, kap = projected_spectrum(Z, Delta, k=12)
        nneg = int((w < -1e-9 * max(kap, 1e-300)).sum())
        negs.append(nneg); ratios.append(w[0] / max(kap, 1e-300))
        print(f"    run {m:2d}  lam_min/kappa+ = {w[0]/max(kap,1e-300):+.3e}"
              f"   음의 eigenvalue {nneg}개")
    print(f"    -> saddle 후보 {sum(1 for x in negs if x>0)}/{nsub},"
          f"  lam_min/kappa+ 중앙 {np.median(ratios):+.3e}")

    # ── K 결정: polish 후에는 cutoff 가 필요 없다
    A = np.stack(pol); iu = np.triu_indices(n, 1)
    V = A[:, iu[0], iu[1]]
    G = np.linalg.norm(V[:, None, :] - V[None, :, :], axis=2)
    scale = np.linalg.norm(V, axis=1).mean()
    Gn = G / max(scale, 1e-300)
    off = Gn[np.triu_indices(M, 1)]
    print(f"  polish 후 run 간 상대거리:  최소 {off.min():.3e}  중앙 {np.median(off):.3e}"
          f"  최대 {off.max():.3e}")
    for tau in (1e-8, 1e-6, 1e-4, 1e-3, 1e-2):
        lab = -np.ones(M, int); c = 0
        for i in range(M):
            if lab[i] >= 0:
                continue
            stack = [i]; lab[i] = c
            while stack:
                a = stack.pop()
                for b in range(M):
                    if lab[b] < 0 and Gn[a, b] <= tau:
                        lab[b] = c; stack.append(b)
            c += 1
        print(f"    cutoff {tau:.0e} -> K = {c}")


if __name__ == "__main__":
    main()
