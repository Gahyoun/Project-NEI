# 연구미팅 open questions와 evidence ladder

2026-09-04 · corrected architecture

## 해석보다 먼저 확인할 층

| 층 | 연구 질문 | 현재 지위 |
|---|---|---|
| L0 | 어떤 $G\mapsto\Delta$, $p$, $W$를 썼는가 | 선언 필요 |
| L1 | $\Delta$는 $\mathbb R^p$에서 얼마나 representable한가 | $\mathcal D_p^{\rm dim}$, $\mathcal D^{\rm neg}$ |
| L2 | 얻은 embedding이 $\Delta$를 충분히 보존하는가 | normalized stress와 residual profile 필요 |
| L3 | terminal이 stationary한 numerical second-order candidate인가 | corrected all-run gate 재실행 필요 |
| L4 | admissible terminal law가 얼마나 퍼졌는가 | standardized NEI 재계산 |
| L5 | recurrent terminal class와 occupancy가 어떻게 분포하는가 | independent-batch recurrence와 $K_{\rm eff}$ |
| L6 | certified class들이 normalized stress에서 near-equivalent한가 | 해당 claim에 한해 equivalence test 필요 |
| L7 | 추가 zero mode가 finite motion으로 이어지는가 | continuation 미측정 |
| L8 | separated states 사이에 barrier가 있는가 | path/saddle search 미측정 |
| L9 | 결과가 protocol과 graph null을 넘어 안정적인가 | robustness와 null ensemble 필요 |

## 지금 가장 중요한 재실행

기존 artifact에는 terminal $X^{(m)}$, pair-standardized vectors, run별 normalized
stress, collision과 corrected quotient-Hessian inertia가 모두 없다. 다음 실행에서는
적어도

$$
\{X^{(m)},D^{(m)},z_m,S_{\Delta,W},\mathcal F_m/S_{\Delta,W},\eta_{g,m},
\min_{i<j}d_{ij}^{(m)},\chi_{\mathrm{coll},m},n_{-,m},n_{0,m},
\lambda_{\mathrm{soft},m}\}
$$

을 저장한다. 저장 용량을 줄일 때에는 $X^{(m)}$를 compact source of truth로 두고
$D^{(m)}$와 $z_m$를 결정론적으로 재구성할 수 있지만, raw $S_{\Delta,W}$와 run별
$\min_{i<j}d_{ij}^{(m)}$는 artifact에 명시적으로 남긴다. quotient-Hessian inertia는
기본적으로 일부 표본이 아니라 admissible terminal 전부에 대해 계산하며, 계산량 때문에
subsample을 쓰면 그 결과는 exploratory coverage로 따로 표시한다.

여기서

$$
s_{\Delta,W}=\sqrt{S_{\Delta,W}/\sum_{i<j}w_{ij}},\qquad
\chi_{\mathrm{coll},m}=\frac{\min_{i<j}d_{ij}^{(m)}}{s_{\Delta,W}}
$$

를 쓴다. 현재 implementation의 $W\equiv1$에서는
$s_{\Delta,W}=\sqrt{S_\Delta/N_+}$다. Hessian을 모든 terminal에서 계산했는지는 **coverage**, 각 terminal이
optimizer success, $\eta_g\le\tau_g$, $\chi_{\rm coll}\ge\tau_c$와 $n_-=0$을
모두 만족하는지는 **admissibility**다. 두 조건을 혼동하지 않는다. 전체 terminal이
gate를 통과한 경우의 all-run summary와 admissible subset의 conditional summary를
구분한다. 후자에는 $M_{\rm adm}$, acceptance
$\widehat\alpha_{\Pi,M}=M_{\rm adm}/M$와 conditional uncertainty를 붙인다. Hessian
subsample 또는 gate failure가 있으면 전체-run 값은 `all-run ungated diagnostic`으로만
보존한다.

## soft mode localization

soft eigenvalue가 중복되거나 eigengap이 작으면 개별 eigenvector는 basis rotation에
민감하다. 따라서 하나의 $v_{\rm soft}$ 대신 soft subspace projector

$$
P_{\mathcal S}=\sum_{a\in\mathcal S}v_av_a^{\mathsf T}
$$

와 node leverage

$$
s_i=\operatorname{tr}(P_{\mathcal S})_{ii}
=\sum_{a\in\mathcal S}\|v_{a,i}\|_2^2
$$

를 사용한다. $s_i$와 pairwise instability field $r_i$의 정렬은 random subspace 또는
degree-preserving null과 비교한다. 이는 degenerate eigenspace 안의 임의 basis 선택에
불변이다.

## continuous degeneracy

