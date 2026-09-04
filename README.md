# Project NEI — research-meeting architecture

웹 지도: https://gahyoun.github.io/Project-NEI/

## 0. 이 문제가 놓인 자리

이 연구는 **distance geometry**, **비볼록 역문제**, **무질서계 통계물리**가 겹치는
자리에 있다. 세 분야가 모두 *degeneracy*를 쓰지만 지시대상이 다르다. 최소한 여섯을
갈라야 한다.

| 이름 | 가리키는 것 |
|---|---|
| representability deficiency | $\Delta\notin\mathrm{EDM}_p$. $\mathcal D_p$가 재는 것 |
| conic / Slater degeneracy | feasible set이 proper face에 놓이는 현상 |
| quotient-Hessian degeneracy | rigid-body mode 제거 후 Hessian의 singularity |
| terminal multiplicity | 분리된 terminal class의 존재 |
| equal-stress degeneracy | 서로 다른 state의 stress 등가성 |
| **realized terminal-geometry spread** | $\mu^{\rm adm}_{G,\Pi}$의 noncollapse. **NEI가 재는 것** |

Drusvyatskiy–Wolkowicz(2017)가 다루는 것은 둘째 줄이다. multiple minima나 Hessian
zero mode가 아니므로, 그 문헌은 *terminology를 경계하는 근거*로만 쓰고 landscape
multiplicity의 정당화로 쓰면 category error다.

**중요한 구조적 사실.** complete all-pairs metric이 정확히 Euclidean-representable이면
centered Gram이 결정되므로 realization은 Euclidean isometry까지 유일하다. 따라서 NEI가
보는 multiplicity는 고전적 *incomplete* distance-geometry ambiguity(sensor localization,
graph realization)가 아니라 complete non-Euclidean graph metric의 **fixed-rank nonconvex
approximation**에서 발생한다. 이 구분이 인용 배치를 정한다.

### 연구의 수학적 중심 — kernel

중심은 확률측도 하나가 아니라 **graph-to-terminal-law kernel**이다.

$$K_\Pi(\Delta,B)=\Pr\left[q\left(T_\Pi(\Delta,Z,\Xi)\right)\in B \mid \mathrm{Adm}\right]$$

$$\mu^{\rm adm}_{G,\Pi}=K_\Pi(\Delta(G),\cdot),\qquad \mathcal I=\Phi(\mu^{\rm adm}_{G,\Pi})$$

$$G\longmapsto\Delta(G)\longmapsto\mu^{\rm adm}_{G,\Pi}\longmapsto\{\mathcal I,\;K_{\rm eff},\;\lambda_{\rm soft},\ldots\}$$

$\mathcal I$는 이 law의 functional 하나일 뿐이고 $K_{\rm eff}$, $\lambda_{\rm soft}$,
class separation은 같은 law의 다른 functional이다. kernel로 세워야 protocol을 바꿀 때
무엇이 변하고 무엇이 남는지 물을 수 있다.

pushforward 자체에는 선례가 있다 — Stillinger–Weber의 inherent-structure 구성, Menck 등의
basin stability. NEI의 차별점은 이를 quotient terminal geometry 전체에 대한 **primary
estimand**로 삼은 구성이다.

### 열린 물리 질문

현재 결과가 지지하는 것은

$$\mathcal D_p>0 \;\not\Rightarrow\; \mathcal I>0$$

이다. stationarity 허용오차를 12자릿수 훑으면 질서 대조군의 NEI는 numerical floor로
내려가고 ER·BA는 $O(10^{-1})$에 머문다. 전자는 **point mass로부터 unresolved**이고
후자는 **tolerance-stable nonconcentration**이다. (마지막 단 $10^{-18}$은 double
precision 범위를 넘으므로 saturation 확인으로만 쓴다.)

따라서 질문은 이렇게 바뀐다:

> *Which organization of geometric incompatibility, beyond its total magnitude, controls
> the nonconcentration of the protocol-induced terminal law?*

