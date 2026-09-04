# NEI는 energy landscape의 realized geometric degeneracy를 재는가?

2026-09-04 · corrected claim

## 연구미팅용 한 문장

> **NEI is a geometry-weighted observable of realized terminal degeneracy under a
> fully declared embedding protocol.**

여기서 realized terminal degeneracy는 $\alpha_\Pi>0$인 numerical admissibility에
조건부인 terminal law가 rigid-motion quotient의 distance space에서, 선언한 metric과
resolution 아래 하나의 geometry로 붕괴하지 않는다는 **operational definition**이다.
서로 다른 terminal의 stress가 같다는 energetic
degeneracy, global-minimum nonuniqueness, optimizer-independent landscape invariant와는
다르다. 정의와 인증 조건은 [06](06-real-degeneracy-definition.md)에 정리했다.

## Why this distinction is necessary

degeneracy에는 적어도 다음이 섞일 수 있다.

1. **gauge redundancy** — translation, rotation, reflection. 물리적 차이가 아니므로
   $\mathrm E(p)$ quotient에서 제거한다.
2. **symmetry-related multiplicity** — $\operatorname{Aut}(\Delta)$가 만드는 finite
   orbit. labeled geometry를 셀지 topology quotient를 셀지 정책이 필요하다.
3. **normalized-stress near-equivalence** — 분리된 states의 embedding stress가 declared
   tolerance 안에서 같다. thermodynamic energy degeneracy와는 다른 operational statement다.
4. **local-minimum multiplicity** — 서로 다른 stress를 가질 수 있는 여러 local minima.
   Metastability는 barrier 또는 residence-time evidence를 추가로 요구한다.
5. **continuous degeneracy** — 실제 minimum manifold가 존재한다.
6. **spectral degeneracy/softness** — Hessian에 추가 영모드가 있다. 5의 필요조건일 수
   있지만 충분조건은 아니다.

NEI는 3–6을 한 번에 판정하지 않는다. NEI가 직접 재는 것은 protocol이 실제로
sampling한 terminal pair-distance geometry의 상대분산이다.

## 정확한 estimand

완전한 protocol을

$$
\Pi=(G\mapsto\Delta,p,W,\rho_0,\rho_{\rm alg},\mathcal A,
\tau_g,\tau_H,\tau_c,T_{\max})
$$

라 하고, 초기조건에서 terminal로 가는 algorithmic map을 $T_\Pi$, pair-distance
representation을 $q(X)=D(X)$라 하면

$$
\mu_\Pi=(q\circ T_\Pi)_\#(\rho_0\otimes\rho_{\rm alg})
$$

가 population 분석 대상이다. $M$개 independent runs가 만드는
$\widehat\mu_{\Pi,M}=M^{-1}\sum_m\delta_{q(T_\Pi^{(m)})}$은 이 law의 empirical
measure이며, $M$은 $\Pi$의 인자가 아니다. $M$은 Monte Carlo precision과 rare-class
detection power를 제한하고, geometric resolution은 $\varepsilon_D$가 정한다. numerical
event를 $A_{\rm num}$이라 하면

$$
\mu_\Pi^{\rm adm}=\mathcal L(q(T_\Pi)\mid A_{\rm num}),\qquad
\alpha_\Pi=\Pr_\Pi(A_{\rm num})
$$

를 함께 보고한다. 따라서 “realized”는 **early stopping 근처의 수치산포를 numerical
gate로 분리한 protocol-conditioned spread**라는 뜻이다. intrinsic 또는
thermodynamic이라는 뜻이 아니다.

## NEI와 degeneracy의 정확한 관계

prespecified pair set $\mathcal P$와 $N_+=|\mathcal P|$를 고정하고, 모든
$a\in\mathcal P$에서 $0<\mathbb E[d_a]<\infty$와 $\mathbb E[d_a^2]<\infty$를
가정한다. 그러면

$$
\mathcal I(\mu_\Pi^{\rm adm})=\frac1{N_+}\sum_{a\in\mathcal P}
\frac{\operatorname{Var}_{\mu_\Pi^{\rm adm}}(d_a)}
{\mathbb E_{\mu_\Pi^{\rm adm}}[d_a]^2}.
$$

