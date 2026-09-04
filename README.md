# Project NEI — research-meeting architecture

고정된 topology-to-geometry 및 optimization protocol 아래에서

1. 선택한 graph dissimilarity의 low-dimensional **representability**와
2. 반복 embedding에서 얻는 terminal geometry의 **variability/multiplicity**

를 분리해 정량화한다.

웹 지도: https://gahyoun.github.io/Project-NEI/

## 핵심 estimand

완전한 protocol을

$$
\Pi=(G\mapsto\Delta,p,W,\rho_0,\rho_{\rm alg},\mathcal A,
\text{stopping/polish},\text{tolerances})
$$

라 하고 terminal map을 $T_\Pi$, pair-distance representation을 $q(X)=D(X)$라 하면

$$
\mu_\Pi=(q\circ T_\Pi)_\#(\rho_0\otimes\rho_{\rm alg})
$$

가 NEI의 분석 대상이다. 따라서 NEI는 intrinsic graph invariant가 아니라 declared
protocol에 조건부인 response observable이다. $M$은 population law $\mu_\Pi$의 인자가
아니라 empirical measure $\widehat\mu_{\Pi,M}$의 sample size다. 본 연구의 $M=100$은
동일 graph의 repeated embedding consistency를 추정하기 위한 finite-sample design이다.
independent-batch recurrence를 확인한 뒤에만 reproducibility라는 말을 쓴다.

pair weights가 일반적일 때 dimensionless energy scale은

$$
S_{\Delta,W}=\sum_{i<j}w_{ij}\Delta_{ij}^2,
\qquad
s_{\Delta,W}=\sqrt{S_{\Delta,W}/\sum_{i<j}w_{ij}}
$$

로 둔다. 현재 first-closure implementation은 $W\equiv1$이다. numerical admissibility는
optimizer success, stationarity, collision과 quotient-Hessian inertia를 판정한다.
representational fidelity는 $\phi$와 residual profile로 topology-to-geometry 해석의
적용 범위를 정하며, poor fidelity 자체는 local minimum을 배제하지 않는다.

| 층 | 질문 | 양 | 정확한 지위 |
|---|---|---|---|
| distance geometry | $\Delta$가 $\mathbb R^p$에서 실현되는가 | $\mathcal D_p$ | fixed $(\Delta,p)$에서 algorithm-independent |
| fidelity | terminal이 $\Delta$를 얼마나 보존하는가 | $\phi=\mathcal F/S_{\Delta,W}$ | objective-conditioned lack of fit |
| terminal law | 반복 결과가 얼마나 퍼지는가 | $\mathcal I$ | protocol-conditioned geometry-weighted spread |
| occupancy | 관측된 class에 probability mass가 얼마나 분산되는가 | $K_{\rm eff}$ | clustering, recurrence와 finite-$M$ 조건부 |
| local curvature | terminal이 saddle/soft/strict인가 | inertia of $H_\perp$ | gate/diagnostic |
| energy | 다른 class가 같은 stress인가 | $\Delta_E$ | energetic degeneracy test |

## “NEI는 energy landscape의 realized geometric degeneracy를 잰다”의 정의

numerical admissibility event를 $A_{\rm num}$이라 하고 acceptance probability
$\alpha_\Pi=\Pr_\Pi(A_{\rm num})$를 함께 보고한다. 조건부 terminal law는

$$
\mu_\Pi^{\rm adm}=\mathcal L\!\left(q(T_\Pi)\mid A_{\rm num}\right)
$$

이다. 이 문서에서
**realized geometric degeneracy**는 다음 operational meaning으로만 사용한다.

> fully specified protocol 아래 conditional terminal law $\mu_\Pi^{\rm adm}$가, 선언한
> pair-distance metric $\rho_D$와 resolution $\varepsilon_D$에서 하나의 geometry로
> 붕괴하지 않는다:
> $\operatorname{diam}_{\rho_D}\operatorname{supp}(\mu_\Pi^{\rm adm})>\varepsilon_D$.

Population level에서는 $\mathcal I(\mu_\Pi^{\rm adm})>0$이 non-point-mass law와
동치이지만, finite $M$의 양의 $\widehat{\mathcal I}_M$만으로 population support를
certify할 수는 없다. 이 의미에서 NEI는 degeneracy의 geometry-weighted **크기**를 잰다.
그러나 NEI 하나는