가장 유망한 mechanism은 **signed prestress의 organization**이다. raw-stress Hessian은
개념적으로 $H_\perp=H_{\rm rigidity}+H_{\rm prestress}$로 분해되는데, $\mathcal D_p$나
total stress는 mismatch의 총량을 압축하는 반면 $H_{\rm prestress}$는 residual의 부호,
방향, 쌍의 위치를 보존한다. 이 prestress가 soft subspace와 어디서 겹치고 cancellation을
만드는지가 branch formation을 좌우한다는 가설이 총량 가설보다 훨씬 물리적이다.

$\mathcal I$ 하나로 "many minima"를 말해서는 안 된다. $K_{\rm eff}$(occupancy
multiplicity), $\mathcal I_{\rm between}$(class separation), stress-equivalence test,
$\lambda_{\rm soft}$와 continuation을 분리해 보고한다.

연구 의제는 [`data/agenda.json`](data/agenda.json)에 항목별로 있고, 웹 지도의
`연구 의제` 절에서 볼 수 있다.

## 0.1 독창성과 필요성

**이미 있는 것.** 그래프를 저차원에 묻는 일은 오래되었고(MDS, spring layout, spectral
embedding, representation learning 계열) 평가 기준도 있다 — stress, distortion,
downstream 성능. 그러나 이 기준들은 모두 *하나의 임베딩 결과*를 평가한다. "이 임베딩이
얼마나 좋은가"를 묻지 "이 topology가 임베딩을 결정하는가"를 묻지 않는다.

결정성 자체를 묻는 언어는 다른 분야에 있다 — rigidity theory의 global rigidity, 통계학의
identifiability. 그런데 둘 다 이 문제에 그대로 맞지 않는다. global rigidity는 **주어진
거리가 실현 가능할 때** 유일성을 묻는데 실제 network는 거의 항상 실현 불가능하다(40개
표본의 $\mathcal D_2$ 최솟값이 $0.107$). identifiability는 보통 매끄러운 모수 모형의
국소 문제로 다루는데 여기서는 전역 다중성이 본체다.

**비어 있는 것.** *실현 불가능한 metric을 강제로 묻을 때, 그 강제가 geometry를 결정하는가*를
묻는 언어가 없다. 인공적 질문이 아니다 — 실제 network의 hop metric은 거의 항상 실현
불가능하고($\mathcal D_2$ 중앙 $0.481$), 그런데도 사람들은 매일 이것을 2차원에 그린다.

**왜 지금인가.** 임베딩은 network 연구의 기본 도구가 되었다. 그림을 그리고, 그 위에서
거리를 재고, 군집을 찾는다. 그런데 *같은 topology에서 다른 그림이 나올 수 있는가*를
정량화하는 표준이 없다. 이것이 공허한 걱정이 아님은 측정이 말한다 — ER·BA에서
$\widehat{\mathcal I}_M\approx10^{-1}$은 쌍거리의 상대 표준편차가 run마다
$\sqrt{0.1}\approx32\%$라는 뜻이다.

**새로운 것 (정확히 셋).**

1. **두 축의 분리.** representability는 protocol 무관이고 닫힌 형태, identifiability는
   protocol 조건부. 기존 문헌은 둘을 "임베딩 품질" 하나로 뭉뚱그린다. 분리하면 격자처럼
   *실현은 안 되는데 결정은 되는* 경우가 모순이 아니라 관측이 된다.
2. **protocol을 estimand 안에 넣은 것.** NEI를 graph의 invariant라 부르지 않고 $\mu_\Pi$의
   functional로 정의했다. protocol 의존성을 결함으로 숨기는 대신 정의의 일부로 만든다.
3. **floor와 signal을 가르는 설계.** 허용오차 사다리는 "이 spread가 실재하는가"를 묻는
   재사용 가능한 장치다. 이 시험 없이 보고된 embedding 변동성 수치는 해석할 수 없다.

**주장하지 않는 것.** 새로운 임베딩 알고리즘이 아니다. 더 나은 임베딩 품질 지표가 아니다.
아직 mechanism이 아니다 — 무엇이 multiplicity를 만드는지는 열려 있다.

