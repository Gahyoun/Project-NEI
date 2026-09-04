#!/usr/bin/env python3
"""polish_certify.py — terminal 산포가 수렴 실패만으로 생겼는지 검사한다.

논증
----
SMACOF 종점은 stationary point 가 아니다. sklearn 의 정지규칙은 상대 stress
개선량이지 optimality gap 이 아니어서, 실측 eta_g 가 L-BFGS 보다 4-5 자릿수 크다.
그 상태의 terminal ensemble 로는 '서로 다른 minimizer 인가, 같은 minimizer 근처에서
멈춘 것인가' 를 구분할 수 없다.

그래서 각 SMACOF terminal 을 L-BFGS 로 **다듬는다(polish)**. eta_g 를 1e-9 아래로
내리면 두 가지가 동시에 해결된다.

  1. 다듬은 점의 stationarity 와 quotient Hessian 을 검사할 수 있다. E(p) orbit의
     tangent space 자체를 버리는 대신 그 직교여공간에서 Hessian 을 대각화한다.
     분해능 아래 음의 곡률이 없다는 것은 second-order local-minimum candidate라는
     뜻이지, strict minimum 또는 연속 minimizer 부재의 증명은 아니다.

  2. polishing 전후의 terminal separation을 비교하면 early-stopping scatter의 기여를
     진단할 수 있다. 다만 K는 여전히 finite-M, clustering resolution과 independent-
     batch recurrence에 조건부이므로 polishing만으로 state count가 결정되지는 않는다.

판정
----
  polish 후에도 I가 남고 declared gate를 통과하면 -> realized terminal multiplicity 후보
  polish 후 I가 무너지면                         -> SMACOF 수렴오차 기여가 큼

주의
----
서로 다른 local minima는 일반적으로 서로 다른 stress 값을 가질 수 있다. 따라서 이
검사만으로 energetic degeneracy(동일 energy)를 주장할 수 없다. 또한 Hessian의 추가
영모드는 infinitesimal softness를 뜻할 뿐, 실제 minimizer continuum은 continuation
또는 Morse--Bott 조건을 별도로 확인해야 한다.
"""
from __future__ import annotations

import argparse
from pathlib import Path
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
    off = ~np.eye(n, dtype=bool)
    if np.any(d[off] <= np.finfo(float).eps):
        raise FloatingPointError("off-diagonal collision: stress is not differentiable")
    w = r / d
    np.fill_diagonal(w, 0.0)
    # F = sum_{i<j} (d_ij-Delta_ij)^2, hence the factor 2.
    return F, (2.0 * (w[:, :, None] * diff).sum(1)).ravel()


# ---------------------------------------------------------------- Hessian
def rigid_basis(X):
    """현재 배치에서 실제로 독립인 E(p)-orbit tangent의 정규직교기저.

    rank-deficient 또는 대칭적인 배치에서는 형식적인 p+p(p-1)/2개 생성벡터가
    선형독립이 아닐 수 있으므로 SVD로 수치 rank를 판정한다.
    """
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
    U, s, _ = np.linalg.svd(B, full_matrices=False)
    tol = max(B.shape) * np.finfo(float).eps * max(float(s[0]), 1.0)
    rank = int(np.sum(s > tol))
    return U[:, :rank]


def hessian(X, Delta):
    """F=sum_{i<j}(d_ij-Delta_ij)^2의 정확한 좌표 Hessian."""
    n, p = X.shape
    d, diff = _dist(X)
    np.fill_diagonal(d, np.inf)
    H = np.zeros((n * p, n * p))
    I = np.eye(p)
    for i in range(n):
        for j in range(i + 1, n):
            dij = d[i, j]
            if dij <= np.finfo(float).eps:
                raise FloatingPointError(
                    "off-diagonal collision: coordinate Hessian is undefined"
                )
            u = diff[i, j] / dij
            B = 2.0 * (
                np.outer(u, u)
                + (1.0 - Delta[i, j] / dij) * (I - np.outer(u, u))
            )
            si, sj = i * p, j * p
            H[si:si + p, si:si + p] += B
            H[sj:sj + p, sj:sj + p] += B
            H[si:si + p, sj:sj + p] -= B
            H[sj:sj + p, si:si + p] -= B
    return H


