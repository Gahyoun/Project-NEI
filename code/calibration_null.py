"""Protocol-specific calibration controls, not a universal numerical error bound.
Exact representability does not certify global convergence of nonconvex MDS.
Reported NEI uses all pairs; terminal-level admissibility is a separate test.
Ihat_M = tr(B_z)/M, z_ma = d_a/(dbar_a sqrt(N+)).
"""
import argparse
import numpy as np, networkx as nx
from sklearn.manifold import smacof
from scipy.optimize import minimize

IMPLEMENTATION = "calibration-null/corrected-gradient-v1"


def spd(G):
    G=G.subgraph(max(nx.connected_components(G),key=len)).copy()
    n=G.number_of_nodes(); ix={v:i for i,v in enumerate(G)}
    D=np.zeros((n,n))
    for s,dd in nx.all_pairs_shortest_path_length(G):
        for t,l in dd.items(): D[ix[s],ix[t]]=l
    return D,n

def Dp(Delta,p=2):
    D2=Delta**2; rm=D2.mean(1,keepdims=True)
    B=-0.5*(D2-rm-rm.T+D2.mean()); B=0.5*(B+B.T)
    mu=np.linalg.eigvalsh(B)[::-1]; tot=np.abs(mu).sum()
    if tot == 0:
        return 0.0
    return float((np.maximum(mu[p:],0).sum()+np.maximum(-mu,0).sum())/tot)

def fg(x,Delta,n,p):
    X=x.reshape(n,p); df=X[:,None,:]-X[None,:,:]
    d=np.sqrt((df**2).sum(-1))
    iu=np.triu_indices(n,1)
    if np.any(d[iu] == 0.0):
        count=int(np.count_nonzero(d[iu] == 0.0))
        raise FloatingPointError(
            f"raw-stress gradient is undefined at {count} off-diagonal "
            "exact collision(s)"
        )
    np.fill_diagonal(d,1.0)
    r=d-Delta; np.fill_diagonal(r,0.0)
    w=r/d; np.fill_diagonal(w,0.0)
    # F = 1/2 sum_{i,j} r_ij^2 = sum_{i<j} r_ij^2, hence the factor 2.
    return float((r**2).sum()/2.0), (2.0*(w[:,:,None]*df).sum(1)).ravel()


def gradient_check(seed=1729,n=7,p=2,n_directions=8,tol=5e-7):
    """Central-difference directional check for the supplied raw-stress gradient."""
    Delta,_=spd(nx.path_graph(n))
    rng=np.random.default_rng(seed)
    x=rng.normal(size=(n,p)).ravel()
    _,g=fg(x,Delta,n,p)
    h=np.cbrt(np.finfo(float).eps)*(1.0+np.linalg.norm(x))
    errors=[]
    for _ in range(n_directions):
        direction=rng.normal(size=x.size)
        direction/=np.linalg.norm(direction)
        fp=fg(x+h*direction,Delta,n,p)[0]
        fm=fg(x-h*direction,Delta,n,p)[0]
        finite_difference=(fp-fm)/(2.0*h)
        analytic=float(g@direction)
        errors.append(
            abs(finite_difference-analytic)/
            max(1.0,abs(finite_difference),abs(analytic))
        )
    max_error=float(max(errors))
    if not np.isfinite(max_error) or max_error > tol:
        raise AssertionError(
            f"gradient check failed: max relative directional error "
            f"{max_error:.3e} > {tol:.3e}"
        )
    return max_error

def nei_std(Ds):
    """쌍별 표준화 NEI. Ds 는 거리행렬 리스트."""
    A=np.stack(Ds); iu=np.triu_indices(A.shape[1],1)
    P=A[:,iu[0],iu[1]]                      # (M, N+)
    if P.shape[1] == 0:
        raise ValueError(
            "NEI undefined under the primary all-pairs policy: "
            "at least one off-diagonal pair is required"
        )
    if not np.all(np.isfinite(P)):
        raise ValueError("NEI undefined: terminal pair distances must all be finite")
    dbar=P.mean(0)
    bad=np.flatnonzero(~(dbar>0))
    if bad.size:
        raise ValueError(
            "NEI undefined under the primary all-pairs policy: "
            f"{bad.size}/{dbar.size} empirical pair means are nonpositive"
        )
    return float((P.var(0)/dbar**2).mean())

def run(name,G,M=24,p=2,polish=True):
    Delta,n=spd(G); rng=np.random.default_rng(11)
    raw,pol=[],[]
    for m in range(M):
        x0=rng.random((n,p))
        Y,_=smacof(Delta,n_components=p,init=x0.copy(),n_init=1,max_iter=3000,
                   eps=1e-12,random_state=0,normalized_stress=False)
        dm=lambda X:np.sqrt(((X[:,None,:]-X[None,:,:])**2).sum(-1))
        raw.append(dm(Y))
        if polish:
            r=minimize(fg,Y.ravel(),args=(Delta,n,p),jac=True,method="L-BFGS-B",
                       options=dict(maxiter=40000,ftol=1e-18,gtol=1e-14))
            pol.append(dm(r.x.reshape(n,p)))
    print(f"  {name:<22} N={n:4d}  D_2={Dp(Delta):.4f}   "
          f"I_smacof={nei_std(raw):.3e}   I_polish={nei_std(pol) if polish else float('nan'):.3e}")


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gradient-check-only",
        action="store_true",
        help="validate the analytic gradient and skip all calibration runs",
    )
    args=parser.parse_args(argv)

    max_error=gradient_check()
    print(f"implementation: {IMPLEMENTATION}")
    print(
        "derivative provenance: F=sum_{i<j}(d_ij-Delta_ij)^2, "
        f"gradient=2*sum_j[(d_ij-Delta_ij)/d_ij](x_i-x_j), "
        f"central-difference check=PASS (max relative error {max_error:.3e})"
    )
    if args.gradient_check_only:
        return

    print("\n쌍별 표준화 NEI (Ihat = mean_a Var/dbar^2), M=24, p=2\n")
    run("경로 P_60",        nx.path_graph(60))
    run("경로 P_120",       nx.path_graph(120))
    run("격자 8x8",         nx.grid_2d_graph(8,8))
    run("격자 12x12",       nx.grid_2d_graph(12,12))
    run("링 C_60",          nx.cycle_graph(60))
    run("ER n=120 p=.05",   nx.gnp_random_graph(120,0.05,seed=3))
    run("BA n=120 m=2",     nx.barabasi_albert_graph(120,2,seed=3))


if __name__ == "__main__":
    main()