population-dependent metric을

$$
\rho_\mu^2(d,d')=\frac1{N_+}\sum_{a\in\mathcal P}
\left(\frac{d_a-d'_a}{\mathbb E[d_a]}\right)^2
$$

로 두면 iid $D,D'\sim\mu_\Pi^{\rm adm}$에 대해
$\mathcal I=\tfrac12\mathbb E[\rho_\mu^2(D,D')]$이다. 따라서 $\mathcal I=0$ iff
$\mu_\Pi^{\rm adm}$ is a point mass. finite-resolution 판정에는 별도로 predeclared metric

$$
\rho_D(d,d')=
\left[\frac{\sum_{a\in\mathcal P}w_a(d_a-d'_a)^2}
{S_{\Delta,W}}\right]^{1/2},\qquad
S_{\Delta,W}=\sum_{a\in\mathcal P}w_a\Delta_a^2
$$

를 사용하며 $S_{\Delta,W}>0$과 $w_a>0$을 가정한다. $\rho_\mu$와 $\rho_D$는
point-mass zero set을 공유하지만 positive threshold에서 일반적으로 동치가 아니다.
따라서 resolution $\varepsilon_D$를 먼저 선언하고
$\operatorname{diam}_{\rho_D}\operatorname{supp}(\mu_\Pi^{\rm adm})>
\varepsilon_D$인지를 별도로 묻는다. finite $M$은 recurrent
$\varepsilon_D$-separated classes를 관측할 수 있을 뿐 arbitrarily rare population
support를 배제하지 못한다. complete-support detection claim에는 minimum class mass 또는
missing-mass assumption이 필요하다. 어떤 empirical $\bar d_a=0$이면 NEI는 undefined이며
해당 pair를 post hoc으로 버리거나 0을 대입하지 않는다.

하지만 역해석에는 한계가 있다.

- $\mathcal I$는 total state 수 $K$를 세지 않는다.
- 큰 $\mathcal I$는 두 개의 멀리 떨어진 states만으로도 가능하다.
- 많은 states가 서로 가까우면 $\mathcal I$는 작을 수 있다.
- 서로 다른 states의 normalized stress objective가 같은지는 $\mathcal I$에서 알 수 없다.
- discrete cloud와 continuous curve가 같은 covariance trace를 가질 수 있다.

따라서 degeneracy의 완성된 ledger는 최소한

$$
\{\mathcal I,\ d_{\rm eff},\ K_{\rm eff},\ \Delta_E,\
n_-(H_\perp),n_0(H_\perp),\ \text{recurrence},\ \text{continuation}\}
$$

을 함께 사용한다.

## Legacy polish 결과가 말해 준 것

기존 실행에서는 SMACOF terminal을 L-BFGS로 polish한 뒤
$\widehat{\mathcal I}_M:0.1100\to0.07665$로 감소했고, 24개 terminal distance
matrices의 최소 상대거리가 $7.95\times10^{-2}$였다. 즉, 그 stated polishing
schedule은 observed dispersion을 제거하지 못했다.

다만 감사에서 두 구현 문제가 발견되었다.

1. 목적함수 $\sum_{i<j}(d_{ij}-\Delta_{ij})^2$와 analytic gradient/Hessian 사이에
   factor 2 불일치가 있었다.
2. $PH P$의 정렬 eigenvalues에서 앞의 gauge-mode 수를 잘라내어 true negative
   eigenvalues도 버릴 수 있었다.

두 코드는 수정했지만 결과를 아직 재실행하지 않았다. 따라서 과거의 “negative
eigenvalue 0/8”, “24개 모두 진짜 local minimizer”는 인증으로 사용할 수 없다.
현재 허용되는 서술은 다음이다.

> Polishing left a substantial dispersion among 24 well-separated sampled terminal
> geometries. The corrected stationarity and quotient-Hessian tests must be rerun
> before these states are classified as local minima.

## Realized geometric degeneracy를 지지하는 최소 조건

### A. Realized geometric degeneracy

- 모든 분석 run의 optimizer success, $\eta_g\le\tau_g$, no-collision을 기록하고
  acceptance rate $\alpha_\Pi$를 보고
- 실제 gauge tangent의 직교여공간에서 $n_-(H_\perp)=0$
- independent batches에서 $\varepsilon_D$-separated classes가 재현
- between-terminal separation이 numerical within-terminal scale보다 큼
- $\widehat{\mathcal I}$의 bootstrap CI가 numerical floor와 분리

이 조건은 declared $(M,\varepsilon_D)$에서 observed recurrent terminal multiplicity를
지지하며 population multiplicity의 evidence가 된다. complete population support에 대한
주장은 $M$--$\varepsilon_D$ sensitivity만으로 충분하지 않고 minimum-mass 또는
missing-mass assumption을 추가로 요구한다.

### B. Multiple strict-local-minimum candidates

A에 더해 각 representative의 stationarity와 $H_\perp\succ0$가 tolerance와 refinement에
안정적인지 확인한다. 이것은 declared numerical tolerance에서의 strict-local-minimum
candidate다. exact analytic certificate를 주장하려면 별도 오차 bound가 필요하다.
해상되지 않은 zero mode가 있으면 higher-order candidate로 남긴다.

### C. Normalized-stress near-equivalence

각 state의 normalized stress를

$$
e_\gamma=\mathcal F(X_\gamma^\star)/S_{\Delta,W},\qquad
\Delta_E=\max_\gamma e_\gamma-\min_\gamma e_\gamma
$$

를 저장한다. 여기서 $X_\gamma^\star$는 사전에 정한 class representative이고,
$\mathcal F$는 thermodynamic energy가 아니라 embedding stress objective다. pairwise
stress-difference confidence interval이
$[-\tau_E,\tau_E]$ 안에 들어가는 equivalence test를 통과한 경우에만
$\tau_E$-near-degenerate minima라고 부른다. 단순한 non-rejection은 충분하지 않다.

### D. Continuous-degeneracy candidate와 analytic manifold

$\ker H_\perp\ne0$만으로는 부족하다. soft subspace를 따라 finite displacement를
continuation하며 low stress, low gradient, no collision을 동시에 보이면 declared
resolution에서 numerical candidate를 얻는다. exact local manifold에는 smooth fixed-rank
quotient stratum에서 $\dim\mathcal M\ge1$, $\mathcal M\subset\operatorname{Crit}(\mathcal F)$,
$\ker H_X=T_X\mathcal M$과 positive-definite normal Hessian을 갖는 analytic Morse–Bott
structure가 필요하다.

## $K=M$의 해석

현재 $K_{\rm obs}=M=24$는 “적어도 24개의 separated sampled geometries”만 뜻한다.
모든 state가 singleton이므로 occupancy $P_\gamma$, total state count와 coverage는
식별되지 않는다. 따라서 $M=100$은 consistency ensemble로 의도된 값이라는 점은
타당하지만, observed multiplicity의 stability를 평가하려면 $M$-rarefaction과
independent-batch recurrence가 별도로 필요하다. 어떤 finite $M$도 arbitrarily rare state를
배제하지 못한다.

## 최종 권장 용어

| 증거 | 연구미팅에서 쓸 말 |
|---|---|
| polish 뒤 spread가 남음 | persistent terminal-geometry dispersion |
| corrected gates를 통과한 separated observations | admissible terminal-distance dispersion |
| independent batches에서 재현되는 classes | observed recurrent terminal multiplicity at $(M,\varepsilon_D)$ |
| class-wise numerical minimum test | strict-local-minimum candidates |
| stress-difference interval이 margin 안에 포함 | $\tau_E$-near-equivalent stress minima |
| barrier까지 확인 | metastable basins |
| finite continuation으로 connected family 해상 | continuous-degeneracy candidate |
| analytic Morse–Bott 조건 확인 | local continuous minimizer manifold |

따라서 headline은 operational definition과 함께 사용할 수 있지만, 첫 등장 직후 반드시
다음 제한문을 붙인다.

> Here “realized geometric degeneracy” denotes a protocol-conditioned terminal law
> whose support diameter exceeds a declared pair-distance resolution. Finite samples
> provide recurrent separated classes rather than a proof of population support, and
> the term does not imply energy equivalence or optimizer-independent nonuniqueness.