**최소 기여.** 실제 network에서 hop metric의 Euclidean 실현 결손을 닫힌 형태로 재고, 같은
network에서 protocol이 만든 terminal geometry의 산포가 수치 잔여물과 구분되는지를 재사용
가능한 시험으로 가른 것. 이 둘은 서로 독립이며, 둘을 함께 보고해야 임베딩 위의 결론이
언제 안전한지 말할 수 있다.


## 한 문장 기여

이 연구는 한 network에 대해 서로 다른 두 질문을 분리한다.

1. 선택한 graph dissimilarity가 target dimension에서 얼마나 Euclidean-representable한가?
2. fully specified embedding protocol이 어떤 distribution of terminal geometries를 만드는가?

첫 질문에는 spectral diagnostic $\mathcal D_p$를, 둘째 질문에는 terminal-law observable
$\mathcal I$를 사용한다. NEI의 기여는 network에 새로운 intrinsic invariant를 붙이는 데
있지 않다. 같은 topology라도 graph metric, dimension, initialization law, optimizer와
stopping rule에 따라 달라지는 **protocol-conditioned terminal response**를 명시적인
ensemble quantity로 만드는 데 있다.

## 1. 먼저 estimand를 정의한다

완전한 protocol을

$$
\Pi=(G\mapsto\Delta,p,W,\rho_0,\rho_{\rm alg},\mathcal A,
\text{stopping/polish},\text{tolerances})
$$

라 하자. terminal map을 $T_\Pi$, pair-distance representation을 $q(X)=D(X)$라 하면
population object는 pushforward law

$$
\mu_\Pi=(q\circ T_\Pi)_\#(\rho_0\otimes\rho_{\rm alg})
$$

이다. NEI는 이 law의 geometry-weighted spread다. 따라서 $\mathcal I$는 intrinsic graph
invariant가 아니라 declared $\Pi$에 조건부인 response observable이다. 반복수 $M$은
$\mu_\Pi$의 인자가 아니라 empirical measure $\widehat\mu_{\Pi,M}$의 sample size다.
따라서 $M$은 Monte Carlo precision과 rare-class detection power를 제한하고, geometric
resolution은 사전에 선언한 $\varepsilon_D$가 정한다.
본 연구의 $M=100$은 동일 graph를 반복 embedding할 때의 repeat-to-repeat variability를
관측하기 위한 finite-sample design이며, population state count를 정하는 parameter가 아니다.

일반 pair weights에 대한 dimensionless energy scale은

$$
S_{\Delta,W}=\sum_{i<j}w_{ij}\Delta_{ij}^2,
\qquad
s_{\Delta,W}=\sqrt{S_{\Delta,W}/\sum_{i<j}w_{ij}}
$$

로 둔다. 현재 구현은 $W\equiv1$이다. numerical admissibility는 optimizer success,
stationarity, collision과 quotient-Hessian inertia를 검사한다. representational fidelity는
$\phi$와 residual profile로 topology-to-geometry interpretation의 유효 범위를 정한다.
poor fidelity인 stationary local minimum도 가능하므로 두 gate를 합치지 않는다.

## 2. 서로 다른 layer를 한 scalar로 섞지 않는다

| Layer | Question | Observable | Epistemic status |
|---|---|---|---|
| distance geometry | fixed $\Delta$가 $\mathbb R^p$에서 실현되는가 | $\mathcal D_p$ | fixed $(\Delta,p)$에서 algorithm-independent |
| fidelity | terminal geometry가 target dissimilarity를 얼마나 근사하는가 | $\phi=\mathcal F/S_{\Delta,W}$ | objective-conditioned lack of fit |
| terminal law | admissible repeated runs가 얼마나 퍼지는가 | $\mathcal I$ | protocol-conditioned geometric spread |
| covariance geometry | terminal cloud가 몇 개의 방향으로 퍼지는가 | $d_{\rm eff}$ | standardized covariance effective rank |
| occupancy | observed classes에 probability mass가 어떻게 나뉘는가 | $K_{\rm eff}$ | clustering, resolution, recurrence와 finite-$M$ 조건부 |
| local curvature | terminal이 saddle, soft, strict 중 무엇인가 | inertia of $H_\perp$ | local second-order diagnostic |
| objective value | separated classes가 같은 normalized stress level인가 | $\Delta_E$ and equivalence interval | non-thermodynamic stress-equivalence test |

