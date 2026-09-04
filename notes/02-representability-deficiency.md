# Representability deficiency $\mathcal{D}_p$

`2026-09-04`

## 왜 필요한가

$\mathcal{I}$ 는 protocol $\Pi=(\rho_0,\Gamma,p,\varepsilon,T_{\max})$ 에 의존하고
$\rho_0$ 가 비퇴화일 때만 정의된다. 그것만으로는 `네트워크의 성질` 이라고 부를
근거가 약하다. protocol 이 개입하지 않는 축이 하나 필요하다.

## 정의

$\Delta^{(2)}=(\delta_{ij}^2)$, $C=I-\mathbf{1}\mathbf{1}^{\mathsf T}/N$ 에 대해
$G=-\tfrac12 C\Delta^{(2)}C$ 의 eigenvalue 를 $\mu_1\ge\cdots\ge\mu_N$ 이라 할 때

$$\mathcal{D}_p=\frac{\sum_{a>p}\max\{\mu_a,0\}+\sum_a\max\{-\mu_a,0\}}{\sum_a|\mu_a|}\in[0,1]$$

분자의 첫 항이 **차원 초과**, 둘째 항이 **비유클리드** 성분이다.

- protocol 무관. embedding 을 돌리지 않고 eigendecomposition 한 번.
- $\delta\mapsto c\delta$ 에 불변 (dimensionless).
- $p$ 에 대해 비증가.
- **Schoenberg**: $\mathcal{D}_p=0 \iff \delta$ 가 $\mathbb{R}^p$ 에서 정확히 실현된다.

## 측정 (직접 계산)

| 모형 | $\mathcal{D}_1$ | $\mathcal{D}_2$ | $\mathcal{D}_3$ |
|---|---|---|---|
| 경로 $P_{200}$ | **0.0000** | **0.0000** | 0.0000 |
| $\mathbb{R}^2$ 좌표 거리 | 0.4762 | **0.0000** | 0.0000 |
| 링 $C_{200}$ | 0.6960 | 0.3920 | 0.3582 |
| 격자 14×14 | 0.7029 | 0.4058 | 0.3621 |
| RGG $r{=}0.12$ | 0.7128 | **0.4638** | 0.4421 |
| RGG $r{=}0.20$ | 0.8150 | 0.6483 | 0.6344 |
| WS $k{=}6,p{=}.05$ | 0.9172 | 0.8385 | 0.7734 |
| BA $m{=}2$ | 0.9631 | 0.9290 | 0.8986 |
| ER $p{=}0.02$ | 0.9847 | 0.9701 | 0.9557 |
| 완전그래프 $K_{200}$ | 0.9950 | 0.9899 | 0.9849 |

순서가 해석 가능하다. 경로 → 격자 · 성긴 RGG → 조밀 RGG → WS → BA → ER → 완전그래프.

## 원고에서 무너지는 문장

> `the random geometric graph---whose metric is Euclidean by construction`

RGG 에서 Euclidean 인 것은 **잠재 좌표**이지 graph metric 이 아니다. hop metric 의
$\mathcal{D}_2=0.464$ 로 격자(0.406)보다 **크고**, 밀도를 올리면 0.648 로 더
나빠진다 — hop 이 포화하기 때문이다. 같은 점집합의 좌표 거리는 $\mathcal{D}_2=0.000$.

## 정리 하나

**$\mathcal{D}_p=0$ 이면 $\min\mathcal{F}=0$ 이고 그 minimizer 는 $\Omega$ 에서 유일하다.
역은 성립하지 않는다.**

증명. $\mathcal{D}_p=0$ 이면 $d_{ij}(Y)=\delta_{ij}$ 인 $Y$ 가 있어 $\mathcal{F}(Y)=0$
이고 $\mathcal{F}\ge0$ 이므로 global minimum 이다. 역으로 $\mathcal{F}(X)=0$ 이면 모든
쌍에서 거리가 일치하고, 완전한 distance matrix 는 점집합을 isometry 까지 결정하므로
$X\in \mathrm{E}(p)\cdot Y$ 이다. 반사가 포함되므로 quotient 는 $\mathrm{SE}(p)$ 가
아니라 $\mathrm{E}(p)$ 이다. 역의 반례는 정사각격자이다 — $\mathcal{D}_2=0.406>0$ 인데
terminal geometry 는 수치오차까지 구분되지 않는다. ∎

## 따라오는 것: 정리로 뒷받침되는 protocol control

격자에서 $\mathcal{I}\approx0$ 인 것은 **관측**이지 정리가 아니다. 반면
$\mathcal{D}_p=0$ 인 그래프에서는 landscape degeneracy 가 **정리로** 배제되므로,
거기서 관측되는 $\mathcal{I}>0$ 은 전부 protocol 의 실패로 귀속된다.

경로 그래프 $P_n$ 이 그 예이다. $\delta_{ij}=|i-j|$ 는 직선 위에서 정확히 실현되어
$\mathcal{D}_1=\mathcal{D}_2=0$ 이다. 노트의 exact-Euclidean unit test 를 합성
dissimilarity 가 아니라 **실제 그래프** 수준으로 끌어올린 것이며, 격자보다 강하다.

## 기호 주의

노트의 $\kappa_+$ 는 projected Hessian 의 positive spectral scale 이다. Schoenberg
결손에는 $\mathcal{D}_p$ 를 쓴다. 혼동하지 말 것.

## 남은 물음

격자는 $\mathcal{D}_2=0.406$ 으로 좌절되어 있는데도 $\mathcal{I}\approx0$ 이다. 즉
**좌절의 크기만으로는 landscape 가 거칠어지지 않는다.** 좌절의 *무질서도* 가 필요한
것으로 보이며, 이것이 다음 물음이다.