$H_\perp$의 near-zero eigenvalue는 higher-order candidate다. 다음 세 조건을 같이
만족하는 constrained continuation은 declared resolution에서 numerical candidate를
지지한다.

1. soft direction으로 quotient distance가 유한하게 증가
2. $\|\nabla_\perp\mathcal F\|$가 tolerance 안에 유지
3. stress rise가 선언한 scale에 비해 bounded이고 collision이 없음

경로 $P_n$의 collinear exact embedding은 필수 negative control이다. 이 경우 extra
Hessian zero modes가 있어도 stress는 transverse displacement에서 quartic하게 증가하고
continuous minimizer family는 없다.

Smooth nontrivial critical family가 존재하면 그 tangent는 Hessian kernel에 포함되지만
converse는 성립하지 않는다. Analytic family는 direct construction과 local-minimality
argument로 증명 가능. Kernel–tangent equality와 positive-definite normal Hessian의
Morse–Bott condition은 strong sufficient certificate이지 continuous degeneracy의
필요조건이 아니다.

## barrier와 metastability

terminal distribution의 gap은 barrier의 정황이지 증거가 아니다. algorithmic basin은
특정 optimizer map의 preimage로 정의할 수 있지만 physical metastability를 말하려면
두 terminal 사이의 minimax path, nudged-elastic-band류 경로 또는 saddle search가
필요하다.

## finite-$M$과 coverage

$M=100$은 같은 graph를 반복 embedding하여 consistency를 보는 설계로 타당하다. 다만
state multiplicity와 covariance spectrum의 해상도는 별도 문제다.

- $\widehat{\mathcal I}(M)$ rarefaction과 bootstrap CI
- $K_{\rm obs}(M)$, singleton/doubleton, new-state rate
- independent seed batch에서 class matching
- $K_{\rm eff}^{(1)}$, $K_{\rm eff}^{(2)}$
- $d_{\rm eff}(M)$과 leading eigenspaces

$K=M$이면 적어도 관측 범위에서는 coverage가 부족하므로 occupancy 추정과 total-state
count를 보류한다.

## protocol robustness

NEI는 $\Pi$에 조건부이다. network-level descriptor로 올리려면

- $\rho_0$: uniform, cMDS+noise, spectral+noise
- optimizer: corrected SMACOF+polish, direct stress L-BFGS
- 차원과 weight sensitivity
- value뿐 아니라 network rank와 terminal-law distance

를 보고한다. 같은 초기조건에서 optimizer가 다른 terminal에 가는 것은 적어도 하나가
실패했다는 뜻이 아니라 basin partition 자체가 algorithm-dependent하다는 뜻이다.

## graph null ensemble

random graph 한 realization의 순서가 아니라 이중 ensemble로 설계한다.

$$
G^{(b)}\sim\mathcal E_{\rm null},\qquad
X_0^{(b,m)}\sim\rho_0.
$$

- ordered $k$-regular graph와 동일한 $(N,E,k)$의 connected random-regular ensemble
- 일반 graph의 degree-preserving simple connected rewiring
- random-regular ensemble과 matched $G(N,E)$ 또는 density-null ER
- exact-realizable path control
- symmetry-rich control

모든 null에 같은 preprocessing, $\Delta$, $p$, $W$, optimizer, polish와 $M$을 적용한다.
첫 비교는 degree를 고정한 edge organization, 두 번째 비교는 full degree sequence,
세 번째 비교는 degree heterogeneity까지 순서대로 해제한다. Real network가 두 null보다
작다는 hypothesis를 쓸 경우 다음 one-sided contrasts를 사전 선언할 수 있다.

$$
\mathcal I_{\rm real}<\widetilde{\mathcal I}_{\rm deg},\qquad
\mathcal I_{\rm real}<\widetilde{\mathcal I}_{\rm ER}
$$

두 방향의 관측은 해당 hypothesis를 지지하지만 방향 자체를 narrative로 강제하지 않는다.
두 null 사이의 순서도 강제하지 않는다. graph-to-graph variation과 within-graph restart
variation을 계층적으로 분리한다.

## nonredundancy

Representability와 terminal reproducibility가 different estimands라는 정의적 구분은
statistical independence 또는 nonredundancy를 함의하지 않는다.
$\mathcal I$–$d_{\rm eff}$ correlation도 그 주장을 검정하지 않는다. 필요한 것은

$$
\mathcal D_p^{\rm dim},\mathcal D^{\rm neg}
\quad\text{versus}\quad
\mathcal I,d_{\rm eff},K_{\rm eff}
$$

의 cross-analysis와 size, mean shortest path, density, degree heterogeneity를 통제한
partial association이다. 이것이 있어야 MDS 결과로 네트워크의 추가 성질을
정량화한다는 주장이 비중복성 측면에서 완성된다.
