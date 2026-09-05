# “realized geometric degeneracy”의 수학적 정의와 인증 조건

`2026-09-04`

## 1. 논문에서 쓸 정의

이 프로젝트에서 **realized geometric degeneracy**는 다음처럼 제한하여 정의한다.

> 고정된 protocol \(\Pi\) 아래 numerical admissibility에 조건부인 terminal law가,
> 사전에 선언한 pair-distance metric \(\rho_D\)와 resolution \(\varepsilon_D\)에서
> 하나의 geometry로 붕괴하지 않는 현상을 **realized geometric degeneracy**라 한다.

여기서

\[
\Pi=(G\mapsto\Delta,\,p,\,W,\,\rho_0,\,\rho_{\rm alg},\,\mathcal A,
\tau_g,\tau_H,\tau_D,T_{\max})
\]

는 dissimilarity 규칙, 차원, 가중치, 초기분포, 최적화기와 수치 문턱값까지 포함하는
완전한 protocol이다. 초기조건과 algorithmic random variable \(\Xi\)에 대한 measurable
terminal map을 \(T_\Pi(X^{(0)},\Xi)\)라 하고 \(q(X)=D(X)\)를 모든 쌍의 Euclidean
distance vector라 하면, population 분석 대상은

\[
\mu_\Pi=(q\circ T_\Pi)_\#(\rho_0\otimes\rho_{\rm alg})
\]

이다. numerical event를

\[
A_{\rm num}=\{\mathrm{success},\eta_g\le\tau_g,
\chi_{\rm coll}\ge\tau_c,n_-(H_\perp)=0\}
\]

로 선언하면 실제 분석 law와 acceptance probability는

\[
\mu_\Pi^{\rm adm}=\mathcal L(q(T_\Pi)\mid A_{\rm num}),\qquad
\alpha_\Pi=\Pr_\Pi(A_{\rm num})
\]

이다. conditional law를 정의하려면 \(\alpha_\Pi>0\)이어야 한다. \(\mu_\Pi^{\rm adm}\)은
\(\mathrm E(p)\)를 이미 몫한 full terminal distance geometry의 conditional distribution이고,
NEI는 아래에서 선언하는 \(\mathcal P\)-coordinate projection을 사용한다. \(M\)은 이
population law의 인자가 아니라 empirical measure
\(\widehat\mu_{\Pi,M}\)의 sample size다. 따라서 \(M\)은 Monte Carlo precision과
rare-class detection power를 제한하고, geometric resolution은 \(\varepsilon_D\)가 정한다.

full pair vector의 coordinate restriction을 \(\pi_{\mathcal P}\)라 하고

\[
D_{\mathcal P}=\pi_{\mathcal P}(D),\qquad
q_{\mathcal P}=\pi_{\mathcal P}\circ q,\qquad
\mu_{\Pi,\mathcal P}^{\rm adm}
=(\pi_{\mathcal P})_\#\mu_\Pi^{\rm adm}
\]

로 둔다. prespecified pair set \(\mathcal P\)에서 \(w_a>0\)이고
\(S_{\Delta,W}>0\)이라 하자. 일반 weight에서는

