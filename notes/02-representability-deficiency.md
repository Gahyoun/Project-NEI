# Representability deficiency $\mathcal D_p$

2026-09-04 · corrected definition

## 지위

$\mathcal I$는 완전한 protocol
$\Pi=(\Phi,p,W,\rho_0,\rho_{\rm alg},\mathcal A,\varepsilon,T_{\max})$에 의존한다.
$M$은 empirical estimator의 sample size이지 population law의 인자가 아니다. 반면
$\mathcal D_p$는 $(\Delta,p)$가 정해진 뒤에는 optimizer, initialization과 stopping
rule에 의존하지 않는다. 다만 graph-to-dissimilarity map $\Phi:G\mapsto\Delta$와
target dimension $p$에는 여전히 의존한다.

## 정의와 선형대수적 의미

$\Delta^{(2)}=(\delta_{ij}^2)$, $C=I-\mathbf1\mathbf1^{\mathsf T}/N$에 대해

$$
B=-\frac12C\Delta^{(2)}C,\qquad
\mu_1\ge\cdots\ge\mu_N
$$

라 하고

$$
\mathcal D_p=
\frac{\sum_{a>p}\max\{\mu_a,0\}+\sum_a\max\{-\mu_a,0\}}
{\sum_a|\mu_a|}.
$$

이는 $\|B\|_*>0$일 때

$$
\mathcal D_p=
\frac{\min_{K\succeq0,\,\operatorname{rank}K\le p}\|B-K\|_*}{\|B\|_*}
$$

인 normalized nuclear-norm spectral residual이다. $B=0$인 trivial case에는
$\mathcal D_p=0$ convention을 쓴다. 여기서 $\Delta$는 finite, symmetric, hollow,
nonnegative dissimilarity로 가정한다. 따라서

Primary implementation의 numerator는
$\sum_{a>p}\mu_a^++\sum_a\mu_a^-$이며 factor $2$를 붙이지 않는다.
이는 Hermitian nuclear-norm projection residual과 일치한다. Full symmetric
pair-matrix의 off-diagonal Frobenius bookkeeping에서 생기는 factor $2$와 혼합하지 않는다.

- $\delta\mapsto c\delta$에 불변이다.
- $p$에 대해 비증가한다.
- $\mathcal D_p=0$은 $\Delta$가 $\mathbb R^p$에서 exact Euclidean realizable인
  것과 동치이다.
- zero set은 Schoenberg 정리로 canonical하지만 양의 결손에 사용할 norm과
  normalization은 하나의 diagnostic 선택이다.

## 두 성분의 linear-algebraic 구분

$$
\mathcal D_p=\mathcal D_p^{\rm dim}+\mathcal D^{\rm neg},
$$

$$
\mathcal D_p^{\rm dim}=
\frac{\sum_{a>p}\mu_a^+}{\sum_a|\mu_a|},\qquad
\mathcal D^{\rm neg}=
\frac{\sum_a\mu_a^-}{\sum_a|\mu_a|}.
$$

$\mathcal D_p^{\rm dim}$은 Euclidean이지만 target dimension보다 높은 성분이고,
$\mathcal D^{\rm neg}$은 어떤 Euclidean dimension에서도 Gram PSD 조건을 깨는 성분이다.
완전그래프의 큰 $\mathcal D_2$처럼 주된 원인이 dimension truncation일 수 있으므로,
전체 $\mathcal D_p$를 곧바로 physical frustration이라고 부르지 않는다.

## negative type convention

Euclidean distance $\Delta$의 Schoenberg 조건은

$$
z^{\mathsf T}\Delta^{\circ2}z\le0
\quad\text{for every }z\perp\mathbf1
$$

이다. 반면 metric $\Delta$가 negative type이라고 부르는 다른 관례는
$z^{\mathsf T}\Delta z\le0$을 뜻하며, 이는 $\sqrt\Delta$가 Hilbert-embeddable이라는
말이다. $\ell_1$ metric은 후자를 만족할 수 있지만 $\Delta$ 자체가 Euclidean이라는
뜻은 아니다. 격자 hop metric이 $\ell_1$이면서 $\mathcal D_2>0$인 것은 모순이 아니다.

## stress와의 정확한 정리

모든 off-diagonal weight가 양수이면

$$
\mathcal D_p=0\iff\min_X\mathcal F(X)=0,
$$

이며 모든 zero-stress realization은
$\Omega=\mathbb R^{N\times p}/\mathrm E(p)$에서 하나의 orbit을 이룬다.

증명은 간단하다. $\mathcal D_p=0$이면 모든 target distance를 실현하는 $Y$가 있어
$\mathcal F(Y)=0$이다. 반대로 $\mathcal F(X)=0$이고 모든 pair weight가 양수이면 모든
pair distance가 target과 같으므로 Schoenberg criterion을 만족한다. 완전 distance
matrix는 configuration을 translation, rotation, reflection까지 결정한다.

이 정리는 positive-stress local minima의 부재나 optimizer의 global convergence를
보장하지 않는다. 또한 best-fit minimizer가 유일하면 $\mathcal D_p=0$이라는 역은
거짓이지만, 격자의 반복수렴은 global uniqueness의 증명이 아니므로 정리의 반례로
쓰지 않는다.

엄밀한 반례는 $p=1$에서

$$
\delta_{12}=c,\qquad \delta_{13}=\delta_{23}=1,\qquad 1<c<2
$$

인 세 점 metric이다. $\mathcal D_1>0$이지만 유일한 optimal order는 $1-3-2$이고 두
gap은 $(1+c)/3$이며

$$
\mathcal F_{\min}=(2-c)^2/3>0.
$$

다른 middle-node order의 최소값은 $c^2/3$이므로 quotient global minimizer는 유일하다.

## 측정값의 현재 의미

| 모형 | $\mathcal D_1$ | $\mathcal D_2$ | $\mathcal D_3$ |
|---|---:|---:|---:|
| 경로 $P_{200}$ | 0.0000 | 0.0000 | 0.0000 |
| $\mathbb R^2$ 좌표 거리 | 0.4762 | 0.0000 | 0.0000 |
| 링 $C_{200}$ | 0.6960 | 0.3920 | 0.3582 |
| 격자 14×14 | 0.7029 | 0.4058 | 0.3621 |
| RGG $r=0.12$ | 0.7128 | 0.4638 | 0.4421 |
| RGG $r=0.20$ | 0.8150 | 0.6483 | 0.6344 |
| WS $k=6,p=.05$ | 0.9172 | 0.8385 | 0.7734 |
| BA $m=2$ | 0.9631 | 0.9290 | 0.8986 |
| ER $p=0.02$ | 0.9847 | 0.9701 | 0.9557 |
| 완전그래프 $K_{200}$ | 0.9950 | 0.9899 | 0.9849 |

RGG에서 Euclidean인 것은 latent coordinates이지 hop metric이 아니다. 같은 점집합의
coordinate distance는 $\mathcal D_2=0$이지만 hop metric은 양의 결손을 갖는다.

경로 $P_n$은 graph-level exact-realizable control이다. 다만 $p=2$의 collinear
realization에서 transverse displacement는 distance를 $O(t^2)$, stress를 $O(t^4)$로
바꾼다. 그러므로 unique exact geometry이면서 quotient Hessian에 추가 zero modes가
존재할 수 있다. 이는 Hessian zero mode를 continuous degeneracy로 오독하지 않게 하는
내부 unit test다.
