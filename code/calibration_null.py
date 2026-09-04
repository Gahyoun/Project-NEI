"""calibration null: D_p=0 인 그래프에서 잰 NEI 가 곧 수치 잡음 바닥이다.
NEI 는 반드시 쌍별 표준화로 계산한다 (Ihat_M = tr(B_z)/M, z_ma = d_a/(dbar_a sqrt(N+)))."""
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

def Dp(Delta,p=2):
    D2=Delta**2; rm=D2.mean(1,keepdims=True)
    B=-0.5*(D2-rm-rm.T+D2.mean()); B=0.5*(B+B.T)
    mu=np.linalg.eigvalsh(B)[::-1]; tot=np.abs(mu).sum()
    return float((np.maximum(mu[p:],0).sum()+np.maximum(-mu,0).sum())/tot)

def fg(x,Delta,n,p):
    X=x.reshape(n,p); df=X[:,None,:]-X[None,:,:]
    d=np.sqrt((df**2).sum(-1)); np.fill_diagonal(d,1.0)
    r=d-Delta; np.fill_diagonal(r,0.0)
    w=r/d; np.fill_diagonal(w,0.0)
    return float((r**2).sum()/2.0), ((w[:,:,None]*df).sum(1)).ravel()

def nei_std(Ds):
    """쌍별 표준화 NEI. Ds 는 거리행렬 리스트."""
    A=np.stack(Ds); iu=np.triu_indices(A.shape[1],1)
    P=A[:,iu[0],iu[1]]                      # (M, N+)
    dbar=P.mean(0)
    ok=dbar>0
    return float((P[:,ok].var(0)/dbar[ok]**2).mean())

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

print("쌍별 표준화 NEI (Ihat = mean_a Var/dbar^2), M=24, p=2\n")
run("경로 P_60",        nx.path_graph(60))
run("경로 P_120",       nx.path_graph(120))
run("격자 8x8",         nx.grid_2d_graph(8,8))
run("격자 12x12",       nx.grid_2d_graph(12,12))
run("링 C_60",          nx.cycle_graph(60))
run("ER n=120 p=.05",   nx.gnp_random_graph(120,0.05,seed=3))
run("BA n=120 m=2",     nx.barabasi_albert_graph(120,2,seed=3))