- total support size 또는 state 수,
- equal-energy degeneracy,
- global-minimum nonuniqueness,
- barrier/metastability,
- continuous minimizer manifold

를 판정하지 않는다. $K_{\rm eff}$는 total state count가 아니라 observed occupancy의
effective number이다. state-count inference에는 recurrence와 coverage analysis가,
나머지에는 각각 $\Delta_E$, global bound, barrier search, Morse–Bott/continuation이
필요하다. 자세한 정의는
[notes/01](notes/01-nei-measures-real-degeneracy.md)과
[notes/06](notes/06-real-degeneracy-definition.md)에 있다.

## Validity conditions and withdrawn claims

- 목적함수와 gradient/Hessian의 factor 2 불일치를 수정했다.
- $PH P$의 eigenvalues를 앞에서 잘라내던 방식을 폐기하고 실제
  $\mathrm E(p)$-orbit tangent의 직교여공간에서 $H_\perp$를 계산하도록 고쳤다.
- 기존 “0/8 saddle, 24개 모두 local minima”는 corrected code 재실행 전까지
  철회했다.
- $\ker H_\perp\ne0\Rightarrow$ continuous family라는 함의를 삭제했다. 경로 그래프의
  collinear exact embedding은 extra zero modes와 isolated minimum이 공존하는 내부
  반례다.
- 기존 global-scale run distance의 Gram spectrum은 NEI와 같은 covariance가 아님을
  명시했다. pair-standardized vectors를 저장해 $d_{\rm eff}$를 재계산해야 한다.
- cMDS optimum의 무조건적 유일성, Hessian=Fisher, $1-\rho_S^2=43\%$ 정보량,
  “optimizer-independent within 15%” 주장을 조건부·탐색적 수준으로 내렸다.
- $\mathcal D_p$를 $\mathcal D_p^{\rm dim}+\mathcal D^{\rm neg}$로 분해하고
  fixed $(\Delta,p)$에서의 diagnostic이라고 명시했다.

## 현재 실증 결과의 허용 문장

기존 실행에서는 stated polishing schedule 뒤 $\widehat{\mathcal I}_M$이
$0.1100\to0.07665$로 감소했고 24개 terminal distance matrices가 보고된 cutoff
범위에서 분리되어 있었다. 즉, 그 polishing schedule은 observed dispersion을 제거하지
못했다. 그러나 이는 corrected implementation 이전의 legacy all-run ungated diagnostic이다.
corrected numerical gate, gate acceptance rate와 independent-batch recurrence 전에는
terminal multiplicity를 확정하지 않는다. class energy ledger 전에는 energetic
near-degeneracy를 말하지 않는다.

논문에 지금 쓸 수 있는 문장은 다음이다.

> In the legacy runs, the stated polishing schedule did not eliminate the observed
> terminal-distance dispersion. Because that calculation is ungated and predates the
> corrected implementation, it does not establish recurrent terminal multiplicity
> or multiple local minima.

## 1차 일단락

이것은 최종 결론이 아니라 현재 증거로 닫을 **최소 claim set 후보**다.

1. fixed $(\Delta,p)$에서 Schoenberg criterion과 $\mathcal D_p$의 exact zero-set
2. 완전히 선언한 protocol이 유도하는 terminal law $\mu_\Pi$
3. population NEI와 구분된 pair-standardized finite-sample identity
   $\widehat{\mathcal I}_M=\operatorname{tr}B_z/M$
4. corrected numerical gates 뒤 독립 batch에서 재현되는
   $\varepsilon_D$-separated terminal classes의 empirical demonstration

필수 재실행과 범위는 [data/scope.json](data/scope.json), 열린 문제는
[notes/05](notes/05-open.md), claim별 지위는 [data/claims.json](data/claims.json)에
정리했다.

## 저장소 구성

- index.html, krds.css, app.js — 연구미팅용 interactive map
- graph.js — 계층형 DAG renderer
- data — concepts, connectors, claims, references, measurements, scope, and the
  manuscript/SI/Note source map
- notes — derivations, audits, open questions
- code — reproducibility and validation code

Recommended reading order: 이 README에서 출발해 [핵심 정의](notes/01-nei-measures-real-degeneracy.md),
[covariance identity](notes/03-trace-vs-spectrum.md),
[formal definition](notes/06-real-degeneracy-definition.md),
[철회된 주장](notes/04-withdrawn-claims.md), [open questions](notes/05-open.md),
[claim ledger](data/claims.json) 순서로 확인한다.