\[
S_{\Delta,W}=\sum_{a\in\mathcal P}w_a\Delta_a^2,
\qquad
\rho_D(d,d')=\left[
\frac{\sum_{a\in\mathcal P}w_a(d_a-d'_a)^2}{S_{\Delta,W}}
\right]^{1/2}
\]

를 사용한다. 이 \(\rho_D\)는 projected pair space의 metric이며 full pair space에서는
partial \(\mathcal P\)에 대해 pseudometric이다. population definition은
\(\operatorname{diam}_{\rho_D}\operatorname{supp}(\mu_{\Pi,\mathcal P}^{\rm adm})>
\varepsilon_D\)이다. finite sample은 recurrent \(\varepsilon_D\)-separated classes를
관측할 뿐 arbitrarily rare population support를 배제하지 못한다. complete-support
detection claim에는 minimum class mass 또는 missing-mass assumption이 필요하다.
이 판정이 full terminal geometry의 noncollapse와 동치인 경우는 \(\mathcal P\)가 모든
unordered pair를 포함하거나 \(\pi_{\mathcal P}\)가 admissible support에서 injective인
경우다. 그 외에는 \(\mathcal P\)-resolved degeneracy로 표기한다.

이 정의에서 **realized**는 population protocol이 terminal geometry를 유도하고 점유한다는
뜻이다. finite-\(M\) observation 자체가 population property를 인증한다는 뜻은 아니다.
또한 다음 세 뜻을 포함하지 않는다.

- 서로 다른 terminal이 정확히 같은 stress를 갖는다는 뜻이 아니다.
- optimizer 또는 초기분포와 무관한 landscape invariant라는 뜻이 아니다.
- Hessian 영모드만으로 연속 minimizer manifold가 증명되었다는 뜻이 아니다.

따라서 본문의 가장 안전한 핵심 문장은 다음이다.

> **NEI is a geometry-weighted observable of realized terminal degeneracy under a
> declared embedding protocol.**

independent-batch recurrence까지 확인하기 전에는 `terminal-distance dispersion`, 그
뒤에는 `observed recurrent terminal multiplicity at $(M,\varepsilon_D)$`라고 부른다.
class-wise numerical test 뒤에는 `strict-local-minimum candidates`, stress-equivalence
interval 뒤에는 `normalized-stress near-equivalence`, barrier evidence 뒤에는
`metastability under the tested dynamics`라고 부른다.

## 2. 서로 다른 네 종류의 degeneracy

### 2.1 Gauge degeneracy

stress는 \(X\mapsto XQ+\mathbf1a^{\mathsf T}\), \(Q\in O(p)\)에 불변이다. 이것은
물리적 비유일성이 아니라 좌표 표현의 중복이다. full configuration space의 일반 위치에서는 orbit tangent의
차원이

\[
q=p+\frac{p(p-1)}2
\]

이지만, centered configuration의 rank가 $r<p$이거나 비자명한 stabilizer가 있으면

\[
q(X)=\dim \mathrm E(p)-\dim\operatorname{Stab}(X)
=p+\frac{r(2p-r-1)}2
\]

으로 작아질 수 있다. centered subspace를 ambient constraint로 이미 적용했다면
translation term \(p\)가 사라져 \(q_{\rm centered}=r(2p-r-1)/2\)이다. 따라서 형식적인
\(q\)개 고유값을 잘라내면 안 되고, 실제 coordinate representation의 orbit-tangent
matrix를 만든 뒤 그 orthogonal complement에서 Hessian을 계산해야 한다.

### 2.2 Spectral degeneracy와 soft mode

stationary point에서 \(H=\nabla^2\mathcal F\)의 inertia를 quotient space에서 읽는다.

\[
n_-(H_\perp),\qquad n_0(H_\perp),\qquad n_+(H_\perp).
\]

- \(n_->0\): saddle 방향이 해상되므로 local minimum이 아니다.
- \(n_-=0\), \(\lambda_{\min}(H_\perp)>\tau_H\): 해상도 안에서 strict
  second-order minimum 후보이다.
- \(n_-=0\), 추가 영모드 존재: infinitesimal soft-mode 후보이다.

마지막 경우가 곧 연속 degeneracy는 아니다. \(f(x)=x^4\)는 고립된 strict minimum을
가지지만 \(f''(0)=0\)이다. 반대로 \(f(x,y)=y^4\)의 minimizer set \(\{y=0\}\)은 exact
continuous manifold이지만 normal Hessian이 0이므로 Morse–Bott가 아니다. exact family는
quotient space의 nonconstant path \(X(t)\)가 exact local minimizers로 이루어짐을 직접
보이는 방식으로 인증할 수 있다. global-minimum degeneracy를 주장할 때는 추가로
\(X(t)\in\operatorname*{argmin}\mathcal F\)가 필요하다.

더 강한 regularity를 위해 smooth fixed-rank quotient stratum에서
\(\dim\mathcal M\ge1\), \(\mathcal M\subset\operatorname{Crit}(\mathcal F)\)와 모든
\(X\in\mathcal M\)에서

\[
\ker H_X=T_X\mathcal M,\qquad
H_X\big|_{(T_X\mathcal M)^\perp}\succ0
\]

인 Morse–Bott 구조를 보이면 smooth local minimizer manifold와 transverse quadratic
stability의 sufficient analytic certificate가 된다. 모든 continuous minimizer set의
필요조건은 아니다. finite continuation은 declared resolution에서의 numerical
continuous-degeneracy candidate를 지지하지만 exact manifold의 증명은 아니다.

프로젝트 내부의 더 강한 반례는 path control이다. $P_n$을 $p=2$에서
$X_i=(a_i,0)$로 exact embedding하고 transverse perturbation
$X_i(t)=(a_i,tv_i)$를 주면

\[
d_{ij}(t)=|a_i-a_j|
+\frac{t^2(v_i-v_j)^2}{2|a_i-a_j|}+O(t^4),
\]

따라서

\[
\mathcal F(X(t))
=\frac{t^4}{4}\sum_{i<j}w_{ij}
\frac{(v_i-v_j)^4}{|a_i-a_j|^2}+O(t^6).
\]

quotient Hessian에는 transverse zero modes가 있지만 full distance matrix의 exact
realization은 $\mathrm E(2)$까지 유일하다. 즉 extra kernel과 isolated minimum이
공존하며, 이 예를 Hessian classifier의 필수 unit test로 사용한다. 여기서 유일성은
zero-stress global realization orbit에 대한 statement다. 같은 nonconvex raw-stress
objective에 다른 positive-stress local minima가 없다는 결론은 따르지 않는다.

### 2.3 Normalized-stress near-equivalence

서로 분리된 terminal class를 \(\gamma\)라 하고 대표점의 무차원 stress를

\[
e_\gamma=\frac{\mathcal F(X_\gamma^\star)}{S_{\Delta,W}}
\]

라 하자. 여기서 \(X_\gamma^\star\)는 사전에 정한 class representative이고,
\(\mathcal F\)는 thermodynamic energy가 아니라 embedding stress objective다. 두 class의
stress-difference confidence interval이 수치오차와 반복실험
불확실성을 포함한 declared equivalence margin \([-\tau_E,\tau_E]\) 안에 들어갈 때만
`\(\tau_E\)-near-degenerate`라고 부른다. null hypothesis를 기각하지 못했다는 사실만으로
equivalence가 성립하지 않는다. NEI는 거리를 사용하므로 \(e_\gamma\)의 equivalence를
단독으로 판정할 수 없다.

보고할 보조량은 예를 들어

\[
V_E=\sum_\gamma P_\gamma(e_\gamma-\bar e)^2,
\qquad
\Delta_E=\max_\gamma e_\gamma-\min_\gamma e_\gamma
\]

이다. objective-value equivalence를 말하려면 \(\Delta_E\), 각 \(e_\gamma\)의 uncertainty와
equivalence margin을 반드시 함께 보고한다.

### 2.4 Realized terminal multiplicity

이것이 NEI와 직접 연결되는 층이다. class occupancy를 \(P_\gamma\)라 하면 관측된 class
수 \(K_{\rm obs}\) 외에

\[
K_{\rm eff}^{(2)}=\frac1{\sum_\gamma P_\gamma^2},\qquad
K_{\rm eff}^{(1)}=\exp\!\left[-\sum_\gamma P_\gamma\log P_\gamma\right]
\]

을 보고할 수 있다. 이들은 observed occupancy distribution의 effective number이지
total support size 또는 state count가 아니다. 또한 기하학적으로 얼마나 멀리
떨어졌는지는 말하지 않는다. 반대로 NEI는 geometry-weighted spread를 재지만 class 수를
세지 않는다. 두 observable을 함께 보고해도 finite-\(M\) coverage와 recurrence가 없으면
population state count는 식별되지 않는다.

## 3. Representability spectrum에서의 두 degeneracy

finite, symmetric, hollow, nonnegative $\Delta$에 대해
$B=-C\Delta^{\circ2}C/2$의 spectrum에서
$\mu_a^+=\max(\mu_a,0)$, $\mu_a^-=\max(-\mu_a,0)$로 두면

\[
\mathcal D_p^{\rm dim}
=\frac{\sum_{a>p}\mu_a^+}{\sum_a|\mu_a|},
\qquad
\mathcal D^{\rm neg}
=\frac{\sum_a\mu_a^-}{\sum_a|\mu_a|}
\]

를 나눈다. 첫 항은 Euclidean dimension이 $p$보다 높은 성분, 둘째는 Gram PSD를 깨는
genuine non-Euclidean 성분이다. 둘의 합은

\[
\mathcal D_p
=\frac{\min_{K\succeq0,\,\operatorname{rank}K\le p}\|B-K\|_*}{\|B\|_*}
\]

인 normalized nuclear-norm residual이다. 이 ratio는 $\|B\|_*>0$에서 정의하고
$B=0$에는 $\mathcal D_p=0$ convention을 쓴다. 큰 $\mathcal D_p$를 곧바로 physical
frustration으로 읽지 않고 두 성분을 먼저 보고한다.

$\mathcal D_p$와 $\mathcal I$는 서로 다른 mathematical object다. 이 구분은 두 양의
statistical independence를 뜻하지 않는다. graph ensemble에서 두 양은 같은 $\Delta$와
graph covariates를 공유할 수 있으므로 association 또는 conditional independence는 별도
empirical hypothesis로 검사한다.

cMDS cutoff에서 $\mu_p=\mu_{p+1}>0$이면 optimal subspace가 비유일하고, eigengap이
작으면 Davis--Kahan 관점에서 eigenvectors가 perturbation에 민감하다. 반복고유값 안의
개별 eigenvector 대신 spectral projector를 보고하는 것이 basis-invariant하다.

## 4. NEI의 정확한 선형대수 표현

prespecified pair set \(\mathcal P\), \(N_+=|\mathcal P|\)에서
\(0<\mathbb E[d_a]<\infty\), \(\mathbb E[d_a^2]<\infty\)를 가정하고

\[
\rho_\mu^2(d,d')=\frac1{N_+}\sum_{a\in\mathcal P}
\left(\frac{d_a-d'_a}{\mathbb E[d_a]}\right)^2
\]

로 두자. iid \(D_{\mathcal P},D'_{\mathcal P}\sim
\mu_{\Pi,\mathcal P}^{\rm adm}\)에 대해

\[
\mathcal I(\mu_{\Pi,\mathcal P}^{\rm adm})
=\frac12\mathbb E[\rho_\mu^2(D_{\mathcal P},D'_{\mathcal P})].
\]

따라서 \(\mathcal I=0\) iff \(\mu_{\Pi,\mathcal P}^{\rm adm}\) is a point mass. full law
\(\mu_\Pi^{\rm adm}\)의 point-mass collapse와 동치이려면 \(\mathcal P\)가 모든 unordered
pair를 포함하거나 \(\pi_{\mathcal P}\)가 admissible support에서 injective여야 한다.

\(m_a=\mathbb E[d_a]\)라 하고

\[
c_-^2=\frac{S_{\Delta,W}}{N_+}
\min_{a\in\mathcal P}\frac1{w_am_a^2},\qquad
c_+^2=\frac{S_{\Delta,W}}{N_+}
\max_{a\in\mathcal P}\frac1{w_am_a^2}
\]

로 두면 finite \(\mathcal P\)에서

\[
c_-\rho_D(d,d')\le\rho_\mu(d,d')\le c_+\rho_D(d,d')
\]

이다. 즉 두 metric은 norm-equivalent이지만 같은 numerical threshold를 공유하지 않는다.
따라서 explicit calibration 없이 NEI alone을
\(\operatorname{diam}_{\rho_D}\operatorname{supp}
(\mu_{\Pi,\mathcal P}^{\rm adm})>\varepsilon_D\)의 estimator로 읽을 수 없다.

쌍 \(a=(i,j)\), \(a=1,\dots,N_+\)에 대해

\[
z_{ma}=\frac{d_a^{(m)}}{\bar d_a\sqrt{N_+}},\qquad
\bar d_a=\frac1M\sum_{m=1}^M d_a^{(m)}
\]

를 정의하고, \(Z_c=C_MZ\), \(C_M=I_M-\mathbf1\mathbf1^{\mathsf T}/M\)라 하자.
empirical variance divisor \((1/M)\)을 쓰면

\[
\widehat{\mathcal I}_M
=\frac1{N_+}\sum_a\frac{\operatorname{Var}_m(d_a^{(m)})}{\bar d_a^2}
=\frac1M\lVert Z_c\rVert_F^2
=\frac1M\operatorname{tr}(Z_cZ_c^{\mathsf T}).
\]

표준화된 run 거리 \(\delta^{(z)}_{mm'}=\|z_m-z_{m'}\|_2\)를 저장하면

\[
B_z=-\frac12C_M\bigl(\delta^{(z)}\bigr)^{\circ2}C_M=Z_cZ_c^{\mathsf T},
\qquad
\boxed{\widehat{\mathcal I}_M=\operatorname{tr}B_z/M}.
\]

이는 finite-sample plug-in identity이지 population NEI의 unbiasedness statement가 아니다.
sample variance convention \((1/(M-1))\)이면 마지막 분모도 \(M-1\)이다. 모든
\(\bar d_a>0\)이어야 하며 하나라도 0이면 primary NEI는 undefined다. upper-triangle
vector가 아니라 full Frobenius distance를 쓰면 off-diagonal pair가 두 번 들어가므로
추가 \(2\)배 계수를 맞춰야 한다.

중요하게도 현재 artifact의

\[
\Delta_{mm'}=\frac{\|D^{(m)}-D^{(m')}\|_F}
{\sqrt{\sum_a\bar d_a^2}}
\]

는 pair별 \(1/\bar d_a\) 표준화를 하지 않는다. 이 \(\Delta\)로 복원한 Gram trace와
spectrum은 **raw-distance terminal cloud**의 양이며 NEI의 covariance operator와 같지
않다. 기존 artifact만으로 \(B_z\)를 복원할 수 없으므로 terminal pair vectors 또는
\(\delta^{(z)}\)를 다시 저장해야 한다.

표준화된 covariance의 고유값을 \(\nu_a\)라 할 때

\[
d_{\rm eff}=\frac{(\sum_a\nu_a)^2}{\sum_a\nu_a^2}
\]

는 covariance의 spectral participation ratio이다. 이는 선형 분산의 유효 rank이지
minimizer manifold의 위상적 차원도, 독립 physical degree of freedom의 개수도 아니다.
이산 점구름도 큰 \(d_{\rm eff}\)를 가질 수 있고 굽은 1차원 manifold도 여러 선형
주성분을 요구할 수 있다. \(\operatorname{tr}\Sigma_z=0\)이면 numerator와 denominator가
모두 0이므로 \(d_{\rm eff}\)는 NA로 보고한다.

## 5. Exact-convergence decomposition

terminal class \(\gamma\) 안의 평균과 분산을 \(\mu_a^\gamma,v_a^\gamma\)라 하면

\[
\operatorname{Var}(d_a)
=\sum_\gamma P_\gamma v_a^\gamma
+\sum_\gamma P_\gamma(\mu_a^\gamma-\bar d_a)^2.
\]

따라서

\[
\mathcal I=\mathcal I_{\rm within}+\mathcal I_{\rm between}.
\]

각 run이 고립된 minimizer orbit에 정확히 수렴하면 \(v_a^\gamma=0\)이므로
\(\mathcal I_{\rm within}=0\)이다. 이 극한에서 NEI는 occupancy와 terminal geometry의
조합으로 정해지며, occupancy와 class geometry를 고정한 conditional identity에는 Hessian
spectrum이 직접 나타나지 않는다. 그러나 이것은 dynamical independence가 아니다. local
curvature, barrier와 basin-boundary geometry는 protocol-induced occupancy $P_\gamma$를
바꾸어 exact convergence에서도 $\mathcal I$에 간접적으로 영향을 줄 수 있다. 따라서
NEI와 softness는 distinct observables이며 generally independent mechanisms가 아니다.

또한 큰 \(\mathcal I\)가 많은 minima를 뜻하지 않는다. 드물게 점유되지만 매우 멀리
떨어진 class 하나만 있어도 \(K=2\)에서 큰 값이 가능하다. 그러므로 \(\mathcal I\),
\(K_{\rm eff}\), \(\Delta_E\), Hessian/continuation은 서로 대체할 수 없다.

## 6. Symmetry가 만드는 degeneracy

먼저 모든 configuration에서 생기는 Euclidean gauge \(\mathrm E(p)\)를 제거한다. 그 뒤
metric automorphism \(\sigma\in\operatorname{Aut}(\Delta)\)를 셀지는 연구 질문에 따라
정책을 명시해야 한다.

- 노드 identity가 관측 의미를 가지면 \(D\)와 \(P_\sigma DP_\sigma^{\mathsf T}\)를 서로
  다른 labeled geometry로 센다.
- topology-only observable을 원하면 \(\operatorname{Aut}(\Delta)\)까지 몫하고
  \(\min_\sigma\|D-P_\sigma D'P_\sigma^{\mathsf T}\|\)로 비교한다.

대칭점에서 Hessian이 group action과 commute하면 representation의 irreducible block으로
분해할 수 있고, 일부 eigenvalue multiplicity는 대칭에 의해 강제된다. 반대로
symmetry-broken minimum 하나가 있으면 그 group orbit가 같은 stress의 여러 minimum을
만들 수 있다. 이것은 accidental degeneracy와 구분해 보고해야 한다.

## 7. cMDS에서 놓치기 쉬운 또 하나의 degeneracy

strain은 Gram 변수 전체 공간에서는 convex quadratic이지만 제약집합

\[
\{G\succeq0:\operatorname{rank}G\le p,\ G\mathbf1=0\}
\]

은 rank 제약 때문에 nonconvex이다. positive spectral truncation이 global solution을
주지만 \(p<n\)이고 \(\mu_p=\mu_{p+1}>0\)인 positive cutoff tie에서는 최적 rank-\(p\)
Gram이 유일하지 않을 수 있다. zero-eigenvalue tie는 이 비유일성을 만들지 않는다.
따라서 `cMDS를 반복하면 NEI=0`은 결정론적 tie-breaking을 고정한 구현의
항등식이지, strain landscape의 유일성 정리가 아니다. cutoff spectral gap을 함께
확인해야 `unique cMDS geometry`라고 말할 수 있다.

## 8. “real”을 주장하기 위한 검증 사다리

1. **Protocol declaration** — \(\Delta,p,W,\rho_0,\rho_{\rm alg},\mathcal A\), stopping/polish 규칙을
   고정한다.
2. **Stationarity** — 모든 포함 run이 \(\eta_g\le\tau_g\)를 통과한다.
3. **Regularity** — collision, rank, cap, optimizer failure를 별도 flag로 저장한다.
4. **Quotient curvature** — 실제 orbit tangent의 직교여공간에서 \(H_\perp\)의 inertia를
   계산한다.
5. **Recurrence and separation** — declared \(\rho_D,\varepsilon_D\) 아래 independent batches에서 class가 재현되고,
   between-class separation이 within-class 수치산포보다 크다.
6. **Normalized-stress equivalence** — objective-value near-equivalence를 말하려면
   stress-difference interval이 \([-\tau_E,\tau_E]\)에 포함되는 equivalence test를
   통과한다. 이는 thermodynamic energy degeneracy가 아니다.
7. **Continuation과 analytic structure** — finite continuation에서 유한한 기하변위,
   작은 gradient, bounded stress rise와 no collision을 함께 보이면 numerical candidate다.
   exact family에는 nonconstant minimizer path 또는 manifold의 직접 인증이 필요하다.
   Morse–Bott structure는 smoothness와 transverse quadratic stability의 stronger sufficient
   certificate다.
8. **Finite-\(M\) uncertainty** — \(K_{\rm eff}\), \(\mathcal I\), spectrum을 독립 batch
   또는 bootstrap으로 보고하고 \(M\)에 대한 stability를 검사한다. complete-support
   detection probability에는 minimum class mass 또는 missing-mass assumption이 필요하다.
9. **Protocol robustness** — network-level descriptor라고 부르려면 여러 \(\rho_0\)와
   optimizer에서 값 또는 적어도 network 순위의 안정성을 보인다.

현재 관측은 “polish 뒤에도 NEI가 남고 terminal distance matrices가 분리된다”는 데까지
강한 증거를 준다. 그러나 기존 Hessian 투영 코드의 음의 모드 제거 오류와 gradient의
계수 불일치를 수정해 재실행해야 하고, 8/24만 검사했으며, energy equality와 independent
batch recurrence가 아직 없다. 따라서 재검산 전의 정확한 상태는

> **In the legacy runs, the stated polishing schedule did not eliminate the observed
> terminal-distance dispersion. Because those results are ungated and predate the
> corrected implementation, recurrent terminal multiplicity, multiple local minima,
> normalized-stress near-equivalence, and a continuous minimizer manifold remain open.**

이다.