$\mathcal I$, $d_{\rm eff}$와 $K_{\rm eff}$는 서로 대체할 수 없다. 각각 spread의 크기,
spread direction의 effective rank, observed occupancy의 effective number를 요약한다. 값이
함께 변할 수 있다는 사실은 동일한 quantity이거나 causal relation이라는 뜻이 아니다.

## 3. “Realized geometric degeneracy”의 정확한 뜻

numerical admissibility event를 $A_{\rm num}$이라 하고 acceptance probability
$\alpha_\Pi=\Pr_\Pi(A_{\rm num})>0$를 함께 보고한다. conditional terminal law는

$$
\mu_\Pi^{\rm adm}
=\mathcal L\!\left(q(T_\Pi)\mid A_{\rm num}\right)
$$

이다. prespecified pair set $\mathcal P$에서 $w_a>0$이고 $S_{\Delta,W}>0$이라 하자.
이 프로젝트에서 **realized geometric degeneracy**는 다음 operational definition만을 뜻한다.

> Under a fully specified protocol, the admissible terminal law does not collapse to a
> single geometry at the predeclared pair-distance metric $\rho_D$ and resolution
> $\varepsilon_D$:
> $\operatorname{diam}_{\rho_D}\operatorname{supp}(\mu_\Pi^{\rm adm})>\varepsilon_D$.

여기서 “realized”는 abstract objective가 가질 수 있는 모든 stationary point가 아니라
declared initialization and algorithmic ensemble이 실제 probability mass를 부여하는 terminal
geometry를 가리킨다. finite $M$에서는 recurrent $\varepsilon_D$-separated classes와
observed occupancy를 추정할 뿐 arbitrarily rare population support를 배제하지 못한다.
그러므로 positive
$\widehat{\mathcal I}_M$ 하나만으로 population degeneracy를 certified했다고 쓰지 않는다.

prespecified pair set $\mathcal P$와 $N_+=|\mathcal P|$를 고정하고, 모든 $a\in\mathcal P$에서
$0<\mathbb E[d_a]<\infty$와 $\mathbb E[d_a^2]<\infty$를 가정한다. 이때

