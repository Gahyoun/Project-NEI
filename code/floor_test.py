"""floor_test.py — 17자릿수 대비가 물리적 분리인가 numerical floor 인가.

결정적 시험: optimizer 의 허용오차를 사다리로 낮추며 Ihat 이 따라 내려가는지 본다.

  floor 라면  Ihat 이 허용오차를 따라 내려간다 (신호가 없고 잔여물만 재고 있다)
  신호라면    Ihat 이 허용오차와 무관하게 머문다

같은 초기조건 집합의 paired comparison. Finite-M uncertainty를 제거하지는 않음.
Printed NEI is an ungated diagnostic; full admissibility requires separate checks.
"""
import argparse
from collections import Counter

import networkx as nx
import numpy as np
from sklearn.manifold import smacof
from scipy.optimize import minimize


COLLISION_TOL = 1e-12

def spd(G):
    G=G.subgraph(max(nx.connected_components(G),key=len)).copy()
    n=G.number_of_nodes(); ix={v:i for i,v in enumerate(G)}
    D=np.zeros((n,n))
    for s,dd in nx.all_pairs_shortest_path_length(G):
        for t,l in dd.items(): D[ix[s],ix[t]]=l
    return D,n

def fg(x,Delta,n,p):
    X=x.reshape(n,p); df=X[:,None,:]-X[None,:,:]
    d=np.sqrt((df**2).sum(-1)); np.fill_diagonal(d,1.0)
    iu=np.triu_indices(n,1)
    if np.any(d[iu] == 0.0):
        raise FloatingPointError("raw-stress gradient is undefined at an exact collision")
    r=d-Delta; np.fill_diagonal(r,0.0)
    w=r/d; np.fill_diagonal(w,0.0)
    # F = sum_{i<j} r_ij^2 = (1/2) sum_{i,j} r_ij^2, hence the
    # coordinate gradient carries the factor 2 below.
    return float((r**2).sum()/2.0), (2.0*(w[:,:,None]*df).sum(1)).ravel()

def dm(X): return np.sqrt(((X[:,None,:]-X[None,:,:])**2).sum(-1))

def nei(Ds,mean_tol=0.0):
    A=np.stack(Ds); iu=np.triu_indices(A.shape[1],1)
    P=A[:,iu[0],iu[1]]; db=P.mean(0)
    if not db.size or not np.all(np.isfinite(P)) or np.any(P < 0):
        raise ValueError("NEI undefined: require nonempty finite nonnegative pair distances")
    bad=np.flatnonzero(db <= mean_tol)
    if bad.size:
        pairs=list(zip(iu[0][bad].tolist(),iu[1][bad].tolist()))
        raise ValueError(
            "NEI undefined: nonpositive empirical mean distance for pair(s) "
            f"{pairs[:8]}" + (" ..." if len(pairs)>8 else "")
        )
    return float((P.var(0)/db**2).mean())

def eta(X,Delta,S):
    _,g=fg(X.ravel(),Delta,X.shape[0],X.shape[1]); return np.linalg.norm(g)/S


def collision_ratio(X,s_delta):
    D=dm(X); iu=np.triu_indices(D.shape[0],1)
    return float(D[iu].min()/s_delta)


def finite_difference_gradient_error(seed=17,n=6,p=2,step=1e-6):
    """Small deterministic regression check for the raw-stress gradient."""
    rng=np.random.default_rng(seed)
    X=rng.normal(size=(n,p))
    Y=rng.normal(size=(n,p))
    Delta=dm(Y)+0.25*(np.ones((n,n))-np.eye(n))
    x=X.ravel()
    _,g=fg(x,Delta,n,p)
    g_fd=np.empty_like(g)
    for k in range(x.size):
        h=step*max(1.0,abs(x[k]))
        xp=x.copy(); xm=x.copy()
        xp[k]+=h; xm[k]-=h
        fp,_=fg(xp,Delta,n,p); fm,_=fg(xm,Delta,n,p)
        g_fd[k]=(fp-fm)/(2.0*h)
    return float(np.linalg.norm(g-g_fd)/max(1.0,np.linalg.norm(g),np.linalg.norm(g_fd)))

LADDER=[(1e-6,1e-8),(1e-10,1e-12),(1e-14,1e-16),(1e-18,1e-20)]

def run(name,G,M=16,p=2):
    Delta,n=spd(G); iu=np.triu_indices(n,1)
    S=np.sqrt((Delta[iu]**2).sum())
    s_delta=np.sqrt((Delta[iu]**2).mean())
    rng=np.random.default_rng(5); X0=[rng.random((n,p)) for _ in range(M)]
    print(f"\n  {name}  (N={n})")
    print(f"    {'gtol':>8} {'ftol':>8} {'success':>9} {'eta_g med':>12} "
          f"{'eta_g max':>12} {'min chi':>10} {'coll':>6} {'Ihat':>13}")
    for gt,ft in LADDER:
        Ds,es,chis,statuses=[],[],[],[]
        for x0 in X0:
            Y,_=smacof(Delta,n_components=p,init=x0.copy(),n_init=1,max_iter=3000,
                       eps=1e-12,random_state=0,normalized_stress=False)
            r=minimize(fg,Y.ravel(),args=(Delta,n,p),jac=True,method="L-BFGS-B",
                       options=dict(maxiter=200000,ftol=ft,gtol=gt))
            Z=r.x.reshape(n,p)
            Ds.append(dm(Z)); es.append(eta(Z,Delta,S))
            chis.append(collision_ratio(Z,s_delta))
            statuses.append((bool(r.success),int(r.status),str(r.message)))
        success=sum(ok for ok,_,_ in statuses)
        collisions=sum(chi <= COLLISION_TOL for chi in chis)
        if collisions:
            Itext=f"{'invalid(coll)':>13}"
        else:
            try:
                I=nei(Ds)
                Itext=f"{I:13.4e}"
            except ValueError:
                Itext=f"{'undefined':>13}"
        print(f"    {gt:8.0e} {ft:8.0e} {success:4d}/{M:<4d} "
              f"{np.median(es):12.3e} {np.max(es):12.3e} {np.min(chis):10.3e} "
              f"{collisions:3d}/{M:<2d} {Itext}")
        if success != M:
            counts=Counter((status,message) for _,status,message in statuses)
            for (status,message),count in sorted(counts.items()):
                print(f"      optimizer status {status}: {count}/{M} — {message}")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gradient-check-only",action="store_true",
        help="run the small finite-difference regression and skip the expensive sweep",
    )
    args=parser.parse_args()

    error=finite_difference_gradient_error()
    print(f"raw-stress gradient relative finite-difference error: {error:.3e}")
    if error >= 1e-6:
        raise RuntimeError(f"raw-stress gradient regression failed: relative error={error:.3e}")
    if args.gradient_check_only:
        return

    print("Coupled tolerance ladder — corrected gradient; ungated spread diagnostic")
    run("격자 8x8",   nx.grid_2d_graph(8,8))
    run("링 C_60",    nx.cycle_graph(60))
    run("ER n=100",   nx.gnp_random_graph(100,0.06,seed=3))
    run("BA n=100",   nx.barabasi_albert_graph(100,2,seed=3))


if __name__ == "__main__":
    main()