def projected_spectrum(X, Delta, k=12):
    """E(p)-orbit의 직교여공간에서 Hessian spectrum을 직접 계산한다."""
    n, p = X.shape
    H = hessian(X, Delta)
    Q = rigid_basis(X)
    if Q.shape[1] == 0:
        Qperp = np.eye(n * p)
    else:
        Qfull, _ = np.linalg.qr(Q, mode="complete")
        Qperp = Qfull[:, Q.shape[1]:]
    Hperp = Qperp.T @ H @ Qperp
    w = np.linalg.eigvalsh(0.5 * (Hperp + Hperp.T))
    # 방법 노트의 정의: positive spectral mass를 quotient dimension으로 나눈 scale.
    kappa = np.maximum(w, 0.0).sum() / w.size if w.size else 0.0
    return (w if k is None else w[:k]), float(kappa), int(Q.shape[1])


def dmat(X):
    d = X[:, None, :] - X[None, :, :]
    return np.sqrt((d ** 2).sum(-1))


def nei(Ds):
    A = np.stack(Ds); iu = np.triu_indices(A.shape[1], 1)
    Pm = A[:, iu[0], iu[1]]; mu = Pm.mean(0)
    if Pm.shape[0] < 2:
        raise ValueError("NEI requires at least two terminal configurations")
    if np.any(~np.isfinite(mu)) or np.any(mu <= 0):
        raise ValueError(
            "NEI is undefined when any empirical mean pair distance is nonpositive"
        )
    return float((Pm.var(0, ddof=0) / mu ** 2).mean())