$$
\rho_\mu^2(d,d')=\frac1{N_+}\sum_{a\in\mathcal P}
\left(\frac{d_a-d'_a}{\mathbb E[d_a]}\right)^2,
\qquad
\mathcal I(\mu_\Pi^{\rm adm})
=\frac12\mathbb E\!\left[\rho_\mu^2(D,D')\right]
$$

이며 $D,D'$는 $\mu_\Pi^{\rm adm}$의 iid draw다. 따라서 $\mathcal I=0$ iff
$\mu_\Pi^{\rm adm}$ is a point mass. 이것이 NEI와 exact population non-collapse 사이의 정확한
명제다. 반면 operational definition에 쓰는 predeclared $\rho_D$와 population-dependent
$\rho_\mu$는 positive threshold에서 일반적으로 동치가 아니다. 그러므로 $\mathcal I>0$만으로
$\operatorname{diam}_{\rho_D}\operatorname{supp}\mu>\varepsilon_D$를 인증할 수 없으며,
calibration, numerical-noise bound와 recurrence가 추가로 필요하다. 또한 NEI는 다음을
판정하지 않는다.

- total support size 또는 number of states
- equal-energy or global-minimum degeneracy
- barrier and metastability
- continuous minimizer manifold
- optimizer-independent landscape structure

$K_{\rm eff}$ 역시 total state count가 아니라 observed occupancy distribution의 effective
number다. complete-support claim에는 recurrence뿐 아니라 minimum-mass 또는 missing-mass
assumption이 필요하다. normalized-objective statement에는 class-wise stress-equivalence
interval이, metastability에는 barrier or residence-time evidence가,
continuous family의 analytic conclusion에는 smooth critical manifold와 Morse–Bott condition이
필요하다. Finite continuation은 declared resolution에서의 numerical candidate evidence다.
자세한 정의는 [notes/01](notes/01-nei-measures-real-degeneracy.md)과
[notes/06](notes/06-real-degeneracy-definition.md)에 있다.

## 4. Evidence에서 conclusion으로 가는 사다리

| Available evidence | Allowed conclusion | Not yet implied |
|---|---|---|
| $\widehat{\mathcal I}_M$이 predeclared numerical-noise bound를 초과 | resolved terminal-distance dispersion | multiple minima |
| independent batches에서 recurrent $\varepsilon_D$-separated classes | declared $(M,\varepsilon_D)$에서 observed recurrent terminal multiplicity; population multiplicity의 evidence | complete population support 또는 equal-energy degeneracy |
| 앞선 조건과 함께, 각 class에서 stationarity 및 positive-definite quotient Hessian을 tolerance-stable하게 확인 | declared tolerance에서 distinct strict-local-minimum candidates | exact, global or equal-depth minima |
| normalized-stress difference interval 전체가 $[-\tau_E,\tau_E]$에 포함 | $\tau_E$-near-equivalent stress minima | thermodynamic or global-minimum degeneracy |
| barrier 또는 residence-time evidence | metastability under the tested dynamics | equilibrium phase structure |
| finite-amplitude continuation이 refinement와 tolerance 변화에도 낮은 residual·bounded stress rise·no collision을 유지 | numerically resolved continuous-degeneracy candidate | exact minimizer manifold |
| smooth fixed-rank quotient stratum에서 $\dim\mathcal M\ge1$, $\mathcal M\subset\operatorname{Crit}(\mathcal F)$, $\ker H_X=T_X\mathcal M$ 및 positive-definite normal Hessian | analytic Morse–Bott local minimizer manifold | universality or $N\to\infty$ persistence |

각 row는 독립적인 shortcut이 아니라 누적 evidence ladder다. 특히 class-wise certificate는
먼저 분리된 class와 admissible terminal을 전제로 한다. Numerical continuation은 analytic
existence theorem이 아니라 declared resolution에서의 candidate certificate다. 이 순서를
건너뛰지 않는다. near-zero Hessian mode도 continuous degeneracy의 증명이 아니다.
$f(x)=x^4$처럼 isolated minimum이면서 Hessian이 0인 경우가 있기 때문이다.

## 5. Baseline과 null model을 먼저 둔다

NEI 값 하나에는 비교 기준이 없다. 해석은 다음 baseline을 사전에 선언한 뒤 시작한다.

- **Numerical-noise null:** tighter tolerances, repeated polishing과 deterministic control로
  optimizer noise floor를 정한다.
- **Finite-$M$ baseline:** $M=25,50,100,200,400$ rarefaction, independent-batch recurrence,
  singleton/doubleton과 new-class rate로 coverage를 확인한다.
- **Protocol sensitivity:** initialization law와 optimizer를 바꾸어 value뿐 아니라 class
  recurrence와 network rank stability를 비교한다.
- **Graph null ensembles:** degree-preserving connected rewiring과 matched ER를 구분하고,
  각각 무엇을 보존하는지, connectedness conditioning과 rewiring mixing을 명시한다.
- **Confounder control:** network size, density, mean distance와 degree heterogeneity를
  matched or stratified한 뒤 conditional association을 평가한다.

$\mathcal D_p$와 $\mathcal I$의 nonredundancy도 raw correlation으로 판정하지 않는다.
matched ensemble에서 conditional mutual information, permutation null 또는 out-of-sample
incremental prediction을 사용한다. 이 경우에도 허용되는 문장은 analyzed ensemble 안의
conditional association이지 universality나 mechanism이 아니다.

## 6. 현재 empirical evidence가 허용하는 문장

legacy runs에서 stated polishing schedule 뒤 $\widehat{\mathcal I}_M$은
$0.1100\to0.07665$로 감소했고, 24개 terminal distance matrices는 보고된 cutoff 범위에서
분리되어 있었다. 이 결과가 직접 지지하는 것은 polishing이 observed terminal-distance
dispersion을 제거하지 못했다는 사실이다.

그러나 이 계산은 corrected implementation 이전의 all-run ungated diagnostic이다. corrected
numerical gate, gate acceptance rate와 independent-batch recurrence 전에는 recurrent terminal
multiplicity를 결론으로 올리지 않는다. class-wise curvature certificate 전에는 multiple
local minima를, energy ledger 전에는 energetic near-degeneracy를 말하지 않는다.

현재 manuscript에 사용할 수 있는 문장은 다음과 같다.

> In the legacy runs, the stated polishing schedule did not eliminate the observed
> terminal-distance dispersion. Because that calculation is ungated and predates the
> corrected implementation, it does not establish recurrent terminal multiplicity or
> multiple local minima.

## 7. Correctness audit and withdrawn claims

- objective와 gradient/Hessian의 factor-of-two inconsistency를 수정했다.
- $PHP$의 eigenvalues를 형식적 개수만큼 잘라내던 방식을 폐기하고, 실제
  $\mathrm E(p)$-orbit tangent의 orthogonal complement에서 $H_\perp$를 계산한다.
- 기존 “0/8 saddle, 24개 모두 local minima”는 corrected code 재실행 전까지 철회한다.
- $\ker H_\perp\ne0\Rightarrow$ continuous family라는 implication을 삭제했다. path graph의
  collinear exact embedding은 extra zero modes와 isolated minimum이 공존하는 내부 반례다.
- 기존 global-scale run-distance Gram spectrum은 NEI와 같은 covariance가 아니다.
  pair-standardized vectors를 저장해 $d_{\rm eff}$를 재계산해야 한다.
- cMDS optimum의 unconditional uniqueness, Hessian=Fisher,
  $1-\rho_S^2=43\%$ information content와 optimizer independence 주장을 철회하거나
  conditional exploratory statement로 낮췄다.
- $\mathcal D_p$를 $\mathcal D_p^{\rm dim}+\mathcal D^{\rm neg}$로 분해하고 fixed
  $(\Delta,p)$의 diagnostic이라고 명시했다.

## 8. 1차 일단락

이것은 final conclusion이 아니라 corrected analysis로 닫을 최소 claim set 후보다.

1. finite, symmetric, hollow, nonnegative $\Delta$와 fixed $p$에서 Schoenberg criterion 및
   $\mathcal D_p=0$의 exact Euclidean realizability zero-set
2. fully specified protocol이 유도하는 terminal law $\mu_\Pi$
3. population NEI와 구분되는 pair-standardized finite-sample identity
   $\widehat{\mathcal I}_M=\operatorname{tr}B_z/M$
4. corrected numerical gates 뒤 independent batches에서 재현되는
   $\varepsilon_D$-separated terminal classes의 empirical demonstration

필수 재실행과 범위는 [data/scope.json](data/scope.json), 열린 문제는
[notes/05](notes/05-open.md), claim별 status는 [data/claims.json](data/claims.json)에 있다.

## 9. 저장소 구성

- `index.html`, `krds.css`, `app.js` — research-meeting interactive map; `index.html`을 직접 열어도 작동
- `graph.js` — horizontal dependency-DAG renderer
- `data/` — concepts, connectors, claims, references, measurements, scope, source map 및 file-mode bundle
- `notes/` — definitions, derivations, audits, open questions
- `code/` — reproducibility and validation code. JSON 수정 뒤 `node code/build_offline_data.mjs`로
  `data/offline-data.js`를 갱신하며 validator가 동기화를 확인한다.

Recommended reading order: 이 README → [핵심 정의](notes/01-nei-measures-real-degeneracy.md)
→ [covariance identity](notes/03-trace-vs-spectrum.md)
→ [formal definition](notes/06-real-degeneracy-definition.md)
→ [withdrawn claims](notes/04-withdrawn-claims.md)
→ [open questions](notes/05-open.md)
→ [claim ledger](data/claims.json).
