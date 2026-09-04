"""floor_test.py — 17자릿수 대비가 물리적 분리인가 numerical floor 인가.

결정적 시험: optimizer 의 허용오차를 사다리로 낮추며 Ihat 이 따라 내려가는지 본다.

  floor 라면  Ihat 이 허용오차를 따라 내려간다 (신호가 없고 잔여물만 재고 있다)
  신호라면    Ihat 이 허용오차와 무관하게 머문다

같은 초기조건 집합을 모든 단계에서 재사용해 표본 잡음을 없앤다.
"""
import numpy as np, networkx as nx
from sklearn.manifold import smacof
from scipy.optimize import minimize

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
    r=d-Delta; np.fill_diagonal(r,0.0)
    w=r/d; np.fill_diagonal(w,0.0)
    return float((r**2).sum()/2.0), ((w[:,:,None]*df).sum(1)).ravel()

def dm(X): return np.sqrt(((X[:,None,:]-X[None,:,:])**2).sum(-1))

def nei(Ds):
    A=np.stack(Ds); iu=np.triu_indices(A.shape[1],1)
    P=A[:,iu[0],iu[1]]; db=P.mean(0); ok=db>0
    return float((P[:,ok].var(0)/db[ok]**2).mean())

def eta(X,Delta,S):
    _,g=fg(X.ravel(),Delta,X.shape[0],X.shape[1]); return np.linalg.norm(g)/S

LADDER=[(1e-6,1e-8),(1e-10,1e-12),(1e-14,1e-16),(1e-18,1e-20)]

def run(name,G,M=16,p=2):
    Delta,n=spd(G); S=np.sqrt((Delta[np.triu_indices(n,1)]**2).sum())
    rng=np.random.default_rng(5); X0=[rng.random((n,p)) for _ in range(M)]
    print(f"\n  {name}  (N={n})")
    print(f"    {'gtol':>8} {'ftol':>8} {'eta_g 중앙':>12} {'Ihat':>13}")
    for gt,ft in LADDER:
        Ds,es=[],[]
        for x0 in X0:
            Y,_=smacof(Delta,n_components=p,init=x0.copy(),n_init=1,max_iter=3000,
                       eps=1e-12,random_state=0,normalized_stress=False)
            r=minimize(fg,Y.ravel(),args=(Delta,n,p),jac=True,method="L-BFGS-B",
                       options=dict(maxiter=200000,ftol=ft,gtol=gt))
            Z=r.x.reshape(n,p); Ds.append(dm(Z)); es.append(eta(Z,Delta,S))
        print(f"    {gt:8.0e} {ft:8.0e} {np.median(es):12.3e} {nei(Ds):13.4e}")

print("허용오차 사다리 — floor 는 따라 내려가고 신호는 머문다")
run("격자 8x8",   nx.grid_2d_graph(8,8))
run("링 C_60",    nx.cycle_graph(60))
run("ER n=100",   nx.gnp_random_graph(100,0.06,seed=3))
run("BA n=100",   nx.barabasi_albert_graph(100,2,seed=3))