def main():
    parser = argparse.ArgumentParser(
        description="Polish every SMACOF terminal and certify it on the E(p) quotient."
    )
    parser.add_argument("path", help="unweighted edge-list input")
    parser.add_argument("M", nargs="?", type=int, default=24,
                        help="number of independent restarts (default: 24)")
    parser.add_argument(
        "--hessian-limit", type=int, default=None,
        help="explicit exploratory cap; omission certifies all M terminals",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="compressed artifact path (default: ./<network>.polish_certify.npz)",
    )
    parser.add_argument("--tau-g", type=float, default=1e-9,
                        help="dimensionless stationarity threshold (default: 1e-9)")
    parser.add_argument(
        "--tau-h-rel", type=float, default=1e-9,
        help="relative quotient-Hessian eigenvalue threshold (default: 1e-9)",
    )
    parser.add_argument(
        "--tau-c", type=float, default=1e-8,
        help="dimensionless collision margin threshold (default: 1e-8)",
    )
    parser.add_argument("--no-save", action="store_true",
                        help="print diagnostics without writing an artifact")
    args = parser.parse_args()
    if args.M < 2:
        parser.error("M must be at least 2")
    if args.hessian_limit is not None and args.hessian_limit < 1:
        parser.error("--hessian-limit must be positive")
    if args.tau_g <= 0 or args.tau_h_rel <= 0 or args.tau_c <= 0:
        parser.error("all gate thresholds must be positive")

    path = args.path
    M = args.M
    p = 2
    Delta, n, E = load(path)
    target_pairs = Delta[np.triu_indices(n, 1)]
    S_delta = float((target_pairs ** 2).sum())
    if target_pairs.size == 0 or not np.isfinite(S_delta) or S_delta <= 0:
        parser.error("the target dissimilarity must contain at least one positive pair")
    s_delta = np.sqrt(S_delta / target_pairs.size)
    sq = np.sqrt(S_delta)
    rng = np.random.default_rng(42)
    print(f"\n### {path.split('/')[-1]}  N={n} E={E} M={M}", flush=True)

    raw, pol, raw_coords, coords = [], [], [], []
    eta_r, eta_p, dF, opt_ok = [], [], [], []
    stress_r, stress_p, min_d_r, min_d_p = [], [], [], []
    pair_index = np.triu_indices(n, 1)
    for m in range(M):
        x0 = rng.random((n, p))
        Y, _ = smacof(Delta, n_components=p, init=x0.copy(), n_init=1,
                      max_iter=300, eps=1e-10, random_state=0, normalized_stress=False)
        F0, g0 = fg(Y.ravel(), Delta, n, p)
        D0 = dmat(Y)
        raw.append(D0); raw_coords.append(Y)
        eta_r.append(np.linalg.norm(g0) / sq); stress_r.append(F0)
        min_d_r.append(float(D0[pair_index].min()))
        r = minimize(fg, Y.ravel(), args=(Delta, n, p), jac=True, method="L-BFGS-B",
                     options=dict(maxiter=50000, ftol=1e-18, gtol=1e-14))
        Z = r.x.reshape(n, p)
        F1, g1 = fg(r.x, Delta, n, p)
        D1 = dmat(Z)
        pol.append(D1); coords.append(Z); eta_p.append(np.linalg.norm(g1) / sq)
        stress_p.append(F1); min_d_p.append(float(D1[pair_index].min()))
        dF.append((F0 - F1) / max(F0, 1e-300))
        opt_ok.append(bool(r.success))

    print(f"  eta_g   SMACOF {np.median(eta_r):.2e}  ->  polish {np.median(eta_p):.2e}"
          f"   ({np.median(eta_r)/max(np.median(eta_p),1e-300):.0e} 배 개선)")
    print(f"  stress 가 polish 로 더 내려간 비율(중앙) {np.median(dF):.3e}")
    print(f"  L-BFGS 종료 success {sum(opt_ok)}/{M}")
    I0, I1 = nei(raw), nei(pol)
    print(f"  I (all-run ungated diagnostic)  SMACOF {I0:.4e}  ->  polish {I1:.4e}"
          f"   (비 {I1/max(I0,1e-300):.3f})")

    eta_p_arr = np.asarray(eta_p)
    stress_p_arr = np.asarray(stress_p)
    min_d_r_arr = np.asarray(min_d_r)
    min_d_p_arr = np.asarray(min_d_p)
    chi_coll_r = min_d_r_arr / s_delta
    chi_coll_p = min_d_p_arr / s_delta

    # ── minimizer 인증: 기본값은 모든 terminal이다. 명시적인 cap은 exploratory
    #    실행에만 허용하고 artifact에 coverage를 함께 기록한다.
    nsub = M if args.hessian_limit is None else min(M, args.hessian_limit)
    coverage = "all terminals" if nsub == M else "exploratory subset"
    print(f"  projected Hessian 인증 ({nsub}/{M}, {coverage}):")
    hessian_tested = np.zeros(M, dtype=bool)
    inertia = np.full((M, 3), -1, dtype=int)
    ratios = np.full(M, np.nan)
    kappas = np.full(M, np.nan)
    lambda_min = np.full(M, np.nan)
    gauge_ranks = np.full(M, -1, dtype=int)
    for m in range(nsub):
        if not np.isfinite(chi_coll_p[m]) or chi_coll_p[m] < args.tau_c:
            print(f"    run {m:2d}  Hessian 보류: chi_coll={chi_coll_p[m]:.3e}"
                  f" < tau_c={args.tau_c:.1e}")
            continue
        Z = coords[m]
        w, kap, q = projected_spectrum(Z, Delta, k=None)
        tol = args.tau_h_rel * max(kap, 1e-300)
        nneg = int((w < -tol).sum())
        nzero = int((np.abs(w) <= tol).sum())
        npos = int((w > tol).sum())
        hessian_tested[m] = True
        inertia[m] = (nneg, nzero, npos)
        lambda_min[m] = w[0]
        ratios[m] = w[0] / max(kap, 1e-300)
        kappas[m] = kap
        gauge_ranks[m] = q
        print(f"    run {m:2d}  lam_min/kappa+ = {w[0]/max(kap,1e-300):+.3e}"
              f"   inertia=({nneg},{nzero},{npos})  gauge-rank={q}")
    tested_ratios = ratios[hessian_tested]
    tested_negs = inertia[hessian_tested, 0]
    if hessian_tested.any():
        print(f"    -> saddle 후보 {(tested_negs > 0).sum()}/{hessian_tested.sum()},"
              f"  lam_min/kappa+ 중앙 {np.median(tested_ratios):+.3e}")
    else:
        print("    -> collision gate를 통과해 Hessian을 계산한 terminal이 없음")

    finite = np.isfinite(eta_p_arr) & np.isfinite(stress_p_arr) & np.isfinite(min_d_p_arr)
    admissible = (
        np.asarray(opt_ok, dtype=bool)
        & finite
        & (eta_p_arr <= args.tau_g)
        & (chi_coll_p >= args.tau_c)
        & hessian_tested
        & (inertia[:, 0] == 0)
    )
    coverage_complete = bool(hessian_tested.all())
    all_terminal_gate = bool(coverage_complete and admissible.all())
    I1_certified = I1 if all_terminal_gate else np.nan
    n_adm = int(admissible.sum())
    I1_admissible = nei([pol[m] for m in np.flatnonzero(admissible)]) if n_adm >= 2 else np.nan
    print(f"  admissibility gate {admissible.sum()}/{M}: success, eta_g<={args.tau_g:.1e},"
          f" chi_coll>={args.tau_c:.1e}, n_-=0")
    print("  conditional admissible-sample I = "
          + (f"{I1_admissible:.4e}" if np.isfinite(I1_admissible) else "보류 (M_adm<2)"))
    print("  certified I = " + (f"{I1_certified:.4e}" if all_terminal_gate else "보류"))

    # ── 관측 표본에서의 terminal separation. 이것만으로 basin/energy degeneracy를
    #    인증하지는 않는다; independent-batch recurrence와 energy 비교가 별도로 필요하다.
    A = np.stack(pol); iu = np.triu_indices(n, 1)
    V = A[:, iu[0], iu[1]]
    G = np.linalg.norm(V[:, None, :] - V[None, :, :], axis=2)
    # Dimensionless metric declared in the architecture, with W=1 here:
    # rho_D(d,d') = ||d-d'||_2 / sqrt(S_delta).
    Gn = G / sq
    off = Gn[np.triu_indices(M, 1)]
    print(f"  polish 후 run 간 상대거리 (all-run ungated):  최소 {off.min():.3e}  중앙 {np.median(off):.3e}"
          f"  최대 {off.max():.3e}")
    cutoffs = np.asarray((1e-8, 1e-6, 1e-4, 1e-3, 1e-2))
    K_all = []
    for tau in cutoffs:
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
        K_all.append(c)
        label = "certified" if all_terminal_gate else "all-run ungated"
        print(f"    cutoff {tau:.0e} -> K = {c} ({label})")
    K_all = np.asarray(K_all)
    K_certified = K_all.copy() if all_terminal_gate else np.full(K_all.shape, -1)

    # Coordinates are the compact source of truth: full pair-distance matrices
    # and pair-standardized z vectors can be reconstructed deterministically
    # without duplicating O(MN^2) storage.  Raw S_delta and per-run collision
    # margins are persisted explicitly because they cannot be inferred from a
    # legacy aggregate-only artifact.
    if not args.no_save:
        out = args.output or Path.cwd() / f"{Path(path).stem}.polish_certify.npz"
        np.savez_compressed(
            out,
            source_path=np.asarray(str(Path(path).resolve())),
            target_dimension=np.asarray(p),
            Delta=Delta,
            S_delta=np.asarray(S_delta),
            s_delta=np.asarray(s_delta),
            X_raw=np.stack(raw_coords),
            X_polished=np.stack(coords),
            stress_raw=np.asarray(stress_r),
            stress_polished=np.asarray(stress_p),
            normalized_stress_raw=np.asarray(stress_r) / S_delta,
            normalized_stress_polished=np.asarray(stress_p) / S_delta,
            eta_g_raw=np.asarray(eta_r),
            eta_g_polished=eta_p_arr,
            min_pair_distance_raw=min_d_r_arr,
            min_pair_distance_polished=min_d_p_arr,
            chi_coll_raw=chi_coll_r,
            chi_coll_polished=chi_coll_p,
            optimizer_success=np.asarray(opt_ok, dtype=bool),
            tau_g=np.asarray(args.tau_g),
            tau_h_rel=np.asarray(args.tau_h_rel),
            tau_c=np.asarray(args.tau_c),
            hessian_tested=hessian_tested,
            hessian_run_index=np.flatnonzero(hessian_tested),
            hessian_inertia=inertia,
            hessian_lambda_min=lambda_min,
            hessian_lambda_min_over_kappa=ratios,
            hessian_kappa_plus=kappas,
            gauge_rank=gauge_ranks,
            coverage_complete=np.asarray(coverage_complete),
            hessian_all_terminals=np.asarray(coverage_complete),
            admissible=admissible,
            acceptance_rate=np.asarray(n_adm / M),
            all_terminal_gate=np.asarray(all_terminal_gate),
            nei_smacof_all_ungated=np.asarray(I0),
            nei_polished_all_ungated=np.asarray(I1),
            nei_polished_admissible=np.asarray(I1_admissible),
            nei_polished_certified=np.asarray(I1_certified),
            cluster_cutoffs=cutoffs,
            K_all_ungated=K_all,
            K_certified=K_certified,
        )
        print(f"  artifact 저장: {out}")


if __name__ == "__main__":
    main()
